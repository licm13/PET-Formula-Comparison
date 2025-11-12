"""Physical constants used across evapotranspiration models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class PhysicalConstants:
    """Collection of physical constants required by ET formulations."""

    GAMMA: float = 0.066  # psychrometric constant [kPa / degC]
    LAMBDA_VAP: float = 2.45  # latent heat of vaporisation [MJ / kg]
    RHO_AIR: float = 1.225  # mean air density at sea level [kg / m^3]
    CP_AIR: float = 1004.0  # specific heat of air at constant pressure [J / kg / K]
    STEFAN_BOLTZMANN: float = 5.670374419e-8  # Stefan-Boltzmann constant [W / m^2 / K^4]
    EPSILON: float = 0.622  # ratio molecular weight water vapour/dry air [-]
    G_SC: float = 0.0820  # solar constant [MJ / m^2 / min]


CONSTANTS: Mapping[str, float] = PhysicalConstants().__dict__
"""Mapping-style access to :class:`PhysicalConstants` values."""

