#!/bin/bash
# Quick launcher script for Zerodha Kite Trading Bot
# Makes it easy to run without remembering python3.9

cd "$(dirname "$0")"

if command -v python3.9 &> /dev/null; then
    python3.9 launcher.py "$@"
else
    echo "Error: python3.9 not found"
    echo "Please install Python 3.9 or use: python3.9 launcher.py"
    exit 1
fi
