\
# -*- coding: utf-8 -*-
"""
Penman–Monteith family and helpers (bilingual).

主要包含：
- 心理常数 γ、饱和水汽压斜率 s、空气密度 ρ_a、比热 C_p、潜热 λ 等计算
- Penman–Monteith 族模型：PM_OW（式4）、PM_RC（式5）、PM_CO2（式14）
- 通用 PM 计算框架（教学用）

All formulas follow Yang et al. (2018) Methods, FAO-56, and Shuttleworth (1993).
"""

from __future__ import annotations
import numpy as np
import sys
import os

# Import core physical functions from main library
# 从主库导入核心物理函数，避免重复定义
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
from pet_comparison.utils.constants import (
    saturation_vapor_pressure as _svp_kpa,
    slope_saturation_vapor_pressure as _slope_svp_kpa,
    get_psychrometric_constant as _gamma_kpa,
    get_latent_heat as _latent_heat_mj
)

# --- Physical constants (常数)
CP = 1004.0          # J kg^-1 K^-1, specific heat of air at constant pressure  空气定压比热
KAPPA = 0.41         # von Karman constant
EPS = 0.622          # epsilon for moist air
P0 = 101325.0        # Pa
RHO_W = 1000.0       # kg m^-3, water density

def latent_heat(T):
    """
    Latent heat of vaporization λ (J kg^-1), function of air temperature T (°C).
    潜热 λ，随气温 T (°C) 的函数。FAO 常用线性近似。

    Note: Uses unified function from pet_comparison.utils.constants
    """
    return _latent_heat_mj(T) * 1e6  # Convert MJ/kg to J/kg

def saturation_vapor_pressure(T):
    """
    Saturation vapor pressure es(T) in Pa (Tetens-like).
    饱和水汽压 es，单位 Pa。

    Note: Uses unified function from pet_comparison.utils.constants
    """
    # Main library returns kPa, convert to Pa
    return _svp_kpa(T) * 1000.0

def slope_svp(T):
    """
    s = d(es)/dT in Pa K^-1, saturation vapor pressure slope wrt T.
    饱和水汽压曲线斜率 s，单位 Pa/K。

    Note: Uses unified function from pet_comparison.utils.constants
    """
    # Main library returns kPa/°C, convert to Pa/K
    return _slope_svp_kpa(T) * 1000.0

def psychrometric_constant(P=P0, lambda_Jkg=2.45e6):
    """
    Psychrometric constant γ in Pa K^-1.
    心理常数 γ（Pa/K）。FAO56 常用：γ = Cp * P / (ε λ)

    Note: Uses unified function from pet_comparison.utils.constants
    """
    # Convert P from Pa to kPa for main library function
    P_kpa = P / 1000.0
    # A nominal temperature is passed to satisfy the function signature, though it is currently unused.
    T_nominal = 20.0
    # Main library returns kPa/°C, convert to Pa/K
    return _gamma_kpa(P_kpa, T_nominal) * 1000.0

def air_density(P=P0, T=20.0, RH=0.5):
    """
    Approximate moist air density ρ_a (kg m^-3).
    简化湿空气密度。教学足够。
    """
    # Ideal gas: rho = P / (R_specific * T_kelvin)
    # Use dry air approx
    R_specific = 287.058
    T_k = T + 273.15
    return P / (R_specific * T_k)

def aerodynamic_resistance(u2, z0m=0.12, z=2.0, d=0.0):
    """
    Very simplified aerodynamic resistance r_a (s m^-1).
    极简气动阻力，仅用于教学演示；真实应用请用稳定度修正。
    """
    u = np.maximum(u2, 0.1)
    return 208.0 / u  # rough order typical at 2 m height

def penman_monteith(Rn_star, T, D, ra, rs, P=P0):
    """
    General PM evapotranspiration E (mm day^-1) under non-water-limited assumptions.
    通用 PM 计算（单位：mm/day，非水分限制）。

    Eq. (3) in Methods (Yang et al.), rearranged to mm/day.
    """
    lam = latent_heat(T)
    s = slope_svp(T)
    gamma = psychrometric_constant(P=P, lambda_Jkg=lam)
    rho_a = air_density(P=P, T=T)
    # Energy + aerodynamic components (per PM). Units careful:
    # Convert W/m2 to mm/day: 1 mm/day ≈ 1e-3 m * rho_w * L / day -> but we rely on FAO-style scaling below.
    # We'll follow FAO56 pattern to produce mm/day with empirical constants.
    # For teaching, we use:
    # E = [ s*Rn* + rho_a*Cp*D/ra ] / [ lam*(s + gamma*(1 + rs/ra)) ]
    num = s * Rn_star + rho_a * CP * D / ra
    den = lam * (s + gamma * (1.0 + rs / ra))
    E_kg_m2_s = num / den  # kg m^-2 s^-1
    # Convert to mm/day: 1 kg m^-2 s^-1 == 1 mm s^-1; multiply by 86400
    E_mm_day = E_kg_m2_s * 86400.0
    return E_mm_day

# --- Standardized variants

def PM_OW(Rn_star, T, D, u2, P=P0):
    """
    Open-water Penman (Eq. 4). PM over water: rs=0, specified "0.00137 m" roughness in original text.
    参考：式(4)，简化实现。输入：Rn* (W/m2), T (°C), D (Pa), u2 (m/s)
    输出：EP (mm/day)
    """
    lam = latent_heat(T)
    s = slope_svp(T)
    gamma = psychrometric_constant(P=P, lambda_Jkg=lam)
    # FAO-like: we mimic form: EP = (s*Rn* + gamma*(6.43*(1 + 0.536u))*D*something) / (s + gamma)
    # But D in Pa; classic PM uses D in kPa. We'll convert D to kPa:
    D_kPa = D / 1000.0
    # Convert Rn* W/m2 to MJ m^-2 day^-1: 1 W/m2 = 0.0864 MJ m^-2 day^-1
    Rn_MJ = Rn_star * 0.0864
    # gamma in kPa/°C: current gamma is Pa/K; convert to kPa/K
    gamma_kPa = gamma / 1000.0
    # s in kPa/°C
    s_kPa = s / 1000.0

    EP = (s_kPa * Rn_MJ + gamma_kPa * (6.43 * (1 + 0.536 * u2)) * D_kPa) / (s_kPa + gamma_kPa)
    return EP  # mm/day, by FAO scaling

def PM_RC(Rn_star, T, D, u2, P=P0):
    """
    FAO-56 reference crop (Eq. 5). Uses rs=70 s m^-1 implicitly.
    参考作物 Penman-Monteith（式5的标准化形式，教学近似）。
    Inputs: Rn* [W/m2], T [°C], D [Pa], u2 [m/s]
    Output: EP [mm/day]
    """
    # Convert to FAO56 units
    lam = latent_heat(T)
    s = slope_svp(T)
    gamma = psychrometric_constant(P=P, lambda_Jkg=lam)
    Rn_MJ = Rn_star * 0.0864
    gamma_kPa = gamma / 1000.0
    s_kPa = s / 1000.0
    D_kPa = D / 1000.0

    # FAO-56 pm: ET0 = 0.408*s*Rn + gamma*(900/(T+273))*u2*D / (s + gamma*(1+0.34u2))
    # Here we keep the classic constants for demonstration:
    EP = (0.408 * s_kPa * Rn_MJ + gamma_kPa * (900.0 / (T + 273.0)) * u2 * D_kPa) / (s_kPa + gamma_kPa * (1.0 + 0.34 * u2))
    return EP

def PM_CO2(Rn_star, T, D, u2, co2_ppm, P=P0):
    """
    PM-RC modified to include explicit [CO2] effect (Eq. 14).
    考虑大气 CO2 的参考作物 Penman–Monteith（式14）。

    EP = [0.408*s*Rn* + gamma*(900/(T+273))*u2*D] / [ s + gamma * {1 + 0.34u2 + 2.4e-4*(CO2-300)} ]

    Note: We encode the CO2 term in the denominator as in Methods Eq. (14).
    """
    lam = latent_heat(T)
    s = slope_svp(T)
    gamma = psychrometric_constant(P=P, lambda_Jkg=lam)
    Rn_MJ = Rn_star * 0.0864
    gamma_kPa = gamma / 1000.0
    s_kPa = s / 1000.0
    D_kPa = D / 1000.0
    co2_term = 2.4e-4 * (co2_ppm - 300.0)  # 2.4×10^-4 ([CO2]-300)

    denom = s_kPa + gamma_kPa * (1.0 + 0.34 * u2 + co2_term)
    EP = (0.408 * s_kPa * Rn_MJ + gamma_kPa * (900.0 / (T + 273.0)) * u2 * D_kPa) / denom
    return EP
