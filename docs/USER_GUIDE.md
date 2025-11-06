# User Guide

## Quick Start

```python
import pandas as pd
from pet_comparison.analysis import PETComparison

# Prepare forcing data
forcing_data = pd.DataFrame({
    'temperature': [20, 22, 25],  # °C
    'relative_humidity': [60, 65, 70],  # %
    'wind_speed': [2.5, 3.0, 2.0],  # m/s
    'net_radiation': [15, 18, 20],  # MJ m-2 day-1
})

# Run comparison
comparison = PETComparison(forcing_data)
results = comparison.run_all()

# Get results
results_df = comparison.get_results_dataframe()
print(results_df)
```

## Input Requirements

### Required Variables
- temperature: Air temperature (°C)
- relative_humidity: Relative humidity (%)
- wind_speed: Wind speed at 2m (m/s)
- net_radiation: Net radiation (MJ m-2 day-1)

### Optional Variables
- lai: Leaf Area Index (m2/m2)
- soil_moisture: Relative soil moisture (0-1)
- co2: CO2 concentration (ppm)
- pressure: Atmospheric pressure (kPa)

## Examples

See `examples/` directory for complete examples:
- `basic_comparison.py`: Compare all formulas
- `co2_sensitivity.py`: Analyze CO2 effects

Run examples:
```bash
cd examples
python basic_comparison.py
```

## Troubleshooting

**Negative values**: Check input units
**High values**: Verify radiation units (MJ m-2 day-1)
**Missing data**: Use pandas interpolation

For detailed documentation, see API_REFERENCE.md
