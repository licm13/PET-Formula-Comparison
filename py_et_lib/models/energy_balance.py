"""Energy balance evapotranspiration models."""
from __future__ import annotations

import xarray as xr

from ..core.base_models import EnergyBalanceBase
from ..core.constants import CONSTANTS
from ..utils.validators import ensure_variables
from . import pet


def _clip_fraction(values: xr.DataArray) -> xr.DataArray:
    return values.clip(min=0.0, max=1.0)


class SEBAL(EnergyBalanceBase):
    """Simplified Surface Energy Balance Algorithm for Land."""

    def _validate_inputs(self) -> None:  # noqa: D401
        return None

    def _compute_sensible_heat(self, ds: xr.Dataset) -> xr.DataArray:
        ensure_variables(ds, {"Rn", "G", "LST", "ra"})

        lst = ds["LST"]
        ra = ds["ra"].clip(min=1.0)

        hot_mask = lst >= lst.quantile(0.95, dim=["lat", "lon"], skipna=True)
        cold_mask = lst <= lst.quantile(0.05, dim=["lat", "lon"], skipna=True)

        rn_hot = ds["Rn"].where(hot_mask).mean(dim="time")
        g_hot = ds["G"].where(hot_mask).mean(dim="time")
        h_hot = rn_hot - g_hot

        rn_cold = ds["Rn"].where(cold_mask).mean(dim="time")
        g_cold = ds["G"].where(cold_mask).mean(dim="time")
        h_cold = xr.zeros_like(h_hot)

        dt_hot = (h_hot * ra.where(hot_mask).mean(dim="time")) / (CONSTANTS["RHO_AIR"] * CONSTANTS["CP_AIR"])
        dt_cold = (h_cold * ra.where(cold_mask).mean(dim="time")) / (CONSTANTS["RHO_AIR"] * CONSTANTS["CP_AIR"])

        a = (dt_hot - dt_cold) / (lst.where(hot_mask).mean(dim="time") - lst.where(cold_mask).mean(dim="time") + 1e-6)
        b = dt_hot - a * lst.where(hot_mask).mean(dim="time")

        dt = a * lst + b
        return CONSTANTS["RHO_AIR"] * CONSTANTS["CP_AIR"] * dt / ra

    def compute_et(self, ds: xr.Dataset) -> xr.Dataset:
        ensure_variables(ds, {"Rn", "G", "LST", "ra"})
        h = self._compute_sensible_heat(ds)
        le = ds["Rn"] - ds["G"] - h
        aet = le / CONSTANTS["LAMBDA_VAP"] * 86400 / 1e6
        return xr.Dataset({"AET": aet.rename("AET")})


class SSEBop(EnergyBalanceBase):
    """Operational Simplified Surface Energy Balance model."""

    def _validate_inputs(self) -> None:  # noqa: D401
        return None

    def _compute_cold_limit(self, ds: xr.Dataset) -> xr.DataArray:
        air_temp = ds.get("T_air", ds["T_mean"])
        return air_temp - 2.0

    def _compute_hot_limit(self, ds: xr.Dataset, tc: xr.DataArray) -> xr.DataArray:
        rn = ds["Rn"]
        g = ds["G"]
        ra = ds.get("ra", xr.zeros_like(rn) + 50.0)
        delta_t = (rn - g) * ra / (CONSTANTS["RHO_AIR"] * CONSTANTS["CP_AIR"])
        return tc + delta_t

    def _compute_et_fraction(self, ds: xr.Dataset) -> xr.DataArray:
        tc = self._compute_cold_limit(ds)
        th = self._compute_hot_limit(ds, tc)
        ts = ds["LST"]
        etf = (th - ts) / (th - tc + 1e-6)
        return _clip_fraction(etf)

    def compute_et(self, ds: xr.Dataset) -> xr.Dataset:
        ensure_variables(ds, {"Rn", "G", "LST", "T_mean"})
        eto = pet.fao56_penman_monteith(ds)
        etf = self._compute_et_fraction(ds)
        aet = etf * eto
        return xr.Dataset({"AET": aet.rename("AET")})

