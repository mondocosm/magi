"""
Core infrastructure for MAGI Pipeline
"""

from .config import Config
from .logger import setup_logger
from .exceptions import MAGIPipelineError

__all__ = ["Config", "setup_logger", "MAGIPipelineError"]