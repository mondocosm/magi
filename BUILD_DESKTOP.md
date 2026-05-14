# Building MAGI Pipeline Desktop Applications

This guide explains how to build desktop application binaries for MAGI Pipeline on Windows, macOS, and Linux.

## Quick Start

```bash
# Build with Nuitka (recommended for performance)
python build_desktop.py --nuitka

# Or build with PyInstaller (faster build, slightly less performance)
python build_desktop.py
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
- `dist/MAGI Pipeline.exe` - Standalone executable
- `installer.exe` - Windows installer (if NSIS is installed)

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
- `dist/MAGI Pipeline.app` - macOS application bundle
- `MAGI-Pipeline.pkg` - macOS installer (if pkgbuild is available)

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
- `dist/MAGI Pipeline` - Linux executable
- `MAGI-Pipeline.AppImage` - AppImage (if appimagetool is installed)

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

You can set up GitHub Actions to automatically build desktop applications:

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
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install nuitka pyinstaller
          pip install -r requirements.txt
      
      - name: Build desktop app
        run: python build_desktop.py --nuitka
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: magi-pipeline-${{ matrix.os }}
          path: dist/
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/mondocosm/magi/issues
- Documentation: See USER_MANUAL.md
- Build Options: See docs/DESKTOP_APP_OPTIONS.md