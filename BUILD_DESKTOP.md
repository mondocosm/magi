# Building MAGI Pipeline Desktop Applications

This guide explains how to build desktop application binaries for MAGI Pipeline on Windows, macOS, and Linux.

## Overview

MAGI Pipeline provides a web-based desktop application that launches the web UI in a browser or native window. The desktop application includes all recent MAGI Viewer updates:

- **Frame Info & Cadence Indicator**: Positioned above video window with smaller text
- **MAGI Logo**: Consistent branding across all pages
- **3D Display Modes**: Shutter glasses, anaglyph (Red-Cyan, Green-Magenta, Amber-Blue), side-by-side, top-bottom, interleaved, checkerboard, autostereoscopic (glasses-free), VR headset
- **Eye Swap & Parallax Adjustment**: Fine-tune 3D viewing experience
- **Aspect Ratio Selector**: 16:9, 4:3, 21:9, 1:1, Auto
- **Enhanced Test Patterns**: Better error handling and logging
- **Frame Synchronization**: VSync, G-Sync, FreeSync support for smooth 120fps playback

## Quick Start

```bash
# Build with Nuitka (recommended for performance)
python build_desktop.py --nuitka

# Or build with PyInstaller (faster build, slightly less performance)
python build_desktop.py
```

## Desktop Launcher

The desktop application uses [`src/ui/desktop_launcher.py`](src/ui/desktop_launcher.py) to launch the web UI. This provides:

- **Automatic browser opening**: Launches the web UI in your default browser
- **Standalone operation**: Runs as a native desktop application
- **Web UI access**: Full access to all MAGI Pipeline features including:
  - Video processing pipeline
  - MAGI Viewer with test patterns
  - Frame synchronization controls
  - 3D display mode options
  - Real-time statistics

**Command-line options:**
```bash
python -m src.ui.desktop_launcher --host 127.0.0.1 --port 8000
python -m src.ui.desktop_launcher --no-browser  # Don't open browser
python -m src.ui.desktop_launcher --debug  # Enable debug mode
```

## Build Methods

### Method 1: Nuitka (Recommended)

**Pros:**
- Compiles Python to C for better performance
- Smaller bundle size (~100-200 MB)
- Faster execution
- Better optimization

**Cons:**
- Longer build time
- Requires C compiler

**Usage:**
```bash
python build_desktop.py --nuitka
```

### Method 2: PyInstaller

**Pros:**
- Faster build time
- No C compiler required
- Well-tested and reliable

**Cons:**
- Larger bundle size (~200-500 MB)
- Slightly slower execution
- Slower startup

**Usage:**
```bash
python build_desktop.py
```

## Platform-Specific Requirements

### Windows

**Required:**
- Python 3.8+
- Microsoft Visual C++ Build Tools
- (Optional) NSIS for creating installers

**Install Visual C++ Build Tools:**
```bash
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Select "Desktop development with C++"
```

**Build:**
```bash
python build_desktop.py --nuitka
```

**Output:**
- `dist/MAGI Pipeline.exe` - Standalone executable (launches web UI)
- `installer.exe` - Windows installer (if NSIS is installed)

**Usage:**
```bash
# Run the desktop application
./dist/MAGI\ Pipeline.exe

# The web UI will open in your default browser at http://127.0.0.1:8000
# Access MAGI Viewer at http://127.0.0.1:8000/viewer/viewer
```

### macOS

**Required:**
- Python 3.8+
- Xcode Command Line Tools
- (Optional) pkgbuild for creating installers

**Install Xcode Command Line Tools:**
```bash
xcode-select --install
```

**Build:**
```bash
python build_desktop.py --nuitka
```

**Output:**
- `dist/MAGI Pipeline.app` - macOS application bundle (launches web UI)
- `MAGI-Pipeline.pkg` - macOS installer (if pkgbuild is available)

**Usage:**
```bash
# Run the desktop application
open dist/MAGI\ Pipeline.app

# The web UI will open in your default browser at http://127.0.0.1:8000
# Access MAGI Viewer at http://127.0.0.1:8000/viewer/viewer
```

### Linux

**Required:**
- Python 3.8+
- GCC compiler
- (Optional) appimagetool for creating AppImages

**Install GCC:**
```bash
# Ubuntu/Debian
sudo apt-get install build-essential

# Fedora/RHEL
sudo dnf install gcc gcc-c++

# Arch Linux
sudo pacman -S base-devel
```

**Build:**
```bash
python build_desktop.py --nuitka
```

**Output:**
- `dist/MAGI Pipeline` - Linux executable (launches web UI)
- `MAGI-Pipeline.AppImage` - AppImage (if appimagetool is installed)

**Usage:**
```bash
# Run the desktop application
./dist/MAGI\ Pipeline

# The web UI will open in your default browser at http://127.0.0.1:8000
# Access MAGI Viewer at http://127.0.0.1:8000/viewer/viewer

# Or run the AppImage
./MAGI-Pipeline.AppImage
```

## Advanced Options

### Custom Build Configuration

You can modify `build_desktop.py` to customize the build:

```python
# Change optimization level
cmd.extend(["--lto=yes"])  # Link-time optimization

# Change number of parallel jobs
cmd.extend(["--jobs=8"])  # Use 8 parallel jobs

# Add additional data files
cmd.extend(["--include-data-dir=path/to/data=path/to/data"])
```

### Building for Multiple Platforms

To build for multiple platforms, you'll need to run the build script on each platform:

```bash
# On Windows
python build_desktop.py --nuitka

# On macOS
python build_desktop.py --nuitka

# On Linux
python build_desktop.py --nuitka
```

### Cross-Compilation

Cross-compilation is complex and not recommended. It's better to build on each target platform.

## Troubleshooting

### Build Fails with "Compiler not found"

**Solution:** Install the required C compiler for your platform (see Platform-Specific Requirements above).

### Build Fails with "Module not found"

**Solution:** Install the missing module:
```bash
pip install <module_name>
```

### Executable is Too Large

**Solution:** 
1. Use Nuitka instead of PyInstaller
2. Exclude unnecessary modules in the build script
3. Use UPX compression (enabled by default)

### Executable Runs Slowly

**Solution:**
1. Use Nuitka for better performance
2. Enable link-time optimization (`--lto=yes`)
3. Increase number of parallel jobs (`--jobs=8`)

### Antivirus Flags Executable

**Solution:** This is a false positive. You can:
1. Add the executable to antivirus exclusions
2. Sign the executable with a code signing certificate
3. Submit to antivirus vendors for whitelisting

## Performance Comparison

| Method | Build Time | Bundle Size | Startup Time | Execution Speed |
|--------|------------|-------------|--------------|-----------------|
| Nuitka | 10-20 min | 100-200 MB | Fast | Fastest |
| PyInstaller | 2-5 min | 200-500 MB | Medium | Fast |

## Distribution

### Windows

1. Upload `installer.exe` to GitHub Releases
2. Users download and run the installer
3. Application is installed to Program Files

### macOS

1. Upload `MAGI-Pipeline.pkg` to GitHub Releases
2. Users download and open the package
3. Application is installed to Applications folder

### Linux

1. Upload `MAGI-Pipeline.AppImage` to GitHub Releases
2. Users download and make executable:
   ```bash
   chmod +x MAGI-Pipeline.AppImage
   ./MAGI-Pipeline.AppImage
   ```

## Automated Builds

GitHub Actions workflows are set up to automatically build desktop applications:

### Available Workflows

1. **Build Windows Executable** - Builds Windows executable
2. **Build macOS Executable** - Builds macOS app bundle and package
3. **Build Linux Executable** - Builds Linux binary and AppImage
4. **Build All Platforms** - Builds all platforms in one workflow

### Downloading Executables

1. Go to [GitHub Actions](https://github.com/mondocosm/magi/actions)
2. Click on the latest workflow run
3. Scroll down to the **Artifacts** section
4. Download the executable for your platform

### Artifact Names

- **Windows**: `MAGI-Pipeline-Windows-Executable`
- **macOS**: `MAGI-Pipeline-macOS-Executable`
- **Linux**: `MAGI-Pipeline-Linux-Executable`
- **All Platforms**: `MAGI-Pipeline-All-Platforms`

### Workflow Triggers

- **Automatic**: Runs on push to `master` or `main` branches
- **Manual**: Can be triggered manually from the Actions tab
- **Releases**: Creates GitHub releases when tags are pushed (v*)

## Support

For issues or questions:
- GitHub Issues: https://github.com/mondocosm/magi/issues
- Documentation: See USER_MANUAL.md
- Build Options: See docs/DESKTOP_APP_OPTIONS.md