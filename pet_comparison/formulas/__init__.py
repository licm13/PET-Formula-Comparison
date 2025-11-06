"""
PET Formula implementations
"""

from .penman_monteith import penman_monteith, penman_monteith_general
from .priestley_taylor import priestley_taylor, priestley_taylor_with_advection
from .priestley_taylor_jpl import priestley_taylor_jpl, priestley_taylor_jpl_partition
from .penman_monteith_leuning import penman_monteith_leuning, pml_v2
from .co2_aware import pm_co2_aware, pm_co2_lai_aware, co2_response_factor
from .complementary_relationship import (
    bouchet_complementary,
    advection_aridity_model,
    cr_nonlinear,
    granger_gray_model,
)

__all__ = [
    # Classic Penman-Monteith
    'penman_monteith',
    'penman_monteith_general',
    # Priestley-Taylor
    'priestley_taylor',
    'priestley_taylor_with_advection',
    # PT-JPL
    'priestley_taylor_jpl',
    'priestley_taylor_jpl_partition',
    # PML
    'penman_monteith_leuning',
    'pml_v2',
    # CO2-aware
    'pm_co2_aware',
    'pm_co2_lai_aware',
    'co2_response_factor',
    # Complementary relationship
    'bouchet_complementary',
    'advection_aridity_model',
    'cr_nonlinear',
    'granger_gray_model',
]
