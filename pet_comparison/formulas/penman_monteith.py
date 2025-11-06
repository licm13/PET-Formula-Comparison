"""
Classic Penman-Monteith PET Formula
FAO-56 Reference Evapotranspiration
"""

import numpy as np
from ..utils.constants import (
    saturation_vapor_pressure,
    slope_saturation_vapor_pressure,
    actual_vapor_pressure,
    get_psychrometric_constant,
)


def penman_monteith(
    temperature,
    relative_humidity,
    wind_speed,
    net_radiation,
    pressure=101.3,
    soil_heat_flux=0.0,
    albedo=0.23,
    crop_height=0.12,
    surface_resistance=70.0,
):
    """
    Calculate reference evapotranspiration using FAO-56 Penman-Monteith equation
    
    The Penman-Monteith equation is the most widely used method for calculating
    reference evapotranspiration (ET0) and is recommended by FAO.
    
    Parameters:
    -----------
    temperature : float or array-like
        Mean daily air temperature (°C)
    relative_humidity : float or array-like
        Mean relative humidity (%)
    wind_speed : float or array-like
        Wind speed at 2m height (m s-1)
    net_radiation : float or array-like
        Net radiation at the crop surface (MJ m-2 day-1)
    pressure : float or array-like, optional
        Atmospheric pressure (kPa), default: 101.3
    soil_heat_flux : float or array-like, optional
        Soil heat flux density (MJ m-2 day-1), default: 0.0
    albedo : float, optional
        Albedo or canopy reflection coefficient, default: 0.23
    crop_height : float, optional
        Crop height (m), default: 0.12 (grass reference)
    surface_resistance : float, optional
        Bulk surface resistance (s m-1), default: 70
    
    Returns:
    --------
    ET0 : float or array-like
        Reference evapotranspiration (mm day-1)
    
    References:
    -----------
    Allen, R.G., Pereira, L.S., Raes, D., Smith, M., 1998. 
    Crop evapotranspiration - Guidelines for computing crop water requirements.
    FAO Irrigation and Drainage Paper 56, FAO, Rome.
    """
    # Calculate slope of saturation vapor pressure curve
    delta = slope_saturation_vapor_pressure(temperature)
    
    # Calculate psychrometric constant
    gamma = get_psychrometric_constant(pressure, temperature)
    
    # Calculate vapor pressure deficit
    es = saturation_vapor_pressure(temperature)
    ea = actual_vapor_pressure(temperature, relative_humidity=relative_humidity)
    vpd = es - ea
    
    # Aerodynamic resistance
    # For grass reference: ra = 208/wind_speed
    # Add minimum wind speed to prevent division by zero
    wind_speed_safe = np.maximum(wind_speed, 0.5)  # Minimum 0.5 m/s
    ra = 208.0 / wind_speed_safe
    
    # Calculate ET0 using Penman-Monteith equation
    numerator = (
        0.408 * delta * (net_radiation - soil_heat_flux) +
        gamma * (900 / (temperature + 273)) * wind_speed * vpd
    )
    denominator = delta + gamma * (1 + 0.34 * wind_speed_safe)
    
    ET0 = numerator / denominator
    
    # Ensure non-negative values
    ET0 = np.maximum(ET0, 0.0)
    
    return ET0


def penman_monteith_general(
    temperature,
    relative_humidity,
    wind_speed,
    net_radiation,
    pressure=101.3,
    soil_heat_flux=0.0,
    aerodynamic_resistance=None,
    surface_resistance=70.0,
):
    """
    General Penman-Monteith equation for any surface
    
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
    aerodynamic_resistance : float or array-like, optional
        Aerodynamic resistance (s m-1)
    surface_resistance : float or array-like, optional
        Surface resistance (s m-1)
    
    Returns:
    --------
    ET : float or array-like
        Evapotranspiration (mm day-1)
    """
    from ..utils.constants import SPECIFIC_HEAT_AIR, air_density
    
    # Calculate slope of saturation vapor pressure curve
    delta = slope_saturation_vapor_pressure(temperature)
    
    # Calculate psychrometric constant
    gamma = get_psychrometric_constant(pressure, temperature)
    
    # Calculate vapor pressure deficit
    es = saturation_vapor_pressure(temperature)
    ea = actual_vapor_pressure(temperature, relative_humidity=relative_humidity)
    vpd = es - ea
    
    # Default aerodynamic resistance if not provided
    if aerodynamic_resistance is None:
        aerodynamic_resistance = 208.0 / wind_speed
    
    # Air density
    rho = air_density(temperature, pressure, relative_humidity)
    
    # Lambda (latent heat of vaporization) in MJ kg-1
    lambda_v = 2.45
    
    # Calculate ET using Penman-Monteith equation
    numerator = (
        delta * (net_radiation - soil_heat_flux) +
        rho * SPECIFIC_HEAT_AIR * vpd / aerodynamic_resistance / 1000  # Convert to MJ
    )
    denominator = lambda_v * (delta + gamma * (1 + surface_resistance / aerodynamic_resistance))
    
    ET = numerator / denominator
    
    # Ensure non-negative values
    ET = np.maximum(ET, 0.0)
    
    return ET
