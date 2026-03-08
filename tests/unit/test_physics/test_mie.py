"""
Unit tests for Mie scattering module
"""

import numpy as np
import pytest
from opticlens.scattering.mie import MieScattering, AerosolMode


class TestMieScattering:
    """Test suite for Mie scattering calculations"""
    
    def setup_method(self):
        """Setup test instance"""
        self.wavelengths = np.array([0.44, 0.55, 0.67])
        self.mie = MieScattering(self.wavelengths)
    
    def test_single_particle_conservation(self):
        """Test energy conservation: Q_ext = Q_scat + Q_abs"""
        x = 10.0
        m = 1.5 + 0.01j
        
        Q_ext, Q_scat, g = self.mie._single_particle(x, m)
        
        # Q_abs should be positive and Q_ext >= Q_scat
        assert Q_ext >= Q_scat
        assert Q_ext > 0
        assert Q_scat > 0
    
    def test_bohren_huffman_benchmark(self):
        """Compare with Bohren & Huffman (1983) benchmark values"""
        # Test case from BH Table 4.4
        x = 10.0
        m = 1.5
        
        Q_ext, Q_scat, g = self.mie._single_particle(x, m)
        
        # BH values: Q_ext = 2.882, Q_scat = 2.882, g = 0.947
        assert abs(Q_ext - 2.882) < 0.001
        assert abs(Q_scat - 2.882) < 0.001
        assert abs(g - 0.947) < 0.001
    
    def test_rayleigh_limit(self):
        """Test Rayleigh scattering limit (x << 1)"""
        x = 0.01
        m = 1.5
        
        Q_ext, Q_scat, g = self.mie._single_particle(x, m)
        
        # Rayleigh: Q_scat ∝ x^4, g ≈ 0
        assert Q_scat < 1e-4
        assert abs(g) < 0.01
    
    def test_geometric_limit(self):
        """Test geometric optics limit (x >> 1)"""
        x = 1000.0
        m = 1.5
        
        Q_ext, Q_scat, g = self.mie._single_particle(x, m)
        
        # Geometric: Q_ext → 2, g → 1
        assert abs(Q_ext - 2.0) < 0.1
        assert abs(g - 1.0) < 0.1
    
    def test_polydisperse_integration(self):
        """Test polydisperse aerosol population"""
        modes = [
            AerosolMode(r_modal=0.12, sigma=1.45, N=800, m=1.45+0.01j),
            AerosolMode(r_modal=1.80, sigma=2.10, N=3, m=1.53+0.003j)
        ]
        
        results = self.mie.compute_bulk_properties(modes)
        
        assert 'beta_ext' in results
        assert 'beta_scat' in results
        assert 'asymmetry' in results
        assert len(results['beta_ext']) == len(self.wavelengths)
    
    def test_asymmetry_range(self):
        """Test asymmetry parameter bounds"""
        x_values = np.logspace(-2, 3, 10)
        m = 1.5
        
        for x in x_values:
            _, _, g = self.mie._single_particle(x, m)
            assert -1 <= g <= 1
    
    @pytest.mark.parametrize("x,m", [
        (1.0, 1.5),
        (10.0, 1.5+0.1j),
        (100.0, 1.33)
    ])
    def test_phase_function_normalization(self, x, m):
        """Test phase function normalization"""
        _, _, _, P_theta = self.mie._single_particle(x, m, return_phase=True)
        
        # Phase function should integrate to approximately 4π
        theta = np.linspace(0, np.pi, len(P_theta))
        integral = np.trapz(P_theta * np.sin(theta), theta) * 2 * np.pi
        
        assert abs(integral - 4*np.pi) / (4*np.pi) < 0.1
