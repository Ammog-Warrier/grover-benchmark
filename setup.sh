#!/bin/bash

# Grover's Algorithm Benchmarking Suite - Quick Start Script

echo "========================================"
echo "Grover's Algorithm Benchmarking Suite"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Setup complete! You can now run:"
echo ""
echo "  1. python main.py              - Run benchmarking suite"
echo "  2. python visualize.py         - Generate comparison chart"
echo "  3. python bloch_animation.py   - Generate animations"
echo ""
echo "Results will be saved in the 'benchmarks/' directory"
echo ""
