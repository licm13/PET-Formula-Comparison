
"""
EP estimation algorithms (monthly scale) / 潜在蒸散发算法（按月）

Notes:
- Units are documented in each function. This module follows the equations cited by the paper.
- For simplicity, inputs are NumPy arrays with matching shapes (t, y, x) or broadcastable.
"""
from __future__ import annotations
import numpy as np
import sys
import os

# Import core physical functions from main library
# 从主库导入核心物理函数，避免重复定义
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from pet_comparison.utils.constants import (
    saturation_vapor_pressure,
    slope_saturation_vapor_pressure,
    get_psychrometric_constant,
)

LV = 2.45  # latent heat of vaporization [MJ kg-1]
CP = 1.013e-3  # specific heat of air [MJ kg-1 K-1]
EPS = 0.622  # ratio of molecular weights Mw/Ma
RHO_W = 1000.0  # water density kg m-3
SEC_PER_DAY = 86400.0

def _svp(t):
    """
    Saturation vapor pressure (kPa) for temperature in °C (Tetens).
    Note: Uses unified function from pet_comparison.utils.constants
    """
    return saturation_vapor_pressure(t)

def _slope_svp(t):
    """
    Slope of saturation vapor pressure curve Δ (kPa °C-1).
    Note: Uses unified function from pet_comparison.utils.constants
    """
    return slope_saturation_vapor_pressure(t)

def _gamma(ps):
    """
    Psychrometric constant γ (kPa °C-1), ps in kPa (near-sfc).
    Note: Uses unified function from pet_comparison.utils.constants
    """
    # The central `get_psychrometric_constant` function requires a temperature
    # argument, but its current implementation ignores it. A nominal value is
    # used here to satisfy the function signature.
    T_NOMINAL_FOR_GAMMA = 20.0
    return get_psychrometric_constant(ps, T_NOMINAL_FOR_GAMMA)

def pm_rc(tas, rh, ps, u2, Rn, G):
    """
    FAO-56 Penman–Monteith reference crop EP (mm/day-equivalent).
    Parameters follow FAO-56 notation.
    Inputs:
      tas: 2m air temperature (°C)
      rh : relative humidity (%) [0,100]
      ps : air pressure (kPa)
      u2 : wind speed at 2m (m/s)
      Rn : net radiation (MJ m-2 d-1)
      G  : soil heat flux (MJ m-2 d-1), often ~0 monthly
    """
    tas = np.asarray(tas)
    rh = np.asarray(rh)
    ps = np.asarray(ps)
    u2 = np.asarray(u2)
    Rn = np.asarray(Rn)
    G = np.asarray(G)

    es = _svp(tas)
    ea = es * (np.clip(rh, 0, 100) / 100.0)
    delta = _slope_svp(tas)
    gamma = _gamma(ps)

    num = delta * (Rn - G) + (900.0 / (tas + 273.0)) * u2 * (es - ea)
    den = delta + gamma * (1.0 + 0.34 * u2)
    # Convert MJ m-2 d-1 to mm/day using LV and rho_water.
    # 1 mm/day of water evap requires LV * RHO_W * (1e-3 m) per m2 per day = 2.45 MJ m-2 day-1 approximately
    # So EP(mm/day) ≈ (num/den) / LV
    return (num / den) / LV

def pm_rc_co2(tas, rh, ps, u2, Rn, G, co2):
    """
    PM-RC-CO2: FAO-56 with stomatal response to elevated CO2 (Yang et al. 2019).
    Here we use the simple linear scaling of the aerodynamic term per the paper's equation.
    co2: atmospheric CO2 concentration (ppm)
    """
    tas = np.asarray(tas)
    rh = np.asarray(rh)
    ps = np.asarray(ps)
    u2 = np.asarray(u2)
    Rn = np.asarray(Rn)
    G = np.asarray(G)
    co2 = np.asarray(co2)

    es = _svp(tas)
    ea = es * (np.clip(rh, 0, 100) / 100.0)
    delta = _slope_svp(tas)
    gamma = _gamma(ps)

    # Linear plant response factor in aerodynamic term (following the paper's eq. (2) form)
    co2_fac = (1.0 - (0.34 * u2) * (2.4e-4 * (co2 - 300.0)))  # heuristic scaling in mm/day formulation
    num = delta * (Rn - G) + (900.0 / (tas + 273.0)) * u2 * (es - ea) * co2_fac
    den = delta + gamma * (1.0 + 0.34 * u2)
    return (num / den) / LV

def penman_ow(tas, rh, ps, u2, Rn, G):
    """
    Penman equation for open water (Penman-OW) (mm/day).
    """
    tas = np.asarray(tas)
    rh = np.asarray(rh); ps = np.asarray(ps)
    u2 = np.asarray(u2); Rn = np.asarray(Rn); G = np.asarray(G)
    es = _svp(tas); ea = es * (np.clip(rh,0,100)/100.0)
    delta = _slope_svp(tas); gamma = _gamma(ps)

    # Following paper's eq.(3): EP = [Δ/(Δ+γ)]*(Rn-G)/λ + [γ/(Δ+γ)]*6.43*(1+0.536u2)*(es-ea)
    rad_term = (delta/(delta+gamma)) * (Rn - G) / LV
    aero_term = (gamma/(delta+gamma)) * 6.43 * (1.0 + 0.536*u2) * (es - ea) / LV
    return rad_term + aero_term

def priestley_taylor(tas, ps, Rn, G, alpha=1.26):
    """
    Priestley–Taylor (mm/day). No explicit aerodynamic term.
    """
    tas = np.asarray(tas); ps = np.asarray(ps)
    Rn = np.asarray(Rn); G = np.asarray(G)
    delta = _slope_svp(tas); gamma = _gamma(ps)
    return alpha * (delta/(delta+gamma)) * (Rn - G) / LV

def yang_roderick(tas, ps, Rn, G, beta=0.24):
    """
    Yang & Roderick (2019)-type bulk formulation (mm/day).
    """
    tas = np.asarray(tas); ps = np.asarray(ps)
    Rn = np.asarray(Rn); G = np.asarray(G)
    delta = _slope_svp(tas); gamma = _gamma(ps)
    return ((delta)/(delta + beta*gamma)) * (Rn - G) / LV

def oudin(tas, Re):
    """
    Oudin temperature-based EP (mm/day).
    tas: air temperature (°C), Re: extraterrestrial radiation (MJ m-2 d-1)
    """
    tas = np.asarray(tas); Re = np.asarray(Re)
    EP = np.where(tas > 5.0, (Re * (tas + 5.0)) / (100.0 * LV * (RHO_W/1000.0)), 0.0)
    return EP
