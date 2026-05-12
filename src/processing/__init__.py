"""
Processing modules for MAGI Pipeline
"""

from .interpolation import FrameInterpolator
from .upscaling import ImageUpscaler
from .processing_3d import Processor3D
from .frame_cadence import FrameCadenceManager
from .stereocrafter import StereoCrafterIntegration

__all__ = ["FrameInterpolator", "ImageUpscaler", "Processor3D", "FrameCadenceManager", "StereoCrafterIntegration"]