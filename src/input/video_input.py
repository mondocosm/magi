"""
Video input handling for MAGI Pipeline
"""

import cv2
import numpy as np
from typing import Dict, Any, Optional, Iterator, Tuple
from pathlib import Path

from .format_detector import FormatDetector
from .frame_extractor import FrameExtractor, StereoFrameExtractor
from ..core.exceptions import InputError
from ..core.logger import LoggerMixin


class VideoInput(LoggerMixin):
    """Main video input handler for MAGI Pipeline"""
    
    def __init__(self, buffer_size: int = 8):
        """
        Initialize video input handler
        
        Args:
            buffer_size: Number of frames to buffer
        """
        self.buffer_size = buffer_size
        self.format_detector = FormatDetector()
        self.frame_extractor = None
        self.stereo_extractor = None
        
        self.video_path = None
        self.video_info = None
        self.is_open = False
        
        self.logger.info(f"VideoInput initialized with buffer size: {buffer_size}")
    
    def load(self, video_path: str) -> bool:
        """
        Load video file
        
        Args:
            video_path: Path to video file
            
        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"Loading video: {video_path}")
        
        if not Path(video_path).exists():
            raise InputError(f"Video file not found: {video_path}")
        
        try:
            # Detect video format and properties
            self.video_info = self.format_detector.detect_video_info(video_path)
            self.video_path = video_path
            
            # Create appropriate frame extractor
            if self.video_info['3d']['is_3d']:
                self.logger.info(f"3D video detected: {self.video_info['3d']['format']}")
                self.stereo_extractor = StereoFrameExtractor(
                    buffer_size=self.buffer_size,
                    stereo_format=self.video_info['3d']['format']
                )
                self.stereo_extractor.open(video_path)
                self.frame_extractor = self.stereo_extractor
            else:
                self.logger.info("2D video detected")
                self.frame_extractor = FrameExtractor(buffer_size=self.buffer_size)
                self.frame_extractor.open(video_path)
            
            self.is_open = True
            self.logger.info(f"Video loaded successfully: {self.video_info['video']['width']}x{self.video_info['video']['height']} @ {self.video_info['video']['fps']:.2f}fps")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading video: {e}")
            self.close()
            return False
    
    def close(self):
        """Close video file and release resources"""
        if self.frame_extractor:
            self.frame_extractor.close()
            self.frame_extractor = None
        
        self.stereo_extractor = None
        self.is_open = False
        self.logger.info("Video input closed")
    
    def get_video_info(self) -> Optional[Dict[str, Any]]:
        """
        Get video information
        
        Returns:
            Dictionary with video information or None if not loaded
        """
        return self.video_info
    
    def is_3d(self) -> bool:
        """
        Check if video is 3D
        
        Returns:
            True if video is 3D, False otherwise
        """
        if not self.video_info:
            return False
        return self.video_info['3d']['is_3d']
    
    def get_3d_format(self) -> str:
        """
        Get 3D format of video
        
        Returns:
            3D format string
        """
        if not self.video_info:
            return "2d"
        return self.video_info['3d']['format']
    
    def get_frame(self) -> Optional[Tuple[int, np.ndarray]]:
        """
        Get next frame from video
        
        Returns:
            Tuple of (frame_number, frame) or None if end of stream
        """
        if not self.is_open or not self.frame_extractor:
            raise InputError("Video not loaded")
        
        return self.frame_extractor.get_frame()
    
    def get_stereo_frame(self) -> Optional[Tuple[int, np.ndarray, np.ndarray]]:
        """
        Get next stereo frame from video
        
        Returns:
            Tuple of (frame_number, left_frame, right_frame) or None if end of stream
        """
        if not self.is_open or not self.stereo_extractor:
            raise InputError("Video not loaded or not 3D")
        
        # Get next frame from stereo extractor
        try:
            for frame_num, left_frame, right_frame in self.stereo_extractor.get_stereo_frames():
                return (frame_num, left_frame, right_frame)
            return None
        except:
            return None
    
    def get_frames(self) -> Iterator[Tuple[int, np.ndarray]]:
        """
        Get all frames from video
        
        Yields:
            Tuple of (frame_number, frame)
        """
        if not self.is_open or not self.frame_extractor:
            raise InputError("Video not loaded")
        
        for frame_num, frame in self.frame_extractor.extract_all_frames():
            yield (frame_num, frame)
    
    def get_stereo_frames(self) -> Iterator[Tuple[int, np.ndarray, np.ndarray]]:
        """
        Get all stereo frames from video
        
        Yields:
            Tuple of (frame_number, left_frame, right_frame)
        """
        if not self.is_open or not self.stereo_extractor:
            raise InputError("Video not loaded or not 3D")
        
        for frame_num, left_frame, right_frame in self.stereo_extractor.get_stereo_frames():
            yield (frame_num, left_frame, right_frame)
    
    def get_sample_frames(self, num_samples: int = 10) -> list:
        """
        Get sample frames from video
        
        Args:
            num_samples: Number of sample frames to extract
            
        Returns:
            List of (frame_number, frame) tuples
        """
        if not self.is_open or not self.frame_extractor:
            raise InputError("Video not loaded")
        
        return self.frame_extractor.extract_sample_frames(num_samples)
    
    def seek_to_frame(self, frame_number: int) -> bool:
        """
        Seek to specific frame
        
        Args:
            frame_number: Frame number to seek to
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_open or not self.frame_extractor:
            return False
        
        return self.frame_extractor.seek_to_frame(frame_number)
    
    def seek_to_time(self, time_seconds: float) -> bool:
        """
        Seek to specific time
        
        Args:
            time_seconds: Time in seconds to seek to
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_open or not self.frame_extractor:
            return False
        
        return self.frame_extractor.seek_to_time(time_seconds)
    
    def get_processing_requirements(self, target_fps: int, target_resolution: str) -> Dict[str, Any]:
        """
        Get processing requirements for this video
        
        Args:
            target_fps: Target frame rate
            target_resolution: Target resolution
            
        Returns:
            Dictionary with processing requirements
        """
        if not self.video_info:
            return {}
        
        # Get interpolation requirements
        interp_req = self.format_detector.get_interpolation_requirements(
            self.video_info, target_fps
        )
        
        # Get upscaling requirements
        upscale_req = self.format_detector.get_upscaling_requirements(
            self.video_info, target_resolution
        )
        
        return {
            'interpolation': interp_req,
            'upscaling': upscale_req,
            'is_3d': self.video_info['3d']['is_3d'],
            '3d_format': self.video_info['3d']['format'],
            'current_fps': self.video_info['video']['fps'],
            'current_resolution': f"{self.video_info['video']['width']}x{self.video_info['video']['height']}",
            'target_fps': target_fps,
            'target_resolution': target_resolution
        }
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False
    
    def __del__(self):
        """Destructor"""
        self.close()