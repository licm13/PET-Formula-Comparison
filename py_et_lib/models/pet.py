"""Reference evapotranspiration formulations."""
from __future__ import annotations

import numpy as np
import xarray as xr

from ..core.constants import CONSTANTS
from ..utils.validators import ensure_variables


def _saturation_vapour_pressure(temp_c: xr.DataArray) -> xr.DataArray:
    return 0.6108 * xr.apply_ufunc(np.exp, (17.27 * temp_c) / (temp_c + 237.3))


def _slope_svp_curve(temp_c: xr.DataArray) -> xr.DataArray:
    return 4098 * _saturation_vapour_pressure(temp_c) / (temp_c + 237.3) ** 2


def _mean_saturation_vapour_pressure(tmax: xr.DataArray, tmin: xr.DataArray) -> xr.DataArray:
    return (_saturation_vapour_pressure(tmax) + _saturation_vapour_pressure(tmin)) / 2.0


def fao56_penman_monteith(ds: xr.Dataset) -> xr.DataArray:
    """Return FAO-56 Penman-Monteith reference evapotranspiration."""

    ensure_variables(ds, {"T_mean", "T_max", "T_min", "Rn", "G", "u2"})
    rh = ds.get("RH")
    if rh is None:
        raise ValueError("Relative humidity 'RH' is required for FAO-56 computation.")

    delta = _slope_svp_curve(ds["T_mean"])
    es = _mean_saturation_vapour_pressure(ds["T_max"], ds["T_min"])
    ea = es * rh / 100.0
    vpd = es - ea

    gamma = CONSTANTS["GAMMA"]

    term1 = 0.408 * delta * (ds["Rn"] - ds["G"])
    term2 = gamma * (900.0 / (ds["T_mean"] + 273.0)) * ds["u2"] * vpd
    eto = (term1 + term2) / (delta + gamma * (1.0 + 0.34 * ds["u2"]))
    return eto.rename("ETo")


def _declination(day_of_year: xr.DataArray) -> xr.DataArray:
    return 0.409 * xr.apply_ufunc(np.sin, 2 * np.pi * day_of_year / 365 - 1.39)


def _inverse_relative_distance(day_of_year: xr.DataArray) -> xr.DataArray:
    return 1.0 + 0.033 * xr.apply_ufunc(np.cos, 2 * np.pi * day_of_year / 365)


def _sunset_hour_angle(latitude_rad: xr.DataArray, declination: xr.DataArray) -> xr.DataArray:
    return xr.apply_ufunc(np.arccos, -np.tan(latitude_rad) * np.tan(declination))


def _extraterrestrial_radiation(ds: xr.Dataset) -> xr.DataArray:
    ensure_variables(ds, {"latitude", "day_of_year"})
    lat_rad = np.deg2rad(ds["latitude"])
    doy = ds["day_of_year"]
    delta = _declination(doy)
    dr = _inverse_relative_distance(doy)
    ws = _sunset_hour_angle(lat_rad, delta)
    ra = (
        (24 * 60 / np.pi)
        * CONSTANTS["G_SC"]
        * dr
        * (ws * xr.apply_ufunc(np.sin, lat_rad) * xr.apply_ufunc(np.sin, delta)
           + xr.apply_ufunc(np.cos, lat_rad) * xr.apply_ufunc(np.cos, delta) * xr.apply_ufunc(np.sin, ws))
    )
    return ra


def hargreaves(ds: xr.Dataset) -> xr.DataArray:
    """Return reference ET from the Hargreaves equation."""

    ensure_variables(ds, {"T_max", "T_min", "T_mean", "latitude", "day_of_year"})
    ra = _extraterrestrial_radiation(ds)
    et0 = 0.0023 * ra * (ds["T_max"] - ds["T_min"]) ** 0.5 * (ds["T_mean"] + 17.8)
    return et0.rename("ETo")

