#!/bin/bash
# Setup script for OPTIC-LENS

echo "🔭 Setting up OPTIC-LENS..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .

# Install pre-commit hooks
pre-commit install

# Create necessary directories
mkdir -p data/raw data/processed data/benchmarks
mkdir -p logs
mkdir -p output

echo "✅ OPTIC-LENS setup complete!"
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run tests:"
echo "  pytest tests/ -v"
echo ""
echo "To launch dashboard:"
echo "  opticlens dashboard"
