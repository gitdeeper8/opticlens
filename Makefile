# 🔭 OPTICLENS Makefile
# Optical Phenomena, Turbulence & Imaging --- Light Environmental Nonlinearity System

.PHONY: help install dev test lint format clean docs run docker-build docker-run

help:
	@echo "🔭 OPTICLENS Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make install     Install production dependencies"
	@echo "  make dev         Install development dependencies"
	@echo "  make test        Run tests"
	@echo "  make lint        Run linters (flake8, mypy)"
	@echo "  make format      Format code (black, isort)"
	@echo "  make clean       Clean build artifacts"
	@echo "  make docs        Build documentation"
	@echo "  make run         Run OPTICLENS locally"
	@echo "  make docker-build Build Docker image"
	@echo "  make docker-run  Run Docker container"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=opticlens

test-mie:
	pytest tests/unit/physics/test_mie.py -v --mie-accuracy 1e-6

test-edlen:
	pytest tests/unit/physics/test_edlen.py -v --refractive-index-tol 1e-9

test-turbulence:
	pytest tests/unit/physics/test_turbulence.py -v

lint:
	flake8 opticlens tests
	mypy opticlens

format:
	black opticlens tests
	isort opticlens tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf docs/build/
	rm -rf docs/site/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:
	cd docs && make html
	@echo "Documentation built in docs/build/html/"

docs-serve:
	cd docs/build/html && python -m http.server 8001

run:
	opticlens dashboard --port 8501

docker-build:
	docker build -t opticlens:latest .

docker-run:
	docker run -p 8000:8000 -p 8501:8501 opticlens:latest

docker-dev:
	docker-compose -f docker-compose.dev.yml up

docker-prod:
	docker-compose up -d

data-fetch-aeronet:
	opticlens data fetch --source aeronet --station GSFC --hours 24

data-fetch-modis:
	opticlens data fetch --source modis --days 1

simulate-mie:
	opticlens mie --radius 0.1 --wavelength 0.55 --refractive-index 1.5+0.01j

simulate-mirage:
	opticlens mirage --temp-gradient 0.5 --path 1000 --observer-height 1.7

simulate-halo:
	opticlens halo --type 22-degree --crystal-type hexagonal

check-env:
	@echo "🔭 Checking OPTICLENS environment..."
	@python -c "import opticlens; print(f'OPTICLENS version: {opticlens.__version__}')" 2>/dev/null || echo "❌ OPTICLENS not installed"
	@python --version
	@pip list | grep -E "numpy|scipy|matplotlib|pandas"

version:
	@python -c "import opticlens; print(opticlens.__version__)"

release:
	python -m build
	twine check dist/*
	@echo "Ready to upload to PyPI: twine upload dist/*"

.PHONY: help install dev test lint format clean docs run docker-build docker-run
