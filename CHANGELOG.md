# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2024-11-06

### Added
- Initial release of PET Formula Comparison framework
- Classic PET formulas:
  - Penman-Monteith (FAO-56 standard)
  - Priestley-Taylor
  - Priestley-Taylor JPL
  - Penman-Monteith-Leuning (PML)
- CO2-aware formulas:
  - PM with CO2 response
  - PM with CO2 and LAI response
- Complementary relationship formulas:
  - Bouchet complementary relationship
  - Advection-Aridity model
  - Granger-Gray model
  - Nonlinear CR model
- PETComparison framework for unified analysis
- Visualization utilities:
  - Time series plots
  - Box plot comparisons
  - Correlation matrices
  - Seasonal patterns
  - Sensitivity analysis plots
- Statistical analysis tools:
  - Summary statistics
  - Correlations
  - Pairwise differences
- Example scripts:
  - Basic comparison with synthetic data
  - CO2 sensitivity analysis
- Comprehensive documentation:
  - Scientific background
  - User guide
  - API reference
- Test suite for validation

### Features
- Support for scalar and array inputs
- Automatic handling of missing optional parameters
- Component partitioning (transpiration vs evaporation)
- Multiple CO2 response functions
- LAI and vegetation dynamics
- Soil moisture constraints

### Documentation
- README with quick start guide
- Scientific background on PET formulas
- User guide with examples
- API reference documentation
- In-code documentation for all functions

## [Unreleased]

### Planned Features
- Integration with remote sensing data (MODIS, Landsat)
- Ensemble PET estimates
- Uncertainty quantification
- Real-time data processing
- Machine learning-based PET prediction
- Additional validation datasets
- Performance optimization for large datasets
- NetCDF input/output support
- Spatial analysis tools
