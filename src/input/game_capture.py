"""
Game capture module for real-time MAGI conversion
Supports screen capture, OBS integration, and game hooks
"""

import cv2
import numpy as np
import time
import threading
import queue
from typing import Optional, Tuple, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import platform


class CaptureMethod(Enum):
    """Game capture methods"""
    SCREEN_CAPTURE = "screen_capture"
    WINDOW_CAPTURE = "window_capture"
    OBS_WEBSOCKET = "obs_websocket"
    GAME_HOOK = "game_hook"
    VIRTUAL_CAMERA = "virtual_camera"


@dataclass
class GameFrame:
    """Captured game frame"""
    frame: np.ndarray
    timestamp: float
    frame_number: int
    width: int
    height: int
    fps: float
    capture_method: CaptureMethod


@dataclass
class CaptureStats:
    """Capture statistics"""
    frames_captured: int = 0
    frames_dropped: int = 0
    avg_fps: float = 0.0
    avg_latency_ms: float = 0.0
    current_latency_ms: float = 0.0


class GameCapture:
    """Real-time game capture for MAGI conversion"""
    
    def __init__(self, 
                 method: CaptureMethod = CaptureMethod.SCREEN_CAPTURE,
                 target_fps: int = 120,
                 target_resolution: Tuple[int, int] = (3840, 2160),
                 buffer_size: int = 8):
        """
        Initialize game capture
        
        Args:
            method: Capture method to use
            target_fps: Target frame rate for capture
            target_resolution: Target resolution (width, height)
            buffer_size: Frame buffer size
        """
        self.method = method
        self.target_fps = target_fps
        self.target_resolution = target_resolution
        self.buffer_size = buffer_size
        
        # Capture state
        self._running = False
        self._capture_thread = None
        self._frame_queue = queue.Queue(maxsize=buffer_size)
        self._frame_number = 0
        self._last_frame_time = 0
        
        # Statistics
        self._stats = CaptureStats()
        self._latency_samples = []
        
        # Platform-specific setup
        self._platform = platform.system()
        self._setup_capture()
    
    def _setup_capture(self):
        """Setup capture based on platform and method"""
        if self.method == CaptureMethod.SCREEN_CAPTURE:
            self._setup_screen_capture()
        elif self.method == CaptureMethod.WINDOW_CAPTURE:
            self._setup_window_capture()
        elif self.method == CaptureMethod.OBS_WEBSOCKET:
            self._setup_obs_websocket()
        elif self.method == CaptureMethod.GAME_HOOK:
            self._setup_game_hook()
        elif self.method == CaptureMethod.VIRTUAL_CAMERA:
            self._setup_virtual_camera()
    
    def _setup_screen_capture(self):
        """Setup screen capture"""
        # Use OpenCV for screen capture
        self._screen_capture = None
        self._screen_region = None
    
    def _setup_window_capture(self):
        """Setup window capture"""
        self._window_title = None
        self._window_handle = None
    
    def _setup_obs_websocket(self):
        """Setup OBS WebSocket connection"""
        self._obs_host = "localhost"
        self._obs_port = 4455
        self._obs_password = ""
        self._obs_connected = False
    
    def _setup_game_hook(self):
        """Setup game hook (DirectX/OpenGL)"""
        self._hooked_process = None
        self._hook_active = False
    
    def _setup_virtual_camera(self):
        """Setup virtual camera capture"""
        self._camera_index = 0
        self._camera = None
    
    def start(self) -> bool:
        """
        Start game capture
        
        Returns:
            True if started successfully, False otherwise
        """
        if self._running:
            return True
        
        try:
            if self.method == CaptureMethod.SCREEN_CAPTURE:
                success = self._start_screen_capture()
            elif self.method == CaptureMethod.WINDOW_CAPTURE:
                success = self._start_window_capture()
            elif self.method == CaptureMethod.OBS_WEBSOCKET:
                success = self._start_obs_websocket()
            elif self.method == CaptureMethod.GAME_HOOK:
                success = self._start_game_hook()
            elif self.method == CaptureMethod.VIRTUAL_CAMERA:
                success = self._start_virtual_camera()
            else:
                success = False
            
            if success:
                self._running = True
                self._capture_thread = threading.Thread(
                    target=self._capture_loop,
                    daemon=True
                )
                self._capture_thread.start()
                return True
        
        except Exception as e:
            print(f"Error starting capture: {e}")
            return False
        
        return False
    
    def _start_screen_capture(self) -> bool:
        """Start screen capture"""
        try:
            # Try to use mss for faster screen capture
            import mss
            self._mss = mss.mss()
            
            # Get primary monitor
            monitor = self._mss.monitors[1]  # Primary monitor
            self._screen_region = {
                "top": monitor["top"],
                "left": monitor["left"],
                "width": monitor["width"],
                "height": monitor["height"]
            }
            return True
        
        except ImportError:
            # Fallback to OpenCV
            try:
                # Use OpenCV's VideoCapture for screen (platform-specific)
                if self._platform == "Windows":
                    # Use dshow for Windows
                    self._screen_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                elif self._platform == "Darwin":
                    # Use avfoundation for macOS
                    self._screen_capture = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
                else:
                    # Use v4l2 for Linux
                    self._screen_capture = cv2.VideoCapture(0, cv2.CAP_V4L2)
                
                return self._screen_capture.isOpened()
            
            except Exception as e:
                print(f"Error setting up screen capture: {e}")
                return False
    
    def _start_window_capture(self) -> bool:
        """Start window capture"""
        try:
            import pygetwindow as gw
            
            # Get all windows
            windows = gw.getAllWindows()
            
            # Find game windows (common game window titles)
            game_keywords = ["game", "steam", "epic", "origin", "uplay"]
            for window in windows:
                if any(keyword in window.title.lower() for keyword in game_keywords):
                    self._window_handle = window
                    self._window_title = window.title
                    print(f"Found game window: {window.title}")
                    return True
            
            # If no game window found, use the active window
            active_window = gw.getActiveWindow()
            if active_window:
                self._window_handle = active_window
                self._window_title = active_window.title
                return True
            
            return False
        
        except ImportError:
            print("pygetwindow not available, falling back to screen capture")
            self.method = CaptureMethod.SCREEN_CAPTURE
            return self._start_screen_capture()
    
    def _start_obs_websocket(self) -> bool:
        """Start OBS WebSocket connection"""
        try:
            import obsws_python as obs
            
            self._obs = obs.ReqClient(
                host=self._obs_host,
                port=self._obs_port,
                password=self._obs_password
            )
            
            # Test connection
            self._obs.get_version()
            self._obs_connected = True
            return True
        
        except ImportError:
            print("obsws_python not available")
            return False
        except Exception as e:
            print(f"Error connecting to OBS: {e}")
            return False
    
    def _start_game_hook(self) -> bool:
        """Start game hook"""
        # This would require platform-specific implementation
        # For now, return False as it's complex
        print("Game hook not implemented yet")
        return False
    
    def _start_virtual_camera(self) -> bool:
        """Start virtual camera capture"""
        try:
            self._camera = cv2.VideoCapture(self._camera_index)
            if self._camera.isOpened():
                # Set camera properties
                self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_resolution[0])
                self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_resolution[1])
                self._camera.set(cv2.CAP_PROP_FPS, self.target_fps)
                return True
            return False
        
        except Exception as e:
            print(f"Error starting virtual camera: {e}")
            return False
    
    def _capture_loop(self):
        """Main capture loop"""
        frame_interval = 1.0 / self.target_fps
        
        while self._running:
            start_time = time.time()
            
            try:
                # Capture frame
                frame = self._capture_frame()
                
                if frame is not None:
                    # Process frame
                    processed_frame = self._process_frame(frame)
                    
                    # Create game frame object
                    game_frame = GameFrame(
                        frame=processed_frame,
                        timestamp=time.time(),
                        frame_number=self._frame_number,
                        width=processed_frame.shape[1],
                        height=processed_frame.shape[0],
                        fps=self.target_fps,
                        capture_method=self.method
                    )
                    
                    # Add to queue (non-blocking)
                    try:
                        self._frame_queue.put_nowait(game_frame)
                        self._frame_number += 1
                        self._stats.frames_captured += 1
                    except queue.Full:
                        self._stats.frames_dropped += 1
                    
                    # Calculate latency
                    capture_time = time.time() - start_time
                    self._stats.current_latency_ms = capture_time * 1000
                    self._latency_samples.append(capture_time * 1000)
                    if len(self._latency_samples) > 100:
                        self._latency_samples.pop(0)
                    self._stats.avg_latency_ms = np.mean(self._latency_samples)
                
                # Calculate FPS
                if self._last_frame_time > 0:
                    elapsed = time.time() - self._last_frame_time
                    current_fps = 1.0 / elapsed if elapsed > 0 else 0
                    # Smooth FPS
                    self._stats.avg_fps = 0.9 * self._stats.avg_fps + 0.1 * current_fps
                
                self._last_frame_time = time.time()
                
                # Maintain target FPS
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_interval - elapsed)
                time.sleep(sleep_time)
            
            except Exception as e:
                print(f"Error in capture loop: {e}")
                time.sleep(0.01)
    
    def _capture_frame(self) -> Optional[np.ndarray]:
        """Capture a single frame"""
        if self.method == CaptureMethod.SCREEN_CAPTURE:
            return self._capture_screen_frame()
        elif self.method == CaptureMethod.WINDOW_CAPTURE:
            return self._capture_window_frame()
        elif self.method == CaptureMethod.OBS_WEBSOCKET:
            return self._capture_obs_frame()
        elif self.method == CaptureMethod.GAME_HOOK:
            return self._capture_hook_frame()
        elif self.method == CaptureMethod.VIRTUAL_CAMERA:
            return self._capture_camera_frame()
        return None
    
    def _capture_screen_frame(self) -> Optional[np.ndarray]:
        """Capture screen frame"""
        try:
            if hasattr(self, '_mss'):
                # Use mss for fast capture
                screenshot = self._mss.grab(self._screen_region)
                frame = np.array(screenshot)
                # Convert BGRA to BGR
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                return frame
            elif self._screen_capture and self._screen_capture.isOpened():
                # Use OpenCV
                ret, frame = self._screen_capture.read()
                if ret:
                    return frame
            return None
        
        except Exception as e:
            print(f"Error capturing screen frame: {e}")
            return None
    
    def _capture_window_frame(self) -> Optional[np.ndarray]:
        """Capture window frame"""
        try:
            import pygetwindow as gw
            
            if self._window_handle:
                # Get window bounds
                bbox = (
                    self._window_handle.left,
                    self._window_handle.top,
                    self._window_handle.width,
                    self._window_handle.height
                )
                
                # Capture window region
                if hasattr(self, '_mss'):
                    screenshot = self._mss.grab({
                        "top": bbox[1],
                        "left": bbox[0],
                        "width": bbox[2],
                        "height": bbox[3]
                    })
                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    return frame
            
            return None
        
        except Exception as e:
            print(f"Error capturing window frame: {e}")
            return None
    
    def _capture_obs_frame(self) -> Optional[np.ndarray]:
        """Capture OBS frame"""
        try:
            # Request screenshot from OBS
            response = self._obs.get_source_screenshot(
                source_name="Game Capture",
                image_format="jpg",
                width=self.target_resolution[0],
                height=self.target_resolution[1],
                quality=100
            )
            
            if response and 'imageData' in response:
                import base64
                import io
                from PIL import Image
                
                # Decode base64 image
                image_data = base64.b64decode(response['imageData'])
                image = Image.open(io.BytesIO(image_data))
                frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                return frame
            
            return None
        
        except Exception as e:
            print(f"Error capturing OBS frame: {e}")
            return None
    
    def _capture_hook_frame(self) -> Optional[np.ndarray]:
        """Capture hooked game frame"""
        # Not implemented yet
        return None
    
    def _capture_camera_frame(self) -> Optional[np.ndarray]:
        """Capture virtual camera frame"""
        try:
            if self._camera and self._camera.isOpened():
                ret, frame = self._camera.read()
                if ret:
                    return frame
            return None
        
        except Exception as e:
            print(f"Error capturing camera frame: {e}")
            return None
    
    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process captured frame"""
        # Resize to target resolution if needed
        if frame.shape[1] != self.target_resolution[0] or frame.shape[0] != self.target_resolution[1]:
            frame = cv2.resize(frame, self.target_resolution, interpolation=cv2.INTER_LINEAR)
        
        return frame
    
    def get_frame(self, timeout: float = 0.1) -> Optional[GameFrame]:
        """
        Get the next frame from the queue
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            GameFrame object or None if timeout
        """
        try:
            return self._frame_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_stats(self) -> CaptureStats:
        """Get capture statistics"""
        return self._stats
    
    def stop(self):
        """Stop game capture"""
        self._running = False
        
        if self._capture_thread:
            self._capture_thread.join(timeout=1.0)
        
        # Cleanup resources
        if hasattr(self, '_screen_capture') and self._screen_capture:
            self._screen_capture.release()
        
        if hasattr(self, '_camera') and self._camera:
            self._camera.release()
        
        if hasattr(self, '_obs') and self._obs_connected:
            self._obs.disconnect()
    
    def is_running(self) -> bool:
        """Check if capture is running"""
        return self._running
    
    def set_window(self, window_title: str) -> bool:
        """
        Set target window for window capture
        
        Args:
            window_title: Window title to capture
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import pygetwindow as gw
            
            windows = gw.getWindowsWithTitle(window_title)
            if windows:
                self._window_handle = windows[0]
                self._window_title = window_title
                return True
            
            return False
        
        except Exception as e:
            print(f"Error setting window: {e}")
            return False
    
    def list_windows(self) -> list:
        """List available windows"""
        try:
            import pygetwindow as gw
            windows = gw.getAllWindows()
            return [{"title": w.title, "id": id(w)} for w in windows if w.title]
        except ImportError:
            return []


def create_game_capture(method: str = "screen_capture",
                       target_fps: int = 120,
                       target_resolution: Tuple[int, int] = (3840, 2160),
                       buffer_size: int = 8) -> GameCapture:
    """
    Create game capture instance
    
    Args:
        method: Capture method (screen_capture, window_capture, obs_websocket, game_hook, virtual_camera)
        target_fps: Target frame rate
        target_resolution: Target resolution (width, height)
        buffer_size: Frame buffer size
        
    Returns:
        GameCapture instance
    """
    try:
        capture_method = CaptureMethod(method)
    except ValueError:
        capture_method = CaptureMethod.SCREEN_CAPTURE
    
    return GameCapture(
        method=capture_method,
        target_fps=target_fps,
        target_resolution=target_resolution,
        buffer_size=buffer_size
    )


if __name__ == "__main__":
    # Test game capture
    print("Testing game capture...")
    
    capture = create_game_capture(
        method="screen_capture",
        target_fps=60,
        target_resolution=(1920, 1080)
    )
    
    if capture.start():
        print("Capture started successfully!")
        
        # Capture 10 frames
        for i in range(10):
            frame = capture.get_frame(timeout=1.0)
            if frame:
                print(f"Frame {i}: {frame.width}x{frame.height}, latency: {capture._stats.current_latency_ms:.2f}ms")
            else:
                print(f"Frame {i}: timeout")
        
        stats = capture.get_stats()
        print(f"\nStats:")
        print(f"  Frames captured: {stats.frames_captured}")
        print(f"  Frames dropped: {stats.frames_dropped}")
        print(f"  Avg FPS: {stats.avg_fps:.2f}")
        print(f"  Avg latency: {stats.avg_latency_ms:.2f}ms")
        
        capture.stop()
        print("Capture stopped.")
    else:
        print("Failed to start capture.")
