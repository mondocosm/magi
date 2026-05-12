"""
StereoCrafter integration for MAGI Pipeline
Converts 2D videos to high-quality stereoscopic 3D using diffusion-based generation
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import numpy as np
import cv2

from ..core.exceptions import ProcessingError
from ..core.logger import LoggerMixin


class StereoCrafterIntegration(LoggerMixin):
    """Integration with StereoCrafter for 2D to 3D conversion"""
    
    def __init__(self, stereocrafter_path: str = "../StereoCrafter", 
                 weights_path: Optional[str] = None,
                 max_disp: int = 20):
        """
        Initialize StereoCrafter integration
        
        Args:
            stereocrafter_path: Path to StereoCrafter directory
            weights_path: Path to model weights (uses default if not specified)
            max_disp: Maximum disparity for depth-based splatting
        """
        self.stereocrafter_path = Path(stereocrafter_path)
        self.weights_path = Path(weights_path) if weights_path else self.stereocrafter_path / "weights"
        self.max_disp = max_disp
        
        # Verify StereoCrafter installation
        if not self.stereocrafter_path.exists():
            self.logger.warning(f"StereoCrafter not found at {stereocrafter_path}")
            self.available = False
        else:
            self.available = True
            self.logger.info(f"StereoCrafter integration initialized at {stereocrafter_path}")
    
    def is_available(self) -> bool:
        """
        Check if StereoCrafter is available
        
        Returns:
            True if available, False otherwise
        """
        return self.available
    
    def convert_2d_to_3d(self, input_video: str, output_video: str, 
                        tile_num: int = 1) -> bool:
        """
        Convert 2D video to 3D using StereoCrafter
        
        Args:
            input_video: Path to input 2D video
            output_video: Path to output 3D video
            tile_num: Number of tiles for processing (higher = more memory efficient)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.available:
            raise ProcessingError("StereoCrafter is not available")
        
        self.logger.info(f"Converting 2D to 3D: {input_video} -> {output_video}")
        
        try:
            # Step 1: Depth-based video splatting
            splatting_output = self._run_depth_splatting(input_video)
            
            # Step 2: Stereo video inpainting
            success = self._run_stereo_inpainting(splatting_output, output_video, tile_num)
            
            if success:
                self.logger.info(f"2D to 3D conversion complete: {output_video}")
                return True
            else:
                self.logger.error("Stereo inpainting failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in 2D to 3D conversion: {e}")
            return False
    
    def _run_depth_splatting(self, input_video: str) -> str:
        """
        Run depth-based video splatting
        
        Args:
            input_video: Path to input video
            
        Returns:
            Path to splatting output video
        """
        self.logger.info("Running depth-based video splatting")
        
        # Prepare paths
        output_dir = self.stereocrafter_path / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        input_name = Path(input_video).stem
        splatting_output = output_dir / f"{input_name}_splatting_results.mp4"
        
        # Build command
        cmd = [
            sys.executable,
            str(self.stereocrafter_path / "depth_splatting_inference.py"),
            "--pre_trained_path", str(self.weights_path / "stable-video-diffusion-img2vid-xt-1-1"),
            "--unet_path", str(self.weights_path / "DepthCrafter"),
            "--input_video_path", input_video,
            "--output_video_path", str(splatting_output),
            "--max_disp", str(self.max_disp)
        ]
        
        # Run command
        result = subprocess.run(
            cmd,
            cwd=str(self.stereocrafter_path),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise ProcessingError(f"Depth splatting failed: {result.stderr}")
        
        self.logger.info(f"Depth splatting complete: {splatting_output}")
        return str(splatting_output)
    
    def _run_stereo_inpainting(self, input_video: str, output_video: str, 
                              tile_num: int = 1) -> bool:
        """
        Run stereo video inpainting
        
        Args:
            input_video: Path to splatting video
            output_video: Path to final output video
            tile_num: Number of tiles for processing
            
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Running stereo video inpainting")
        
        # Prepare paths
        output_dir = Path(output_video).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Build command
        cmd = [
            sys.executable,
            str(self.stereocrafter_path / "inpainting_inference.py"),
            "--pre_trained_path", str(self.weights_path / "stable-video-diffusion-img2vid-xt-1-1"),
            "--unet_path", str(self.weights_path / "StereoCrafter"),
            "--input_video_path", input_video,
            "--save_dir", str(output_dir),
            "--tile_num", str(tile_num)
        ]
        
        # Run command
        result = subprocess.run(
            cmd,
            cwd=str(self.stereocrafter_path),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            self.logger.error(f"Stereo inpainting failed: {result.stderr}")
            return False
        
        # StereoCrafter outputs side-by-side format
        # The output file will be named based on input
        input_name = Path(input_video).stem.replace("_splatting_results", "")
        sbs_output = output_dir / f"{input_name}_sbs.mp4"
        
        # Copy to desired output location if different
        if sbs_output.exists() and str(sbs_output) != output_video:
            import shutil
            shutil.copy(str(sbs_output), output_video)
        
        self.logger.info(f"Stereo inpainting complete: {output_video}")
        return True
    
    def convert_frame_to_3d(self, frame: np.ndarray, depth_map: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert single 2D frame to 3D stereo pair
        
        Args:
            frame: Input 2D frame
            depth_map: Optional depth map (will estimate if not provided)
            
        Returns:
            Tuple of (left_frame, right_frame)
        """
        if not self.available:
            # Fall back to simple depth-based conversion
            return self._simple_2d_to_3d(frame, depth_map)
        
        # For single frame conversion, we'd need to implement frame-level StereoCrafter
        # For now, fall back to simple conversion
        self.logger.warning("Frame-level StereoCrafter not implemented, using simple conversion")
        return self._simple_2d_to_3d(frame, depth_map)
    
    def _simple_2d_to_3d(self, frame: np.ndarray, depth_map: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simple 2D to 3D conversion using depth estimation
        
        Args:
            frame: Input 2D frame
            depth_map: Optional depth map
            
        Returns:
            Tuple of (left_frame, right_frame)
        """
        # Estimate depth if not provided
        if depth_map is None:
            depth_map = self._estimate_depth(frame)
        
        # Generate left and right views
        left_view = self._shift_view(frame, depth_map, shift_amount=-self.max_disp)
        right_view = self._shift_view(frame, depth_map, shift_amount=self.max_disp)
        
        return left_view, right_view
    
    def _estimate_depth(self, frame: np.ndarray) -> np.ndarray:
        """
        Estimate depth map from 2D frame
        
        Args:
            frame: Input frame
            
        Returns:
            Depth map
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Simple depth estimation based on gradient and edge detection
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Calculate gradient magnitude
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Normalize to 0-1 range
        depth_map = gradient_magnitude / np.max(gradient_magnitude)
        
        # Invert (edges are typically closer)
        depth_map = 1.0 - depth_map
        
        # Apply Gaussian blur for smoothness
        depth_map = cv2.GaussianBlur(depth_map, (15, 15), 0)
        
        return depth_map
    
    def _shift_view(self, frame: np.ndarray, depth_map: np.ndarray, shift_amount: int) -> np.ndarray:
        """
        Shift view based on depth map
        
        Args:
            frame: Input frame
            depth_map: Depth map
            shift_amount: Amount to shift (positive = right, negative = left)
            
        Returns:
            Shifted view
        """
        height, width = frame.shape[:2]
        shifted = np.zeros_like(frame)
        
        # Create mesh grid
        x_coords, y_coords = np.meshgrid(np.arange(width), np.arange(height))
        
        # Calculate shift based on depth
        shift = depth_map * shift_amount
        
        # Apply shift to x coordinates
        x_shifted = x_coords + shift
        
        # Clip to valid range
        x_shifted = np.clip(x_shifted, 0, width - 1)
        
        # Remap frame
        for c in range(frame.shape[2]):
            shifted[:, :, c] = cv2.remap(
                frame[:, :, c],
                x_shifted.astype(np.float32),
                y_coords.astype(np.float32),
                cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REFLECT
            )
        
        return shifted
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about StereoCrafter models
        
        Returns:
            Dictionary with model information
        """
        return {
            'available': self.available,
            'path': str(self.stereocrafter_path),
            'weights_path': str(self.weights_path),
            'max_disp': self.max_disp,
            'models': {
                'svd_img2vid': str(self.weights_path / "stable-video-diffusion-img2vid-xt-1-1"),
                'depthcrafter': str(self.weights_path / "DepthCrafter"),
                'stereocrafter': str(self.weights_path / "StereoCrafter"),
            }
        }
    
    def check_dependencies(self) -> Dict[str, bool]:
        """
        Check if all required dependencies are available
        
        Returns:
            Dictionary with dependency status
        """
        dependencies = {
            'stereocrafter': self.stereocrafter_path.exists(),
            'svd_model': (self.weights_path / "stable-video-diffusion-img2vid-xt-1-1").exists(),
            'depthcrafter': (self.weights_path / "DepthCrafter").exists(),
            'stereocrafter_model': (self.weights_path / "StereoCrafter").exists(),
        }
        
        return dependencies