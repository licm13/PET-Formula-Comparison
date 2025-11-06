"""
Example: CO2 Sensitivity Analysis

This example demonstrates how to analyze the sensitivity of different
PET formulas to changes in atmospheric CO2 concentration.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pet_comparison.analysis import PETComparison
from pet_comparison.analysis.visualization import plot_co2_response


def generate_base_data():
    """Generate base meteorological data"""
    dates = pd.date_range(start='2020-01-01', periods=365, freq='D')
    
    # Create representative conditions
    data = pd.DataFrame({
        'temperature': 20.0,
        'relative_humidity': 60.0,
        'wind_speed': 2.5,
        'net_radiation': 15.0,
        'lai': 3.0,
        'soil_moisture': 0.5,
        'co2': 380.0,  # Will be varied
    }, index=dates)
    
    return data


def main():
    """Main execution function"""
    
    print("=" * 70)
    print("CO2 Sensitivity Analysis")
    print("=" * 70)
    print()
    
    # CO2 scenarios (ppm)
    co2_scenarios = [280, 350, 380, 450, 550, 700, 900, 1200]
    
    print(f"Testing {len(co2_scenarios)} CO2 scenarios:")
    print(f"  Range: {min(co2_scenarios)} - {max(co2_scenarios)} ppm")
    print(f"  Reference: 380 ppm (pre-industrial)")
    print()
    
    # Store results
    results_by_co2 = {}
    
    # Run analysis for each CO2 scenario
    for co2 in co2_scenarios:
        print(f"Running analysis for CO2 = {co2} ppm...")
        
        # Generate data with specific CO2
        forcing_data = generate_base_data()
        forcing_data['co2'] = co2
        
        # Run comparison
        comparison = PETComparison(forcing_data)
        comparison.run_all()
        
        # Get mean results
        results_df = comparison.get_results_dataframe()
        results_by_co2[co2] = results_df.mean()
    
    # Convert to DataFrame
    sensitivity_df = pd.DataFrame(results_by_co2).T
    
    print("\n" + "=" * 70)
    print("SENSITIVITY RESULTS")
    print("=" * 70)
    print("\nMean PET (mm/day) for each formula at different CO2 levels:")
    print(sensitivity_df)
    
    # Calculate relative changes from reference (380 ppm)
    print("\n" + "-" * 70)
    print("Relative change from 380 ppm reference (%):")
    ref_values = sensitivity_df.loc[380]
    relative_change = ((sensitivity_df - ref_values) / ref_values * 100)
    print(relative_change)
    
    # Analyze CO2-sensitive formulas
    print("\n" + "=" * 70)
    print("CO2 SENSITIVITY ANALYSIS")
    print("=" * 70)
    
    # Calculate sensitivity as change per 100 ppm increase
    co2_range = max(co2_scenarios) - min(co2_scenarios)
    pet_change = sensitivity_df.loc[max(co2_scenarios)] - sensitivity_df.loc[min(co2_scenarios)]
    sensitivity_per_100ppm = pet_change / co2_range * 100
    
    print("\nSensitivity (change in PET per 100 ppm CO2 increase):")
    for formula, sens in sensitivity_per_100ppm.items():
        print(f"  {formula:20s}: {sens:+.3f} mm/day per 100 ppm")
    
    # Identify most and least sensitive formulas
    print("\nMost CO2-sensitive formula:")
    most_sensitive = sensitivity_per_100ppm.abs().idxmax()
    print(f"  {most_sensitive}: {sensitivity_per_100ppm[most_sensitive]:+.3f} mm/day per 100 ppm")
    
    print("\nLeast CO2-sensitive formula:")
    least_sensitive = sensitivity_per_100ppm.abs().idxmin()
    print(f"  {least_sensitive}: {sensitivity_per_100ppm[least_sensitive]:+.3f} mm/day per 100 ppm")
    
    # Create visualizations
    print("\n" + "=" * 70)
    print("GENERATING VISUALIZATIONS")
    print("=" * 70)
    
    # Plot for each formula
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.ravel()
    
    # Select key formulas to plot
    key_formulas = ['PM', 'PM-CO2', 'PM-CO2-LAI', 'PML']
    
    for idx, formula in enumerate(key_formulas):
        if idx < len(axes):
            ax = axes[idx]
            ax.plot(sensitivity_df.index, sensitivity_df[formula], 
                   marker='o', linewidth=2, markersize=8)
            ax.axvline(x=380, color='red', linestyle='--', alpha=0.5, label='Reference')
            ax.set_xlabel('CO2 Concentration (ppm)', fontsize=11)
            ax.set_ylabel('PET (mm/day)', fontsize=11)
            ax.set_title(formula, fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend()
    
    plt.suptitle('CO2 Sensitivity of Different PET Formulas', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('co2_sensitivity.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("\nSaved: co2_sensitivity.png")
    
    # Plot relative changes
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for formula in key_formulas:
        relative = ((sensitivity_df[formula] - sensitivity_df.loc[380, formula]) / 
                   sensitivity_df.loc[380, formula] * 100)
        ax.plot(sensitivity_df.index, relative, marker='o', 
               linewidth=2, markersize=6, label=formula)
    
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax.axvline(x=380, color='red', linestyle='--', alpha=0.5, label='Reference')
    ax.set_xlabel('CO2 Concentration (ppm)', fontsize=12)
    ax.set_ylabel('Relative Change in PET (%)', fontsize=12)
    ax.set_title('Relative Changes in PET with CO2', fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('co2_relative_change.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: co2_relative_change.png")
    
    print("\n" + "=" * 70)
    print("KEY IMPLICATIONS")
    print("=" * 70)
    
    # Calculate doubling scenario (280 -> 560 ppm)
    if 280 in co2_scenarios and 550 in co2_scenarios:
        print("\nCO2 doubling scenario (280 → 550 ppm):")
        for formula in key_formulas:
            pet_280 = sensitivity_df.loc[280, formula]
            pet_550 = sensitivity_df.loc[550, formula]
            change = pet_550 - pet_280
            pct_change = (change / pet_280) * 100
            print(f"  {formula:20s}: {change:+.2f} mm/day ({pct_change:+.1f}%)")
    
    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
