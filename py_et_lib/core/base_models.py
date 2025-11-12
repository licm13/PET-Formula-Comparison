"""Abstract base classes for evapotranspiration model families."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

import xarray as xr


class EvapotranspirationModel(ABC):
    """Base class for all ET models in the library."""

    def __init__(self, **params: Any) -> None:
        self.params: Dict[str, Any] = params
        self._validate_inputs()

    @abstractmethod
    def _validate_inputs(self) -> None:
        """Ensure all required parameters are provided when the model is initialised."""

    @abstractmethod
    def compute_et(self, ds: xr.Dataset) -> xr.Dataset:
        """Return actual ET in millimetres per day for each grid cell."""

    def partition_components(self, ds: xr.Dataset) -> xr.Dataset:
        """Optional component breakdown of ET into transpiration and evaporation terms."""

        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement component partitioning."
        )


class PenmanMonteithBase(EvapotranspirationModel):
    """Base class for Penman-Monteith style models."""


class PriestleyTaylorBase(EvapotranspirationModel):
    """Base class for Priestley-Taylor style models."""


class EnergyBalanceBase(EvapotranspirationModel):
    """Base class for surface energy balance models."""

