#!/bin/bash
echo "========================================"
echo "System Monitor Pro - Glassmorphism Edition"
echo "Installation Script"
echo "========================================"
echo ""

# Check Python
echo "Checking Python version..."
python3 --version || { echo "Python 3.7+ required"; exit 1; }
echo "✓ Python found"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Installation complete!"
    echo ""
    echo "Run with: python3 system_monitor_glass.py"
    echo "Or use: ./run.sh"
else
    echo "✗ Installation failed"
    exit 1
fi
