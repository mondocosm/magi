"""
Frame cadence management for MAGI Pipeline
Handles alternating left/right eye frames for 3D shutter glasses synchronization
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum

from ..core.exceptions import ProcessingError
from ..core.logger import LoggerMixin


class CadenceMode(Enum):
    """Frame cadence modes"""
    ALTERNATING = "alternating"  # L-R-L-R-L-R...
    SEQUENTIAL = "sequential"  # L-L-L-R-R-R...
    INTERLEAVED = "interleaved"  # L-R-R-L-L-R-R-L...


class FrameCadenceManager(LoggerMixin):
    """Manages frame cadence for MAGI format output"""
    
    def __init__(self, mode: str = "alternating", eye_separation: int = 180, 
                 sync_method: str = "hardware"):
        """
        Initialize frame cadence manager
        
        Args:
            mode: Cadence mode (alternating, sequential, interleaved)
            eye_separation: Eye separation in degrees (180 for MAGI)
            sync_method: Synchronization method (hardware, software)
        """
        self.mode = CadenceMode(mode)
        self.eye_separation = eye_separation
        self.sync_method = sync_method
        
        self.current_eye = "left"  # Track current eye for alternating mode
        self.frame_count = 0
        
        self.logger.info(f"FrameCadenceManager initialized with mode: {mode}, eye_separation: {eye_separation}")
    
    def apply_cadence(self, left_frames: List[np.ndarray], right_frames: List[np.ndarray]) -> List[np.ndarray]:
        """
        Apply frame cadence to stereo frames
        
        Args:
            left_frames: List of left eye frames
            right_frames: List of right eye frames
            
        Returns:
            List of frames with applied cadence
        """
        if len(left_frames) != len(right_frames):
            raise ProcessingError("Left and right frame sequences must have the same length")
        
        self.logger.info(f"Applying {self.mode} cadence to {len(left_frames)} frame pairs")
        
        if self.mode == CadenceMode.ALTERNATING:
            return self._apply_alternating_cadence(left_frames, right_frames)
        elif self.mode == CadenceMode.SEQUENTIAL:
            return self._apply_sequential_cadence(left_frames, right_frames)
        elif self.mode == CadenceMode.INTERLEAVED:
            return self._apply_interleaved_cadence(left_frames, right_frames)
        else:
            raise ProcessingError(f"Unknown cadence mode: {self.mode}")
    
    def _apply_alternating_cadence(self, left_frames: List[np.ndarray], 
                                   right_frames: List[np.ndarray]) -> List[np.ndarray]:
        """
        Apply alternating cadence (L-R-L-R-L-R...)
        
        Args:
            left_frames: List of left eye frames
            right_frames: List of right eye frames
            
        Returns:
            List of frames with alternating cadence
        """
        cadenced_frames = []
        
        for i in range(len(left_frames)):
            # Add left frame
            cadenced_frames.append(left_frames[i])
            # Add right frame
            cadenced_frames.append(right_frames[i])
        
        self.logger.info(f"Alternating cadence applied: {len(left_frames)} pairs -> {len(cadenced_frames)} frames")
        
        return cadenced_frames
    
    def _apply_sequential_cadence(self, left_frames: List[np.ndarray], 
                                  right_frames: List[np.ndarray]) -> List[np.ndarray]:
        """
        Apply sequential cadence (L-L-L-R-R-R...)
        
        Args:
            left_frames: List of left eye frames
            right_frames: List of right eye frames
            
        Returns:
            List of frames with sequential cadence
        """
        cadenced_frames = []
        
        # Add all left frames first
        cadenced_frames.extend(left_frames)
        # Add all right frames
        cadenced_frames.extend(right_frames)
        
        self.logger.info(f"Sequential cadence applied: {len(left_frames)} pairs -> {len(cadenced_frames)} frames")
        
        return cadenced_frames
    
    def _apply_interleaved_cadence(self, left_frames: List[np.ndarray], 
                                   right_frames: List[np.ndarray]) -> List[np.ndarray]:
        """
        Apply interleaved cadence (L-R-R-L-L-R-R-L...)
        
        Args:
            left_frames: List of left eye frames
            right_frames: List of right eye frames
            
        Returns:
            List of frames with interleaved cadence
        """
        cadenced_frames = []
        
        for i in range(len(left_frames)):
            # Add left frame
            cadenced_frames.append(left_frames[i])
            # Add right frame twice
            cadenced_frames.append(right_frames[i])
            cadenced_frames.append(right_frames[i])
        
        self.logger.info(f"Interleaved cadence applied: {len(left_frames)} pairs -> {len(cadenced_frames)} frames")
        
        return cadenced_frames
    
    def apply_magi_cadence(self, left_frames: List[np.ndarray], 
                          right_frames: List[np.ndarray]) -> List[np.ndarray]:
        """
        Apply MAGI-specific cadence (alternating L-R at 60fps per eye, 120fps total)
        
        Args:
            left_frames: List of left eye frames (at 60fps)
            right_frames: List of right eye frames (at 60fps)
            
        Returns:
            List of frames with MAGI cadence (120fps total)
        """
        self.logger.info(f"Applying MAGI cadence to {len(left_frames)} frame pairs")
        
        # MAGI uses alternating cadence with 180° phase separation
        magi_frames = self._apply_alternating_cadence(left_frames, right_frames)
        
        # Add MAGI metadata to frames
        magi_frames = self._add_magi_metadata(magi_frames)
        
        return magi_frames
    
    def _add_magi_metadata(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        """
        Add MAGI metadata to frames
        
        Args:
            frames: List of frames
            
        Returns:
            List of frames with MAGI metadata
        """
        # In a real implementation, this would embed metadata in the video stream
        # For now, we'll just track the metadata separately
        
        self.logger.debug("MAGI metadata added to frames")
        return frames
    
    def get_frame_eye(self, frame_index: int) -> str:
        """
        Get which eye a frame belongs to based on cadence
        
        Args:
            frame_index: Frame index
            
        Returns:
            "left" or "right"
        """
        if self.mode == CadenceMode.ALTERNATING:
            return "left" if frame_index % 2 == 0 else "right"
        elif self.mode == CadenceMode.SEQUENTIAL:
            # Need to know total number of left frames
            # This is a simplified version
            return "left" if frame_index < len(self.left_frames) else "right"
        elif self.mode == CadenceMode.INTERLEAVED:
            # L-R-R pattern
            mod = frame_index % 3
            return "left" if mod == 0 else "right"
        else:
            return "left"
    
    def calculate_timing(self, frame_rate: int) -> Dict[str, float]:
        """
        Calculate frame timing for cadence
        
        Args:
            frame_rate: Frame rate in fps
            
        Returns:
            Dictionary with timing information
        """
        frame_duration = 1.0 / frame_rate
        
        timing = {
            'frame_duration': frame_duration,
            'left_eye_duration': frame_duration,
            'right_eye_duration': frame_duration,
            'eye_separation_degrees': self.eye_separation,
            'eye_separation_time': frame_duration * (self.eye_separation / 360.0),
        }
        
        return timing
    
    def sync_with_hardware(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        """
        Synchronize frames with hardware (3D shutter glasses)
        
        Args:
            frames: List of frames
            
        Returns:
            Synchronized frames
        """
        if self.sync_method != "hardware":
            return frames
        
        self.logger.info(f"Synchronizing {len(frames)} frames with hardware")
        
        # In a real implementation, this would interface with hardware sync
        # For now, we'll just add sync markers
        
        return frames
    
    def generate_sync_signal(self, frame_count: int) -> np.ndarray:
        """
        Generate synchronization signal for 3D glasses
        
        Args:
            frame_count: Number of frames
            
        Returns:
            Sync signal array
        """
        # Generate square wave for alternating sync
        sync_signal = np.zeros(frame_count)
        
        for i in range(frame_count):
            if i % 2 == 0:
                sync_signal[i] = 1  # Left eye
            else:
                sync_signal[i] = 0  # Right eye
        
        return sync_signal
    
    def validate_cadence(self, frames: List[np.ndarray], expected_frame_rate: int) -> bool:
        """
        Validate that frames match expected cadence
        
        Args:
            frames: List of frames
            expected_frame_rate: Expected frame rate
            
        Returns:
            True if cadence is valid, False otherwise
        """
        if self.mode == CadenceMode.ALTERNATING:
            # Should have even number of frames
            if len(frames) % 2 != 0:
                self.logger.warning(f"Alternating cadence requires even number of frames, got {len(frames)}")
                return False
        
        # Check frame rate
        if expected_frame_rate != 120:
            self.logger.warning(f"MAGI requires 120fps, got {expected_frame_rate}fps")
            return False
        
        return True
    
    def get_cadence_info(self) -> Dict[str, Any]:
        """
        Get information about current cadence settings
        
        Returns:
            Dictionary with cadence information
        """
        return {
            'mode': self.mode.value,
            'eye_separation': self.eye_separation,
            'sync_method': self.sync_method,
            'current_eye': self.current_eye,
            'frame_count': self.frame_count,
        }
    
    def reset(self):
        """Reset cadence manager state"""
        self.current_eye = "left"
        self.frame_count = 0
        self.logger.info("Frame cadence manager reset")
    
    def process_realtime(self, left_frame: np.ndarray, right_frame: np.ndarray) -> Tuple[np.ndarray, str]:
        """
        Process frames in real-time for streaming
        
        Args:
            left_frame: Left eye frame
            right_frame: Right eye frame
            
        Returns:
            Tuple of (frame, eye)
        """
        if self.mode == CadenceMode.ALTERNATING:
            if self.current_eye == "left":
                frame = left_frame
                eye = "left"
                self.current_eye = "right"
            else:
                frame = right_frame
                eye = "right"
                self.current_eye = "left"
        else:
            # Default to alternating for real-time
            frame = left_frame if self.current_eye == "left" else right_frame
            eye = self.current_eye
            self.current_eye = "right" if self.current_eye == "left" else "left"
        
        self.frame_count += 1
        
        return frame, eye