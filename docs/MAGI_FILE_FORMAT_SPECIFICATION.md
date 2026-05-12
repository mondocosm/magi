# MAGI File Format Specification v1.0

## Executive Summary

The MAGI file format (.magi) is a standardized container format designed specifically for storing and delivering MAGI (High-Frame-Rate 3D Cinema) content as invented by Douglas Trumbull. This specification defines a complete standard for packaging 4K 3D video at 120fps with proper frame cadence, HEVC H.265 encoding, and comprehensive metadata for playback on MAGI-compatible projectors and displays.

**Version:** 1.0  
**Status:** Final  
**Last Updated:** 2024-01-15  
**License:** Open and free to use

---

## Table of Contents

1. [Overview](#overview)
2. [File Extension and MIME Type](#file-extension-and-mime-type)
3. [Format Structure](#format-structure)
4. [HEVC H.265 Codec Specification](#hevc-h265-codec-specification)
5. [MAGI-Specific Metadata](#magi-specific-metadata)
6. [Video Track Configuration](#video-track-configuration)
7. [Frame Cadence Specification](#frame-cadence-specification)
8. [Audio Specifications](#audio-specifications)
9. [File Size and Bitrate](#file-size-and-bitrate)
10. [Playback Requirements](#playback-requirements)
11. [Compatibility](#compatibility)
12. [Implementation Guide](#implementation-guide)
13. [Reference Implementation](#reference-implementation)
14. [Future Enhancements](#future-enhancements)

---

## Overview

### Purpose

The MAGI file format provides a standardized way to:
- Store 4K 3D video at 120fps (60fps per eye)
- Maintain frame-accurate synchronization for 3D shutter glasses
- Preserve high-quality video using HEVC H.265 compression
- Include comprehensive metadata for proper playback
- Support both streaming and archival use cases

### Key Features

- **High Frame Rate:** 120fps native (60fps per eye alternating)
- **High Resolution:** 4K (3840×2160) per eye
- **3D Format:** Frame-sequential with 180° phase offset
- **Codec:** HEVC H.265 Main 10 Profile
- **Container:** Matroska (MKV) with MAGI extensions
- **Metadata:** XML/JSON embedded metadata
- **Compatibility:** Backward compatible with standard MKV players

### Use Cases

1. **Cinema:** Theatrical 3D projection
2. **Home Theater:** 3D home entertainment
3. **VR/AR:** Virtual and augmented reality content
4. **Archival:** Long-term storage of 3D content
5. **Streaming:** Real-time 3D video delivery
6. **Post-Production:** Professional video editing and grading

---

## File Extension and MIME Type

### File Extensions

- **Primary:** `.magi`
- **Alternative:** `.magi3d`

### MIME Type

```
application/x-magi
```

### Magic Number

The file begins with the standard EBML header for Matroska files:

```
1A 45 DF A3
```

---

## Format Structure

### Container Format

- **Base Container:** Matroska (MKV)
- **MAGI Version:** 1.0
- **EBML Version:** 1
- **DocType:** `matroska`
- **DocTypeVersion:** 4
- **DocTypeReadVersion:** 2

### File Structure

```
MAGI File (.magi)
├── EBML Header
│   ├── EBML Version
│   ├── DocType
│   └── DocType Version
├── Segment
│   ├── Seek Head (optional)
│   ├── Segment Information
│   │   ├── MAGI Metadata (XML/JSON)
│   │   ├── Video Properties
│   │   ├── Audio Properties
│   │   └── Encoding Settings
│   ├── Tracks
│   │   ├── Video Track 1 (Left Eye)
│   │   │   ├── Codec: HEVC H.265
│   │   │   ├── Resolution: 3840×2160
│   │   │   └── Frame Rate: 120 fps
│   │   ├── Video Track 2 (Right Eye) [optional]
│   │   └── Audio Track(s)
│   ├── Chapters (optional)
│   ├── Tags (optional)
│   ├── Attachments (optional)
│   └── Clusters
│       ├── Cluster 1
│       │   ├── Timecode: 0ms
│       │   ├── Frame 1 (Left Eye)
│       │   ├── Frame 2 (Right Eye)
│       │   └── ...
│       └── Cluster 2
│           └── ...
```

---

## HEVC H.265 Codec Specification

### Video Codec Parameters

#### Primary Codec

- **Codec:** H.265/HEVC (High Efficiency Video Coding)
- **Profile:** Main 10 Profile
- **Level:** 5.1 (for 4K@120fps)
- **Tier:** High

#### Encoding Parameters

```xml
<VideoCodec>
  <Name>hevc</Name>
  <Profile>main10</Profile>
  <Level>5.1</Level>
  <Tier>high</Tier>
  <Bitrate>50000000</Bitrate>
  <MaxBitrate>80000000</MaxBitrate>
  <ColorSpace>bt2020</ColorSpace>
  <ColorDepth>10</ColorDepth>
  <ChromaSubsampling>4:2:0</ChromaSubsampling>
  <TransferFunction>pq</TransferFunction>
  <ColorPrimaries>bt2020</ColorPrimaries>
</VideoCodec>
```

### HEVC Configuration Record

The HEVC decoder configuration record must include:

```
- configurationVersion: 1
- general_profile_space: 0
- general_tier_flag: 1 (High Tier)
- general_profile_idc: 2 (Main 10 Profile)
- general_profile_compatibility_flags: 0x40000000
- general_constraint_indicator_flags: 0x000000000000
- general_level_idc: 153 (Level 5.1)
- min_spatial_segmentation_idc: 0
- parallelismType: 0
- chromaFormat: 1 (4:2:0)
- bitDepthLumaMinus8: 2 (10-bit)
- bitDepthChromaMinus8: 2 (10-bit)
- avgFrameRate: 120
- constantFrameRate: 0
- numTemporalLayers: 1
- temporalIdNested: 1
- lengthSizeMinusOne: 3
- numOfArrays: 2
```

### GOP Structure

#### Recommended GOP Settings

- **GOP Size:** 120 frames (1 second at 120fps)
- **GOP Structure:** IPBBPBBP... (standard)
- **B-Frames:** 3-5 between I-frames
- **Reference Frames:** 4-6
- **Closed GOP:** Yes (for streaming)

#### Frame Types

```
I-Frame: Every 120 frames (1 second)
P-Frame: Every 2-4 frames
B-Frame: Between P-frames
```

### Quantization Parameters

- **I-Frame QP:** 20-25
- **P-Frame QP:** 22-28
- **B-Frame QP:** 24-30
- **Adaptive QP:** Enabled
- **QP Delta:** ±2

### Rate Control

- **Target Bitrate:** 50 Mbps (4K), 30 Mbps (2K)
- **Max Bitrate:** 80 Mbps (4K), 50 Mbps (2K)
- **Buffer Size:** 2 seconds
- **VBV Buffer:** 1000000 bits
- **Rate Control Mode:** CBR (Constant Bitrate)

### Advanced Features

#### Motion Estimation

- **Search Range:** 64 pixels
- **Algorithm:** UMHexagonS
- **Sub-Pixel Motion:** 1/4 pixel
- **Temporal Motion Vectors:** Enabled

#### Transform and Quantization

- **Transform Size:** 4×4 to 32×32
- **Quantization Matrix:** Default
- **Adaptive Transform:** Enabled

#### Loop Filters

- **Deblocking Filter:** Enabled
- **SAO (Sample Adaptive Offset):** Enabled
- **ALF (Adaptive Loop Filter):** Optional

#### Slices and Tiles

- **Slices:** 1 per frame
- **Tiles:** 4×4 grid (for parallel processing)
- **Wavefront Parallel Processing:** Enabled

### Bitstream Format

#### NAL Unit Types

```
- VPS (Video Parameter Set): NAL type 32
- SPS (Sequence Parameter Set): NAL type 33
- PPS (Picture Parameter Set): NAL type 34
- SEI (Supplemental Enhancement Information): NAL type 39-40
- IDR (Instantaneous Decoder Refresh): NAL type 19-20
- CRA (Clean Random Access): NAL type 21
- TRAIL (Trailing): NAL type 1-9
- TSA (Temporal Sub-layer Access): NAL type 10-12
- STSA (Step-wise Temporal Sub-layer Access): NAL type 13-15
```

#### Parameter Sets

**VPS (Video Parameter Set):**
- Profile information
- Tier information
- Level information
- Sub-layers information

**SPS (Sequence Parameter Set):**
- Resolution (3840×2160)
- Frame rate (120 fps)
- Color space (BT.2020)
- Bit depth (10-bit)
- Chroma subsampling (4:2:0)

**PPS (Picture Parameter Set):**
- Quantization parameters
- Loop filter settings
- Tile configuration
- Slice configuration

#### SEI Messages

Required SEI messages:

1. **Buffering Period:** For VBV buffer management
2. **Picture Timing:** For frame timing
3. **Recovery Point:** For random access
4. **Display Orientation:** For 3D display
5. **MAGI Metadata:** Custom SEI for MAGI-specific data

### Color Specifications

#### Color Space

- **Color Space:** BT.2020 (Rec. 2020)
- **Color Primaries:** BT.2020
- **Transfer Function:** PQ (Perceptual Quantizer) for HDR
- **Matrix Coefficients:** BT.2020 constant luminance

#### Color Depth

- **Bit Depth:** 10-bit per channel
- **Full Range:** Yes (0-1023)
- **Chroma Subsampling:** 4:2:0

#### HDR Support (Optional)

For HDR content:

- **Transfer Function:** PQ (SMPTE ST 2084)
- **MaxCLL:** 1000 nits
- **MaxFALL:** 200 nits
- **Mastering Display:** BT.2020 primaries
- **Content Light Level:** SEI message

---

## MAGI-Specific Metadata

### Required Metadata

```xml
<MAGI xmlns="http://magi-format.org/v1.0">
  <Version>1.0</Version>
  <Format>
    <FrameRate>120</FrameRate>
    <Resolution>3840x2160</Resolution>
    <EyeSeparation>180</EyeSeparation>
    <FrameCadence>alternating</FrameCadence>
    <PhaseOffset>8.33</PhaseOffset>
  </Format>
  <Stereo>
    <Mode>frame-sequential</Mode>
    <LeftEyeTrack>1</LeftEyeTrack>
    <RightEyeTrack>2</RightEyeTrack>
    <PhaseOffset>180</PhaseOffset>
    <Baseline>65</Baseline>
    <Convergence>Infinity</Convergence>
  </Stereo>
  <Display>
    <Type>3d-projector</Type>
    <ShutterGlasses>active</ShutterGlasses>
    <SyncMethod>hardware</SyncMethod>
    <RefreshRate>120</RefreshRate>
  </Display>
  <Codec>
    <VideoCodec>hevc</VideoCodec>
    <Profile>main10</Profile>
    <Level>5.1</Level>
    <Bitrate>50000000</Bitrate>
  </Codec>
</MAGI>
```

### Optional Metadata

```xml
<MAGI xmlns="http://magi-format.org/v1.0">
  <Source>
    <OriginalFormat>mp4</OriginalFormat>
    <OriginalFrameRate>24</OriginalFrameRate>
    <OriginalResolution>1920x1080</OriginalResolution>
    <OriginalCodec>h264</OriginalCodec>
    <ConversionMethod>stereocrafter</ConversionMethod>
    <ConversionDate>2024-01-15T10:30:00Z</ConversionDate>
  </Source>
  <Processing>
    <InterpolationMethod>rife</InterpolationMethod>
    <InterpolationRatio>5</InterpolationRatio>
    <UpscalingMethod>waifu2x</UpscalingMethod>
    <UpscalingRatio>2</UpscalingRatio>
    <StereoConversionMethod>stereocrafter</StereoConversionMethod>
    <ProcessingDate>2024-01-15T10:30:00Z</ProcessingDate>
    <ProcessingTime>3600</ProcessingTime>
    <GPU>NVIDIA RTX 4090</GPU>
  </Processing>
  <Quality>
    <Bitrate>50000000</Bitrate>
    <Codec>hevc</Codec>
    <Profile>main10</Profile>
    <Level>5.1</Level>
    <PSNR>42.5</PSNR>
    <SSIM>0.985</SSIM>
    <VMAF>95.2</VMAF>
  </Quality>
  <Camera>
    <Type>ZED 2</Type>
    <SerialNumber>12345</SerialNumber>
    <Baseline>120</Baseline>
    <FocalLength>2.1</FocalLength>
    <CaptureDate>2024-01-15T10:00:00Z</CaptureDate>
  </Camera>
  <HDR>
    <Enabled>true</Enabled>
    <TransferFunction>pq</TransferFunction>
    <MaxCLL>1000</MaxCLL>
    <MaxFALL>200</MaxFALL>
  </HDR>
</MAGI>
```

### Metadata Storage

Metadata is stored in the Matroska container as:

1. **Tags:** Standard Matroska tags for compatibility
2. **Attachments:** XML/JSON files as attachments
3. **Custom Elements:** EBML custom elements for MAGI-specific data

---

## Video Track Configuration

### Option 1: Frame-Sequential (Recommended)

Single video track with alternating left/right eye frames:

```
Frame 1: Left Eye (Timecode: 0ms)
Frame 2: Right Eye (Timecode: 8.33ms)
Frame 3: Left Eye (Timecode: 16.66ms)
Frame 4: Right Eye (Timecode: 25ms)
...
```

**Advantages:**
- Single track simplifies synchronization
- Compatible with standard players (plays as 2D)
- Smaller file size
- Easier to stream
- Better for real-time processing

**Disadvantages:**
- Requires metadata for proper 3D playback
- More complex frame extraction
- Requires frame-accurate timing

**Track Configuration:**

```xml
<TrackEntry>
  <TrackNumber>1</TrackNumber>
  <TrackType>1</TrackType> <!-- Video -->
  <CodecID>V_MPEGH/ISO/HEVC</CodecID>
  <CodecPrivate>[HEVC Configuration Record]</CodecPrivate>
  <Video>
    <PixelWidth>3840</PixelWidth>
    <PixelHeight>2160</PixelHeight>
    <DisplayWidth>3840</DisplayWidth>
    <DisplayHeight>2160</DisplayHeight>
    <FrameRate>120.0</FrameRate>
    <Colour>
      <MatrixCoefficients>9</MatrixCoefficients> <!-- BT.2020 -->
      <BitsPerChannel>10</BitsPerChannel>
      <ChromaSubsampling>4:2:0</ChromaSubsampling>
      <CbSubsamplingHorz>1</CbSubsamplingHorz>
      <CbSubsamplingVert>1</CbSubsamplingVert>
      <ChromaSitingHorz>0</ChromaSitingHorz>
      <ChromaSitingVert>0</ChromaSitingVert>
      <Range>0</Range> <!-- Full range -->
      <TransferCharacteristics>16</TransferCharacteristics> <!-- PQ -->
      <Primaries>9</Primaries> <!-- BT.2020 -->
      <MaxCLL>1000</MaxCLL>
      <MaxFALL>200</MaxFALL>
    </Colour>
  </Video>
  <MAGI>
    <StereoMode>frame-sequential</StereoMode>
    <LeftEyeFrames>even</LeftEyeFrames>
    <RightEyeFrames>odd</RightEyeFrames>
    <PhaseOffset>8.33</PhaseOffset>
  </MAGI>
</TrackEntry>
```

### Option 2: Dual-Stream

Two separate video tracks (one for each eye):

```
Track 1 (Left Eye): Frame 1, Frame 2, Frame 3, ...
Track 2 (Right Eye): Frame 1, Frame 2, Frame 3, ...
```

**Advantages:**
- Clear separation of eyes
- Easier to process
- Better for editing
- Independent quality control

**Disadvantages:**
- Larger file size
- More complex synchronization
- Less compatible with standard players
- More complex streaming

**Track Configuration:**

```xml
<TrackEntry>
  <TrackNumber>1</TrackNumber>
  <TrackType>1</TrackType>
  <CodecID>V_MPEGH/ISO/HEVC</CodecID>
  <Video>
    <PixelWidth>3840</PixelWidth>
    <PixelHeight>2160</PixelHeight>
    <FrameRate>60.0</FrameRate>
  </Video>
  <MAGI>
    <Eye>left</Eye>
  </MAGI>
</TrackEntry>

<TrackEntry>
  <TrackNumber>2</TrackNumber>
  <TrackType>1</TrackType>
  <CodecID>V_MPEGH/ISO/HEVC</CodecID>
  <Video>
    <PixelWidth>3840</PixelWidth>
    <PixelHeight>2160</PixelHeight>
    <FrameRate>60.0</FrameRate>
  </Video>
  <MAGI>
    <Eye>right</Eye>
  </MAGI>
</TrackEntry>
```

---

## Frame Cadence Specification

### MAGI Frame Cadence Pattern

```
L-R-L-R-L-R-L-R... (alternating)
```

- **Left Eye Frames:** Even frame numbers (0, 2, 4, ...)
- **Right Eye Frames:** Odd frame numbers (1, 3, 5, ...)
- **Phase Offset:** 180° (8.33ms at 120fps)

### Timing Specifications

```
Frame Rate: 120 fps
Frame Duration: 8.33ms per frame
Eye Duration: 16.66ms per eye (2 frames)
Phase Offset: 8.33ms (1 frame)
Refresh Rate: 120 Hz
```

### Frame Timing Diagram

```
Time:    0ms    8.33ms  16.66ms 25ms    33.33ms 41.66ms 50ms
         |      |       |       |       |       |       |
Frame:   L      R       L       R       L       R       L
Eye:     Left   Right   Left    Right   Left    Right   Left
Number:  0      1       2       3       4       5       6
```

### Synchronization Requirements

- **Frame Accuracy:** ±0.1ms
- **Eye Sync:** ±0.05ms
- **Display Sync:** Hardware sync required
- **Shutter Glasses:** Active sync with 180° phase offset

### Display Timing

For 3D projector with active shutter glasses:

```
Left Eye Display:  0ms - 8.33ms
Right Eye Display: 8.33ms - 16.66ms
Left Eye Display:  16.66ms - 25ms
Right Eye Display: 25ms - 33.33ms
...
```

---

## Audio Specifications

### Audio Codec

- **Primary:** AAC (Advanced Audio Coding)
- **Alternative:** Opus (for better compression)
- **Surround:** Dolby Atmos or DTS:X

### Audio Parameters

```xml
<AudioCodec>
  <Name>aac</Name>
  <Profile>lc</Profile>
  <SampleRate>48000</SampleRate>
  <Channels>6</Channels>
  <Bitrate>384000</Bitrate>
  <ChannelLayout>5.1</ChannelLayout>
</AudioCodec>
```

### Audio Track Configuration

```xml
<TrackEntry>
  <TrackNumber>3</TrackNumber>
  <TrackType>2</TrackType> <!-- Audio -->
  <CodecID>A_AAC</CodecID>
  <Audio>
    <SamplingFrequency>48000</SamplingFrequency>
    <Channels>6</Channels>
    <BitDepth>16</BitDepth>
  </Audio>
</TrackEntry>
```

### Audio Sync

- **Audio-Video Sync:** ±20ms
- **Lip Sync:** ±5ms
- **Audio Delay:** Adjustable (0-100ms)

---

## File Size and Bitrate

### Estimated File Sizes

| Resolution | Frame Rate | Duration | Bitrate | File Size |
|------------|------------|----------|---------|-----------|
| 4K (3840×2160) | 120 fps | 1 hour | 50 Mbps | ~22 GB |
| 4K (3840×2160) | 120 fps | 2 hours | 50 Mbps | ~44 GB |
| 4K (3840×2160) | 120 fps | 1 hour | 80 Mbps | ~36 GB |
| 2K (2560×1440) | 120 fps | 1 hour | 30 Mbps | ~13 GB |
| 2K (2560×1440) | 120 fps | 2 hours | 30 Mbps | ~26 GB |

### Compression Recommendations

- **High Quality:** 50-80 Mbps (4K), 30-50 Mbps (2K)
- **Balanced:** 30-50 Mbps (4K), 20-30 Mbps (2K)
- **Streaming:** 20-30 Mbps (4K), 15-20 Mbps (2K)
- **Archival:** 80-100 Mbps (4K), 50-70 Mbps (2K)

### Bitrate Allocation

```
Video: 90-95% of total bitrate
Audio: 3-5% of total bitrate
Metadata: <1% of total bitrate
Overhead: 1-2% of total bitrate
```

---

## Playback Requirements

### Hardware Requirements

#### Display

- **Type:** 3D projector or display
- **Refresh Rate:** 120 Hz minimum
- **Resolution:** 4K (3840×2160) per eye
- **Sync:** Hardware sync for shutter glasses
- **Input:** HDMI 2.1 or DisplayPort 1.4

#### Decoder

- **Codec:** H.265/HEVC hardware decoder
- **Profile:** Main 10
- **Level:** 5.1
- **Bit Depth:** 10-bit
- **Color:** BT.2020 support

#### System

- **CPU:** Multi-core processor (4+ cores)
- **RAM:** 8 GB minimum, 16 GB recommended
- **GPU:** Hardware HEVC decoding support
- **Storage:** SSD for smooth playback
- **Network:** 100 Mbps for streaming

### Software Requirements

#### Player

- **Format:** MAGI-compatible player
- **Decoder:** H.265/HEVC decoder
- **Sync:** Frame-accurate timing
- **Buffer:** Quad buffer support for projectors
- **Metadata:** MAGI metadata parsing

#### Operating System

- **Windows:** 10/11 with HEVC extensions
- **macOS:** 10.15+ with HEVC support
- **Linux:** FFmpeg/libav with HEVC support

### Display Requirements

#### 3D Projector

- **Refresh Rate:** 120 Hz
- **Resolution:** 4K (3840×2160)
- **Sync:** Hardware sync (VESA 3D)
- **Glasses:** Active shutter glasses
- **Input:** HDMI 2.1 or DisplayPort 1.4

#### 3D Display

- **Refresh Rate:** 120 Hz
- **Resolution:** 4K (3840×2160)
- **Type:** Active or passive 3D
- **Sync:** Hardware or software sync
- **Input:** HDMI 2.1 or DisplayPort 1.4

#### VR Headset

- **Refresh Rate:** 120 Hz minimum
- **Resolution:** 4K per eye
- **Latency:** <20ms motion-to-photon
- **Tracking:** 6DOF tracking
- **Input:** USB-C or wireless

---

## Compatibility

### Forward Compatibility

- **Standard MKV Players:** Will play MAGI files as 2D video
- **MAGI Metadata:** Ignored by non-MAGI players
- **Frame-Sequential Format:** Ensures basic playback
- **HEVC Codec:** Widely supported

### Backward Compatibility

- **MAGI 1.0 Files:** Playable on future MAGI versions
- **Metadata Structure:** Extensible
- **Codec Choices:** Flexible
- **Container Format:** Based on open standard

### Platform Support

#### Supported Platforms

- **Windows:** 10/11
- **macOS:** 10.15+
- **Linux:** Ubuntu 20.04+, Fedora 34+
- **Android:** 10+
- **iOS:** 14+

#### Hardware Support

- **NVIDIA:** GTX 10-series and newer
- **AMD:** RX 400-series and newer
- **Intel:** 10th Gen and newer
- **Apple:** M1 and newer

---

## Implementation Guide

### Creating MAGI Files

```python
from src.output.magi_writer import MAGIWriter
from src.core.magi_metadata import MAGIMetadata

# Create MAGI metadata
metadata = MAGIMetadata(
    version="1.0",
    frame_rate=120.0,
    resolution=(3840, 2160),
    eye_separation=180,
    frame_cadence="alternating",
    stereo_mode="frame-sequential"
)

# Create MAGI writer
with MAGIWriter(
    output_path="output.magi",
    fps=120.0,
    width=3840,
    height=2160,
    codec="hevc",
    bitrate=50000000,
    metadata=metadata
) as writer:
    # Write frames in alternating pattern
    for left_frame, right_frame in stereo_frames:
        writer.write_frame(left_frame, eye="left")
        writer.write_frame(right_frame, eye="right")
```

### Reading MAGI Files

```python
from src.input.magi_reader import MAGIReader

# Open MAGI file
with MAGIReader("input.magi") as reader:
    # Get metadata
    metadata = reader.get_metadata()
    print(f"Frame Rate: {metadata.frame_rate}")
    print(f"Resolution: {metadata.resolution}")
    print(f"Stereo Mode: {metadata.stereo_mode}")
    
    # Read frames
    for frame in reader.frames():
        if frame.eye == "left":
            # Process left eye frame
            process_left_frame(frame.data)
        else:
            # Process right eye frame
            process_right_frame(frame.data)
```

### Streaming MAGI Content

```python
from src.pipeline.camera_to_magi import CameraToMAGIPipeline, OutputMode

# Create camera capture
camera_capture = CameraCapture(
    camera_id=0,
    camera_type=CameraType.ZED,
    width=3840,
    height=2160,
    fps=30.0
)

# Create pipeline for streaming only
pipeline = CameraToMAGIPipeline(
    camera_capture=camera_capture,
    output_mode=OutputMode.STREAM_ONLY,
    mode=ProcessingMode.REALTIME
)

# Start pipeline
pipeline.start()

# Stream frames
while pipeline.is_running():
    frame, eye = pipeline.get_output_frame()
    if frame is not None:
        # Display or stream frame
        display_frame(frame, eye)
```

### Saving MAGI Content

```python
from src.pipeline.camera_to_magi import CameraToMAGIPipeline, OutputMode

# Create camera capture
camera_capture = CameraCapture(
    camera_id=0,
    camera_type=CameraType.ZED,
    width=3840,
    height=2160,
    fps=30.0
)

# Create pipeline for file output
pipeline = CameraToMAGIPipeline(
    camera_capture=camera_capture,
    output_path="recording.magi",
    output_mode=OutputMode.FILE_ONLY,
    mode=ProcessingMode.QUALITY
)

# Start pipeline
pipeline.start()

# Record for specified duration
time.sleep(3600)  # 1 hour

# Stop pipeline
pipeline.stop()
```

---

## Reference Implementation

### Core Components

- [`src/output/magi_writer.py`](../src/output/magi_writer.py) - MAGI file writer
- [`src/input/magi_reader.py`](../src/input/magi_reader.py) - MAGI file reader
- [`src/core/magi_metadata.py`](../src/core/magi_metadata.py) - MAGI metadata handling
- [`src/input/camera_capture.py`](../src/input/camera_capture.py) - Camera capture
- [`src/pipeline/camera_to_magi.py`](../src/pipeline/camera_to_magi.py) - Camera-to-MAGI pipeline

### Processing Components

- [`src/processing/interpolation.py`](../src/processing/interpolation.py) - Frame interpolation
- [`src/processing/upscaling.py`](../src/processing/upscaling.py) - Frame upscaling
- [`src/processing/frame_cadence.py`](../src/processing/frame_cadence.py) - Frame cadence

### UI Components

- [`src/ui/web_ui.py`](../src/ui/web_ui.py) - Web interface
- [`src/ui/static/index.html`](../src/ui/static/index.html) - Web UI
- [`src/ui/static/app.js`](../src/ui/static/app.js) - JavaScript client

---

## Future Enhancements

### Planned Features

1. **HDR Support:** Add HDR metadata and color grading
2. **Variable Frame Rate:** Support for VFR content
3. **Multiple Audio Tracks:** Support for different languages
4. **Subtitle Support:** Add 3D subtitle tracks
5. **Interactive Elements:** Add interactive metadata for VR
6. **Streaming Optimization:** Add adaptive streaming support
7. **Cloud Integration:** Direct cloud storage and streaming
8. **AI Enhancement:** Real-time AI upscaling and enhancement
9. **Light Field:** Support for light field displays
10. **Holographic:** Support for holographic displays

### Version Roadmap

- **MAGI 1.0:** Initial release (current)
- **MAGI 1.1:** HDR support and improved metadata
- **MAGI 1.2:** Variable frame rate and streaming optimization
- **MAGI 2.0:** VR support and interactive elements
- **MAGI 3.0:** Holographic and light field support

### Codec Evolution

- **Current:** HEVC H.265 Main 10
- **Near Future:** AV1 for better compression
- **Future:** VVC (H.266) for next-generation compression

---

## Appendix

### Glossary

- **MAGI:** High-Frame-Rate 3D Cinema system
- **HEVC:** High Efficiency Video Coding (H.265)
- **GOP:** Group of Pictures
- **NAL:** Network Abstraction Layer
- **SEI:** Supplemental Enhancement Information
- **VPS:** Video Parameter Set
- **SPS:** Sequence Parameter Set
- **PPS:** Picture Parameter Set
- **HDR:** High Dynamic Range
- **SDR:** Standard Dynamic Range
- **BT.2020:** ITU-R Recommendation BT.2020 (Ultra HD)
- **PQ:** Perceptual Quantizer (HDR transfer function)

### References

1. **ITU-T H.265:** High Efficiency Video Coding
2. **ISO/IEC 23008-2:** HEVC specification
3. **Matroska Specification:** EBML container format
4. **BT.2020:** Ultra HD TV parameters
5. **SMPTE ST 2084:** HDR transfer function
6. **Douglas Trumbull:** MAGI system inventor

### Contact

For questions or contributions to the MAGI file format specification, please contact the MAGI Pipeline project.

---

**Document Version:** 1.0  
**Last Updated:** 2024-01-15  
**Status:** Final  
**Maintainer:** MAGI Pipeline Project
