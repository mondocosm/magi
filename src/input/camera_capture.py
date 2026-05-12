"""
Camera Capture Module for MAGI Pipeline

Supports various camera types:
- Stereo cameras (ZED, Google 180 VR, HUD stereo cameras)
- Depth cameras (Xbox Kinect, Intel RealSense, Azure Kinect)
- VR cameras (Insta360, Ricoh Theta)
- Generic stereo webcams
"""

import cv2
import numpy as np
import threading
import queue
import time
from typing import Optional, Tuple, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CameraType(Enum):
    """Supported camera types"""
    ZED = "zed"
    KINECT = "kinect"
    REALSENSE = "realsense"
    AZURE_KINECT = "azure_kinect"
    GOOGLE_180_VR = "google_180_vr"
    INSTA360 = "insta360"
    RICOH_THETA = "ricoh_theta"
    HUD_STEREO = "hud_stereo"
    GENERIC_STEREO = "generic_stereo"
    GENERIC_MONO = "generic_mono"
    UNKNOWN = "unknown"


class CameraFormat(Enum):
    """Camera output formats"""
    STEREO_SBS = "stereo_sbs"  # Side-by-side
    STEREO_TAB = "stereo_tab"  # Top-bottom
    STEREO_SEQUENTIAL = "stereo_sequential"  # Frame-sequential
    DEPTH_COLOR = "depth_color"  # Depth + color
    MONO = "mono"  # Single view
    VR_180 = "vr_180"  # 180-degree VR
    VR_360 = "vr_360"  # 360-degree VR


@dataclass
class CameraInfo:
    """Camera information"""
    camera_id: int
    camera_type: CameraType
    name: str
    width: int
    height: int
    fps: float
    format: CameraFormat
    backend: str = "opencv"
    device_path: Optional[str] = None
    is_stereo: bool = False
    has_depth: bool = False
    additional_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CameraFrame:
    """Camera frame data"""
    left: Optional[np.ndarray] = None
    right: Optional[np.ndarray] = None
    depth: Optional[np.ndarray] = None
    color: Optional[np.ndarray] = None
    timestamp: float = 0.0
    frame_number: int = 0
    camera_type: CameraType = CameraType.UNKNOWN


class CameraCapture:
    """
    Camera capture class supporting various camera types
    
    Features:
    - Real-time capture from stereo/depth cameras
    - Automatic camera detection
    - Format conversion (SBS, TAB, sequential)
    - Depth data extraction
    - Thread-safe frame access
    - Performance monitoring
    """
    
    def __init__(
        self,
        camera_id: int = 0,
        camera_type: CameraType = CameraType.GENERIC_MONO,
        width: int = 1920,
        height: int = 1080,
        fps: float = 30.0,
        format: CameraFormat = CameraFormat.MONO,
        backend: str = "opencv"
    ):
        """
        Initialize camera capture
        
        Args:
            camera_id: Camera device ID or path
            camera_type: Type of camera
            width: Capture width
            height: Capture height
            fps: Target frame rate
            format: Camera output format
            backend: Capture backend (opencv, zed, realsense, etc.)
        """
        self.camera_id = camera_id
        self.camera_type = camera_type
        self.width = width
        self.height = height
        self.fps = fps
        self.format = format
        self.backend = backend
        
        self.cap = None
        self.running = False
        self.thread = None
        self.frame_queue = queue.Queue(maxsize=10)
        self.frame_count = 0
        self.start_time = 0.0
        self.last_frame_time = 0.0
        
        # Statistics
        self.stats = {
            "fps": 0.0,
            "frames_captured": 0,
            "frames_dropped": 0,
            "avg_latency": 0.0,
            "current_latency": 0.0
        }
        
        # Camera-specific settings
        self.camera_settings = {}
        
    def start(self) -> bool:
        """
        Start camera capture
        
        Returns:
            True if successful, False otherwise
        """
        if self.running:
            logger.warning("Camera already running")
            return False
            
        try:
            # Initialize camera based on type
            if self.backend == "opencv":
                success = self._init_opencv()
            elif self.backend == "zed":
                success = self._init_zed()
            elif self.backend == "realsense":
                success = self._init_realsense()
            elif self.backend == "kinect":
                success = self._init_kinect()
            else:
                logger.error(f"Unknown backend: {self.backend}")
                return False
                
            if not success:
                logger.error("Failed to initialize camera")
                return False
                
            self.running = True
            self.start_time = time.time()
            self.last_frame_time = time.time()
            
            # Start capture thread
            self.thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.thread.start()
            
            logger.info(f"Camera started: {self.camera_type.value} @ {self.fps}fps")
            return True
            
        except Exception as e:
            logger.error(f"Error starting camera: {e}")
            return False
    
    def stop(self) -> None:
        """Stop camera capture"""
        if not self.running:
            return
            
        self.running = False
        
        # Wait for thread to finish
        if self.thread:
            self.thread.join(timeout=2.0)
            
        # Release camera
        if self.cap:
            self.cap.release()
            self.cap = None
            
        logger.info("Camera stopped")
    
    def _init_opencv(self) -> bool:
        """Initialize OpenCV camera"""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera {self.camera_id}")
                return False
                
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Verify settings
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            logger.info(f"Camera initialized: {actual_width}x{actual_height} @ {actual_fps}fps")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing OpenCV camera: {e}")
            return False
    
    def _init_zed(self) -> bool:
        """Initialize ZED camera"""
        try:
            import pyzed.sl as sl
            
            # Create ZED camera object
            self.cap = sl.Camera()
            
            # Configure camera
            init_params = sl.InitParameters()
            init_params.camera_resolution = sl.RESOLUTION.HD1080
            init_params.camera_fps = int(self.fps)
            init_params.depth_mode = sl.DEPTH_MODE.ULTRA
            init_params.coordinate_units = sl.UNIT.MILLIMETER
            
            # Open camera
            err = self.cap.open(init_params)
            if err != sl.ERROR_CODE.SUCCESS:
                logger.error(f"Failed to open ZED camera: {err}")
                return False
                
            logger.info("ZED camera initialized")
            return True
            
        except ImportError:
            logger.error("ZED SDK not installed. Install with: pip install pyzed")
            return False
        except Exception as e:
            logger.error(f"Error initializing ZED camera: {e}")
            return False
    
    def _init_realsense(self) -> bool:
        """Initialize Intel RealSense camera"""
        try:
            import pyrealsense2 as rs
            
            # Create pipeline
            self.cap = rs.pipeline()
            
            # Configure streams
            config = rs.config()
            config.enable_stream(rs.stream.color, self.width, self.height, rs.format.bgr8, int(self.fps))
            config.enable_stream(rs.stream.depth, self.width, self.height, rs.format.z16, int(self.fps))
            
            # Start pipeline
            profile = self.cap.start(config)
            
            logger.info("RealSense camera initialized")
            return True
            
        except ImportError:
            logger.error("RealSense SDK not installed. Install with: pip install pyrealsense2")
            return False
        except Exception as e:
            logger.error(f"Error initializing RealSense camera: {e}")
            return False
    
    def _init_kinect(self) -> bool:
        """Initialize Xbox Kinect camera"""
        try:
            # Try libfreenect2
            import pykinect2
            from pykinect2 import PyKinectV2
            
            # Initialize Kinect
            self.cap = PyKinectV2.PyKinectRuntime(
                PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Depth
            )
            
            logger.info("Kinect camera initialized")
            return True
            
        except ImportError:
            logger.error("Kinect SDK not installed. Install with: pip install pykinect2")
            return False
        except Exception as e:
            logger.error(f"Error initializing Kinect camera: {e}")
            return False
    
    def _capture_loop(self) -> None:
        """Main capture loop running in thread"""
        while self.running:
            try:
                frame = self._capture_frame()
                
                if frame is not None:
                    # Update statistics
                    self._update_stats()
                    
                    # Add to queue (drop if full)
                    try:
                        self.frame_queue.put(frame, timeout=0.01)
                    except queue.Full:
                        self.stats["frames_dropped"] += 1
                        
                time.sleep(0.001)  # Small sleep to prevent CPU overload
                
            except Exception as e:
                logger.error(f"Error in capture loop: {e}")
                time.sleep(0.1)
    
    def _capture_frame(self) -> Optional[CameraFrame]:
        """Capture a single frame"""
        try:
            if self.backend == "opencv":
                return self._capture_opencv()
            elif self.backend == "zed":
                return self._capture_zed()
            elif self.backend == "realsense":
                return self._capture_realsense()
            elif self.backend == "kinect":
                return self._capture_kinect()
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None
    
    def _capture_opencv(self) -> Optional[CameraFrame]:
        """Capture frame from OpenCV camera"""
        ret, frame = self.cap.read()
        
        if not ret or frame is None:
            return None
            
        self.frame_count += 1
        timestamp = time.time()
        
        # Process based on format
        if self.format == CameraFormat.STEREO_SBS:
            # Split side-by-side
            h, w = frame.shape[:2]
            left = frame[:, :w//2]
            right = frame[:, w//2:]
            return CameraFrame(left=left, right=right, timestamp=timestamp, 
                             frame_number=self.frame_count, camera_type=self.camera_type)
        elif self.format == CameraFormat.STEREO_TAB:
            # Split top-bottom
            h, w = frame.shape[:2]
            left = frame[:h//2, :]
            right = frame[h//2:, :]
            return CameraFrame(left=left, right=right, timestamp=timestamp,
                             frame_number=self.frame_count, camera_type=self.camera_type)
        else:
            # Mono
            return CameraFrame(color=frame, timestamp=timestamp,
                             frame_number=self.frame_count, camera_type=self.camera_type)
    
    def _capture_zed(self) -> Optional[CameraFrame]:
        """Capture frame from ZED camera"""
        import pyzed.sl as sl
        
        # Create image and depth objects
        image = sl.Mat()
        depth = sl.Mat()
        
        # Grab frame
        if self.cap.grab() == sl.ERROR_CODE.SUCCESS:
            # Retrieve images
            self.cap.retrieve_image(image, sl.VIEW.LEFT)
            self.cap.retrieve_image(depth, sl.VIEW.DEPTH)
            
            # Convert to numpy
            left_img = image.get_data()
            depth_img = depth.get_data()
            
            self.frame_count += 1
            timestamp = time.time()
            
            return CameraFrame(left=left_img, depth=depth_img, timestamp=timestamp,
                             frame_number=self.frame_count, camera_type=self.camera_type)
        
        return None
    
    def _capture_realsense(self) -> Optional[CameraFrame]:
        """Capture frame from RealSense camera"""
        import pyrealsense2 as rs
        
        # Wait for frames
        frames = self.cap.wait_for_frames()
        
        # Get color and depth frames
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        
        if not color_frame or not depth_frame:
            return None
            
        # Convert to numpy
        color_img = np.asanyarray(color_frame.get_data())
        depth_img = np.asanyarray(depth_frame.get_data())
        
        self.frame_count += 1
        timestamp = time.time()
        
        return CameraFrame(color=color_img, depth=depth_img, timestamp=timestamp,
                         frame_number=self.frame_count, camera_type=self.camera_type)
    
    def _capture_kinect(self) -> Optional[CameraFrame]:
        """Capture frame from Kinect camera"""
        # Get color frame
        if self.cap.has_new_color_frame():
            color_frame = self.cap.get_last_color_frame()
            color_img = color_frame.copy()
            
            # Get depth frame
            if self.cap.has_new_depth_frame():
                depth_frame = self.cap.get_last_depth_frame()
                depth_img = depth_frame.copy()
            else:
                depth_img = None
                
            self.frame_count += 1
            timestamp = time.time()
            
            return CameraFrame(color=color_img, depth=depth_img, timestamp=timestamp,
                             frame_number=self.frame_count, camera_type=self.camera_type)
        
        return None
    
    def _update_stats(self) -> None:
        """Update capture statistics"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        if elapsed > 0:
            self.stats["fps"] = self.frame_count / elapsed
            
        self.stats["frames_captured"] = self.frame_count
        self.stats["current_latency"] = current_time - self.last_frame_time
        self.stats["avg_latency"] = (
            self.stats["avg_latency"] * 0.9 + self.stats["current_latency"] * 0.1
        )
        self.last_frame_time = current_time
    
    def get_frame(self, timeout: float = 1.0) -> Optional[CameraFrame]:
        """
        Get the latest frame
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            CameraFrame or None if timeout
        """
        try:
            return self.frame_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get capture statistics"""
        return self.stats.copy()
    
    def is_running(self) -> bool:
        """Check if camera is running"""
        return self.running
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
