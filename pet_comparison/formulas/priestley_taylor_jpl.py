"""
Priestley-Taylor JPL Model
Enhanced PT model with constraints based on vegetation properties
"""

import numpy as np
from ..utils.constants import (
    slope_saturation_vapor_pressure,
    get_psychrometric_constant,
    ALPHA_PT,
)


def priestley_taylor_jpl(
    temperature,
    net_radiation,
    ndvi=None,
    lai=None,
    soil_moisture=None,
    tmin=None,
    tmax=None,
    pressure=101.3,
    soil_heat_flux=0.0,
):
    """
    Calculate evapotranspiration using Priestley-Taylor JPL model
    
    The PT-JPL model uses the Priestley-Taylor equation as a baseline but
    introduces reduction factors based on vegetation properties, soil moisture,
    and temperature constraints.
    
    Parameters:
    -----------
    temperature : float or array-like
        Air temperature (°C)
    net_radiation : float or array-like
        Net radiation (MJ m-2 day-1)
    ndvi : float or array-like, optional
        Normalized Difference Vegetation Index (0-1)
    lai : float or array-like, optional
        Leaf Area Index (m2 m-2)
    soil_moisture : float or array-like, optional
        Relative soil moisture (0-1)
    tmin : float or array-like, optional
        Minimum temperature (°C)
    tmax : float or array-like, optional
        Maximum temperature (°C)
    pressure : float or array-like, optional
        Atmospheric pressure (kPa)
    soil_heat_flux : float or array-like, optional
        Soil heat flux (MJ m-2 day-1)
    
    Returns:
    --------
    ET : float or array-like
        Evapotranspiration (mm day-1)
    
    References:
    -----------
    Fisher, J.B., Tu, K.P. and Baldocchi, D.D., 2008.
    Global estimates of the land–atmosphere water flux based on monthly
    AVHRR and ISLSCP-II data, validated at 16 FLUXNET sites.
    Remote Sensing of Environment, 112(3), pp.901-919.
    """
    # Calculate slope of saturation vapor pressure curve
    delta = slope_saturation_vapor_pressure(temperature)
    
    # Calculate psychrometric constant
    gamma = get_psychrometric_constant(pressure, temperature)
    
    # Lambda (latent heat of vaporization)
    lambda_v = 2.45
    
    # Calculate maximum (potential) evapotranspiration
    PET_max = ALPHA_PT * (delta / (delta + gamma)) * (net_radiation - soil_heat_flux) / lambda_v
    
    # Initialize constraint factors
    f_green = 1.0  # Green canopy fraction
    f_sm = 1.0     # Soil moisture constraint
    f_temp = 1.0   # Temperature constraint
    
    # Green canopy fraction from NDVI or LAI
    if ndvi is not None:
        # NDVI-based green vegetation fraction
        ndvi_min = 0.05
        ndvi_max = 0.95
        f_green = np.clip((ndvi - ndvi_min) / (ndvi_max - ndvi_min), 0, 1)
    elif lai is not None:
        # LAI-based green vegetation fraction
        f_green = 1 - np.exp(-lai / 2.0)
    
    # Soil moisture constraint
    if soil_moisture is not None:
        # Soil moisture stress function
        # Assumes soil_moisture is relative (0-1)
        sm_crit = 0.3  # Critical soil moisture threshold
        f_sm = np.clip((soil_moisture - sm_crit) / (1 - sm_crit), 0, 1)
    
    # Temperature constraint
    if tmin is not None and tmax is not None:
        # Temperature stress based on temperature range
        # Cold or hot temperatures reduce ET
        t_opt = 25.0  # Optimal temperature
        t_range = (tmax - tmin) / 2.0
        temp_stress = np.exp(-((temperature - t_opt) ** 2) / (2 * t_range ** 2))
        f_temp = np.clip(temp_stress, 0.5, 1.0)
    
    # Calculate actual ET with constraints
    ET = PET_max * f_green * f_sm * f_temp
    
    # Ensure non-negative values
    ET = np.maximum(ET, 0.0)
    
    return ET


def priestley_taylor_jpl_partition(
    temperature,
    net_radiation,
    ndvi,
    lai,
    soil_moisture,
    pressure=101.3,
    soil_heat_flux=0.0,
):
    """
    PT-JPL model with partitioning into canopy transpiration, 
    canopy evaporation, and soil evaporation
    
    Parameters:
    -----------
    temperature : float or array-like
        Air temperature (°C)
    net_radiation : float or array-like
        Net radiation (MJ m-2 day-1)
    ndvi : float or array-like
        Normalized Difference Vegetation Index (0-1)
    lai : float or array-like
        Leaf Area Index (m2 m-2)
    soil_moisture : float or array-like
        Relative soil moisture (0-1)
    pressure : float or array-like, optional
        Atmospheric pressure (kPa)
    soil_heat_flux : float or array-like, optional
        Soil heat flux (MJ m-2 day-1)
    
    Returns:
    --------
    dict : Dictionary containing:
        - 'total': Total ET (mm day-1)
        - 'transpiration': Canopy transpiration (mm day-1)
        - 'canopy_evap': Canopy evaporation (mm day-1)
        - 'soil_evap': Soil evaporation (mm day-1)
    """
    # Calculate slope of saturation vapor pressure curve
    delta = slope_saturation_vapor_pressure(temperature)
    
    # Calculate psychrometric constant
    gamma = get_psychrometric_constant(pressure, temperature)
    
    # Lambda (latent heat of vaporization)
    lambda_v = 2.45
    
    # Green canopy fraction
    f_green = 1 - np.exp(-lai / 2.0)
    
    # Soil moisture constraint
    sm_crit = 0.3
    f_sm = np.clip((soil_moisture - sm_crit) / (1 - sm_crit), 0, 1)
    
    # Partition net radiation
    Rn_canopy = net_radiation * f_green
    Rn_soil = net_radiation * (1 - f_green)
    
    # Canopy transpiration
    PET_canopy = ALPHA_PT * (delta / (delta + gamma)) * Rn_canopy / lambda_v
    transpiration = PET_canopy * f_sm
    
    # Canopy interception evaporation (simplified)
    canopy_evap = 0.1 * Rn_canopy / lambda_v  # Assume 10% of canopy radiation
    
    # Soil evaporation
    PET_soil = (delta / (delta + gamma)) * (Rn_soil - soil_heat_flux) / lambda_v
    soil_evap = PET_soil * np.sqrt(f_sm)  # Square root for soil evaporation
    
    # Total ET
    total_et = transpiration + canopy_evap + soil_evap
    
    return {
        'total': np.maximum(total_et, 0.0),
        'transpiration': np.maximum(transpiration, 0.0),
        'canopy_evap': np.maximum(canopy_evap, 0.0),
        'soil_evap': np.maximum(soil_evap, 0.0),
    }
