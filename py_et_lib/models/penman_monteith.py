"""Penman-Monteith family evapotranspiration models."""
from __future__ import annotations

import numpy as np
import xarray as xr

from ..core.base_models import PenmanMonteithBase
from ..core.constants import CONSTANTS
from ..utils.validators import ensure_params, ensure_variables


REQUIRED_MET_VARS = {
    "T_mean",
    "Rn",
    "G",
    "RH",
    "VPD",
    "u2",
    "LAI",
}


def _saturation_vapour_pressure(temp_c: xr.DataArray) -> xr.DataArray:
    return 0.6108 * xr.apply_ufunc(np.exp, (17.27 * temp_c) / (temp_c + 237.3))


def _slope_svp_curve(temp_c: xr.DataArray) -> xr.DataArray:
    return 4098 * _saturation_vapour_pressure(temp_c) / (temp_c + 237.3) ** 2


def _vpd_from_rh(temp_c: xr.DataArray, rh: xr.DataArray) -> xr.DataArray:
    es = _saturation_vapour_pressure(temp_c)
    ea = es * rh / 100.0
    return es - ea


class MOD16(PenmanMonteithBase):
    """Simplified implementation of the MOD16 evapotranspiration model."""

    def _validate_inputs(self) -> None:  # noqa: D401
        ensure_params(self.params, ["bplut_params"])

    def _compute_aerodynamic_resistance(self, ds: xr.Dataset) -> xr.DataArray:
        """Approximate aerodynamic resistance using wind speed and LAI."""

        wind = ds["u2"].clip(min=0.1)
        lai = ds["LAI"].clip(min=0.1)
        return 100.0 / (wind * np.sqrt(lai))

    def _compute_surface_resistance(self, ds: xr.Dataset) -> xr.DataArray:
        """Simplified canopy/soil resistance parameterisation."""

        rh = ds["RH"].clip(0, 100)
        vpd = ds.get("VPD", _vpd_from_rh(ds["T_mean"], rh))
        tmin = ds.get("T_min", ds["T_mean"] - 5.0)

        wet_canopy = xr.where(rh > 80, 0.0, 1.0)

        stress_temp = xr.where(tmin < 0, 0.1, 1.0 - (tmin - 5.0) / 40.0)
        stress_temp = xr.clip(stress_temp, 0.1, 1.0)
        stress_vpd = xr.where(vpd < 0.5, 1.0, xr.clip(1.0 - (vpd - 0.5) / 3.0, 0.1, 1.0))
        g_s = 0.01 + 0.08 * stress_temp * stress_vpd
        r_c = xr.where(g_s > 0, 1.0 / g_s, 1e6)

        soil_moisture = ds.get("soil_moisture", xr.zeros_like(ds["Rn"]) + 0.2)
        soil_moisture_max = ds.get("soil_moisture_max", xr.zeros_like(soil_moisture) + 0.4)
        soil_stress = xr.clip(soil_moisture / soil_moisture_max, 0.05, 1.0)
        r_soil = 500.0 / soil_stress

        r_s = wet_canopy * 50.0 + (1.0 - wet_canopy) * (r_c + r_soil)
        return r_s.clip(min=10.0, max=2000.0)

    def compute_et(self, ds: xr.Dataset) -> xr.Dataset:  # noqa: D401
        ensure_variables(ds, REQUIRED_MET_VARS)

        delta = _slope_svp_curve(ds["T_mean"])
        gamma = CONSTANTS["GAMMA"]
        rho = CONSTANTS["RHO_AIR"]
        cp = CONSTANTS["CP_AIR"]

        vpd = ds.get("VPD", _vpd_from_rh(ds["T_mean"], ds["RH"]))
        ra = self._compute_aerodynamic_resistance(ds)
        rs = self._compute_surface_resistance(ds)

        numerator = delta * (ds["Rn"] - ds["G"]) + rho * cp * vpd / ra
        denominator = delta + gamma * (1.0 + rs / ra)
        le = numerator / denominator

        aet = le / CONSTANTS["LAMBDA_VAP"] * 86400 / 1e6
        return xr.Dataset({"AET": aet.rename("AET")})


class PMLv2(PenmanMonteithBase):
    """Two-source Penman-Monteith-Leuning model."""

    def _validate_inputs(self) -> None:  # noqa: D401
        # All parameters optional
        return None

    def _compute_gpp(self, ds: xr.Dataset) -> xr.DataArray:
        apar = ds.get("fAPAR", xr.zeros_like(ds["Rn"]) + 0.5) * ds["Rn"].clip(min=0)
        lue = self.params.get("lue", 1.5)
        temp_scalar = xr.where(ds["T_mean"] < 0, 0.0, 1.0)
        return apar * lue * temp_scalar

    def _compute_canopy_conductance(self, ds: xr.Dataset) -> xr.DataArray:
        gpp = self._compute_gpp(ds)
        g0 = self.params.get("g0", 0.01)
        k = self.params.get("k", 0.05)
        d0 = self.params.get("D0", 1.5)
        gamma_star = self.params.get("Gamma", 40.0)

        co2 = ds.get("CO2", xr.zeros_like(ds["Rn"]) + 400.0)
        vpd = ds.get(
            "VPD",
            _vpd_from_rh(
                ds["T_mean"],
                ds.get("RH", xr.zeros_like(ds["T_mean"]) + 60),
            ),
        )
        return (g0 + (k * gpp) / ((co2 - gamma_star) * (1.0 + vpd / d0))).clip(min=1e-4)

    def compute_et(self, ds: xr.Dataset) -> xr.Dataset:
        ensure_variables(ds, {"Rn", "G", "T_mean"})

        delta = _slope_svp_curve(ds["T_mean"])
        gamma = CONSTANTS["GAMMA"]
        rho = CONSTANTS["RHO_AIR"]
        cp = CONSTANTS["CP_AIR"]

        ga = self.params.get("ga", 0.01)  # aerodynamic conductance [m/s]
        gc = self._compute_canopy_conductance(ds)

        vpd = ds.get(
            "VPD",
            _vpd_from_rh(
                ds["T_mean"],
                ds.get("RH", xr.zeros_like(ds["T_mean"]) + 60),
            ),
        )

        ac = ds["Rn"] * 0.6
        as_ = ds["Rn"] * 0.4

        le_c = (delta * ac + rho * cp * vpd * ga) / (delta + gamma * (1.0 + ga / gc))
        soil_factor = self.params.get("soil_factor", 0.8)
        le_s = soil_factor * delta * as_ / (delta + gamma)
        le_total = le_c + le_s

        aet = le_total / CONSTANTS["LAMBDA_VAP"] * 86400 / 1e6
        return xr.Dataset({"AET": aet.rename("AET")})

    def partition_components(self, ds: xr.Dataset) -> xr.Dataset:
        ensure_variables(ds, {"Rn", "G", "T_mean"})
        delta = _slope_svp_curve(ds["T_mean"])
        gamma = CONSTANTS["GAMMA"]
        rho = CONSTANTS["RHO_AIR"]
        cp = CONSTANTS["CP_AIR"]

        ga = self.params.get("ga", 0.01)
        gc = self._compute_canopy_conductance(ds)
        vpd = ds.get(
            "VPD",
            _vpd_from_rh(
                ds["T_mean"],
                ds.get("RH", xr.zeros_like(ds["T_mean"]) + 60),
            ),
        )

        ac = ds["Rn"] * 0.6
        as_ = ds["Rn"] * 0.4

        le_c = (delta * ac + rho * cp * vpd * ga) / (delta + gamma * (1.0 + ga / gc))
        soil_factor = self.params.get("soil_factor", 0.8)
        le_s = soil_factor * delta * as_ / (delta + gamma)

        mm_conversion = 86400 / 1e6 / CONSTANTS["LAMBDA_VAP"]
        transp = le_c * mm_conversion
        soil = le_s * mm_conversion
        return xr.Dataset({"transpiration": transp, "soil_evaporation": soil})

