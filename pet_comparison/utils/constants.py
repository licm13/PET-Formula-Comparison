"""
Physical and meteorological constants used in PET calculations
"""

import numpy as np

# Physical constants
STEFAN_BOLTZMANN = 5.67e-8  # Stefan-Boltzmann constant (W m-2 K-4)
SPECIFIC_HEAT_AIR = 1013.0  # Specific heat of air at constant pressure (J kg-1 K-1)
LATENT_HEAT_VAPORIZATION = 2.45e6  # Latent heat of vaporization (J kg-1)
GAS_CONSTANT = 8.314  # Universal gas constant (J mol-1 K-1)
MOLECULAR_WEIGHT_WATER = 18.015  # Molecular weight of water (g mol-1)
MOLECULAR_WEIGHT_AIR = 28.97  # Molecular weight of dry air (g mol-1)
VON_KARMAN = 0.41  # von Karman constant
GRAVITY = 9.81  # Gravitational acceleration (m s-2)

# Standard atmospheric pressure (Pa)
STANDARD_PRESSURE = 101325.0

# Psychrometric constant at standard pressure (kPa K-1)
PSYCHROMETRIC_CONSTANT = 0.067

# Reference values
T_ZERO = 273.15  # Zero Celsius in Kelvin
T_REF = 293.15  # Reference temperature (20°C in Kelvin)

# Priestley-Taylor coefficient
ALPHA_PT = 1.26  # Standard Priestley-Taylor coefficient

# CO2 reference concentration (ppm)
CO2_REF = 380.0  # Pre-industrial reference CO2 level


def get_latent_heat(temperature):
    """
    Calculate latent heat of vaporization as a function of temperature
    
    Parameters:
    -----------
    temperature : float or array-like
        Air temperature (°C)
    
    Returns:
    --------
    lambda_v : float or array-like
        Latent heat of vaporization (MJ kg-1)
    """
    return 2.501 - 0.002361 * temperature


def get_psychrometric_constant(pressure, temperature):
    """
    Calculate psychrometric constant
    
    Parameters:
    -----------
    pressure : float or array-like
        Atmospheric pressure (kPa)
    temperature : float or array-like
        Air temperature (°C)
    
    Returns:
    --------
    gamma : float or array-like
        Psychrometric constant (kPa °C-1)
    """
    # Simplified formula: gamma = cp * P / (epsilon * lambda)
    # For standard conditions, gamma ≈ 0.665e-3 * P (kPa)
    # More accurate: gamma = 0.665e-3 * P / lambda_v
    # But lambda_v varies little (~2.45 MJ/kg), so simplified form is typically used
    return 0.665e-3 * pressure


def saturation_vapor_pressure(temperature):
    """
    Calculate saturation vapor pressure using Tetens formula
    
    Parameters:
    -----------
    temperature : float or array-like
        Air temperature (°C)
    
    Returns:
    --------
    es : float or array-like
        Saturation vapor pressure (kPa)
    """
    return 0.6108 * np.exp((17.27 * temperature) / (temperature + 237.3))


def slope_saturation_vapor_pressure(temperature):
    """
    Calculate slope of saturation vapor pressure curve
    
    Parameters:
    -----------
    temperature : float or array-like
        Air temperature (°C)
    
    Returns:
    --------
    delta : float or array-like
        Slope of saturation vapor pressure curve (kPa °C-1)
    """
    es = saturation_vapor_pressure(temperature)
    return 4098 * es / ((temperature + 237.3) ** 2)


def actual_vapor_pressure(temperature, relative_humidity=None, dewpoint=None):
    """
    Calculate actual vapor pressure
    
    Parameters:
    -----------
    temperature : float or array-like
        Air temperature (°C)
    relative_humidity : float or array-like, optional
        Relative humidity (%)
    dewpoint : float or array-like, optional
        Dewpoint temperature (°C)
    
    Returns:
    --------
    ea : float or array-like
        Actual vapor pressure (kPa)
    """
    if relative_humidity is not None:
        es = saturation_vapor_pressure(temperature)
        return es * relative_humidity / 100.0
    elif dewpoint is not None:
        return saturation_vapor_pressure(dewpoint)
    else:
        raise ValueError("Either relative_humidity or dewpoint must be provided")


def vapor_pressure_deficit(temperature, relative_humidity=None, dewpoint=None):
    """
    Calculate vapor pressure deficit
    
    Parameters:
    -----------
    temperature : float or array-like
        Air temperature (°C)
    relative_humidity : float or array-like, optional
        Relative humidity (%)
    dewpoint : float or array-like, optional
        Dewpoint temperature (°C)
    
    Returns:
    --------
    vpd : float or array-like
        Vapor pressure deficit (kPa)
    """
    es = saturation_vapor_pressure(temperature)
    ea = actual_vapor_pressure(temperature, relative_humidity, dewpoint)
    return es - ea


def air_density(temperature, pressure, relative_humidity=None):
    """
    Calculate air density
    
    Parameters:
    -----------
    temperature : float or array-like
        Air temperature (°C)
    pressure : float or array-like
        Atmospheric pressure (kPa)
    relative_humidity : float or array-like, optional
        Relative humidity (%)
    
    Returns:
    --------
    rho : float or array-like
        Air density (kg m-3)
    """
    # Convert to Kelvin and Pa
    T_k = temperature + T_ZERO
    P_pa = pressure * 1000
    
    if relative_humidity is not None:
        ea = actual_vapor_pressure(temperature, relative_humidity)
        # Account for water vapor
        rho = (P_pa - ea * 1000) / (287.05 * T_k) + ea * 1000 / (461.5 * T_k)
    else:
        # Dry air
        rho = P_pa / (287.05 * T_k)
    
    return rho
