"""
MAGI file reader
Reads .magi files with HEVC H.265 codec and MAGI metadata
"""

import cv2
import numpy as np
import json
from typing import Optional, Tuple, Dict, Any, Iterator
from pathlib import Path
import subprocess
import tempfile
import os

from ..core.magi_metadata import MAGIMetadataHandler, MAGIMetadata


class MAGIReader:
    """Read MAGI files with HEVC H.265 codec"""
    
    def __init__(self, input_path: str):
        """
        Initialize MAGI reader
        
        Args:
            input_path: Input file path (.magi)
        """
        self.input_path = Path(input_path)
        
        # Metadata handler
        self.metadata_handler = MAGIMetadataHandler()
        self.metadata = None
        
        # Video capture
        self.video_capture = None
        self.is_open = False
        
        # Frame tracking
        self.current_frame_number = 0
        self.total_frames = 0
        
        # Video properties
        self.frame_rate = 0
        self.resolution = (0, 0)
        self.codec = ""
    
    def open(self):
        """Open MAGI file for reading"""
        if self.is_open:
            return
        
        if not self.input_path.exists():
            raise FileNotFoundError(f"MAGI file not found: {self.input_path}")
        
        # Open video file
        self.video_capture = cv2.VideoCapture(str(self.input_path))
        
        if not self.video_capture.isOpened():
            raise RuntimeError(f"Failed to open MAGI file: {self.input_path}")
        
        # Get video properties
        self.frame_rate = int(self.video_capture.get(cv2.CAP_PROP_FPS))
        width = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.resolution = (width, height)
        self.total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Get codec
        fourcc = int(self.video_capture.get(cv2.CAP_PROP_FOURCC))
        self.codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
        
        # Extract and parse metadata
        self._extract_metadata()
        
        self.is_open = True
    
    def _extract_metadata(self):
        """Extract MAGI metadata from file"""
        try:
            # Use FFprobe to extract metadata
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 's',  # Select subtitle streams (metadata)
                '-show_entries', 'stream_tags=language,title',
                '-of', 'json',
                str(self.input_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            # Look for MAGI metadata stream
            for stream in data.get('streams', []):
                tags = stream.get('tags', {})
                if tags.get('title') == 'MAGI Metadata':
                    # Extract metadata from stream
                    self._extract_metadata_stream()
                    break
            
            # If no metadata stream found, create default metadata
            if not self.metadata:
                self.metadata = self.metadata_handler.create_default_metadata(
                    frame_rate=self.frame_rate,
                    resolution=f"{self.resolution[0]}x{self.resolution[1]}",
                    codec=self.codec
                )
        
        except Exception as e:
            print(f"Warning: Could not extract metadata: {e}")
            # Create default metadata
            self.metadata = self.metadata_handler.create_default_metadata(
                frame_rate=self.frame_rate,
                resolution=f"{self.resolution[0]}x{self.resolution[1]}",
                codec=self.codec
            )
    
    def _extract_metadata_stream(self):
        """Extract metadata stream from file"""
        try:
            # Use FFmpeg to extract metadata stream
            temp_metadata_path = tempfile.NamedTemporaryFile(
                suffix='.json',
                delete=False
            ).name
            
            cmd = [
                'ffmpeg',
                '-i', str(self.input_path),
                '-map', '0:s',  # Select subtitle stream
                '-c', 'copy',
                '-f', 'json',
                '-y',
                temp_metadata_path
            ]
            
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Read metadata
            with open(temp_metadata_path, 'r') as f:
                metadata_json = f.read()
            
            # Parse metadata
            self.metadata = self.metadata_handler.from_json(metadata_json)
            
            # Clean up
            os.remove(temp_metadata_path)
        
        except Exception as e:
            print(f"Warning: Could not extract metadata stream: {e}")
    
    def read_frame(self) -> Optional[np.ndarray]:
        """
        Read next frame from MAGI file
        
        Returns:
            Frame as numpy array, or None if end of file
        """
        if not self.is_open:
            self.open()
        
        ret, frame = self.video_capture.read()
        
        if ret:
            self.current_frame_number += 1
            return frame
        else:
            return None
    
    def read_stereo_frame(self) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Read next stereo frame pair (left and right eye)
        
        Returns:
            Tuple of (left_frame, right_frame), or None if end of file
        """
        # Read left eye frame
        left_frame = self.read_frame()
        if left_frame is None:
            return None
        
        # Read right eye frame
        right_frame = self.read_frame()
        if right_frame is None:
            return None
        
        return (left_frame, right_frame)
    
    def frames(self) -> Iterator[np.ndarray]:
        """
        Iterator over all frames
        
        Yields:
            Frames as numpy arrays
        """
        if not self.is_open:
            self.open()
        
        while True:
            frame = self.read_frame()
            if frame is None:
                break
            yield frame
    
    def stereo_frames(self) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        """
        Iterator over all stereo frame pairs
        
        Yields:
            Tuples of (left_frame, right_frame)
        """
        if not self.is_open:
            self.open()
        
        while True:
            stereo_frame = self.read_stereo_frame()
            if stereo_frame is None:
                break
            yield stereo_frame
    
    def seek(self, frame_number: int):
        """
        Seek to specific frame
        
        Args:
            frame_number: Frame number to seek to
        """
        if not self.is_open:
            self.open()
        
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        self.current_frame_number = frame_number
    
    def get_frame_at(self, frame_number: int) -> Optional[np.ndarray]:
        """
        Get frame at specific position
        
        Args:
            frame_number: Frame number
            
        Returns:
            Frame as numpy array, or None if invalid
        """
        self.seek(frame_number)
        return self.read_frame()
    
    def get_stereo_frame_at(self, frame_number: int) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Get stereo frame pair at specific position
        
        Args:
            frame_number: Frame number (left eye frame)
            
        Returns:
            Tuple of (left_frame, right_frame), or None if invalid
        """
        self.seek(frame_number)
        return self.read_stereo_frame()
    
    def close(self):
        """Close MAGI file"""
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        
        self.is_open = False
    
    def get_metadata(self) -> Optional[MAGIMetadata]:
        """
        Get MAGI metadata
        
        Returns:
            MAGIMetadata object, or None if not available
        """
        if not self.is_open:
            self.open()
        
        return self.metadata
    
    def get_frame_count(self) -> int:
        """Get total number of frames"""
        if not self.is_open:
            self.open()
        
        return self.total_frames
    
    def get_current_frame_number(self) -> int:
        """Get current frame number"""
        return self.current_frame_number
    
    def get_frame_rate(self) -> int:
        """Get frame rate"""
        if not self.is_open:
            self.open()
        
        return self.frame_rate
    
    def get_resolution(self) -> Tuple[int, int]:
        """Get resolution"""
        if not self.is_open:
            self.open()
        
        return self.resolution
    
    def get_duration_seconds(self) -> float:
        """Get duration in seconds"""
        if not self.is_open:
            self.open()
        
        return self.total_frames / self.frame_rate if self.frame_rate > 0 else 0.0
    
    def get_codec(self) -> str:
        """Get codec"""
        if not self.is_open:
            self.open()
        
        return self.codec
    
    def is_left_eye_frame(self, frame_number: int) -> bool:
        """
        Check if frame is left eye frame
        
        Args:
            frame_number: Frame number
            
        Returns:
            True if left eye frame, False if right eye
        """
        # In frame-sequential mode, even frames are left eye
        return frame_number % 2 == 0
    
    def get_eye_frame_number(self, frame_number: int) -> int:
        """
        Get eye-specific frame number
        
        Args:
            frame_number: Absolute frame number
            
        Returns:
            Eye-specific frame number (0, 1, 2, ...)
        """
        return frame_number // 2
    
    def __enter__(self):
        """Context manager entry"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def create_magi_reader(input_path: str) -> MAGIReader:
    """
    Create MAGI reader instance
    
    Args:
        input_path: Input file path
        
    Returns:
        MAGIReader instance
    """
    return MAGIReader(input_path)


if __name__ == "__main__":
    # Test MAGI reader
    print("Testing MAGI reader...")
    
    # Create test MAGI file first
    from ..output.magi_writer import create_magi_writer
    
    print("Creating test MAGI file...")
    writer = create_magi_writer(
        output_path="test_input.magi",
        frame_rate=120,
        resolution=(1920, 1080),  # Smaller for testing
        codec="hevc",
        bitrate=10000000
    )
    
    # Write test frames
    for i in range(10):
        left_frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        right_frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        writer.write_stereo_frame(left_frame, right_frame)
    
    writer.close()
    print("Test file created.")
    
    # Read MAGI file
    print("\nReading MAGI file...")
    reader = create_magi_reader("test_input.magi")
    
    # Get metadata
    metadata = reader.get_metadata()
    if metadata:
        print(f"\nMetadata:")
        print(f"  Version: {metadata.version}")
        print(f"  Frame Rate: {metadata.format.frame_rate} fps")
        print(f"  Resolution: {metadata.format.resolution}")
        print(f"  Frame Cadence: {metadata.format.frame_cadence}")
        print(f"  Stereo Mode: {metadata.stereo.mode}")
    
    # Get file info
    print(f"\nFile Info:")
    print(f"  Frame Rate: {reader.get_frame_rate()} fps")
    print(f"  Resolution: {reader.get_resolution()[0]}x{reader.get_resolution()[1]}")
    print(f"  Total Frames: {reader.get_frame_count()}")
    print(f"  Duration: {reader.get_duration_seconds():.2f} seconds")
    print(f"  Codec: {reader.get_codec()}")
    
    # Read frames
    print(f"\nReading frames...")
    frame_count = 0
    for frame in reader.frames():
        frame_count += 1
        if frame_count <= 5:
            print(f"  Frame {frame_count}: {frame.shape}")
    
    print(f"\nTotal frames read: {frame_count}")
    
    # Close reader
    reader.close()
    
    # Clean up test file
    os.remove("test_input.magi")
    print("\nTest completed.")
