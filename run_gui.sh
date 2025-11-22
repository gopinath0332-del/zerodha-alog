#!/bin/bash

# Run the Trading Bot GUI
# This script ensures the GUI runs with the correct Python version

cd "$(dirname "$0")"

echo "Starting Trading Bot GUI..."
python3.9 Application/gui.py
