# Native Apps Update - MAGI Viewer Changes

## Overview

This document describes the updates made to the native desktop applications to reflect the recent MAGI Viewer page changes.

## Changes Made

### 1. Desktop Launcher (`src/ui/desktop_launcher.py`)

Created a new desktop launcher that provides a native application experience while using the web UI:

**Features:**
- Automatic browser opening to the web UI
- Standalone operation as a native desktop application
- Full access to all MAGI Pipeline features
- Command-line options for customization

**Usage:**
```bash
python -m src.ui.desktop_launcher --host 127.0.0.1 --port 8000
python -m src.ui.desktop_launcher --no-browser  # Don't open browser
python -m src.ui.desktop_launcher --debug  # Enable debug mode
```

### 2. Build Script Updates (`build_desktop.py`)

Updated the build script to use the desktop launcher instead of the CLI:

**Nuitka Build:**
- Changed entry point from `src/cli.py` to `src/ui/desktop_launcher.py`

**PyInstaller Build:**
- Changed entry point from `src/cli.py` to `src/ui/desktop_launcher.py`
- Added hidden imports for web UI modules:
  - `src.ui.web_ui`
  - `src.ui.magi_viewer`
  - `src.ui.bino_integration`
  - `src.processing.frame_sync`

### 3. Documentation Updates

**BUILD_DESKTOP.md:**
- Added overview section describing the web-based desktop application
- Added desktop launcher section with usage instructions
- Updated output sections for Windows, macOS, and Linux to reflect web UI launch
- Added usage examples for each platform

**README.md:**
- Added MAGI Viewer to features list
- Added Frame Synchronization to features list
- Added Desktop Application to features list
- Added Desktop Application usage section
- Added MAGI Viewer usage section with feature list

## MAGI Viewer Features Included

The desktop application now includes all recent MAGI Viewer updates:

### Frame Info & Cadence Indicator
- Positioned above video window (not overlaying)
- Smaller text for cleaner appearance
- Real-time frame statistics display

### 3D Display Modes
- Shutter glasses (frame sequential)
- Anaglyph (Red-Cyan, Green-Magenta, Amber-Blue)
- Side-by-side
- Top-bottom
- Interleaved
- Checkerboard
- Autostereoscopic (glasses-free)
- VR headset

### Viewing Controls
- Eye swap toggle
- Parallax adjustment slider
- Aspect ratio selector (16:9, 4:3, 21:9, 1:1, Auto)

### Test Patterns
- Enhanced error handling
- Better logging
- Multiple test pattern types

### Frame Synchronization
- VSync support
- G-Sync detection and optimization
- FreeSync detection and optimization
- MAGI optimization mode for 120fps 3D playback

## Platform-Specific Changes

### Windows
- Executable: `dist/MAGI Pipeline.exe`
- Launches web UI at `http://127.0.0.1:8000`
- Opens browser automatically
- MAGI Viewer accessible at `http://127.0.0.1:8000/viewer/viewer`

### macOS
- App bundle: `dist/MAGI Pipeline.app`
- Launches web UI at `http://127.0.0.1:8000`
- Opens browser automatically
- MAGI Viewer accessible at `http://127.0.0.1:8000/viewer/viewer`

### Linux
- Executable: `dist/MAGI Pipeline`
- AppImage: `MAGI-Pipeline.AppImage`
- Launches web UI at `http://127.0.0.1:8000`
- Opens browser automatically
- MAGI Viewer accessible at `http://127.0.0.1:8000/viewer/viewer`

## Benefits

1. **Consistent Experience**: Desktop applications now provide the same features as the web UI
2. **Easy Updates**: Web UI changes automatically reflected in desktop apps
3. **Native Feel**: Desktop launcher provides native application experience
4. **Full Feature Set**: All MAGI Viewer features available in desktop apps
5. **Frame Synchronization**: Support for VSync, G-Sync, FreeSync in desktop apps

## Testing

To test the desktop application:

```bash
# Build the desktop application
python build_desktop.py --nuitka

# Run the built executable
./dist/MAGI\ Pipeline  # Linux/macOS
./dist/MAGI\ Pipeline.exe  # Windows

# Or run the desktop launcher directly
python -m src.ui.desktop_launcher
```

## Future Enhancements

Potential future improvements:
- Native window embedding (Electron-style)
- Offline mode support
- System tray integration
- Auto-update functionality
- Native notifications

## Conclusion

The native desktop applications have been successfully updated to reflect all recent MAGI Viewer changes, providing a consistent and feature-rich experience across all platforms.