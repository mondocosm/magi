"""
3D processing for MAGI Pipeline
Handles 3D format conversion and left/right eye separation
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional, Dict, Any
from enum import Enum

from ..core.exceptions import ProcessingError
from ..core.logger import LoggerMixin
from .stereocrafter import StereoCrafterIntegration


class StereoFormat(Enum):
    """Stereo 3D formats"""
    SIDE_BY_SIDE = "side_by_side"
    TOP_BOTTOM = "top_bottom"
    FRAME_SEQUENTIAL = "frame_sequential"
    ANAGLYPH = "anaglyph"
    CHECKERBOARD = "checkerboard"


class Processor3D(LoggerMixin):
    """3D processor for format conversion and eye separation"""
    
    def __init__(self, input_format: str = "auto", output_format: str = "side_by_side", 
                 depth_estimation: bool = True, use_stereocrafter: bool = True,
                 stereocrafter_path: Optional[str] = None):
        """
        Initialize 3D processor
        
        Args:
            input_format: Input 3D format (auto, side_by_side, top_bottom, frame_sequential, etc.)
            output_format: Output 3D format (side_by_side for MAGI)
            depth_estimation: Whether to enable depth estimation for 2D to 3D conversion
            use_stereocrafter: Whether to use StereoCrafter for high-quality 2D to 3D conversion
            stereocrafter_path: Path to StereoCrafter directory
        """
        self.input_format = input_format
        self.output_format = StereoFormat(output_format)
        self.depth_estimation = depth_estimation
        self.use_stereocrafter = use_stereocrafter
        
        # Initialize StereoCrafter if enabled
        self.stereocrafter = None
        if use_stereocrafter:
            self.stereocrafter = StereoCrafterIntegration(
                stereocrafter_path=stereocrafter_path or "../StereoCrafter"
            )
            if self.stereocrafter.is_available():
                self.logger.info("StereoCrafter integration enabled for high-quality 2D to 3D conversion")
            else:
                self.logger.warning("StereoCrafter not available, falling back to simple depth estimation")
                self.use_stereocrafter = False
        
        self.logger.info(f"Processor3D initialized with input_format: {input_format}, output_format: {output_format}")
    
    def convert_to_side_by_side(self, frame: np.ndarray, input_format: Optional[str] = None) -> np.ndarray:
        """
        Convert frame to side-by-side format
        
        Args:
            frame: Input frame
            input_format: Input format (uses class default if not specified)
            
        Returns:
            Side-by-side frame
        """
        fmt = input_format or self.input_format
        
        if fmt == "auto":
            fmt = self._detect_format(frame)
        
        if fmt == "side_by_side":
            return frame  # Already in side-by-side format
        elif fmt == "top_bottom":
            return self._convert_top_bottom_to_sbs(frame)
        elif fmt == "frame_sequential":
            raise ProcessingError("Frame-sequential requires two consecutive frames")
        elif fmt == "anaglyph":
            return self._convert_anaglyph_to_sbs(frame)
        elif fmt == "2d":
            return self._convert_2d_to_sbs(frame)
        else:
            raise ProcessingError(f"Unknown input format: {fmt}")
    
    def _detect_format(self, frame: np.ndarray) -> str:
        """
        Detect 3D format of frame
        
        Args:
            frame: Input frame
            
        Returns:
            Detected format string
        """
        height, width = frame.shape[:2]
        
        # Check aspect ratio for common formats
        aspect_ratio = width / height
        
        # Side-by-side: typically 2:1 or wider
        if aspect_ratio >= 2.0:
            return "side_by_side"
        # Top-bottom: typically 1:2 or taller
        elif aspect_ratio <= 0.5:
            return "top_bottom"
        # Check for anaglyph (color channels)
        elif self._is_anaglyph(frame):
            return "anaglyph"
        else:
            return "2d"
    
    def _is_anaglyph(self, frame: np.ndarray) -> bool:
        """
        Check if frame is in anaglyph format
        
        Args:
            frame: Input frame
            
        Returns:
            True if anaglyph format detected
        """
        if len(frame.shape) < 3:
            return False
        
        # Split color channels
        red_channel = frame[:, :, 0]
        green_channel = frame[:, :, 1]
        blue_channel = frame[:, :, 2]
        
        # Calculate similarity between red and green+blue (cyan)
        cyan_channel = cv2.addWeighted(green_channel, 0.5, blue_channel, 0.5, 0)
        
        # Calculate correlation
        correlation = np.corrcoef(red_channel.flatten(), cyan_channel.flatten())[0, 1]
        
        # Anaglyph should have lower correlation
        return correlation < 0.7
    
    def _convert_top_bottom_to_sbs(self, frame: np.ndarray) -> np.ndarray:
        """
        Convert top-bottom format to side-by-side
        
        Args:
            frame: Top-bottom frame
            
        Returns:
            Side-by-side frame
        """
        height, width = frame.shape[:2]
        mid_point = height // 2
        
        # Split into top and bottom
        top_half = frame[:mid_point, :]
        bottom_half = frame[mid_point:, :]
        
        # Resize halves to match original width
        top_resized = cv2.resize(top_half, (width // 2, height))
        bottom_resized = cv2.resize(bottom_half, (width // 2, height))
        
        # Combine side-by-side
        sbs_frame = np.hstack([top_resized, bottom_resized])
        
        return sbs_frame
    
    def _convert_anaglyph_to_sbs(self, frame: np.ndarray) -> np.ndarray:
        """
        Convert anaglyph format to side-by-side
        
        Args:
            frame: Anaglyph frame
            
        Returns:
            Side-by-side frame
        """
        if len(frame.shape) < 3:
            raise ProcessingError("Anaglyph frame must have 3 channels")
        
        # Extract red channel (left eye)
        left_eye = frame[:, :, 0]
        
        # Extract cyan channel (right eye) - average of green and blue
        right_eye = cv2.addWeighted(frame[:, :, 1], 0.5, frame[:, :, 2], 0.5, 0)
        
        # Convert to 3-channel
        left_eye_3ch = cv2.cvtColor(left_eye, cv2.COLOR_GRAY2BGR)
        right_eye_3ch = cv2.cvtColor(right_eye, cv2.COLOR_GRAY2BGR)
        
        # Combine side-by-side
        sbs_frame = np.hstack([left_eye_3ch, right_eye_3ch])
        
        return sbs_frame
    
    def _convert_2d_to_sbs(self, frame: np.ndarray) -> np.ndarray:
        """
        Convert 2D frame to side-by-side 3D using depth estimation or StereoCrafter
        
        Args:
            frame: 2D frame
            
        Returns:
            Side-by-side 3D frame
        """
        if not self.depth_estimation:
            # Simple duplication if depth estimation is disabled
            return np.hstack([frame, frame])
        
        # Use StereoCrafter if available for high-quality conversion
        if self.use_stereocrafter and self.stereocrafter and self.stereocrafter.is_available():
            try:
                left_view, right_view = self.stereocrafter.convert_frame_to_3d(frame)
                sbs_frame = np.hstack([left_view, right_view])
                self.logger.debug("Used StereoCrafter for 2D to 3D conversion")
                return sbs_frame
            except Exception as e:
                self.logger.warning(f"StereoCrafter conversion failed: {e}, falling back to depth estimation")
        
        # Fall back to depth estimation
        depth_map = self._estimate_depth(frame)
        
        # Generate left and right views
        left_view = self._shift_view(frame, depth_map, shift_amount=-5)
        right_view = self._shift_view(frame, depth_map, shift_amount=5)
        
        # Combine side-by-side
        sbs_frame = np.hstack([left_view, right_view])
        
        return sbs_frame
    
    def _estimate_depth(self, frame: np.ndarray) -> np.ndarray:
        """
        Estimate depth map from 2D frame
        
        Args:
            frame: Input frame
            
        Returns:
            Depth map
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Simple depth estimation based on gradient and edge detection
        # This is a simplified approach - for production, use a proper depth estimation model
        
        # Calculate gradients
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Calculate gradient magnitude
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Normalize to 0-1 range
        depth_map = gradient_magnitude / np.max(gradient_magnitude)
        
        # Invert (edges are typically closer)
        depth_map = 1.0 - depth_map
        
        # Apply Gaussian blur for smoothness
        depth_map = cv2.GaussianBlur(depth_map, (15, 15), 0)
        
        return depth_map
    
    def _shift_view(self, frame: np.ndarray, depth_map: np.ndarray, shift_amount: int) -> np.ndarray:
        """
        Shift view based on depth map
        
        Args:
            frame: Input frame
            depth_map: Depth map
            shift_amount: Amount to shift (positive = right, negative = left)
            
        Returns:
            Shifted view
        """
        height, width = frame.shape[:2]
        shifted = np.zeros_like(frame)
        
        # Create mesh grid
        x_coords, y_coords = np.meshgrid(np.arange(width), np.arange(height))
        
        # Calculate shift based on depth
        shift = depth_map * shift_amount
        
        # Apply shift to x coordinates
        x_shifted = x_coords + shift
        
        # Clip to valid range
        x_shifted = np.clip(x_shifted, 0, width - 1)
        
        # Remap frame
        for c in range(frame.shape[2]):
            shifted[:, :, c] = cv2.remap(
                frame[:, :, c],
                x_shifted.astype(np.float32),
                y_coords.astype(np.float32),
                cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REFLECT
            )
        
        return shifted
    
    def separate_eyes(self, sbs_frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Separate left and right eyes from side-by-side frame
        
        Args:
            sbs_frame: Side-by-side frame
            
        Returns:
            Tuple of (left_eye, right_eye)
        """
        width = sbs_frame.shape[1]
        mid_point = width // 2
        
        left_eye = sbs_frame[:, :mid_point]
        right_eye = sbs_frame[:, mid_point:]
        
        return left_eye, right_eye
    
    def combine_eyes(self, left_eye: np.ndarray, right_eye: np.ndarray, 
                     output_format: Optional[StereoFormat] = None) -> np.ndarray:
        """
        Combine left and right eyes into specified format
        
        Args:
            left_eye: Left eye frame
            right_eye: Right eye frame
            output_format: Output format (uses class default if not specified)
            
        Returns:
            Combined frame
        """
        fmt = output_format or self.output_format
        
        if fmt == StereoFormat.SIDE_BY_SIDE:
            return np.hstack([left_eye, right_eye])
        elif fmt == StereoFormat.TOP_BOTTOM:
            return np.vstack([left_eye, right_eye])
        elif fmt == StereoFormat.ANAGLYPH:
            return self._create_anaglyph(left_eye, right_eye)
        else:
            raise ProcessingError(f"Unsupported output format: {fmt}")
    
    def _create_anaglyph(self, left_eye: np.ndarray, right_eye: np.ndarray) -> np.ndarray:
        """
        Create anaglyph from left and right eyes
        
        Args:
            left_eye: Left eye frame
            right_eye: Right eye frame
            
        Returns:
            Anaglyph frame
        """
        if len(left_eye.shape) < 3:
            left_eye = cv2.cvtColor(left_eye, cv2.COLOR_GRAY2BGR)
        if len(right_eye.shape) < 3:
            right_eye = cv2.cvtColor(right_eye, cv2.COLOR_GRAY2BGR)
        
        # Extract red channel from left eye
        red_channel = left_eye[:, :, 0]
        
        # Extract cyan channels from right eye
        cyan_channel = cv2.addWeighted(right_eye[:, :, 1], 0.5, right_eye[:, :, 2], 0.5, 0)
        
        # Create anaglyph
        anaglyph = np.zeros_like(left_eye)
        anaglyph[:, :, 0] = red_channel
        anaglyph[:, :, 1] = cyan_channel
        anaglyph[:, :, 2] = cyan_channel
        
        return anaglyph
    
    def process_frame_sequential(self, frame1: np.ndarray, frame2: np.ndarray) -> np.ndarray:
        """
        Process frame-sequential format to side-by-side
        
        Args:
            frame1: First frame (left or right eye)
            frame2: Second frame (right or left eye)
            
        Returns:
            Side-by-side frame
        """
        # Ensure frames are the same size
        if frame1.shape != frame2.shape:
            frame2 = cv2.resize(frame2, (frame1.shape[1], frame1.shape[0]))
        
        # Combine side-by-side
        sbs_frame = np.hstack([frame1, frame2])
        
        return sbs_frame
    
    def enhance_depth(self, frame: np.ndarray, depth_map: np.ndarray) -> np.ndarray:
        """
        Enhance 3D effect using depth map
        
        Args:
            frame: Input frame
            depth_map: Depth map
            
        Returns:
            Enhanced frame
        """
        # Apply depth-based enhancement
        # This could include depth-based color adjustment, blur, etc.
        
        # Normalize depth map
        depth_normalized = (depth_map - np.min(depth_map)) / (np.max(depth_map) - np.min(depth_map))
        
        # Apply slight depth-based color adjustment
        enhanced = frame.copy()
        
        # Darken distant areas slightly
        for c in range(3):
            enhanced[:, :, c] = enhanced[:, :, c] * (0.9 + 0.1 * depth_normalized)
        
        return enhanced
    
    def process_sequence(self, frames: List[np.ndarray], input_format: Optional[str] = None) -> List[np.ndarray]:
        """
        Process a sequence of frames to side-by-side format
        
        Args:
            frames: List of input frames
            input_format: Input format (uses class default if not specified)
            
        Returns:
            List of side-by-side frames
        """
        self.logger.info(f"Processing {len(frames)} frames to side-by-side format")
        
        sbs_frames = []
        
        for i, frame in enumerate(frames):
            if i % 10 == 0:
                self.logger.debug(f"Processing frame {i+1}/{len(frames)}")
            
            sbs_frame = self.convert_to_side_by_side(frame, input_format)
            sbs_frames.append(sbs_frame)
        
        self.logger.info(f"3D processing complete: {len(frames)} frames -> {len(sbs_frames)} frames")
        
        return sbs_frames
    
    def convert_video_2d_to_3d(self, input_video: str, output_video: str, 
                               tile_num: int = 1) -> bool:
        """
        Convert entire 2D video to 3D using StereoCrafter
        
        Args:
            input_video: Path to input 2D video
            output_video: Path to output 3D video
            tile_num: Number of tiles for processing (higher = more memory efficient)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.use_stereocrafter or not self.stereocrafter or not self.stereocrafter.is_available():
            raise ProcessingError("StereoCrafter is not available for video-level 2D to 3D conversion")
        
        self.logger.info(f"Converting 2D video to 3D: {input_video} -> {output_video}")
        
        return self.stereocrafter.convert_2d_to_3d(input_video, output_video, tile_num)
    
    def get_stereocrafter_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about StereoCrafter integration
        
        Returns:
            Dictionary with StereoCrafter information or None if not available
        """
        if not self.stereocrafter:
            return None
        
        return {
            'available': self.stereocrafter.is_available(),
            'enabled': self.use_stereocrafter,
            'model_info': self.stereocrafter.get_model_info(),
            'dependencies': self.stereocrafter.check_dependencies(),
        }