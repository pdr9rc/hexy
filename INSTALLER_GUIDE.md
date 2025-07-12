# The Dying Lands - Installer Creation Guide

This guide explains how to package The Dying Lands Hexcrawl Generator as a standalone desktop application with installer.

## 🎯 Overview

The application can be packaged as a standalone executable that launches in a WebView window, eliminating the need for users to:
- Install Python
- Install dependencies
- Open a web browser
- Remember localhost URLs

## 📋 Prerequisites

### For Development/Building
- Python 3.7+ installed
- Git (for cloning the repository)
- Platform-specific tools (see below)

### Platform-Specific Requirements

#### Windows
- **NSIS** (Nullsoft Scriptable Install System) - optional but recommended
  - Download from: https://nsis.sourceforge.io/
  - Used to create professional Windows installers

#### macOS
- **Xcode Command Line Tools** (for hdiutil)
  ```bash
  xcode-select --install
  ```

#### Linux
- **Build tools** (usually pre-installed)
  ```bash
  sudo apt-get install build-essential  # Ubuntu/Debian
  ```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Install the application requirements
pip install -r requirements.txt

# Install additional build requirements
pip install pyinstaller>=5.0.0 setuptools>=60.0.0 wheel>=0.37.0
```

### 2. Build the Installer
```bash
# One-command build (recommended)
python build_installer.py

# Or build step-by-step
python -m PyInstaller dying_lands.spec
```

### 3. Test the Application
```bash
# Test the WebView launcher directly
python src/webview_launcher.py

# Test the built executable
./dist/DyingLands  # Linux/macOS
./dist/DyingLands.exe  # Windows
```

## 📦 Build Process Details

### What Gets Built

1. **Executable**: A standalone executable that contains:
   - Python interpreter
   - All dependencies (Flask, pywebview, etc.)
   - Your application code
   - Web templates and static files
   - Data files

2. **Installer**: Platform-specific installer that:
   - Installs the application
   - Creates start menu/desktop shortcuts
   - Registers uninstall information
   - Handles file associations

### Build Files Created

- `dist/DyingLands` or `dist/DyingLands.exe` - The main executable
- `DyingLands-Windows.zip` or `DyingLands-Setup.exe` - Windows installer
- `DyingLands-macOS.dmg` - macOS installer
- `DyingLands-Linux.tar.gz` - Linux installer

## 🔧 Configuration Options

### WebView Window Settings
Edit `src/webview_launcher.py` to customize:

```python
window_config = {
    'title': 'The Dying Lands - Hexcrawl Generator',
    'width': 1200,           # Window width
    'height': 800,           # Window height
    'min_size': (800, 600),  # Minimum window size
    'resizable': True,       # Allow resizing
    'fullscreen': False,     # Start fullscreen
    'on_top': False,         # Always on top
}
```

### PyInstaller Options
Edit `dying_lands.spec` to customize:

```python
exe = EXE(
    # ... other options ...
    console=False,           # False = GUI app, True = console app
    icon='icon.ico',         # Add application icon
    name='DyingLands',       # Executable name
)
```

## 🎨 Adding an Application Icon

### 1. Create Icon Files
- **Windows**: Create `icon.ico` (16x16, 32x32, 48x48, 256x256)
- **macOS**: Create `icon.icns` (multiple sizes)
- **Linux**: Create `icon.png` (256x256 or 512x512)

### 2. Update Configuration
In `dying_lands.spec`:
```python
exe = EXE(
    # ... other options ...
    icon='icon.ico',  # Windows
)

# For macOS
app = BUNDLE(
    exe,
    name='DyingLands.app',
    icon='icon.icns',  # macOS
)
```

## 🔀 Alternative Packaging Methods

### 1. Simple Zip Distribution
```bash
# Create a portable zip file
python -m PyInstaller dying_lands.spec
cd dist
zip -r DyingLands-Portable.zip DyingLands* README.md
```

### 2. Python Package Installation
```bash
# Install as a Python package
pip install -e .

# Run from anywhere
dying-lands
```

### 3. Docker Container
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "src/webview_launcher.py"]
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. WebView Won't Start
```bash
# Install system WebView dependencies
# Ubuntu/Debian:
sudo apt-get install python3-gi python3-gi-cairo gir1.2-webkit2-4.0

# CentOS/RHEL:
sudo yum install python3-gobject python3-gobject-devel webkit2gtk3-devel
```

#### 2. PyInstaller Import Errors
Add missing modules to `dying_lands.spec`:
```python
hiddenimports = [
    'flask',
    'webview',
    'your_missing_module',
]
```

#### 3. Missing Web Files
Ensure templates and static files are included:
```python
datas = [
    ('web/templates', 'web/templates'),
    ('web/static', 'web/static'),
]
```

#### 4. Port Already in Use
The application will try different ports if 5000 is busy:
```python
# Edit src/webview_launcher.py
self.port = 5001  # Change default port
```

### Build Issues

#### Windows
- Install Microsoft Visual C++ Redistributable if needed
- Use Administrator privileges for NSIS installer creation

#### macOS
- Code signing: Add your Developer ID to the spec file
- Notarization: Use `xcrun altool` for App Store distribution

#### Linux
- Install missing system libraries
- Use `ldd` to check executable dependencies

## 📊 Performance Optimization

### Reduce File Size
1. **Exclude unnecessary modules**:
```python
excludes = ['matplotlib', 'scipy', 'numpy']  # If not needed
```

2. **Use UPX compression**:
```python
upx=True,  # Enable UPX compression
```

3. **One-file vs One-folder**:
```python
# One file (slower startup, smaller distribution)
onefile=True,

# One folder (faster startup, larger distribution)
onefile=False,
```

### Improve Startup Time
1. **Lazy imports**: Import modules only when needed
2. **Preload**: Start Flask server before WebView
3. **Splash screen**: Add loading screen for better UX

## 🚀 Distribution

### Upload to GitHub Releases
```bash
# Create release files
python build_installer.py

# Upload to GitHub Releases
# - DyingLands-Windows.zip or DyingLands-Setup.exe
# - DyingLands-macOS.dmg  
# - DyingLands-Linux.tar.gz
```

### Distribution Checklist
- [ ] Test on clean systems (no Python installed)
- [ ] Verify all features work offline
- [ ] Check file permissions (executable files)
- [ ] Test installation and uninstallation
- [ ] Verify shortcuts are created correctly
- [ ] Test with antivirus software
- [ ] Create installation instructions for users

## 📄 User Installation Instructions

### Windows
1. Download `DyingLands-Setup.exe`
2. Run the installer (may need Administrator privileges)
3. Follow installation wizard
4. Launch from Start Menu or Desktop shortcut

### macOS
1. Download `DyingLands-macOS.dmg`
2. Open the DMG file
3. Drag "DyingLands" to Applications folder
4. Launch from Applications or Spotlight

### Linux
1. Download `DyingLands-Linux.tar.gz`
2. Extract: `tar -xzf DyingLands-Linux.tar.gz`
3. Run: `./run.sh` or `./DyingLands`
4. Optional: Create desktop shortcut

## 🎯 Next Steps

1. **Test the WebView launcher**: `python src/webview_launcher.py`
2. **Build your first installer**: `python build_installer.py`
3. **Customize the appearance**: Add icons and branding
4. **Test on different systems**: Ensure compatibility
5. **Create documentation**: User manual and troubleshooting guide

The application will now run as a native desktop application with a WebView interface, providing a much better user experience than requiring users to open a browser and navigate to localhost!