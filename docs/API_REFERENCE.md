# API Reference

## Main Functions

### penman_monteith(temperature, relative_humidity, wind_speed, net_radiation, ...)
FAO-56 Penman-Monteith reference evapotranspiration

### priestley_taylor(temperature, net_radiation, alpha=1.26, ...)
Priestley-Taylor potential evapotranspiration

### priestley_taylor_jpl(temperature, net_radiation, lai, soil_moisture, ...)
PT-JPL model with vegetation constraints

### penman_monteith_leuning(temperature, rh, wind_speed, net_radiation, lai, ...)
PML model with explicit LAI effects
Returns: dict with 'total', 'transpiration', 'evaporation'

### pm_co2_aware(temperature, rh, wind_speed, net_radiation, co2, ...)
CO2-aware Penman-Monteith

### pm_co2_lai_aware(temperature, rh, wind_speed, net_radiation, co2, lai, ...)
CO2 and LAI-aware Penman-Monteith
Returns: dict with 'total', 'transpiration', 'evaporation'

## PETComparison Class

```python
comparison = PETComparison(forcing_data)
```

### Methods

- `run_all()`: Run all formulas
- `run_penman_monteith()`: Run PM only
- `run_priestley_taylor()`: Run PT only
- `get_results_dataframe()`: Get results as DataFrame
- `compute_statistics()`: Compute statistics
- `compute_correlations()`: Compute correlations
- `compute_pairwise_differences()`: Compute differences

## Visualization Functions

- `plot_timeseries(results_df)`: Time series plot
- `plot_box_comparison(results_df)`: Box plot
- `plot_correlation_matrix(results_df)`: Correlation heatmap
- `plot_seasonal_comparison(results_df)`: Monthly averages

## Units

Inputs:
- Temperature: °C
- RH: %
- Wind: m/s
- Radiation: MJ m-2 day-1
- Pressure: kPa
- CO2: ppm

Outputs:
- PET/ET: mm/day
