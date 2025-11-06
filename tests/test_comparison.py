"""
Tests for comparison framework
"""

import numpy as np
import pandas as pd
import pytest
from pet_comparison.analysis import PETComparison


def generate_test_data(n_days=30):
    """Generate simple test data with variation"""
    dates = pd.date_range(start='2020-01-01', periods=n_days, freq='D')
    
    # Add some variation to ensure correlations are computable
    data = pd.DataFrame({
        'temperature': 20.0 + np.linspace(0, 10, n_days),  # 20-30°C
        'relative_humidity': 60.0 + np.sin(np.linspace(0, 4*np.pi, n_days)) * 20.0,  # 40-80%
        'wind_speed': 2.5 + np.cos(np.linspace(0, 2*np.pi, n_days)) * 1.0,  # 1.5-3.5 m/s
        'net_radiation': 15.0 + np.sin(np.linspace(0, 2*np.pi, n_days)) * 5.0,  # 10-20 MJ/m²/day
        'lai': 3.0 + np.linspace(0, 1, n_days),  # 3-4 LAI
        'soil_moisture': 0.5 + np.sin(np.linspace(0, 3*np.pi, n_days)) * 0.2,  # 0.3-0.7
        'co2': np.ones(n_days) * 380.0,  # Constant CO2
    }, index=dates)
    
    return data


class TestPETComparison:
    """Test comparison framework"""
    
    def test_initialization(self):
        """Test initialization with data"""
        data = generate_test_data()
        comparison = PETComparison(data)
        assert comparison.forcing_data is not None
    
    def test_run_single_formula(self):
        """Test running single formula"""
        data = generate_test_data()
        comparison = PETComparison(data)
        
        result = comparison.run_penman_monteith()
        assert result is not None
        assert len(result) == len(data)
        assert np.all(result >= 0)
    
    def test_run_all_formulas(self):
        """Test running all formulas"""
        data = generate_test_data()
        comparison = PETComparison(data)
        
        results = comparison.run_all()
        assert len(results) > 0
        
        # Check all results are non-negative
        for name, values in results.items():
            assert np.all(values >= 0)
    
    def test_get_results_dataframe(self):
        """Test getting results as DataFrame"""
        data = generate_test_data()
        comparison = PETComparison(data)
        comparison.run_all()
        
        df = comparison.get_results_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(data)
    
    def test_compute_statistics(self):
        """Test statistics computation"""
        data = generate_test_data()
        comparison = PETComparison(data)
        comparison.run_all()
        
        stats = comparison.compute_statistics()
        assert 'mean' in stats.index
        assert 'std' in stats.index
        assert 'cv' in stats.index
    
    def test_compute_correlations(self):
        """Test correlation computation"""
        data = generate_test_data()
        comparison = PETComparison(data)
        comparison.run_all()
        
        corr = comparison.compute_correlations()
        assert isinstance(corr, pd.DataFrame)
        
        # Check diagonal is 1
        for col in corr.columns:
            if col in corr.index:
                assert corr.loc[col, col] == 1.0
    
    def test_compute_pairwise_differences(self):
        """Test pairwise differences"""
        data = generate_test_data()
        comparison = PETComparison(data)
        comparison.run_all()
        
        diff = comparison.compute_pairwise_differences()
        assert isinstance(diff, pd.DataFrame)
        
        # Check diagonal is 0
        for col in diff.columns:
            if col in diff.index:
                assert diff.loc[col, col] == 0.0


class TestDataValidation:
    """Test data validation and defaults"""
    
    def test_missing_optional_columns(self):
        """Test with missing optional columns"""
        dates = pd.date_range(start='2020-01-01', periods=10, freq='D')
        
        # Minimal data
        data = pd.DataFrame({
            'temperature': np.ones(10) * 20.0,
            'relative_humidity': np.ones(10) * 60.0,
            'wind_speed': np.ones(10) * 2.5,
            'net_radiation': np.ones(10) * 15.0,
        }, index=dates)
        
        comparison = PETComparison(data)
        
        # Should add defaults
        assert 'pressure' in comparison.forcing_data.columns
        assert 'soil_heat_flux' in comparison.forcing_data.columns
        assert 'co2' in comparison.forcing_data.columns
    
    def test_with_all_columns(self):
        """Test with all columns provided"""
        data = generate_test_data()
        comparison = PETComparison(data)
        
        # Should not modify existing columns
        assert comparison.forcing_data['co2'].iloc[0] == 380.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
