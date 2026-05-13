# MAGI Pipeline User Manual

## Table of Contents

1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Video Conversion](#video-conversion)
6. [Game Capture](#game-capture)
7. [Camera Input](#camera-input)
8. [Configuration](#configuration)
9. [GPU Acceleration](#gpu-acceleration)
10. [Cloud Processing](#cloud-processing)
11. [Troubleshooting](#troubleshooting)
12. [Advanced Usage](#advanced-usage)
13. [FAQ](#faq)

---

## Introduction

MAGI Pipeline is a comprehensive software solution for converting any video content to MAGI format - Douglas Trumbull's revolutionary high-frame-rate 3D cinema system. This manual will guide you through installation, configuration, and usage of all MAGI Pipeline features.

### What You Can Do

- **Convert Videos** - Transform any video file (2D or 3D) to MAGI format
- **Capture Games** - Record and convert gameplay to MAGI in real-time
- **Use Cameras** - Capture from stereo/depth cameras and convert to MAGI
- **Process in Real-time** - Near real-time conversion with GPU acceleration
- **Use Cloud Processing** - Optional cloud GPU support for faster processing

---

## System Requirements

### Minimum Requirements

| Component | Minimum |
|-----------|---------|
| **Operating System** | Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+) |
| **CPU** | Intel Core i5 / AMD Ryzen 5 (8 cores recommended) |
| **RAM** | 16 GB (32 GB recommended) |
| **GPU** | NVIDIA GTX 1660 SUPER or equivalent |
| **Storage** | 50 GB free space (SSD recommended) |
| **Network** | Broadband internet (for cloud processing) |

### Recommended Requirements

| Component | Recommended |
|-----------|-------------|
| **Operating System** | Windows 11, macOS 13+, Linux (Ubuntu 22.04+) |
| **CPU** | Intel Core i7 / AMD Ryzen 7 (12+ cores) |
| **RAM** | 32 GB (64 GB for 4K processing) |
| **GPU** | NVIDIA RTX 3060 or better (RTX 4090 for real-time) |
| **Storage** | 100 GB+ NVMe SSD |
| **Network** | High-speed internet (100+ Mbps for cloud) |

### Supported GPUs

**NVIDIA (CUDA)**
- GTX 1660 SUPER or better
- RTX 20 series, 30 series, 40 series
- Quadro RTX series

**AMD (ROCm)**
- RX 5000 series or better
- RX 6000 series, RX 7000 series

**Apple Silicon (Metal)**
- M1, M1 Pro, M1 Max, M1 Ultra
- M2, M2 Pro, M2 Max, M2 Ultra

---

## Installation

### Method 1: Using pip (Recommended)

```bash
# Clone the repository
git clone https://github.com/mondocosm/magi.git
cd magi

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install MAGI Pipeline
pip install -e .
```

### Method 2: Using Docker

```bash
# Pull the Docker image
docker pull mondocosm/magi-pipeline:latest

# Run the web interface
docker run -p 8000:8000 --gpus all mondocosm/magi-pipeline
```

### Method 3: From Source

```bash
# Clone the repository
git clone https://github.com/mondocosm/magi.git
cd magi

# Install dependencies
pip install -r requirements.txt

# Run the web interface
python -m src.ui.web_ui
```

### Verifying Installation

```bash
# Check if MAGI Pipeline is installed
python -c "import src.ui.web_ui; print('MAGI Pipeline installed successfully')"

# Start the web interface
python -m src.ui.web_ui
```

The web interface should be available at: http://localhost:8000

---

## Quick Start

### 1. Launch the Web Interface

```bash
python -m src.ui.web_ui
```

### 2. Open Your Browser

Navigate to: http://localhost:8000

### 3. Choose Your Mode

- **Video Mode** - Convert video files to MAGI format
- **Game Mode** - Capture and convert gameplay to MAGI
- **Camera Mode** - Capture from cameras and convert to MAGI

### 4. Configure Settings

- Select your input source
- Choose interpolation method
- Set upscaling options
- Configure 3D processing
- Select output location

### 5. Start Processing

Click "Start Conversion" and monitor progress in real-time.

---

## Video Conversion

### Supported Input Formats

**Video Containers**
- MP4, AVI, MKV, MOV, WMV, FLV, WebM
- Most professional formats: ProRes, DNxHD, etc.

**Video Codecs**
- H.264, H.265, VP9, AV1
- ProRes, DNxHD, CineForm
- Most uncompressed formats

**3D Formats**
- Side-by-Side (SBS)
- Top-Bottom (TAB)
- Frame-Sequential
- Anaglyph
- MVC

### Step-by-Step Video Conversion

#### 1. Select Video Mode

Click the "Video" button in the mode selection section.

#### 2. Upload Your Video

- **Drag and drop** your video file onto the upload area
- Or **click to browse** and select your file

#### 3. Configure Video Settings

**Input Detection**
- MAGI Pipeline automatically detects:
  - Video format and codec
  - Frame rate
  - Resolution
  - 3D format (if applicable)

**Interpolation Settings**
- **Method**: Choose interpolation algorithm
  - `Optical Flow` - Good quality, moderate speed
  - `RIFE (AI)` - Best quality, requires GPU
  - `DAIN (AI)` - Excellent quality, slower
  - `FILM` - Good balance of quality/speed
  - `X-INT` - Fast, good for real-time

- **Target Frame Rate**: Automatically set to 120 fps
  - 24 fps → 120 fps (5x interpolation)
  - 30 fps → 120 fps (4x interpolation)
  - 60 fps → 120 fps (2x interpolation)

**Upscaling Settings**
- **Method**: Choose upscaling algorithm
  - `Bicubic` - Fast, basic quality
  - `Lanczos` - Good quality, moderate speed
  - `Waifu2x (AI)` - Excellent quality, requires GPU
  - `RealESRGAN (AI)` - Best quality, requires GPU
  - `SwinIR` - Great for detail enhancement
  - `HAT` - State-of-the-art AI upscaling

- **Target Resolution**: 4K per eye (3840×2160)
  - Can be adjusted if needed

**3D Processing Settings**
- **Source 3D Format**: Auto-detected or manually selected
  - `2D` - Convert 2D to 3D using StereoCrafter
  - `SBS` - Side-by-Side
  - `TAB` - Top-Bottom
  - `Frame Sequential` - Already in frame-sequential format
  - `Anaglyph` - Red/cyan 3D
  - `MVC` - Multiview Video Coding

- **2D to 3D Conversion**: If source is 2D
  - `StereoCrafter` - AI-powered depth estimation and view synthesis
  - `Traditional` - Basic depth-based conversion

**Frame Cadence Settings**
- **Left/Right Phase**: 180° (standard for MAGI)
- **Alternation Pattern**: L-R-L-R (standard)
- Can be customized for specific projectors

#### 4. Start Conversion

Click "Start Conversion" to begin processing.

#### 5. Monitor Progress

- **Pipeline Visualization** - See which stage is active
- **Progress Bar** - Overall completion percentage
- **Detailed Stats** - Frame rate, resolution, processing time
- **Estimated Time Remaining** - Based on current speed

#### 6. Download Results

Once complete:
- Download the MAGI file (.magi)
- View processing statistics
- Compare input vs output quality

### Video Conversion Tips

**For Best Quality**
- Use AI-based interpolation (RIFE or DAIN)
- Use AI-based upscaling (RealESRGAN or HAT)
- Ensure source video is high quality
- Use GPU acceleration

**For Faster Processing**
- Use optical flow interpolation
- Use bicubic upscaling
- Use cloud GPU processing
- Reduce resolution if acceptable

**For Real-time Processing**
- Use X-INT interpolation
- Use bicubic upscaling
- Use RTX 4090 or better GPU
- Consider cloud processing

---

## Game Capture

### Supported Games

MAGI Pipeline can capture from any game or application running on your system:

- **PC Games** - Any DirectX, OpenGL, or Vulkan game
- **Emulators** - Retro games, console emulators
- **VR Games** - SteamVR, Oculus games
- **Applications** - Any window or screen content

### Step-by-Step Game Capture

#### 1. Select Game Mode

Click the "Game" button in the mode selection section.

#### 2. Configure Game Capture

**Capture Method**
- **Screen Capture** - Capture entire screen
- **Window Capture** - Capture specific window
- **OBS WebSocket** - Connect to OBS Studio
- **Virtual Camera** - Use virtual camera device

**Capture Settings**
- **Resolution**: Auto-detected (can be overridden)
- **Frame Rate**: Auto-detected (will be interpolated to 120 fps)
- **Audio**: Include game audio (optional)

#### 3. Start Game Capture

1. Launch your game or application
2. Click "Start Capture" in MAGI Pipeline
3. Select the game window or screen
4. MAGI Pipeline will begin capturing and converting

#### 4. Monitor Real-time Processing

- **Live Preview** - See captured content
- **Processing Stats** - Frame rate, resolution, GPU usage
- **Quality Metrics** - Interpolation quality, upscaling quality
- **Performance** - CPU/GPU usage, memory usage

#### 5. Stop and Save

Click "Stop Capture" to:
- Save the MAGI file
- View capture statistics
- Review quality metrics

### Game Capture Tips

**For Best Quality**
- Capture at highest possible resolution
- Use AI-based interpolation and upscaling
- Ensure stable frame rate in game
- Use powerful GPU (RTX 4090 recommended)

**For Real-time Capture**
- Use X-INT interpolation
- Use bicubic upscaling
- Optimize game settings for performance
- Use dedicated capture GPU if available

**For Streaming**
- Use OBS WebSocket integration
- Configure OBS for optimal quality
- Use cloud processing for encoding
- Consider lower resolution for bandwidth

---

## Camera Input

### Supported Cameras

MAGI Pipeline supports various camera types:

**Stereo Cameras**
- ZED cameras (ZED 2, ZED 2i, ZED X)
- Intel RealSense (D400 series)
- Microsoft Kinect (v1, v2)
- Google 180 VR cameras
- HUD stereo cameras

**Depth Cameras**
- Intel RealSense (D400 series)
- Microsoft Kinect (v1, v2)
- Orbbec cameras
- LiDAR cameras

**Standard Cameras**
- USB webcams
- DSLR/Mirrorless cameras (via capture card)
- IP cameras
- Professional video cameras

### Step-by-Step Camera Capture

#### 1. Select Camera Mode

Click the "Camera" button in the mode selection section.

#### 2. Detect and Select Camera

MAGI Pipeline will automatically detect available cameras:
- **Stereo Cameras** - Listed with stereo capabilities
- **Depth Cameras** - Listed with depth capabilities
- **Standard Cameras** - Listed as single cameras

Select your camera from the dropdown list.

#### 3. Configure Camera Settings

**Camera Settings**
- **Resolution**: Auto-detected (can be adjusted)
- **Frame Rate**: Auto-detected (will be interpolated to 120 fps)
- **Exposure**: Auto or manual
- **White Balance**: Auto or manual
- **Focus**: Auto or manual

**Stereo Settings** (for stereo cameras)
- **Depth Mode**: Enable/disable depth processing
- **Stereo Alignment**: Auto or manual calibration
- **Baseline Distance**: Distance between cameras

**3D Processing Settings**
- **Source Format**: Auto-detected (stereo or 2D)
- **2D to 3D**: If using single camera, enable StereoCrafter
- **Depth Enhancement**: Enhance depth estimation

#### 4. Start Camera Capture

1. Click "Start Capture"
2. MAGI Pipeline will begin capturing from camera
3. Real-time processing to MAGI format
4. Live preview of captured content

#### 5. Monitor Real-time Processing

- **Live Preview** - See captured content
- **Camera Stats** - Resolution, frame rate, exposure
- **Processing Stats** - Interpolation, upscaling, 3D processing
- **Performance** - CPU/GPU usage, memory usage

#### 6. Stop and Save

Click "Stop Capture" to:
- Save the MAGI file
- View capture statistics
- Review quality metrics

### Camera Capture Tips

**For Best Quality**
- Use high-quality stereo camera (ZED 2i recommended)
- Capture at highest possible resolution
- Use AI-based interpolation and upscaling
- Ensure good lighting conditions

**For Real-time Capture**
- Use X-INT interpolation
- Use bicubic upscaling
- Optimize camera settings for performance
- Use powerful GPU

**For Depth Processing**
- Use dedicated depth camera (RealSense, Kinect)
- Enable depth enhancement
- Use StereoCrafter for 2D to 3D conversion
- Consider cloud processing for complex scenes

---

## Configuration

### Configuration File

MAGI Pipeline uses a YAML configuration file for advanced settings:

```bash
# Create configuration file
cp config/config.example.yaml config/config.yaml
```

### Configuration Options

```yaml
# GPU Configuration
gpu:
  mode: auto  # auto, cuda, rocm, metal, cpu
  device: 0   # GPU device number
  memory_fraction: 0.8  # GPU memory to use

# Interpolation Settings
interpolation:
  method: rife  # optical_flow, rife, dain, film, x_int
  model: rife_v4  # Model version
  quality: high  # low, medium, high, ultra

# Upscaling Settings
upscaling:
  method: realesrgan  # bicubic, lanczos, waifu2x, realesrgan, swinir, hat
  model: realesrgan_x4  # Model version
  quality: high  # low, medium, high, ultra

# 3D Processing Settings
processing_3d:
  method: stereocrafter  # stereocrafter, traditional
  depth_model: midas  # Depth estimation model
  quality: high  # low, medium, high, ultra

# Frame Cadence Settings
frame_cadence:
  target_fps: 120
  phase: 180  # Phase separation in degrees
  pattern: L-R-L-R  # Alternation pattern

# Output Settings
output:
  format: magi  # magi, mkv, mp4
  codec: hevc  # hevc, h264, vp9, av1
  quality: high  # low, medium, high, ultra
  bitrate: auto  # auto or specific bitrate

# Cloud Processing Settings
cloud:
  enabled: false  # Enable cloud processing
  provider: runpod  # runpod, vast, lambda, custom
  endpoint: ""  # Custom endpoint URL
  api_key: ""  # API key for cloud service

# Logging Settings
logging:
  level: info  # debug, info, warning, error
  file: logs/magi_pipeline.log
```

### Environment Variables

You can also configure MAGI Pipeline using environment variables:

```bash
# GPU Configuration
export MAGI_GPU_MODE=cuda
export MAGI_GPU_DEVICE=0

# Processing Settings
export MAGI_INTERPOLATION_METHOD=rife
export MAGI_UPSCALING_METHOD=realesrgan

# Cloud Processing
export MAGI_CLOUD_ENABLED=true
export MAGI_CLOUD_PROVIDER=runpod
export MAGI_CLOUD_API_KEY=your_api_key

# Logging
export MAGI_LOG_LEVEL=debug
```

---

## GPU Acceleration

### Automatic GPU Detection

MAGI Pipeline automatically detects and configures the best available GPU:

1. **NVIDIA GPUs** - Uses CUDA acceleration
2. **AMD GPUs** - Uses ROCm acceleration
3. **Apple Silicon** - Uses Metal acceleration
4. **CPU Fallback** - Uses CPU if no GPU available

### Manual GPU Configuration

If automatic detection fails, you can manually configure:

```yaml
gpu:
  mode: cuda  # cuda, rocm, metal, cpu
  device: 0   # GPU device number
  memory_fraction: 0.8  # GPU memory to use
```

### GPU Performance Comparison

| GPU | Real-time Speed | Quality |
|-----|-----------------|---------|
| GTX 1660 SUPER | 0.5x | Good |
| RTX 3060 | 1.0x | Excellent |
| RTX 3070 | 1.5x | Excellent |
| RTX 3080 | 2.0x | Excellent |
| RTX 4090 | 2.5x | Excellent |

### GPU Optimization Tips

**For NVIDIA GPUs**
- Install latest CUDA drivers
- Use RTX series for Tensor Cores
- Enable GPU scaling in NVIDIA Control Panel
- Use dedicated GPU for processing

**For AMD GPUs**
- Install latest ROCm drivers
- Use RDNA2/RDNA3 architecture
- Enable GPU scaling in AMD Software
- Use dedicated GPU for processing

**For Apple Silicon**
- Use M1 Pro/Max/Ultra or M2 Pro/Max/Ultra
- Enable Metal acceleration
- Use unified memory efficiently
- Close other GPU-intensive applications

---

## Cloud Processing

### Why Use Cloud Processing?

- **Faster Processing** - Access to powerful cloud GPUs
- **No Local Hardware** - Process without powerful local GPU
- **Scalability** - Process multiple files simultaneously
- **Cost-Effective** - Pay only for what you use

### Supported Cloud Providers

**RunPod**
- High-performance GPUs (RTX 4090, A100)
- Low latency
- Competitive pricing
- Easy integration

**Vast.ai**
- Wide range of GPU options
- Flexible pricing
- Good availability
- Community marketplace

**Lambda Labs**
- Professional-grade GPUs
- Excellent performance
- Reliable service
- Enterprise support

**Custom Endpoints**
- Use your own cloud infrastructure
- Private cloud deployment
- Custom configurations
- Full control

### Setting Up Cloud Processing

#### 1. Choose a Provider

Select your preferred cloud provider in the configuration:

```yaml
cloud:
  enabled: true
  provider: runpod  # runpod, vast, lambda, custom
  endpoint: ""  # For custom endpoints
  api_key: "your_api_key_here"
```

#### 2. Get API Key

- **RunPod**: https://www.runpod.io/console/api-keys
- **Vast.ai**: https://cloud.vast.ai/apikeys/
- **Lambda Labs**: https://cloud.lambdalabs.com/api-keys
- **Custom**: Configure your own endpoint

#### 3. Configure Cloud Settings

```yaml
cloud:
  enabled: true
  provider: runpod
  endpoint: ""
  api_key: "your_api_key_here"
  gpu_type: "RTX 4090"  # GPU type to use
  region: "us-east-1"  # Region preference
  max_price: 1.0  # Maximum price per hour
}
```

#### 4. Use Cloud Processing

When processing, MAGI Pipeline will automatically:
1. Check if cloud processing is enabled
2. Connect to cloud provider
3. Upload input data
4. Process on cloud GPU
5. Download results

### Cloud Pricing

**RunPod**
- RTX 4090: ~$1.00/hour
- A100: ~$2.50/hour
- Free tier: $0/month (limited)

**Vast.ai**
- RTX 4090: ~$0.50/hour
- A100: ~$1.50/hour
- Variable pricing based on demand

**Lambda Labs**
- RTX 4090: ~$1.20/hour
- A100: ~$3.00/hour
- Enterprise plans available

### Cloud Processing Tips

**For Best Performance**
- Use RTX 4090 or A100 GPUs
- Choose region closest to you
- Use high-speed internet connection
- Process multiple files in parallel

**For Cost Efficiency**
- Use Vast.ai for lower cost
- Process during off-peak hours
- Batch process multiple files
- Use spot instances when available

**For Reliability**
- Use Lambda Labs for enterprise
- Set up monitoring and alerts
- Use multiple regions for redundancy
- Implement error handling

---

## Troubleshooting

### Common Issues

#### Issue: "No GPU detected"

**Solution:**
1. Check GPU drivers are installed
2. Verify GPU is recognized by system
3. Check GPU configuration in config file
4. Try manual GPU configuration

```bash
# Check NVIDIA GPU
nvidia-smi

# Check AMD GPU
rocm-smi

# Check Apple Silicon
system_profiler SPDisplaysDataType
```

#### Issue: "Out of memory"

**Solution:**
1. Reduce GPU memory fraction in config
2. Lower processing quality
3. Use smaller batch sizes
4. Close other GPU-intensive applications

```yaml
gpu:
  memory_fraction: 0.6  # Reduce from 0.8
```

#### Issue: "Slow processing"

**Solution:**
1. Check GPU is being used (not CPU)
2. Use faster interpolation method
3. Use faster upscaling method
4. Enable cloud processing
5. Upgrade GPU if possible

#### Issue: "Poor quality output"

**Solution:**
1. Use AI-based interpolation (RIFE, DAIN)
2. Use AI-based upscaling (RealESRGAN, HAT)
3. Ensure high-quality input
4. Increase processing quality settings
5. Check 3D processing settings

#### Issue: "Camera not detected"

**Solution:**
1. Check camera is connected
2. Install camera drivers
3. Check camera permissions
4. Try different USB port
5. Test camera with other software

#### Issue: "Game capture not working"

**Solution:**
1. Run MAGI Pipeline as administrator
2. Check game is running in compatible mode
3. Try different capture method
4. Disable game overlay (Steam, Discord, etc.)
5. Use OBS WebSocket integration

#### Issue: "Cloud processing failed"

**Solution:**
1. Check API key is correct
2. Verify internet connection
3. Check cloud provider status
4. Verify account has credits
5. Try different cloud provider

### Getting Help

If you encounter issues not covered here:

1. **Check Documentation** - Read all documentation files
2. **Search Issues** - Check GitHub issues for similar problems
3. **Create Issue** - Report bug on GitHub with details
4. **Join Community** - Ask for help in community forums

### Debug Mode

Enable debug logging for detailed information:

```yaml
logging:
  level: debug
  file: logs/magi_pipeline_debug.log
```

Or use environment variable:

```bash
export MAGI_LOG_LEVEL=debug
python -m src.ui.web_ui
```

---

## Advanced Usage

### Command Line Interface

MAGI Pipeline also provides a CLI for advanced users:

```bash
# Convert video to MAGI
python -m src.cli --input video.mp4 --output video.magi --mode video

# Capture game to MAGI
python -m src.cli --game "Game Name" --output game.magi --mode game

# Capture camera to MAGI
python -m src.cli --camera 0 --output camera.magi --mode camera

# Use custom configuration
python -m src.cli --input video.mp4 --config config/custom.yaml
```

### Batch Processing

Process multiple files at once:

```bash
# Process all videos in directory
python -m src.cli --batch --input ./videos --output ./magi_files

# Process with specific settings
python -m src.cli --batch --input ./videos --output ./magi_files \
  --interpolation rife --upscaling realesrgan --quality high
```

### API Integration

MAGI Pipeline provides a REST API for integration:

```python
import requests

# Start conversion
response = requests.post('http://localhost:8000/api/convert', json={
    'input': 'video.mp4',
    'output': 'video.magi',
    'mode': 'video',
    'settings': {
        'interpolation': 'rife',
        'upscaling': 'realesrgan',
        'quality': 'high'
    }
})

# Check status
status = requests.get(f'http://localhost:8000/api/status/{response.json()["job_id"]}')
```

### Custom Processing Pipelines

Create custom processing pipelines:

```python
from src.pipeline.controller import PipelineController
from src.input.video_input import VideoInput
from src.processing.interpolation import InterpolationProcessor
from src.processing.upscaling import UpscalingProcessor
from src.output.magi_encoder import MAGIEncoder

# Create custom pipeline
pipeline = PipelineController()

# Add custom processors
pipeline.add_processor(VideoInput('input.mp4'))
pipeline.add_processor(InterpolationProcessor(method='rife'))
pipeline.add_processor(UpscalingProcessor(method='realesrgan'))
pipeline.add_processor(MAGIEncoder('output.magi'))

# Run pipeline
pipeline.run()
```

### Plugin Development

Create custom plugins for MAGI Pipeline:

```python
from src.pipeline.plugin import Plugin

class CustomPlugin(Plugin):
    def __init__(self):
        super().__init__(name='custom_plugin')
    
    def process(self, frame):
        # Custom processing logic
        processed_frame = self.custom_function(frame)
        return processed_frame
    
    def custom_function(self, frame):
        # Your custom processing
        return frame

# Register plugin
plugin = CustomPlugin()
pipeline.register_plugin(plugin)
```

---

## FAQ

### General Questions

**Q: What is MAGI format?**
A: MAGI is Douglas Trumbull's high-frame-rate 3D cinema system with 120 fps at 4K resolution per eye.

**Q: Can I convert any video to MAGI?**
A: Yes, MAGI Pipeline supports most video formats and can convert both 2D and 3D content.

**Q: Do I need a 3D display to view MAGI files?**
A: Yes, you need a 3D display or projector that supports 120 fps frame-sequential 3D.

**Q: Is MAGI Pipeline free?**
A: Yes, MAGI Pipeline is open-source and free to use. Cloud processing may incur costs.

### Technical Questions

**Q: What GPU do I need?**
A: Minimum: GTX 1660 SUPER. Recommended: RTX 3060 or better. Real-time: RTX 4090.

**Q: Can I use CPU instead of GPU?**
A: Yes, but processing will be much slower (27x slower than GPU).

**Q: How long does conversion take?**
A: Depends on hardware and settings. With RTX 3060: ~1x real-time. With RTX 4090: ~2.5x real-time.

**Q: What's the output file size?**
A: Depends on input and quality settings. Typically 2-5x larger than input due to higher frame rate and resolution.

### Usage Questions

**Q: Can I convert in real-time?**
A: Yes, with powerful GPU (RTX 4090) and optimized settings.

**Q: Can I capture games?**
A: Yes, MAGI Pipeline supports game capture from any game or application.

**Q: Can I use cameras?**
A: Yes, MAGI Pipeline supports stereo cameras, depth cameras, and standard cameras.

**Q: Can I use cloud processing?**
A: Yes, MAGI Pipeline supports multiple cloud providers for faster processing.

### Troubleshooting Questions

**Q: Why is my GPU not detected?**
A: Check GPU drivers are installed and GPU is recognized by system. Try manual GPU configuration.

**Q: Why is processing slow?**
A: Check if GPU is being used, try faster methods, enable cloud processing, or upgrade GPU.

**Q: Why is quality poor?**
A: Use AI-based methods, ensure high-quality input, increase quality settings, check 3D processing.

**Q: Why did cloud processing fail?**
A: Check API key, internet connection, cloud provider status, account credits, or try different provider.

---

## Support and Resources

### Documentation

- [README.md](README.md) - Project overview and quick start
- [ABOUT.md](ABOUT.md) - About MAGI and Douglas Trumbull
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick reference guide
- [GPU_AND_AI_USAGE.md](docs/GPU_AND_AI_USAGE.md) - GPU and AI usage guide
- [HYBRID_DEPLOYMENT.md](docs/HYBRID_DEPLOYMENT.md) - Hybrid deployment guide
- [PROJECTOR_COMPATIBILITY.md](docs/PROJECTOR_COMPATIBILITY.md) - Projector compatibility guide

### Community

- **GitHub Repository**: https://github.com/mondocosm/magi
- **Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Wiki**: Community-maintained documentation

### Additional Resources

- [MAGI File Format Specification](docs/MAGI_FILE_FORMAT_SPECIFICATION.md)
- [Hardware Requirements](docs/MINIMUM_HARDWARE_REQUIREMENTS.md)
- [Compatible Devices](docs/MAGI_COMPATIBLE_DEVICES.md)
- [Market Research](docs/research/MARKET_RESEARCH.md)
- [Competitor Analysis](docs/research/COMPETITOR_ANALYSIS.md)

---

## License

MAGI Pipeline is released under the MIT License. See LICENSE file for details.

---

## Credits

- **Douglas Trumbull** - Creator of MAGI format
- **MAGI Pipeline Team** - Software development
- **Open Source Community** - Contributions and support

---

*"The goal of MAGI is to create an experience that's so immersive, you forget you're watching a movie."* - Douglas Trumbull