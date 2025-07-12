#!/usr/bin/env python3
"""
Test script for WebView launcher
Quick test to verify the WebView setup works correctly
"""

import sys
import subprocess
import importlib.util
import os

def check_dependency(package_name, install_name=None):
    """Check if a package is installed."""
    if install_name is None:
        install_name = package_name
    
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        print(f"❌ {package_name} is not installed")
        print(f"   Install with: pip install {install_name}")
        return False
    else:
        print(f"✅ {package_name} is available")
        return True

def test_webview_import():
    """Test if webview can be imported and works."""
    try:
        import webview
        print(f"✅ pywebview {webview.__version__} imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Could not import webview: {e}")
        return False
    except Exception as e:
        print(f"❌ Error with webview: {e}")
        return False

def test_flask_import():
    """Test if Flask can be imported."""
    try:
        import flask
        print(f"✅ Flask {flask.__version__} imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Could not import Flask: {e}")
        return False

def test_src_files():
    """Test if source files exist."""
    required_files = [
        'src/webview_launcher.py',
        'src/ascii_map_viewer.py',
        'web/templates',
        'web/static'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def test_webview_launcher():
    """Test if the WebView launcher script is working."""
    try:
        # Test import of the launcher
        sys.path.insert(0, 'src')
        from webview_launcher import HexcrawlApp
        
        app = HexcrawlApp()
        print("✅ WebView launcher class created successfully")
        print(f"   Server will run on: {app.url}")
        return True
    except Exception as e:
        print(f"❌ Error testing WebView launcher: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Testing WebView Setup for The Dying Lands")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 7):
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} (OK)")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} (Need 3.7+)")
        return False
    
    print("\n📦 Checking Dependencies:")
    dependencies_ok = True
    dependencies_ok &= check_dependency('flask')
    dependencies_ok &= check_dependency('webview', 'pywebview')
    dependencies_ok &= check_dependency('requests')
    dependencies_ok &= check_dependency('markdown')
    
    print("\n📁 Checking Source Files:")
    files_ok = test_src_files()
    
    print("\n🔗 Testing Imports:")
    flask_ok = test_flask_import()
    webview_ok = test_webview_import()
    
    print("\n🚀 Testing WebView Launcher:")
    launcher_ok = test_webview_launcher()
    
    print("\n" + "=" * 50)
    
    if all([dependencies_ok, files_ok, flask_ok, webview_ok, launcher_ok]):
        print("🎉 All tests passed! Ready to build installer.")
        print("\n🔧 Next steps:")
        print("   1. Test the launcher: python src/webview_launcher.py")
        print("   2. Build installer: python build_installer.py")
        print("   3. Test executable: ./dist/DyingLands")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\n🔧 Common fixes:")
        print("   - Install missing dependencies: pip install -r requirements.txt")
        print("   - Check file paths and project structure")
        print("   - Verify Python version (3.7+ required)")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)