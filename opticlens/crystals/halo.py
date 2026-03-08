"""
Ice crystal halo simulations
22° and 46° halos from hexagonal ice crystals
"""

import numpy as np
from typing import Tuple, Dict, Optional, List
from dataclasses import dataclass
from opticlens.utils.constants import *


@dataclass
class IceCrystal:
    """Ice crystal parameters"""
    shape: str  # 'plate', 'column', 'bullet', 'irregular'
    aspect_ratio: float = 1.0  # length/diameter
    orientation: str = 'random'  # 'random', 'horizontal', 'parry'
    size: float = 50.0  # μm


class IceCrystalHalo:
    """
    Simulation of atmospheric halos from ice crystals
    
    Implements ray tracing through hexagonal ice crystals to compute
    halo intensity as function of scattering angle.
    """
    
    def __init__(self):
        # Refractive index of ice (visible wavelengths)
        self.n_ice = 1.309  # at λ = 0.55 μm
        
        # Prism angles for hexagonal crystal
        self.prism_angle_60 = 60 * DEG2RAD  # 60° prism (22° halo)
        self.prism_angle_90 = 90 * DEG2RAD  # 90° prism (46° halo)
        
    def minimum_deviation_angle(self, prism_angle: float) -> float:
        """
        Compute minimum deviation angle for a prism
        
        Parameters
        ----------
        prism_angle : float
            Prism apex angle [rad]
            
        Returns
        -------
        float
            Minimum deviation angle [deg]
        """
        # δ_min = 2·arcsin[n·sin(A/2)] − A
        delta_min = 2 * np.arcsin(self.n_ice * np.sin(prism_angle / 2)) - prism_angle
        
        return delta_min * RAD2DEG
    
    def halo_22(self, theta: np.ndarray) -> np.ndarray:
        """
        Compute intensity profile for 22° halo
        
        Parameters
        ----------
        theta : ndarray
            Scattering angles [deg]
            
        Returns
        -------
        ndarray
            Normalized intensity
        """
        theta_rad = theta * DEG2RAD
        
        # Minimum deviation angle
        delta_min = self.minimum_deviation_angle(self.prism_angle_60)
        delta_min_rad = delta_min * DEG2RAD
        
        # Intensity profile (simplified geometric optics)
        intensity = np.zeros_like(theta_rad)
        
        # Halo appears for angles >= minimum deviation
        mask = theta_rad >= delta_min_rad
        
        # Intensity decays with angle beyond minimum
        intensity[mask] = np.exp(-(theta_rad[mask] - delta_min_rad) / (2 * DEG2RAD))
        
        # Normalize
        if np.sum(intensity) > 0:
            intensity /= np.max(intensity)
        
        return intensity
    
    def halo_46(self, theta: np.ndarray) -> np.ndarray:
        """
        Compute intensity profile for 46° halo (from 90° prisms)
        
        Parameters
        ----------
        theta : ndarray
            Scattering angles [deg]
            
        Returns
        -------
        ndarray
            Normalized intensity
        """
        theta_rad = theta * DEG2RAD
        
        # Minimum deviation angle for 90° prism
        delta_min = self.minimum_deviation_angle(self.prism_angle_90)
        delta_min_rad = delta_min * DEG2RAD
        
        # Intensity profile
        intensity = np.zeros_like(theta_rad)
        
        mask = theta_rad >= delta_min_rad
        intensity[mask] = np.exp(-(theta_rad[mask] - delta_min_rad) / (3 * DEG2RAD))
        
        if np.sum(intensity) > 0:
            intensity /= np.max(intensity)
        
        return intensity
    
    def circumzenithal_arc(self, theta: np.ndarray, solar_elevation: float) -> np.ndarray:
        """
        Compute circumzenithal arc intensity
        
        Parameters
        ----------
        theta : ndarray
            Scattering angles [deg]
        solar_elevation : float
            Solar elevation angle [deg]
            
        Returns
        -------
        ndarray
            Normalized intensity
        """
        # Circumzenithal arc appears at specific solar elevations ( < 32°)
        if abs(solar_elevation) > 32:
            return np.zeros_like(theta)
        
        theta_rad = theta * DEG2RAD
        elevation_rad = solar_elevation * DEG2RAD
        
        # Arc position depends on solar elevation
        arc_angle = 90 - solar_elevation  # deg
        arc_angle_rad = arc_angle * DEG2RAD
        
        # Gaussian around arc angle
        intensity = np.exp(-(theta_rad - arc_angle_rad)**2 / (2 * DEG2RAD**2))
        
        return intensity
    
    def parhelic_circle(self, theta: np.ndarray) -> np.ndarray:
        """
        Compute parhelic circle (horizontal through sun)
        
        Parameters
        ----------
        theta : ndarray
            Scattering angles [deg]
            
        Returns
        -------
        ndarray
            Normalized intensity
        """
        theta_rad = theta * DEG2RAD
        
        # Parhelic circle at 0° elevation
        intensity = np.exp(-theta_rad**2 / (10 * DEG2RAD**2))
        
        return intensity
    
    def sun_dogs(self, theta: np.ndarray, solar_elevation: float) -> np.ndarray:
        """
        Compute parhelia (sun dogs) intensity
        
        Parameters
        ----------
        theta : ndarray
            Scattering angles [deg]
        solar_elevation : float
            Solar elevation angle [deg]
            
        Returns
        -------
        ndarray
            Normalized intensity
        """
        theta_rad = theta * DEG2RAD
        elevation_rad = solar_elevation * DEG2RAD
        
        # Sun dogs appear at 22° from sun, same elevation
        sun_dog_angle = 22 * DEG2RAD
        
        intensity = np.exp(-(theta_rad - sun_dog_angle)**2 / (3 * DEG2RAD**2))
        intensity *= np.exp(-(elevation_rad)**2 / (5 * DEG2RAD**2))
        
        return intensity
    
    def complete_halo_pattern(self, 
                            theta: np.ndarray,
                            solar_elevation: float = 30,
                            crystal_mix: Optional[Dict[str, float]] = None) -> Dict[str, np.ndarray]:
        """
        Compute complete halo pattern with multiple components
        
        Parameters
        ----------
        theta : ndarray
            Scattering angles [deg]
        solar_elevation : float
            Solar elevation angle [deg]
        crystal_mix : dict, optional
            Fraction of each crystal type
            e.g., {'plate': 0.6, 'column': 0.3, 'bullet': 0.1}
            
        Returns
        -------
        dict
            Intensity for each halo component
        """
        if crystal_mix is None:
            crystal_mix = {'plate': 0.5, 'column': 0.5}
        
        results = {}
        
        # Always present components
        results['halo_22'] = self.halo_22(theta)
        results['halo_46'] = self.halo_46(theta)
        
        # Components that depend on crystal orientation
        if crystal_mix.get('plate', 0) > 0:
            results['circumzenithal'] = self.circumzenithal_arc(theta, solar_elevation)
            results['parhelic'] = self.parhelic_circle(theta)
        
        if crystal_mix.get('column', 0) > 0:
            results['sun_dogs'] = self.sun_dogs(theta, solar_elevation)
        
        # Weight by crystal mix
        for key in results:
            if 'halo' in key:
                results[key] *= 1.0  # Always present
            elif key == 'circumzenithal':
                results[key] *= crystal_mix.get('plate', 0)
            elif key == 'parhelic':
                results[key] *= crystal_mix.get('plate', 0)
            elif key == 'sun_dogs':
                results[key] *= crystal_mix.get('column', 0)
        
        return results
    
    def wavelength_dependence(self, wavelength: float, base_intensity: np.ndarray) -> np.ndarray:
        """
        Apply wavelength-dependent scattering (dispersion)
        
        Parameters
        ----------
        wavelength : float
            Wavelength [μm]
        base_intensity : ndarray
            Intensity at reference wavelength
            
        Returns
        -------
        ndarray
            Intensity at specified wavelength
        """
        # Refractive index variation with wavelength
        # Cauchy's formula for ice
        lambda_ref = 0.55  # μm
        n_ref = self.n_ice
        
        # Dispersion coefficient (approximate)
        dn_dlambda = -0.02  # Δn per μm
        
        n = n_ref + dn_dlambda * (wavelength - lambda_ref)
        
        # Scale intensity based on refractive index
        # Simplified: intensity proportional to (n-1)^2
        intensity_scale = ((n - 1) / (n_ref - 1))**2
        
        return base_intensity * intensity_scale
    
    def generate_sky_image(self, 
                          sun_altitude: float = 30,
                          sun_azimuth: float = 0,
                          resolution: Tuple[int, int] = (360, 180)) -> np.ndarray:
        """
        Generate 2D sky image of halos
        
        Parameters
        ----------
        sun_altitude : float
            Sun altitude [deg]
        sun_azimuth : float
            Sun azimuth [deg]
        resolution : tuple
            (azimuth_bins, elevation_bins)
            
        Returns
        -------
        ndarray
            2D image of sky intensity
        """
        n_az, n_el = resolution
        
        azimuth = np.linspace(0, 360, n_az)
        elevation = np.linspace(0, 90, n_el)
        
        Az, El = np.meshgrid(azimuth * DEG2RAD, elevation * DEG2RAD)
        
        # Angular distance from sun
        sun_az_rad = sun_azimuth * DEG2RAD
        sun_el_rad = sun_altitude * DEG2RAD
        
        cos_theta = np.sin(El) * np.sin(sun_el_rad) + \
                   np.cos(El) * np.cos(sun_el_rad) * np.cos(Az - sun_az_rad)
        cos_theta = np.clip(cos_theta, -1, 1)
        theta = np.arccos(cos_theta) * RAD2DEG
        
        # Compute halo pattern
        halos = self.complete_halo_pattern(theta.flatten(), sun_altitude)
        
        # Combine components
        image = np.zeros_like(theta.flatten())
        for key, intensity in halos.items():
            image += intensity
        
        image = image.reshape(theta.shape)
        
        return image
