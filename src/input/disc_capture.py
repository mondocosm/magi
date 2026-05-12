"""
DVD/Blu-ray Disc Capture Module

This module provides real-time capture from DVD and Blu-ray discs
with buffering for near real-time MAGI conversion.
"""

import cv2
import numpy as np
import threading
import queue
import time
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import subprocess
import os


class DiscType(Enum):
    """Disc type enumeration"""
    DVD = "dvd"
    BLURAY = "bluray"
    UNKNOWN = "unknown"


@dataclass
class DiscInfo:
    """Disc information"""
    disc_type: DiscType
    title_count: int
    current_title: int
    duration: float  # in seconds
    chapters: int
    audio_tracks: int
    subtitle_tracks: int
    resolution: Tuple[int, int]
    frame_rate: float
    aspect_ratio: str


@dataclass
class BufferStats:
    """Buffer statistics"""
    buffer_size: int = 0
    buffer_capacity: int = 0
    buffer_usage: float = 0.0  # percentage
    frames_dropped: int = 0
    frames_processed: int = 0
    avg_latency: float = 0.0  # in seconds


class DiscCapture:
    """
    DVD/Blu-ray disc capture with real-time streaming and buffering
    
    Supports:
    - DVD discs (MPEG-2)
    - Blu-ray discs (H.264, H.265)
    - Real-time streaming with buffering
    - Chapter navigation
    - Audio/subtitle track selection
    """
    
    def __init__(
        self,
        device_path: str = "/dev/dvd",
        buffer_size: int = 60,  # seconds of buffering
        processing_mode: str = "realtime",  # realtime, balanced, quality
        gpu_acceleration: bool = True
    ):
        """
        Initialize disc capture
        
        Args:
            device_path: Path to DVD/Blu-ray device
            buffer_size: Buffer size in seconds
            processing_mode: Processing mode (realtime, balanced, quality)
            gpu_acceleration: Enable GPU acceleration
        """
        self.device_path = device_path
        self.buffer_size = buffer_size
        self.processing_mode = processing_mode
        self.gpu_acceleration = gpu_acceleration
        
        # Disc information
        self.disc_info: Optional[DiscInfo] = None
        self.current_title = 1
        self.current_chapter = 1
        
        # Capture thread
        self.capture_thread: Optional[threading.Thread] = None
        self.is_capturing = False
        self.stop_event = threading.Event()
        
        # Frame buffer
        self.frame_queue: queue.Queue = queue.Queue(maxsize=buffer_size * 60)  # 60 fps
        self.buffer_stats = BufferStats(buffer_capacity=buffer_size * 60)
        
        # Statistics
        self.start_time: Optional[float] = None
        self.frames_captured = 0
        self.frames_dropped = 0
        self.total_latency = 0.0
        
        # FFmpeg process
        self.ffmpeg_process: Optional[subprocess.Popen] = None
        
    def detect_disc(self) -> Optional[DiscInfo]:
        """
        Detect disc type and information
        
        Returns:
            DiscInfo object or None if no disc detected
        """
        try:
            # Check if device exists
            if not os.path.exists(self.device_path):
                print(f"Device not found: {self.device_path}")
                return None
            
            # Try to detect disc type using FFmpeg
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_format",
                "-show_streams",
                "-of", "json",
                self.device_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                print(f"Failed to probe disc: {result.stderr}")
                return None
            
            # Parse output to determine disc type
            output = result.stdout
            
            if "mpeg2video" in output:
                disc_type = DiscType.DVD
            elif "h264" in output or "hevc" in output:
                disc_type = DiscType.BLURAY
            else:
                disc_type = DiscType.UNKNOWN
            
            # Extract disc information
            # This is a simplified version - in production, you'd parse the JSON properly
            disc_info = DiscInfo(
                disc_type=disc_type,
                title_count=1,  # Would need to parse properly
                current_title=1,
                duration=0.0,  # Would need to parse properly
                chapters=1,  # Would need to parse properly
                audio_tracks=1,  # Would need to parse properly
                subtitle_tracks=0,  # Would need to parse properly
                resolution=(1920, 1080),  # Default
                frame_rate=24.0,  # Default
                aspect_ratio="16:9"
            )
            
            self.disc_info = disc_info
            return disc_info
            
        except Exception as e:
            print(f"Error detecting disc: {e}")
            return None
    
    def start_capture(
        self,
        title: int = 1,
        chapter: int = 1,
        audio_track: int = 1,
        subtitle_track: int = 0
    ) -> bool:
        """
        Start capturing from disc
        
        Args:
            title: Title number to capture
            chapter: Chapter number to start from
            audio_track: Audio track number
            subtitle_track: Subtitle track number
            
        Returns:
            True if capture started successfully
        """
        if self.is_capturing:
            print("Already capturing")
            return False
        
        # Detect disc if not already done
        if self.disc_info is None:
            self.disc_info = self.detect_disc()
            if self.disc_info is None:
                print("No disc detected")
                return False
        
        self.current_title = title
        self.current_chapter = chapter
        
        # Build FFmpeg command for disc capture
        cmd = self._build_ffmpeg_command(title, chapter, audio_track, subtitle_track)
        
        try:
            # Start FFmpeg process
            self.ffmpeg_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=10**8
            )
            
            # Start capture thread
            self.is_capturing = True
            self.stop_event.clear()
            self.start_time = time.time()
            self.frames_captured = 0
            self.frames_dropped = 0
            self.total_latency = 0.0
            
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            print(f"Started capturing from {self.disc_info.disc_type.value} disc")
            return True
            
        except Exception as e:
            print(f"Error starting capture: {e}")
            return False
    
    def _build_ffmpeg_command(
        self,
        title: int,
        chapter: int,
        audio_track: int,
        subtitle_track: int
    ) -> list:
        """
        Build FFmpeg command for disc capture
        
        Args:
            title: Title number
            chapter: Chapter number
            audio_track: Audio track
            subtitle_track: Subtitle track
            
        Returns:
            FFmpeg command as list
        """
        cmd = [
            "ffmpeg",
            "-i", self.device_path,
            "-map", f"0:v:{title-1}",  # Video stream
            "-map", f"0:a:{audio_track-1}",  # Audio stream
        ]
        
        # Add subtitle if specified
        if subtitle_track > 0:
            cmd.extend(["-map", f"0:s:{subtitle_track-1}"])
        
        # Output format (raw video for processing)
        cmd.extend([
            "-f", "rawvideo",
            "-pix_fmt", "bgr24",  # OpenCV format
            "-vsync", "0",  # No frame rate conversion
            "-threads", "4",  # Multi-threading
            "-"
        ])
        
        return cmd
    
    def _capture_loop(self):
        """
        Capture loop running in separate thread
        """
        frame_size = 1920 * 1080 * 3  # BGR24 format
        
        while not self.stop_event.is_set():
            try:
                # Read frame from FFmpeg
                frame_data = self.ffmpeg_process.stdout.read(frame_size)
                
                if len(frame_data) != frame_size:
                    # End of stream or error
                    break
                
                # Convert to numpy array
                frame = np.frombuffer(frame_data, dtype=np.uint8).reshape((1080, 1920, 3))
                
                # Add timestamp
                timestamp = time.time() - self.start_time
                
                # Try to add to buffer
                try:
                    self.frame_queue.put((frame, timestamp), timeout=0.01)
                    self.frames_captured += 1
                except queue.Full:
                    # Buffer full, drop frame
                    self.frames_dropped += 1
                    print(f"Buffer full, dropping frame {self.frames_dropped}")
                
                # Update buffer stats
                self._update_buffer_stats()
                
            except Exception as e:
                print(f"Error in capture loop: {e}")
                break
        
        self.is_capturing = False
        print("Capture loop ended")
    
    def _update_buffer_stats(self):
        """Update buffer statistics"""
        self.buffer_stats.buffer_size = self.frame_queue.qsize()
        self.buffer_stats.buffer_usage = (
            self.buffer_stats.buffer_size / self.buffer_stats.buffer_capacity * 100
        )
        self.buffer_stats.frames_dropped = self.frames_dropped
        self.buffer_stats.frames_processed = self.frames_captured
        
        if self.frames_captured > 0:
            self.buffer_stats.avg_latency = self.total_latency / self.frames_captured
    
    def get_frame(self, timeout: float = 1.0) -> Optional[Tuple[np.ndarray, float]]:
        """
        Get next frame from buffer
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (frame, timestamp) or None if timeout
        """
        try:
            frame, timestamp = self.frame_queue.get(timeout=timeout)
            
            # Calculate latency
            latency = time.time() - timestamp
            self.total_latency += latency
            
            return frame, timestamp
            
        except queue.Empty:
            return None
    
    def stop_capture(self):
        """Stop capturing"""
        if not self.is_capturing:
            return
        
        self.stop_event.set()
        self.is_capturing = False
        
        # Wait for capture thread to end
        if self.capture_thread:
            self.capture_thread.join(timeout=5.0)
        
        # Terminate FFmpeg process
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            try:
                self.ffmpeg_process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                self.ffmpeg_process.kill()
        
        print("Capture stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get capture statistics
        
        Returns:
            Dictionary with statistics
        """
        elapsed_time = 0.0
        if self.start_time:
            elapsed_time = time.time() - self.start_time
        
        fps = 0.0
        if elapsed_time > 0:
            fps = self.frames_captured / elapsed_time
        
        return {
            "is_capturing": self.is_capturing,
            "disc_type": self.disc_info.disc_type.value if self.disc_info else "unknown",
            "current_title": self.current_title,
            "current_chapter": self.current_chapter,
            "frames_captured": self.frames_captured,
            "frames_dropped": self.frames_dropped,
            "fps": fps,
            "elapsed_time": elapsed_time,
            "buffer_size": self.buffer_stats.buffer_size,
            "buffer_capacity": self.buffer_stats.buffer_capacity,
            "buffer_usage": self.buffer_stats.buffer_usage,
            "avg_latency": self.buffer_stats.avg_latency
        }
    
    def set_chapter(self, chapter: int):
        """
        Jump to specific chapter
        
        Args:
            chapter: Chapter number
        """
        if not self.is_capturing:
            print("Not capturing")
            return
        
        # This would require restarting FFmpeg with seek
        # For now, just update the chapter number
        self.current_chapter = chapter
        print(f"Chapter changed to {chapter} (requires restart)")
    
    def set_title(self, title: int):
        """
        Switch to different title
        
        Args:
            title: Title number
        """
        if not self.is_capturing:
            print("Not capturing")
            return
        
        # This would require restarting FFmpeg
        # For now, just update the title number
        self.current_title = title
        print(f"Title changed to {title} (requires restart)")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop_capture()


class DiscToMAGIPipeline:
    """
    Real-time disc to MAGI conversion pipeline with buffering
    
    This pipeline captures from DVD/Blu-ray discs and converts to MAGI format
    in near real-time with buffering to handle processing delays.
    """
    
    def __init__(
        self,
        device_path: str = "/dev/dvd",
        buffer_size: int = 60,  # seconds of buffering
        processing_mode: str = "realtime",
        output_mode: str = "stream",  # stream, file, both
        output_file: Optional[str] = None
    ):
        """
        Initialize disc to MAGI pipeline
        
        Args:
            device_path: Path to DVD/Blu-ray device
            buffer_size: Buffer size in seconds
            processing_mode: Processing mode (realtime, balanced, quality)
            output_mode: Output mode (stream, file, both)
            output_file: Output file path (if file mode)
        """
        self.device_path = device_path
        self.buffer_size = buffer_size
        self.processing_mode = processing_mode
        self.output_mode = output_mode
        self.output_file = output_file
        
        # Disc capture
        self.disc_capture = DiscCapture(
            device_path=device_path,
            buffer_size=buffer_size,
            processing_mode=processing_mode
        )
        
        # Processing thread
        self.processing_thread: Optional[threading.Thread] = None
        self.is_processing = False
        self.stop_event = threading.Event()
        
        # Statistics
        self.processing_stats = {
            "frames_processed": 0,
            "frames_output": 0,
            "avg_processing_time": 0.0,
            "total_processing_time": 0.0
        }
    
    def start(self, title: int = 1, chapter: int = 1) -> bool:
        """
        Start disc to MAGI conversion
        
        Args:
            title: Title number
            chapter: Chapter number
            
        Returns:
            True if started successfully
        """
        # Start disc capture
        if not self.disc_capture.start_capture(title=title, chapter=chapter):
            print("Failed to start disc capture")
            return False
        
        # Start processing thread
        self.is_processing = True
        self.stop_event.clear()
        
        self.processing_thread = threading.Thread(
            target=self._processing_loop,
            daemon=True
        )
        self.processing_thread.start()
        
        print("Started disc to MAGI conversion")
        return True
    
    def _processing_loop(self):
        """
        Processing loop running in separate thread
        """
        while not self.stop_event.is_set():
            # Get frame from buffer
            frame_data = self.disc_capture.get_frame(timeout=1.0)
            
            if frame_data is None:
                continue
            
            frame, timestamp = frame_data
            
            # Process frame (this would be the actual MAGI conversion)
            start_time = time.time()
            
            # TODO: Implement actual MAGI conversion pipeline
            # 1. 2D to 3D conversion (if needed)
            # 2. Frame interpolation (to 120 fps)
            # 3. Upscaling (to 4K per eye)
            # 4. Frame cadence (left/right eye alternating)
            # 5. MAGI encoding
            
            processed_frame = frame  # Placeholder
            
            processing_time = time.time() - start_time
            
            # Update statistics
            self.processing_stats["frames_processed"] += 1
            self.processing_stats["total_processing_time"] += processing_time
            self.processing_stats["avg_processing_time"] = (
                self.processing_stats["total_processing_time"] /
                self.processing_stats["frames_processed"]
            )
            
            # Output frame
            if self.output_mode in ["stream", "both"]:
                # Stream to display
                self._output_frame(processed_frame)
                self.processing_stats["frames_output"] += 1
            
            if self.output_mode in ["file", "both"] and self.output_file:
                # Write to file
                self._write_frame(processed_frame)
    
    def _output_frame(self, frame: np.ndarray):
        """
        Output frame to display
        
        Args:
            frame: Processed frame
        """
        # TODO: Implement frame output to display
        # This would send the frame to a MAGI-compatible display
        pass
    
    def _write_frame(self, frame: np.ndarray):
        """
        Write frame to output file
        
        Args:
            frame: Processed frame
        """
        # TODO: Implement frame writing to MAGI file
        # This would write the frame to a .magi file
        pass
    
    def stop(self):
        """Stop disc to MAGI conversion"""
        self.stop_event.set()
        self.is_processing = False
        
        # Stop disc capture
        self.disc_capture.stop_capture()
        
        # Wait for processing thread to end
        if self.processing_thread:
            self.processing_thread.join(timeout=5.0)
        
        print("Disc to MAGI conversion stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get pipeline statistics
        
        Returns:
            Dictionary with statistics
        """
        disc_stats = self.disc_capture.get_stats()
        
        return {
            **disc_stats,
            "processing_stats": self.processing_stats,
            "output_mode": self.output_mode,
            "output_file": self.output_file
        }


# Example usage
if __name__ == "__main__":
    # Create disc to MAGI pipeline
    pipeline = DiscToMAGIPipeline(
        device_path="/dev/dvd",
        buffer_size=60,
        processing_mode="realtime",
        output_mode="stream"
    )
    
    # Detect disc
    disc_info = pipeline.disc_capture.detect_disc()
    if disc_info:
        print(f"Detected {disc_info.disc_type.value} disc")
        print(f"Titles: {disc_info.title_count}")
        print(f"Duration: {disc_info.duration} seconds")
        
        # Start conversion
        if pipeline.start(title=1, chapter=1):
            print("Conversion started")
            
            # Run for 10 seconds
            time.sleep(10)
            
            # Get statistics
            stats = pipeline.get_stats()
            print(f"Statistics: {stats}")
            
            # Stop conversion
            pipeline.stop()
    else:
        print("No disc detected")
