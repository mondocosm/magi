# Platform-Specific Build Configurations

This directory contains platform-specific build configurations for MAGI Pipeline desktop applications.

## Overview

Each platform has its own YAML configuration file that defines:
- Build method (Nuitka or PyInstaller)
- Compiler settings
- Optimization flags
- Platform-specific features
- GPU support
- Camera support
- Game capture methods
- Package formats
- Dependencies
- Testing requirements
- Version tracking

## Configuration Files

### [`windows.yaml`](windows.yaml:1)
- **Platform**: Windows 10+
- **Build Method**: Nuitka (recommended) or PyInstaller
- **GPU Support**: CUDA (NVIDIA), DirectML (AMD)
- **Camera Support**: DirectShow, Media Foundation
- **Game Capture**: Desktop Duplication, Windows Graphics Capture
- **Package Format**: NSIS installer
- **Bundle Size**: 100-200 MB (Nuitka), 200-500 MB (PyInstaller)

### [`macos.yaml`](macos.yaml:1)
- **Platform**: macOS 10.15+ (Catalina)
- **Build Method**: Nuitka (recommended) or PyInstaller
- **GPU Support**: Metal (Apple Silicon), OpenGL (Intel)
- **Camera Support**: AVFoundation, QTKit
- **Game Capture**: ScreenCaptureKit, CGDisplayStream
- **Package Format**: App bundle (.app), PKG installer
- **Bundle Size**: 100-200 MB (Nuitka), 200-500 MB (PyInstaller)
- **Architectures**: Universal2, ARM64, x86_64

### [`linux.yaml`](linux.yaml:1)
- **Platform**: Linux (kernel 5.4+)
- **Build Method**: Nuitka (recommended) or PyInstaller
- **GPU Support**: CUDA, ROCm, Vulkan, OpenGL
- **Camera Support**: V4L2, libcamera
- **Game Capture**: X11, PipeWire, KMS
- **Package Formats**: AppImage, DEB, RPM, Arch PKGBUILD, tarball
- **Bundle Size**: 100-200 MB (Nuitka), 200-500 MB (PyInstaller)
- **Architectures**: x86_64, ARM64

## Using the Configurations

### Build for Current Platform

```bash
# Build using platform-specific configuration
python build_desktop.py --config build_configs/$(uname -s | tr '[:upper:]' '[:lower:]').yaml
```

### Build for Specific Platform

```bash
# Build for Windows
python build_desktop.py --config build_configs/windows.yaml

# Build for macOS
python build_desktop.py --config build_configs/macos.yaml

# Build for Linux
python build_desktop.py --config build_configs/linux.yaml
```

### Build with Nuitka (Recommended)

```bash
python build_desktop.py --nuitka --config build_configs/windows.yaml
```

### Build with PyInstaller (Fallback)

```bash
python build_desktop.py --config build_configs/windows.yaml
```

## Configuration Structure

Each configuration file follows this structure:

```yaml
# Build Method
build_method: nuitka  # or pyinstaller

# Nuitka Configuration
nuitka:
  compiler: gcc  # or clang, msvc
  lto: true  # Link-time optimization
  jobs: 4  # Parallel jobs
  # ... more settings

# PyInstaller Configuration (fallback)
pyinstaller:
  onefile: true
  console: false
  # ... more settings

# Platform-Specific Settings
windows:  # or macos, linux
  min_version: "10"
  gpu_support:
    - cuda
    - directml
  # ... more settings

# Performance Optimization
performance:
  gpu_acceleration: true
  cpu_optimization: true
  # ... more settings

# Dependencies
dependencies:
  python_version: "3.9"
  system:
    - "Microsoft Visual C++ Redistributable"
  python:
    - opencv-python
    - numpy
    # ... more dependencies

# Testing
testing:
  test_versions:
    - "Windows 10 (21H2)"
    - "Windows 11 (22H2)"
  # ... more settings

# Version Tracking
version:
  current: "0.1.0"
  config_version: "1.0.0"
  last_updated: "2024-01-01"
  # ... more settings
```

## Maintaining Configurations

### When to Update

Update configurations when:
1. **New Python version** is released
2. **New GPU drivers** are released
3. **New platform features** are added
4. **Dependencies change** (new versions, deprecations)
5. **Performance optimizations** are discovered
6. **Security vulnerabilities** are found
7. **Testing reveals issues** on specific platforms

### Update Process

1. **Check version compatibility**
   ```bash
   # Test new Python version
   python3.11 --version
   
   # Test new CUDA version
   nvcc --version
   ```

2. **Update configuration file**
   ```yaml
   # Update Python version
   python_version: "3.11"
   
   # Update CUDA version
   cuda_version: "12.1"
   
   # Update version tracking
   version:
     current: "0.1.1"
     last_updated: "2024-01-15"
   ```

3. **Test the build**
   ```bash
   python build_desktop.py --config build_configs/windows.yaml
   ```

4. **Test on target platform**
   - Run the built application
   - Test all features (video, game, camera)
   - Test on different hardware configurations
   - Verify performance benchmarks

5. **Update documentation**
   - Update BUILD_DESKTOP.md
   - Update compatibility matrix
   - Document any breaking changes

6. **Commit changes**
   ```bash
   git add build_configs/
   git commit -m "Update Windows build config for Python 3.11 and CUDA 12.1"
   ```

### Version Tracking

Each configuration tracks:
- **Current version**: Application version
- **Config version**: Configuration file version
- **Last updated**: Date of last update
- **Compatibility matrix**: Minimum/maximum versions for dependencies

Example:
```yaml
version:
  current: "0.1.0"
  config_version: "1.0.0"
  last_updated: "2024-01-01"
  
  compatibility:
    "0.1.0":
      python_min: "3.9"
      python_max: "3.11"
      cuda_min: "11.0"
      cuda_max: "12.1"
```

## Platform-Specific Considerations

### Windows

- **Compiler**: MSVC (recommended) or MinGW
- **GPU**: CUDA (NVIDIA) or DirectML (AMD)
- **Installer**: NSIS or Inno Setup
- **Code Signing**: Optional but recommended for distribution
- **Antivirus**: May flag executables (false positives)

### macOS

- **Compiler**: Clang (Xcode)
- **GPU**: Metal (Apple Silicon) or OpenGL (Intel)
- **Architectures**: Universal2, ARM64, x86_64
- **Code Signing**: Required for distribution
- **Notarization**: Required for macOS 10.15+
- **App Store**: Optional (requires additional setup)

### Linux

- **Compiler**: GCC or Clang
- **GPU**: CUDA, ROCm, Vulkan, OpenGL
- **Package Formats**: AppImage, DEB, RPM, PKGBUILD
- **Distributions**: Ubuntu, Debian, Fedora, Arch, etc.
- **Desktop Environments**: GNOME, KDE, Xfce, Wayland, X11
- **Dependencies**: Varies by distribution

## Performance Optimization

### Nuitka Optimizations

```yaml
nuitka:
  lto: true  # Link-time optimization
  jobs: 4  # Use multiple cores
  follow_imports: true  # Include all imports
  # ... more optimizations
```

### Platform-Specific Optimizations

```yaml
performance:
  gpu_acceleration: true
  cpu_optimization: true
  memory_optimization: true
  
  # SIMD instructions
  simd:
    - "AVX2"
    - "AVX-512"
    - "NEON"  # ARM
```

## Testing

### Automated Testing

Each configuration includes testing requirements:

```yaml
testing:
  test_versions:
    - "Windows 10 (21H2)"
    - "Windows 11 (22H2)"
  
  test_gpus:
    - "NVIDIA GTX 1660 SUPER"
    - "NVIDIA RTX 3060"
    - "AMD RX 6800 XT"
```

### Manual Testing Checklist

- [ ] Application launches successfully
- [ ] Video processing works
- [ ] Game capture works
- [ ] Camera input works
- [ ] GPU acceleration is detected
- [ ] Performance is acceptable
- [ ] No crashes or errors
- [ ] UI renders correctly
- [ ] File associations work
- [ ] Installer/uninstaller work

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/build-desktop.yml
name: Build Desktop Apps

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
    
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Build desktop app
        run: |
          python build_desktop.py \
            --config build_configs/${{ matrix.os }}.yaml \
            --nuitka
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: magi-pipeline-${{ matrix.os }}
          path: dist/
```

## Troubleshooting

### Build Fails

1. **Check compiler is installed**
   ```bash
   gcc --version  # Linux
   clang --version  # macOS
   cl  # Windows (MSVC)
   ```

2. **Check Python version**
   ```bash
   python --version
   ```

3. **Check dependencies**
   ```bash
   pip list
   ```

4. **Check configuration syntax**
   ```bash
   python -c "import yaml; yaml.safe_load(open('build_configs/windows.yaml'))"
   ```

### Application Crashes

1. **Check GPU drivers**
   ```bash
   nvidia-smi  # NVIDIA
   rocm-smi  # AMD
   ```

2. **Check dependencies**
   ```bash
   ldd ./dist/MAGI\ Pipeline  # Linux
   otool -L ./dist/MAGI\ Pipeline.app  # macOS
   ```

3. **Check logs**
   ```bash
   ./dist/MAGI\ Pipeline --debug
   ```

## Contributing

When adding new features or fixing bugs:

1. **Update all platform configurations**
2. **Test on all platforms**
3. **Update version tracking**
4. **Document changes**
5. **Update CI/CD if needed**

## Resources

- [Nuitka Documentation](https://nuitka.net/doc/user-manual.html)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [BUILD_DESKTOP.md](../BUILD_DESKTOP.md)
- [docs/DESKTOP_APP_OPTIONS.md](../docs/DESKTOP_APP_OPTIONS.md)

## Support

For issues or questions:
- GitHub Issues: https://github.com/mondocosm/magi/issues
- Documentation: See BUILD_DESKTOP.md
- Platform-specific: See respective configuration file