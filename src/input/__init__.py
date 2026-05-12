"""
Input handling for MAGI Pipeline
"""

from .video_input import VideoInput
from .format_detector import FormatDetector
from .frame_extractor import FrameExtractor

__all__ = ["VideoInput", "FormatDetector", "FrameExtractor"]