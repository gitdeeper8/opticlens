"""
Input validation utilities for OPTIC-LENS
"""

import numpy as np
from typing import Union, Tuple


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_atmospheric_state(P: Union[float, np.ndarray],
                               T: Union[float, np.ndarray],
                               RH: Union[float, np.ndarray]) -> None:
    """
    Validate atmospheric state parameters
    
    Parameters
    ----------
    P : float or array
        Pressure [Pa]
    T : float or array
        Temperature [K]
    RH : float or array
        Relative humidity [0-1]
        
    Raises
    ------
    ValidationError
        If parameters are out of physical range
    """
    # Pressure range (0-2000 hPa)
    P_min, P_max = 50000, 110000  # Pa (500-1100 hPa)
    
    if np.any(P < P_min) or np.any(P > P_max):
        raise ValidationError(f"Pressure out of range [{P_min}, {P_max}] Pa")
    
    # Temperature range (180-330 K)
    T_min, T_max = 180, 330  # K
    
    if np.any(T < T_min) or np.any(T > T_max):
        raise ValidationError(f"Temperature out of range [{T_min}, {T_max}] K")
    
    # Relative humidity range
    if np.any(RH < 0) or np.any(RH > 1):
        raise ValidationError(f"Relative humidity must be in [0, 1], got {RH}")


def validate_wavelength(wavelength: Union[float, np.ndarray]) -> None:
    """
    Validate wavelength
    
    Parameters
    ----------
    wavelength : float or array
        Wavelength [μm]
        
    Raises
    ------
    ValidationError
        If wavelength out of range
    """
    wav_min, wav_max = 0.2, 20  # μm (UV to thermal IR)
    
    if np.any(wavelength < wav_min) or np.any(wavelength > wav_max):
        raise ValidationError(f"Wavelength out of range [{wav_min}, {wav_max}] μm")


def validate_cn2(Cn2: float) -> None:
    """
    Validate refractive index structure parameter
    
    Parameters
    ----------
    Cn2 : float
        Cn2 [m^(-2/3)]
        
    Raises
    ------
    ValidationError
        If Cn2 out of physical range
    """
    Cn2_min, Cn2_max = 1e-18, 1e-10  # m^(-2/3)
    
    if Cn2 < Cn2_min or Cn2 > Cn2_max:
        raise ValidationError(f"Cn2 out of range [{Cn2_min}, {Cn2_max}] m^(-2/3)")


def validate_path_length(L: float) -> None:
    """
    Validate optical path length
    
    Parameters
    ----------
    L : float
        Path length [m]
        
    Raises
    ------
    ValidationError
        If path length out of range
    """
    L_min, L_max = 1, 100000  # m (1 m to 100 km)
    
    if L < L_min or L > L_max:
        raise ValidationError(f"Path length out of range [{L_min}, {L_max}] m")


def validate_aerosol_parameters(r_modal: float, N: float, m: complex) -> None:
    """
    Validate aerosol mode parameters
    
    Parameters
    ----------
    r_modal : float
        Modal radius [μm]
    N : float
        Number concentration [cm⁻³]
    m : complex
        Complex refractive index
        
    Raises
    ------
    ValidationError
        If parameters out of physical range
    """
    # Radius range (0.001-100 μm)
    if r_modal < 0.001 or r_modal > 100:
        raise ValidationError(f"Modal radius out of range [0.001, 100] μm")
    
    # Concentration range (0-10^6 cm⁻³)
    if N < 0 or N > 1e6:
        raise ValidationError(f"Number concentration out of range [0, 1e6] cm⁻³")
    
    # Refractive index real part (1.0-2.0)
    if m.real < 1.0 or m.real > 2.0:
        raise ValidationError(f"Refractive index real part out of range [1.0, 2.0]")
    
    # Refractive index imaginary part (0-1)
    if m.imag < 0 or m.imag > 1:
        raise ValidationError(f"Refractive index imaginary part out of range [0, 1]")
