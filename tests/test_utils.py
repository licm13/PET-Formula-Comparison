"""
Tests for utility functions
"""

import numpy as np
import pytest
from pet_comparison.utils.constants import (
    saturation_vapor_pressure,
    slope_saturation_vapor_pressure,
    actual_vapor_pressure,
    vapor_pressure_deficit,
    get_psychrometric_constant,
)


class TestConstants:
    """Test constant calculations"""
    
    def test_saturation_vapor_pressure(self):
        """Test saturation vapor pressure calculation"""
        # At 20°C, es should be about 2.34 kPa
        es = saturation_vapor_pressure(20.0)
        assert 2.3 < es < 2.4
        
        # Should increase with temperature
        es_10 = saturation_vapor_pressure(10.0)
        es_30 = saturation_vapor_pressure(30.0)
        assert es_30 > es_10
    
    def test_slope_saturation_vapor_pressure(self):
        """Test slope calculation"""
        delta = slope_saturation_vapor_pressure(20.0)
        assert delta > 0
        
        # Slope should increase with temperature
        delta_10 = slope_saturation_vapor_pressure(10.0)
        delta_30 = slope_saturation_vapor_pressure(30.0)
        assert delta_30 > delta_10
    
    def test_actual_vapor_pressure(self):
        """Test actual vapor pressure from RH"""
        ea = actual_vapor_pressure(20.0, relative_humidity=50.0)
        es = saturation_vapor_pressure(20.0)
        
        # At 50% RH, ea should be half of es
        np.testing.assert_allclose(ea, es * 0.5, rtol=0.01)
    
    def test_vapor_pressure_deficit(self):
        """Test VPD calculation"""
        vpd = vapor_pressure_deficit(20.0, relative_humidity=50.0)
        
        # VPD should be positive
        assert vpd > 0
        
        # At 100% RH, VPD should be near zero
        vpd_100 = vapor_pressure_deficit(20.0, relative_humidity=100.0)
        assert vpd_100 < 0.01
    
    def test_psychrometric_constant(self):
        """Test psychrometric constant"""
        gamma = get_psychrometric_constant(101.3, 20.0)
        
        # Should be around 0.067 kPa/°C at standard pressure
        assert 0.06 < gamma < 0.07
    
    def test_array_inputs(self):
        """Test with array inputs"""
        temps = np.array([10, 20, 30])
        es = saturation_vapor_pressure(temps)
        
        assert len(es) == 3
        assert np.all(es > 0)
        assert es[2] > es[1] > es[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
