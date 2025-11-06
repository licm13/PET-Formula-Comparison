# PET Formula Comparison

对比不同的PET（潜在蒸散发）公式，包括经典公式和考虑CO2影响的新型公式，旨在研究不同公式的应用场景和差异性。

A comprehensive comparison framework for different Potential Evapotranspiration (PET) formulas, including classic formulas and modern CO2-aware approaches.

## 🎯 Project Goals

1. **Compare PET formulas** under identical forcing conditions to identify differences
2. **Identify optimal use cases** for different PET formulas based on research objectives
3. **Analyze paradoxes** and conflicts between different PET approaches
4. **Support high-impact research** targeting Nature Water or Nature Climate Change

## 📚 Implemented PET Formulas

### Classic Formulas
- **PM (Penman-Monteith)**: FAO-56 reference evapotranspiration, the most widely used standard
- **PT (Priestley-Taylor)**: Simplified energy-based approach with empirical coefficient
- **PT-JPL**: Enhanced Priestley-Taylor with vegetation and soil moisture constraints
- **PML (Penman-Monteith-Leuning)**: Extended PM model with explicit LAI and vegetation dynamics

### CO2-Aware Formulas
- **PM-CO2**: Penman-Monteith with CO2 effects on stomatal conductance
  - Based on: *"Hydrologic implications of vegetation response to elevated CO2 in climate projections"* (Yang et al., 2019, Nature Climate Change)
- **PM-CO2-LAI**: Accounts for both CO2 and LAI effects
  - Based on: *"A physically-based potential evapotranspiration model for global water availability projections"*

### Complementary Relationship Formulas
- **CR-Bouchet**: Classic complementary relationship (Bouchet, 1963)
- **CR-AA**: Advection-Aridity model (Brutsaert & Stricker, 1979)
- **CR-GG**: Granger-Gray model (1989)
- **CR-Nonlinear**: Modern nonlinear complementary relationship

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/licm13/PET-Formula-Comparison.git
cd PET-Formula-Comparison

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## 💡 Quick Start

### Basic Comparison

```python
import pandas as pd
from pet_comparison.analysis import PETComparison

# Prepare forcing data
forcing_data = pd.DataFrame({
    'temperature': [20, 22, 25],  # °C
    'relative_humidity': [60, 65, 70],  # %
    'wind_speed': [2.5, 3.0, 2.0],  # m/s
    'net_radiation': [15, 18, 20],  # MJ m-2 day-1
    'lai': [3.0, 3.5, 4.0],  # Leaf Area Index
    'soil_moisture': [0.5, 0.6, 0.55],  # 0-1
    'co2': [380, 400, 420],  # ppm
})

# Run comparison
comparison = PETComparison(forcing_data)
results = comparison.run_all()

# Get results as DataFrame
results_df = comparison.get_results_dataframe()
print(results_df)

# Compute statistics
stats = comparison.compute_statistics()
print(stats)
```

### Running Examples

```bash
# Basic comparison with synthetic data
cd examples
python basic_comparison.py

# CO2 sensitivity analysis
python co2_sensitivity.py
```

## 📊 Features

### 1. Comprehensive Formula Implementation
- All formulas based on peer-reviewed scientific literature
- Physically-based with explicit parameter meanings
- Support for both simple and complex forcing data

### 2. Comparison Framework
- Run multiple formulas with identical forcing data
- Statistical comparison (mean, std, CV)
- Pairwise differences and correlations
- Partitioning into components (transpiration, evaporation, etc.)

### 3. Sensitivity Analysis
- CO2 sensitivity testing
- LAI and vegetation response
- Soil moisture constraints
- Temperature and humidity effects

### 4. Visualization Tools
- Time series comparison
- Box plots and distributions
- Correlation matrices
- Sensitivity plots
- Seasonal patterns

## 📖 Documentation

### Required Input Data

Minimum requirements:
- `temperature`: Air temperature (°C)
- `relative_humidity`: Relative humidity (%)
- `wind_speed`: Wind speed at 2m height (m/s)
- `net_radiation`: Net radiation (MJ m-2 day-1)

Optional inputs (enable additional formulas):
- `lai`: Leaf Area Index (m2/m2)
- `ndvi`: Normalized Difference Vegetation Index (0-1)
- `soil_moisture`: Relative soil moisture (0-1)
- `co2`: Atmospheric CO2 concentration (ppm)
- `pressure`: Atmospheric pressure (kPa)
- `soil_heat_flux`: Soil heat flux (MJ m-2 day-1)

### Formula Selection Guidelines

| Research Goal | Recommended Formula | Reason |
|---------------|-------------------|---------|
| FAO reference ET | PM | Standard, well-validated |
| Data-limited regions | PT | Requires only radiation and temperature |
| Remote sensing applications | PT-JPL | Uses satellite LAI/NDVI |
| Climate change impacts | PM-CO2, PM-CO2-LAI | Accounts for CO2 fertilization |
| Vegetation dynamics | PML | Explicit LAI and conductance |
| Regional water balance | CR models | Accounts for feedback effects |

## 🔬 Scientific Background

### CO2 Effects on PET

Elevated CO2 reduces stomatal conductance, leading to:
- ⬇️ Reduced transpiration rates
- ⬆️ Increased water use efficiency
- 📊 Non-linear response (~√(CO2_ref/CO2))

### Complementary Relationship

The complementary relationship states:
```
ET_actual + ET_potential = 2 × ET_wet
```

This reflects the feedback between surface conditions and atmospheric demand.

### LAI Effects

Leaf Area Index affects:
- Radiation partitioning between canopy and soil
- Total canopy conductance (scales with LAI)
- Interception evaporation

## 📈 Example Results

The framework enables analysis of:

1. **Formula differences**: Which formulas give highest/lowest PET?
2. **Correlation patterns**: Which formulas are most similar?
3. **Sensitivity**: How do formulas respond to CO2, LAI, soil moisture?
4. **Seasonal patterns**: Do formulas differ more in summer or winter?
5. **Component partitioning**: How is ET split between transpiration and evaporation?

## 🤝 Contributing

Contributions are welcome! Areas of interest:
- Additional PET formulas
- New analysis methods
- Real-world case studies
- Performance optimizations

## 📚 References

### Key Papers

1. **Allen et al. (1998)**: FAO-56 Penman-Monteith equation
2. **Priestley & Taylor (1972)**: Priestley-Taylor equation
3. **Fisher et al. (2008)**: PT-JPL model
4. **Zhang et al. (2016)**: PML model
5. **Yang et al. (2019)**: CO2-aware PET (*Nature Climate Change*)
6. **Milly & Dunne (2016)**: CO2 effects on continental drying (*Nature Climate Change*)
7. **Brutsaert & Stricker (1979)**: Advection-Aridity model

## 📄 License

This project is open source and available under the MIT License.

## 👥 Authors

- **licm13** - Initial work and framework development

## 🎓 Citation

If you use this framework in your research, please cite:

```bibtex
@software{pet_comparison_2024,
  author = {licm13},
  title = {PET Formula Comparison: A Comprehensive Framework},
  year = {2024},
  url = {https://github.com/licm13/PET-Formula-Comparison}
}
```

## 🔮 Future Directions

- Integration with remote sensing data (MODIS, Landsat)
- Machine learning-based PET prediction
- Uncertainty quantification
- Ensemble PET estimates
- Real-time data processing pipeline

---

**Note**: This framework is designed for research purposes. For operational applications, please validate against local observations and consider site-specific calibration.
