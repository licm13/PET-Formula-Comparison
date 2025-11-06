"""
Complementary Relationship PET Models
Based on the complementary relationship between actual and potential evapotranspiration
"""

import numpy as np
from ..utils.constants import (
    slope_saturation_vapor_pressure,
    get_psychrometric_constant,
    actual_vapor_pressure,
    saturation_vapor_pressure,
)


def bouchet_complementary(
    temperature,
    relative_humidity,
    net_radiation,
    pressure=101.3,
    soil_heat_flux=0.0,
):
    """
    Bouchet's complementary relationship
    
    The complementary relationship states that:
    ET_actual + ET_potential = 2 * ET_wet
    
    where ET_wet is the evapotranspiration from a wet surface (equilibrium evaporation)
    
    Parameters:
    -----------
    temperature : float or array-like
        Air temperature (°C)
    relative_humidity : float or array-like
        Relative humidity (%)
    net_radiation : float or array-like
        Net radiation (MJ m-2 day-1)
    pressure : float or array-like, optional
        Atmospheric pressure (kPa)
    soil_heat_flux : float or array-like, optional
        Soil heat flux (MJ m-2 day-1)
    
    Returns:
    --------
    dict : Dictionary containing:
        - 'wet_environment': ET from wet environment (mm day-1)
        - 'potential': Potential ET (mm day-1)
        - 'apparent_potential': Apparent potential ET (mm day-1)
    
    References:
    -----------
    Bouchet, R.J., 1963.
    Evapotranspiration réelle et potentielle, signification climatique.
    International Association of Hydrological Sciences, Publ, 62, pp.134-142.
    """
    # Calculate slope of saturation vapor pressure curve
    delta = slope_saturation_vapor_pressure(temperature)
    
    # Calculate psychrometric constant
    gamma = get_psychrometric_constant(pressure, temperature)
    
    # Lambda (latent heat of vaporization)
    lambda_v = 2.45
    
    # Equilibrium evaporation (wet surface, Priestley-Taylor alpha=1)
    ET_wet = (delta / (delta + gamma)) * (net_radiation - soil_heat_flux) / lambda_v
    
    # Drying power (function of humidity deficit)
    es = saturation_vapor_pressure(temperature)
    ea = actual_vapor_pressure(temperature, relative_humidity=relative_humidity)
    vpd = es - ea
    
    # Drying power term
    drying_power = (gamma / (delta + gamma)) * vpd * 6.43  # Simplified, 6.43 is a coefficient
    
    # Apparent potential ET (what would be measured in a pan)
    ET_apparent = ET_wet + drying_power
    
    # Standard potential ET (reference crop)
    # Using Priestley-Taylor with alpha=1.26
    ET_potential = 1.26 * ET_wet
    
    return {
        'wet_environment': np.maximum(ET_wet, 0.0),
        'potential': np.maximum(ET_potential, 0.0),
        'apparent_potential': np.maximum(ET_apparent, 0.0),
    }


def advection_aridity_model(
    temperature,
    relative_humidity,
    wind_speed,
    net_radiation,
    pressure=101.3,
    soil_heat_flux=0.0,
):
    """
    Advection-Aridity (AA) Complementary Relationship model
    
    This model partitions ET into wet environment (equilibrium) evaporation
    and a drying power component based on atmospheric aridity.
    
    Parameters:
    -----------
    temperature : float or array-like
        Air temperature (°C)
    relative_humidity : float or array-like
        Relative humidity (%)
    wind_speed : float or array-like
        Wind speed (m s-1)
    net_radiation : float or array-like
        Net radiation (MJ m-2 day-1)
    pressure : float or array-like, optional
        Atmospheric pressure (kPa)
    soil_heat_flux : float or array-like, optional
        Soil heat flux (MJ m-2 day-1)
    
    Returns:
    --------
    dict : Dictionary with ET components
    
    References:
    -----------
    Brutsaert, W. and Stricker, H., 1979.
    An advection-aridity approach to estimate actual regional evapotranspiration.
    Water Resources Research, 15(2), pp.443-450.
    """
    # Calculate slope of saturation vapor pressure curve
    delta = slope_saturation_vapor_pressure(temperature)
    
    # Calculate psychrometric constant
    gamma = get_psychrometric_constant(pressure, temperature)
    
    # Lambda (latent heat of vaporization)
    lambda_v = 2.45
    
    # Equilibrium evaporation
    ET_wet = (delta / (delta + gamma)) * (net_radiation - soil_heat_flux) / lambda_v
    
    # Calculate vapor pressure deficit
    es = saturation_vapor_pressure(temperature)
    ea = actual_vapor_pressure(temperature, relative_humidity=relative_humidity)
    vpd = es - ea
    
    # Aerodynamic term (drying power)
    ra = 208.0 / wind_speed
    aerodynamic_term = (1.01 * 1013 * vpd / ra) / lambda_v
    
    # Potential ET (wet surface)
    ET_potential = ET_wet + (gamma / (delta + gamma)) * aerodynamic_term
    
    # Aridity index
    aridity = vpd / (es + 1e-6)
    
    return {
        'equilibrium': np.maximum(ET_wet, 0.0),
        'potential': np.maximum(ET_potential, 0.0),
        'aridity_index': aridity,
    }


def cr_nonlinear(
    temperature,
    relative_humidity,
    net_radiation,
    pressure=101.3,
    soil_heat_flux=0.0,
):
    """
    Nonlinear Complementary Relationship model
    
    A more recent formulation that uses a nonlinear relationship between
    actual ET and atmospheric demand.
    
    Parameters:
    -----------
    temperature : float or array-like
        Air temperature (°C)
    relative_humidity : float or array-like
        Relative humidity (%)
    net_radiation : float or array-like
        Net radiation (MJ m-2 day-1)
    pressure : float or array-like, optional
        Atmospheric pressure (kPa)
    soil_heat_flux : float or array-like, optional
        Soil heat flux (MJ m-2 day-1)
    
    Returns:
    --------
    dict : Dictionary with ET estimates
    
    References:
    -----------
    Kahler, D.M. and Brutsaert, W., 2006.
    Complementary relationship between daily evaporation in the environment
    and pan evaporation. Water Resources Research, 42(5).
    """
    # Calculate slope of saturation vapor pressure curve
    delta = slope_saturation_vapor_pressure(temperature)
    
    # Calculate psychrometric constant
    gamma = get_psychrometric_constant(pressure, temperature)
    
    # Lambda (latent heat of vaporization)
    lambda_v = 2.45
    
    # Wet surface evaporation (Priestley-Taylor)
    ET_wet = 1.26 * (delta / (delta + gamma)) * (net_radiation - soil_heat_flux) / lambda_v
    
    # Calculate humidity deficit parameter
    es = saturation_vapor_pressure(temperature)
    ea = actual_vapor_pressure(temperature, relative_humidity=relative_humidity)
    
    # Relative humidity as fraction
    rh_frac = relative_humidity / 100.0
    
    # Nonlinear function based on relative humidity
    # When RH is high (wet), actual ET approaches potential
    # When RH is low (dry), actual ET is reduced
    
    # B parameter (controls nonlinearity)
    b = 2.0
    
    # Relative evaporation (actual/wet)
    x = 1 - rh_frac
    relative_et = (1 - x ** b) ** (1 / b)
    
    # Actual ET estimate
    ET_actual = ET_wet * relative_et
    
    # Complementary potential ET
    # ET_a + ET_p = 2 * ET_wet
    ET_complementary = 2 * ET_wet - ET_actual
    
    return {
        'wet_surface': np.maximum(ET_wet, 0.0),
        'actual': np.maximum(ET_actual, 0.0),
        'complementary_potential': np.maximum(ET_complementary, 0.0),
        'relative_evaporation': relative_et,
    }


def granger_gray_model(
    temperature,
    relative_humidity,
    net_radiation,
    pressure=101.3,
    soil_heat_flux=0.0,
):
    """
    Granger-Gray complementary relationship model
    
    This model uses the concept of relative evaporation and includes
    both radiative and aerodynamic components.
    
    Parameters:
    -----------
    temperature : float or array-like
        Air temperature (°C)
    relative_humidity : float or array-like
        Relative humidity (%)
    net_radiation : float or array-like
        Net radiation (MJ m-2 day-1)
    pressure : float or array-like, optional
        Atmospheric pressure (kPa)
    soil_heat_flux : float or array-like, optional
        Soil heat flux (MJ m-2 day-1)
    
    Returns:
    --------
    ET_actual : float or array-like
        Actual evapotranspiration (mm day-1)
    
    References:
    -----------
    Granger, R.J. and Gray, D.M., 1989.
    Evaporation from natural nonsaturated surfaces.
    Journal of Hydrology, 111(1-4), pp.21-29.
    """
    # Calculate slope of saturation vapor pressure curve
    delta = slope_saturation_vapor_pressure(temperature)
    
    # Calculate psychrometric constant
    gamma = get_psychrometric_constant(pressure, temperature)
    
    # Lambda (latent heat of vaporization)
    lambda_v = 2.45
    
    # Available energy
    A = net_radiation - soil_heat_flux
    
    # Equilibrium evaporation
    ET_eq = (delta / (delta + gamma)) * A / lambda_v
    
    # Calculate vapor pressure deficit
    es = saturation_vapor_pressure(temperature)
    ea = actual_vapor_pressure(temperature, relative_humidity=relative_humidity)
    vpd = es - ea
    
    # Relative humidity
    rh = relative_humidity / 100.0
    
    # Relative evaporation based on the Granger-Gray model
    # This depends on the surface wetness and atmospheric demand
    
    # Parameter G (typically around 0.06 to 0.08 kPa)
    G_param = 0.07
    
    # Calculate relative evaporation
    if isinstance(vpd, np.ndarray):
        rel_evap = np.zeros_like(vpd)
        mask = vpd > 0
        rel_evap[mask] = 1 / (1 + (vpd[mask] / G_param))
        rel_evap[~mask] = 1.0
    else:
        if vpd > 0:
            rel_evap = 1 / (1 + (vpd / G_param))
        else:
            rel_evap = 1.0
    
    # Actual ET
    ET_actual = rel_evap * ET_eq
    
    return np.maximum(ET_actual, 0.0)
