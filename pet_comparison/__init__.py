"""
PET Formula Comparison Package
A comprehensive comparison of different PET (Potential Evapotranspiration) formulas
"""

__version__ = "0.1.0"

from .formulas import (
    penman_monteith,
    priestley_taylor,
    priestley_taylor_jpl,
    penman_monteith_leuning,
    pm_co2_aware,
    pm_co2_lai_aware,
    bouchet_complementary,
    advection_aridity_model,
    granger_gray_model,
)

from .utils import constants, meteorology

__all__ = [
    "penman_monteith",
    "priestley_taylor",
    "priestley_taylor_jpl",
    "penman_monteith_leuning",
    "pm_co2_aware",
    "pm_co2_lai_aware",
    "bouchet_complementary",
    "advection_aridity_model",
    "granger_gray_model",
    "constants",
    "meteorology",
]
