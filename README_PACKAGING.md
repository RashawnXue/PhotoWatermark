Packaging summary - how to build standalone apps

This repo includes helper scripts under `packaging/` to build standalone applications using PyInstaller.

Quick start (macOS example)

- Create a virtualenv: python -m venv .venv && source .venv/bin/activate
- Install deps: pip install -r requirements.txt
- Put your icon at `assets/app_icon.png` (1024x1024 recommended)
- Build: ./packaging/build_app.sh mac

The script will create `dist/PhotoWatermark` with a bundled app. See `packaging/README.md` for more details.
