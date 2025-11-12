"""Placeholders for land surface model wrappers."""
from __future__ import annotations

import xarray as xr

from ..core.base_models import EvapotranspirationModel


class ERA5(EvapotranspirationModel):
    """Placeholder ERA5 land surface model wrapper."""

    def _validate_inputs(self) -> None:  # noqa: D401
        return None

    def compute_et(self, ds: xr.Dataset) -> xr.Dataset:
        raise NotImplementedError("ERA5 wrapper is not yet implemented.")


class GLDAS(EvapotranspirationModel):
    """Placeholder GLDAS land surface model wrapper."""

    def _validate_inputs(self) -> None:  # noqa: D401
        return None

    def compute_et(self, ds: xr.Dataset) -> xr.Dataset:
        raise NotImplementedError("GLDAS wrapper is not yet implemented.")

