#!/bin/bash
# Run all tests for OPTIC-LENS

echo "🔭 Running OPTIC-LENS test suite..."

# Unit tests
echo ""
echo "📊 Unit tests:"
pytest tests/unit/ -v --cov=opticlens --cov-report=term

# Integration tests
echo ""
echo "🔄 Integration tests:"
pytest tests/integration/ -v

# Performance tests (optional)
if [ "$1" == "--performance" ]; then
    echo ""
    echo "⚡ Performance tests:"
    pytest tests/performance/ -v --durations=10
fi

# Generate coverage report
echo ""
echo "📈 Coverage report:"
pytest --cov=opticlens --cov-report=html
echo "HTML coverage report generated in htmlcov/"

echo ""
echo "✅ Tests complete!"
