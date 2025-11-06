"""
Priestley-Taylor PET Formula
Simplified energy-based approach
"""

import numpy as np
from ..utils.constants import (
    slope_saturation_vapor_pressure,
    get_psychrometric_constant,
    ALPHA_PT,
)


def priestley_taylor(
    temperature,
    net_radiation,
    pressure=101.3,
    soil_heat_flux=0.0,
    alpha=ALPHA_PT,
):
    """
    Calculate potential evapotranspiration using Priestley-Taylor equation
    
    The Priestley-Taylor equation is a simplified form of the Penman equation
    that eliminates the need for wind speed and humidity data by using an
    empirical coefficient (alpha) to account for the advective component.
    
    Parameters:
    -----------
    temperature : float or array-like
        Air temperature (°C)
    net_radiation : float or array-like
        Net radiation (MJ m-2 day-1)
    pressure : float or array-like, optional
        Atmospheric pressure (kPa), default: 101.3
    soil_heat_flux : float or array-like, optional
        Soil heat flux (MJ m-2 day-1), default: 0.0
    alpha : float, optional
        Priestley-Taylor coefficient, default: 1.26
        (1.26 for well-watered surfaces, can vary from 1.1-1.3)
    
    Returns:
    --------
    PET : float or array-like
        Potential evapotranspiration (mm day-1)
    
    References:
    -----------
    Priestley, C.H.B. and Taylor, R.J., 1972.
    On the assessment of surface heat flux and evaporation using large-scale parameters.
    Monthly Weather Review, 100(2), pp.81-92.
    """
    # Calculate slope of saturation vapor pressure curve
    delta = slope_saturation_vapor_pressure(temperature)
    
    # Calculate psychrometric constant
    gamma = get_psychrometric_constant(pressure, temperature)
    
    # Lambda (latent heat of vaporization) in MJ kg-1
    lambda_v = 2.45
    
    # Calculate PET using Priestley-Taylor equation
    PET = alpha * (delta / (delta + gamma)) * (net_radiation - soil_heat_flux) / lambda_v
    
    # Ensure non-negative values
    PET = np.maximum(PET, 0.0)
    
    return PET


def priestley_taylor_with_advection(
    temperature,
    net_radiation,
    vapor_pressure_deficit,
    pressure=101.3,
    soil_heat_flux=0.0,
    alpha=ALPHA_PT,
):
    """
    Modified Priestley-Taylor with advection term
    
    Parameters:
    -----------
    temperature : float or array-like
        Air temperature (°C)
    net_radiation : float or array-like
        Net radiation (MJ m-2 day-1)
    vapor_pressure_deficit : float or array-like
        Vapor pressure deficit (kPa)
    pressure : float or array-like, optional
        Atmospheric pressure (kPa)
    soil_heat_flux : float or array-like, optional
        Soil heat flux (MJ m-2 day-1)
    alpha : float, optional
        Priestley-Taylor coefficient
    
    Returns:
    --------
    PET : float or array-like
        Potential evapotranspiration (mm day-1)
    """
    # Calculate slope of saturation vapor pressure curve
    delta = slope_saturation_vapor_pressure(temperature)
    
    # Calculate psychrometric constant
    gamma = get_psychrometric_constant(pressure, temperature)
    
    # Lambda (latent heat of vaporization)
    lambda_v = 2.45
    
    # Equilibrium evaporation
    PET_eq = (delta / (delta + gamma)) * (net_radiation - soil_heat_flux) / lambda_v
    
    # Add advection component based on VPD
    # This is a simplified approach
    advection_factor = 1 + 0.1 * vapor_pressure_deficit
    
    PET = alpha * PET_eq * advection_factor
    
    # Ensure non-negative values
    PET = np.maximum(PET, 0.0)
    
    return PET
