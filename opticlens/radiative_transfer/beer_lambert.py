"""
Beer-Lambert-Bouguer law for radiative transfer
Aerosol optical depth, transmission, and extinction
"""

import numpy as np
from typing import Optional, Union, Tuple, List
from scipy import integrate
from opticlens.utils.constants import *


class BeerLambert:
    """
    Beer-Lambert-Bouguer law for atmospheric transmission
    
    I(λ) = I₀(λ) · exp[−τ(λ)]
    where τ(λ) = ∫ β_ext(z, λ) dz
    """
    
    def __init__(self):
        pass
    
    def optical_depth(self, 
                     extinction_coefficient: Union[float, np.ndarray],
                     layer_thickness: Union[float, np.ndarray],
                     path_length: Optional[float] = None) -> Union[float, np.ndarray]:
        """
        Compute optical depth from extinction coefficient
        
        Parameters
        ----------
        extinction_coefficient : float or array
            Volume extinction coefficient [m⁻¹]
        layer_thickness : float or array
            Layer thickness [m]
        path_length : float, optional
            Total path length (if None, use sum of layers)
            
        Returns
        -------
        float or array
            Optical depth τ
        """
        if path_length is not None:
            # Constant extinction along path
            return extinction_coefficient * path_length
        else:
            # Integrate over layers
            return np.sum(extinction_coefficient * layer_thickness)
    
    def transmission(self, optical_depth: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Compute transmission from optical depth
        
        Parameters
        ----------
        optical_depth : float or array
            Optical depth τ
            
        Returns
        -------
        float or array
            Transmission T = exp(-τ)
        """
        return np.exp(-optical_depth)
    
    def angstrom_exponent(self, 
                         tau1: float, 
                         tau2: float, 
                         lambda1: float, 
                         lambda2: float) -> float:
        """
        Compute Ångström exponent from optical depths at two wavelengths
        
        Parameters
        ----------
        tau1 : float
            Optical depth at lambda1
        tau2 : float
            Optical depth at lambda2
        lambda1 : float
            First wavelength [μm]
        lambda2 : float
            Second wavelength [μm]
            
        Returns
        -------
        float
            Ångström exponent α
        """
        # τ(λ) ∝ λ^(-α)
        alpha = -np.log(tau1 / tau2) / np.log(lambda1 / lambda2)
        return alpha
    
    def turbidity_coefficient(self, 
                             tau: float, 
                             lambda_ref: float = 1.0,
                             alpha: Optional[float] = None) -> float:
        """
        Compute Ångström turbidity coefficient β
        
        Parameters
        ----------
        tau : float
            Optical depth at lambda
        lambda_ref : float
            Reference wavelength [μm] (typically 1.0 μm)
        alpha : float, optional
            Ångström exponent (if None, use typical value)
            
        Returns
        -------
        float
            Turbidity coefficient β
        """
        if alpha is None:
            alpha = 1.3  # Typical continental aerosol
        
        # τ(λ) = β · (λ/λ₀)^(-α)
        beta = tau * (lambda_ref / 1.0)**alpha
        return beta
    
    def rayleigh_optical_depth(self, 
                              wavelength: Union[float, np.ndarray],
                              pressure: float = STANDARD_PRESSURE,
                              temperature: float = STANDARD_TEMPERATURE) -> Union[float, np.ndarray]:
        """
        Compute Rayleigh scattering optical depth from air molecules
        
        Parameters
        ----------
        wavelength : float or array
            Wavelength [μm]
        pressure : float
            Surface pressure [Pa]
        temperature : float
            Surface temperature [K]
            
        Returns
        -------
        float or array
            Rayleigh optical depth
        """
        # Hansen & Travis (1974) formula
        # τ_R(λ) = 0.008569 * λ^(-4) * (1 + 0.0113 * λ^(-2) + 0.00013 * λ^(-4)) * (P/P0)
        
        lambda_um = wavelength
        P0 = STANDARD_PRESSURE
        
        # Wavelength in μm
        term1 = lambda_um**(-4)
        term2 = 1 + 0.0113 * lambda_um**(-2) + 0.00013 * lambda_um**(-4)
        
        tau_R = 0.008569 * term1 * term2 * (pressure / P0)
        
        return tau_R
    
    def ozone_optical_depth(self, 
                           wavelength: Union[float, np.ndarray],
                           ozone_column: float = 300) -> Union[float, np.ndarray]:
        """
        Compute ozone absorption optical depth
        
        Parameters
        ----------
        wavelength : float or array
            Wavelength [μm]
        ozone_column : float
            Total ozone column [Dobson Units]
            
        Returns
        -------
        float or array
            Ozone optical depth
        """
        # Simplified ozone absorption cross-section
        # Strong absorption in Hartley (200-300 nm) and Huggins (300-360 nm) bands
        
        lambda_nm = wavelength * 1000
        
        if isinstance(lambda_nm, np.ndarray):
            tau_O3 = np.zeros_like(lambda_nm)
            
            # Hartley band (strong)
            mask_hartley = (lambda_nm >= 200) & (lambda_nm <= 300)
            tau_O3[mask_hartley] = 0.1 * ozone_column / 300 * \
                                   np.exp(-(lambda_nm[mask_hartley] - 250)**2 / 1000)
            
            # Huggins band (moderate)
            mask_huggins = (lambda_nm > 300) & (lambda_nm <= 360)
            tau_O3[mask_huggins] = 0.02 * ozone_column / 300 * \
                                    np.exp(-(lambda_nm[mask_huggins] - 320)**2 / 500)
            
            # Chappuis band (weak, visible)
            mask_chappuis = (lambda_nm > 450) & (lambda_nm <= 750)
            tau_O3[mask_chappuis] = 0.005 * ozone_column / 300 * \
                                     np.exp(-(lambda_nm[mask_chappuis] - 600)**2 / 10000)
        else:
            if 200 <= lambda_nm <= 300:
                tau_O3 = 0.1 * ozone_column / 300 * np.exp(-(lambda_nm - 250)**2 / 1000)
            elif 300 < lambda_nm <= 360:
                tau_O3 = 0.02 * ozone_column / 300 * np.exp(-(lambda_nm - 320)**2 / 500)
            elif 450 < lambda_nm <= 750:
                tau_O3 = 0.005 * ozone_column / 300 * np.exp(-(lambda_nm - 600)**2 / 10000)
            else:
                tau_O3 = 0.0
        
        return tau_O3
    
    def total_optical_depth(self,
                           aerosol_tau: Union[float, np.ndarray],
                           wavelength: Union[float, np.ndarray],
                           pressure: float = STANDARD_PRESSURE,
                           ozone_column: float = 300,
                           include_rayleigh: bool = True,
                           include_ozone: bool = True) -> Union[float, np.ndarray]:
        """
        Compute total atmospheric optical depth
        
        Parameters
        ----------
        aerosol_tau : float or array
            Aerosol optical depth
        wavelength : float or array
            Wavelength [μm]
        pressure : float
            Surface pressure [Pa]
        ozone_column : float
            Total ozone column [DU]
        include_rayleigh : bool
            Include Rayleigh scattering
        include_ozone : bool
            Include ozone absorption
            
        Returns
        -------
        float or array
            Total optical depth
        """
        tau_total = aerosol_tau
        
        if include_rayleigh:
            tau_total += self.rayleigh_optical_depth(wavelength, pressure)
        
        if include_ozone:
            tau_total += self.ozone_optical_depth(wavelength, ozone_column)
        
        return tau_total
    
    def layer_optical_depth(self,
                           extinction_profile: np.ndarray,
                           height_profile: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute cumulative optical depth profile
        
        Parameters
        ----------
        extinction_profile : ndarray
            Extinction coefficient profile [m⁻¹]
        height_profile : ndarray
            Height profile [m]
            
        Returns
        -------
        tuple
            (height_profile, cumulative_tau)
        """
        # Layer thicknesses
        dz = np.diff(height_profile)
        dz = np.append(dz, dz[-1])
        
        # Layer optical depths
        layer_tau = extinction_profile * dz
        
        # Cumulative optical depth from TOA to surface
        cumulative_tau = np.cumsum(layer_tau[::-1])[::-1]
        
        return height_profile, cumulative_tau
    
    def transmission_profile(self,
                           extinction_profile: np.ndarray,
                           height_profile: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute transmission profile
        
        Parameters
        ----------
        extinction_profile : ndarray
            Extinction coefficient profile [m⁻¹]
        height_profile : ndarray
            Height profile [m]
            
        Returns
        -------
        tuple
            (height_profile, transmission)
        """
        _, cumulative_tau = self.layer_optical_depth(extinction_profile, height_profile)
        transmission = np.exp(-cumulative_tau)
        
        return height_profile, transmission
