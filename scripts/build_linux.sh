#!/bin/bash
source .venv/bin/activate
pyinstaller pyinstaller_config.spec --clean --workpath build/linux --distpath dist/linux