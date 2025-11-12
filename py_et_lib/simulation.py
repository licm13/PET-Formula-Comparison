"""Example script demonstrating model execution within :mod:`py_et_lib`."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

from .models import GLEAM, MOD16, PMLv2, PTJPL, SSEBop
from .models.pet import fao56_penman_monteith, hargreaves


def create_simulation_data(seed: int = 42) -> xr.Dataset:
    """Create a pseudo realistic forcing dataset for 10x10 pixels and 365 days."""

    rng = np.random.default_rng(seed)
    days = pd.date_range("2023-01-01", periods=365, freq="D")
    lats = np.linspace(40.0, 40.9, 10)
    lons = np.linspace(-105.9, -105.0, 10)

    time = xr.DataArray(days, dims="time", name="time")
    lat = xr.DataArray(lats, dims="lat", name="lat")
    lon = xr.DataArray(lons, dims="lon", name="lon")

    seasonal = np.sin(np.linspace(0, 2 * np.pi, len(days)))

    shape = (len(days), len(lats), len(lons))

    t_mean = 15 + 10 * seasonal[:, None, None] + rng.normal(0, 2, size=shape)
    t_max = t_mean + 5 + rng.normal(0, 1, size=shape)
    t_min = t_mean - 5 + rng.normal(0, 1, size=shape)
    rh = np.clip(60 - 15 * seasonal[:, None, None] + rng.normal(0, 5, size=shape), 20, 95)
    vpd = np.clip(1.5 + 0.5 * seasonal[:, None, None] + rng.normal(0, 0.3, size=shape), 0.1, 4.0)
    rn = np.clip(180 + 80 * seasonal[:, None, None] + rng.normal(0, 15, size=shape), 0, 400)
    g = 20 + rng.normal(0, 2, size=shape)
    u2 = np.clip(2.0 + rng.normal(0, 0.5, size=shape), 0.5, 6.0)
    lai = np.clip(2 + 1.5 * seasonal[:, None, None] + rng.normal(0, 0.3, size=shape), 0.2, 6.0)
    fapar = np.clip(0.5 + 0.3 * seasonal[:, None, None] + rng.normal(0, 0.05, size=shape), 0.1, 0.9)
    fipar = np.clip(fapar + rng.normal(0.02, 0.02, size=shape), 0.2, 0.95)
    lst = t_mean + 3 + rng.normal(0, 1, size=shape)
    soil_moisture = np.clip(0.25 + 0.05 * seasonal[:, None, None] + rng.normal(0, 0.02, size=shape), 0.05, 0.45)
    ra = np.clip(70 + 5 * rng.normal(size=shape), 30, 150)

    ds = xr.Dataset(
        {
            "T_mean": (("time", "lat", "lon"), t_mean),
            "T_max": (("time", "lat", "lon"), t_max),
            "T_min": (("time", "lat", "lon"), t_min),
            "RH": (("time", "lat", "lon"), rh),
            "VPD": (("time", "lat", "lon"), vpd),
            "Rn": (("time", "lat", "lon"), rn),
            "G": (("time", "lat", "lon"), g),
            "u2": (("time", "lat", "lon"), u2),
            "LAI": (("time", "lat", "lon"), lai),
            "fAPAR": (("time", "lat", "lon"), fapar),
            "fIPAR": (("time", "lat", "lon"), fipar),
            "LST": (("time", "lat", "lon"), lst),
            "soil_moisture": (("time", "lat", "lon"), soil_moisture),
            "ra": (("time", "lat", "lon"), ra),
            "day_of_year": (("time",), days.dayofyear),
        },
        coords={"time": time, "lat": lat, "lon": lon},
    )

    ds["soil_moisture_max"] = (("lat", "lon"), np.full((len(lats), len(lons)), 0.5))
    ds["latitude"] = (("lat", "lon"), np.broadcast_to(lat.values[:, None], (len(lats), len(lons))))
    ds["longitude"] = (("lat", "lon"), np.broadcast_to(lon.values[None, :], (len(lats), len(lons))))
    ds["CO2"] = (("time", "lat", "lon"), np.full(shape, 410.0))
    ds["RH_min"] = ds["RH"] * 0.7

    return ds


def run_comparison() -> xr.Dataset:
    """Run all ET models on the synthetic dataset and plot the results."""

    print("1. Creating synthetic dataset...")
    sim_data = create_simulation_data()

    print("2. Initialising models...")
    mod16 = MOD16(bplut_params={"g_lbl": 10.0})
    pmlv2 = PMLv2()
    ptjpl = PTJPL(T_opt=25.0, fAPAR_max=0.9)
    gleam = GLEAM(soil_moisture_max=0.5)
    ssebop = SSEBop()

    models = {
        "MOD16": mod16,
        "PMLv2": pmlv2,
        "PTJPL": ptjpl,
        "GLEAM": gleam,
        "SSEBop": ssebop,
    }

    print("3. Computing reference ET...")
    results: dict[str, xr.DataArray] = {}
    results["FAO56_ETo"] = fao56_penman_monteith(sim_data)
    results["Hargreaves_ETo"] = hargreaves(sim_data)

    print("4. Computing actual ET models...")
    for name, model in models.items():
        print(f"   - Running {name}")
        try:
            results[name] = model.compute_et(sim_data)["AET"]
        except Exception as exc:  # pragma: no cover - demonstration logging
            print(f"     ! {name} failed: {exc}")

    print("5. Consolidating results...")
    combined = xr.Dataset({key: value for key, value in results.items()})

    print("6. Plotting comparison (first grid cell)...")
    plt.figure(figsize=(14, 8))
    for var in combined.data_vars:
        combined[var].isel(lat=0, lon=0).plot(label=var)
    plt.title("Evapotranspiration model comparison")
    plt.ylabel("mm/day")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("et_model_comparison.png")
    print("   Plot saved to et_model_comparison.png")

    return combined


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    run_comparison()
