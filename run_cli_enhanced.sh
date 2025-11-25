#!/bin/bash
# Launcher for Enhanced Trading CLI
# Provides feature parity with gui_modern.py in terminal interface

cd "$(dirname "$0")"

echo "Starting Enhanced Trading CLI..."
echo ""

if command -v python3.9 &> /dev/null; then
    python3.9 Application/main_enhanced.py "$@"
else
    echo "Error: python3.9 not found"
    echo "Please install Python 3.9 or use: python3.9 Application/main_enhanced.py"
    exit 1
fi
