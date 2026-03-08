#!/data/data/com.termux/files/usr/bin/bash
# Simple test runner for OPTICLENS on Termux

echo "🔭 OPTICLENS Test Runner (Termux)"
echo "=================================="

# Go to project directory
cd /storage/emulated/0/Download/OPTIC-LENS

# Add current directory to Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Install dependencies if needed
pip install --user pytest pytest-cov 2>/dev/null

# Run tests
echo ""
echo "Running tests..."
python -m pytest tests/unit/ -v

echo ""
echo "Done!"
