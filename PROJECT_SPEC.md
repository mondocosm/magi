# MAGI Video Pipeline - Project Specification

## Project Overview
A real-time 3D video interpolation and upscaling pipeline to convert video content into the MAGI (Magical Image) format invented by Douglas Trumbull.

## MAGI Format Specifications
- **Frame Rate**: 120 fps (native) or 60 fps per eye in 3D
- **Resolution**: 4K 3D projection (3840×2160 per eye)
- **Capture**: 100% action shooting at 120 fps
- **3D Technique**: Left and right eye images captured 180° out of phase
- **Projection**: Matched to projector cadence for maximum immersion
- **Output Format**: Alternating left/right eye frames synchronized with 3D shutter glasses

## Input Format Examples

### YouTube 3D
- **Resolution**: Up to 4K (variable)
- **Frame Rate**: Up to 60fps (variable)
- **Format**: Side-by-side or top-bottom 3D
- **Challenge**: Variable quality and frame rates

### 3D Blu-ray
- **Resolution**: Up to 1080p (1920×1080)
- **Frame Rate**: 24fps
- **Format**: MVC (Multiview Video Coding) or frame-sequential
- **Challenge**: Lower resolution and frame rate

## Conversion Requirements

### Frame Rate Conversion
- **Any frame rate → 120fps**: Adaptive interpolation based on input frame rate
  - 24fps → 120fps: 5x interpolation (1 frame → 5 frames)
  - 30fps → 120fps: 4x interpolation (1 frame → 4 frames)
  - 60fps → 120fps: 2x interpolation (1 frame → 2 frames)
  - Custom frame rates: Automatic ratio calculation

### Resolution Upscaling
- **1080p → 4K**: 2x upscaling per dimension
- **720p → 4K**: 3x upscaling per dimension
- **480p → 4K**: 4x upscaling per dimension

### Processing Pipeline
1. **Input Detection**: Identify format, resolution, frame rate
2. **Upscaling**: Scale to 4K resolution per eye
3. **Frame Interpolation**: Convert to 120fps total
4. **3D Format Conversion**: Ensure side-by-side format
5. **Frame Cadence**: Alternate left/right eye frames for MAGI output
6. **Output**: 60fps per eye alternating in sync with 3D glasses

## System Architecture

### Core Components

#### 1. Input Module
- Accept various video formats (MP4, AVI, MKV, MOV)
- Support 2D and 3D input formats (side-by-side, top-bottom, frame-sequential)
- Detect input characteristics (resolution, frame rate, codec)
- Handle streaming and file-based inputs

#### 2. 3D Processing Module
- Convert 2D content to 3D using depth estimation
- Process existing 3D formats (SBS, TAB, frame-sequential)
- Separate left/right eye channels
- Apply 3D enhancement algorithms

#### 3. Frame Interpolation Module
- Interpolate frames to achieve 120 fps from lower frame rates
- Support multiple interpolation algorithms:
  - Optical flow-based interpolation
  - Motion-compensated frame interpolation
  - AI-based interpolation (RIFE, DAIN)
- Handle motion blur and artifact reduction

#### 3.5. 2D to 3D Conversion Module
- Convert 2D videos to high-quality stereoscopic 3D
- Integration with StereoCrafter for diffusion-based 3D generation
- Depth estimation and view synthesis
- Fallback to simple depth-based conversion when StereoCrafter unavailable
- Support for various content types (movies, vlogs, animations, AIGC videos)

#### 4. Upscaling Module
- Upscale content to 4K resolution per eye
- Integrate with Waifu2x-Extension-GUI for AI upscaling
- Support multiple upscaling models:
  - Waifu2x (anime-style)
  - RealESRGAN (realistic)
  - Anime4K (fast anime upscaling)
- Maintain edge detail and reduce artifacts

#### 5. Frame Cadence Module
- Synchronize left/right eye frames 180° out of phase
- Match projector/display cadence
- Handle frame timing and synchronization
- Implement frame doubling/tripling as needed

#### 6. Output Module
- Generate MAGI format output
- Support various output containers
- Embed metadata for MAGI compatibility
- Handle audio synchronization

#### 7. Real-time Pipeline Controller
- Coordinate all modules for streaming processing
- Manage buffer queues and memory
- Optimize for low latency
- Support GPU acceleration

#### 8. Configuration & UI
- Web-based interface for configuration
- Real-time monitoring and control
- Preset management for different content types
- Performance metrics and logging

## Technology Stack

### Core Technologies
- **Python 3.9+**: Primary development language
- **FFmpeg**: Video processing and codec handling
- **OpenCV**: Image processing and computer vision
- **PyTorch/TensorFlow**: AI model inference
- **CUDA/Vulkan**: GPU acceleration

### External Tools Integration
- **Bino3D**: 3D video playback and format handling
- **Waifu2x-Extension-GUI**: AI upscaling capabilities
- **RIFE/DAIN**: Frame interpolation models

### Performance Optimization
- Multi-threading and parallel processing
- GPU acceleration (CUDA, Vulkan, Metal)
- Memory-efficient buffer management
- Just-in-time processing for real-time performance

## Key Features

### Input Support
- Video formats: MP4, AVI, MKV, MOV, WebM
- 3D formats: Side-by-Side, Top-Bottom, Frame-Sequential
- Frame rates: 24fps, 30fps, 60fps, 120fps
- Resolutions: SD, HD, Full HD, 4K

### Processing Capabilities
- Real-time 2D to 3D conversion
- Frame rate upconversion (24/30/60 → 120 fps)
- Resolution upscaling (to 4K per eye)
- Motion-compensated interpolation
- AI-enhanced upscaling

### Output Options
- MAGI format (120 fps, 4K 3D)
- Various container formats
- Configurable quality settings
- Audio track preservation

## Performance Targets
- **Latency**: < 100ms for real-time processing
- **Throughput**: Support 4K@120fps processing
- **Quality**: Minimal artifacts, high visual fidelity
- **Resource Usage**: Efficient GPU/CPU utilization

## Development Phases

### Phase 1: Core Infrastructure
- Project structure and dependencies
- Basic video I/O
- Configuration system

### Phase 2: Processing Modules
- Frame interpolation implementation
- Upscaling integration
- 3D processing

### Phase 3: Pipeline Integration
- Real-time pipeline controller
- Buffer management
- Performance optimization

### Phase 4: UI and Polish
- Web interface
- Monitoring and logging
- Testing and optimization

## Dependencies

### Python Packages
```
opencv-python>=4.8.0
numpy>=1.24.0
ffmpeg-python>=0.2.0
torch>=2.0.0
torchvision>=0.15.0
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
asyncio>=3.4.3
```

### System Dependencies
- FFmpeg 4.4+
- CUDA Toolkit 11.8+ (for NVIDIA GPUs)
- Vulkan SDK (for cross-platform GPU)

### External Tools
- Bino3D (already present)
- Waifu2x-Extension-GUI (already present)

## File Structure
```
magipipeline/
├── src/
│   ├── core/           # Core infrastructure
│   ├── input/          # Input handling
│   ├── processing/     # Processing modules
│   ├── output/         # Output generation
│   ├── pipeline/       # Pipeline controller
│   └── ui/             # User interface
├── models/             # AI models
├── config/             # Configuration files
├── tests/              # Test suite
├── docs/               # Documentation
└── scripts/            # Utility scripts
```

## Success Criteria
- Successfully convert 2D/3D video to MAGI format
- Achieve near real-time performance
- Maintain high visual quality
- Support various input formats
- Provide intuitive user interface
- Comprehensive documentation

## Future Enhancements
- VR headset support
- Cloud processing capabilities
- Mobile app interface
- Advanced AI models
- Real-time streaming integration
- Custom interpolation algorithms