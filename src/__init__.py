"""
MAGI Video Pipeline
A real-time 3D video interpolation and upscaling pipeline for MAGI format conversion.
"""

__version__ = "0.1.0"
__author__ = "MAGI Pipeline Team"
__license__ = "MIT"

from .core.config import Config
from .pipeline.controller import MAGIPipeline

__all__ = ["Config", "MAGIPipeline"]