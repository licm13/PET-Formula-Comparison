"""
Meteorological utility functions
"""

import numpy as np
from .constants import GRAVITY, T_ZERO


def net_radiation(shortwave_in, albedo, longwave_in=None, temperature=None, emissivity=0.98):
    """
    Calculate net radiation
    
    Parameters:
    -----------
    shortwave_in : float or array-like
        Incoming shortwave radiation (W m-2)
    albedo : float or array-like
        Surface albedo (0-1)
    longwave_in : float or array-like, optional
        Incoming longwave radiation (W m-2)
    temperature : float or array-like, optional
        Surface temperature (°C), used if longwave_in not provided
    emissivity : float, optional
        Surface emissivity (default: 0.98)
    
    Returns:
    --------
    Rn : float or array-like
        Net radiation (W m-2)
    """
    # Net shortwave
    Rns = (1 - albedo) * shortwave_in
    
    # Net longwave
    if longwave_in is not None:
        from .constants import STEFAN_BOLTZMANN
        if temperature is not None:
            T_k = temperature + T_ZERO
        else:
            # Default to 20°C (293.15 K) if temperature not provided
            T_k = 293.15
        Rnl = longwave_in - emissivity * STEFAN_BOLTZMANN * (T_k ** 4)
    else:
        # Simplified approach if longwave not available
        Rnl = 0
    
    return Rns + Rnl


def extraterrestrial_radiation(doy, latitude):
    """
    Calculate extraterrestrial radiation
    
    Parameters:
    -----------
    doy : int or array-like
        Day of year (1-365)
    latitude : float or array-like
        Latitude (degrees)
    
    Returns:
    --------
    Ra : float or array-like
        Extraterrestrial radiation (MJ m-2 day-1)
    """
    # Solar constant
    Gsc = 0.0820  # MJ m-2 min-1
    
    # Convert latitude to radians
    lat_rad = np.deg2rad(latitude)
    
    # Inverse relative distance Earth-Sun
    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365)
    
    # Solar declination
    delta = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    
    # Sunset hour angle
    ws = np.arccos(-np.tan(lat_rad) * np.tan(delta))
    
    # Extraterrestrial radiation
    Ra = (24 * 60 / np.pi) * Gsc * dr * (
        ws * np.sin(lat_rad) * np.sin(delta) + 
        np.cos(lat_rad) * np.cos(delta) * np.sin(ws)
    )
    
    return Ra


def clear_sky_radiation(elevation, Ra):
    """
    Calculate clear sky radiation
    
    Parameters:
    -----------
    elevation : float or array-like
        Elevation above sea level (m)
    Ra : float or array-like
        Extraterrestrial radiation (MJ m-2 day-1)
    
    Returns:
    --------
    Rso : float or array-like
        Clear sky radiation (MJ m-2 day-1)
    """
    return (0.75 + 2e-5 * elevation) * Ra


def atmospheric_pressure(elevation):
    """
    Calculate atmospheric pressure as function of elevation
    
    Parameters:
    -----------
    elevation : float or array-like
        Elevation above sea level (m)
    
    Returns:
    --------
    P : float or array-like
        Atmospheric pressure (kPa)
    """
    return 101.3 * ((293 - 0.0065 * elevation) / 293) ** 5.26


def wind_speed_adjustment(u_z, z=2.0):
    """
    Adjust wind speed to 2m height
    
    Parameters:
    -----------
    u_z : float or array-like
        Wind speed at height z (m s-1)
    z : float, optional
        Height of wind measurement (m), default: 2.0
    
    Returns:
    --------
    u_2 : float or array-like
        Wind speed at 2m height (m s-1)
    """
    if z == 2.0:
        return u_z
    else:
        # Logarithmic wind profile
        return u_z * (4.87 / np.log(67.8 * z - 5.42))


def aerodynamic_resistance(wind_speed, height=2.0, roughness_length=0.03):
    """
    Calculate aerodynamic resistance
    
    Parameters:
    -----------
    wind_speed : float or array-like
        Wind speed at reference height (m s-1)
    height : float, optional
        Reference height (m), default: 2.0
    roughness_length : float, optional
        Surface roughness length (m), default: 0.03
    
    Returns:
    --------
    ra : float or array-like
        Aerodynamic resistance (s m-1)
    """
    from .constants import VON_KARMAN
    
    # Zero plane displacement
    d = 2.0 / 3.0 * roughness_length * 10
    
    # Roughness length for heat
    z0h = 0.1 * roughness_length
    
    # Calculate resistance
    ra = (np.log((height - d) / roughness_length) * 
          np.log((height - d) / z0h)) / (VON_KARMAN ** 2 * wind_speed)
    
    return ra
