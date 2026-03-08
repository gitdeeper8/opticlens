"""
Physical constants for OPTIC-LENS calculations
"""

import numpy as np

# Mathematical constants
PI = np.pi
TWOPI = 2 * np.pi
DEG2RAD = PI / 180.0
RAD2DEG = 180.0 / PI

# Physical constants
SPEED_OF_LIGHT = 2.99792458e8      # m/s
PLANCK_CONSTANT = 6.62607015e-34   # J·s
BOLTZMANN_CONSTANT = 1.380649e-23   # J/K
AVOGADRO_NUMBER = 6.02214076e23     # mol⁻¹
GAS_CONSTANT = 8.314462618          # J/(mol·K)

# Atmospheric constants
STANDARD_PRESSURE = 101325.0        # Pa
STANDARD_TEMPERATURE = 288.15       # K (15°C)
STANDARD_LAPSE_RATE = 0.0065         # K/m
STANDARD_GRAVITY = 9.80665           # m/s²
MOLAR_MASS_DRY_AIR = 0.028964        # kg/mol
MOLAR_MASS_WATER = 0.018016          # kg/mol

# Optical constants
REFERENCE_WAVELENGTH = 0.55          # μm (green light)
SOLAR_CONSTANT = 1361.0              # W/m²

# Aerosol refractive indices (typical values)
REFractive_INDEX_WATER = 1.333 + 0j
REFractive_INDEX_ICE = 1.309 + 0j
REFractive_INDEX_DUST = 1.53 + 0.003j
REFractive_INDEX_SOOT = 1.75 + 0.45j
REFractive_INDEX_SALT = 1.50 + 0j
REFractive_INDEX_SULFATE = 1.43 + 0j

# Turbulence constants
KOLMOGOROV_CONSTANT = 0.5            # Optical turbulence constant
FRIED_CONSTANT = 0.423                # Fried parameter constant
RYTOV_CONSTANT = 0.563                # Rytov variance constant

# Mie scattering constants
MIE_CONVERGENCE_FACTOR = 4            # n_max = x + factor * x^(1/3) + 2
