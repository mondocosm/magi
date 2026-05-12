"""
MAGI file format metadata handling
Manages MAGI-specific metadata for .magi files
"""

import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum


class MAGIVersion(Enum):
    """MAGI format version"""
    V1_0 = "1.0"
    V1_1 = "1.1"
    V2_0 = "2.0"


class FrameCadence(Enum):
    """Frame cadence patterns"""
    ALTERNATING = "alternating"  # L-R-L-R pattern
    SEQUENTIAL = "sequential"    # L-L-R-R pattern
    CUSTOM = "custom"            # Custom pattern


class StereoMode(Enum):
    """Stereo mode types"""
    FRAME_SEQUENTIAL = "frame-sequential"
    DUAL_STREAM = "dual-stream"
    SIDE_BY_SIDE = "side-by-side"
    TOP_BOTTOM = "top-bottom"


class DisplayType(Enum):
    """Display types"""
    PROJECTOR_3D = "3d-projector"
    VR_HEADSET = "vr-headset"
    TV_3D = "3d-tv"
    CUSTOM = "custom"


@dataclass
class MAGIFormat:
    """MAGI format specifications"""
    frame_rate: int = 120
    resolution: str = "3840x2160"
    eye_separation: int = 180
    frame_cadence: str = "alternating"
    color_space: str = "bt2020"
    color_depth: int = 10
    chroma_subsampling: str = "4:2:0"


@dataclass
class MAGIStereo:
    """MAGI stereo configuration"""
    mode: str = "frame-sequential"
    left_eye_track: int = 1
    right_eye_track: int = 2
    phase_offset: int = 180
    baseline: float = 0.065  # meters


@dataclass
class MAGIDisplay:
    """MAGI display configuration"""
    display_type: str = "3d-projector"
    shutter_glasses: bool = True
    sync_method: str = "hardware"
    refresh_rate: int = 120


@dataclass
class MAGISource:
    """Source information"""
    original_format: str = ""
    original_frame_rate: int = 0
    original_resolution: str = ""
    conversion_method: str = ""
    source_file: str = ""


@dataclass
class MAGIProcessing:
    """Processing information"""
    interpolation_method: str = ""
    upscaling_method: str = ""
    processing_date: str = ""
    processing_time: float = 0.0
    gpu_used: str = ""


@dataclass
class MAGIQuality:
    """Quality settings"""
    bitrate: int = 50000000
    codec: str = "hevc"
    profile: str = "main10"
    level: str = "5.1"


@dataclass
class MAGIMetadata:
    """Complete MAGI metadata"""
    version: str = "1.0"
    format: MAGIFormat = field(default_factory=MAGIFormat)
    stereo: MAGIStereo = field(default_factory=MAGIStereo)
    display: MAGIDisplay = field(default_factory=MAGIDisplay)
    source: Optional[MAGISource] = None
    processing: Optional[MAGIProcessing] = None
    quality: Optional[MAGIQuality] = None
    custom_data: Dict[str, Any] = field(default_factory=dict)


class MAGIMetadataHandler:
    """Handle MAGI metadata operations"""
    
    def __init__(self):
        self.metadata = MAGIMetadata()
    
    def create_default_metadata(self, 
                               frame_rate: int = 120,
                               resolution: str = "3840x2160",
                               codec: str = "hevc") -> MAGIMetadata:
        """
        Create default MAGI metadata
        
        Args:
            frame_rate: Target frame rate
            resolution: Target resolution
            codec: Video codec
            
        Returns:
            MAGIMetadata object
        """
        self.metadata = MAGIMetadata(
            version="1.0",
            format=MAGIFormat(
                frame_rate=frame_rate,
                resolution=resolution,
                eye_separation=180,
                frame_cadence="alternating"
            ),
            stereo=MAGIStereo(
                mode="frame-sequential",
                left_eye_track=1,
                right_eye_track=2,
                phase_offset=180
            ),
            display=MAGIDisplay(
                display_type="3d-projector",
                shutter_glasses=True,
                sync_method="hardware",
                refresh_rate=frame_rate
            ),
            quality=MAGIQuality(
                codec=codec,
                profile="main10",
                level="5.1"
            )
        )
        
        return self.metadata
    
    def to_xml(self) -> str:
        """
        Convert metadata to XML string
        
        Returns:
            XML string representation
        """
        root = ET.Element("MAGI")
        
        # Version
        version = ET.SubElement(root, "Version")
        version.text = self.metadata.version
        
        # Format
        format_elem = ET.SubElement(root, "Format")
        self._add_xml_element(format_elem, "FrameRate", str(self.metadata.format.frame_rate))
        self._add_xml_element(format_elem, "Resolution", self.metadata.format.resolution)
        self._add_xml_element(format_elem, "EyeSeparation", str(self.metadata.format.eye_separation))
        self._add_xml_element(format_elem, "FrameCadence", self.metadata.format.frame_cadence)
        self._add_xml_element(format_elem, "ColorSpace", self.metadata.format.color_space)
        self._add_xml_element(format_elem, "ColorDepth", str(self.metadata.format.color_depth))
        self._add_xml_element(format_elem, "ChromaSubsampling", self.metadata.format.chroma_subsampling)
        
        # Stereo
        stereo_elem = ET.SubElement(root, "Stereo")
        self._add_xml_element(stereo_elem, "Mode", self.metadata.stereo.mode)
        self._add_xml_element(stereo_elem, "LeftEyeTrack", str(self.metadata.stereo.left_eye_track))
        self._add_xml_element(stereo_elem, "RightEyeTrack", str(self.metadata.stereo.right_eye_track))
        self._add_xml_element(stereo_elem, "PhaseOffset", str(self.metadata.stereo.phase_offset))
        self._add_xml_element(stereo_elem, "Baseline", str(self.metadata.stereo.baseline))
        
        # Display
        display_elem = ET.SubElement(root, "Display")
        self._add_xml_element(display_elem, "Type", self.metadata.display.display_type)
        self._add_xml_element(display_elem, "ShutterGlasses", str(self.metadata.display.shutter_glasses).lower())
        self._add_xml_element(display_elem, "SyncMethod", self.metadata.display.sync_method)
        self._add_xml_element(display_elem, "RefreshRate", str(self.metadata.display.refresh_rate))
        
        # Source (optional)
        if self.metadata.source:
            source_elem = ET.SubElement(root, "Source")
            self._add_xml_element(source_elem, "OriginalFormat", self.metadata.source.original_format)
            self._add_xml_element(source_elem, "OriginalFrameRate", str(self.metadata.source.original_frame_rate))
            self._add_xml_element(source_elem, "OriginalResolution", self.metadata.source.original_resolution)
            self._add_xml_element(source_elem, "ConversionMethod", self.metadata.source.conversion_method)
            self._add_xml_element(source_elem, "SourceFile", self.metadata.source.source_file)
        
        # Processing (optional)
        if self.metadata.processing:
            processing_elem = ET.SubElement(root, "Processing")
            self._add_xml_element(processing_elem, "InterpolationMethod", self.metadata.processing.interpolation_method)
            self._add_xml_element(processing_elem, "UpscalingMethod", self.metadata.processing.upscaling_method)
            self._add_xml_element(processing_elem, "ProcessingDate", self.metadata.processing.processing_date)
            self._add_xml_element(processing_elem, "ProcessingTime", str(self.metadata.processing.processing_time))
            self._add_xml_element(processing_elem, "GPUUsed", self.metadata.processing.gpu_used)
        
        # Quality (optional)
        if self.metadata.quality:
            quality_elem = ET.SubElement(root, "Quality")
            self._add_xml_element(quality_elem, "Bitrate", str(self.metadata.quality.bitrate))
            self._add_xml_element(quality_elem, "Codec", self.metadata.quality.codec)
            self._add_xml_element(quality_elem, "Profile", self.metadata.quality.profile)
            self._add_xml_element(quality_elem, "Level", self.metadata.quality.level)
        
        # Custom data (optional)
        if self.metadata.custom_data:
            custom_elem = ET.SubElement(root, "CustomData")
            for key, value in self.metadata.custom_data.items():
                self._add_xml_element(custom_elem, key, str(value))
        
        # Convert to string
        return ET.tostring(root, encoding='unicode', method='xml')
    
    def _add_xml_element(self, parent: ET.Element, tag: str, text: str):
        """Add XML element with text"""
        elem = ET.SubElement(parent, tag)
        elem.text = text
    
    def from_xml(self, xml_string: str) -> MAGIMetadata:
        """
        Parse metadata from XML string
        
        Args:
            xml_string: XML string
            
        Returns:
            MAGIMetadata object
        """
        root = ET.fromstring(xml_string)
        
        # Version
        version_elem = root.find("Version")
        if version_elem is not None:
            self.metadata.version = version_elem.text
        
        # Format
        format_elem = root.find("Format")
        if format_elem is not None:
            self.metadata.format = MAGIFormat(
                frame_rate=int(self._get_xml_text(format_elem, "FrameRate", 120)),
                resolution=self._get_xml_text(format_elem, "Resolution", "3840x2160"),
                eye_separation=int(self._get_xml_text(format_elem, "EyeSeparation", 180)),
                frame_cadence=self._get_xml_text(format_elem, "FrameCadence", "alternating"),
                color_space=self._get_xml_text(format_elem, "ColorSpace", "bt2020"),
                color_depth=int(self._get_xml_text(format_elem, "ColorDepth", 10)),
                chroma_subsampling=self._get_xml_text(format_elem, "ChromaSubsampling", "4:2:0")
            )
        
        # Stereo
        stereo_elem = root.find("Stereo")
        if stereo_elem is not None:
            self.metadata.stereo = MAGIStereo(
                mode=self._get_xml_text(stereo_elem, "Mode", "frame-sequential"),
                left_eye_track=int(self._get_xml_text(stereo_elem, "LeftEyeTrack", 1)),
                right_eye_track=int(self._get_xml_text(stereo_elem, "RightEyeTrack", 2)),
                phase_offset=int(self._get_xml_text(stereo_elem, "PhaseOffset", 180)),
                baseline=float(self._get_xml_text(stereo_elem, "Baseline", 0.065))
            )
        
        # Display
        display_elem = root.find("Display")
        if display_elem is not None:
            self.metadata.display = MAGIDisplay(
                display_type=self._get_xml_text(display_elem, "Type", "3d-projector"),
                shutter_glasses=self._get_xml_text(display_elem, "ShutterGlasses", "true").lower() == "true",
                sync_method=self._get_xml_text(display_elem, "SyncMethod", "hardware"),
                refresh_rate=int(self._get_xml_text(display_elem, "RefreshRate", 120))
            )
        
        # Source (optional)
        source_elem = root.find("Source")
        if source_elem is not None:
            self.metadata.source = MAGISource(
                original_format=self._get_xml_text(source_elem, "OriginalFormat", ""),
                original_frame_rate=int(self._get_xml_text(source_elem, "OriginalFrameRate", 0)),
                original_resolution=self._get_xml_text(source_elem, "OriginalResolution", ""),
                conversion_method=self._get_xml_text(source_elem, "ConversionMethod", ""),
                source_file=self._get_xml_text(source_elem, "SourceFile", "")
            )
        
        # Processing (optional)
        processing_elem = root.find("Processing")
        if processing_elem is not None:
            self.metadata.processing = MAGIProcessing(
                interpolation_method=self._get_xml_text(processing_elem, "InterpolationMethod", ""),
                upscaling_method=self._get_xml_text(processing_elem, "UpscalingMethod", ""),
                processing_date=self._get_xml_text(processing_elem, "ProcessingDate", ""),
                processing_time=float(self._get_xml_text(processing_elem, "ProcessingTime", 0.0)),
                gpu_used=self._get_xml_text(processing_elem, "GPUUsed", "")
            )
        
        # Quality (optional)
        quality_elem = root.find("Quality")
        if quality_elem is not None:
            self.metadata.quality = MAGIQuality(
                bitrate=int(self._get_xml_text(quality_elem, "Bitrate", 50000000)),
                codec=self._get_xml_text(quality_elem, "Codec", "hevc"),
                profile=self._get_xml_text(quality_elem, "Profile", "main10"),
                level=self._get_xml_text(quality_elem, "Level", "5.1")
            )
        
        # Custom data (optional)
        custom_elem = root.find("CustomData")
        if custom_elem is not None:
            self.metadata.custom_data = {}
            for child in custom_elem:
                self.metadata.custom_data[child.tag] = child.text
        
        return self.metadata
    
    def _get_xml_text(self, parent: ET.Element, tag: str, default: str = "") -> str:
        """Get text from XML element with default"""
        elem = parent.find(tag)
        return elem.text if elem is not None and elem.text else default
    
    def to_json(self) -> str:
        """
        Convert metadata to JSON string
        
        Returns:
            JSON string representation
        """
        data = {
            "version": self.metadata.version,
            "format": asdict(self.metadata.format),
            "stereo": asdict(self.metadata.stereo),
            "display": asdict(self.metadata.display)
        }
        
        if self.metadata.source:
            data["source"] = asdict(self.metadata.source)
        
        if self.metadata.processing:
            data["processing"] = asdict(self.metadata.processing)
        
        if self.metadata.quality:
            data["quality"] = asdict(self.metadata.quality)
        
        if self.metadata.custom_data:
            data["custom_data"] = self.metadata.custom_data
        
        return json.dumps(data, indent=2)
    
    def from_json(self, json_string: str) -> MAGIMetadata:
        """
        Parse metadata from JSON string
        
        Args:
            json_string: JSON string
            
        Returns:
            MAGIMetadata object
        """
        data = json.loads(json_string)
        
        self.metadata.version = data.get("version", "1.0")
        self.metadata.format = MAGIFormat(**data.get("format", {}))
        self.metadata.stereo = MAGIStereo(**data.get("stereo", {}))
        self.metadata.display = MAGIDisplay(**data.get("display", {}))
        
        if "source" in data:
            self.metadata.source = MAGISource(**data["source"])
        
        if "processing" in data:
            self.metadata.processing = MAGIProcessing(**data["processing"])
        
        if "quality" in data:
            self.metadata.quality = MAGIQuality(**data["quality"])
        
        if "custom_data" in data:
            self.metadata.custom_data = data["custom_data"]
        
        return self.metadata
    
    def validate(self) -> bool:
        """
        Validate metadata
        
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if not self.metadata.version:
            return False
        
        if self.metadata.format.frame_rate <= 0:
            return False
        
        if not self.metadata.format.resolution:
            return False
        
        if self.metadata.stereo.left_eye_track <= 0:
            return False
        
        if self.metadata.stereo.right_eye_track <= 0:
            return False
        
        # Validate frame cadence
        valid_cadences = ["alternating", "sequential", "custom"]
        if self.metadata.format.frame_cadence not in valid_cadences:
            return False
        
        # Validate stereo mode
        valid_modes = ["frame-sequential", "dual-stream", "side-by-side", "top-bottom"]
        if self.metadata.stereo.mode not in valid_modes:
            return False
        
        return True
    
    def get_frame_duration_ms(self) -> float:
        """
        Get frame duration in milliseconds
        
        Returns:
            Frame duration in ms
        """
        return 1000.0 / self.metadata.format.frame_rate
    
    def get_eye_duration_ms(self) -> float:
        """
        Get eye duration in milliseconds (time between same eye frames)
        
        Returns:
            Eye duration in ms
        """
        return self.get_frame_duration_ms() * 2
    
    def get_phase_offset_ms(self) -> float:
        """
        Get phase offset in milliseconds
        
        Returns:
            Phase offset in ms
        """
        return self.get_frame_duration_ms()


def create_metadata_handler() -> MAGIMetadataHandler:
    """
    Create MAGI metadata handler instance
    
    Returns:
        MAGIMetadataHandler instance
    """
    return MAGIMetadataHandler()


if __name__ == "__main__":
    # Test metadata handler
    print("Testing MAGI metadata handler...")
    
    handler = create_metadata_handler()
    
    # Create default metadata
    metadata = handler.create_default_metadata(
        frame_rate=120,
        resolution="3840x2160",
        codec="hevc"
    )
    
    print("Default metadata created:")
    print(f"  Version: {metadata.version}")
    print(f"  Frame Rate: {metadata.format.frame_rate} fps")
    print(f"  Resolution: {metadata.format.resolution}")
    print(f"  Frame Cadence: {metadata.format.frame_cadence}")
    print(f"  Stereo Mode: {metadata.stereo.mode}")
    print(f"  Display Type: {metadata.display.display_type}")
    
    # Convert to XML
    xml_string = handler.to_xml()
    print("\nXML representation:")
    print(xml_string)
    
    # Convert to JSON
    json_string = handler.to_json()
    print("\nJSON representation:")
    print(json_string)
    
    # Validate
    is_valid = handler.validate()
    print(f"\nValidation: {'Valid' if is_valid else 'Invalid'}")
    
    # Test parsing
    new_handler = create_metadata_handler()
    new_handler.from_xml(xml_string)
    print("\nParsed from XML:")
    print(f"  Version: {new_handler.metadata.version}")
    print(f"  Frame Rate: {new_handler.metadata.format.frame_rate} fps")
