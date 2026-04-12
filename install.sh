#!/bin/bash
# Friday Night Funkin' Lightweight - Installation Script

echo ""
echo "========================================"
echo "FNF Lightweight - Setup Installation"
echo "========================================"
echo ""

# Check if python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

echo "Python found:"
python3 --version

echo ""
echo "Installing dependencies..."

# Install pygame
python3 -m pip install pygame==2.5.0 --upgrade

if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: pygame installation failed!"
    echo "Trying alternative installation..."
    python3 -m pip install --user pygame
fi

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Could not install pygame."
    echo ""
    echo "Try these alternatives:"
    echo "1. Use Anaconda: conda install pygame"
    echo "2. Try another pip command: pip3 install pygame"
    echo "3. Check your internet connection"
    exit 1
fi

echo ""
echo "========================================"
echo "Installation complete!"
echo "========================================"
echo ""
echo "You can now run the game with:"
echo "    python main.py"
echo ""
echo "Or create custom charts with:"
echo "    python -m src.chart_editor"
echo ""
