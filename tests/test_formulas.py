"""
Tests for PET formula implementations
"""

import numpy as np
import pytest
from pet_comparison.formulas import (
    penman_monteith,
    priestley_taylor,
    priestley_taylor_jpl,
    penman_monteith_leuning,
    pm_co2_aware,
    pm_co2_lai_aware,
    bouchet_complementary,
    advection_aridity_model,
    granger_gray_model,
)


class TestBasicFormulas:
    """Test basic PET formulas"""
    
    def test_penman_monteith_basic(self):
        """Test PM formula with basic inputs"""
        pet = penman_monteith(
            temperature=20.0,
            relative_humidity=60.0,
            wind_speed=2.5,
            net_radiation=15.0,
        )
        assert pet > 0
        assert pet < 20  # Reasonable range
    
    def test_penman_monteith_array(self):
        """Test PM formula with array inputs"""
        pet = penman_monteith(
            temperature=np.array([15, 20, 25]),
            relative_humidity=np.array([50, 60, 70]),
            wind_speed=np.array([2.0, 2.5, 3.0]),
            net_radiation=np.array([10, 15, 20]),
        )
        assert len(pet) == 3
        assert np.all(pet > 0)
    
    def test_priestley_taylor_basic(self):
        """Test PT formula"""
        pet = priestley_taylor(
            temperature=20.0,
            net_radiation=15.0,
        )
        assert pet > 0
        assert pet < 20
    
    def test_priestley_taylor_alpha(self):
        """Test PT formula with different alpha values"""
        pet_126 = priestley_taylor(temperature=20.0, net_radiation=15.0, alpha=1.26)
        pet_110 = priestley_taylor(temperature=20.0, net_radiation=15.0, alpha=1.10)
        
        # Higher alpha should give higher PET
        assert pet_126 > pet_110
    
    def test_pt_jpl_basic(self):
        """Test PT-JPL formula"""
        pet = priestley_taylor_jpl(
            temperature=20.0,
            net_radiation=15.0,
            lai=3.0,
            soil_moisture=0.5,
        )
        assert pet > 0
    
    def test_pt_jpl_constraints(self):
        """Test PT-JPL with different constraints"""
        # High LAI and soil moisture
        pet_high = priestley_taylor_jpl(
            temperature=20.0,
            net_radiation=15.0,
            lai=5.0,
            soil_moisture=0.8,
        )
        
        # Low LAI and soil moisture
        pet_low = priestley_taylor_jpl(
            temperature=20.0,
            net_radiation=15.0,
            lai=1.0,
            soil_moisture=0.3,
        )
        
        # Higher LAI and SM should give higher PET
        assert pet_high > pet_low


class TestCO2Aware:
    """Test CO2-aware formulas"""
    
    def test_pm_co2_basic(self):
        """Test CO2-aware PM"""
        pet = pm_co2_aware(
            temperature=20.0,
            relative_humidity=60.0,
            wind_speed=2.5,
            net_radiation=15.0,
            co2=380.0,
        )
        assert pet > 0
    
    def test_pm_co2_response(self):
        """Test CO2 response"""
        # Reference CO2
        pet_380 = pm_co2_aware(
            temperature=20.0,
            relative_humidity=60.0,
            wind_speed=2.5,
            net_radiation=15.0,
            co2=380.0,
        )
        
        # Elevated CO2
        pet_560 = pm_co2_aware(
            temperature=20.0,
            relative_humidity=60.0,
            wind_speed=2.5,
            net_radiation=15.0,
            co2=560.0,
        )
        
        # Higher CO2 should reduce PET (stomatal closure)
        assert pet_560 < pet_380
    
    def test_pm_co2_lai_basic(self):
        """Test CO2+LAI aware PM"""
        result = pm_co2_lai_aware(
            temperature=20.0,
            relative_humidity=60.0,
            wind_speed=2.5,
            net_radiation=15.0,
            co2=380.0,
            lai=3.0,
        )
        
        assert 'total' in result
        assert 'transpiration' in result
        assert 'evaporation' in result
        assert result['total'] > 0
    
    def test_pm_co2_lai_partitioning(self):
        """Test that components sum to total"""
        result = pm_co2_lai_aware(
            temperature=20.0,
            relative_humidity=60.0,
            wind_speed=2.5,
            net_radiation=15.0,
            co2=380.0,
            lai=3.0,
        )
        
        total = result['transpiration'] + result['evaporation']
        np.testing.assert_allclose(total, result['total'], rtol=1e-5)


class TestPML:
    """Test PML formula"""
    
    def test_pml_basic(self):
        """Test PML basic functionality"""
        result = penman_monteith_leuning(
            temperature=20.0,
            relative_humidity=60.0,
            wind_speed=2.5,
            net_radiation=15.0,
            lai=3.0,
        )
        
        assert 'total' in result
        assert 'transpiration' in result
        assert 'evaporation' in result
        assert result['total'] > 0
    
    def test_pml_lai_effect(self):
        """Test LAI effect on PML"""
        # Low LAI
        result_low = penman_monteith_leuning(
            temperature=20.0,
            relative_humidity=60.0,
            wind_speed=2.5,
            net_radiation=15.0,
            lai=1.0,
        )
        
        # High LAI
        result_high = penman_monteith_leuning(
            temperature=20.0,
            relative_humidity=60.0,
            wind_speed=2.5,
            net_radiation=15.0,
            lai=5.0,
        )
        
        # Higher LAI should increase transpiration
        assert result_high['transpiration'] > result_low['transpiration']


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_zero_radiation(self):
        """Test with zero net radiation"""
        pet = penman_monteith(
            temperature=20.0,
            relative_humidity=60.0,
            wind_speed=2.5,
            net_radiation=0.0,
        )
        # Should still compute but be very small
        assert pet >= 0
    
    def test_high_humidity(self):
        """Test with very high humidity"""
        pet = penman_monteith(
            temperature=20.0,
            relative_humidity=95.0,
            wind_speed=2.5,
            net_radiation=15.0,
        )
        assert pet >= 0
    
    def test_low_wind(self):
        """Test with low wind speed"""
        pet = penman_monteith(
            temperature=20.0,
            relative_humidity=60.0,
            wind_speed=0.5,
            net_radiation=15.0,
        )
        assert pet >= 0
    
    def test_negative_temperature(self):
        """Test with negative temperature"""
        pet = penman_monteith(
            temperature=-5.0,
            relative_humidity=60.0,
            wind_speed=2.5,
            net_radiation=5.0,
        )
        # Should handle gracefully
        assert pet >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
