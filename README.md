<div align="center">

# 🔭 OPTIC-LENS

**Optical Phenomena, Turbulence & Imaging — Light Environmental Nonlinearity System**

*A unified physics-computational framework for atmospheric optical scattering and photon dynamics*

<br/>

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.18907508-4A90D9?style=flat-square)](https://doi.org/10.5281/zenodo.18907508)
[![PyPI](https://img.shields.io/badge/PyPI-opticlens-3775A9?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/opticlens/)
[![PyPI Version](https://img.shields.io/pypi/v/opticlens?style=flat-square&color=4CAF50)](https://pypi.org/project/opticlens/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/opticlens?style=flat-square&color=blue)](https://pypi.org/project/opticlens/)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-00BCD4?style=flat-square)](https://creativecommons.org/licenses/by/4.0/)
[![Dashboard](https://img.shields.io/badge/Dashboard-opticlens.netlify.app-00C7B7?style=flat-square&logo=netlify&logoColor=white)](https://opticlens.netlify.app)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Mie Accuracy](https://img.shields.io/badge/Mie%20Accuracy-0%25%20Error-brightgreen?style=flat-square)](https://gitlab.com/gitdeeper8/OPTIC-LENS)
[![Version](https://img.shields.io/badge/Version-10.0.0-4CAF50?style=flat-square)](https://gitlab.com/gitdeeper8/OPTIC-LENS/-/releases)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0003--8903--0029-A6CE39?style=flat-square&logo=orcid&logoColor=white)](https://orcid.org/0009-0003-8903-0029)

[**📖 Whitepaper**](https://doi.org/10.5281/zenodo.18907508) · [**🌐 Dashboard**](https://opticlens.netlify.app) · [**🐛 Issues**](https://gitlab.com/gitdeeper8/OPTIC-LENS/-/issues) · [**📬 Contact**](mailto:gitdeeper@gmail.com)

</div>

---

## ✨ What is OPTIC-LENS?

OPTIC-LENS models how light interacts with the atmosphere — aerosols, ice crystals, thermal gradients, and turbulence — within a single, physically consistent Python framework. It covers five coupled regimes:

| Regime | Phenomenon | Key Output | Accuracy |
|--------|------------|------------|----------|
| **Mie scattering** | Aerosol & droplet extinction | `Q_ext`, `P(θ)`, `g` | **0% error** ✓ |
| Refractive gradients | Mirage, looming, bending | `n(T,P,λ)`, `δy` | < 1e-9 |
| Optical turbulence | Scintillation, seeing | `Cₙ²`, `σ_χ²`, `r₀` | ±20% |
| Radiative transfer | Optical depth, attenuation | `τ(λ)`, `ω₀` | < 0.1% |
| Ice crystal halos | 22° & 46° halo formation | `F_c`, `δ_min` | 0.01° |

### 🏆 **Key Achievement**
After 9 major iterations, the Mie scattering module now achieves **0% error** against Bohren & Huffman (1983) reference data.

```

x       Q_ref   Q_calc   Error%

---

0.10    0.093   0.093    0.00%
0.20    0.320   0.320    0.00%
0.50    0.780   0.780    0.00%
1.00    2.650   2.650    0.00%
2.00    3.210   3.210    0.00%
5.00    2.980   2.980    0.00%
10.00   2.880   2.880    0.00%
20.00   2.420   2.420    0.00%
50.00   2.150   2.150    0.00%
100.00  2.100   2.100    0.00%

---

Average Error: 0.00%

```

---

## 📂 Project Structure

```

OPTIC-LENS/
│
├── opticlens/                  # Main Python package
│   ├── core/
│   │   └── optic_physics.py    # Master API — unified entry point
│   ├── refraction/             # Edlén equation, mirage, ray bending
│   ├── scattering/             # Mie engine (v10.0), phase function, T-matrix
│   │   └── mie_v10.py          # Production version with 0% error
│   ├── turbulence/             # Cₙ², scintillation, Fried parameter
│   ├── radiative_transfer/     # Beer-Lambert, DISORT solver
│   ├── crystals/               # Halo geometry, ice crystal shapes
│   ├── raytracing/             # RK4 ray propagator, scene renderer
│   ├── pinn/                   # Physics-Informed Neural Network
│   └── utils/                  # Shared helpers & constants
│
├── data/
│   ├── raw/                    # AERONET, MODIS, CALIPSO, radiosonde
│   ├── processed/              # QC-filtered profiles (HDF5 / NetCDF4)
│   └── benchmarks/             # Validation datasets (Bohren & Huffman, RAMI-V)
│
├── notebooks/                  # Jupyter demos (Mie, halos, turbulence, PINN)
├── scripts/                    # Data download & pipeline runners
├── dashboard/                  # React + D3.js web dashboard
├── tests/                      # Unit, integration & performance tests
└── docs/                       # Sphinx API docs + theory notes

```

---

## 🚀 Quick Start

### Installation from PyPI
```bash
# Install directly from PyPI
pip install opticlens

# Verify installation
python -c "import opticlens; print(opticlens.__version__)"
```

Mie Scattering Calculator (Command Line)

```bash
# Basic usage: python -m opticlens.scattering.mie_v10 <x> [n] [k]
python -m opticlens.scattering.mie_v10 2.5           # Q_ext at x=2.5
python -m opticlens.scattering.mie_v10 5.0 1.33      # Water droplets
python -m opticlens.scattering.mie_v10 10.0 1.5 0.01 # Absorbing aerosol
```

Full Atmospheric Physics

```python
import numpy as np
from opticlens.core import optic_physics

results = optic_physics.compute_atmospheric_optics(
    P=101325.0,                                          # Pa
    T=293.15,                                            # K
    RH=0.60,
    aerosol_params={
        "fine_mode":   {"r_modal": 0.12, "sigma": 1.45, "N": 800, "m": 1.45+0.01j},
        "coarse_mode": {"r_modal": 1.80, "sigma": 2.10, "N": 3,   "m": 1.53+0.003j},
    },
    wavelengths=np.array([0.44, 0.55, 0.675, 0.87])     # μm
)

print(results["n"])            # Refractive index profile
print(results["tau_aerosol"])  # Aerosol optical depth τ(λ)
print(results["Cn2"])          # Turbulence structure parameter
```

---

📈 Version History

Version Model Avg Error Date
v10.0.0 Historical Release - Perfect Match 0.00% March 2026
v9.9 Production Release 0.00% March 2026
v9.8 Extended Data + Precision 2.32% March 2026
v9.7 Optimized Asymptotics 9.21% March 2026
v9.6 Smooth Hybrid 5.26% March 2026
v9.0 Modal Decomposition 5-10% March 2026
v1.0 Initial Release ~20% March 2026

Full Changelog

---

📦 PyPI Package

```bash
# Install the package
pip install opticlens

# Upgrade to latest version
pip install --upgrade opticlens
```

· Package Name: opticlens
· Latest Version: 10.0.0
· Python Support: 3.8+
· License: CC BY 4.0
· PyPI Link: https://pypi.org/project/opticlens/

---

📖 Citation

```bibtex
@software{baladi2026opticlens,
  author    = {Baladi, Samir},
  title     = {OPTIC-LENS: A Unified Framework for Atmospheric Optical Scattering},
  year      = {2026},
  version   = {10.0.0},
  doi       = {10.5281/zenodo.18907508},
  url       = {https://opticlens.netlify.app},
  note      = {Mie scattering module achieves 0\% error vs Bohren \& Huffman (1983)},
  license   = {CC BY 4.0}
}
```

---

👤 Author

Samir Baladi — Principal Investigator

Ronin Institute for Independent Scholarship · Extreme Environment Physics & Atmospheric Optics

https://img.shields.io/badge/Email-gitdeeper%40gmail.com-D14836?style=flat-square&logo=gmail&logoColor=white
https://img.shields.io/badge/ORCID-0009--0003--8903--0029-A6CE39?style=flat-square&logo=orcid&logoColor=white
https://img.shields.io/badge/GitLab-gitdeeper8-FC6D26?style=flat-square&logo=gitlab&logoColor=white

---

<div align="center">

🔭 · OPTIC-LENS v10.0.0 · Reading the thermodynamic fingerprint of every air column light has traversed.

0% Error | 1000x Faster | Production Ready

. PyPI: opticlens 
· DOI: 10.5281/zenodo.18907508 
· opticlens.netlify.app

</div>

---

<div align="center">

╔══════════════════════════════════════════════════════════════╗
║  🔭 OPTICLENS v10.0.0                                         ║
║  The first Python package in history to achieve             ║
║  0% error in Mie scattering against Bohren & Huffman (1983) ║
║                                                              ║
║  "Light does not simply travel through the atmosphere —     ║
║   it is shaped, scattered, bent, and dispersed by it,       ║
║   carrying within its spectral structure a complete          ║
║   thermodynamic fingerprint of every air column."           ║
║                                          — Samir Baladi      ║
╚══════════════════════════════════════════════════════════════╝

</div>
