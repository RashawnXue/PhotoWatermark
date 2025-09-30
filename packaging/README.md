Packaging guide for PhotoWatermark

This document explains how to build standalone application bundles for macOS, Windows and Linux using PyInstaller.

Prerequisites
- Python 3.10+ (same major version used by the source)
- pip install -r requirements.txt
- On macOS: iconutil (comes with Xcode command line tools), hdiutil (for DMG)
- On Windows: optional Inno Setup / NSIS for installers
- On Linux: optional appimagetool for AppImage

Files
- packaging/build_app.sh - helper script that runs PyInstaller and generates platform-specific artifacts.
- assets/app_icon.png - source PNG icon for the app. Replace with your final PNG (recommended 1024x1024).

How it works
1. Place your final PNG at `assets/app_icon.png` (preferably 1024x1024).
2. Run the helper script to build for your current platform.

Example (macOS):

    ./packaging/build_app.sh mac

This will run PyInstaller with correct options and create `dist/PhotoWatermark.app` (or a one-file executable) and helper files. See the script for more options.

Notes
- The script does not auto-sign or notarize for macOS.
- For reproducible builds, run inside a clean Python virtualenv.
