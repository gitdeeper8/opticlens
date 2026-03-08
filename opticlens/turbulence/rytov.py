"""
Rytov theory for optical turbulence
Refractive index structure parameter, scintillation, Fried parameter
"""

import numpy as np
from typing import Optional, Union, Tuple
from scipy import integrate
from opticlens.utils.constants import *


class RytovTurbulence:
    """
    Optical turbulence calculations based on Rytov theory
    
    Implements Kolmogorov turbulence statistics for refractive index fluctuations
    and their effect on optical propagation.
    """
    
    def __init__(self, wavelength: float = 0.55):
        """
        Parameters
        ----------
        wavelength : float
            Optical wavelength [μm]
        """
        self.wavelength = wavelength  # μm
        self.k = 2 * np.pi / (wavelength * 1e-6)  # wavenumber [m⁻¹]
    
    def estimate_cn2(self, 
                    T: float,
                    P: float,
                    height: float = 10,
                    wind_speed: Optional[float] = None,
                    solar_flux: Optional[float] = None) -> float:
        """
        Estimate Cn2 from meteorological parameters
        
        Parameters
        ----------
        T : float
            Temperature [K]
        P : float
            Pressure [Pa]
        height : float
            Height above ground [m]
        wind_speed : float, optional
            Wind speed [m/s]
        solar_flux : float, optional
            Solar flux [W/m²]
            
        Returns
        -------
        float
            Estimated Cn2 [m^(-2/3)]
        """
        # Hufnagel-Valley boundary layer model
        # Cn2(h) = A·exp(-h/100) + B·(h/1000)^10·exp(-h/1500) + C·exp(-h/1000)
        
        # Boundary layer term (strongest near ground)
        A = 1.7e-14  # Boundary layer strength
        
        # Tropospheric term
        B = 3.2e-17  # Tropospheric strength
        
        # Free atmosphere term
        C = 1.0e-16  # Free atmosphere strength
        
        # Temperature structure parameter (simplified)
        if solar_flux is not None:
            # Daytime convection
            CT2 = 0.1 * (solar_flux / 1000) * height**(-2/3)
        else:
            # Nighttime or neutral
            CT2 = 1e-6 * height**(-2/3)
        
        # Convert CT2 to Cn2
        # Cn2 = (79e-6 * P/T^2)^2 * CT2
        dn_dT = 79e-6 * P / T**2
        Cn2 = (dn_dT**2) * CT2
        
        # Add Hufnagel-Valley terms
        Cn2 += A * np.exp(-height/100)
        Cn2 += B * (height/1000)**10 * np.exp(-height/1500)
        Cn2 += C * np.exp(-height/1000)
        
        return max(Cn2, 1e-18)  # Floor at 1e-18
    
    def scintillation_index(self, 
                           Cn2: Union[float, np.ndarray],
                           path_length: float,
                           spherical_wave: bool = False) -> float:
        """
        Compute Rytov scintillation index σχ²
        
        Parameters
        ----------
        Cn2 : float or array
            Refractive index structure parameter [m^(-2/3)]
        path_length : float
            Propagation path length [m]
        spherical_wave : bool
            True for spherical wave, False for plane wave
            
        Returns
        -------
        float
            Log-amplitude variance σχ²
        """
        if spherical_wave:
            # Spherical wave scintillation index
            # σχ² = 0.124 * k^(7/6) * Cn2 * L^(11/6)
            sigma2 = 0.124 * self.k**(7/6) * Cn2 * path_length**(11/6)
        else:
            # Plane wave scintillation index (Rytov formula)
            # σχ² = 0.563 * k^(7/6) * Cn2 * L^(11/6)
            sigma2 = 0.563 * self.k**(7/6) * Cn2 * path_length**(11/6)
        
        # Rytov theory valid only for weak fluctuations (σχ² < 0.3)
        # For stronger fluctuations, use empirical saturation
        if isinstance(sigma2, np.ndarray):
            sigma2[sigma2 > 0.3] = 0.3 + 0.5 * np.log(sigma2[sigma2 > 0.3] / 0.3)
        elif sigma2 > 0.3:
            sigma2 = 0.3 + 0.5 * np.log(sigma2 / 0.3)
        
        return sigma2
    
    def fried_parameter(self, 
                       Cn2: Union[float, np.ndarray],
                       zenith_angle: float = 0) -> float:
        """
        Compute Fried coherence length r0
        
        Parameters
        ----------
        Cn2 : float or array
            Refractive index structure parameter [m^(-2/3)]
        zenith_angle : float
            Zenith angle [deg]
            
        Returns
        -------
        float
            Fried parameter [m]
        """
        sec_zeta = 1.0 / np.cos(zenith_angle * DEG2RAD)
        
        # For constant Cn2 along path
        # r0 = [0.423 * k^2 * sec(ζ) * Cn2 * L]^(-3/5)
        if isinstance(Cn2, (int, float)):
            # Assume path length L = 20 km for astronomical seeing
            L = 20000  # m
            r0 = (0.423 * self.k**2 * sec_zeta * Cn2 * L)**(-3/5)
        else:
            # Cn2 profile provided
            # r0 = [0.423 * k^2 * sec(ζ) * ∫ Cn2(z) dz]^(-3/5)
            integral = np.trapz(Cn2)
            r0 = (0.423 * self.k**2 * sec_zeta * integral)**(-3/5)
        
        return r0
    
    def isoplanatic_angle(self, Cn2_profile: np.ndarray, z_profile: np.ndarray) -> float:
        """
        Compute isoplanatic angle θ0
        
        Parameters
        ----------
        Cn2_profile : ndarray
            Cn2 profile [m^(-2/3)]
        z_profile : ndarray
            Height profile [m]
            
        Returns
        -------
        float
            Isoplanatic angle [arcsec]
        """
        # θ0 = [2.91 * k^2 * ∫ Cn2(z) * z^(5/3) dz]^(-3/5)
        integrand = Cn2_profile * z_profile**(5/3)
        integral = np.trapz(integrand, z_profile)
        
        theta0_rad = (2.91 * self.k**2 * integral)**(-3/5)
        theta0_arcsec = theta0_rad * RAD2DEG * 3600
        
        return theta0_arcsec
    
    def coherence_time(self, 
                      Cn2: Union[float, np.ndarray],
                      wind_speed: Union[float, np.ndarray]) -> float:
        """
        Compute atmospheric coherence time τ0
        
        Parameters
        ----------
        Cn2 : float or array
            Refractive index structure parameter
        wind_speed : float or array
            Wind speed [m/s]
            
        Returns
        -------
        float
            Coherence time [s]
        """
        # τ0 = 0.314 * r0 / v_wind
        r0 = self.fried_parameter(Cn2)
        
        if isinstance(wind_speed, np.ndarray):
            # Average weighted by Cn2
            v_avg = np.trapz(wind_speed * Cn2) / np.trapz(Cn2)
        else:
            v_avg = wind_speed
        
        tau0 = 0.314 * r0 / max(v_avg, 0.1)
        
        return tau0
    
    def greenwood_frequency(self, 
                           Cn2_profile: np.ndarray,
                           wind_profile: np.ndarray,
                           z_profile: np.ndarray) -> float:
        """
        Compute Greenwood frequency fG for adaptive optics
        
        Parameters
        ----------
        Cn2_profile : ndarray
            Cn2 profile [m^(-2/3)]
        wind_profile : ndarray
            Wind speed profile [m/s]
        z_profile : ndarray
            Height profile [m]
            
        Returns
        -------
        float
            Greenwood frequency [Hz]
        """
        # fG = [0.102 * k^2 * ∫ Cn2(z) * v(z)^(5/3) dz]^(3/5)
        integrand = Cn2_profile * wind_profile**(5/3)
        integral = np.trapz(integrand, z_profile)
        
        fG = (0.102 * self.k**2 * integral)**(3/5)
        
        return fG
    
    def cn2_from_scintillation(self,
                              scint_index: float,
                              path_length: float,
                              spherical_wave: bool = False) -> float:
        """
        Invert scintillation measurement to get Cn2
        
        Parameters
        ----------
        scint_index : float
            Measured scintillation index σχ²
        path_length : float
            Propagation path length [m]
        spherical_wave : bool
            True for spherical wave
            
        Returns
        -------
        float
            Estimated Cn2 [m^(-2/3)]
        """
        if spherical_wave:
            Cn2 = scint_index / (0.124 * self.k**(7/6) * path_length**(11/6))
        else:
            Cn2 = scint_index / (0.563 * self.k**(7/6) * path_length**(11/6))
        
        return Cn2
    
    def rytov_variance_profile(self,
                              Cn2_profile: np.ndarray,
                              z_profile: np.ndarray,
                              source_distance: float) -> np.ndarray:
        """
        Compute Rytov variance as a function of distance
        
        Parameters
        ----------
        Cn2_profile : ndarray
            Cn2 profile [m^(-2/3)]
        z_profile : ndarray
            Distance profile [m]
        source_distance : float
            Distance to source [m]
            
        Returns
        -------
        ndarray
            Cumulative Rytov variance profile
        """
        # For plane wave
        # σχ²(z) = 0.563 * k^(7/6) * ∫ Cn2(ζ) * ζ^(5/6) * (1 - ζ/L)^(5/6) dζ
        
        n_points = len(z_profile)
        sigma2_profile = np.zeros(n_points)
        
        for i in range(1, n_points):
            z_slice = z_profile[:i+1]
            Cn2_slice = Cn2_profile[:i+1]
            
            # Integrand
            integrand = Cn2_slice * z_slice**(5/6) * (1 - z_slice/source_distance)**(5/6)
            integral = np.trapz(integrand, z_slice)
            
            sigma2_profile[i] = 0.563 * self.k**(7/6) * integral
        
        return sigma2_profile
