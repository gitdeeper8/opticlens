# 🔭 OPTICLENS Installation Guide

## Quick Install

```bash
pip install opticlens
```

Development Install

```bash
git clone https://gitlab.com/gitdeeper8/opticlens.git
cd opticlens
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

Docker Install

```bash
docker pull gitlab.com/gitdeeper8/opticlens:latest
docker run -p 8000:8000 -p 8501:8501 opticlens:latest
```

Requirements

· Python 3.8–3.11
· 8GB RAM minimum (16GB recommended for full simulations)
· 20GB disk space for satellite data archives
· Internet connection for real-time AERONET/MODIS feeds

Termux (Android) Install

```bash
pkg update && pkg upgrade
pkg install python python-pip git
pip install numpy scipy matplotlib pandas
pip install opticlens
```

Verify Installation

```bash
opticlens doctor
opticlens stations list
opticlens mie --radius 0.1 --wavelength 0.55 --refractive-index 1.5
opticlens edlen --pressure 101325 --temperature 288.15 --wavelength 0.55
opticlens turbulence --cn2 1e-15 --path-length 1000
```

Quick Start Example

```python
import opticlens as ol

# Calculate Mie scattering for aerosol particle
mie = ol.MieScattering(
    wavelength=0.55,  # μm
    radius=0.1,       # μm
    refractive_index=1.5 + 0.01j
)
results = mie.compute_efficiencies()
print(f"Q_ext: {results['Q_ext']:.4f}")
print(f"Q_scat: {results['Q_scat']:.4f}")
print(f"Asymmetry parameter g: {results['g']:.4f}")

# Calculate refractive index of air
n = ol.refractive_index(
    pressure=101325,  # Pa
    temperature=288.15,  # K
    wavelength=0.55,  # μm
    humidity=0.5
)
print(f"Refractive index: {n:.9f}")

# Calculate turbulence parameters
turb = ol.Turbulence(
    cn2=1e-15,  # m^(-2/3)
    wavelength=0.55,  # μm
    path_length=1000  # m
)
print(f"Scintillation index: {turb.scintillation_index():.4f}")
print(f"Fried parameter: {turb.fried_parameter():.4f} m")
```

📚 Full documentation: https://opticlens.readthedocs.io
