

"""
PET formulas used in the "Three Paradoxes" paper (teaching re-implementation).
基于"三大悖论"论文的 PET 公式（教学演示版）。
Note: Units are important — see each function docstring.
注意：单位非常重要——请查阅函数文档。

References / 参考:
- PM-RC (FAO-56)
- Yang et al. (2019) linear CO2 -> rs relationship (教学复刻)
- Jarvis-type multiplicative stomatal model (Sg, Ta, VPD, CO2)

This module avoids external dependencies beyond numpy.
"""
from __future__ import annotations
import numpy as np
import sys
import os

# Import core physical functions from main library
# 从主库导入核心物理函数，避免重复定义
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
from pet_comparison.utils.constants import (
    saturation_vapor_pressure,
    slope_saturation_vapor_pressure,
)

# --- Physical constants / 物理常数 ---
# Psychrometric constant gamma typically ~ 0.066 kPa/°C (depends on pressure, here fixed for demo)
GAMMA_KPA_PER_C = 0.066  # 教学演示取定值
LAMBDA_MJ_PER_KG = 2.45  # latent heat of vaporization 潜热
SEC_PER_DAY = 86400.0

def saturation_vapor_pressure_kpa(Ta_C: np.ndarray) -> np.ndarray:
    """
    Saturation vapor pressure (kPa) at air temperature Ta (°C).
    饱和水汽压公式 (kPa)，输入空气温度 (°C)。

    Note: Uses unified function from pet_comparison.utils.constants
    """
    return saturation_vapor_pressure(Ta_C)

def slope_svp_kpa_per_C(Ta_C: np.ndarray) -> np.ndarray:
    """
    Slope of saturation vapor pressure curve (kPa/°C).
    饱和水汽压曲线斜率 (kPa/°C)。

    Note: Uses unified function from pet_comparison.utils.constants
    """
    return slope_saturation_vapor_pressure(Ta_C)

def pm_rc_pet_mm_day(
    Ta_C: np.ndarray,
    Rn_star_MJ_m2_day: np.ndarray,
    VPD_kPa: np.ndarray,
    WS2_m_s: np.ndarray,
    gamma_kPa_per_C: float = GAMMA_KPA_PER_C,
) -> np.ndarray:
    """
    FAO-56 PM reference crop PET (mm/day). Eq similar to paper (ETrc).
    FAO-56 Penman–Monteith 参考作物 PET (mm/day)。

    ETrc = [0.408 s Rn* + gamma * 900/(Ta+273) * WS2 * VPD] / [s + gamma * (1 + 0.34 * WS2)]
    Where s = slope of SVP curve (kPa/°C)

    Inputs:
    - Ta_C: air temperature (°C)
    - Rn_star_MJ_m2_day: available energy (net radiation - ground heat flux), MJ/m2/day
    - VPD_kPa: vapor pressure deficit (kPa)
    - WS2_m_s: wind speed at 2 m (m/s)
    - gamma_kPa_per_C: psychrometric constant (kPa/°C)

    Outputs: PET in mm/day
    """
    Ta = np.asarray(Ta_C, dtype=float)
    Rn = np.asarray(Rn_star_MJ_m2_day, dtype=float)
    VPD = np.asarray(VPD_kPa, dtype=float)
    WS2 = np.asarray(WS2_m_s, dtype=float)
    s = slope_svp_kpa_per_C(Ta)

    num = 0.408 * s * Rn + gamma_kPa_per_C * (900.0 / (Ta + 273.0)) * WS2 * VPD
    den = s + gamma_kPa_per_C * (1.0 + 0.34 * WS2)
    return num / np.maximum(den, 1e-6)

def yang_rs_co2_linear(rs_base_300: float, co2_ppm: np.ndarray) -> np.ndarray:
    """
    Yang et al. linear rs relation: rs = rs_300 + 0.05 * ([CO2] - 300)
    Yang 等线性 rs 关系（教学复刻）。
    """
    return rs_base_300 + 0.05 * (np.asarray(co2_ppm, dtype=float) - 300.0)

def pm_rc_pet_yang_mm_day(
    Ta_C: np.ndarray,
    Rn_star_MJ_m2_day: np.ndarray,
    VPD_kPa: np.ndarray,
    WS2_m_s: np.ndarray,
    co2_ppm: np.ndarray,
    gamma_kPa_per_C: float = GAMMA_KPA_PER_C,
) -> np.ndarray:
    """
    PM-RC modified with Yang-style CO2->rs influence. (教学复刻)
    教学复刻：在 PM-RC 分母中把 (1 + 0.34*WS2) 换成 (1 + WS2*(0.34 + 2.4e-4*(CO2-300))).

    ETrc-Yang = [0.408 s Rn* + gamma * 900/(Ta+273) * WS2 * VPD] / [s + gamma * {1 + WS2*(0.34 + 2.4e-4*(CO2-300))}]
    """
    Ta = np.asarray(Ta_C, dtype=float)
    Rn = np.asarray(Rn_star_MJ_m2_day, dtype=float)
    VPD = np.asarray(VPD_kPa, dtype=float)
    WS2 = np.asarray(WS2_m_s, dtype=float)
    CO2 = np.asarray(co2_ppm, dtype=float)
    s = slope_svp_kpa_per_C(Ta)

    num = 0.408 * s * Rn + gamma_kPa_per_C * (900.0 / (Ta + 273.0)) * WS2 * VPD
    adj = 1.0 + WS2 * (0.34 + 2.4e-4 * (CO2 - 300.0))
    den = s + gamma_kPa_per_C * np.maximum(adj, 1e-6)
    return num / np.maximum(den, 1e-6)

# ---- Jarvis-type stomatal response weights / Jarvis 型权重 ----
def jarvis_f_Sg(Sg_W_m2: np.ndarray, rlmin: float, rlmax: float, Sgl: float, LAI: float) -> np.ndarray:
    """
    f(Sg) = rlmin/rlmax + 0.55 * (2*Sg / (Sgl*LAI)) / (1 + 0.55 * (2*Sg / (Sgl*LAI)))
    Bound to [rlmin/rlmax, 1].
    """
    Sg = np.asarray(Sg_W_m2, dtype=float)
    term = 0.55 * (2.0 * Sg / np.maximum(Sgl * LAI, 1e-6))
    f = (rlmin/rlmax) + term / (1.0 + term)
    return np.clip(f, rlmin/rlmax, 1.0)

def jarvis_f_Ta(Ta_C: np.ndarray) -> np.ndarray:
    """
    f(Ta) = 1 - 0.0016 * (298 - 273.15 - Ta)^2
    """
    Ta = np.asarray(Ta_C, dtype=float)
    f = 1.0 - 0.0016 * (24.85 - Ta)**2  # (298-273.15)=24.85
    return np.clip(f, 0.0, 1.1)

def jarvis_f_VPD(VPD_kPa: np.ndarray) -> np.ndarray:
    """
    f(VPD) = 1 - 0.025 * VPD
    """
    VPD = np.asarray(VPD_kPa, dtype=float)
    f = 1.0 - 0.025 * VPD
    return np.clip(f, 0.0, 1.1)

def jarvis_f_CO2(CO2_ppm: np.ndarray, x: float = 0.9) -> np.ndarray:
    """
    Jarvis (1976) style piecewise CO2 weighting (teaching param).
    """
    CO2 = np.asarray(CO2_ppm, dtype=float)
    f = np.ones_like(CO2, dtype=float)
    # piecewise
    mask1 = CO2 <= 100.0
    mask2 = (CO2 > 100.0) & (CO2 < 1000.0)
    mask3 = CO2 >= 1000.0
    f[mask1] = 1.0
    f[mask2] = 1.0 - (1.0 - x) / (900.0) * (CO2[mask2] - 100.0)
    f[mask3] = x
    return np.clip(f, 0.1, 1.0)

def pm_rc_pet_jarvis_mm_day(
    Ta_C: np.ndarray,
    Rn_star_MJ_m2_day: np.ndarray,
    VPD_kPa: np.ndarray,
    WS2_m_s: np.ndarray,
    Sg_W_m2: np.ndarray,
    CO2_ppm: np.ndarray,
    crop_height_m: float = 0.12,  # reference crop
    rlmin_s_per_m: float = 100.0,
    rlmax_s_per_m: float = 5000.0,
    Sgl_W_m2: float = 100.0,
    gamma_kPa_per_C: float = GAMMA_KPA_PER_C,
) -> np.ndarray:
    """
    PM-RC + Jarvis-type multi-factor stomatal response (teaching re-implementation).
    在 PM-RC 分母中把 (1 + 0.34*WS2) 替换为 (1 + 0.116*WS2 * f^-1(Sg)*f^-1(Ta)*f^-1(VPD)*f^-1(CO2)).

    LAI for reference crop: 24 * crop_height (paper note).
    """
    Ta = np.asarray(Ta_C, dtype=float)
    Rn = np.asarray(Rn_star_MJ_m2_day, dtype=float)
    VPD = np.asarray(VPD_kPa, dtype=float)
    WS2 = np.asarray(WS2_m_s, dtype=float)
    Sg = np.asarray(Sg_W_m2, dtype=float)
    CO2 = np.asarray(CO2_ppm, dtype=float)
    s = slope_svp_kpa_per_C(Ta)

    LAI = 24.0 * crop_height_m  # per paper guidance for Jarvis usage
    fSg = jarvis_f_Sg(Sg, rlmin_s_per_m, rlmax_s_per_m, Sgl_W_m2, LAI)
    fTa = jarvis_f_Ta(Ta)
    fV  = jarvis_f_VPD(VPD)
    fC  = jarvis_f_CO2(CO2)

    # multiplicative factor inverse in denominator as described
    inv_factor = 1.0 / np.maximum(fSg * fTa * fV * fC, 1e-6)

    num = 0.408 * s * Rn + gamma_kPa_per_C * (900.0 / (Ta + 273.0)) * WS2 * VPD
    adj = 1.0 + 0.116 * WS2 * inv_factor
    den = s + gamma_kPa_per_C * np.maximum(adj, 1e-6)
    return num / np.maximum(den, 1e-6)
