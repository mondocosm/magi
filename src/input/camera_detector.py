"""
Camera Detector Module for MAGI Pipeline

Automatically detects and identifies available cameras:
- Stereo cameras (ZED, Google 180 VR, HUD stereo cameras)
- Depth cameras (Xbox Kinect, Intel RealSense, Azure Kinect)
- VR cameras (Insta360, Ricoh Theta)
- Generic stereo webcams
- Generic mono webcams
"""

import cv2
import numpy as np
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from .camera_capture import CameraType, CameraFormat, CameraInfo

logger = logging.getLogger(__name__)


class CameraBackend(Enum):
    """Supported camera backends"""
    OPENCV = "opencv"
    ZED = "zed"
    REALSENSE = "realsense"
    KINECT = "kinect"
    AZURE_KINECT = "azure_kinect"
    INSTA360 = "insta360"
    RICOH_THETA = "ricoh_theta"


@dataclass
class DetectedCamera:
    """Detected camera information"""
    camera_id: int
    camera_type: CameraType
    name: str
    width: int
    height: int
    fps: float
    format: CameraFormat
    backend: CameraBackend
    device_path: Optional[str] = None
    is_stereo: bool = False
    has_depth: bool = False
    is_available: bool = True
    additional_info: Dict[str, Any] = None


class CameraDetector:
    """
    Camera detector for finding available cameras
    
    Features:
    - Automatic camera detection
    - Camera type identification
    - Format detection (SBS, TAB, sequential)
    - Capability detection (stereo, depth)
    - Multiple backend support
    """
    
    def __init__(self):
        """Initialize camera detector"""
        self.detected_cameras: List[DetectedCamera] = []
        self.backends_available = self._check_backends()
        
    def _check_backends(self) -> Dict[CameraBackend, bool]:
        """Check which camera backends are available"""
        backends = {}
        
        # OpenCV is always available
        backends[CameraBackend.OPENCV] = True
        
        # Check ZED SDK
        try:
            import pyzed.sl
            backends[CameraBackend.ZED] = True
            logger.info("ZED SDK detected")
        except ImportError:
            backends[CameraBackend.ZED] = False
            
        # Check RealSense SDK
        try:
            import pyrealsense2
            backends[CameraBackend.REALSENSE] = True
            logger.info("RealSense SDK detected")
        except ImportError:
            backends[CameraBackend.REALSENSE] = False
            
        # Check Kinect SDK
        try:
            import pykinect2
            backends[CameraBackend.KINECT] = True
            logger.info("Kinect SDK detected")
        except ImportError:
            backends[CameraBackend.KINECT] = False
            
        # Check Azure Kinect
        try:
            import azure_kinect
            backends[CameraBackend.AZURE_KINECT] = True
            logger.info("Azure Kinect SDK detected")
        except ImportError:
            backends[CameraBackend.AZURE_KINECT] = False
            
        return backends
    
    def detect_all(self) -> List[DetectedCamera]:
        """
        Detect all available cameras
        
        Returns:
            List of detected cameras
        """
        self.detected_cameras = []
        
        # Detect OpenCV cameras
        if self.backends_available[CameraBackend.OPENCV]:
            self._detect_opencv_cameras()
            
        # Detect ZED cameras
        if self.backends_available[CameraBackend.ZED]:
            self._detect_zed_cameras()
            
        # Detect RealSense cameras
        if self.backends_available[CameraBackend.REALSENSE]:
            self._detect_realsense_cameras()
            
        # Detect Kinect cameras
        if self.backends_available[CameraBackend.KINECT]:
            self._detect_kinect_cameras()
            
        # Detect Azure Kinect cameras
        if self.backends_available[CameraBackend.AZURE_KINECT]:
            self._detect_azure_kinect_cameras()
            
        logger.info(f"Detected {len(self.detected_cameras)} camera(s)")
        return self.detected_cameras
    
    def _detect_opencv_cameras(self) -> None:
        """Detect OpenCV-compatible cameras"""
        # Try camera IDs 0-9
        for camera_id in range(10):
            try:
                cap = cv2.VideoCapture(camera_id)
                
                if not cap.isOpened():
                    cap.release()
                    continue
                    
                # Get camera properties
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                # Try to capture a frame to detect format
                ret, frame = cap.read()
                
                if ret and frame is not None:
                    # Detect camera type and format
                    camera_type, camera_format, is_stereo, has_depth = self._analyze_frame(
                        frame, width, height
                    )
                    
                    # Get camera name
                    name = self._get_camera_name(camera_id, camera_type)
                    
                    detected_camera = DetectedCamera(
                        camera_id=camera_id,
                        camera_type=camera_type,
                        name=name,
                        width=width,
                        height=height,
                        fps=fps if fps > 0 else 30.0,
                        format=camera_format,
                        backend=CameraBackend.OPENCV,
                        is_stereo=is_stereo,
                        has_depth=has_depth,
                        is_available=True
                    )
                    
                    self.detected_cameras.append(detected_camera)
                    logger.info(f"Detected OpenCV camera: {name} ({width}x{height} @ {fps}fps)")
                
                cap.release()
                
            except Exception as e:
                logger.debug(f"Error checking camera {camera_id}: {e}")
                continue
    
    def _detect_zed_cameras(self) -> None:
        """Detect ZED cameras"""
        try:
            import pyzed.sl as sl
            
            # Create ZED camera object
            zed = sl.Camera()
            
            # Try to open camera
            init_params = sl.InitParameters()
            err = zed.open(init_params)
            
            if err == sl.ERROR_CODE.SUCCESS:
                # Get camera information
                camera_info = zed.get_camera_information()
                serial_number = camera_info.serial_number
                model = camera_info.camera_model
                
                # Get resolution
                resolution = camera_info.camera_resolution
                width = resolution.width
                height = resolution.height
                
                detected_camera = DetectedCamera(
                    camera_id=0,
                    camera_type=CameraType.ZED,
                    name=f"ZED {model.name} (SN: {serial_number})",
                    width=width,
                    height=height,
                    fps=30.0,
                    format=CameraFormat.STEREO_SEQUENTIAL,
                    backend=CameraBackend.ZED,
                    is_stereo=True,
                    has_depth=True,
                    is_available=True,
                    additional_info={
                        "serial_number": serial_number,
                        "model": model.name
                    }
                )
                
                self.detected_cameras.append(detected_camera)
                logger.info(f"Detected ZED camera: {detected_camera.name}")
                
                zed.close()
                
        except Exception as e:
            logger.debug(f"Error detecting ZED camera: {e}")
    
    def _detect_realsense_cameras(self) -> None:
        """Detect Intel RealSense cameras"""
        try:
            import pyrealsense2 as rs
            
            # Create context
            ctx = rs.context()
            devices = ctx.query_devices()
            
            for i, device in enumerate(devices):
                # Get device info
                name = device.get_info(rs.camera_info.name)
                serial = device.get_info(rs.camera_info.serial_number)
                
                detected_camera = DetectedCamera(
                    camera_id=i,
                    camera_type=CameraType.REALSENSE,
                    name=f"{name} (SN: {serial})",
                    width=1920,
                    height=1080,
                    fps=30.0,
                    format=CameraFormat.DEPTH_COLOR,
                    backend=CameraBackend.REALSENSE,
                    is_stereo=False,
                    has_depth=True,
                    is_available=True,
                    additional_info={
                        "serial_number": serial,
                        "product_name": name
                    }
                )
                
                self.detected_cameras.append(detected_camera)
                logger.info(f"Detected RealSense camera: {detected_camera.name}")
                
        except Exception as e:
            logger.debug(f"Error detecting RealSense cameras: {e}")
    
    def _detect_kinect_cameras(self) -> None:
        """Detect Xbox Kinect cameras"""
        try:
            import pykinect2
            from pykinect2 import PyKinectV2
            
            # Try to initialize Kinect
            kinect = PyKinectV2.PyKinectRuntime(
                PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Depth
            )
            
            detected_camera = DetectedCamera(
                camera_id=0,
                camera_type=CameraType.KINECT,
                name="Xbox Kinect v2",
                width=1920,
                height=1080,
                fps=30.0,
                format=CameraFormat.DEPTH_COLOR,
                backend=CameraBackend.KINECT,
                is_stereo=False,
                has_depth=True,
                is_available=True
            )
            
            self.detected_cameras.append(detected_camera)
            logger.info(f"Detected Kinect camera: {detected_camera.name}")
            
        except Exception as e:
            logger.debug(f"Error detecting Kinect camera: {e}")
    
    def _detect_azure_kinect_cameras(self) -> None:
        """Detect Azure Kinect cameras"""
        try:
            import azure_kinect
            
            # Try to detect Azure Kinect devices
            # (Implementation depends on specific Azure Kinect SDK)
            
            detected_camera = DetectedCamera(
                camera_id=0,
                camera_type=CameraType.AZURE_KINECT,
                name="Azure Kinect DK",
                width=3840,
                height=2160,
                fps=30.0,
                format=CameraFormat.DEPTH_COLOR,
                backend=CameraBackend.AZURE_KINECT,
                is_stereo=False,
                has_depth=True,
                is_available=True
            )
            
            self.detected_cameras.append(detected_camera)
            logger.info(f"Detected Azure Kinect camera: {detected_camera.name}")
            
        except Exception as e:
            logger.debug(f"Error detecting Azure Kinect camera: {e}")
    
    def _analyze_frame(
        self,
        frame: np.ndarray,
        width: int,
        height: int
    ) -> tuple[CameraType, CameraFormat, bool, bool]:
        """
        Analyze a frame to determine camera type and format
        
        Args:
            frame: Captured frame
            width: Frame width
            height: Frame height
            
        Returns:
            Tuple of (camera_type, camera_format, is_stereo, has_depth)
        """
        h, w = frame.shape[:2]
        
        # Check for side-by-side stereo
        if w >= 2 * h:
            # Likely side-by-side stereo
            return CameraType.GENERIC_STEREO, CameraFormat.STEREO_SBS, True, False
            
        # Check for top-bottom stereo
        if h >= 2 * w:
            # Likely top-bottom stereo
            return CameraType.GENERIC_STEREO, CameraFormat.STEREO_TAB, True, False
            
        # Check for depth channel
        if len(frame.shape) == 3 and frame.shape[2] == 4:
            # Might have depth in alpha channel
            return CameraType.GENERIC_MONO, CameraFormat.DEPTH_COLOR, False, True
            
        # Default to mono
        return CameraType.GENERIC_MONO, CameraFormat.MONO, False, False
    
    def _get_camera_name(self, camera_id: int, camera_type: CameraType) -> str:
        """
        Get camera name based on ID and type
        
        Args:
            camera_id: Camera ID
            camera_type: Camera type
            
        Returns:
            Camera name
        """
        # Try to get camera name from backend
        try:
            cap = cv2.VideoCapture(camera_id)
            if cap.isOpened():
                backend_name = cap.getBackendName()
                cap.release()
                
                if backend_name:
                    return f"Camera {camera_id} ({backend_name})"
        except:
            pass
        
        # Fallback to type-based name
        type_names = {
            CameraType.GENERIC_MONO: f"Mono Camera {camera_id}",
            CameraType.GENERIC_STEREO: f"Stereo Camera {camera_id}",
            CameraType.HUD_STEREO: f"HUD Stereo Camera {camera_id}",
            CameraType.GOOGLE_180_VR: f"Google 180 VR Camera {camera_id}",
            CameraType.INSTA360: f"Insta360 Camera {camera_id}",
            CameraType.RICOH_THETA: f"Ricoh Theta Camera {camera_id}",
        }
        
        return type_names.get(camera_type, f"Camera {camera_id}")
    
    def get_camera_by_id(self, camera_id: int) -> Optional[DetectedCamera]:
        """
        Get camera by ID
        
        Args:
            camera_id: Camera ID
            
        Returns:
            DetectedCamera or None
        """
        for camera in self.detected_cameras:
            if camera.camera_id == camera_id:
                return camera
        return None
    
    def get_cameras_by_type(self, camera_type: CameraType) -> List[DetectedCamera]:
        """
        Get cameras by type
        
        Args:
            camera_type: Camera type
            
        Returns:
            List of cameras of the specified type
        """
        return [c for c in self.detected_cameras if c.camera_type == camera_type]
    
    def get_stereo_cameras(self) -> List[DetectedCamera]:
        """Get all stereo cameras"""
        return [c for c in self.detected_cameras if c.is_stereo]
    
    def get_depth_cameras(self) -> List[DetectedCamera]:
        """Get all depth cameras"""
        return [c for c in self.detected_cameras if c.has_depth]
    
    def get_available_backends(self) -> List[CameraBackend]:
        """Get list of available backends"""
        return [backend for backend, available in self.backends_available.items() if available]
    
    def print_summary(self) -> None:
        """Print summary of detected cameras"""
        print("\n" + "="*60)
        print("DETECTED CAMERAS")
        print("="*60)
        
        if not self.detected_cameras:
            print("No cameras detected")
            return
            
        for i, camera in enumerate(self.detected_cameras, 1):
            print(f"\n{i}. {camera.name}")
            print(f"   Type: {camera.camera_type.value}")
            print(f"   Resolution: {camera.width}x{camera.height}")
            print(f"   FPS: {camera.fps}")
            print(f"   Format: {camera.format.value}")
            print(f"   Backend: {camera.backend.value}")
            print(f"   Stereo: {'Yes' if camera.is_stereo else 'No'}")
            print(f"   Depth: {'Yes' if camera.has_depth else 'No'}")
            print(f"   Available: {'Yes' if camera.is_available else 'No'}")
        
        print("\n" + "="*60)
