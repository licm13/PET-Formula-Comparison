"""
Penman-Monteith-Leuning (PML) Model
Extended PM model accounting for LAI and vegetation dynamics
"""

import numpy as np
from ..utils.constants import (
    slope_saturation_vapor_pressure,
    get_psychrometric_constant,
    actual_vapor_pressure,
    saturation_vapor_pressure,
)


def penman_monteith_leuning(
    temperature,
    relative_humidity,
    wind_speed,
    net_radiation,
    lai,
    pressure=101.3,
    soil_heat_flux=0.0,
    co2=380.0,
):
    """
    Calculate evapotranspiration using Penman-Monteith-Leuning (PML) model
    
    The PML model extends the PM equation by explicitly considering LAI
    and its effect on canopy conductance and radiation partitioning.
    
    Parameters:
    -----------
    temperature : float or array-like
        Air temperature (°C)
    relative_humidity : float or array-like
        Relative humidity (%)
    wind_speed : float or array-like
        Wind speed at reference height (m s-1)
    net_radiation : float or array-like
        Net radiation (MJ m-2 day-1)
    lai : float or array-like
        Leaf Area Index (m2 m-2)
    pressure : float or array-like, optional
        Atmospheric pressure (kPa)
    soil_heat_flux : float or array-like, optional
        Soil heat flux (MJ m-2 day-1)
    co2 : float or array-like, optional
        Atmospheric CO2 concentration (ppm), default: 380
    
    Returns:
    --------
    dict : Dictionary containing:
        - 'total': Total ET (mm day-1)
        - 'transpiration': Canopy transpiration (mm day-1)
        - 'evaporation': Soil evaporation (mm day-1)
    
    References:
    -----------
    Zhang, Y., Peña-Arancibia, J.L., McVicar, T.R., Chiew, F.H., Vaze, J.,
    Liu, C., Lu, X., Zheng, H., Wang, Y., Liu, Y.Y. and Miralles, D.G., 2016.
    Multi-decadal trends in global terrestrial evapotranspiration and its components.
    Scientific reports, 6(1), pp.1-12.
    """
    # Calculate slope of saturation vapor pressure curve
    delta = slope_saturation_vapor_pressure(temperature)
    
    # Calculate psychrometric constant
    gamma = get_psychrometric_constant(pressure, temperature)
    
    # Calculate vapor pressure deficit
    es = saturation_vapor_pressure(temperature)
    ea = actual_vapor_pressure(temperature, relative_humidity=relative_humidity)
    vpd = es - ea
    
    # Lambda (latent heat of vaporization)
    lambda_v = 2.45
    
    # Canopy conductance with LAI effect
    # Maximum canopy conductance (mm s-1)
    gc_max = 0.006  # m s-1 = 6 mm s-1 at standard conditions
    
    # LAI effect on conductance
    f_lai = 1 - np.exp(-0.5 * lai)
    
    # Temperature response function
    t_opt = 25.0  # Optimal temperature
    f_temp = np.exp(-((temperature - t_opt) ** 2) / 200.0)
    
    # VPD response function (stomatal closure at high VPD)
    vpd_max = 3.0  # kPa
    f_vpd = np.exp(-vpd / vpd_max)
    
    # Surface conductance
    gc = gc_max * f_lai * f_temp * f_vpd
    
    # Aerodynamic resistance
    ra = 208.0 / wind_speed
    
    # Surface resistance (inverse of conductance)
    # Convert conductance from m/s to s/m
    rs = 1.0 / (gc + 1e-6)  # Add small value to avoid division by zero
    rs = np.clip(rs, 10, 1000)  # Reasonable bounds
    
    # Partition radiation between canopy and soil
    f_canopy = 1 - np.exp(-0.6 * lai)
    Rn_canopy = net_radiation * f_canopy
    Rn_soil = net_radiation * (1 - f_canopy)
    
    # Canopy transpiration (Penman-Monteith)
    numerator_c = delta * Rn_canopy + (1.01 * 1013 * vpd / ra)  # rho*cp*VPD/ra
    denominator_c = lambda_v * (delta + gamma * (1 + rs / ra))
    transpiration = numerator_c / denominator_c
    
    # Soil evaporation (Priestley-Taylor for equilibrium evaporation)
    evaporation = 1.26 * (delta / (delta + gamma)) * (Rn_soil - soil_heat_flux) / lambda_v
    
    # Total ET
    total_et = transpiration + evaporation
    
    return {
        'total': np.maximum(total_et, 0.0),
        'transpiration': np.maximum(transpiration, 0.0),
        'evaporation': np.maximum(evaporation, 0.0),
    }


def pml_v2(
    temperature,
    relative_humidity,
    wind_speed,
    net_radiation,
    lai,
    soil_moisture,
    pressure=101.3,
    soil_heat_flux=0.0,
):
    """
    PML Version 2 with improved soil moisture constraint
    
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
    dict : Dictionary with ET components
    """
    # Get base PML results
    result = penman_monteith_leuning(
        temperature, relative_humidity, wind_speed,
        net_radiation, lai, pressure, soil_heat_flux
    )
    
    # Apply soil moisture constraint
    # Transpiration is more sensitive to soil moisture
    sm_crit = 0.3
    f_sm_transp = np.clip((soil_moisture - sm_crit) / (1 - sm_crit), 0, 1)
    
    # Soil evaporation has different soil moisture response
    f_sm_evap = np.sqrt(np.clip(soil_moisture, 0, 1))
    
    # Apply constraints
    result['transpiration'] = result['transpiration'] * f_sm_transp
    result['evaporation'] = result['evaporation'] * f_sm_evap
    result['total'] = result['transpiration'] + result['evaporation']
    
    return result
