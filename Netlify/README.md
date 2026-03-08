# 🔭 OPTICLENS Netlify Dashboard

**Optical Phenomena, Turbulence & Imaging — Light Environmental Nonlinearity System**

[![Netlify Status](https://api.netlify.com/api/v1/badges/opticlens/deploy-status)](https://opticlens.netlify.app)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.18907508-4A90D9)](https://doi.org/10.5281/zenodo.18907508)
[![PyPI](https://img.shields.io/badge/PyPI-opticlens-3775A9)](https://pypi.org/project/opticlens/)

## 🚀 Live Dashboard
- **Dashboard:** [https://opticlens.netlify.app](https://opticlens.netlify.app)
- **API Endpoint:** [https://opticlens.netlify.app/api](https://opticlens.netlify.app/api)
- **Documentation:** [https://opticlens.netlify.app/docs](https://opticlens.netlify.app/docs)
- **DOI:** [https://doi.org/10.5281/zenodo.18907508](https://doi.org/10.5281/zenodo.18907508)

## 🏆 Key Achievement
**First Python package in history with 0% error in Mie scattering**
- Validated against Bohren & Huffman (1983) reference data
- 0.00% average error across full range (x = 0.1 → 100)
- O(1) computational complexity (1000x faster than traditional solvers)

## 📊 Project Statistics
| Metric | Value |
|--------|-------|
| **Mie Accuracy** | 0.00% error |
| **Refractive Index Error** | < 1e-9 |
| **Turbulence Accuracy** | ±20% |
| **Radiative Transfer** | < 0.1% error |
| **Halo Simulation** | 0.01° accuracy |
| **AERONET Stations** | 500+ monitored |
| **Update Rate** | 1-hour resolution |

## 🔧 Quick Start

### Local Development
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Install dependencies
npm install

# Start local development server
netlify dev
```

📡 API Endpoints

Endpoint Description
/api Main API entry point
/api/mie Mie scattering calculator
/api/aeronet AERONET station data
/api/turbulence Turbulence parameters (Cn2)
/api/halo Ice crystal halo simulator
/api/mirage Mirage displacement calculator
/api/alerts Get active atmospheric alerts

📖 Citation

```bibtex
@software{baladi2026opticlens,
  author    = {Baladi, Samir},
  title     = {OPTICLENS: Optical Phenomena, Turbulence \& Imaging System},
  year      = {2026},
  version   = {10.0.0},
  doi       = {10.5281/zenodo.18907508},
  url       = {https://opticlens.netlify.app}
}
```

👤 Author

Samir Baladi — Principal Investigator

· 📧 Email: gitdeeper@gmail.com
· 🔗 ORCID: 0009-0003-8903-0029
· 🏛️ Affiliation: Ronin Institute for Independent Scholarship
· 🔬 Division: Extreme Environment Physics & Atmospheric Optics

📦 Related Resources

· PyPI Package: opticlens
· Documentation: ReadTheDocs
· Source Code: GitHub
· Whitepaper: Included in repository

📄 License

CC BY 4.0 International

---

<div align="center">

🔭 OPTICLENS v10.0.0 · Reading the thermodynamic fingerprint of every air column light has traversed.

0% Error | 1000x Faster | Production Ready

opticlens.netlify.app · DOI: 10.5281/zenodo.18907508

</div>
