"""Meteorological utility functions for ET calculations."""
from __future__ import annotations

import numpy as np
import xarray as xr


def _saturation_vapour_pressure(temp_c: xr.DataArray) -> xr.DataArray:
    """Calculate saturation vapour pressure using Tetens formula.

    Parameters
    ----------
    temp_c : xr.DataArray
        Air temperature in degrees Celsius

    Returns
    -------
    xr.DataArray
        Saturation vapour pressure in kPa
    """
    return 0.6108 * xr.apply_ufunc(np.exp, (17.27 * temp_c) / (temp_c + 237.3))


def _slope_svp_curve(temp_c: xr.DataArray) -> xr.DataArray:
    """Calculate slope of saturation vapour pressure curve.

    Parameters
    ----------
    temp_c : xr.DataArray
        Air temperature in degrees Celsius

    Returns
    -------
    xr.DataArray
        Slope of saturation vapour pressure curve in kPa/°C
    """
    return 4098 * _saturation_vapour_pressure(temp_c) / (temp_c + 237.3) ** 2


def _vpd_from_rh(temp_c: xr.DataArray, rh: xr.DataArray) -> xr.DataArray:
    """Calculate vapour pressure deficit from temperature and relative humidity.

    Parameters
    ----------
    temp_c : xr.DataArray
        Air temperature in degrees Celsius
    rh : xr.DataArray
        Relative humidity in percent (0-100)

    Returns
    -------
    xr.DataArray
        Vapour pressure deficit in kPa
    """
    es = _saturation_vapour_pressure(temp_c)
    ea = es * rh / 100.0
    return es - ea
