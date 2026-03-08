#!/usr/bin/env python
"""Setup script for OPTICLENS - Optical Phenomena, Turbulence & Imaging."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="opticlens",
    version="10.0.0",
    author="Samir Baladi",
    author_email="gitdeeper@gmail.com",
    description="OPTICLENS: Optical Phenomena, Turbulence & Imaging --- Light Environmental Nonlinearity System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitdeeper8/opticlens",
    project_urls={
        "Documentation": "https://opticlens.readthedocs.io",
        "Dashboard": "https://opticlens.netlify.app",
        "DOI": "https://doi.org/10.5281/zenodo.18907508",
        "Source": "https://github.com/gitdeeper8/opticlens",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Engineering",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Optics",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
        "viz": [
            "matplotlib>=3.7.0",
            "plotly>=5.14.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "opticlens=opticlens.cli:main",
            "opticlens-mie=opticlens.scattering.mie_v10:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
