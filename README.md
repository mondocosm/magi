# MAGI Pipeline

A comprehensive 3D video interpolation and upscaling pipeline that converts any video content to MAGI format - the high-frame-rate 3D cinema system invented by Douglas Trumbull.

## 🎬 What is MAGI?

MAGI is a high-frame-rate (HFR) 3D cinema system designed for maximum immersion:

- **Frame Rate**: 120 fps (60 fps per eye alternating)
- **Resolution**: 4K per eye (3840×2160)
- **Capture**: 100% action shooting at 120 fps
- **Cadence**: Left-Right alternating frames (L-R-L-R-L-R...)
- **Eye Separation**: 180° out of phase for 3D shutter glasses

## 🚀 Features

- **Video Conversion**: Convert any 2D or 3D video to MAGI format
- **Frame Rate Conversion**: Adaptive interpolation from any frame rate to 120 fps
- **Upscaling**: AI-powered upscaling to 4K resolution
- **2D to 3D**: StereoCrafter integration for converting 2D content to 3D
- **Real-time Processing**: Near real-time conversion with GPU acceleration
- **Game Capture**: Live game capture and conversion to MAGI
- **Camera Input**: Support for stereo cameras, depth cameras, and VR cameras
- **GPU Support**: NVIDIA CUDA, AMD ROCm, Apple Silicon Metal
- **Cloud Processing**: Optional cloud GPU integration
- **MAGI Viewer**: Built-in viewer with test patterns and 3D display modes
- **Frame Synchronization**: VSync, G-Sync, FreeSync support for smooth 120fps playback
- **Desktop Application**: Standalone executables for Windows, macOS, and Linux

## 📥 Download Executables

### Quick Download
1. Go to [GitHub Actions](https://github.com/mondocosm/magi/actions)
2. Click on the latest workflow run
3. Scroll down to "Artifacts" section
4. Download the executable for your platform

### Windows
- **Artifact**: `MAGI-Pipeline-Windows-Executable`
- **File**: `MAGI-Pipeline-Windows.exe`
- **Usage**: Double-click to run, web UI opens automatically

### macOS
- **Artifact**: `MAGI-Pipeline-macOS-Executable`
- **Files**: `MAGI Pipeline.app`, `MAGI-Pipeline.pkg`
- **Usage**: Double-click the app or install the package

### Linux
- **Artifact**: `MAGI-Pipeline-Linux-Executable`
- **Files**: `MAGI-Pipeline-Linux`, `MAGI-Pipeline.AppImage`
- **Usage**: `chmod +x MAGI-Pipeline-Linux && ./MAGI-Pipeline-Linux`

### All Platforms
- **Artifact**: `MAGI-Pipeline-All-Platforms`
- **Usage**: Contains executables for all platforms in one download

## 🛠️ Installation

### From Source
```bash
git clone https://github.com/mondocosm/magi.git
cd magi
pip install -r requirements.txt
python -m src.ui.web_ui
```

### Using Executable
Download the appropriate executable for your platform from GitHub Actions (see above).

## 📖 Usage

### Web Interface
1. Run the application
2. Open your browser to `http://localhost:8000`
3. Upload your video file
4. Configure settings (frame rate, resolution, 3D mode)
5. Click "Convert to MAGI"
6. Download the converted MAGI file

### Desktop Application
The desktop application launches the web UI automatically:
```bash
# Run the desktop launcher
python -m src.ui.desktop_launcher

# Or run the built executable
./MAGI\ Pipeline  # Linux/macOS
MAGI\ Pipeline.exe  # Windows
```

### MAGI Viewer
Access the MAGI Viewer at `http://localhost:8000/viewer/viewer`:
- Test patterns for 3D display calibration
- 3D display mode selection (shutter glasses, anaglyph, side-by-side, etc.)
- Eye swap and parallax adjustment
- Aspect ratio selector (16:9, 4:3, 21:9, 1:1, Auto)
- Frame synchronization controls (VSync, G-Sync, FreeSync)

### Command Line
```bash
python src/cli.py --input video.mp4 --output video.magi --fps 120 --resolution 3840x2160
```

### Game Capture
1. Select "Game Capture" mode
2. Choose your game window or screen
3. Configure capture settings
4. Start real-time conversion to MAGI

### Camera Input
1. Connect your stereo camera or depth camera
2. Select "Camera Input" mode
3. Choose your camera from the list
4. Configure capture settings
5. Start real-time conversion to MAGI

## 🔧 Configuration

### GPU Acceleration
The application automatically detects and uses available GPUs:
- **NVIDIA**: CUDA support
- **AMD**: ROCm support
- **Apple Silicon**: Metal support

### Cloud GPU
Configure cloud GPU endpoints in settings:
- RunPod
- Vast.ai
- Lambda Labs
- Custom endpoints

## 📚 Documentation

- [User Manual](USER_MANUAL.md) - Complete usage guide
- [About MAGI](ABOUT.md) - MAGI format specification and history
- [Build Guide](BUILD_DESKTOP.md) - Building from source
- [Desktop App Options](docs/DESKTOP_APP_OPTIONS.md) - Desktop application approaches

## 🎯 Supported Formats

### Input Formats
- **Video**: MP4, AVI, MKV, MOV, WebM
- **3D Formats**: Side-by-side (SBS), Top-bottom (TAB), Frame-sequential, Anaglyph
- **Frame Rates**: Any frame rate (24, 30, 60, etc.)
- **Resolutions**: Any resolution (up to 4K)

### Output Format
- **Container**: MP4 (Matroska MKV coming soon)
- **Codec**: HEVC H.265
- **Frame Rate**: 120 fps (60 fps per eye)
- **Resolution**: 4K per eye (3840×2160)
- **Cadence**: L-R alternating (left-right-left-right...)

## 🖥️ System Requirements

### Minimum
- **CPU**: 4-core processor
- **RAM**: 8 GB
- **GPU**: Integrated graphics or entry-level GPU
- **Storage**: 10 GB free space

### Recommended
- **CPU**: 8-core processor or better
- **RAM**: 16 GB or more
- **GPU**: NVIDIA RTX 3060 or better, AMD RX 6600 or better, Apple M1 or better
- **Storage**: 50 GB free space (SSD recommended)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Douglas Trumbull** - Inventor of the MAGI format
- **StereoCrafter** - 2D to 3D conversion
- **Bino3D** - 3D video player reference
- **Waifu2x** - AI upscaling reference

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the [User Manual](USER_MANUAL.md)
- Review the [FAQ](docs/FAQ.md)

## 🔗 Links

- [GitHub Repository](https://github.com/mondocosm/magi)
- [MAGI Format Specification](docs/MAGI_FORMAT_SPEC.md)
- [Display Compatibility Guide](docs/DISPLAY_COMPATIBILITY.md)

---

**MAGI Pipeline** - Converting the world to high-frame-rate 3D cinema 🎬✨
