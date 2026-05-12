"""
Camera to MAGI Pipeline

Real-time conversion of camera input to MAGI format:
- Stereo cameras (ZED, Google 180 VR, HUD stereo cameras)
- Depth cameras (Xbox Kinect, Intel RealSense, Azure Kinect)
- VR cameras (Insta360, Ricoh Theta)
- Generic stereo/mono cameras
"""

import cv2
import numpy as np
import time
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue

from ..input.camera_capture import CameraCapture, CameraFrame, CameraType, CameraFormat
from ..processing.interpolation import FrameInterpolator
from ..processing.upscaling import FrameUpscaler
from ..processing.frame_cadence import FrameCadence
from ..output.magi_writer import MAGIWriter
from ..core.config import Config

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Processing modes for camera-to-MAGI conversion"""
    REALTIME = "realtime"  # Fastest processing, lower quality
    BALANCED = "balanced"  # Balance between speed and quality
    QUALITY = "quality"  # Highest quality, slower processing


class OutputMode(Enum):
    """Output modes for camera-to-MAGI conversion"""
    STREAM_ONLY = "stream_only"  # Real-time streaming only
    FILE_ONLY = "file_only"  # Save to file only
    BOTH = "both"  # Both streaming and file output


@dataclass
class CameraProcessingStats:
    """Statistics for camera processing"""
    fps: float = 0.0
    frames_processed: int = 0
    frames_dropped: int = 0
    avg_latency: float = 0.0
    current_latency: float = 0.0
    processing_times: Dict[str, float] = field(default_factory=dict)
    start_time: float = 0.0
    last_frame_time: float = 0.0


class CameraToMAGIPipeline:
    """
    Real-time camera-to-MAGI conversion pipeline
    
    Features:
    - Real-time capture from various camera types
    - Automatic format detection and conversion
    - Frame interpolation to 120fps
    - Upscaling to 4K resolution
    - MAGI frame cadence application
    - Performance monitoring
    - Multiple processing modes
    """
    
    def __init__(
        self,
        camera_capture: CameraCapture,
        output_path: Optional[str] = None,
        config: Optional[Config] = None,
        mode: ProcessingMode = ProcessingMode.BALANCED,
        output_mode: OutputMode = OutputMode.BOTH
    ):
        """
        Initialize camera-to-MAGI pipeline
        
        Args:
            camera_capture: Camera capture instance
            output_path: Output MAGI file path (optional for streaming only)
            config: Configuration object
            mode: Processing mode
            output_mode: Output mode (stream_only, file_only, or both)
        """
        self.camera_capture = camera_capture
        self.output_path = output_path
        self.config = config or Config()
        self.mode = mode
        self.output_mode = output_mode
        
        # Processing components
        self.interpolator = None
        self.upscaler = None
        self.cadence = None
        self.magi_writer = None
        
        # Processing state
        self.running = False
        self.thread = None
        self.frame_queue = queue.Queue(maxsize=30)
        self.output_queue = queue.Queue(maxsize=30)
        
        # Statistics
        self.stats = CameraProcessingStats()
        self.stats.start_time = time.time()
        self.stats.last_frame_time = time.time()
        
        # Processing settings based on mode
        self._setup_processing_mode()
        
    def _setup_processing_mode(self) -> None:
        """Setup processing parameters based on mode"""
        if self.mode == ProcessingMode.REALTIME:
            self.interpolation_method = "optical_flow"
            self.upscale_method = "bicubic"
            self.quality = 0.7
        elif self.mode == ProcessingMode.BALANCED:
            self.interpolation_method = "rife"
            self.upscale_method = "waifu2x"
            self.quality = 0.85
        elif self.mode == ProcessingMode.QUALITY:
            self.interpolation_method = "film"
            self.upscale_method = "realesrgan"
            self.quality = 0.95
    
    def start(self) -> bool:
        """
        Start the camera-to-MAGI pipeline
        
        Returns:
            True if successful, False otherwise
        """
        if self.running:
            logger.warning("Pipeline already running")
            return False
            
        try:
            # Initialize camera capture
            if not self.camera_capture.start():
                logger.error("Failed to start camera capture")
                return False
                
            # Initialize processing components
            self._initialize_components()
            
            # Start processing thread
            self.running = True
            self.thread = threading.Thread(target=self._processing_loop, daemon=True)
            self.thread.start()
            
            logger.info(f"Camera-to-MAGI pipeline started in {self.mode.value} mode")
            return True
            
        except Exception as e:
            logger.error(f"Error starting pipeline: {e}")
            return False
    
    def stop(self) -> None:
        """Stop the camera-to-MAGI pipeline"""
        if not self.running:
            return
            
        self.running = False
        
        # Wait for thread to finish
        if self.thread:
            self.thread.join(timeout=5.0)
            
        # Stop camera capture
        self.camera_capture.stop()
        
        # Close MAGI writer
        if self.magi_writer:
            self.magi_writer.close()
            
        logger.info("Camera-to-MAGI pipeline stopped")
    
    def _initialize_components(self) -> None:
        """Initialize processing components"""
        # Initialize interpolator
        self.interpolator = FrameInterpolator(
            method=self.interpolation_method,
            target_fps=120.0,
            config=self.config
        )
        
        # Initialize upscaler
        self.upscaler = FrameUpscaler(
            method=self.upscale_method,
            target_width=3840,
            target_height=2160,
            config=self.config
        )
        
        # Initialize frame cadence
        self.cadence = FrameCadence(
            target_fps=120.0,
            phase_offset=0.5  # 180° phase offset for MAGI
        )
        
        # Initialize MAGI writer (only if file output is enabled)
        if self.output_mode in [OutputMode.FILE_ONLY, OutputMode.BOTH]:
            if self.output_path is None:
                raise ValueError("output_path is required for file output mode")
                
            self.magi_writer = MAGIWriter(
                output_path=self.output_path,
                fps=120.0,
                width=3840,
                height=2160,
                codec="hevc",
                config=self.config
            )
            logger.info(f"MAGI writer initialized for file output: {self.output_path}")
        else:
            self.magi_writer = None
            logger.info("File output disabled, streaming only")
        
        logger.info("Processing components initialized")
    
    def _processing_loop(self) -> None:
        """Main processing loop"""
        while self.running:
            try:
                # Get frame from camera
                camera_frame = self.camera_capture.get_frame(timeout=0.1)
                
                if camera_frame is None:
                    continue
                    
                # Process frame
                magi_frame = self._process_frame(camera_frame)
                
                if magi_frame is not None:
                    # Add to output queue
                    try:
                        self.output_queue.put(magi_frame, timeout=0.01)
                    except queue.Full:
                        self.stats.frames_dropped += 1
                        
                # Update statistics
                self._update_stats()
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                time.sleep(0.1)
    
    def _process_frame(self, camera_frame: CameraFrame) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Process a camera frame to MAGI format
        
        Args:
            camera_frame: Input camera frame
            
        Returns:
            Tuple of (left_eye, right_eye) frames or None
        """
        start_time = time.time()
        
        try:
            # Step 1: Extract stereo views
            left, right = self._extract_stereo_views(camera_frame)
            processing_time = time.time() - start_time
            self.stats.processing_times["stereo_extraction"] = processing_time
            
            if left is None or right is None:
                return None
                
            # Step 2: Interpolate frames to 120fps
            start_time = time.time()
            left_interpolated = self._interpolate_frames(left)
            right_interpolated = self._interpolate_frames(right)
            processing_time = time.time() - start_time
            self.stats.processing_times["interpolation"] = processing_time
            
            # Step 3: Upscale to 4K
            start_time = time.time()
            left_upscaled = self._upscale_frames(left_interpolated)
            right_upscaled = self._upscale_frames(right_interpolated)
            processing_time = time.time() - start_time
            self.stats.processing_times["upscaling"] = processing_time
            
            # Step 4: Apply MAGI frame cadence
            start_time = time.time()
            left_cadence, right_cadence = self._apply_cadence(left_upscaled, right_upscaled)
            processing_time = time.time() - start_time
            self.stats.processing_times["cadence"] = processing_time
            
            # Step 5: Write to MAGI file
            start_time = time.time()
            self._write_magi_frames(left_cadence, right_cadence)
            processing_time = time.time() - start_time
            self.stats.processing_times["encoding"] = processing_time
            
            self.stats.frames_processed += 1
            return (left_cadence, right_cadence)
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return None
    
    def _extract_stereo_views(self, camera_frame: CameraFrame) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Extract left and right eye views from camera frame
        
        Args:
            camera_frame: Input camera frame
            
        Returns:
            Tuple of (left, right) views
        """
        # If camera already provides stereo views
        if camera_frame.left is not None and camera_frame.right is not None:
            return camera_frame.left, camera_frame.right
            
        # If camera provides depth, generate stereo from depth
        if camera_frame.depth is not None and camera_frame.color is not None:
            return self._generate_stereo_from_depth(camera_frame.color, camera_frame.depth)
            
        # If camera provides only color, convert to stereo
        if camera_frame.color is not None:
            return self._convert_mono_to_stereo(camera_frame.color)
            
        return None, None
    
    def _generate_stereo_from_depth(
        self,
        color: np.ndarray,
        depth: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate stereo views from color and depth
        
        Args:
            color: Color image
            depth: Depth map
            
        Returns:
            Tuple of (left, right) views
        """
        # Simple depth-based stereo generation
        # In production, use more sophisticated methods
        
        h, w = color.shape[:2]
        
        # Create left and right views by shifting pixels based on depth
        baseline = 0.1  # Baseline in meters
        focal_length = w / 2  # Approximate focal length
        
        # Normalize depth
        depth_normalized = depth.astype(np.float32) / np.max(depth)
        
        # Calculate disparity
        disparity = (baseline * focal_length) / (depth_normalized + 1e-6)
        disparity = np.clip(disparity, -50, 50).astype(np.int32)
        
        # Create left and right views
        left = np.zeros_like(color)
        right = np.zeros_like(color)
        
        for y in range(h):
            for x in range(w):
                d = disparity[y, x]
                
                # Left view: shift right
                x_left = min(x + d, w - 1)
                left[y, x] = color[y, x_left]
                
                # Right view: shift left
                x_right = max(x - d, 0)
                right[y, x] = color[y, x_right]
        
        return left, right
    
    def _convert_mono_to_stereo(self, mono: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert mono view to stereo (simple copy)
        
        Args:
            mono: Mono image
            
        Returns:
            Tuple of (left, right) views
        """
        # In production, use StereoCrafter or similar
        return mono.copy(), mono.copy()
    
    def _interpolate_frames(self, frames: np.ndarray) -> np.ndarray:
        """
        Interpolate frames to 120fps
        
        Args:
            frames: Input frames
            
        Returns:
            Interpolated frames
        """
        # Calculate interpolation ratio
        input_fps = self.camera_capture.fps
        target_fps = 120.0
        ratio = int(target_fps / input_fps)
        
        if ratio <= 1:
            return frames
            
        # Interpolate frames
        return self.interpolator.interpolate(frames, ratio)
    
    def _upscale_frames(self, frames: np.ndarray) -> np.ndarray:
        """
        Upscale frames to 4K
        
        Args:
            frames: Input frames
            
        Returns:
            Upscaled frames
        """
        return self.upscaler.upscale(frames)
    
    def _apply_cadence(
        self,
        left: np.ndarray,
        right: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply MAGI frame cadence
        
        Args:
            left: Left eye frames
            right: Right eye frames
            
        Returns:
            Tuple of (left, right) frames with cadence applied
        """
        return self.cadence.apply_cadence(left, right)
    
    def _write_magi_frames(self, left: np.ndarray, right: np.ndarray) -> None:
        """
        Write frames to MAGI file or stream
        
        Args:
            left: Left eye frames
            right: Right eye frames
        """
        # Write to file if file output is enabled
        if self.output_mode in [OutputMode.FILE_ONLY, OutputMode.BOTH] and self.magi_writer:
            # Write frames in alternating pattern
            for i in range(min(len(left), len(right))):
                if i % 2 == 0:
                    self.magi_writer.write_frame(left[i], eye="left")
                else:
                    self.magi_writer.write_frame(right[i], eye="right")
        
        # Always add to output queue for streaming
        for i in range(min(len(left), len(right))):
            if i % 2 == 0:
                frame_data = (left[i], "left")
            else:
                frame_data = (right[i], "right")
            
            try:
                self.output_queue.put(frame_data, timeout=0.01)
            except queue.Full:
                self.stats.frames_dropped += 1
    
    def _update_stats(self) -> None:
        """Update processing statistics"""
        current_time = time.time()
        elapsed = current_time - self.stats.start_time
        
        if elapsed > 0:
            self.stats.fps = self.stats.frames_processed / elapsed
            
        self.stats.current_latency = current_time - self.stats.last_frame_time
        self.stats.avg_latency = (
            self.stats.avg_latency * 0.9 + self.stats.current_latency * 0.1
        )
        self.stats.last_frame_time = current_time
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get processing statistics
        
        Returns:
            Dictionary of statistics
        """
        return {
            "fps": self.stats.fps,
            "frames_processed": self.stats.frames_processed,
            "frames_dropped": self.stats.frames_dropped,
            "avg_latency": self.stats.avg_latency,
            "current_latency": self.stats.current_latency,
            "processing_times": self.stats.processing_times.copy(),
            "mode": self.mode.value,
            "camera_type": self.camera_capture.camera_type.value,
            "camera_fps": self.camera_capture.fps
        }
    
    def get_output_frame(self, timeout: float = 1.0) -> Optional[Tuple[np.ndarray, str]]:
        """
        Get the latest output frame for streaming
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (frame, eye) where eye is "left" or "right", or None
        """
        try:
            return self.output_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def is_running(self) -> bool:
        """Check if pipeline is running"""
        return self.running
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
