"""Utility helpers for validating evapotranspiration model inputs."""
from __future__ import annotations

from typing import Iterable

import xarray as xr


def ensure_variables(ds: xr.Dataset, required: Iterable[str]) -> None:
    """Ensure that *required* variables exist in *ds*.

    Parameters
    ----------
    ds:
        Dataset to validate.
    required:
        Names that must be present in :pyattr:`ds.data_vars`.
    """

    missing = [name for name in required if name not in ds]
    if missing:
        raise ValueError(f"Missing required dataset variables: {', '.join(missing)}")


def ensure_params(params: dict, required: Iterable[str]) -> None:
    """Ensure required model parameter keys are present."""

    missing = [name for name in required if name not in params]
    if missing:
        raise ValueError(f"Missing required parameters: {', '.join(missing)}")

