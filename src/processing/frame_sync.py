"""
Frame Synchronization Module
Supports VSync, G-Sync, FreeSync, and adaptive sync technologies
Critical for 120fps MAGI format with 3D shutter glasses
"""

import time
import threading
from enum import Enum
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
import platform
import subprocess
import re

from ..core.logger import LoggerMixin


class SyncTechnology(Enum):
    """Available synchronization technologies"""
    VSYNC = "vsync"  # Vertical Synchronization
    GSYNC = "gsync"  # NVIDIA G-Sync
    FREESYNC = "freesync"  # AMD FreeSync
    ADAPTIVE_SYNC = "adaptive_sync"  # Generic adaptive sync
    NONE = "none"  # No synchronization


class SyncMode(Enum):
    """Synchronization modes"""
    OFF = "off"  # Synchronization disabled
    ON = "on"  # Synchronization enabled
    ADAPTIVE = "adaptive"  # Adaptive synchronization
    FAST = "fast"  # Fast sync (NVIDIA)
    IMMEDIATE = "immediate"  # Immediate presentation


@dataclass
class DisplayInfo:
    """Display information"""
    display_id: int
    name: str
    resolution: tuple  # (width, height)
    refresh_rate: float  # Hz
    primary: bool
    sync_technology: Optional[SyncTechnology] = None
    sync_range: Optional[tuple] = None  # (min_hz, max_hz) for adaptive sync


@dataclass
class FrameTiming:
    """Frame timing information"""
    frame_number: int
    presentation_time: float  # When frame should be displayed
    render_time: float  # Time taken to render frame
    display_time: float  # Time when frame was actually displayed
    vsync_offset: float  # Offset from vsync
    frame_interval: float  # Time between frames (should be 8.33ms for 120fps)


class FrameSynchronizer(LoggerMixin):
    """
    Frame synchronization manager
    Supports VSync, G-Sync, FreeSync, and adaptive sync technologies
    """
    
    def __init__(self, target_fps: float = 120.0):
        """
        Initialize frame synchronizer
        
        Args:
            target_fps: Target frame rate (default 120fps for MAGI)
        """
        self.target_fps = target_fps
        self.frame_interval = 1.0 / target_fps  # 8.33ms for 120fps
        
        # Current sync settings
        self.sync_technology = SyncTechnology.VSYNC
        self.sync_mode = SyncMode.ON
        
        # Display information
        self.displays: Dict[int, DisplayInfo] = {}
        self.primary_display: Optional[DisplayInfo] = None
        
        # Frame timing
        self.frame_number = 0
        self.last_frame_time = 0.0
        self.frame_timings: list = []
        self.max_timing_history = 1000
        
        # Synchronization state
        self.vsync_enabled = True
        self.adaptive_sync_enabled = False
        self.tear_free = True
        
        # Performance monitoring
        self.frame_drops = 0
        self.frame_duplicates = 0
        self.sync_errors = 0
        
        # Callbacks
        self.frame_callback: Optional[Callable] = None
        self.vsync_callback: Optional[Callable] = None
        
        # Threading
        self.sync_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Detect available sync technologies
        self._detect_sync_capabilities()
        
        self.logger.info(f"FrameSynchronizer initialized for {target_fps}fps")
    
    def _detect_sync_capabilities(self):
        """Detect available synchronization technologies"""
        system = platform.system()
        
        # Detect NVIDIA G-Sync
        if self._detect_nvidia_gpu():
            self.logger.info("NVIDIA GPU detected - G-Sync available")
            # Check if G-Sync is enabled
            if self._check_gsync_enabled():
                self.sync_technology = SyncTechnology.GSYNC
                self.logger.info("G-Sync is enabled")
        
        # Detect AMD FreeSync
        elif self._detect_amd_gpu():
            self.logger.info("AMD GPU detected - FreeSync available")
            # Check if FreeSync is enabled
            if self._check_freesync_enabled():
                self.sync_technology = SyncTechnology.FREESYNC
                self.logger.info("FreeSync is enabled")
        
        # Detect generic adaptive sync
        elif self._detect_adaptive_sync():
            self.logger.info("Adaptive sync detected")
            self.sync_technology = SyncTechnology.ADAPTIVE_SYNC
        
        # Get display information
        self._get_display_info()
    
    def _detect_nvidia_gpu(self) -> bool:
        """Detect if NVIDIA GPU is present"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["wmic", "path", "win32_VideoController", "get", "name"],
                    capture_output=True, text=True, timeout=5
                )
                return "NVIDIA" in result.stdout
            elif platform.system() == "Linux":
                result = subprocess.run(
                    ["lspci"], capture_output=True, text=True, timeout=5
                )
                return "NVIDIA" in result.stdout
            elif platform.system() == "Darwin":  # macOS
                # macOS doesn't typically have NVIDIA GPUs in recent systems
                return False
        except Exception as e:
            self.logger.warning(f"Failed to detect NVIDIA GPU: {e}")
        return False
    
    def _detect_amd_gpu(self) -> bool:
        """Detect if AMD GPU is present"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["wmic", "path", "win32_VideoController", "get", "name"],
                    capture_output=True, text=True, timeout=5
                )
                return "AMD" in result.stdout or "Radeon" in result.stdout
            elif platform.system() == "Linux":
                result = subprocess.run(
                    ["lspci"], capture_output=True, text=True, timeout=5
                )
                return "AMD" in result.stdout or "Radeon" in result.stdout
            elif platform.system() == "Darwin":  # macOS
                # macOS uses AMD GPUs in some systems
                result = subprocess.run(
                    ["system_profiler", "SPDisplaysDataType"],
                    capture_output=True, text=True, timeout=5
                )
                return "AMD" in result.stdout or "Radeon" in result.stdout
        except Exception as e:
            self.logger.warning(f"Failed to detect AMD GPU: {e}")
        return False
    
    def _check_gsync_enabled(self) -> bool:
        """Check if G-Sync is enabled"""
        try:
            if platform.system() == "Windows":
                # Check NVIDIA control panel settings
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=gpu_name", "--format=csv"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    # NVIDIA GPU detected, assume G-Sync capable
                    return True
        except Exception as e:
            self.logger.warning(f"Failed to check G-Sync status: {e}")
        return False
    
    def _check_freesync_enabled(self) -> bool:
        """Check if FreeSync is enabled"""
        try:
            if platform.system() == "Windows":
                # Check AMD driver settings
                result = subprocess.run(
                    ["wmic", "path", "win32_VideoController", "get", "name"],
                    capture_output=True, text=True, timeout=5
                )
                if "AMD" in result.stdout or "Radeon" in result.stdout:
                    # AMD GPU detected, assume FreeSync capable
                    return True
        except Exception as e:
            self.logger.warning(f"Failed to check FreeSync status: {e}")
        return False
    
    def _detect_adaptive_sync(self) -> bool:
        """Detect generic adaptive sync support"""
        try:
            if platform.system() == "Linux":
                # Check for variable refresh rate support
                result = subprocess.run(
                    ["xrandr", "--prop"],
                    capture_output=True, text=True, timeout=5
                )
                return "variable refresh rate" in result.stdout.lower()
        except Exception as e:
            self.logger.warning(f"Failed to detect adaptive sync: {e}")
        return False
    
    def _get_display_info(self):
        """Get display information"""
        try:
            if platform.system() == "Windows":
                self._get_windows_display_info()
            elif platform.system() == "Linux":
                self._get_linux_display_info()
            elif platform.system() == "Darwin":
                self._get_macos_display_info()
        except Exception as e:
            self.logger.warning(f"Failed to get display info: {e}")
    
    def _get_windows_display_info(self):
        """Get Windows display information"""
        try:
            import ctypes
            import win32api
            
            def get_refresh_rate():
                dc = ctypes.windll.user32.GetDC(0)
                freq = ctypes.windll.gdi32.GetDeviceCaps(dc, 116)  # VREFRESH
                ctypes.windll.user32.ReleaseDC(0, dc)
                return freq
            
            refresh_rate = get_refresh_rate()
            
            # Create primary display info
            self.primary_display = DisplayInfo(
                display_id=0,
                name="Primary Display",
                resolution=(win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)),
                refresh_rate=refresh_rate,
                primary=True,
                sync_technology=self.sync_technology
            )
            
            self.displays[0] = self.primary_display
            
            self.logger.info(f"Primary display: {self.primary_display.resolution} @ {refresh_rate}Hz")
            
        except Exception as e:
            self.logger.warning(f"Failed to get Windows display info: {e}")
    
    def _get_linux_display_info(self):
        """Get Linux display information"""
        try:
            result = subprocess.run(
                ["xrandr"],
                capture_output=True, text=True, timeout=5
            )
            
            lines = result.stdout.split('\n')
            display_id = 0
            
            for line in lines:
                if ' connected' in line:
                    parts = line.split()
                    name = parts[0]
                    resolution_match = re.search(r'(\d+)x(\d+)', line)
                    refresh_match = re.search(r'(\d+\.?\d*)\*', line)
                    
                    if resolution_match:
                        width = int(resolution_match.group(1))
                        height = int(resolution_match.group(2))
                        refresh_rate = float(refresh_match.group(1)) if refresh_match else 60.0
                        
                        display = DisplayInfo(
                            display_id=display_id,
                            name=name,
                            resolution=(width, height),
                            refresh_rate=refresh_rate,
                            primary='primary' in line,
                            sync_technology=self.sync_technology
                        )
                        
                        self.displays[display_id] = display
                        
                        if display.primary:
                            self.primary_display = display
                        
                        display_id += 1
            
            if self.primary_display:
                self.logger.info(f"Primary display: {self.primary_display.name} - {self.primary_display.resolution} @ {self.primary_display.refresh_rate}Hz")
            
        except Exception as e:
            self.logger.warning(f"Failed to get Linux display info: {e}")
    
    def _get_macos_display_info(self):
        """Get macOS display information"""
        try:
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True, text=True, timeout=5
            )
            
            lines = result.stdout.split('\n')
            display_id = 0
            
            for i, line in enumerate(lines):
                if 'Resolution' in line:
                    resolution_match = re.search(r'(\d+) x (\d+)', line)
                    if resolution_match:
                        width = int(resolution_match.group(1))
                        height = int(resolution_match.group(2))
                        
                        # Look for refresh rate in nearby lines
                        refresh_rate = 60.0  # Default
                        for j in range(max(0, i-2), min(len(lines), i+3)):
                            if 'Hz' in lines[j]:
                                refresh_match = re.search(r'(\d+\.?\d*)\s*Hz', lines[j])
                                if refresh_match:
                                    refresh_rate = float(refresh_match.group(1))
                                    break
                        
                        display = DisplayInfo(
                            display_id=display_id,
                            name=f"Display {display_id}",
                            resolution=(width, height),
                            refresh_rate=refresh_rate,
                            primary=(display_id == 0),
                            sync_technology=SyncTechnology.NONE  # macOS doesn't typically support G-Sync/FreeSync
                        )
                        
                        self.displays[display_id] = display
                        
                        if display.primary:
                            self.primary_display = display
                        
                        display_id += 1
            
            if self.primary_display:
                self.logger.info(f"Primary display: {self.primary_display.name} - {self.primary_display.resolution} @ {self.primary_display.refresh_rate}Hz")
            
        except Exception as e:
            self.logger.warning(f"Failed to get macOS display info: {e}")
    
    def set_sync_technology(self, technology: SyncTechnology):
        """
        Set synchronization technology
        
        Args:
            technology: Sync technology to use
        """
        self.sync_technology = technology
        self.logger.info(f"Sync technology set to {technology.value}")
    
    def set_sync_mode(self, mode: SyncMode):
        """
        Set synchronization mode
        
        Args:
            mode: Sync mode to use
        """
        self.sync_mode = mode
        
        if mode == SyncMode.OFF:
            self.vsync_enabled = False
            self.adaptive_sync_enabled = False
        elif mode == SyncMode.ON:
            self.vsync_enabled = True
            self.adaptive_sync_enabled = False
        elif mode == SyncMode.ADAPTIVE:
            self.vsync_enabled = True
            self.adaptive_sync_enabled = True
        elif mode == SyncMode.FAST:
            self.vsync_enabled = True
            self.adaptive_sync_enabled = True
        elif mode == SyncMode.IMMEDIATE:
            self.vsync_enabled = False
            self.adaptive_sync_enabled = False
        
        self.logger.info(f"Sync mode set to {mode.value}")
    
    def enable_vsync(self, enabled: bool = True):
        """
        Enable or disable VSync
        
        Args:
            enabled: Whether to enable VSync
        """
        self.vsync_enabled = enabled
        self.logger.info(f"VSync {'enabled' if enabled else 'disabled'}")
    
    def enable_adaptive_sync(self, enabled: bool = True):
        """
        Enable or disable adaptive sync (G-Sync/FreeSync)
        
        Args:
            enabled: Whether to enable adaptive sync
        """
        if self.sync_technology in [SyncTechnology.GSYNC, SyncTechnology.FREESYNC, SyncTechnology.ADAPTIVE_SYNC]:
            self.adaptive_sync_enabled = enabled
            self.logger.info(f"Adaptive sync {'enabled' if enabled else 'disabled'}")
        else:
            self.logger.warning(f"Adaptive sync not available with {self.sync_technology.value}")
    
    def calculate_frame_time(self) -> float:
        """
        Calculate optimal frame time for current sync settings
        
        Returns:
            Frame time in seconds
        """
        if self.adaptive_sync_enabled and self.primary_display:
            # Use adaptive sync - can vary frame time
            return self.frame_interval
        elif self.vsync_enabled and self.primary_display:
            # Sync to display refresh rate
            return 1.0 / self.primary_display.refresh_rate
        else:
            # No sync - use target frame rate
            return self.frame_interval
    
    def wait_for_vsync(self):
        """
        Wait for vertical sync
        Blocks until next vsync
        """
        if not self.vsync_enabled:
            return
        
        current_time = time.time()
        if self.last_frame_time > 0:
            elapsed = current_time - self.last_frame_time
            target_time = self.calculate_frame_time()
            
            if elapsed < target_time:
                # Sleep until next frame
                sleep_time = target_time - elapsed
                time.sleep(sleep_time)
        
        self.last_frame_time = time.time()
    
    def sync_frame(self, frame_data: Any, frame_number: int) -> FrameTiming:
        """
        Synchronize a frame for display
        
        Args:
            frame_data: Frame data to display
            frame_number: Frame number
            
        Returns:
            Frame timing information
        """
        start_time = time.time()
        
        # Wait for vsync
        self.wait_for_vsync()
        
        # Calculate presentation time
        presentation_time = time.time()
        
        # Create timing info
        timing = FrameTiming(
            frame_number=frame_number,
            presentation_time=presentation_time,
            render_time=presentation_time - start_time,
            display_time=presentation_time,
            vsync_offset=0.0,  # Would need display API to get actual vsync time
            frame_interval=self.calculate_frame_time()
        )
        
        # Store timing
        self.frame_timings.append(timing)
        if len(self.frame_timings) > self.max_timing_history:
            self.frame_timings.pop(0)
        
        # Update frame number
        self.frame_number = frame_number
        
        # Call frame callback if set
        if self.frame_callback:
            self.frame_callback(frame_data, timing)
        
        return timing
    
    def get_frame_stats(self) -> Dict[str, Any]:
        """
        Get frame statistics
        
        Returns:
            Dictionary with frame statistics
        """
        if not self.frame_timings:
            return {
                "frame_count": 0,
                "avg_fps": 0.0,
                "avg_frame_time": 0.0,
                "frame_drops": 0,
                "frame_duplicates": 0,
                "sync_errors": 0
            }
        
        # Calculate statistics
        frame_times = [t.frame_interval for t in self.frame_timings]
        avg_frame_time = sum(frame_times) / len(frame_times)
        avg_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0
        
        return {
            "frame_count": len(self.frame_timings),
            "avg_fps": avg_fps,
            "avg_frame_time": avg_frame_time * 1000,  # Convert to ms
            "target_fps": self.target_fps,
            "frame_drops": self.frame_drops,
            "frame_duplicates": self.frame_duplicates,
            "sync_errors": self.sync_errors,
            "sync_technology": self.sync_technology.value,
            "sync_mode": self.sync_mode.value,
            "vsync_enabled": self.vsync_enabled,
            "adaptive_sync_enabled": self.adaptive_sync_enabled
        }
    
    def get_display_info(self) -> Dict[str, Any]:
        """
        Get display information
        
        Returns:
            Dictionary with display information
        """
        displays = []
        for display_id, display in self.displays.items():
            displays.append({
                "display_id": display.display_id,
                "name": display.name,
                "resolution": display.resolution,
                "refresh_rate": display.refresh_rate,
                "primary": display.primary,
                "sync_technology": display.sync_technology.value if display.sync_technology else None,
                "sync_range": display.sync_range
            })
        
        return {
            "displays": displays,
            "primary_display": {
                "display_id": self.primary_display.display_id,
                "name": self.primary_display.name,
                "resolution": self.primary_display.resolution,
                "refresh_rate": self.primary_display.refresh_rate,
                "sync_technology": self.primary_display.sync_technology.value if self.primary_display.sync_technology else None
            } if self.primary_display else None
        }
    
    def set_frame_callback(self, callback: Callable):
        """
        Set callback for frame presentation
        
        Args:
            callback: Function to call when frame is presented
        """
        self.frame_callback = callback
    
    def set_vsync_callback(self, callback: Callable):
        """
        Set callback for vsync events
        
        Args:
            callback: Function to call on vsync
        """
        self.vsync_callback = callback
    
    def start_sync_thread(self):
        """Start synchronization thread"""
        if self.sync_thread and self.sync_thread.is_alive():
            self.logger.warning("Sync thread already running")
            return
        
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        self.logger.info("Sync thread started")
    
    def stop_sync_thread(self):
        """Stop synchronization thread"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=1.0)
            self.logger.info("Sync thread stopped")
    
    def _sync_loop(self):
        """Synchronization loop"""
        while self.running:
            self.wait_for_vsync()
            
            if self.vsync_callback:
                self.vsync_callback()
    
    def reset_stats(self):
        """Reset frame statistics"""
        self.frame_timings.clear()
        self.frame_drops = 0
        self.frame_duplicates = 0
        self.sync_errors = 0
        self.frame_number = 0
        self.logger.info("Frame statistics reset")
    
    def optimize_for_magi(self):
        """
        Optimize settings for MAGI format (120fps 3D)
        """
        self.target_fps = 120.0
        self.frame_interval = 1.0 / 120.0  # 8.33ms
        
        # Enable vsync for precise timing
        self.enable_vsync(True)
        
        # Use adaptive sync if available for smoother frame delivery
        if self.sync_technology in [SyncTechnology.GSYNC, SyncTechnology.FREESYNC, SyncTechnology.ADAPTIVE_SYNC]:
            self.enable_adaptive_sync(True)
            self.set_sync_mode(SyncMode.ADAPTIVE)
        else:
            self.set_sync_mode(SyncMode.ON)
        
        # Enable tear-free rendering
        self.tear_free = True
        
        self.logger.info("Optimized for MAGI format (120fps 3D)")


def create_frame_synchronizer(target_fps: float = 120.0) -> FrameSynchronizer:
    """
    Create frame synchronizer instance
    
    Args:
        target_fps: Target frame rate (default 120fps for MAGI)
        
    Returns:
        FrameSynchronizer instance
    """
    return FrameSynchronizer(target_fps=target_fps)