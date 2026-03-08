# 🔭 CONTRIBUTING TO OPTICLENS

First off, thank you for considering contributing to OPTICLENS! We welcome contributions from atmospheric physicists, optical engineers, remote sensing specialists, climate scientists, and anyone passionate about understanding how light interacts with our atmosphere.

---

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

---

## Types of Contributions

### 🔬 Scientific Contributions
- New aerosol optical datasets (AERONET, SKYNET, MAN)
- Mie scattering validation data for complex refractive indices
- Turbulence measurements (scintillometer, sonic anemometer)
- Ice crystal morphology data for halo simulations
- Mirage observations and temperature profile measurements
- Lidar backscatter and depolarization ratio profiles
- Hyperspectral sky radiance measurements

### 🤖 Code Contributions
- Mie scattering algorithm optimizations
- Edlén equation refinements for extreme conditions
- Rytov scintillation model improvements
- DISORT radiative transfer solver enhancements
- Ray-tracing engine GPU acceleration (CUDA)
- Physics-Informed Neural Network architectures
- Real-time data ingestion pipelines
- Dashboard and visualization tools

### 📊 Data Contributions
- AERONET direct-sun and inversion products
- MODIS aerosol optical depth retrievals
- CALIPSO lidar profile data
- Meteorological profiles (radiosonde, reanalysis)
- Scintillometer network measurements
- Halo and mirage photographic observations
- Sun photometer calibration data

### 📝 Documentation Contributions
- Tutorials and examples
- API documentation
- Physics background explanations
- Case study write-ups
- Translation of documentation
- User guides for researchers and students

---

## Getting Started

### Prerequisites
- **Python 3.8–3.11**
- **Git**
- **Basic knowledge of optics or atmospheric physics**

### Setup Development Environment

```bash
# Fork the repository, then clone
git clone https://gitlab.com/YOUR_USERNAME/opticlens.git
cd opticlens

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"
pre-commit install
```

Verify Setup

```bash
# Run basic validation
python scripts/validate_environment.py

# Run tests
pytest tests/unit/ -v

# Check Mie scattering
python scripts/check_mie.py --size-parameter 10 --refractive-index 1.5

# Test refractive index
python scripts/check_edlen.py --pressure 101325 --temperature 288.15 --wavelength 0.55
```

---

Development Workflow

1. Create an issue describing your proposed changes
2. Fork and branch:
   ```bash
   git checkout -b feature/your-feature-name
   git checkout -b fix/issue-description
   git checkout -b physics/new-model
   ```
3. Make changes following our standards
4. Write/update tests
5. Run tests locally
6. Commit with clear messages
7. Push to your fork
8. Open a Merge Request

---

Coding Standards

Python

· Format: Black (line length 88)
· Imports: isort with black profile
· Type Hints: Required for all public functions
· Docstrings: Google style

Example Physics Module

```python
"""Mie scattering calculations for spherical particles."""

from typing import Optional, Tuple, List
import numpy as np
from scipy.special import spherical_jn, spherical_yn

from opticlens.core import ParameterBase
from opticlens.physics.constants import PI


class MieScattering(ParameterBase):
    """Mie scattering theory for spherical aerosol particles.
    
    Implements exact solution to Maxwell's equations for plane wave
    incident on homogeneous sphere. Provides extinction, scattering,
    absorption efficiencies and phase function.
    
    Attributes:
        wavelength: Optical wavelength [μm]
        radius: Particle radius [μm]
        refractive_index: Complex refractive index (n + i·k)
    """
    
    def compute_efficiencies(self) -> dict:
        """Compute Mie scattering efficiencies.
        
        Returns:
            Dictionary with Q_ext, Q_scat, Q_abs, asymmetry parameter g
        """
        x = 2 * PI * self.radius / self.wavelength  # size parameter
        m = self.refractive_index
        
        # Mie coefficients a_n, b_n using Riccati-Bessel functions
        a_n, b_n = self._compute_mie_coefficients(x, m)
        
        # Efficiencies
        n_max = len(a_n)
        n_range = np.arange(1, n_max + 1)
        
        Q_ext = (2 / x**2) * np.sum((2*n_range + 1) * np.real(a_n + b_n))
        Q_scat = (2 / x**2) * np.sum((2*n_range + 1) * (np.abs(a_n)**2 + np.abs(b_n)**2))
        Q_abs = Q_ext - Q_scat
        
        # Asymmetry parameter
        g = self._compute_asymmetry(a_n, b_n, n_range, x)
        
        return {
            'Q_ext': Q_ext,
            'Q_scat': Q_scat,
            'Q_abs': Q_abs,
            'g': g,
            'size_parameter': x
        }
    
    def _compute_mie_coefficients(self, x: float, m: complex) -> Tuple[np.ndarray, np.ndarray]:
        """Compute Mie coefficients a_n and b_n."""
        # Implementation using Riccati-Bessel functions
        n_max = int(x + 4 * x**(1/3) + 2)
        
        # ... detailed implementation ...
        
        return a_n, b_n
```

---

Testing Guidelines

Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── physics/
│   │   ├── test_mie.py
│   │   ├── test_edlen.py
│   │   ├── test_turbulence.py
│   │   ├── test_radiative_transfer.py
│   │   └── test_ray_tracing.py
│   ├── models/
│   │   └── test_pinn.py
│   └── utils/
│       └── test_spectral.py
├── integration/             # Integration tests
│   ├── test_data_ingestion.py
│   └── test_forward_model.py
├── validation/              # Validation against benchmarks
│   ├── test_bohren_huffman.py
│   ├── test_aeronet.py
│   └── test_modis.py
└── fixtures/                # Test data
    ├── mie_benchmarks.json
    ├── aeronet_samples.csv
    └── atmospheric_profiles.nc
```

Running Tests

```bash
# All tests
pytest

# Physics tests
pytest tests/unit/physics/ -v

# Mie scattering validation
pytest tests/validation/test_bohren_huffman.py -v --mie-accuracy 1e-6

# With coverage
pytest --cov=opticlens --cov-report=html
```

---

Data Contributions

New Data Source Requirements

When adding a new data source, include:

1. Source metadata (agency, instrument, location, time period)
2. Data format specification (NetCDF, HDF5, CSV, JSON)
3. Access method (API, FTP, public URL)
4. Update frequency (real-time, daily, monthly)
5. Quality control procedures applied
6. Validation against existing sources
7. Spectral/wavelength coverage
8. Geographic and temporal coverage

Data Format Requirements

Parameter Source Format Required Fields
Aerosol Optical Depth AERONET CSV wavelength, AOD, time, site
Refractive Index Laboratory JSON wavelength, n, k, T, P
Cn2 Profile Scintillometer NetCDF altitude, Cn2, time
Radiance MODIS HDF wavelength, radiance, lat, lon
Backscatter CALIPSO HDF altitude, beta, depolarization
Temperature Radiosonde CSV pressure, temperature, altitude

---

Field Campaign Ethics

Any contribution involving field measurements must:

1. Obtain all necessary permits and permissions
2. Minimize environmental impact
3. Follow best practices for instrument calibration
4. Share data openly with the scientific community
5. Acknowledge all collaborators and funding sources
6. Document measurement uncertainties thoroughly
7. Ensure safety of all personnel during deployments

Contact: fieldwork@opticlens.space

---

Adding New Physical Models

If you propose a new physical model for OPTICLENS:

1. Literature review - Demonstrate physical basis and prior validation
2. Governing equations - Provide complete mathematical formulation
3. Numerical implementation - Specify algorithm and computational requirements
4. Validation data - Provide benchmark datasets
5. Uncertainty quantification - Estimate model errors
6. Computational cost - Profile performance
7. Range of validity - Specify applicable conditions (wavelength, pressure, etc.)

---

Reporting Issues

Bug Reports

Include:

· Clear title and description
· Steps to reproduce
· Expected vs actual behavior
· Environment details (OS, Python version, dependencies)
· Logs or screenshots
· Input parameters and atmospheric conditions

Feature Requests

Include:

· Use case description
· Expected behavior
· Scientific justification
· References to similar work
· Potential data sources
· Applicable atmospheric conditions

---

Contact

Purpose Contact
General inquiries gitdeeper@gmail.com
Code of Conduct conduct@opticlens.space
Data contributions data@opticlens.space
Scientific questions science@opticlens.space
Fieldwork coordination fieldwork@opticlens.space

Repository: https://gitlab.com/gitdeeper8/opticlens
Dashboard: https://opticlens.netlify.app
DOI: 10.5281/zenodo.OPTICLENS.2026

---

🔭 Light does not simply travel through the atmosphere — it is shaped, scattered, bent, and dispersed by it.

Last Updated: March 2026
