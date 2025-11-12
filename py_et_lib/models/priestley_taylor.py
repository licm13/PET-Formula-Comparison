"""Priestley-Taylor style evapotranspiration models."""
from __future__ import annotations

import numpy as np
import xarray as xr

from ..core.base_models import PriestleyTaylorBase
from ..core.constants import CONSTANTS
from ..utils.validators import ensure_params, ensure_variables


def _slope_svp_curve(temp_c: xr.DataArray) -> xr.DataArray:
    es = 0.6108 * xr.apply_ufunc(np.exp, (17.27 * temp_c) / (temp_c + 237.3))
    return 4098 * es / (temp_c + 237.3) ** 2


class PTJPL(PriestleyTaylorBase):
    """Implementation of the PT-JPL evapotranspiration formulation."""

    def _validate_inputs(self) -> None:  # noqa: D401
        ensure_params(self.params, ["T_opt", "fAPAR_max"])

    @staticmethod
    def _calc_alpha_term(delta: xr.DataArray, gamma: float, rn_component: xr.DataArray) -> xr.DataArray:
        return 1.26 * (delta / (delta + gamma)) * rn_component

    @staticmethod
    def _calc_f_wet(rh: xr.DataArray) -> xr.DataArray:
        return (rh / 100.0) ** 4

    @staticmethod
    def _calc_f_sm(vpd: xr.DataArray, rh_min: xr.DataArray) -> xr.DataArray:
        beta = 2.0
        return xr.clip(rh_min / (vpd / beta + 1e-6), 0.0, 1.0)

    @staticmethod
    def _calc_f_c(fapar: xr.DataArray, fipar: xr.DataArray) -> xr.DataArray:
        return xr.where(fipar > 0, fapar / fipar, 0.0).clip(0.0, 1.0)

    def _calc_f_t(self, tmax: xr.DataArray) -> xr.DataArray:
        t_opt = self.params["T_opt"]
        return xr.apply_ufunc(np.exp, -((tmax - t_opt) / t_opt) ** 2)

    def _calc_f_m(self, fapar: xr.DataArray) -> xr.DataArray:
        fapar_max = self.params["fAPAR_max"]
        return xr.clip(fapar / fapar_max, 0.0, 1.0)

    def compute_et(self, ds: xr.Dataset) -> xr.Dataset:
        ensure_variables(ds, {"Rn", "G", "T_mean", "T_max", "RH", "fAPAR", "fIPAR"})

        delta = _slope_svp_curve(ds["T_mean"])
        gamma = CONSTANTS["GAMMA"]

        rn_c = 0.6 * (ds["Rn"] - ds["G"])
        rn_s = 0.4 * (ds["Rn"] - ds["G"])

        f_wet = self._calc_f_wet(ds["RH"])
        rh_min = ds.get("RH_min", ds["RH"] * 0.75)
        vpd = ds.get("VPD", xr.zeros_like(ds["RH"]) + 1.0)
        f_sm = self._calc_f_sm(vpd, rh_min)
        f_c = self._calc_f_c(ds["fAPAR"], ds["fIPAR"])
        f_t = self._calc_f_t(ds["T_max"])
        f_m = self._calc_f_m(ds["fAPAR"])

        alpha_c = self._calc_alpha_term(delta, gamma, rn_c)
        alpha_s = self._calc_alpha_term(delta, gamma, rn_s)

        ei = f_wet * alpha_c
        es = (f_wet + (1.0 - f_wet) * f_sm) * alpha_s
        t = (1.0 - f_wet) * f_c * f_t * f_m * alpha_c

        mm_conversion = 1.0 / CONSTANTS["LAMBDA_VAP"] * 86400 / 1e6
        aet = (ei + es + t) * mm_conversion
        return xr.Dataset({"AET": aet.rename("AET")})

    def partition_components(self, ds: xr.Dataset) -> xr.Dataset:
        ensure_variables(ds, {"Rn", "G", "T_mean", "T_max", "RH", "fAPAR", "fIPAR"})

        delta = _slope_svp_curve(ds["T_mean"])
        gamma = CONSTANTS["GAMMA"]
        rn_c = 0.6 * (ds["Rn"] - ds["G"])
        rn_s = 0.4 * (ds["Rn"] - ds["G"])

        f_wet = self._calc_f_wet(ds["RH"])
        rh_min = ds.get("RH_min", ds["RH"] * 0.75)
        vpd = ds.get("VPD", xr.zeros_like(ds["RH"]) + 1.0)
        f_sm = self._calc_f_sm(vpd, rh_min)
        f_c = self._calc_f_c(ds["fAPAR"], ds["fIPAR"])
        f_t = self._calc_f_t(ds["T_max"])
        f_m = self._calc_f_m(ds["fAPAR"])

        alpha_c = self._calc_alpha_term(delta, gamma, rn_c)
        alpha_s = self._calc_alpha_term(delta, gamma, rn_s)

        ei = f_wet * alpha_c
        es = (f_wet + (1.0 - f_wet) * f_sm) * alpha_s
        t = (1.0 - f_wet) * f_c * f_t * f_m * alpha_c

        mm_conversion = 1.0 / CONSTANTS["LAMBDA_VAP"] * 86400 / 1e6
        return xr.Dataset(
            {
                "interception": ei * mm_conversion,
                "soil_evaporation": es * mm_conversion,
                "transpiration": t * mm_conversion,
            }
        )


class GLEAM(PriestleyTaylorBase):
    """Conceptual implementation of the GLEAM ET model."""

    def _validate_inputs(self) -> None:  # noqa: D401
        ensure_params(self.params, ["soil_moisture_max"])

    def _compute_stress_factor(self, ds: xr.Dataset) -> xr.DataArray:
        """Return a simplified soil moisture stress factor.

        Real-world GLEAM uses microwave soil moisture and vegetation optical depth
        to infer component-specific stress.  For this library skeleton we scale the
        observed soil moisture by its climatological maximum.
        """

        ensure_variables(ds, {"soil_moisture"})
        sm_max = self.params["soil_moisture_max"]
        return xr.clip(ds["soil_moisture"] / sm_max, 0.0, 1.0)

    def compute_et(self, ds: xr.Dataset) -> xr.Dataset:
        ensure_variables(ds, {"Rn", "G", "T_mean", "soil_moisture"})

        delta = _slope_svp_curve(ds["T_mean"])
        gamma = CONSTANTS["GAMMA"]
        potential_et = 1.26 * (delta / (delta + gamma)) * (ds["Rn"] - ds["G"])
        stress = self._compute_stress_factor(ds)
        aet = potential_et * stress / CONSTANTS["LAMBDA_VAP"] * 86400 / 1e6
        return xr.Dataset({"AET": aet.rename("AET")})

