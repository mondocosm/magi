"""
Custom exceptions for MAGI Pipeline
"""


class MAGIPipelineError(Exception):
    """Base exception for MAGI Pipeline errors"""
    pass


class ConfigurationError(MAGIPipelineError):
    """Configuration related errors"""
    pass


class InputError(MAGIPipelineError):
    """Input handling errors"""
    pass


class ProcessingError(MAGIPipelineError):
    """Video processing errors"""
    pass


class InterpolationError(MAGIPipelineError):
    """Frame interpolation errors"""
    pass


class UpscalingError(MAGIPipelineError):
    """Image upscaling errors"""
    pass


class OutputError(MAGIPipelineError):
    """Output generation errors"""
    pass


class GPUError(MAGIPipelineError):
    """GPU related errors"""
    pass


class ModelNotFoundError(MAGIPipelineError):
    """AI model not found errors"""
    pass


class FormatNotSupportedError(MAGIPipelineError):
    """Format not supported errors"""
    pass


class ResourceError(MAGIPipelineError):
    """System resource errors (memory, disk space, etc.)"""
    pass