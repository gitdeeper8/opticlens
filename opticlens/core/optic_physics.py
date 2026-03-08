"""
Master API for OPTIC-LENS — unified entry point for all atmospheric optics calculations
"""

import numpy as np
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field

from opticlens.refraction.edlen import EdlenRefractiveIndex
from opticlens.scattering.mie import MieScattering, AerosolMode
from opticlens.turbulence.rytov import RytovTurbulence
from opticlens.radiative_transfer.beer_lambert import BeerLambert
from opticlens.utils.constants import *
from opticlens.utils.validators import validate_atmospheric_state


@dataclass
class AtmosphericState:
    """Container for atmospheric state parameters"""
    pressure: float                # Pa
    temperature: float              # K
    relative_humidity: float        # 0-1
    co2_ppm: float = 450             # ppm
    height_profile: Optional[np.ndarray] = None   # m
    temperature_profile: Optional[np.ndarray] = None  # K
    pressure_profile: Optional[np.ndarray] = None  # Pa


@dataclass
class AerosolParameters:
    """Container for aerosol microphysical parameters"""
    fine_mode: Dict = field(default_factory=lambda: {
        "r_modal": 0.12,    # μm
        "sigma": 1.45,
        "N": 800,            # cm⁻³
        "m": 1.45 + 0.01j
    })
    coarse_mode: Dict = field(default_factory=lambda: {
        "r_modal": 1.80,    # μm
        "sigma": 2.10,
        "N": 3,              # cm⁻³
        "m": 1.53 + 0.003j
    })


def compute_atmospheric_optics(
    P: float,
    T: float,
    RH: float,
    aerosol_params: Dict,
    wavelengths: np.ndarray,
    path_length: Optional[float] = None,
    zenith_angle: Optional[float] = None,
    Cn2: Optional[float] = None
) -> Dict:
    """
    Master function — compute all optical properties from meteorological state
    
    Parameters
    ----------
    P : float
        Pressure [Pa]
    T : float
        Temperature [K]
    RH : float
        Relative humidity [0-1]
    aerosol_params : dict
        Aerosol size distribution parameters
    wavelengths : ndarray
        Wavelengths [μm]
    path_length : float, optional
        Horizontal path length for mirage/scintillation [m]
    zenith_angle : float, optional
        Solar zenith angle for radiative transfer [deg]
    Cn2 : float, optional
        If provided, override turbulence calculation
        
    Returns
    -------
    dict
        Complete optical property dictionary
    """
    # Validate inputs
    validate_atmospheric_state(P, T, RH)
    
    # 1. Refractive index profile (Edlén equation)
    edlen = EdlenRefractiveIndex()
    n = edlen.compute(P, T, wavelengths, RH)
    
    # 2. Aerosol optical properties (Mie scattering)
    mie = MieScattering(wavelengths)
    fine_mode = AerosolMode(**aerosol_params.get('fine_mode', {}))
    coarse_mode = AerosolMode(**aerosol_params.get('coarse_mode', {}))
    
    beta_ext, beta_scat, g, P_theta = mie.compute_bulk_properties(
        [fine_mode, coarse_mode]
    )
    
    # 3. Aerosol optical depth (Beer-Lambert)
    bl = BeerLambert()
    tau = bl.optical_depth(beta_ext, dz=1000)  # Assume 1km layer
    
    # 4. Turbulence parameters (if path length provided)
    if path_length is not None:
        turb = RytovTurbulence(wavelength=wavelengths[0])
        if Cn2 is None:
            Cn2 = turb.estimate_cn2(T, P, height=10)  # Rough estimate
            
        scintillation = turb.scintillation_index(Cn2, path_length)
        r0 = turb.fried_parameter(Cn2, wavelengths[0])
    else:
        scintillation = None
        r0 = None
    
    # 5. Mirage displacement (if horizontal gradient assumed)
    if path_length is not None:
        # Assume horizontal temperature gradient dT/dy ~ 0.5 K/m
        dTdy = 0.5
        mirage_disp = (79e-6 * P / T**2) * dTdy * path_length**2 / 2
    else:
        mirage_disp = None
    
    # Compile results
    results = {
        'refractive_index': n,
        'aerosol': {
            'beta_ext': beta_ext,
            'beta_scat': beta_scat,
            'asymmetry': g,
            'phase_function': P_theta,
            'optical_depth': tau
        },
        'turbulence': {
            'Cn2': Cn2,
            'scintillation_index': scintillation,
            'fried_parameter': r0
        },
        'mirage_displacement': mirage_disp,
        'metadata': {
            'pressure': P,
            'temperature': T,
            'humidity': RH,
            'wavelengths': wavelengths
        }
    }
    
    return results
