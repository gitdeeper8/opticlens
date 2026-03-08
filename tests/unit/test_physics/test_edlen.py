"""
Unit tests for Edlén refractive index module
"""

import numpy as np
import pytest
from opticlens.refraction.edlen import EdlenRefractiveIndex


class TestEdlenRefractiveIndex:
    """Test suite for Edlén refractive index calculations"""
    
    def setup_method(self):
        """Setup test instance"""
        self.edlen = EdlenRefractiveIndex()
    
    def test_standard_conditions(self):
        """Test refractive index at standard conditions"""
        P = 101325  # Pa
        T = 288.15  # K (15°C)
        wavelength = 0.55  # μm
        
        n = self.edlen.compute(P, T, wavelength)
        
        # n-1 should be ~ 2.7e-4 at standard conditions
        assert abs((n - 1) - 2.7e-4) < 1e-5
    
    def test_ciddor_benchmark(self):
        """Compare with Ciddor (1996) benchmark"""
        P = 101325
        T = 293.15  # 20°C
        wavelength = 0.55
        
        n = self.edlen.compute(P, T, wavelength)
        
        # Ciddor value: n = 1.00027362
        assert abs(n - 1.00027362) < 1e-8
    
    def test_humidity_correction(self):
        """Test humidity correction"""
        P = 101325
        T = 293.15
        wavelength = 0.55
        
        n_dry = self.edlen.compute(P, T, wavelength, humidity=0.0)
        n_moist = self.edlen.compute(P, T, wavelength, humidity=0.5)
        
        # Moist air should have slightly lower refractive index
        assert n_moist < n_dry
        assert (n_dry - n_moist) < 1e-6
    
    def test_wavelength_dependence(self):
        """Test dispersion with wavelength"""
        P = 101325
        T = 288.15
        
        wavelengths = np.array([0.4, 0.55, 0.7])
        n = self.edlen.compute(P, T, wavelengths)
        
        # Refractive index decreases with wavelength (normal dispersion)
        assert n[0] > n[1] > n[2]
    
    def test_pressure_dependence(self):
        """Test pressure dependence"""
        T = 288.15
        wavelength = 0.55
        
        pressures = np.array([80000, 101325, 120000])
        n = self.edlen.compute(pressures, T, wavelength)
        
        # Refractive index increases with pressure
        assert n[0] < n[1] < n[2]
    
    def test_temperature_dependence(self):
        """Test temperature dependence"""
        P = 101325
        wavelength = 0.55
        
        temperatures = np.array([273.15, 288.15, 303.15])
        n = self.edlen.compute(P, temperatures, wavelength)
        
        # Refractive index decreases with temperature
        assert n[0] > n[1] > n[2]
    
    def test_saturation_vapor_pressure(self):
        """Test saturation vapor pressure calculation"""
        # At 20°C, e_sat ≈ 23.37 hPa
        e_sat = self.edlen._saturation_vapor_pressure(293.15)
        assert abs(e_sat - 23.37) < 0.5
    
    def test_vertical_gradient(self):
        """Test vertical gradient calculation"""
        z = np.array([0, 100, 200, 500, 1000])
        T = 288.15 - 0.0065 * z  # Standard lapse rate
        P = 101325 * (1 - 2.26e-5 * z)**5.25  # Barometric formula
        
        dn_dz = self.edlen.vertical_gradient(T, P, z)
        
        # Standard atmosphere: dn/dz ≈ -3.9e-8 m⁻¹
        assert abs(dn_dz[0] - (-3.9e-8)) < 1e-8
    
    def test_ray_curvature(self):
        """Test ray curvature calculation"""
        dn_dz = -3.9e-8
        R = self.edlen.ray_curvature(dn_dz)
        
        # Standard atmosphere: R ≈ 25,000 km
        assert abs(R - 25e6) < 1e6
    
    @pytest.mark.parametrize("wavelength,expected_range", [
        (0.4, (1.00028, 1.00030)),
        (0.55, (1.00027, 1.00029)),
        (0.7, (1.00026, 1.00028))
    ])
    def test_refractive_index_range(self, wavelength, expected_range):
        """Test refractive index within expected range"""
        P = 101325
        T = 288.15
        
        n = self.edlen.compute(P, T, wavelength)
        
        assert expected_range[0] < n < expected_range[1]
