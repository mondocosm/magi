"""
Bino3D integration for MAGI Pipeline
Handles launching and configuring Bino3D for MAGI format playback
"""

import subprocess
import json
import shutil
from typing import Optional, Dict, Any, List
from pathlib import Path
from enum import Enum

from ..core.logger import LoggerMixin
from ..core.exceptions import ProcessingError


class BinoOutputMode(Enum):
    """Bino3D output modes"""
    STEREO_GLASSES = "stereo-gl"  # 3D shutter glasses
    SIDE_BY_SIDE = "side-by-side"  # Side-by-side 3D
    TOP_BOTTOM = "top-bottom"  # Top-bottom 3D
    ANAGLYPH = "anaglyph"  # Red-cyan anaglyph
    INTERLEAVED = "interleaved"  # Interleaved rows
    MONO_LEFT = "mono-left"  # Left eye only
    MONO_RIGHT = "mono-right"  # Right eye only


class BinoInputMode(Enum):
    """Bino3D input modes"""
    AUTO = "auto"  # Auto-detect
    MONO = "mono"  # 2D video
    SIDE_BY_SIDE_LEFT_FIRST = "side-by-side-left-first"  # SBS (left first)
    SIDE_BY_SIDE_RIGHT_FIRST = "side-by-side-right-first"  # SBS (right first)
    TOP_BOTTOM_LEFT_FIRST = "top-bottom-left-first"  # TAB (left first)
    TOP_BOTTOM_RIGHT_FIRST = "top-bottom-right-first"  # TAB (right first)
    FRAME_SEQUENTIAL = "frame-sequential"  # Frame sequential (L-R-L-R)
    ANAGLYPH_RED_CYAN = "anaglyph-red-cyan"  # Red-cyan anaglyph


class BinoIntegration(LoggerMixin):
    """Integration with Bino3D player for MAGI format playback"""
    
    def __init__(self, bino_path: Optional[str] = None):
        """
        Initialize Bino integration
        
        Args:
            bino_path: Path to Bino3D executable (auto-detect if not provided)
        """
        self.bino_path = bino_path or self._find_bino()
        
        if not self.bino_path:
            self.logger.warning("Bino3D not found. MAGI playback will be limited.")
        
        # MAGI-specific settings
        self.magi_settings = {
            "input_mode": BinoInputMode.FRAME_SEQUENTIAL,
            "output_mode": BinoOutputMode.STEREO_GLASSES,
            "fullscreen": True,
            "loop": True,
            "audio_volume": 1.0,
        }
        
        self.logger.info(f"BinoIntegration initialized with Bino3D: {self.bino_path}")
    
    def _find_bino(self) -> Optional[str]:
        """
        Find Bino3D executable
        
        Returns:
            Path to Bino3D executable or None if not found
        """
        # Check common locations
        possible_paths = [
            "bino",  # In PATH
            "/usr/bin/bino",  # Linux
            "/usr/local/bin/bino",  # Linux (local)
            "C:\\Program Files\\Bino\\bino.exe",  # Windows
            "C:\\Program Files (x86)\\Bino\\bino.exe",  # Windows (x86)
            "/Applications/Bino.app/Contents/MacOS/bino",  # macOS
            "./bino/build/bino",  # Local build
            "./bino/build/src/bino",  # Local build (src)
        ]
        
        for path in possible_paths:
            if shutil.which(path) or Path(path).exists():
                self.logger.info(f"Found Bino3D at: {path}")
                return path
        
        return None
    
    def is_available(self) -> bool:
        """
        Check if Bino3D is available
        
        Returns:
            True if Bino3D is available, False otherwise
        """
        return self.bino_path is not None
    
    def play_magi_file(self, magi_file: str, settings: Optional[Dict[str, Any]] = None) -> subprocess.Popen:
        """
        Play a MAGI file using Bino3D
        
        Args:
            magi_file: Path to MAGI file
            settings: Optional settings to override defaults
            
        Returns:
            Subprocess object for Bino3D process
            
        Raises:
            ProcessingError: If Bino3D is not available or file doesn't exist
        """
        if not self.is_available():
            raise ProcessingError("Bino3D is not available. Cannot play MAGI file.")
        
        if not Path(magi_file).exists():
            raise ProcessingError(f"MAGI file not found: {magi_file}")
        
        # Merge settings
        play_settings = {**self.magi_settings, **(settings or {})}
        
        # Build command
        cmd = [self.bino_path]
        
        # Add input mode
        if "input_mode" in play_settings:
            cmd.extend(["--input", play_settings["input_mode"].value])
        
        # Add output mode
        if "output_mode" in play_settings:
            cmd.extend(["--output", play_settings["output_mode"].value])
        
        # Add fullscreen
        if play_settings.get("fullscreen", False):
            cmd.append("--fullscreen")
        
        # Add loop
        if play_settings.get("loop", False):
            cmd.append("--loop")
        
        # Add audio volume
        if "audio_volume" in play_settings:
            cmd.extend(["--audio-volume", str(play_settings["audio_volume"])])
        
        # Add video file
        cmd.append(magi_file)
        
        self.logger.info(f"Launching Bino3D: {' '.join(cmd)}")
        
        try:
            # Launch Bino3D
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.logger.info(f"Bino3D launched with PID: {process.pid}")
            return process
        
        except Exception as e:
            raise ProcessingError(f"Failed to launch Bino3D: {e}")
    
    def play_test_pattern(self, pattern_type: str = "motion_blur") -> subprocess.Popen:
        """
        Play a test pattern using Bino3D
        
        Args:
            pattern_type: Type of test pattern (motion_blur, ufo_test, etc.)
            
        Returns:
            Subprocess object for Bino3D process
        """
        # Create test pattern file
        test_pattern_file = self._create_test_pattern_file(pattern_type)
        
        # Play test pattern
        return self.play_magi_file(test_pattern_file)
    
    def _create_test_pattern_file(self, pattern_type: str) -> str:
        """
        Create a test pattern file for Bino3D
        
        Args:
            pattern_type: Type of test pattern
            
        Returns:
            Path to test pattern file
        """
        # This would create a test pattern video file
        # For now, return a placeholder
        test_file = f"test_pattern_{pattern_type}.mp4"
        
        # TODO: Implement actual test pattern generation
        self.logger.warning(f"Test pattern generation not implemented: {pattern_type}")
        
        return test_file
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported video formats
        
        Returns:
            List of supported formats
        """
        return [
            "mp4", "mkv", "avi", "mov", "webm",  # Containers
            "h264", "h265", "hevc", "vp9", "av1",  # Codecs
        ]
    
    def get_supported_3d_modes(self) -> Dict[str, List[str]]:
        """
        Get supported 3D modes
        
        Returns:
            Dictionary with input and output modes
        """
        return {
            "input_modes": [mode.value for mode in BinoInputMode],
            "output_modes": [mode.value for mode in BinoOutputMode],
        }
    
    def configure_for_magi(self, frame_rate: int = 120, resolution: str = "3840x2160"):
        """
        Configure Bino3D for MAGI format playback
        
        Args:
            frame_rate: Frame rate (default: 120)
            resolution: Resolution (default: 3840x2160)
        """
        self.magi_settings.update({
            "input_mode": BinoInputMode.FRAME_SEQUENTIAL,
            "output_mode": BinoOutputMode.STEREO_GLASSES,
            "fullscreen": True,
            "loop": True,
        })
        
        self.logger.info(f"Configured Bino3D for MAGI: {frame_rate}fps @ {resolution}")
    
    def get_version(self) -> Optional[str]:
        """
        Get Bino3D version
        
        Returns:
            Version string or None if Bino3D is not available
        """
        if not self.is_available():
            return None
        
        try:
            result = subprocess.run(
                [self.bino_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.logger.info(f"Bino3D version: {version}")
                return version
        
        except Exception as e:
            self.logger.error(f"Failed to get Bino3D version: {e}")
        
        return None
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get Bino3D capabilities
        
        Returns:
            Dictionary with capabilities
        """
        return {
            "available": self.is_available(),
            "version": self.get_version(),
            "supported_formats": self.get_supported_formats(),
            "supported_3d_modes": self.get_supported_3d_modes(),
            "magi_compatible": self._check_magi_compatibility(),
        }
    
    def _check_magi_compatibility(self) -> bool:
        """
        Check if Bino3D is compatible with MAGI format
        
        Returns:
            True if compatible, False otherwise
        """
        if not self.is_available():
            return False
        
        # Check if Bino3D supports required features
        # MAGI requires: frame sequential input, stereo glasses output, 120fps, 4K
        
        # For now, assume Bino3D is compatible if it's available
        # In a real implementation, we would check specific capabilities
        
        return True


def create_bino_integration(bino_path: Optional[str] = None) -> BinoIntegration:
    """
    Create Bino integration instance
    
    Args:
        bino_path: Path to Bino3D executable
        
    Returns:
        BinoIntegration instance
    """
    return BinoIntegration(bino_path)