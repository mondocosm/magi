"""
Frame extraction for MAGI Pipeline
"""

import cv2
import numpy as np
from typing import Iterator, Tuple, Optional, Dict, Any
from pathlib import Path
import queue
import threading

from ..core.exceptions import InputError
from ..core.logger import LoggerMixin


class FrameExtractor(LoggerMixin):
    """Extract frames from video files for processing"""
    
    def __init__(self, buffer_size: int = 8):
        """
        Initialize frame extractor
        
        Args:
            buffer_size: Number of frames to buffer
        """
        self.buffer_size = buffer_size
        self.cap = None
        self.frame_queue = queue.Queue(maxsize=buffer_size)
        self.stop_event = threading.Event()
        self.extractor_thread = None
        self.logger.info(f"FrameExtractor initialized with buffer size: {buffer_size}")
    
    def open(self, video_path: str) -> bool:
        """
        Open video file for frame extraction
        
        Args:
            video_path: Path to video file
            
        Returns:
            True if successful, False otherwise
        """
        if not Path(video_path).exists():
            raise InputError(f"Video file not found: {video_path}")
        
        try:
            self.cap = cv2.VideoCapture(video_path)
            
            if not self.cap.isOpened():
                raise InputError(f"Could not open video file: {video_path}")
            
            self.logger.info(f"Opened video file: {video_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error opening video file: {e}")
            return False
    
    def close(self):
        """Close video file and stop extraction"""
        self.stop_event.set()
        
        if self.extractor_thread and self.extractor_thread.is_alive():
            self.extractor_thread.join(timeout=5.0)
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.logger.info("Frame extractor closed")
    
    def start_extraction(self):
        """Start frame extraction in background thread"""
        if not self.cap:
            raise InputError("Video file not opened")
        
        self.stop_event.clear()
        self.extractor_thread = threading.Thread(target=self._extract_frames, daemon=True)
        self.extractor_thread.start()
        self.logger.info("Frame extraction started")
    
    def _extract_frames(self):
        """Extract frames from video in background thread"""
        frame_count = 0
        
        while not self.stop_event.is_set():
            ret, frame = self.cap.read()
            
            if not ret:
                self.logger.info(f"End of video reached at frame {frame_count}")
                break
            
            try:
                # Put frame in queue (blocks if queue is full)
                self.frame_queue.put((frame_count, frame), timeout=1.0)
                frame_count += 1
                
            except queue.Full:
                self.logger.warning("Frame queue full, dropping frame")
                continue
        
        # Signal end of stream
        self.frame_queue.put((None, None))
        self.logger.info(f"Frame extraction completed. Total frames: {frame_count}")
    
    def get_frame(self) -> Optional[Tuple[int, np.ndarray]]:
        """
        Get next frame from queue
        
        Returns:
            Tuple of (frame_number, frame) or None if end of stream
        """
        try:
            frame_num, frame = self.frame_queue.get(timeout=5.0)
            
            if frame_num is None:
                return None
            
            return (frame_num, frame)
            
        except queue.Empty:
            self.logger.warning("Timeout waiting for frame")
            return None
    
    def extract_all_frames(self) -> Iterator[Tuple[int, np.ndarray]]:
        """
        Extract all frames from video (synchronous)
        
        Yields:
            Tuple of (frame_number, frame)
        """
        if not self.cap:
            raise InputError("Video file not opened")
        
        frame_count = 0
        
        while True:
            ret, frame = self.cap.read()
            
            if not ret:
                break
            
            yield (frame_count, frame)
            frame_count += 1
        
        self.logger.info(f"Extracted {frame_count} frames")
    
    def extract_frame_range(self, start_frame: int, end_frame: int) -> Iterator[Tuple[int, np.ndarray]]:
        """
        Extract frames from a specific range
        
        Args:
            start_frame: Starting frame number
            end_frame: Ending frame number
            
        Yields:
            Tuple of (frame_number, frame)
        """
        if not self.cap:
            raise InputError("Video file not opened")
        
        # Set position to start frame
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        frame_count = start_frame
        
        while frame_count <= end_frame:
            ret, frame = self.cap.read()
            
            if not ret:
                break
            
            yield (frame_count, frame)
            frame_count += 1
        
        self.logger.info(f"Extracted frames {start_frame} to {frame_count - 1}")
    
    def extract_sample_frames(self, num_samples: int = 10) -> list:
        """
        Extract sample frames evenly distributed throughout the video
        
        Args:
            num_samples: Number of sample frames to extract
            
        Returns:
            List of (frame_number, frame) tuples
        """
        if not self.cap:
            raise InputError("Video file not opened")
        
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames == 0:
            return []
        
        # Calculate sample positions
        sample_positions = [int(i * total_frames / num_samples) for i in range(num_samples)]
        
        samples = []
        
        for pos in sample_positions:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
            ret, frame = self.cap.read()
            
            if ret:
                samples.append((pos, frame))
        
        self.logger.info(f"Extracted {len(samples)} sample frames")
        return samples
    
    def get_video_properties(self) -> Dict[str, Any]:
        """
        Get video properties
        
        Returns:
            Dictionary with video properties
        """
        if not self.cap:
            return {}
        
        return {
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': self.cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'duration': int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) / self.cap.get(cv2.CAP_PROP_FPS) if self.cap.get(cv2.CAP_PROP_FPS) > 0 else 0
        }
    
    def seek_to_frame(self, frame_number: int) -> bool:
        """
        Seek to specific frame
        
        Args:
            frame_number: Frame number to seek to
            
        Returns:
            True if successful, False otherwise
        """
        if not self.cap:
            return False
        
        return self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    
    def seek_to_time(self, time_seconds: float) -> bool:
        """
        Seek to specific time
        
        Args:
            time_seconds: Time in seconds to seek to
            
        Returns:
            True if successful, False otherwise
        """
        if not self.cap:
            return False
        
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            return False
        
        frame_number = int(time_seconds * fps)
        return self.seek_to_frame(frame_number)


class StereoFrameExtractor(FrameExtractor):
    """Extract stereo (3D) frames from video files"""
    
    def __init__(self, buffer_size: int = 8, stereo_format: str = "side_by_side"):
        """
        Initialize stereo frame extractor
        
        Args:
            buffer_size: Number of frames to buffer
            stereo_format: Stereo format (side_by_side, top_bottom, frame_sequential)
        """
        super().__init__(buffer_size)
        self.stereo_format = stereo_format
        self.logger.info(f"StereoFrameExtractor initialized with format: {stereo_format}")
    
    def extract_stereo_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract left and right eye frames from stereo frame
        
        Args:
            frame: Stereo frame
            
        Returns:
            Tuple of (left_frame, right_frame)
        """
        if self.stereo_format == "side_by_side":
            return self._extract_side_by_side(frame)
        elif self.stereo_format == "top_bottom":
            return self._extract_top_bottom(frame)
        elif self.stereo_format == "frame_sequential":
            return self._extract_frame_sequential(frame)
        else:
            raise InputError(f"Unknown stereo format: {self.stereo_format}")
    
    def _extract_side_by_side(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract left and right frames from side-by-side format
        
        Args:
            frame: Side-by-side frame
            
        Returns:
            Tuple of (left_frame, right_frame)
        """
        width = frame.shape[1]
        mid_point = width // 2
        
        left_frame = frame[:, :mid_point]
        right_frame = frame[:, mid_point:]
        
        return left_frame, right_frame
    
    def _extract_top_bottom(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract left and right frames from top-bottom format
        
        Args:
            frame: Top-bottom frame
            
        Returns:
            Tuple of (left_frame, right_frame)
        """
        height = frame.shape[0]
        mid_point = height // 2
        
        left_frame = frame[:mid_point, :]
        right_frame = frame[mid_point:, :]
        
        return left_frame, right_frame
    
    def _extract_frame_sequential(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract left and right frames from frame-sequential format
        
        Args:
            frame: Current frame (need to track frame parity)
            
        Returns:
            Tuple of (left_frame, right_frame)
        """
        # For frame-sequential, we need to track which eye we're on
        # This is handled by the frame number
        # Left frames are even, right frames are odd
        return frame, frame  # Will be handled by frame number tracking
    
    def get_stereo_frames(self) -> Iterator[Tuple[int, np.ndarray, np.ndarray]]:
        """
        Extract stereo frames from video
        
        Yields:
            Tuple of (frame_number, left_frame, right_frame)
        """
        if not self.cap:
            raise InputError("Video file not opened")
        
        frame_count = 0
        prev_frame = None
        
        while True:
            ret, frame = self.cap.read()
            
            if not ret:
                break
            
            if self.stereo_format == "frame_sequential":
                # Frame-sequential: alternate between left and right
                if frame_count % 2 == 0:
                    # Left frame
                    left_frame = frame
                    if prev_frame is not None:
                        yield (frame_count - 1, left_frame, prev_frame)
                else:
                    # Right frame
                    right_frame = frame
                    if prev_frame is not None:
                        yield (frame_count - 1, prev_frame, right_frame)
                
                prev_frame = frame
            else:
                # Side-by-side or top-bottom
                left_frame, right_frame = self.extract_stereo_frame(frame)
                yield (frame_count, left_frame, right_frame)
            
            frame_count += 1
        
        self.logger.info(f"Extracted {frame_count} stereo frames")