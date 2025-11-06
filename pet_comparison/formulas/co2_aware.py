"""
CO2-aware PET formulas
Accounting for elevated CO2 effects on stomatal conductance and PET
"""

import numpy as np
from ..utils.constants import (
    slope_saturation_vapor_pressure,
    get_psychrometric_constant,
    actual_vapor_pressure,
    saturation_vapor_pressure,
    CO2_REF,
)


def pm_co2_aware(
    temperature,
    relative_humidity,
    wind_speed,
    net_radiation,
    co2,
    pressure=101.3,
    soil_heat_flux=0.0,
):
    """
    CO2-aware Penman-Monteith model
    
    This model accounts for the effect of elevated CO2 on stomatal conductance,
    which reduces transpiration rates. Based on the approach from:
    "Hydrologic implications of vegetation response to elevated CO2 in climate projections"
    
    Parameters:
    -----------
    temperature : float or array-like
        Air temperature (°C)
    relative_humidity : float or array-like
        Relative humidity (%)
    wind_speed : float or array-like
        Wind speed at 2m height (m s-1)
    net_radiation : float or array-like
        Net radiation (MJ m-2 day-1)
    co2 : float or array-like
        Atmospheric CO2 concentration (ppm)
    pressure : float or array-like, optional
        Atmospheric pressure (kPa)
    soil_heat_flux : float or array-like, optional
        Soil heat flux (MJ m-2 day-1)
    
    Returns:
    --------
    PET : float or array-like
        Potential evapotranspiration (mm day-1)
    
    References:
    -----------
    Milly, P.C.D. and Dunne, K.A., 2016.
    Potential evapotranspiration and continental drying.
    Nature Climate Change, 6(10), pp.946-949.
    
    Swann, A.L., Hoffman, F.M., Koven, C.D. and Randerson, J.T., 2016.
    Plant responses to increasing CO2 reduce estimates of climate impacts on drought severity.
    Proceedings of the National Academy of Sciences, 113(36), pp.10019-10024.
    """
    # Calculate slope of saturation vapor pressure curve
    delta = slope_saturation_vapor_pressure(temperature)
    
    # Calculate psychrometric constant
    gamma = get_psychrometric_constant(pressure, temperature)
    
    # Calculate vapor pressure deficit
    es = saturation_vapor_pressure(temperature)
    ea = actual_vapor_pressure(temperature, relative_humidity=relative_humidity)
    vpd = es - ea
    
    # CO2 effect on stomatal conductance
    # Stomatal conductance decreases with increasing CO2
    # Typical response: conductance proportional to 1/sqrt(CO2)
    # or linear decrease: gc = gc_ref * (1 - beta * (CO2 - CO2_ref)/CO2_ref)
    
    # Method 1: Square root relationship (more common)
    co2_factor = np.sqrt(CO2_REF / co2)
    
    # Method 2: Linear relationship (alternative)
    # beta = 0.3  # Sensitivity parameter (typically 0.2-0.4)
    # co2_factor = 1 - beta * (co2 - CO2_REF) / CO2_REF
    # co2_factor = np.clip(co2_factor, 0.5, 1.5)
    
    # Reference surface resistance (s m-1)
    rs_ref = 70.0
    
    # Adjust surface resistance based on CO2
    # Higher CO2 -> higher resistance (lower conductance)
    rs = rs_ref / co2_factor
    
    # Aerodynamic resistance
    ra = 208.0 / wind_speed
    
    # Lambda (latent heat of vaporization)
    lambda_v = 2.45
    
    # Penman-Monteith equation with CO2-modified surface resistance
    numerator = delta * (net_radiation - soil_heat_flux) + (1.01 * 1013 * vpd / ra)
    denominator = lambda_v * (delta + gamma * (1 + rs / ra))
    
    PET = numerator / denominator
    
    # Ensure non-negative values
    PET = np.maximum(PET, 0.0)
    
    return PET


def pm_co2_lai_aware(
    temperature,
    relative_humidity,
    wind_speed,
    net_radiation,
    co2,
    lai,
    pressure=101.3,
    soil_heat_flux=0.0,
):
    """
    CO2 and LAI-aware Penman-Monteith model
    
    This model accounts for both CO2 effects on stomatal conductance and
    LAI effects on transpiration, following the approach from:
    "A physically-based potential evapotranspiration model for global water availability projections"
    
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
    co2 : float or array-like
        Atmospheric CO2 concentration (ppm)
    lai : float or array-like
        Leaf Area Index (m2 m-2)
    pressure : float or array-like, optional
        Atmospheric pressure (kPa)
    soil_heat_flux : float or array-like, optional
        Soil heat flux (MJ m-2 day-1)
    
    Returns:
    --------
    dict : Dictionary containing:
        - 'total': Total PET (mm day-1)
        - 'transpiration': Canopy transpiration (mm day-1)
        - 'evaporation': Soil evaporation (mm day-1)
    
    References:
    -----------
    Yang, Y., Roderick, M.L., Zhang, S., McVicar, T.R. and Donohue, R.J., 2019.
    Hydrologic implications of vegetation response to elevated CO2 in climate projections.
    Nature Climate Change, 9(1), pp.44-48.
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
    
    # CO2 effect on stomatal conductance
    co2_factor = np.sqrt(CO2_REF / co2)
    
    # LAI effect on canopy conductance
    # Maximum stomatal conductance (at leaf level)
    gs_max = 0.01  # m s-1
    
    # Canopy conductance scales with LAI
    # But saturates at high LAI
    gc = gs_max * lai * (1 - np.exp(-0.5 * lai)) * co2_factor
    
    # Convert to resistance
    rs_canopy = 1.0 / (gc + 1e-6)
    rs_canopy = np.clip(rs_canopy, 10, 1000)
    
    # Aerodynamic resistance
    ra = 208.0 / wind_speed
    
    # Partition net radiation
    # Canopy fraction increases with LAI
    f_canopy = 1 - np.exp(-0.6 * lai)
    Rn_canopy = net_radiation * f_canopy
    Rn_soil = net_radiation * (1 - f_canopy)
    
    # Canopy transpiration
    numerator_c = delta * Rn_canopy + (1.01 * 1013 * vpd / ra)
    denominator_c = lambda_v * (delta + gamma * (1 + rs_canopy / ra))
    transpiration = numerator_c / denominator_c
    
    # Soil evaporation (potential, without CO2 effect)
    evaporation = 1.26 * (delta / (delta + gamma)) * (Rn_soil - soil_heat_flux) / lambda_v
    
    # Total PET
    total_pet = transpiration + evaporation
    
    return {
        'total': np.maximum(total_pet, 0.0),
        'transpiration': np.maximum(transpiration, 0.0),
        'evaporation': np.maximum(evaporation, 0.0),
    }


def co2_response_factor(co2, method='sqrt'):
    """
    Calculate CO2 response factor for stomatal conductance
    
    Parameters:
    -----------
    co2 : float or array-like
        Atmospheric CO2 concentration (ppm)
    method : str, optional
        Method for calculating response ('sqrt', 'linear', 'log')
    
    Returns:
    --------
    factor : float or array-like
        CO2 response factor (1.0 at CO2_REF)
    """
    if method == 'sqrt':
        # Square root relationship (Ball-Berry model basis)
        return np.sqrt(CO2_REF / co2)
    elif method == 'linear':
        # Linear relationship
        beta = 0.3
        factor = 1 - beta * (co2 - CO2_REF) / CO2_REF
        return np.clip(factor, 0.5, 1.5)
    elif method == 'log':
        # Logarithmic relationship
        return 1 - 0.15 * np.log(co2 / CO2_REF)
    else:
        raise ValueError(f"Unknown method: {method}")
