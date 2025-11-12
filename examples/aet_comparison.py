"""AET Model Comparison Example.

This script demonstrates how to compare different Actual Evapotranspiration (AET) models
using synthetic meteorological data. It includes:
- Generation of synthetic forcing data with all required variables
- Comparison of multiple AET models from different algorithm families
- Time series visualization of model outputs
- Component partitioning for models that support it (e.g., PMLv2)

Author: ET Formula Comparison Framework
Date: 2025-11-12
"""

import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

# Import AET models from the refactored framework
from py_et_lib.models import GLEAM, MOD16, PTJPL, PMLv2, SSEBop

warnings.filterwarnings("ignore", category=FutureWarning)

# Set output directory
OUTPUT_DIR = Path(__file__).parent / "figures"
OUTPUT_DIR.mkdir(exist_ok=True)

# Configure matplotlib for better-looking plots
plt.style.use("seaborn-v0_8-darkgrid")
plt.rcParams["figure.figsize"] = (14, 8)
plt.rcParams["font.size"] = 11
plt.rcParams["axes.labelsize"] = 12
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["legend.fontsize"] = 10


def generate_synthetic_forcing_data(n_days: int = 365) -> xr.Dataset:
    """Generate synthetic meteorological forcing data for AET models.

    This function creates a complete dataset with all variables needed for
    AET calculations, including temperature, radiation, wind speed, VPD,
    soil moisture, LAI, and other required inputs.

    Parameters
    ----------
    n_days : int, default=365
        Number of days to generate

    Returns
    -------
    xr.Dataset
        Dataset containing all forcing variables with time dimension
    """
    print(f"Generating {n_days} days of synthetic forcing data...")

    # Create time coordinate
    dates = pd.date_range(start="2020-01-01", periods=n_days, freq="D")
    day_of_year = np.arange(n_days)

    # Generate seasonal patterns with realistic variability
    # Temperature (°C) - annual cycle with daily noise
    T_mean = 15 + 12 * np.sin(2 * np.pi * day_of_year / 365 - np.pi / 2)
    T_mean += np.random.normal(0, 2, n_days)

    T_max = T_mean + 5 + np.random.normal(0, 1, n_days)
    T_min = T_mean - 5 + np.random.normal(0, 1, n_days)

    # Land Surface Temperature (K) - slightly warmer than air temp
    LST = T_mean + 2.0 + np.random.normal(0, 1, n_days) + 273.15

    # Relative humidity (%) - inverse seasonal pattern
    RH = 65 - 15 * np.sin(2 * np.pi * day_of_year / 365 - np.pi / 2)
    RH += np.random.normal(0, 5, n_days)
    RH = np.clip(RH, 30, 95)

    # Wind speed at 2m (m/s) - with seasonal and daily variability
    u2 = 2.5 + 1.0 * np.sin(2 * np.pi * day_of_year / 365)
    u2 += np.abs(np.random.normal(0, 0.5, n_days))
    u2 = np.maximum(u2, 0.5)

    # Net radiation (W m⁻²) - strong seasonal cycle
    Rn = 150 + 100 * np.sin(2 * np.pi * day_of_year / 365 - np.pi / 2)
    Rn = np.maximum(Rn, 50)

    # Ground heat flux (W m⁻²) - ~10% of net radiation
    G = 0.1 * Rn + np.random.normal(0, 5, n_days)

    # Calculate VPD from T and RH
    es = 0.6108 * np.exp((17.27 * T_mean) / (T_mean + 237.3))  # kPa
    ea = es * RH / 100.0
    VPD = es - ea
    VPD = np.maximum(VPD, 0.1)  # Ensure positive

    # Leaf Area Index (m² m⁻²) - seasonal vegetation growth
    LAI = 3.0 + 1.8 * np.sin(2 * np.pi * day_of_year / 365 - np.pi / 2)
    LAI = np.maximum(LAI, 0.5)

    # Fraction of Absorbed/Intercepted PAR
    fAPAR = 0.5 + 0.3 * np.sin(2 * np.pi * day_of_year / 365 - np.pi / 2)
    fAPAR = np.clip(fAPAR, 0.2, 0.9)

    fIPAR = 0.6 + 0.3 * np.sin(2 * np.pi * day_of_year / 365 - np.pi / 2)
    fIPAR = np.clip(fIPAR, 0.3, 0.95)

    # Soil moisture (0-1) - related to seasonal precipitation
    soil_moisture = 0.4 + 0.2 * np.sin(2 * np.pi * day_of_year / 365)
    soil_moisture += np.random.normal(0, 0.05, n_days)
    soil_moisture = np.clip(soil_moisture, 0.1, 0.8)

    # CO2 concentration (ppm) - constant for baseline
    CO2 = np.ones(n_days) * 400.0

    # Aerodynamic resistance (s/m) - function of wind speed
    ra = 208 / u2  # Simplified calculation

    # Create xarray Dataset
    ds = xr.Dataset(
        {
            "T_mean": (["time"], T_mean),
            "T_max": (["time"], T_max),
            "T_min": (["time"], T_min),
            "T_air": (["time"], T_mean),  # Alias for some models
            "LST": (["time"], LST),
            "RH": (["time"], RH),
            "RH_min": (["time"], RH * 0.7),  # Approximate minimum RH
            "VPD": (["time"], VPD),
            "u2": (["time"], u2),
            "Rn": (["time"], Rn),
            "G": (["time"], G),
            "LAI": (["time"], LAI),
            "fAPAR": (["time"], fAPAR),
            "fIPAR": (["time"], fIPAR),
            "soil_moisture": (["time"], soil_moisture),
            "soil_moisture_max": (["time"], np.ones(n_days) * 0.5),
            "CO2": (["time"], CO2),
            "ra": (["time"], ra),
        },
        coords={"time": dates},
    )

    print(f"Generated dataset with variables: {list(ds.data_vars.keys())}")
    return ds


def run_aet_models(ds: xr.Dataset) -> dict:
    """Run multiple AET models on the forcing dataset.

    Parameters
    ----------
    ds : xr.Dataset
        Input forcing dataset

    Returns
    -------
    dict
        Dictionary mapping model names to their AET output DataArrays
    """
    print("\nRunning AET models...")
    results = {}

    # Penman-Monteith Family
    print("  - MOD16 (P-M resistance model)...")
    mod16 = MOD16(bplut_params={})
    results["MOD16"] = mod16.compute_et(ds)["AET"]

    print("  - PMLv2 (P-M two-source model)...")
    pmlv2 = PMLv2()
    results["PMLv2"] = pmlv2.compute_et(ds)["AET"]

    # Priestley-Taylor Family
    print("  - PTJPL (P-T stress model)...")
    ptjpl = PTJPL(T_opt=25.0, fAPAR_max=0.95)
    results["PTJPL"] = ptjpl.compute_et(ds)["AET"]

    print("  - GLEAM (P-T with soil moisture stress)...")
    gleam = GLEAM(soil_moisture_max=0.5)
    results["GLEAM"] = gleam.compute_et(ds)["AET"]

    # Surface Energy Balance Family
    print("  - SSEBop (thermal-based model)...")
    ssebop = SSEBop()
    try:
        results["SSEBop"] = ssebop.compute_et(ds)["AET"]
    # SSEBop is expected to fail with 1D synthetic data due to lack of spatial dimensions
    # required by SEBAL's hot/cold pixel approach. Catch only expected exceptions.
    except (ValueError, KeyError) as e:
        print(f"    Warning: SSEBop failed ({e}), skipping...")
    print(f"\nSuccessfully ran {len(results)} models.")
    return results


def plot_timeseries_comparison(results: dict, output_dir: Path) -> None:
    """Create time series comparison plot of all AET models.

    Parameters
    ----------
    results : dict
        Dictionary of model results
    output_dir : Path
        Directory to save the figure
    """
    print("\nCreating time series comparison plot...")

    fig, ax = plt.subplots(figsize=(14, 6))

    # Define colors for each algorithm family
    colors = {
        "MOD16": "#e74c3c",  # Red - P-M
        "PMLv2": "#c0392b",  # Dark red - P-M
        "PTJPL": "#3498db",  # Blue - P-T
        "GLEAM": "#2980b9",  # Dark blue - P-T
        "SEBAL": "#2ecc71",  # Green - SEB
        "SSEBop": "#27ae60",  # Dark green - SEB
    }

    line_styles = {
        "MOD16": "-",
        "PMLv2": "--",
        "PTJPL": "-",
        "GLEAM": "--",
        "SEBAL": "-",
        "SSEBop": "--",
    }

    for model_name, aet in results.items():
        # Convert to pandas for easier plotting
        aet_series = aet.to_series()
        ax.plot(
            aet_series.index,
            aet_series.values,
            label=model_name,
            color=colors.get(model_name, "gray"),
            linestyle=line_styles.get(model_name, "-"),
            linewidth=2,
            alpha=0.8,
        )

    ax.set_xlabel("Date", fontsize=12, fontweight="bold")
    ax.set_ylabel("AET (mm/day)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Comparison of Actual Evapotranspiration Models\n"
        "Penman-Monteith (red) | Priestley-Taylor (blue) | Energy Balance (green)",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )

    ax.legend(
        loc="upper left",
        frameon=True,
        fancybox=True,
        shadow=True,
        ncol=3,
    )

    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    output_path = output_dir / "aet_comparison_timeseries.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved: {output_path}")
    plt.close()


def plot_component_partitioning(ds: xr.Dataset, output_dir: Path) -> None:
    """Create stacked area plot showing ET component partitioning for PMLv2.

    Parameters
    ----------
    ds : xr.Dataset
        Input forcing dataset
    output_dir : Path
        Directory to save the figure
    """
    print("\nCreating component partitioning plot for PMLv2...")

    # Run PMLv2 with component partitioning
    pmlv2 = PMLv2()
    components = pmlv2.partition_components(ds)

    # Convert to pandas for plotting
    transp = components["transpiration"].to_series()
    soil_evap = components["soil_evaporation"].to_series()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # Top panel: Stacked area chart
    ax1.fill_between(
        transp.index,
        0,
        transp.values,
        label="Transpiration (T)",
        color="#27ae60",
        alpha=0.7,
    )
    ax1.fill_between(
        soil_evap.index,
        transp.values,
        transp.values + soil_evap.values,
        label="Soil Evaporation (E)",
        color="#e67e22",
        alpha=0.7,
    )

    ax1.set_ylabel("ET Components (mm/day)", fontsize=12, fontweight="bold")
    ax1.set_title(
        "PMLv2 AET Component Partitioning\nStacked Area Chart",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax1.legend(loc="upper left", frameon=True, fancybox=True, shadow=True)
    ax1.grid(True, alpha=0.3)

    # Bottom panel: Line plot with total
    ax2.plot(
        transp.index,
        transp.values,
        label="Transpiration (T)",
        color="#27ae60",
        linewidth=2,
    )
    ax2.plot(
        soil_evap.index,
        soil_evap.values,
        label="Soil Evaporation (E)",
        color="#e67e22",
        linewidth=2,
    )
    ax2.plot(
        transp.index,
        transp.values + soil_evap.values,
        label="Total AET",
        color="#2c3e50",
        linewidth=2.5,
        linestyle="--",
    )

    ax2.set_xlabel("Date", fontsize=12, fontweight="bold")
    ax2.set_ylabel("ET (mm/day)", fontsize=12, fontweight="bold")
    ax2.set_title(
        "Individual Components and Total",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    ax2.legend(loc="upper left", frameon=True, fancybox=True, shadow=True)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    output_path = output_dir / "aet_pmlv2_components.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved: {output_path}")
    plt.close()

    # Print statistics
    print("\nPMLv2 Component Statistics:")
    print(f"  Mean Transpiration: {transp.mean():.2f} mm/day")
    print(f"  Mean Soil Evaporation: {soil_evap.mean():.2f} mm/day")
    print(f"  T/ET Ratio: {transp.mean() / (transp.mean() + soil_evap.mean()):.2%}")


def print_summary_statistics(results: dict) -> None:
    """Print summary statistics for all models.

    Parameters
    ----------
    results : dict
        Dictionary of model results
    """
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)

    print(f"\n{'Model':<15} {'Mean':>10} {'Std':>10} {'Min':>10} {'Max':>10}")
    print("-" * 70)

    for model_name, aet in sorted(results.items()):
        aet_values = aet.values
        print(
            f"{model_name:<15} "
            f"{np.mean(aet_values):>10.2f} "
            f"{np.std(aet_values):>10.2f} "
            f"{np.min(aet_values):>10.2f} "
            f"{np.max(aet_values):>10.2f}"
        )

    print("\nUnits: mm/day")
    print("=" * 70)


def main():
    """Main execution function."""
    print("=" * 70)
    print("AET MODEL COMPARISON FRAMEWORK")
    print("=" * 70)
    print("\nThis example demonstrates the unified AET/PET comparison framework")
    print("with models organized by algorithm family:")
    print("  - Penman-Monteith (P-M) Resistance Models")
    print("  - Priestley-Taylor (P-T) Stress Models")
    print("  - Surface Energy Balance (SEB) Residual Models")
    print()

    # Step 1: Generate synthetic forcing data
    ds = generate_synthetic_forcing_data(n_days=365)

    # Step 2: Run all AET models
    results = run_aet_models(ds)

    # Step 3: Create visualizations
    plot_timeseries_comparison(results, OUTPUT_DIR)
    plot_component_partitioning(ds, OUTPUT_DIR)

    # Step 4: Print summary statistics
    print_summary_statistics(results)

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"\nFigures saved to: {OUTPUT_DIR.absolute()}")
    print("\nGenerated plots:")
    print("  1. aet_comparison_timeseries.png - Time series comparison of all models")
    print("  2. aet_pmlv2_components.png - Component partitioning for PMLv2")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
