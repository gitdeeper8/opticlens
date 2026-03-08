"""
Unit tests for turbulence module
"""

import numpy as np
import pytest
from opticlens.turbulence.rytov import RytovTurbulence


class TestRytovTurbulence:
    """Test suite for turbulence calculations"""
    
    def setup_method(self):
        """Setup test instance"""
        self.turb = RytovTurbulence(wavelength=0.55)
    
    def test_scintillation_index_plane_wave(self):
        """Test plane wave scintillation index"""
        Cn2 = 1e-15
        L = 1000
        
        sigma2 = self.turb.scintillation_index(Cn2, L, spherical_wave=False)
        
        # Should be positive and less than 1 for weak turbulence
        assert sigma2 > 0
        assert sigma2 < 1
    
    def test_scintillation_index_spherical_wave(self):
        """Test spherical wave scintillation index"""
        Cn2 = 1e-15
        L = 1000
        
        sigma2_plane = self.turb.scintillation_index(Cn2, L, spherical_wave=False)
        sigma2_sphere = self.turb.scintillation_index(Cn2, L, spherical_wave=True)
        
        # Spherical wave scintillation should be smaller than plane wave
        assert sigma2_sphere < sigma2_plane
    
    def test_fried_parameter(self):
        """Test Fried parameter calculation"""
        Cn2 = 1e-15
        
        r0 = self.turb.fried_parameter(Cn2)
        
        # Typical r0 at good site: 10-20 cm
        assert 0.05 < r0 < 0.5
    
    def test_zenith_dependence(self):
        """Test zenith angle dependence of Fried parameter"""
        Cn2 = 1e-15
        
        r0_zenith = self.turb.fried_parameter(Cn2, zenith_angle=0)
        r0_60deg = self.turb.fried_parameter(Cn2, zenith_angle=60)
        
        # r0 decreases with zenith angle
        assert r0_60deg < r0_zenith
    
    def test_isoplanatic_angle(self):
        """Test isoplanatic angle calculation"""
        z = np.linspace(0, 20000, 100)
        Cn2 = 1e-15 * np.exp(-z/5000)
        
        theta0 = self.turb.isoplanatic_angle(Cn2, z)
        
        # Typical isoplanatic angle: a few arcsec
        assert 1 < theta0 < 10
    
    def test_coherence_time(self):
        """Test coherence time calculation"""
        Cn2 = 1e-15
        v = 10  # m/s
        
        tau0 = self.turb.coherence_time(Cn2, v)
        
        # Typical coherence time: few ms
        assert 0.001 < tau0 < 0.1
    
    def test_greenwood_frequency(self):
        """Test Greenwood frequency"""
        z = np.linspace(0, 20000, 100)
        Cn2 = 1e-15 * np.exp(-z/5000)
        v = 10 * np.ones_like(z)
        
        fG = self.turb.greenwood_frequency(Cn2, v, z)
        
        # Typical Greenwood frequency: tens of Hz
        assert 10 < fG < 100
    
    def test_cn2_estimation(self):
        """Test Cn2 estimation from meteorology"""
        T = 288.15
        P = 101325
        
        Cn2 = self.turb.estimate_cn2(T, P, height=10)
        
        # Should be within typical range
        assert 1e-18 < Cn2 < 1e-12
    
    def test_cn2_inversion(self):
        """Test inversion from scintillation to Cn2"""
        Cn2_input = 1e-15
        L = 1000
        
        sigma2 = self.turb.scintillation_index(Cn2_input, L)
        Cn2_output = self.turb.cn2_from_scintillation(sigma2, L)
        
        # Should recover input within 10%
        assert abs(Cn2_output - Cn2_input) / Cn2_input < 0.1
    
    def test_rytov_variance_profile(self):
        """Test cumulative Rytov variance profile"""
        z = np.linspace(0, 1000, 50)
        Cn2 = 1e-15 * np.ones_like(z)
        
        sigma2_profile = self.turb.rytov_variance_profile(Cn2, z, source_distance=1000)
        
        # Should increase with distance
        assert np.all(np.diff(sigma2_profile) >= 0)
        
        # Final value should match direct calculation
        sigma2_final = self.turb.scintillation_index(Cn2[0], 1000)
        assert abs(sigma2_profile[-1] - sigma2_final) / sigma2_final < 0.1
    
    @pytest.mark.parametrize("Cn2,L,expected_range", [
        (1e-16, 100, (1e-4, 1e-3)),
        (1e-15, 1000, (1e-3, 1e-1)),
        (1e-14, 10000, (1e-1, 1.0))
    ])
    def test_scintillation_range(self, Cn2, L, expected_range):
        """Test scintillation index within expected range"""
        sigma2 = self.turb.scintillation_index(Cn2, L)
        
        assert expected_range[0] < sigma2 < expected_range[1]
