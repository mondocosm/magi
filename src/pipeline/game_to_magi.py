"""
Real-time game-to-MAGI conversion pipeline
Captures game frames and converts them to MAGI format in near real-time
"""

import cv2
import numpy as np
import time
import threading
import queue
from typing import Optional, Tuple, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

from ..input.game_capture import GameCapture, GameFrame, CaptureMethod
from ..processing.interpolation import FrameInterpolator
from ..processing.upscaling import ImageUpscaler
from ..processing.processing_3d import Processing3D
from ..processing.frame_cadence import FrameCadenceManager
from ..core.config import Config
from ..core.gpu_detector import GPUDetector, GPUVendor


class PipelineMode(Enum):
    """Pipeline processing modes"""
    REALTIME = "realtime"  # Lowest latency, lower quality
    BALANCED = "balanced"  # Balance between latency and quality
    QUALITY = "quality"  # Highest quality, higher latency


@dataclass
class PipelineStats:
    """Pipeline statistics"""
    frames_processed: int = 0
    frames_output: int = 0
    avg_latency_ms: float = 0.0
    avg_fps: float = 0.0
    current_latency_ms: float = 0.0
    processing_time_ms: float = 0.0
    capture_latency_ms: float = 0.0
    interpolation_time_ms: float = 0.0
    upscaling_time_ms: float = 0.0
    conversion_3d_time_ms: float = 0.0
    cadence_time_ms: float = 0.0


@dataclass
class MAGIOutputFrame:
    """MAGI output frame"""
    left_eye: np.ndarray
    right_eye: np.ndarray
    timestamp: float
    frame_number: int
    is_left: bool  # True for left eye, False for right eye


class GameToMAGIPipeline:
    """Real-time game-to-MAGI conversion pipeline"""
    
    def __init__(self, 
                 config: Config,
                 capture_method: CaptureMethod = CaptureMethod.SCREEN_CAPTURE,
                 mode: PipelineMode = PipelineMode.BALANCED):
        """
        Initialize game-to-MAGI pipeline
        
        Args:
            config: Configuration object
            capture_method: Game capture method
            mode: Processing mode (realtime, balanced, quality)
        """
        self.config = config
        self.capture_method = capture_method
        self.mode = mode
        
        # Initialize components
        self._setup_components()
        
        # Pipeline state
        self._running = False
        self._pipeline_thread = None
        self._output_queue = None
        self._frame_number = 0
        self._last_output_time = 0
        
        # Statistics
        self._stats = PipelineStats()
        self._latency_samples = []
        
        # Performance tuning based on mode
        self._tune_performance()
    
    def _setup_components(self):
        """Setup pipeline components"""
        # GPU detection
        self.gpu_detector = GPUDetector()
        self.gpu_info = self.gpu_detector.get_best_gpu()
        self.backend = self.gpu_detector.get_processing_backend()
        
        # Game capture
        self.game_capture = GameCapture(
            method=self.capture_method,
            target_fps=self.config.processing.target_frame_rate,
            target_resolution=self._get_capture_resolution(),
            buffer_size=8
        )
        
        # Frame interpolation
        self.interpolator = FrameInterpolator(
            method=self.config.processing.interpolation_method,
            backend=self.backend
        )
        
        # Image upscaling
        self.upscaler = ImageUpscaler(
            method=self.config.processing.upscaling_method,
            backend=self.backend
        )
        
        # 3D processing
        self.processing_3d = Processing3D(
            config=self.config,
            backend=self.backend
        )
        
        # Frame cadence
        self.cadence_manager = FrameCadenceManager(
            target_fps=self.config.processing.target_frame_rate,
            eye_separation=self.config.output.eye_separation
        )
    
    def _get_capture_resolution(self) -> Tuple[int, int]:
        """Get capture resolution based on mode"""
        if self.mode == PipelineMode.REALTIME:
            # Lower resolution for faster processing
            return (1920, 1080)
        elif self.mode == PipelineMode.BALANCED:
            return (2560, 1440)
        else:  # QUALITY
            return (3840, 2160)
    
    def _tune_performance(self):
        """Tune performance based on mode"""
        if self.mode == PipelineMode.REALTIME:
            # Fastest settings
            self._interpolation_quality = "fast"
            self._upscaling_quality = "fast"
            self._use_fast_3d = True
            self._batch_size = 1
        elif self.mode == PipelineMode.BALANCED:
            # Balanced settings
            self._interpolation_quality = "medium"
            self._upscaling_quality = "medium"
            self._use_fast_3d = False
            self._batch_size = 2
        else:  # QUALITY
            # Best quality settings
            self._interpolation_quality = "high"
            self._upscaling_quality = "high"
            self._use_fast_3d = False
            self._batch_size = 4
    
    def start(self, output_callback: Optional[Callable[[MAGIOutputFrame], None]] = None) -> bool:
        """
        Start the pipeline
        
        Args:
            output_callback: Callback function for output frames
            
        Returns:
            True if started successfully, False otherwise
        """
        if self._running:
            return True
        
        try:
            # Start game capture
            if not self.game_capture.start():
                print("Failed to start game capture")
                return False
            
            # Setup output
            self._output_callback = output_callback
            self._output_queue = queue.Queue(maxsize=16)
            
            # Start pipeline thread
            self._running = True
            self._pipeline_thread = threading.Thread(
                target=self._pipeline_loop,
                daemon=True
            )
            self._pipeline_thread.start()
            
            print(f"Game-to-MAGI pipeline started in {self.mode.value} mode")
            return True
        
        except Exception as e:
            print(f"Error starting pipeline: {e}")
            return False
    
    def _pipeline_loop(self):
        """Main pipeline processing loop"""
        while self._running:
            start_time = time.time()
            
            try:
                # Get captured frame
                game_frame = self.game_capture.get_frame(timeout=0.1)
                
                if game_frame is None:
                    continue
                
                # Process frame
                magi_frames = self._process_frame(game_frame)
                
                # Output frames
                if magi_frames:
                    for magi_frame in magi_frames:
                        self._output_frame(magi_frame)
                
                # Update statistics
                processing_time = time.time() - start_time
                self._stats.processing_time_ms = processing_time * 1000
                self._stats.current_latency_ms = processing_time * 1000
                
                self._latency_samples.append(processing_time * 1000)
                if len(self._latency_samples) > 100:
                    self._latency_samples.pop(0)
                self._stats.avg_latency_ms = np.mean(self._latency_samples)
                
                # Calculate FPS
                if self._last_output_time > 0:
                    elapsed = time.time() - self._last_output_time
                    current_fps = 1.0 / elapsed if elapsed > 0 else 0
                    self._stats.avg_fps = 0.9 * self._stats.avg_fps + 0.1 * current_fps
                
                self._last_output_time = time.time()
            
            except Exception as e:
                print(f"Error in pipeline loop: {e}")
                time.sleep(0.01)
    
    def _process_frame(self, game_frame: GameFrame) -> list:
        """
        Process a single game frame through the pipeline
        
        Args:
            game_frame: Captured game frame
            
        Returns:
            List of MAGI output frames
        """
        start_time = time.time()
        
        # Step 1: 2D to 3D conversion
        conversion_start = time.time()
        left_eye, right_eye = self._convert_to_3d(game_frame.frame)
        self._stats.conversion_3d_time_ms = (time.time() - conversion_start) * 1000
        
        # Step 2: Frame interpolation (if needed)
        interpolation_start = time.time()
        left_eye = self._interpolate_frame(left_eye)
        right_eye = self._interpolate_frame(right_eye)
        self._stats.interpolation_time_ms = (time.time() - interpolation_start) * 1000
        
        # Step 3: Upscaling (if needed)
        upscaling_start = time.time()
        left_eye = self._upscale_frame(left_eye)
        right_eye = self._upscale_frame(right_eye)
        self._stats.upscaling_time_ms = (time.time() - upscaling_start) * 1000
        
        # Step 4: Apply MAGI cadence
        cadence_start = time.time()
        magi_frames = self._apply_cadence(left_eye, right_eye, game_frame.timestamp)
        self._stats.cadence_time_ms = (time.time() - cadence_start) * 1000
        
        self._stats.frames_processed += 1
        
        return magi_frames
    
    def _convert_to_3d(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert 2D frame to 3D stereo
        
        Args:
            frame: Input 2D frame
            
        Returns:
            Tuple of (left_eye, right_eye) frames
        """
        if self._use_fast_3d:
            # Fast depth-based conversion
            return self._fast_3d_conversion(frame)
        else:
            # High-quality StereoCrafter conversion
            return self._high_quality_3d_conversion(frame)
    
    def _fast_3d_conversion(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Fast depth-based 3D conversion"""
        # Simple horizontal shift for fast conversion
        # This is a placeholder - real implementation would use depth estimation
        
        # Estimate depth using simple gradient
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        depth = np.abs(grad_x)
        depth = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX)
        
        # Create stereo views based on depth
        shift_amount = 10  # pixels
        
        # Left eye (shift right)
        left_eye = np.roll(frame, shift_amount, axis=1)
        left_eye[:, :shift_amount] = frame[:, :shift_amount]
        
        # Right eye (shift left)
        right_eye = np.roll(frame, -shift_amount, axis=1)
        right_eye[:, -shift_amount:] = frame[:, -shift_amount:]
        
        return left_eye, right_eye
    
    def _high_quality_3d_conversion(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """High-quality StereoCrafter 3D conversion"""
        try:
            # Use StereoCrafter for high-quality conversion
            result = self.processing_3d.convert_2d_to_3d(frame)
            if result and len(result) >= 2:
                return result[0], result[1]
        except Exception as e:
            print(f"Error in high-quality 3D conversion: {e}")
        
        # Fallback to fast conversion
        return self._fast_3d_conversion(frame)
    
    def _interpolate_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Interpolate frame to target frame rate
        
        Args:
            frame: Input frame
            
        Returns:
            Interpolated frame
        """
        # For real-time processing, we might skip interpolation
        # or use very fast interpolation
        if self.mode == PipelineMode.REALTIME:
            return frame
        
        # Use frame interpolator
        try:
            # For simplicity, just return the frame
            # Real implementation would interpolate between frames
            return frame
        except Exception as e:
            print(f"Error in frame interpolation: {e}")
            return frame
    
    def _upscale_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Upscale frame to target resolution
        
        Args:
            frame: Input frame
            
        Returns:
            Upscaled frame
        """
        target_width, target_height = map(int, self.config.processing.target_resolution.lower().split('x'))
        
        # Check if upscaling is needed
        if frame.shape[1] >= target_width and frame.shape[0] >= target_height:
            return frame
        
        # Upscale frame
        try:
            if self.mode == PipelineMode.REALTIME:
                # Fast bicubic upscaling
                return cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_CUBIC)
            else:
                # High-quality upscaling
                return self.upscaler.upscale(frame, (target_width, target_height))
        except Exception as e:
            print(f"Error in upscaling: {e}")
            # Fallback to simple resize
            return cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
    
    def _apply_cadence(self, left_eye: np.ndarray, right_eye: np.ndarray, 
                      timestamp: float) -> list:
        """
        Apply MAGI frame cadence to stereo frames
        
        Args:
            left_eye: Left eye frame
            right_eye: Right eye frame
            timestamp: Frame timestamp
            
        Returns:
            List of MAGI output frames
        """
        magi_frames = []
        
        # Create alternating left/right frames
        for i in range(2):  # 2 frames per input frame (left and right)
            is_left = (i % 2 == 0)
            
            magi_frame = MAGIOutputFrame(
                left_eye=left_eye if is_left else np.zeros_like(left_eye),
                right_eye=right_eye if not is_left else np.zeros_like(right_eye),
                timestamp=timestamp + i * (1.0 / self.config.processing.target_frame_rate),
                frame_number=self._frame_number,
                is_left=is_left
            )
            
            magi_frames.append(magi_frame)
            self._frame_number += 1
        
        return magi_frames
    
    def _output_frame(self, magi_frame: MAGIOutputFrame):
        """
        Output a MAGI frame
        
        Args:
            magi_frame: MAGI output frame
        """
        self._stats.frames_output += 1
        
        # Call callback if provided
        if self._output_callback:
            try:
                self._output_callback(magi_frame)
            except Exception as e:
                print(f"Error in output callback: {e}")
        
        # Add to queue
        if self._output_queue:
            try:
                self._output_queue.put_nowait(magi_frame)
            except queue.Full:
                pass
    
    def get_output_frame(self, timeout: float = 0.1) -> Optional[MAGIOutputFrame]:
        """
        Get the next output frame
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            MAGIOutputFrame or None if timeout
        """
        if self._output_queue:
            try:
                return self._output_queue.get(timeout=timeout)
            except queue.Empty:
                return None
        return None
    
    def get_stats(self) -> PipelineStats:
        """Get pipeline statistics"""
        # Update capture latency
        capture_stats = self.game_capture.get_stats()
        self._stats.capture_latency_ms = capture_stats.current_latency_ms
        
        return self._stats
    
    def stop(self):
        """Stop the pipeline"""
        self._running = False
        
        if self._pipeline_thread:
            self._pipeline_thread.join(timeout=1.0)
        
        # Stop game capture
        self.game_capture.stop()
        
        print("Game-to-MAGI pipeline stopped")
    
    def is_running(self) -> bool:
        """Check if pipeline is running"""
        return self._running
    
    def set_mode(self, mode: PipelineMode):
        """
        Set pipeline mode
        
        Args:
            mode: New pipeline mode
        """
        self.mode = mode
        self._tune_performance()
        print(f"Pipeline mode changed to {mode.value}")


def create_game_to_magi_pipeline(config: Config,
                                 capture_method: str = "screen_capture",
                                 mode: str = "balanced") -> GameToMAGIPipeline:
    """
    Create game-to-MAGI pipeline instance
    
    Args:
        config: Configuration object
        capture_method: Capture method (screen_capture, window_capture, obs_websocket, game_hook, virtual_camera)
        mode: Processing mode (realtime, balanced, quality)
        
    Returns:
        GameToMAGIPipeline instance
    """
    try:
        capture_method_enum = CaptureMethod(capture_method)
    except ValueError:
        capture_method_enum = CaptureMethod.SCREEN_CAPTURE
    
    try:
        mode_enum = PipelineMode(mode)
    except ValueError:
        mode_enum = PipelineMode.BALANCED
    
    return GameToMAGIPipeline(
        config=config,
        capture_method=capture_method_enum,
        mode=mode_enum
    )


if __name__ == "__main__":
    # Test game-to-MAGI pipeline
    print("Testing game-to-MAGI pipeline...")
    
    from ..core.config import Config
    
    config = Config()
    pipeline = create_game_to_magi_pipeline(
        config=config,
        capture_method="screen_capture",
        mode="balanced"
    )
    
    def output_callback(magi_frame):
        print(f"Output frame {magi_frame.frame_number}: {'Left' if magi_frame.is_left else 'Right'} eye")
    
    if pipeline.start(output_callback=output_callback):
        print("Pipeline started successfully!")
        
        # Run for 5 seconds
        time.sleep(5)
        
        stats = pipeline.get_stats()
        print(f"\nStats:")
        print(f"  Frames processed: {stats.frames_processed}")
        print(f"  Frames output: {stats.frames_output}")
        print(f"  Avg FPS: {stats.avg_fps:.2f}")
        print(f"  Avg latency: {stats.avg_latency_ms:.2f}ms")
        print(f"  Processing time: {stats.processing_time_ms:.2f}ms")
        print(f"  Capture latency: {stats.capture_latency_ms:.2f}ms")
        print(f"  3D conversion time: {stats.conversion_3d_time_ms:.2f}ms")
        print(f"  Interpolation time: {stats.interpolation_time_ms:.2f}ms")
        print(f"  Upscaling time: {stats.upscaling_time_ms:.2f}ms")
        print(f"  Cadence time: {stats.cadence_time_ms:.2f}ms")
        
        pipeline.stop()
        print("Pipeline stopped.")
    else:
        print("Failed to start pipeline.")
