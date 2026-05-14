#!/usr/bin/env python3
"""
Build script for MAGI Pipeline desktop applications
Uses Nuitka for performance optimization and PyInstaller for bundling
Supports platform-specific YAML configurations
"""

import os
import sys
import subprocess
import platform
import argparse
import yaml
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True


def load_config(config_path):
    """Load platform-specific configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Configuration file not found: {config_path}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing configuration file: {e}")
        return None


def get_platform_config():
    """Get configuration for current platform"""
    system = platform.system()
    
    # Map system names to config files
    config_map = {
        'Windows': 'build_configs/windows.yaml',
        'Darwin': 'build_configs/macos.yaml',
        'Linux': 'build_configs/linux.yaml',
    }
    
    config_path = config_map.get(system)
    if config_path and Path(config_path).exists():
        return load_config(config_path)
    
    return None


def install_dependencies(config=None):
    """Install required build dependencies"""
    print("Installing build dependencies...")
    
    dependencies = [
        "nuitka",
        "pyinstaller",
        "ordered-set",
        "zstandard",
        "pyyaml",  # For reading config files
    ]
    
    # Add platform-specific dependencies from config
    if config and 'dependencies' in config:
        if 'python' in config['dependencies']:
            dependencies.extend(config['dependencies']['python'])
    
    for dep in dependencies:
        if not run_command([sys.executable, "-m", "pip", "install", dep]):
            print(f"Failed to install {dep}")
            return False
    
    return True


def build_with_nuitka(config=None):
    """Build using Nuitka for performance optimization"""
    print("Building with Nuitka for performance optimization...")
    
    # Determine platform-specific settings
    system = platform.system()
    
    # Base Nuitka command
    cmd = [
        sys.executable, "-m", "nuitka",
        "--enable-plugin=pylint-warnings",
        "--follow-imports",
        "--output-dir=dist",
        "src/cli.py",
    ]
    
    # Use config settings if available
    if config and 'nuitka' in config:
        nuitka_config = config['nuitka']
        
        # Compiler settings
        if 'compiler' in nuitka_config:
            compiler = nuitka_config['compiler']
            if system == "Linux" and compiler == "gcc":
                cmd.extend(["--clang=no"])
            elif system == "Linux" and compiler == "clang":
                cmd.extend(["--clang=yes"])
        
        # Output settings
        if nuitka_config.get('standalone', True):
            cmd.append("--standalone")
        
        if nuitka_config.get('onefile', True):
            cmd.append("--onefile")
        else:
            cmd.append("--onefile=no")
        
        # Optimization
        if nuitka_config.get('lto', True):
            cmd.append("--lto=yes")
        
        if 'jobs' in nuitka_config:
            cmd.extend(["--jobs", str(nuitka_config['jobs'])])
        
        # Include modules
        if 'include_modules' in nuitka_config:
            for module in nuitka_config['include_modules']:
                cmd.extend(["--include-module", module])
        
        # Include data directories
        if 'include_data_dirs' in nuitka_config:
            for data_dir in nuitka_config['include_data_dirs']:
                cmd.extend(["--include-data-dir", data_dir])
        
        # Exclude modules
        if 'exclude_modules' in nuitka_config:
            for module in nuitka_config['exclude_modules']:
                cmd.extend(["--nofollow-import-to", module])
    
    # Platform-specific settings
    if system == "Windows":
        cmd.extend([
            "--windows-console-mode=disable",
            "--windows-icon-from-ico=src/ui/static/magi-icon.ico",
        ])
    elif system == "Darwin":  # macOS
        cmd.append("--macos-create-app-bundle")
        cmd.extend(["--macos-app-icon=src/ui/static/magi-icon.icns"])
    elif system == "Linux":
        cmd.extend(["--linux-onefile-icon=src/ui/static/magi-icon.png"])
    
    return run_command(cmd)


def build_with_pyinstaller(config=None):
    """Build using PyInstaller (fallback)"""
    print("Building with PyInstaller...")
    
    # Create spec file
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/cli.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/ui/static', 'src/ui/static'),
        ('config', 'config'),
    ],
    hiddenimports=[
        'cv2',
        'numpy',
        'fastapi',
        'uvicorn',
        'pydantic',
        'src.pipeline.controller',
        'src.input.video_input',
        'src.processing.interpolation',
        'src.processing.upscaling',
        'src.processing.frame_cadence',
        'src.output.magi_encoder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'pandas',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MAGI Pipeline',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    
    # Write spec file
    with open("magi_pipeline.spec", "w") as f:
        f.write(spec_content)
    
    # Build with PyInstaller
    return run_command([sys.executable, "-m", "PyInstaller", "magi_pipeline.spec"])


def create_installer():
    """Create platform-specific installer"""
    system = platform.system()
    
    if system == "Windows":
        create_windows_installer()
    elif system == "Darwin":
        create_macos_installer()
    elif system == "Linux":
        create_linux_installer()


def create_windows_installer():
    """Create Windows installer using NSIS"""
    print("Creating Windows installer...")
    
    # Create NSIS script
    nsis_script = """
!define APPNAME "MAGI Pipeline"
!define COMPANYNAME "MAGI Project"
!define DESCRIPTION "Convert videos to MAGI format - 120fps 4K 3D"
!define HELPURL "https://github.com/mondocosm/magi"
!define UPDATEURL "https://github.com/mondocosm/magi"
!define ABOUTURL "https://github.com/mondocosm/magi"
!define INSTALLSIZE 500000

RequestExecutionLevel admin

InstallDir "$PROGRAMFILES\\${APPNAME}"

Page directory
Page instfiles

Section "install"
    SetOutPath $INSTDIR
    File /r "dist\\MAGI Pipeline.exe"
    File /r "src\\ui\\static"
    File /r "config"
    
    WriteUninstaller "$INSTDIR\\uninstall.exe"
    
    CreateDirectory "$SMPROGRAMS\\${APPNAME}"
    CreateShortcut "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk" "$INSTDIR\\MAGI Pipeline.exe"
    CreateShortcut "$SMPROGRAMS\\${APPNAME}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
SectionEnd

Section "uninstall"
    Delete $INSTDIR\\MAGI Pipeline.exe
    Delete $INSTDIR\\uninstall.exe
    RMDir /r "$INSTDIR"
    
    Delete "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\\${APPNAME}\\Uninstall.lnk"
    RMDir "$SMPROGRAMS\\${APPNAME}"
SectionEnd
"""
    
    with open("installer.nsi", "w") as f:
        f.write(nsis_script)
    
    # Build installer (requires NSIS)
    if run_command(["makensis", "installer.nsi"]):
        print("Windows installer created successfully")
    else:
        print("NSIS not found. Skipping installer creation.")


def create_macos_installer():
    """Create macOS installer using pkgbuild"""
    print("Creating macOS installer...")
    
    # Check if pkgbuild is available
    if not run_command(["which", "pkgbuild"]):
        print("pkgbuild not found. Skipping installer creation.")
        return
    
    # Create app bundle if it doesn't exist
    app_path = Path("dist/MAGI Pipeline.app")
    if not app_path.exists():
        print("App bundle not found. Skipping installer creation.")
        return
    
    # Build package
    run_command([
        "pkgbuild",
        "--component", str(app_path),
        "--install-location", "/Applications",
        "MAGI-Pipeline.pkg"
    ])


def create_linux_installer():
    """Create Linux installer using AppImage"""
    print("Creating Linux AppImage...")
    
    # Create AppDir structure
    appdir = Path("MAGI-Pipeline.AppDir")
    appdir.mkdir(exist_ok=True)
    
    # Copy executable
    exe_path = Path("dist/MAGI Pipeline")
    if exe_path.exists():
        import shutil
        shutil.copy(exe_path, appdir / "AppRun")
        os.chmod(appdir / "AppRun", 0o755)
    
    # Create desktop file
    desktop_content = """
[Desktop Entry]
Name=MAGI Pipeline
Comment=Convert videos to MAGI format - 120fps 4K 3D
Exec=AppRun
Icon=icon
Terminal=false
Type=Application
Categories=AudioVideo;Video;
"""
    
    with open(appdir / "MAGI-Pipeline.desktop", "w") as f:
        f.write(desktop_content)
    
    # Copy icon
    icon_src = Path("src/ui/static/magi-icon.png")
    if icon_src.exists():
        import shutil
        shutil.copy(icon_src, appdir / "icon.png")
    
    # Create AppImage (requires appimagetool)
    if run_command(["which", "appimagetool"]):
        run_command(["appimagetool", str(appdir)])
    else:
        print("appimagetool not found. Skipping AppImage creation.")


def main():
    """Main build function"""
    parser = argparse.ArgumentParser(description='Build MAGI Pipeline desktop applications')
    parser.add_argument('--config', '-c', help='Path to platform-specific config file')
    parser.add_argument('--nuitka', '-n', action='store_true', help='Use Nuitka for performance optimization')
    parser.add_argument('--pyinstaller', '-p', action='store_true', help='Use PyInstaller')
    parser.add_argument('--platform', help='Target platform (windows, macos, linux)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("MAGI Pipeline Desktop Application Builder")
    print("=" * 60)
    print()
    
    # Load configuration
    config = None
    if args.config:
        config = load_config(args.config)
    else:
        config = get_platform_config()
    
    if config:
        print(f"Using configuration: {config.get('build_method', 'nuitka')}")
        print(f"Platform: {platform.system()}")
        print()
    
    # Determine build method
    use_nuitka = args.nuitka or (not args.pyinstaller and (config and config.get('build_method') == 'nuitka'))
    
    # Install dependencies
    if not install_dependencies(config):
        print("Failed to install dependencies")
        return 1
    
    # Build
    if use_nuitka:
        if not build_with_nuitka(config):
            print("Nuitka build failed, trying PyInstaller...")
            if not build_with_pyinstaller(config):
                print("Build failed")
                return 1
    else:
        if not build_with_pyinstaller(config):
            print("Build failed")
            return 1
    
    # Create installer
    create_installer()
    
    print()
    print("=" * 60)
    print("Build completed successfully!")
    print("=" * 60)
    print()
    print("Output files:")
    print("  - Executable: dist/")
    print("  - Installer: ./")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())