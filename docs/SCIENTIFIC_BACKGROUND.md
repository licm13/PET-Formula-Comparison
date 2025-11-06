# Scientific Background

## Overview of Potential Evapotranspiration (PET)

Potential Evapotranspiration (PET) represents the maximum amount of water that could be evaporated and transpired from a vegetated surface with adequate water supply. It is a critical component in:
- Water balance calculations
- Irrigation scheduling
- Climate change impact assessment
- Hydrological modeling
- Agricultural planning

## Formula Categories

### 1. Energy Balance Methods

These methods are based on the energy balance at the surface:

**Priestley-Taylor (1972)**
```
PET = α × (Δ/(Δ+γ)) × (Rn - G) / λ
```
Where:
- α = Priestley-Taylor coefficient (typically 1.26)
- Δ = Slope of saturation vapor pressure curve
- γ = Psychrometric constant
- Rn = Net radiation
- G = Soil heat flux
- λ = Latent heat of vaporization

**Advantages:**
- Simple, requires minimal data
- Works well in humid climates
- No need for wind or humidity data

**Limitations:**
- Assumes minimal advection
- Single empirical coefficient
- Less accurate in arid regions

### 2. Combination Methods

These combine energy balance with aerodynamic terms:

**Penman-Monteith (Allen et al., 1998)**
```
PET = [Δ(Rn-G) + ρa·cp·VPD/ra] / [λ(Δ + γ(1+rs/ra))]
```
Where:
- ρa = Air density
- cp = Specific heat of air
- VPD = Vapor pressure deficit
- ra = Aerodynamic resistance
- rs = Surface resistance

**Advantages:**
- Physically-based
- FAO-56 standard
- Well-validated globally
- Accounts for atmospheric demand

**Limitations:**
- Requires more input data
- Sensitive to wind speed measurements
- Fixed canopy parameters

### 3. Remote Sensing Enhanced Methods

**PT-JPL (Fisher et al., 2008)**

Extends PT with constraint factors:
```
ET = PET_max × f_green × f_SM × f_temp
```

Constraint factors based on:
- NDVI or LAI (vegetation greenness)
- Soil moisture
- Temperature stress

**Advantages:**
- Compatible with satellite data
- Captures spatial variability
- Accounts for vegetation dynamics

**Limitations:**
- Requires satellite observations
- Simplified stress functions
- Calibration needed

### 4. CO2-Aware Methods

**PM-CO2 (Yang et al., 2019)**

Modifies surface resistance based on CO2:
```
rs(CO2) = rs_ref / √(CO2_ref/CO2)
```

**Scientific Basis:**
- Higher CO2 → Partial stomatal closure
- Reduced stomatal conductance
- Lower transpiration rates
- Improved water use efficiency

**Key Finding:** Traditional PET formulas may overestimate future water stress because they don't account for CO2-induced stomatal closure.

### 5. Complementary Relationship Methods

**Bouchet (1963) Hypothesis:**
```
ET_actual + ET_potential = 2 × ET_wet
```

This reflects the negative feedback between:
- Actual evapotranspiration (ET_a)
- Potential evapotranspiration (ET_p)
- Wet environment evaporation (ET_w)

**Physical Interpretation:**
- As surface dries → ET_a decreases
- But → Atmospheric demand increases
- Therefore → ET_p increases
- The sum remains relatively constant

## Formula Comparison Insights

### When to Use Each Formula

| Scenario | Recommended Formula | Reason |
|----------|-------------------|---------|
| Data-limited | PT | Minimal inputs |
| Standard reference | PM | FAO-56 standard |
| Satellite-based | PT-JPL | Uses NDVI/LAI |
| Climate change | PM-CO2, PM-CO2-LAI | Accounts for CO2 |
| Regional water balance | CR models | Accounts for feedbacks |
| Vegetation dynamics | PML | Explicit LAI effects |

### Expected Differences

1. **Absolute Values:**
   - PT typically gives lower values (α=1.26 vs full aerodynamic term)
   - PM-CO2 < PM (stomatal closure effect)
   - PT-JPL can be significantly lower (constraint factors)

2. **Seasonal Patterns:**
   - All formulas peak in summer (radiation-driven)
   - Differences larger in spring/fall (vegetation dynamics)
   - CR models show different dry season behavior

3. **Spatial Patterns:**
   - Larger differences in transition zones (semi-arid)
   - More agreement in humid tropics
   - Vegetation-aware formulas differ most where LAI varies

## The CO2 Paradox

**Traditional View:**
- Warmer temperatures → Higher PET → More water stress

**CO2-Aware View:**
- Higher CO2 → Stomatal closure → Lower PET
- Could partially offset temperature increases
- Net effect depends on local conditions

**Key Papers:**
- Milly & Dunne (2016): "Potential evapotranspiration and continental drying"
- Yang et al. (2019): "Hydrologic implications of vegetation response to elevated CO2"
- Swann et al. (2016): "Plant responses to increasing CO2 reduce estimates of climate impacts on drought severity"

## Uncertainties and Challenges

### Parameter Uncertainty
- Surface resistance values
- Aerodynamic parameters
- Constraint function shapes
- CO2 response coefficients

### Scale Issues
- Point measurements vs. grid-scale estimates
- Temporal resolution (daily, monthly)
- Spatial heterogeneity

### Future Research Needs
1. Better quantification of CO2 effects across vegetation types
2. Integration of soil moisture feedbacks
3. Seasonal and diurnal variations in parameters
4. Validation with eddy covariance measurements
5. Ensemble approaches combining multiple formulas

## References

1. Allen, R.G., et al. (1998). Crop evapotranspiration - Guidelines for computing crop water requirements. FAO Irrigation and Drainage Paper 56.

2. Priestley, C.H.B. and Taylor, R.J. (1972). On the assessment of surface heat flux and evaporation using large-scale parameters. Monthly Weather Review, 100(2), 81-92.

3. Fisher, J.B., et al. (2008). Global estimates of the land–atmosphere water flux based on monthly AVHRR and ISLSCP-II data. Remote Sensing of Environment, 112(3), 901-919.

4. Zhang, Y., et al. (2016). Multi-decadal trends in global terrestrial evapotranspiration and its components. Scientific Reports, 6, 19124.

5. Yang, Y., et al. (2019). Hydrologic implications of vegetation response to elevated CO2 in climate projections. Nature Climate Change, 9(1), 44-48.

6. Bouchet, R.J. (1963). Evapotranspiration réelle et potentielle, signification climatique. IAHS Publ. 62, 134-142.

7. Brutsaert, W. and Stricker, H. (1979). An advection-aridity approach to estimate actual regional evapotranspiration. Water Resources Research, 15(2), 443-450.

8. Milly, P.C.D. and Dunne, K.A. (2016). Potential evapotranspiration and continental drying. Nature Climate Change, 6(10), 946-949.
