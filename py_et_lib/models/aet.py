"""Actual Evapotranspiration (AET) models.

This module consolidates all AET model implementations, organized by algorithm family:
- Penman-Monteith (P-M) resistance models: MOD16, PMLv2
- Priestley-Taylor (P-T) stress models: PTJPL, GLEAM
- Surface Energy Balance (SEB) residual models: SEBAL, SSEBop

Each model calculates actual evapotranspiration (AET), which represents the real water
flux from the land surface to the atmosphere, accounting for water availability,
vegetation stress, and environmental constraints.
"""
from __future__ import annotations

import numpy as np
import xarray as xr

from ..core.base_models import (
    EnergyBalanceBase,
    PenmanMonteithBase,
    PriestleyTaylorBase,
)
from ..core.constants import CONSTANTS
from ..utils.validators import ensure_params, ensure_variables

# ============================================================================
# Utility functions
# ============================================================================


def _saturation_vapour_pressure(temp_c: xr.DataArray) -> xr.DataArray:
    """Calculate saturation vapour pressure using Tetens formula."""
    return 0.6108 * xr.apply_ufunc(np.exp, (17.27 * temp_c) / (temp_c + 237.3))


def _slope_svp_curve(temp_c: xr.DataArray) -> xr.DataArray:
    """Calculate slope of saturation vapour pressure curve."""
    return 4098 * _saturation_vapour_pressure(temp_c) / (temp_c + 237.3) ** 2


def _vpd_from_rh(temp_c: xr.DataArray, rh: xr.DataArray) -> xr.DataArray:
    """Calculate vapour pressure deficit from temperature and relative humidity."""
    es = _saturation_vapour_pressure(temp_c)
    ea = es * rh / 100.0
    return es - ea


def _clip_fraction(values: xr.DataArray) -> xr.DataArray:
    """Clip values to valid fraction range [0, 1]."""
    return values.clip(min=0.0, max=1.0)


# ============================================================================
# Penman-Monteith (P-M) Resistance Models
# ============================================================================


REQUIRED_MET_VARS = {
    "T_mean",
    "Rn",
    "G",
    "RH",
    "VPD",
    "u2",
    "LAI",
}


class MOD16(PenmanMonteithBase):
    """Calculate Actual Evapotranspiration (AET) using the MOD16 algorithm.

    Algorithm Family: Penman-Monteith (P-M) Resistance Model

    MOD16 is a simplified Penman-Monteith model that uses biome-specific lookup
    tables (BPLUT) to parameterize surface and aerodynamic resistances. It accounts
    for vegetation stress through temperature and VPD constraints, and soil moisture
    limitations on evaporation.

    The model separates canopy transpiration and soil evaporation internally but
    typically outputs only total AET. It is widely used with MODIS satellite data
    at 500m resolution.

    Parameters
    ----------
    **params : dict
        Model parameters. Required:
        - bplut_params: Biome-specific parameter lookup table

    References
    ----------
    Mu, Q., et al. (2011). Improvements to a MODIS global terrestrial
    evapotranspiration algorithm. Remote Sensing of Environment, 115(8), 1781-1800.
    """

    def _validate_inputs(self) -> None:
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
        stress_temp = stress_temp.clip(0.1, 1.0)
        stress_vpd = xr.where(vpd < 0.5, 1.0, (1.0 - (vpd - 0.5) / 3.0).clip(0.1, 1.0))
        g_s = 0.01 + 0.08 * stress_temp * stress_vpd
        r_c = xr.where(g_s > 0, 1.0 / g_s, 1e6)

        soil_moisture = ds.get("soil_moisture", xr.zeros_like(ds["Rn"]) + 0.2)
        soil_moisture_max = ds.get("soil_moisture_max", xr.zeros_like(soil_moisture) + 0.4)
        soil_stress = xr.clip(soil_moisture / soil_moisture_max, 0.05, 1.0)
        r_soil = 500.0 / soil_stress

        r_s = wet_canopy * 50.0 + (1.0 - wet_canopy) * (r_c + r_soil)
        return r_s.clip(min=10.0, max=2000.0)

    def compute_et(self, ds: xr.Dataset) -> xr.Dataset:
        """Compute actual evapotranspiration.

        Parameters
        ----------
        ds : xr.Dataset
            Input meteorological dataset with required variables

        Returns
        -------
        xr.Dataset
            Dataset containing 'AET' variable in mm/day
        """
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
    """Calculate Actual Evapotranspiration (AET) using the PML-V2 algorithm.

    Algorithm Family: Penman-Monteith (P-M) Resistance Model

    PML-V2 (Penman-Monteith-Leuning Version 2) is a two-source model that explicitly
    separates canopy transpiration and soil evaporation. It uses a physiologically-based
    stomatal conductance model coupled with GPP (Gross Primary Production) to represent
    vegetation response to environmental conditions including CO2, VPD, and radiation.

    The model partitions net radiation between canopy and soil, and calculates separate
    latent heat fluxes for each component. This makes it particularly suitable for
    studying vegetation-atmosphere interactions and climate change impacts.

    Parameters
    ----------
    **params : dict, optional
        Model parameters. Optional parameters include:
        - ga: Aerodynamic conductance (m/s), default 0.01
        - g0: Minimum stomatal conductance (m/s), default 0.01
        - k: Stomatal slope parameter, default 0.05
        - D0: Reference VPD (kPa), default 1.5
        - Gamma: CO2 compensation point (ppm), default 40.0
        - lue: Light use efficiency (g C MJ⁻¹), default 1.5
        - soil_factor: Soil evaporation factor, default 0.8

    References
    ----------
    Zhang, Y., et al. (2019). A global moderate resolution dataset of gross primary
    production of vegetation for 2000–2016. Scientific Data, 6(1), 1-13.
    """

    def _validate_inputs(self) -> None:
        # All parameters optional
        pass

    def _compute_gpp(self, ds: xr.Dataset) -> xr.DataArray:
        """Compute gross primary production from absorbed radiation."""
        apar = ds.get("fAPAR", xr.zeros_like(ds["Rn"]) + 0.5) * ds["Rn"].clip(min=0)
        lue = self.params.get("lue", 1.5)
        temp_scalar = xr.where(ds["T_mean"] < 0, 0.0, 1.0)
        return apar * lue * temp_scalar

    def _compute_canopy_conductance(self, ds: xr.Dataset) -> xr.DataArray:
        """Compute canopy conductance using Leuning stomatal model."""
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
        """Compute actual evapotranspiration.

        Parameters
        ----------
        ds : xr.Dataset
            Input meteorological dataset with required variables:
            Rn, G, T_mean (required); RH, VPD, fAPAR, CO2 (optional)

        Returns
        -------
        xr.Dataset
            Dataset containing 'AET' variable in mm/day
        """
        components = self.partition_components(ds)
        aet = components["transpiration"] + components["soil_evaporation"]
        return xr.Dataset({"AET": aet.rename("AET")})

    def partition_components(self, ds: xr.Dataset) -> xr.Dataset:
        """Partition AET into transpiration and soil evaporation components.

        Parameters
        ----------
        ds : xr.Dataset
            Input meteorological dataset

        Returns
        -------
        xr.Dataset
            Dataset with 'transpiration' and 'soil_evaporation' in mm/day
        """
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


# ============================================================================
# Priestley-Taylor (P-T) Stress Models
# ============================================================================


class PTJPL(PriestleyTaylorBase):
    """Calculate Actual Evapotranspiration (AET) using the PT-JPL algorithm.

    Algorithm Family: Priestley-Taylor (P-T) Stress Model

    PT-JPL (Priestley-Taylor Jet Propulsion Laboratory) calculates potential ET using
    the Priestley-Taylor equation (with α=1.26) and then applies multiple constraint
    functions (f-factors) to reduce it to actual ET. These constraints account for:
    - Canopy wetness (f_wet)
    - Soil moisture availability (f_sm)
    - Vegetation cover (f_c)
    - Temperature stress (f_t)
    - Green vegetation fraction (f_m)

    The model explicitly partitions ET into three components: canopy interception
    evaporation, soil evaporation, and transpiration. It is widely used with remote
    sensing data (MODIS, Landsat) due to its reliance on observable vegetation indices.

    Parameters
    ----------
    **params : dict
        Model parameters. Required:
        - T_opt: Optimal temperature for photosynthesis (°C)
        - fAPAR_max: Maximum fAPAR value for normalization

    References
    ----------
    Fisher, J. B., et al. (2008). Global estimates of the land–atmosphere water flux
    based on monthly AVHRR and ISLSCP-II data, validated at 16 FLUXNET sites.
    Remote Sensing of Environment, 112(3), 901-919.
    """

    def _validate_inputs(self) -> None:
        ensure_params(self.params, ["T_opt", "fAPAR_max"])

    @staticmethod
    def _calc_alpha_term(delta: xr.DataArray, gamma: float, rn_component: xr.DataArray) -> xr.DataArray:
        """Calculate Priestley-Taylor alpha term."""
        return 1.26 * (delta / (delta + gamma)) * rn_component

    @staticmethod
    def _calc_f_wet(rh: xr.DataArray) -> xr.DataArray:
        """Calculate wetness constraint factor."""
        return (rh / 100.0) ** 4

    @staticmethod
    def _calc_f_sm(vpd: xr.DataArray, rh_min: xr.DataArray) -> xr.DataArray:
        """Calculate soil moisture constraint factor."""
        beta = 2.0
        return xr.clip(rh_min / (vpd / beta + 1e-6), 0.0, 1.0)

    @staticmethod
    def _calc_f_c(fapar: xr.DataArray, fipar: xr.DataArray) -> xr.DataArray:
        """Calculate vegetation cover constraint factor."""
        return xr.where(fipar > 0, fapar / fipar, 0.0).clip(0.0, 1.0)

    def _calc_f_t(self, tmax: xr.DataArray) -> xr.DataArray:
        """Calculate temperature stress constraint factor."""
        t_opt = self.params["T_opt"]
        return xr.apply_ufunc(np.exp, -((tmax - t_opt) / t_opt) ** 2)

    def _calc_f_m(self, fapar: xr.DataArray) -> xr.DataArray:
        """Calculate plant moisture constraint factor."""
        fapar_max = self.params["fAPAR_max"]
        return xr.clip(fapar / fapar_max, 0.0, 1.0)

    def compute_et(self, ds: xr.Dataset) -> xr.Dataset:
        """Compute actual evapotranspiration.

        Parameters
        ----------
        ds : xr.Dataset
            Input dataset with required variables:
            Rn, G, T_mean, T_max, RH, fAPAR, fIPAR

        Returns
        -------
        xr.Dataset
            Dataset containing 'AET' variable in mm/day
        """
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
        """Partition AET into interception, soil evaporation, and transpiration.

        Parameters
        ----------
        ds : xr.Dataset
            Input meteorological dataset

        Returns
        -------
        xr.Dataset
            Dataset with 'interception', 'soil_evaporation', and
            'transpiration' in mm/day
        """
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
    """Calculate Actual Evapotranspiration (AET) using the GLEAM algorithm.

    Algorithm Family: Priestley-Taylor (P-T) Stress Model

    GLEAM (Global Land Evaporation Amsterdam Model) is a set of algorithms that
    estimates terrestrial evaporation from satellite data. It uses the Priestley-Taylor
    equation to calculate potential ET (with α=1.26), then applies a multiplicative
    stress factor derived from soil moisture observations (typically from microwave
    satellites) and vegetation optical depth (VOD).

    This simplified implementation uses a basic soil moisture stress factor. The
    operational GLEAM model is more complex, incorporating rainfall interception,
    tall canopy stress, bare soil evaporation, and snow sublimation components.

    Parameters
    ----------
    **params : dict
        Model parameters. Required:
        - soil_moisture_max: Maximum soil moisture value for normalization

    References
    ----------
    Martens, B., et al. (2017). GLEAM v3: Satellite-based land evaporation and
    root-zone soil moisture. Geoscientific Model Development, 10(5), 1903-1925.
    """

    def _validate_inputs(self) -> None:
        ensure_params(self.params, ["soil_moisture_max"])

    def _compute_stress_factor(self, ds: xr.Dataset) -> xr.DataArray:
        """Return a simplified soil moisture stress factor.

        Real-world GLEAM uses microwave soil moisture and vegetation optical depth
        to infer component-specific stress. For this library skeleton we scale the
        observed soil moisture by its climatological maximum.
        """
        ensure_variables(ds, {"soil_moisture"})
        sm_max = self.params["soil_moisture_max"]
        return xr.clip(ds["soil_moisture"] / sm_max, 0.0, 1.0)

    def compute_et(self, ds: xr.Dataset) -> xr.Dataset:
        """Compute actual evapotranspiration.

        Parameters
        ----------
        ds : xr.Dataset
            Input dataset with required variables:
            Rn, G, T_mean, soil_moisture

        Returns
        -------
        xr.Dataset
            Dataset containing 'AET' variable in mm/day
        """
        ensure_variables(ds, {"Rn", "G", "T_mean", "soil_moisture"})

        delta = _slope_svp_curve(ds["T_mean"])
        gamma = CONSTANTS["GAMMA"]
        potential_et = 1.26 * (delta / (delta + gamma)) * (ds["Rn"] - ds["G"])
        stress = self._compute_stress_factor(ds)
        aet = potential_et * stress / CONSTANTS["LAMBDA_VAP"] * 86400 / 1e6
        return xr.Dataset({"AET": aet.rename("AET")})


# ============================================================================
# Surface Energy Balance (SEB) Residual Models
# ============================================================================


class SEBAL(EnergyBalanceBase):
    """Calculate Actual Evapotranspiration (AET) using the SEBAL algorithm.

    Algorithm Family: Surface Energy Balance (SEB) Residual Model

    SEBAL (Surface Energy Balance Algorithm for Land) estimates ET as the residual
    of the surface energy balance equation: LE = Rn - G - H. The key innovation is
    a self-calibrating approach that uses "hot" (dry) and "cold" (wet) anchor pixels
    within each satellite image to establish a linear relationship between land surface
    temperature (LST) and sensible heat flux (H).

    This eliminates the need for accurate air temperature data at every pixel. The
    algorithm is particularly suited for clear-sky satellite overpasses (Landsat, MODIS)
    and is widely used in irrigation management.

    Parameters
    ----------
    **params : dict, optional
        Model parameters (all optional with internal defaults)

    References
    ----------
    Bastiaanssen, W. G. M., et al. (1998). A remote sensing surface energy balance
    algorithm for land (SEBAL). 1. Formulation. Journal of Hydrology, 212, 198-212.
    """

    def _validate_inputs(self) -> None:
        pass

    def _compute_sensible_heat(self, ds: xr.Dataset) -> xr.DataArray:
        """Compute sensible heat flux using hot/cold pixel calibration."""
        ensure_variables(ds, {"Rn", "G", "LST", "ra"})

        lst = ds["LST"]
        ra = ds["ra"].clip(min=1.0)

        hot_mask = lst >= lst.quantile(0.95, dim=["lat", "lon"], skipna=True)
        cold_mask = lst <= lst.quantile(0.05, dim=["lat", "lon"], skipna=True)

        rn_hot = ds["Rn"].where(hot_mask).mean(dim="time")
        g_hot = ds["G"].where(hot_mask).mean(dim="time")
        h_hot = rn_hot - g_hot

        h_cold = xr.zeros_like(h_hot)

        dt_hot = (h_hot * ra.where(hot_mask).mean(dim="time")) / (CONSTANTS["RHO_AIR"] * CONSTANTS["CP_AIR"])
        dt_cold = (h_cold * ra.where(cold_mask).mean(dim="time")) / (CONSTANTS["RHO_AIR"] * CONSTANTS["CP_AIR"])

        a = (dt_hot - dt_cold) / (lst.where(hot_mask).mean(dim="time") - lst.where(cold_mask).mean(dim="time") + 1e-6)
        b = dt_hot - a * lst.where(hot_mask).mean(dim="time")

        dt = a * lst + b
        return CONSTANTS["RHO_AIR"] * CONSTANTS["CP_AIR"] * dt / ra

    def compute_et(self, ds: xr.Dataset) -> xr.Dataset:
        """Compute actual evapotranspiration.

        Parameters
        ----------
        ds : xr.Dataset
            Input dataset with required variables:
            Rn, G, LST (land surface temperature), ra (aerodynamic resistance)

        Returns
        -------
        xr.Dataset
            Dataset containing 'AET' variable in mm/day
        """
        ensure_variables(ds, {"Rn", "G", "LST", "ra"})
        h = self._compute_sensible_heat(ds)
        le = ds["Rn"] - ds["G"] - h
        aet = le / CONSTANTS["LAMBDA_VAP"] * 86400 / 1e6
        return xr.Dataset({"AET": aet.rename("AET")})


class SSEBop(EnergyBalanceBase):
    """Calculate Actual Evapotranspiration (AET) using the SSEBop algorithm.

    Algorithm Family: Surface Energy Balance (SEB) Residual Model

    SSEBop (Operational Simplified Surface Energy Balance) is a simplified thermal-based
    model that estimates ET by combining land surface temperature (LST) observations
    with reference ET (ET₀). It calculates an evaporative fraction (ETf) from the
    difference between observed LST and theoretical hot/cold temperature limits:

    ETf = (Th - Ts) / (Th - Tc)
    AET = ETf × ET₀

    Where Th is the "hot" limit (dry conditions) and Tc is the "cold" limit (wet
    conditions). This approach is computationally efficient and operationally robust,
    making it suitable for large-scale monitoring applications.

    Parameters
    ----------
    **params : dict, optional
        Model parameters (all optional with internal defaults)

    References
    ----------
    Senay, G. B., et al. (2013). Operational evapotranspiration mapping using remote
    sensing and weather datasets: A new parameterization for the SSEB approach.
    Journal of the American Water Resources Association, 49(3), 577-591.
    """

    def _validate_inputs(self) -> None:
        return None

    def _compute_cold_limit(self, ds: xr.Dataset) -> xr.DataArray:
        """Compute cold temperature limit (well-watered surface)."""
        air_temp = ds.get("T_air", ds["T_mean"])
        return air_temp - 2.0

    def _compute_hot_limit(self, ds: xr.Dataset, tc: xr.DataArray) -> xr.DataArray:
        """Compute hot temperature limit (dry surface)."""
        rn = ds["Rn"]
        g = ds["G"]
        ra = ds.get("ra", xr.zeros_like(rn) + 50.0)
        delta_t = (rn - g) * ra / (CONSTANTS["RHO_AIR"] * CONSTANTS["CP_AIR"])
        return tc + delta_t

    def _compute_et_fraction(self, ds: xr.Dataset) -> xr.DataArray:
        """Compute evaporative fraction from temperature limits."""
        tc = self._compute_cold_limit(ds)
        th = self._compute_hot_limit(ds, tc)
        ts = ds["LST"]
        etf = (th - ts) / (th - tc + 1e-6)
        return _clip_fraction(etf)

    def compute_et(self, ds: xr.Dataset) -> xr.Dataset:
        """Compute actual evapotranspiration.

        Parameters
        ----------
        ds : xr.Dataset
            Input dataset with required variables:
            Rn, G, LST, T_mean, T_max, T_min, u2, RH

        Returns
        -------
        xr.Dataset
            Dataset containing 'AET' variable in mm/day
        """
        ensure_variables(ds, {"Rn", "G", "LST", "T_mean", "T_max", "T_min", "u2", "RH"})

        # Import here to avoid circular dependency
        from . import pet

        eto = pet.fao56_penman_monteith(ds)
        etf = self._compute_et_fraction(ds)
        aet = etf * eto
        return xr.Dataset({"AET": aet.rename("AET")})
