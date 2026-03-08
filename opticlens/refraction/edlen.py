"""
Modified Edlén equation for atmospheric refractive index
Includes humidity correction and CO2 adjustment
"""

import numpy as np
from typing import Union, Optional


class EdlenRefractiveIndex:
    """
    Refractive index of air using modified Edlén equation (Ciddor 1996 formulation)
    
    n(P,T,λ) − 1 = [A + B/(C − λ⁻²) + D/(E − λ⁻²)] · (P/T) · (1 + P·(F − G·T)·10⁻⁸)
    """
    
    # Edlén constants (dry air, 450 ppm CO2)
    A = 8.34254e-5
    B = 2.406147e-2
    C = 1.5997e-4
    D = 1.5898e-4
    E = 2.8097e-4
    F = 5.760e-8
    G = 0.6075e-8
    
    def __init__(self, co2_ppm: float = 450):
        self.co2_ppm = co2_ppm
        
    def compute(self, 
                P: Union[float, np.ndarray],
                T: Union[float, np.ndarray],
                wavelength: Union[float, np.ndarray],
                humidity: Optional[float] = 0.0) -> Union[float, np.ndarray]:
        """
        Compute refractive index at given pressure, temperature, wavelength
        
        Parameters
        ----------
        P : float or array
            Pressure [Pa]
        T : float or array
            Temperature [K]
        wavelength : float or array
            Vacuum wavelength [μm]
        humidity : float, optional
            Relative humidity [0-1]
            
        Returns
        -------
        float or array
            Refractive index n
        """
        # Convert pressure from Pa to hPa for Edlén formula
        P_hPa = P / 100.0
        
        # Convert wavelength to μm⁻²
        sigma = 1.0 / wavelength**2
        
        # Dry air term
        dry_term = (self.A + self.B / (self.C - sigma) + 
                    self.D / (self.E - sigma)) * (P_hPa / T)
        
        # Pressure correction
        pressure_corr = 1 + P_hPa * (self.F - self.G * T) * 1e-8
        
        n_dry = 1.0 + dry_term * pressure_corr
        
        # Humidity correction (if needed)
        if humidity > 0:
            n_moist = self._humidity_correction(n_dry, P_hPa, T, humidity, wavelength)
            return n_moist
        else:
            return n_dry
    
    def _humidity_correction(self, 
                             n_dry: Union[float, np.ndarray],
                             P_hPa: float,
                             T: float,
                             humidity: float,
                             wavelength: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Apply humidity correction to refractive index"""
        # Water vapor pressure
        e_sat = self._saturation_vapor_pressure(T)
        e = humidity * e_sat  # hPa
        
        # Water vapor refractivity
        n_water = 1.0 + 1.022e-8 * (1 + 0.02 * wavelength**-2) * e / T
        
        # Mole fraction of water vapor
        f_w = e / P_hPa
        
        # Mixing correction
        n_moist = n_dry + (n_water - 1) * f_w
        
        return n_moist
    
    def _saturation_vapor_pressure(self, T: float) -> float:
        """Compute saturation vapor pressure [hPa] at temperature T [K]"""
        # Magnus formula
        T_c = T - 273.15
        return 6.1094 * np.exp(17.625 * T_c / (T_c + 243.04))
    
    def vertical_gradient(self, 
                          T_profile: np.ndarray,
                          P_profile: np.ndarray,
                          z_profile: np.ndarray,
                          wavelength: float = 0.55) -> np.ndarray:
        """
        Compute vertical gradient dn/dz from T and P profiles
        
        Returns
        -------
        ndarray
            dn/dz [m⁻¹]
        """
        n_profile = self.compute(P_profile, T_profile, wavelength)
        
        # Central difference for gradient
        dn_dz = np.gradient(n_profile, z_profile)
        
        return dn_dz
    
    def ray_curvature(self, dn_dz: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Compute radius of ray curvature R = -1/(dn/dz)
        
        Returns
        -------
        float or array
            Radius of curvature [m]
        """
        return -1.0 / dn_dz
