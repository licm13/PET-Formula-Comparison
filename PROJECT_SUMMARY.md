# Project Summary: PET Formula Comparison Framework

## Overview

This project implements a comprehensive framework for comparing different Potential Evapotranspiration (PET) formulas, designed to support high-impact research on water availability, climate change impacts, and vegetation-atmosphere interactions.

## Implemented Formulas (10 total)

### 1. Classic Formulas (4)

**Penman-Monteith (PM)**
- FAO-56 standard reference evapotranspiration
- Most widely used and validated globally
- Requires: T, RH, wind, radiation

**Priestley-Taylor (PT)**
- Simplified energy balance approach
- Minimal data requirements (T, radiation only)
- α coefficient = 1.26 for well-watered surfaces

**Priestley-Taylor JPL (PT-JPL)**
- Remote sensing compatible
- Incorporates vegetation (LAI/NDVI) and soil moisture constraints
- Suitable for satellite-based applications

**Penman-Monteith-Leuning (PML)**
- Explicit LAI effects on conductance
- Partitions ET into transpiration and evaporation
- Enhanced vegetation representation

### 2. CO2-Aware Formulas (2)

**PM-CO2**
- Accounts for CO2 effects on stomatal conductance
- Based on Yang et al. (2019, Nature Climate Change)
- Critical for climate change projections

**PM-CO2-LAI**
- Combines CO2 and LAI effects
- Most comprehensive vegetation-CO2 interaction
- Partitions ET components

### 3. Complementary Relationship Formulas (4)

**Bouchet CR**
- Classic complementary relationship (1963)
- ETa + ETp = 2·ETwet

**Advection-Aridity (AA)**
- Brutsaert & Stricker model
- Separates equilibrium and advective components

**Granger-Gray (GG)**
- Relative evaporation approach
- Accounts for surface wetness

**Nonlinear CR**
- Modern nonlinear formulation
- Improved humidity deficit response

## Framework Components

### 1. Formula Implementations (`pet_comparison/formulas/`)
- `penman_monteith.py`: PM and general PM
- `priestley_taylor.py`: PT and PT with advection
- `priestley_taylor_jpl.py`: PT-JPL and partitioning
- `penman_monteith_leuning.py`: PML and PML-v2
- `co2_aware.py`: CO2-aware formulas and response functions
- `complementary_relationship.py`: CR models

### 2. Utility Functions (`pet_comparison/utils/`)
- `constants.py`: Physical constants and vapor pressure calculations
- `meteorology.py`: Radiation, pressure, and resistance calculations

### 3. Analysis Framework (`pet_comparison/analysis/`)
- `comparison.py`: PETComparison class for unified analysis
- `visualization.py`: Plotting functions for results

### 4. Documentation (`docs/`)
- `SCIENTIFIC_BACKGROUND.md`: Theory and formulas
- `USER_GUIDE.md`: How to use the framework
- `API_REFERENCE.md`: Function reference

### 5. Examples (`examples/`)
- `basic_comparison.py`: Compare all formulas
- `co2_sensitivity.py`: Analyze CO2 effects

### 6. Tests (`tests/`)
- `test_formulas.py`: Test all formula implementations
- `test_comparison.py`: Test comparison framework
- `test_utils.py`: Test utility functions

## Key Features

### 1. Unified Comparison
```python
comparison = PETComparison(forcing_data)
results = comparison.run_all()
```
- Run all formulas with identical inputs
- Ensures fair comparison
- Automatic handling of missing parameters

### 2. Statistical Analysis
- Summary statistics (mean, std, CV)
- Correlations between formulas
- Pairwise differences
- Formula agreement metrics

### 3. Visualization
- Time series comparison
- Distribution box plots
- Correlation matrices
- Seasonal patterns
- Sensitivity analysis plots

### 4. Component Partitioning
- Separate transpiration and evaporation
- Canopy vs soil contributions
- Available for PML, PM-CO2-LAI, PT-JPL

### 5. CO2 Sensitivity
- Multiple CO2 response functions
- Stomatal conductance adjustment
- Water use efficiency changes

## Research Applications

### 1. Formula Comparison Study
**Question**: How do different PET formulas compare under same conditions?
**Method**: Run all formulas with identical forcing data
**Output**: Statistics, correlations, differences

### 2. Climate Change Impacts
**Question**: How does elevated CO2 affect PET estimates?
**Method**: Compare CO2-aware vs traditional formulas
**Output**: Relative changes, sensitivity analysis

### 3. Vegetation Effects
**Question**: How important is LAI in PET estimation?
**Method**: Compare formulas with/without LAI
**Output**: LAI sensitivity, seasonal patterns

### 4. Formula Selection Guide
**Question**: Which formula to use for specific applications?
**Method**: Compare formula characteristics and requirements
**Output**: Decision matrix based on data availability and objectives

### 5. Paradox Analysis
**Question**: Do formulas show contradictory patterns?
**Method**: Analyze formula differences in extreme conditions
**Output**: Identify conditions of disagreement

## Scientific Contributions

### 1. CO2 Paradox
**Traditional view**: Warmer → Higher PET → More water stress
**CO2-aware view**: Higher CO2 → Stomatal closure → Lower PET
**Net effect**: Potentially offsetting impacts

### 2. Formula Agreements and Disagreements
- High agreement in humid climates
- Large differences in semi-arid regions
- Vegetation dynamics cause seasonal variations

### 3. Component Importance
- Energy vs aerodynamic components
- Vegetation vs soil contributions
- CO2 vs LAI effects

## Future Research Directions

1. **Remote Sensing Integration**
   - MODIS LAI/NDVI
   - Landsat surface temperature
   - GRACE soil moisture

2. **Machine Learning**
   - Ensemble PET predictions
   - Pattern recognition
   - Uncertainty quantification

3. **Validation Studies**
   - Eddy covariance comparison
   - Water balance validation
   - Multi-site analysis

4. **Scale Analysis**
   - Point to grid scale
   - Temporal aggregation
   - Spatial heterogeneity

5. **Operational Applications**
   - Real-time PET estimation
   - Irrigation scheduling
   - Drought monitoring

## Target Journals

Based on the comprehensive analysis this framework enables:

**Nature Water** - Focus on:
- Global water availability under climate change
- CO2 effects on water resources
- Multi-model PET intercomparison

**Nature Climate Change** - Focus on:
- CO2 paradox in climate projections
- Vegetation-climate feedbacks
- Uncertainty in future projections

**Water Resources Research** - Focus on:
- Formula comparison and validation
- Uncertainty quantification
- Regional applications

**Remote Sensing of Environment** - Focus on:
- Satellite-based PET estimation
- PT-JPL and PML validation
- Global ET products

## Usage Quick Reference

```python
# Basic comparison
from pet_comparison.analysis import PETComparison
comparison = PETComparison(forcing_data)
results = comparison.run_all()

# Specific formula
from pet_comparison.formulas import penman_monteith
pet = penman_monteith(T=20, RH=60, wind=2.5, Rn=15)

# CO2 sensitivity
from pet_comparison.formulas import pm_co2_aware
pet_current = pm_co2_aware(..., co2=380)
pet_future = pm_co2_aware(..., co2=550)

# Visualization
from pet_comparison.analysis.visualization import plot_timeseries
fig = plot_timeseries(results_df)
```

## Installation

```bash
git clone https://github.com/licm13/PET-Formula-Comparison.git
cd PET-Formula-Comparison
pip install -r requirements.txt
pip install -e .
```

## Testing

```bash
pytest tests/
```

## Documentation

- README.md: Project overview and quick start
- docs/SCIENTIFIC_BACKGROUND.md: Theory and formulas
- docs/USER_GUIDE.md: Detailed usage instructions
- docs/API_REFERENCE.md: Function documentation
- CHANGELOG.md: Version history
- LICENSE: MIT License

## Contact

Author: licm13
Repository: https://github.com/licm13/PET-Formula-Comparison

---

**Version**: 0.1.0
**Date**: 2024-11-06
**Status**: Production ready for research applications
