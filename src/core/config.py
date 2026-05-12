"""
Configuration management for MAGI Pipeline
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ProcessingConfig:
    """Processing settings"""
    target_resolution: str = "3840x2160"
    target_frame_rate: int = 120
    target_format: str = "magi"
    
    interpolation_enabled: bool = True
    interpolation_method: str = "rife"
    interpolation_quality: str = "high"
    interpolation_gpu: bool = True
    
    upscaling_enabled: bool = True
    upscaling_method: str = "waifu2x"
    upscaling_model: str = "photo-normal"
    upscaling_gpu: bool = True
    
    processing_3d_enabled: bool = True
    input_format: str = "auto"
    output_format: str = "sbs"
    depth_estimation: bool = True
    use_stereocrafter: bool = True
    stereocrafter_path: str = "../StereoCrafter"
    stereocrafter_max_disp: int = 20


@dataclass
class GPUConfig:
    """GPU settings"""
    backend: str = "auto"
    cuda_device_id: int = 0
    cuda_allow_growth: bool = True
    vulkan_device_id: int = 0
    max_memory_gb: int = 8
    buffer_size: int = 4
    use_cloud: bool = False
    cloud_provider: str = "local"  # local, runpod, vastai, lambda, custom


@dataclass
class CloudConfig:
    """Cloud GPU settings"""
    enabled: bool = False
    provider: str = "runpod"  # runpod, vastai, lambda, custom
    api_key: str = ""
    endpoint: str = ""
    gpu_type: str = "NVIDIA RTX 3090"
    region: str = "us-east-1"
    max_cost_per_hour: float = 1.0
    auto_terminate: bool = True
    timeout_minutes: int = 60


@dataclass
class PerformanceConfig:
    """Performance settings"""
    threads: int = 4
    buffer_size: int = 8
    real_time: bool = True
    max_latency_ms: int = 100
    quality_mode: str = "balanced"


@dataclass
class InputConfig:
    """Input settings"""
    formats: list = field(default_factory=lambda: ["mp4", "avi", "mkv", "mov", "webm"])
    auto_detect_3d: bool = True
    preserve_audio: bool = True
    preserve_metadata: bool = True


@dataclass
class OutputConfig:
    """Output settings"""
    container: str = "mp4"
    video_codec: str = "hevc"
    audio_codec: str = "aac"
    video_bitrate: str = "50000k"
    audio_bitrate: str = "320k"
    crf: int = 18
    frame_cadence: str = "alternating"
    eye_separation: int = 180
    sync_method: str = "hardware"


@dataclass
class UIConfig:
    """UI settings"""
    web_enabled: bool = True
    web_host: str = "0.0.0.0"
    web_port: int = 8000
    web_debug: bool = False
    gui_theme: str = "dark"
    gui_language: str = "en"
    show_preview: bool = True
    preview_quality: str = "medium"


@dataclass
class LoggingConfig:
    """Logging settings"""
    level: str = "INFO"
    file: str = "logs/magipipeline.log"
    console: bool = True
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class PathsConfig:
    """Path settings"""
    models_dir: str = "models"
    temp_dir: str = "temp"
    cache_dir: str = "cache"
    output_dir: str = "output"
    bino_path: str = "../bino"
    waifu2x_path: str = "../Waifu2x-Extension-GUI"


class Config:
    """Main configuration class for MAGI Pipeline"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration
        
        Args:
            config_path: Path to configuration file (YAML)
        """
        self.config_path = config_path or self._find_config_file()
        self._raw_config: Dict[str, Any] = {}
        self._load_config()
        
        # Initialize configuration sections
        self.processing = ProcessingConfig()
        self.gpu = GPUConfig()
        self.cloud = CloudConfig()
        self.performance = PerformanceConfig()
        self.input = InputConfig()
        self.output = OutputConfig()
        self.ui = UIConfig()
        self.logging = LoggingConfig()
        self.paths = PathsConfig()
        
        # Apply loaded configuration
        if self._raw_config:
            self._apply_config()
    
    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in standard locations"""
        possible_paths = [
            "config/config.yaml",
            "config/config.example.yaml",
            "../config/config.yaml",
            os.path.expanduser("~/.magipipeline/config.yaml"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _load_config(self):
        """Load configuration from YAML file"""
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self._raw_config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: Could not load config file {self.config_path}: {e}")
    
    def _apply_config(self):
        """Apply loaded configuration to config objects"""
        # Processing settings
        if 'processing' in self._raw_config:
            proc = self._raw_config['processing']
            if 'target' in proc:
                self.processing.target_resolution = proc['target'].get('resolution', self.processing.target_resolution)
                self.processing.target_frame_rate = proc['target'].get('frame_rate', self.processing.target_frame_rate)
                self.processing.target_format = proc['target'].get('format', self.processing.target_format)
            
            if 'interpolation' in proc:
                interp = proc['interpolation']
                self.processing.interpolation_enabled = interp.get('enabled', self.processing.interpolation_enabled)
                self.processing.interpolation_method = interp.get('method', self.processing.interpolation_method)
                self.processing.interpolation_quality = interp.get('quality', self.processing.interpolation_quality)
                self.processing.interpolation_gpu = interp.get('gpu_acceleration', self.processing.interpolation_gpu)
            
            if 'upscaling' in proc:
                upscale = proc['upscaling']
                self.processing.upscaling_enabled = upscale.get('enabled', self.processing.upscaling_enabled)
                self.processing.upscaling_method = upscale.get('method', self.processing.upscaling_method)
                self.processing.upscaling_model = upscale.get('model', self.processing.upscaling_model)
                self.processing.upscaling_gpu = upscale.get('gpu_acceleration', self.processing.upscaling_gpu)
            
            if 'processing_3d' in proc:
                proc3d = proc['processing_3d']
                self.processing.processing_3d_enabled = proc3d.get('enabled', self.processing.processing_3d_enabled)
                self.processing.input_format = proc3d.get('input_format', self.processing.input_format)
                self.processing.output_format = proc3d.get('output_format', self.processing.output_format)
                self.processing.depth_estimation = proc3d.get('depth_estimation', self.processing.depth_estimation)
                self.processing.use_stereocrafter = proc3d.get('use_stereocrafter', self.processing.use_stereocrafter)
                self.processing.stereocrafter_path = proc3d.get('stereocrafter_path', self.processing.stereocrafter_path)
                self.processing.stereocrafter_max_disp = proc3d.get('stereocrafter_max_disp', self.processing.stereocrafter_max_disp)
        
        # GPU settings
        if 'gpu' in self._raw_config:
            gpu = self._raw_config['gpu']
            self.gpu.backend = gpu.get('backend', self.gpu.backend)
            self.gpu.use_cloud = gpu.get('use_cloud', self.gpu.use_cloud)
            self.gpu.cloud_provider = gpu.get('cloud_provider', self.gpu.cloud_provider)
            if 'cuda' in gpu:
                self.gpu.cuda_device_id = gpu['cuda'].get('device_id', self.gpu.cuda_device_id)
                self.gpu.cuda_allow_growth = gpu['cuda'].get('allow_growth', self.gpu.cuda_allow_growth)
            if 'vulkan' in gpu:
                self.gpu.vulkan_device_id = gpu['vulkan'].get('device_id', self.gpu.vulkan_device_id)
            if 'memory' in gpu:
                self.gpu.max_memory_gb = gpu['memory'].get('max_memory_gb', self.gpu.max_memory_gb)
                self.gpu.buffer_size = gpu['memory'].get('buffer_size', self.gpu.buffer_size)
        
        # Cloud settings
        if 'cloud' in self._raw_config:
            cloud = self._raw_config['cloud']
            self.cloud.enabled = cloud.get('enabled', self.cloud.enabled)
            self.cloud.provider = cloud.get('provider', self.cloud.provider)
            self.cloud.api_key = cloud.get('api_key', self.cloud.api_key)
            self.cloud.endpoint = cloud.get('endpoint', self.cloud.endpoint)
            self.cloud.gpu_type = cloud.get('gpu_type', self.cloud.gpu_type)
            self.cloud.region = cloud.get('region', self.cloud.region)
            self.cloud.max_cost_per_hour = cloud.get('max_cost_per_hour', self.cloud.max_cost_per_hour)
            self.cloud.auto_terminate = cloud.get('auto_terminate', self.cloud.auto_terminate)
            self.cloud.timeout_minutes = cloud.get('timeout_minutes', self.cloud.timeout_minutes)
        
        # Performance settings
        if 'performance' in self._raw_config:
            perf = self._raw_config['performance']
            self.performance.threads = perf.get('threads', self.performance.threads)
            self.performance.buffer_size = perf.get('buffer_size', self.performance.buffer_size)
            self.performance.real_time = perf.get('real_time', self.performance.real_time)
            self.performance.max_latency_ms = perf.get('max_latency_ms', self.performance.max_latency_ms)
            self.performance.quality_mode = perf.get('quality_mode', self.performance.quality_mode)
        
        # Input settings
        if 'input' in self._raw_config:
            inp = self._raw_config['input']
            self.input.formats = inp.get('formats', self.input.formats)
            self.input.auto_detect_3d = inp.get('auto_detect_3d', self.input.auto_detect_3d)
            self.input.preserve_audio = inp.get('preserve_audio', self.input.preserve_audio)
            self.input.preserve_metadata = inp.get('preserve_metadata', self.input.preserve_metadata)
        
        # Output settings
        if 'output' in self._raw_config:
            out = self._raw_config['output']
            self.output.container = out.get('container', self.output.container)
            self.output.video_codec = out.get('video_codec', self.output.video_codec)
            self.output.audio_codec = out.get('audio_codec', self.output.audio_codec)
            if 'quality' in out:
                quality = out['quality']
                self.output.video_bitrate = quality.get('video_bitrate', self.output.video_bitrate)
                self.output.audio_bitrate = quality.get('audio_bitrate', self.output.audio_bitrate)
                self.output.crf = quality.get('crf', self.output.crf)
            if 'magi' in out:
                magi = out['magi']
                self.output.frame_cadence = magi.get('frame_cadence', self.output.frame_cadence)
                self.output.eye_separation = magi.get('eye_separation', self.output.eye_separation)
                self.output.sync_method = magi.get('sync_method', self.output.sync_method)
        
        # UI settings
        if 'ui' in self._raw_config:
            ui = self._raw_config['ui']
            if 'web' in ui:
                web = ui['web']
                self.ui.web_enabled = web.get('enabled', self.ui.web_enabled)
                self.ui.web_host = web.get('host', self.ui.web_host)
                self.ui.web_port = web.get('port', self.ui.web_port)
                self.ui.web_debug = web.get('debug', self.ui.web_debug)
            if 'gui' in ui:
                gui = ui['gui']
                self.ui.gui_theme = gui.get('theme', self.ui.gui_theme)
                self.ui.gui_language = gui.get('language', self.ui.gui_language)
                self.ui.show_preview = gui.get('show_preview', self.ui.show_preview)
                self.ui.preview_quality = gui.get('preview_quality', self.ui.preview_quality)
        
        # Logging settings
        if 'logging' in self._raw_config:
            log = self._raw_config['logging']
            self.logging.level = log.get('level', self.logging.level)
            self.logging.file = log.get('file', self.logging.file)
            self.logging.console = log.get('console', self.logging.console)
            self.logging.format = log.get('format', self.logging.format)
        
        # Paths settings
        if 'paths' in self._raw_config:
            paths = self._raw_config['paths']
            self.paths.models_dir = paths.get('models_dir', self.paths.models_dir)
            self.paths.temp_dir = paths.get('temp_dir', self.paths.temp_dir)
            self.paths.cache_dir = paths.get('cache_dir', self.paths.cache_dir)
            self.paths.output_dir = paths.get('output_dir', self.paths.output_dir)
            self.paths.bino_path = paths.get('bino_path', self.paths.bino_path)
            self.paths.waifu2x_path = paths.get('waifu2x_path', self.paths.waifu2x_path)
    
    def save(self, path: Optional[str] = None):
        """
        Save current configuration to YAML file
        
        Args:
            path: Path to save configuration (uses current config path if not specified)
        """
        save_path = path or self.config_path or "config/config.yaml"
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Build configuration dictionary
        config_dict = {
            'processing': {
                'target': {
                    'resolution': self.processing.target_resolution,
                    'frame_rate': self.processing.target_frame_rate,
                    'format': self.processing.target_format
                },
                'interpolation': {
                    'enabled': self.processing.interpolation_enabled,
                    'method': self.processing.interpolation_method,
                    'quality': self.processing.interpolation_quality,
                    'gpu_acceleration': self.processing.interpolation_gpu
                },
                'upscaling': {
                    'enabled': self.processing.upscaling_enabled,
                    'method': self.processing.upscaling_method,
                    'model': self.processing.upscaling_model,
                    'gpu_acceleration': self.processing.upscaling_gpu
                },
                'processing_3d': {
                    'enabled': self.processing.processing_3d_enabled,
                    'input_format': self.processing.input_format,
                    'output_format': self.processing.output_format,
                    'depth_estimation': self.processing.depth_estimation
                }
            },
            'gpu': {
                'backend': self.gpu.backend,
                'use_cloud': self.gpu.use_cloud,
                'cloud_provider': self.gpu.cloud_provider,
                'cuda': {
                    'device_id': self.gpu.cuda_device_id,
                    'allow_growth': self.gpu.cuda_allow_growth
                },
                'vulkan': {
                    'device_id': self.gpu.vulkan_device_id
                },
                'memory': {
                    'max_memory_gb': self.gpu.max_memory_gb,
                    'buffer_size': self.gpu.buffer_size
                }
            },
            'cloud': {
                'enabled': self.cloud.enabled,
                'provider': self.cloud.provider,
                'api_key': self.cloud.api_key,
                'endpoint': self.cloud.endpoint,
                'gpu_type': self.cloud.gpu_type,
                'region': self.cloud.region,
                'max_cost_per_hour': self.cloud.max_cost_per_hour,
                'auto_terminate': self.cloud.auto_terminate,
                'timeout_minutes': self.cloud.timeout_minutes
            },
            'performance': {
                'threads': self.performance.threads,
                'buffer_size': self.performance.buffer_size,
                'real_time': self.performance.real_time,
                'max_latency_ms': self.performance.max_latency_ms,
                'quality_mode': self.performance.quality_mode
            },
            'input': {
                'formats': self.input.formats,
                'auto_detect_3d': self.input.auto_detect_3d,
                'preserve_audio': self.input.preserve_audio,
                'preserve_metadata': self.input.preserve_metadata
            },
            'output': {
                'container': self.output.container,
                'video_codec': self.output.video_codec,
                'audio_codec': self.output.audio_codec,
                'quality': {
                    'video_bitrate': self.output.video_bitrate,
                    'audio_bitrate': self.output.audio_bitrate,
                    'crf': self.output.crf
                },
                'magi': {
                    'frame_cadence': self.output.frame_cadence,
                    'eye_separation': self.output.eye_separation,
                    'sync_method': self.output.sync_method
                }
            },
            'ui': {
                'web': {
                    'enabled': self.ui.web_enabled,
                    'host': self.ui.web_host,
                    'port': self.ui.web_port,
                    'debug': self.ui.web_debug
                },
                'gui': {
                    'theme': self.ui.gui_theme,
                    'language': self.ui.gui_language,
                    'show_preview': self.ui.show_preview,
                    'preview_quality': self.ui.preview_quality
                }
            },
            'logging': {
                'level': self.logging.level,
                'file': self.logging.file,
                'console': self.logging.console,
                'format': self.logging.format
            },
            'paths': {
                'models_dir': self.paths.models_dir,
                'temp_dir': self.paths.temp_dir,
                'cache_dir': self.paths.cache_dir,
                'output_dir': self.paths.output_dir,
                'bino_path': self.paths.bino_path,
                'waifu2x_path': self.paths.waifu2x_path
            }
        }
        
        # Save to file
        with open(save_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)
    
    def get_interpolation_ratio(self, input_fps: int) -> int:
        """
        Calculate frame interpolation ratio based on input frame rate
        
        Args:
            input_fps: Input frame rate
            
        Returns:
            Interpolation ratio (how many output frames per input frame)
        """
        target_fps = self.processing.target_frame_rate
        if input_fps == 0:
            return 1
        
        ratio = target_fps / input_fps
        return int(round(ratio))
    
    def get_upscaling_ratio(self, input_resolution: str) -> tuple:
        """
        Calculate upscaling ratio based on input resolution
        
        Args:
            input_resolution: Input resolution (e.g., "1920x1080")
            
        Returns:
            Tuple of (width_ratio, height_ratio)
        """
        try:
            input_width, input_height = map(int, input_resolution.lower().split('x'))
            target_width, target_height = map(int, self.processing.target_resolution.lower().split('x'))
            
            width_ratio = target_width / input_width
            height_ratio = target_height / input_height
            
            return (width_ratio, height_ratio)
        except:
            return (1.0, 1.0)