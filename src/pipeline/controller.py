"""
Main pipeline controller for MAGI Pipeline
Orchestrates all processing modules for video conversion to MAGI format
"""

import time
import numpy as np
from typing import Optional, Dict, Any, Callable
from pathlib import Path
from queue import Queue
import threading

from ..core.config import Config
from ..core.logger import setup_logger, LoggerMixin
from ..core.exceptions import MAGIPipelineError

from ..input import VideoInput
from ..processing import FrameInterpolator, ImageUpscaler, Processor3D, FrameCadenceManager
from ..output import MAGIEncoder


class MAGIPipeline(LoggerMixin):
    """Main pipeline controller for MAGI video conversion"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize MAGI pipeline
        
        Args:
            config: Configuration object (uses default if not provided)
        """
        self.config = config or Config()
        
        # Setup logger
        self.logger = setup_logger(
            name="magipipeline",
            level=self.config.logging.level,
            log_file=self.config.logging.file,
            console=self.config.logging.console,
            log_format=self.config.logging.format
        )
        
        # Initialize components
        self.video_input = None
        self.frame_interpolator = None
        self.image_upscaler = None
        self.processor_3d = None
        self.frame_cadence = None
        self.magi_encoder = None
        
        # Pipeline state
        self.is_processing = False
        self.progress_callback = None
        self.current_progress = 0
        
        # Performance tracking
        self.start_time = None
        self.end_time = None
        
        self.logger.info("MAGI Pipeline initialized")
    
    def load_input(self, input_path: str) -> bool:
        """
        Load input video file
        
        Args:
            input_path: Path to input video file
            
        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"Loading input video: {input_path}")
        
        try:
            # Initialize video input
            self.video_input = VideoInput(buffer_size=self.config.performance.buffer_size)
            
            if not self.video_input.load(input_path):
                raise MAGIPipelineError(f"Could not load video: {input_path}")
            
            # Get video information
            video_info = self.video_input.get_video_info()
            self.logger.info(f"Video loaded: {video_info['video']['width']}x{video_info['video']['height']} @ {video_info['video']['fps']:.2f}fps")
            
            # Get processing requirements
            requirements = self.video_input.get_processing_requirements(
                target_fps=self.config.processing.target_frame_rate,
                target_resolution=self.config.processing.target_resolution
            )
            
            self.logger.info(f"Processing requirements: {requirements}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading input: {e}")
            return False
    
    def initialize_processors(self):
        """Initialize all processing modules"""
        self.logger.info("Initializing processing modules")
        
        # Initialize frame interpolator
        self.frame_interpolator = FrameInterpolator(
            method=self.config.processing.interpolation_method,
            quality=self.config.processing.interpolation_quality,
            use_gpu=self.config.processing.interpolation_gpu
        )
        
        # Initialize image upscaler
        self.image_upscaler = ImageUpscaler(
            method=self.config.processing.upscaling_method,
            model=self.config.processing.upscaling_model,
            use_gpu=self.config.processing.upscaling_gpu
        )
        
        # Initialize 3D processor
        self.processor_3d = Processor3D(
            input_format=self.config.processing.input_format,
            output_format=self.config.processing.output_format,
            depth_estimation=self.config.processing.depth_estimation,
            use_stereocrafter=self.config.processing.use_stereocrafter,
            stereocrafter_path=self.config.processing.stereocrafter_path
        )
        
        # Initialize frame cadence manager
        self.frame_cadence = FrameCadenceManager(
            mode="alternating",
            eye_separation=self.config.output.eye_separation,
            sync_method=self.config.output.sync_method
        )
        
        self.logger.info("Processing modules initialized")
    
    def process(self, output_path: str, progress_callback: Optional[Callable] = None) -> bool:
        """
        Process video to MAGI format
        
        Args:
            output_path: Path to output file
            progress_callback: Optional callback function for progress updates
            
        Returns:
            True if successful, False otherwise
        """
        if not self.video_input:
            raise MAGIPipelineError("No input video loaded")
        
        self.logger.info(f"Starting processing to: {output_path}")
        
        self.is_processing = True
        self.progress_callback = progress_callback
        self.start_time = time.time()
        
        try:
            # Initialize processors
            self.initialize_processors()
            
            # Get video information
            video_info = self.video_input.get_video_info()
            
            # Extract frames
            self.logger.info("Extracting frames from input video")
            frames = []
            for frame_num, frame in self.video_input.get_frames():
                frames.append(frame)
                
                # Update progress
                if self.progress_callback:
                    progress = (frame_num / video_info['video']['frame_count']) * 10
                    self.progress_callback(progress, "Extracting frames")
            
            self.logger.info(f"Extracted {len(frames)} frames")
            
            # Step 1: 3D processing (convert to side-by-side if needed)
            if self.config.processing.processing_3d_enabled:
                self.logger.info("Processing 3D format")
                frames = self.processor_3d.process_sequence(frames)
                
                if self.progress_callback:
                    self.progress_callback(20, "Processing 3D format")
            
            # Step 2: Upscaling to 4K
            if self.config.processing.upscaling_enabled:
                self.logger.info("Upscaling to 4K")
                target_size = (
                    int(self.config.processing.target_resolution.split('x')[0]),
                    int(self.config.processing.target_resolution.split('x')[1])
                )
                frames = self.image_upscaler.upscale_sequence(frames, target_size)
                
                if self.progress_callback:
                    self.progress_callback(40, "Upscaling to 4K")
            
            # Step 3: Frame interpolation to 120fps
            if self.config.processing.interpolation_enabled:
                self.logger.info("Interpolating frames to 120fps")
                current_fps = video_info['video']['fps']
                target_fps = self.config.processing.target_frame_rate
                frames = self.frame_interpolator.interpolate_sequence(frames, target_fps, current_fps)
                
                if self.progress_callback:
                    self.progress_callback(60, "Interpolating frames")
            
            # Step 4: Separate left and right eyes for MAGI cadence
            self.logger.info("Separating stereo frames")
            left_frames = []
            right_frames = []
            
            for frame in frames:
                left, right = self.processor_3d.separate_eyes(frame)
                left_frames.append(left)
                right_frames.append(right)
            
            if self.progress_callback:
                self.progress_callback(70, "Separating stereo frames")
            
            # Step 5: Apply MAGI cadence
            self.logger.info("Applying MAGI cadence")
            magi_frames = self.frame_cadence.apply_magi_cadence(left_frames, right_frames)
            
            if self.progress_callback:
                self.progress_callback(80, "Applying MAGI cadence")
            
            # Step 6: Encode to MAGI format
            self.logger.info("Encoding to MAGI format")
            self.magi_encoder = MAGIEncoder(
                output_path=output_path,
                frame_rate=self.config.processing.target_frame_rate,
                resolution=self.config.processing.target_resolution
            )
            
            # Extract audio path if available
            audio_path = self.video_input.video_path if self.config.input.preserve_audio else None
            
            self.magi_encoder.encode(left_frames, right_frames, audio_path)
            
            if self.progress_callback:
                self.progress_callback(100, "Encoding complete")
            
            self.end_time = time.time()
            processing_time = self.end_time - self.start_time
            
            self.logger.info(f"Processing complete in {processing_time:.2f} seconds")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error during processing: {e}")
            return False
            
        finally:
            self.is_processing = False
            self.cleanup()
    
    def process_realtime(self, output_path: str, display_callback: Optional[Callable] = None) -> bool:
        """
        Process video in real-time for streaming
        
        Args:
            output_path: Path to output file (or stream URL)
            display_callback: Optional callback for displaying frames
            
        Returns:
            True if successful, False otherwise
        """
        if not self.video_input:
            raise MAGIPipelineError("No input video loaded")
        
        self.logger.info(f"Starting real-time processing to: {output_path}")
        
        self.is_processing = True
        self.start_time = time.time()
        
        try:
            # Initialize processors
            self.initialize_processors()
            
            # Get video information
            video_info = self.video_input.get_video_info()
            
            # Process frames in real-time
            frame_buffer = []
            left_buffer = []
            right_buffer = []
            
            for frame_num, frame in self.video_input.get_frames():
                # Process frame
                processed_frame = self._process_single_frame(frame, frame_num)
                
                # Separate eyes
                left, right = self.processor_3d.separate_eyes(processed_frame)
                left_buffer.append(left)
                right_buffer.append(right)
                
                # Apply cadence and output
                if len(left_buffer) >= 2:
                    magi_frame = self.frame_cadence.apply_magi_cadence([left_buffer[0]], [right_buffer[0]])[0]
                    
                    # Display or output frame
                    if display_callback:
                        display_callback(magi_frame)
                    
                    # Remove processed frames
                    left_buffer.pop(0)
                    right_buffer.pop(0)
            
            self.end_time = time.time()
            processing_time = self.end_time - self.start_time
            
            self.logger.info(f"Real-time processing complete in {processing_time:.2f} seconds")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error during real-time processing: {e}")
            return False
            
        finally:
            self.is_processing = False
            self.cleanup()
    
    def _process_single_frame(self, frame: np.ndarray, frame_num: int) -> np.ndarray:
        """
        Process a single frame
        
        Args:
            frame: Input frame
            frame_num: Frame number
            
        Returns:
            Processed frame
        """
        # 3D processing
        if self.config.processing.processing_3d_enabled:
            frame = self.processor_3d.convert_to_side_by_side(frame)
        
        # Upscaling
        if self.config.processing.upscaling_enabled:
            target_size = (
                int(self.config.processing.target_resolution.split('x')[0]),
                int(self.config.processing.target_resolution.split('x')[1])
            )
            frame = self.image_upscaler.upscale(frame, target_size)
        
        return frame
    
    def get_processing_info(self) -> Dict[str, Any]:
        """
        Get current processing information
        
        Returns:
            Dictionary with processing information
        """
        info = {
            'is_processing': self.is_processing,
            'current_progress': self.current_progress,
        }
        
        if self.video_input:
            video_info = self.video_input.get_video_info()
            info['input'] = {
                'path': self.video_input.video_path,
                'resolution': f"{video_info['video']['width']}x{video_info['video']['height']}",
                'fps': video_info['video']['fps'],
                'is_3d': video_info['3d']['is_3d'],
                '3d_format': video_info['3d']['format'],
            }
        
        if self.start_time and self.end_time:
            info['processing_time'] = self.end_time - self.start_time
        elif self.start_time:
            info['elapsed_time'] = time.time() - self.start_time
        
        return info
    
    def cancel(self):
        """Cancel current processing"""
        if self.is_processing:
            self.logger.info("Cancelling processing")
            self.is_processing = False
    
    def cleanup(self):
        """Clean up resources"""
        if self.video_input:
            self.video_input.close()
        
        self.logger.info("Pipeline cleanup complete")
    
    def __del__(self):
        """Destructor"""
        self.cleanup()