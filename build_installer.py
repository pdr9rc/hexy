#!/usr/bin/env python3
"""
Build script for The Dying Lands - Hexcrawl Generator
Creates installers for different platforms
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Success: {result.stdout}")
    return True

def install_build_requirements():
    """Install build requirements."""
    requirements = [
        "pyinstaller>=5.0.0",
        "setuptools>=60.0.0",
        "wheel>=0.37.0",
    ]
    
    for req in requirements:
        if not run_command([sys.executable, "-m", "pip", "install", req]):
            return False
    return True

def build_executable():
    """Build the executable using PyInstaller."""
    print("\n=== Building executable ===")
    
    # Clean previous builds
    dist_dir = Path("dist")
    build_dir = Path("build")
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Build with PyInstaller
    cmd = [sys.executable, "-m", "PyInstaller", "dying_lands.spec"]
    if not run_command(cmd):
        return False
    
    return True

def create_installer():
    """Create installer packages for different platforms."""
    system = platform.system().lower()
    
    print(f"\n=== Creating installer for {system} ===")
    
    if system == "windows":
        return create_windows_installer()
    elif system == "darwin":
        return create_macos_installer()
    elif system == "linux":
        return create_linux_installer()
    else:
        print(f"Unsupported platform: {system}")
        return False

def create_windows_installer():
    """Create Windows installer using NSIS or create a zip file."""
    print("Creating Windows installer...")
    
    # Check if NSIS is available
    try:
        subprocess.run(["makensis", "/VERSION"], capture_output=True, check=True)
        nsis_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        nsis_available = False
    
    if nsis_available:
        # Create NSIS script
        nsis_script = create_nsis_script()
        with open("installer.nsi", "w") as f:
            f.write(nsis_script)
        
        # Build installer
        return run_command(["makensis", "installer.nsi"])
    else:
        # Create zip file
        print("NSIS not found, creating zip file...")
        import zipfile
        
        with zipfile.ZipFile("DyingLands-Windows.zip", "w", zipfile.ZIP_DEFLATED) as zf:
            exe_path = Path("dist/DyingLands.exe")
            if exe_path.exists():
                zf.write(exe_path, "DyingLands.exe")
                zf.write("README.md", "README.md")
                print("Windows zip package created: DyingLands-Windows.zip")
                return True
        return False

def create_macos_installer():
    """Create macOS installer (.dmg file)."""
    print("Creating macOS installer...")
    
    app_path = Path("dist/DyingLands.app")
    if not app_path.exists():
        print("Error: DyingLands.app not found")
        return False
    
    # Create DMG using hdiutil
    dmg_name = "DyingLands-macOS.dmg"
    cmd = [
        "hdiutil", "create", "-volname", "The Dying Lands",
        "-srcfolder", "dist", "-ov", "-format", "UDZO", dmg_name
    ]
    
    if run_command(cmd):
        print(f"macOS installer created: {dmg_name}")
        return True
    return False

def create_linux_installer():
    """Create Linux installer (AppImage or tar.gz)."""
    print("Creating Linux installer...")
    
    exe_path = Path("dist/DyingLands")
    if not exe_path.exists():
        print("Error: DyingLands executable not found")
        return False
    
    # Create tar.gz file
    import tarfile
    
    with tarfile.open("DyingLands-Linux.tar.gz", "w:gz") as tar:
        tar.add("dist/DyingLands", "DyingLands")
        tar.add("README.md", "README.md")
        
        # Create a simple run script
        run_script = """#!/bin/bash
cd "$(dirname "$0")"
./DyingLands
"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(run_script)
            f.flush()
            os.chmod(f.name, 0o755)
            tar.add(f.name, "run.sh")
        
        os.unlink(f.name)
    
    print("Linux installer created: DyingLands-Linux.tar.gz")
    return True

def create_nsis_script():
    """Create NSIS installer script for Windows."""
    return """
!define APPNAME "The Dying Lands"
!define COMPANYNAME "Mork Borg Hexcrawl Generator"
!define DESCRIPTION "Desktop application for generating hexcrawl maps"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0

RequestExecutionLevel admin

InstallDir "$PROGRAMFILES\\${APPNAME}"
Name "${APPNAME}"
outFile "DyingLands-Setup.exe"

Page directory
Page instfiles

Section "install"
    SetOutPath $INSTDIR
    File "dist\\DyingLands.exe"
    File "README.md"
    
    # Create uninstaller
    WriteUninstaller "$INSTDIR\\uninstall.exe"
    
    # Create start menu entry
    CreateDirectory "$SMPROGRAMS\\${APPNAME}"
    CreateShortcut "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk" "$INSTDIR\\DyingLands.exe"
    CreateShortcut "$SMPROGRAMS\\${APPNAME}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
    
    # Create desktop shortcut
    CreateShortcut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\DyingLands.exe"
    
    # Registry information for add/remove programs
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayIcon" "$INSTDIR\\DyingLands.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "NoRepair" 1
SectionEnd

Section "uninstall"
    Delete "$INSTDIR\\DyingLands.exe"
    Delete "$INSTDIR\\README.md"
    Delete "$INSTDIR\\uninstall.exe"
    RMDir "$INSTDIR"
    
    Delete "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\\${APPNAME}\\Uninstall.lnk"
    RMDir "$SMPROGRAMS\\${APPNAME}"
    
    Delete "$DESKTOP\\${APPNAME}.lnk"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}"
SectionEnd
"""

def main():
    """Main build process."""
    print("=== The Dying Lands - Build Script ===")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    
    # Install build requirements
    print("\n=== Installing build requirements ===")
    if not install_build_requirements():
        print("Failed to install build requirements")
        sys.exit(1)
    
    # Build executable
    if not build_executable():
        print("Failed to build executable")
        sys.exit(1)
    
    # Create installer
    if not create_installer():
        print("Failed to create installer")
        sys.exit(1)
    
    print("\n=== Build completed successfully! ===")
    print("Files created:")
    
    # List created files
    for file in Path(".").glob("DyingLands*"):
        if file.is_file():
            print(f"  - {file}")
    
    print("\nTo distribute your application:")
    print("1. Share the installer file with your users")
    print("2. Users can run the installer to install the application")
    print("3. The application will appear in their Start Menu/Applications folder")

if __name__ == "__main__":
    main()