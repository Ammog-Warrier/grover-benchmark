#!/bin/bash
# Grover's Benchmark Automation Script
# Runs calibration, simulation, and visualization in sequence.

set -e  # Exit immediately if a command exits with a non-zero status

print_header() {
    echo ""
    echo "============================================================"
    echo "$1"
    echo "============================================================"
    echo ""
}

# Ensure we are in the correct virtual environment if it exists
if [ -d "venv" ]; then
    if [[ "$VIRTUAL_ENV" != "$(pwd)/venv" ]]; then
        print_header "Activating virtual environment..."
        source venv/bin/activate
    fi
fi

# Set Matplotlib backend to Agg to prevent blocking window popups
export MPLBACKEND=Agg

print_header "Step 1: Running Grover's Algorithm Benchmark (Simulation)"
python main.py

print_header "Step 2: Generating Consolidated PDF Report"
python generate_report.py

print_header "Step 3: Generating Bloch Sphere Animation (GIF)"
# We still run this for the GIF, but it won't save the PNG anymore if we don't ask it to, 
# relying on generate_report.py for the static chart.
# However, bloch_animation.py execution currently generates the PNG by default IF run as main.
# We should probably let it generate the gif only or just ignore the png it generates.
python bloch_animation.py

print_header "Full Benchmark Pipeline Complete!"
echo "Outputs are available in the 'benchmarks/' directory."
