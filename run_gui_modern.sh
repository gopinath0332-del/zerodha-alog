#!/bin/bash

# Run the Modern Trading Bot GUI (DearPyGui)
# This script ensures the GUI runs with the correct Python version

cd "$(dirname "$0")"

echo "Starting Modern Trading Terminal..."
python3.9 Application/gui_modern.py
