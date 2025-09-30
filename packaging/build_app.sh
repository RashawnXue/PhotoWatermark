#!/usr/bin/env bash
# Usage: ./build_app.sh [platform]
# platform: mac | win | linux
set -euo pipefail
ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"
ICON_PNG=$ROOT_DIR/assets/icon.png
ICON_ICNS=$ROOT_DIR/assets/icon.icns
# User requested canonical icon: prefer assets/icon.ico when present
ICON_ICO=$ROOT_DIR/assets/icon.ico
PYTHON_CMD=python
if [ -n "${VIRTUAL_ENV:-}" ]; then
  PYTHON_CMD="$VIRTUAL_ENV/bin/python"
elif [ -f "$ROOT_DIR/venv/bin/python" ]; then
  PYTHON_CMD="$ROOT_DIR/venv/bin/python"
fi
APP_NAME=PhotoWatermark
PYINSTALLER_OPTS=(--noconfirm --clean)

if [ ! -f "$ICON_PNG" ]; then
  # If an SVG icon exists, try to convert it to PNG so downstream tools can work
  SVG_SRC=$ROOT_DIR/assets/icon.svg
  if [ -f "$SVG_SRC" ]; then
    echo "Found SVG icon at $SVG_SRC — attempting to convert to PNG ($ICON_PNG)..."
    # prefer rsvg-convert, then inkscape, then ImageMagick's convert
    if command -v rsvg-convert >/dev/null 2>&1; then
  rsvg-convert -w 1024 -h 1024 "$SVG_SRC" -o "$ICON_PNG" || true
    elif command -v inkscape >/dev/null 2>&1; then
      # inkscape CLI differs between versions; try modern and legacy flags
  inkscape "$SVG_SRC" --export-type=png --export-filename="$ICON_PNG" --export-width=1024 --export-height=1024 >/dev/null 2>&1 || \
  inkscape -z -e "$ICON_PNG" -w 1024 -h 1024 "$SVG_SRC" >/dev/null 2>&1 || true
    elif command -v convert >/dev/null 2>&1; then
  convert -background none -density 300 "$SVG_SRC" -resize 1024x1024 "$ICON_PNG" || true
    else
      echo "No SVG converter found (rsvg-convert|inkscape|convert). Cannot convert SVG to PNG automatically."
    fi
    if [ -f "$ICON_PNG" ]; then
      echo "SVG successfully converted to $ICON_PNG"
    else
      echo "Conversion failed: $ICON_PNG not created. Please provide a valid PNG at assets/app_icon.png"
    fi
  else
    echo "Warning: $ICON_PNG not found. Please add your icon PNG to assets/"
  fi
fi

case "${1:-}" in
  mac)
    echo "Building for macOS..."
    # try to create .icns from PNG if iconutil available; don't fail the whole build if conversion fails
    # If an .icns already exists (maybe generated earlier), skip regeneration to avoid sips on a bad PNG
    if [ -f "$ICON_ICNS" ]; then
      echo "Found existing $ICON_ICNS — skipping .icns generation."
    elif command -v iconutil >/dev/null 2>&1 && [ -f "$ICON_PNG" ]; then
      ICONSET="$ROOT_DIR/assets/icon.iconset"
      mkdir -p "$ICONSET"
      set +e
      sips -z 16 16     "$ICON_PNG" --out "$ICONSET/icon_16x16.png"
      sips -z 32 32     "$ICON_PNG" --out "$ICONSET/icon_16x16@2x.png"
      sips -z 32 32     "$ICON_PNG" --out "$ICONSET/icon_32x32.png"
      sips -z 64 64     "$ICON_PNG" --out "$ICONSET/icon_32x32@2x.png"
      sips -z 128 128   "$ICON_PNG" --out "$ICONSET/icon_128x128.png"
      sips -z 256 256   "$ICON_PNG" --out "$ICONSET/icon_128x128@2x.png"
      sips -z 256 256   "$ICON_PNG" --out "$ICONSET/icon_256x256.png"
      sips -z 512 512   "$ICON_PNG" --out "$ICONSET/icon_256x256@2x.png"
      sips -z 512 512   "$ICON_PNG" --out "$ICONSET/icon_512x512.png"
      sips -z 1024 1024 "$ICON_PNG" --out "$ICONSET/icon_512x512@2x.png"
      ICONUTIL_RET=0
      iconutil -c icns "$ICONSET" -o "$ICON_ICNS"
      ICONUTIL_RET=$?
      set -e
      rm -rf "$ICONSET"
      if [ $ICONUTIL_RET -ne 0 ]; then
        echo "Warning: iconutil failed (exit $ICONUTIL_RET). Continuing with PNG fallback."
        # remove any partial icns created
        rm -f "$ICON_ICNS" || true
      fi
    fi
    ICON_ARG=""
    if [ -f "$ICON_ICNS" ]; then
      ICON_ARG="--icon=$ICON_ICNS"
    else
      echo "Note: $ICON_ICNS not found, PyInstaller will build without .icns icon (PNG fallback)."
    fi
  "$PYTHON_CMD" -m PyInstaller "${PYINSTALLER_OPTS[@]}" --windowed --name "$APP_NAME" $ICON_ARG gui_main.py
    ;;
  win)
    echo "Building for Windows..."
    # Create .ico using ImageMagick if available (convert)
    if command -v convert >/dev/null 2>&1 && [ -f "$ICON_PNG" ]; then
      convert "$ICON_PNG" -resize 256x256 "$ICON_ICO" || true
    fi
    ICON_ARG=""
    if [ -f "$ICON_ICO" ]; then
      ICON_ARG="--icon=$ICON_ICO"
    else
      echo "Note: $ICON_ICO not found, building without .ico icon."
    fi
  "$PYTHON_CMD" -m PyInstaller "${PYINSTALLER_OPTS[@]}" --windowed --name "$APP_NAME" $ICON_ARG gui_main.py
    ;;
  linux)
    echo "Building for Linux..."
    # linux - use PNG icon and let desktop file reference it; build onefile by default
  "$PYTHON_CMD" -m PyInstaller "${PYINSTALLER_OPTS[@]}" --windowed --name "$APP_NAME" --add-data "assets:assets" gui_main.py
    ;;
  *)
    echo "Usage: $0 {mac|win|linux}"
    exit 2
    ;;
esac

echo "Build finished. See dist/ for output."
