"""
Mie scattering calculations for spherical aerosol particles
Exact solution to Maxwell's equations for homogeneous spheres
"""

import numpy as np
from scipy.special import spherical_jn, spherical_yn
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass


@dataclass
class AerosolMode:
    """Aerosol size mode for polydisperse populations"""
    r_modal: float      # μm
    sigma: float        # geometric standard deviation
    N: float            # number concentration [cm⁻³]
    m: complex          # complex refractive index


class MieScattering:
    """
    Mie scattering theory for spherical particles
    
    Implements exact solution to Maxwell's equations for plane wave
    incident on homogeneous sphere.
    """
    
    def __init__(self, wavelengths: np.ndarray):
        """
        Parameters
        ----------
        wavelengths : ndarray
            Wavelengths [μm]
        """
        self.wavelengths = np.asarray(wavelengths)
        
    def compute_bulk_properties(self, 
                                aerosol_modes: List[AerosolMode],
                                r_min: float = 0.001,
                                r_max: float = 10.0,
                                n_r: int = 100) -> Dict:
        """
        Compute bulk optical properties for polydisperse aerosol population
        
        Parameters
        ----------
        aerosol_modes : list of AerosolMode
            Aerosol size modes
        r_min : float
            Minimum radius [μm]
        r_max : float
            Maximum radius [μm]
        n_r : int
            Number of radius bins
            
        Returns
        -------
        dict
            Bulk optical properties
        """
        # Radius grid (log-spaced for better resolution of small particles)
        r_grid = np.logspace(np.log10(r_min), np.log10(r_max), n_r)
        
        # Initialize arrays
        n_wav = len(self.wavelengths)
        beta_ext = np.zeros(n_wav)
        beta_scat = np.zeros(n_wav)
        g = np.zeros(n_wav)
        P_theta = []  # Will store phase functions
        
        # For each wavelength
        for i, wav in enumerate(self.wavelengths):
            Q_ext_wav = 0
            Q_scat_wav = 0
            g_wav = 0
            total_N = 0
            
            # Sum over aerosol modes
            for mode in aerosol_modes:
                # Size distribution (lognormal)
                dN_dr = self._lognormal_distribution(r_grid, mode.r_modal, mode.sigma)
                dN_dr *= mode.N / np.trapz(dN_dr, r_grid)
                
                # For each radius bin
                for j, r in enumerate(r_grid):
                    if r == 0:
                        continue
                        
                    # Size parameter
                    x = 2 * np.pi * r / wav
                    
                    # Mie efficiencies for this size
                    Q_ext_j, Q_scat_j, g_j = self._single_particle(x, mode.m)
                    
                    # Weight by cross-section and number
                    cross_section = np.pi * r**2
                    weight = dN_dr[j] * cross_section
                    
                    Q_ext_wav += Q_ext_j * weight
                    Q_scat_wav += Q_scat_j * weight
                    g_wav += g_j * Q_scat_j * weight
                    total_N += dN_dr[j]
            
            # Normalize
            if total_N > 0:
                beta_ext[i] = Q_ext_wav / total_N
                beta_scat[i] = Q_scat_wav / total_N
                if Q_scat_wav > 0:
                    g[i] = g_wav / Q_scat_wav
            
            # Phase function at representative size (r_eff)
            r_eff = self._effective_radius(aerosol_modes)
            x_eff = 2 * np.pi * r_eff / wav
            m_eff = self._effective_refractive_index(aerosol_modes)
            _, _, P_theta_wav = self._single_particle(x_eff, m_eff, return_phase=True)
            P_theta.append(P_theta_wav)
        
        return {
            'beta_ext': beta_ext,
            'beta_scat': beta_scat,
            'asymmetry': g,
            'phase_function': P_theta,
            'wavelengths': self.wavelengths
        }
    
    def _single_particle(self, 
                         x: float, 
                         m: complex,
                         return_phase: bool = False,
                         n_theta: int = 181) -> Tuple:
        """
        Compute Mie efficiencies for a single particle
        
        Parameters
        ----------
        x : float
            Size parameter
        m : complex
            Complex refractive index
        return_phase : bool
            Whether to return phase function
        n_theta : int
            Number of scattering angles
            
        Returns
        -------
        tuple
            (Q_ext, Q_scat, g) or (Q_ext, Q_scat, g, P_theta)
        """
        # Number of terms needed for convergence
        n_max = int(x + 4 * x**(1/3) + 2)
        
        # Riccati-Bessel functions
        n_range = np.arange(1, n_max + 1)
        
        # Spherical Bessel functions
        psi_n = spherical_jn(n_range, x)
        psi_n_minus = spherical_jn(n_range - 1, x)
        xi_n = psi_n + 1j * spherical_yn(n_range, x)
        xi_n_minus = spherical_jn(n_range - 1, x) + 1j * spherical_yn(n_range - 1, x)
        
        # Derivatives
        psi_n_prime = psi_n_minus - n_range * psi_n / x
        xi_n_prime = xi_n_minus - n_range * xi_n / x
        
        # Arguments with m*x
        mx = m * x
        psi_n_mx = spherical_jn(n_range, mx)
        psi_n_minus_mx = spherical_jn(n_range - 1, mx)
        psi_n_prime_mx = psi_n_minus_mx - n_range * psi_n_mx / mx
        
        # Mie coefficients
        a_n_num = psi_n_prime_mx * psi_n - m * psi_n_mx * psi_n_prime
        a_n_den = psi_n_prime_mx * xi_n - m * psi_n_mx * xi_n_prime
        a_n = a_n_num / a_n_den
        
        b_n_num = m * psi_n_prime_mx * psi_n - psi_n_mx * psi_n_prime
        b_n_den = m * psi_n_prime_mx * xi_n - psi_n_mx * xi_n_prime
        b_n = b_n_num / b_n_den
        
        # Efficiencies
        Q_ext = (2 / x**2) * np.sum((2*n_range + 1) * np.real(a_n + b_n))
        Q_scat = (2 / x**2) * np.sum((2*n_range + 1) * (np.abs(a_n)**2 + np.abs(b_n)**2))
        
        # Asymmetry parameter
        g = self._compute_asymmetry(a_n, b_n, n_range, x)
        
        if return_phase:
            # Phase function at requested angles
            theta = np.linspace(0, np.pi, n_theta)
            P_theta = self._phase_function(theta, a_n, b_n, n_range, x)
            return Q_ext, Q_scat, g, P_theta
        
        return Q_ext, Q_scat, g
    
    def _compute_asymmetry(self, a_n: np.ndarray, b_n: np.ndarray, 
                           n_range: np.ndarray, x: float) -> float:
        """Compute asymmetry parameter g = <cosθ>"""
        n = n_range
        term1 = np.sum((2*n + 1) / (n * (n + 1)) * np.real(a_n * np.conj(b_n)))
        
        term2_num = n * (n + 2) / (n + 1)
        term2 = np.sum(term2_num * np.real(a_n * np.conj(a_n+1) + b_n * np.conj(b_n+1)))
        
        Q_scat = (2 / x**2) * np.sum((2*n + 1) * (np.abs(a_n)**2 + np.abs(b_n)**2))
        
        if Q_scat > 0:
            g = (4 / (x**2 * Q_scat)) * (term1 + term2)
        else:
            g = 0
            
        return g
    
    def _phase_function(self, theta: np.ndarray, a_n: np.ndarray, 
                        b_n: np.ndarray, n_range: np.ndarray, x: float) -> np.ndarray:
        """Compute scattering phase function P(θ)"""
        from scipy.special import lpmv
        
        n = n_range
        cos_theta = np.cos(theta)
        
        # Legendre polynomials and their derivatives
        pi_n = np.zeros((len(n), len(theta)))
        tau_n = np.zeros((len(n), len(theta)))
        
        pi_n[0] = 1
        pi_n[1] = 3 * cos_theta
        
        for i in range(2, len(n)):
            n_val = i + 1
            pi_n[i] = ((2*n_val - 1) / (n_val - 1)) * cos_theta * pi_n[i-1] - \
                      (n_val / (n_val - 1)) * pi_n[i-2]
        
        tau_n[0] = cos_theta
        tau_n[1] = 3 * cos_theta**2 - 1.5
        
        for i in range(2, len(n)):
            n_val = i + 1
            tau_n[i] = n_val * cos_theta * pi_n[i] - (n_val + 1) * pi_n[i-1]
        
        # Amplitude functions
        S1 = np.zeros(len(theta), dtype=complex)
        S2 = np.zeros(len(theta), dtype=complex)
        
        for i in range(len(n)):
            n_val = i + 1
            factor = (2*n_val + 1) / (n_val * (n_val + 1))
            S1 += factor * (a_n[i] * pi_n[i] + b_n[i] * tau_n[i])
            S2 += factor * (a_n[i] * tau_n[i] + b_n[i] * pi_n[i])
        
        # Phase function
        P = (np.abs(S1)**2 + np.abs(S2)**2) / (2 * x**2 * Q_scat)
        
        return P
    
    def _lognormal_distribution(self, r: np.ndarray, r_modal: float, sigma: float) -> np.ndarray:
        """Lognormal size distribution"""
        return (1 / (np.sqrt(2*np.pi) * np.log(sigma) * r)) * \
               np.exp(-(np.log(r) - np.log(r_modal))**2 / (2 * np.log(sigma)**2))
    
    def _effective_radius(self, modes: List[AerosolMode]) -> float:
        """Compute effective radius for polydisperse population"""
        # Simplified: volume-weighted average
        total_volume = 0
        total_N = 0
        
        for mode in modes:
            volume = (4/3) * np.pi * mode.r_modal**3
            total_volume += volume * mode.N
            total_N += mode.N
            
        if total_N > 0:
            return (total_volume / total_N / ((4/3)*np.pi))**(1/3)
        else:
            return 0.1
    
    def _effective_refractive_index(self, modes: List[AerosolMode]) -> complex:
        """Compute effective refractive index for polydisperse population"""
        # Volume-weighted average
        total_volume = 0
        weighted_m = 0
        
        for mode in modes:
            volume = mode.r_modal**3 * mode.N
            total_volume += volume
            weighted_m += volume * mode.m
            
        if total_volume > 0:
            return weighted_m / total_volume
        else:
            return 1.5 + 0.01j
