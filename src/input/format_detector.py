"""
Video format detection for MAGI Pipeline
"""

import cv2
import numpy as np
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import ffmpeg

from ..core.exceptions import InputError
from ..core.logger import LoggerMixin


class FormatDetector(LoggerMixin):
    """Detect video format, resolution, frame rate, and 3D format"""
    
    # 3D format types
    FORMAT_2D = "2d"
    FORMAT_SBS = "side_by_side"  # Side-by-side
    FORMAT_TAB = "top_bottom"  # Top-bottom
    FORMAT_FRAME_SEQUENTIAL = "frame_sequential"  # Frame-sequential
    FORMAT_ANAGLYPH = "anaglyph"  # Red-cyan anaglyph
    
    def __init__(self):
        """Initialize format detector"""
        self.logger.info("FormatDetector initialized")
    
    def detect_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Detect comprehensive video information
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary containing video information
        """
        self.logger.info(f"Detecting video info for: {video_path}")
        
        if not Path(video_path).exists():
            raise InputError(f"Video file not found: {video_path}")
        
        # Get basic video properties using FFmpeg
        info = self._get_ffmpeg_info(video_path)
        
        # Get detailed video properties using OpenCV
        cv_info = self._get_opencv_info(video_path)
        
        # Detect 3D format
        format_3d = self.detect_3d_format(video_path, cv_info)
        
        # Combine information
        video_info = {
            'path': video_path,
            'format': info.get('format', 'unknown'),
            'duration': info.get('duration', 0),
            'size': info.get('size', 0),
            'bit_rate': info.get('bit_rate', 0),
            'video': {
                'codec': info.get('video_codec', 'unknown'),
                'width': cv_info.get('width', 0),
                'height': cv_info.get('height', 0),
                'fps': cv_info.get('fps', 0),
                'frame_count': cv_info.get('frame_count', 0),
                'aspect_ratio': cv_info.get('aspect_ratio', 0),
            },
            'audio': {
                'codec': info.get('audio_codec', 'unknown'),
                'sample_rate': info.get('audio_sample_rate', 0),
                'channels': info.get('audio_channels', 0),
            },
            '3d': {
                'format': format_3d,
                'is_3d': format_3d != self.FORMAT_2D,
            }
        }
        
        self.logger.info(f"Video info detected: {video_info['video']['width']}x{video_info['video']['height']} @ {video_info['video']['fps']:.2f}fps, 3D: {video_info['3d']['format']}")
        
        return video_info
    
    def _get_ffmpeg_info(self, video_path: str) -> Dict[str, Any]:
        """
        Get video information using FFmpeg
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with FFmpeg information
        """
        try:
            probe = ffmpeg.probe(video_path)
            
            info = {}
            
            # Format information
            if 'format' in probe:
                format_info = probe['format']
                info['format'] = format_info.get('format_name', 'unknown')
                info['duration'] = float(format_info.get('duration', 0))
                info['size'] = int(format_info.get('size', 0))
                info['bit_rate'] = int(format_info.get('bit_rate', 0))
            
            # Video stream information
            if 'streams' in probe:
                for stream in probe['streams']:
                    if stream.get('codec_type') == 'video':
                        info['video_codec'] = stream.get('codec_name', 'unknown')
                        info['width'] = int(stream.get('width', 0))
                        info['height'] = int(stream.get('height', 0))
                        info['video_bit_rate'] = int(stream.get('bit_rate', 0))
                        
                        # Parse frame rate
                        r_frame_rate = stream.get('r_frame_rate', '0/1')
                        if '/' in r_frame_rate:
                            num, den = map(int, r_frame_rate.split('/'))
                            info['fps'] = num / den if den != 0 else 0
                        else:
                            info['fps'] = float(r_frame_rate)
                    
                    elif stream.get('codec_type') == 'audio':
                        info['audio_codec'] = stream.get('codec_name', 'unknown')
                        info['audio_sample_rate'] = int(stream.get('sample_rate', 0))
                        info['audio_channels'] = int(stream.get('channels', 0))
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting FFmpeg info: {e}")
            return {}
    
    def _get_opencv_info(self, video_path: str) -> Dict[str, Any]:
        """
        Get video information using OpenCV
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with OpenCV information
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise InputError(f"Could not open video file: {video_path}")
            
            info = {}
            
            # Get video properties
            info['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            info['height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            info['fps'] = cap.get(cv2.CAP_PROP_FPS)
            info['frame_count'] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Calculate aspect ratio
            if info['height'] > 0:
                info['aspect_ratio'] = info['width'] / info['height']
            else:
                info['aspect_ratio'] = 0
            
            cap.release()
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting OpenCV info: {e}")
            return {}
    
    def detect_3d_format(self, video_path: str, cv_info: Dict[str, Any]) -> str:
        """
        Detect 3D format of video
        
        Args:
            video_path: Path to video file
            cv_info: OpenCV video information
            
        Returns:
            3D format string
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return self.FORMAT_2D
            
            # Read a few frames to analyze
            frames = []
            for _ in range(5):
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
                else:
                    break
            
            cap.release()
            
            if not frames:
                return self.FORMAT_2D
            
            # Analyze frames for 3D format
            return self._analyze_3d_format(frames, cv_info)
            
        except Exception as e:
            self.logger.error(f"Error detecting 3D format: {e}")
            return self.FORMAT_2D
    
    def _analyze_3d_format(self, frames: list, cv_info: Dict[str, Any]) -> str:
        """
        Analyze frames to determine 3D format
        
        Args:
            frames: List of video frames
            cv_info: OpenCV video information
            
        Returns:
            3D format string
        """
        if not frames:
            return self.FORMAT_2D
        
        width = cv_info.get('width', 0)
        height = cv_info.get('height', 0)
        
        # Check for side-by-side format
        if self._is_side_by_side(frames[0], width, height):
            return self.FORMAT_SBS
        
        # Check for top-bottom format
        if self._is_top_bottom(frames[0], width, height):
            return self.FORMAT_TAB
        
        # Check for frame-sequential format
        if self._is_frame_sequential(frames):
            return self.FORMAT_FRAME_SEQUENTIAL
        
        # Check for anaglyph format
        if self._is_anaglyph(frames[0]):
            return self.FORMAT_ANAGLYPH
        
        # Default to 2D
        return self.FORMAT_2D
    
    def _is_side_by_side(self, frame: np.ndarray, width: int, height: int) -> bool:
        """
        Check if frame is in side-by-side 3D format
        
        Args:
            frame: Video frame
            width: Frame width
            height: Frame height
            
        Returns:
            True if side-by-side format detected
        """
        # Side-by-side: Two halves of the frame should be similar but with slight differences
        if width < 2 * height:  # Not wide enough for side-by-side
            return False
        
        # Split frame into left and right halves
        left_half = frame[:, :width//2]
        right_half = frame[:, width//2:]
        
        # Calculate similarity between halves
        similarity = self._calculate_similarity(left_half, right_half)
        
        # Side-by-side typically has moderate similarity (not too high, not too low)
        return 0.7 < similarity < 0.95
    
    def _is_top_bottom(self, frame: np.ndarray, width: int, height: int) -> bool:
        """
        Check if frame is in top-bottom 3D format
        
        Args:
            frame: Video frame
            width: Frame width
            height: Frame height
            
        Returns:
            True if top-bottom format detected
        """
        # Top-bottom: Two halves of the frame should be similar but with slight differences
        if height < 2 * width:  # Not tall enough for top-bottom
            return False
        
        # Split frame into top and bottom halves
        top_half = frame[:height//2, :]
        bottom_half = frame[height//2:, :]
        
        # Calculate similarity between halves
        similarity = self._calculate_similarity(top_half, bottom_half)
        
        # Top-bottom typically has moderate similarity
        return 0.7 < similarity < 0.95
    
    def _is_frame_sequential(self, frames: list) -> bool:
        """
        Check if frames are in frame-sequential 3D format
        
        Args:
            frames: List of video frames
            
        Returns:
            True if frame-sequential format detected
        """
        if len(frames) < 2:
            return False
        
        # Frame-sequential: Alternating frames should be similar but with slight differences
        # Compare frame 0 with frame 2, frame 1 with frame 3, etc.
        similarities = []
        
        for i in range(0, len(frames) - 2, 2):
            if i + 2 < len(frames):
                sim = self._calculate_similarity(frames[i], frames[i + 2])
                similarities.append(sim)
        
        if not similarities:
            return False
        
        # Frame-sequential should have high similarity between same-eye frames
        avg_similarity = np.mean(similarities)
        return avg_similarity > 0.85
    
    def _is_anaglyph(self, frame: np.ndarray) -> bool:
        """
        Check if frame is in anaglyph 3D format
        
        Args:
            frame: Video frame
            
        Returns:
            True if anaglyph format detected
        """
        # Anaglyph: Red and cyan channels should have different content
        if len(frame.shape) < 3:
            return False
        
        # Split color channels
        red_channel = frame[:, :, 0]
        green_channel = frame[:, :, 1]
        blue_channel = frame[:, :, 2]
        
        # Calculate similarity between red and green+blue (cyan)
        cyan_channel = cv2.addWeighted(green_channel, 0.5, blue_channel, 0.5, 0)
        similarity = self._calculate_similarity(red_channel, cyan_channel)
        
        # Anaglyph should have lower similarity between red and cyan
        return similarity < 0.7
    
    def _calculate_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Calculate similarity between two images
        
        Args:
            img1: First image
            img2: Second image
            
        Returns:
            Similarity score (0-1)
        """
        try:
            # Resize images to same size if needed
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Convert to grayscale if needed
            if len(img1.shape) == 3:
                gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            else:
                gray1 = img1
            
            if len(img2.shape) == 3:
                gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            else:
                gray2 = img2
            
            # Calculate structural similarity
            # Using simple correlation for now
            correlation = np.corrcoef(gray1.flatten(), gray2.flatten())[0, 1]
            
            # Handle NaN values
            if np.isnan(correlation):
                return 0.0
            
            # Convert to 0-1 range
            return (correlation + 1) / 2
            
        except Exception as e:
            self.logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def get_interpolation_requirements(self, video_info: Dict[str, Any], target_fps: int) -> Dict[str, Any]:
        """
        Calculate frame interpolation requirements
        
        Args:
            video_info: Video information dictionary
            target_fps: Target frame rate
            
        Returns:
            Dictionary with interpolation requirements
        """
        current_fps = video_info['video']['fps']
        
        if current_fps == 0:
            return {
                'required': False,
                'ratio': 1,
                'current_fps': current_fps,
                'target_fps': target_fps
            }
        
        ratio = target_fps / current_fps
        
        return {
            'required': ratio > 1,
            'ratio': int(round(ratio)),
            'current_fps': current_fps,
            'target_fps': target_fps
        }
    
    def get_upscaling_requirements(self, video_info: Dict[str, Any], target_resolution: str) -> Dict[str, Any]:
        """
        Calculate upscaling requirements
        
        Args:
            video_info: Video information dictionary
            target_resolution: Target resolution (e.g., "3840x2160")
            
        Returns:
            Dictionary with upscaling requirements
        """
        current_width = video_info['video']['width']
        current_height = video_info['video']['height']
        
        try:
            target_width, target_height = map(int, target_resolution.lower().split('x'))
        except:
            return {
                'required': False,
                'width_ratio': 1.0,
                'height_ratio': 1.0,
                'current_resolution': f"{current_width}x{current_height}",
                'target_resolution': target_resolution
            }
        
        width_ratio = target_width / current_width if current_width > 0 else 1.0
        height_ratio = target_height / current_height if current_height > 0 else 1.0
        
        return {
            'required': width_ratio > 1 or height_ratio > 1,
            'width_ratio': width_ratio,
            'height_ratio': height_ratio,
            'current_resolution': f"{current_width}x{current_height}",
            'target_resolution': target_resolution
        }