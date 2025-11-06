"""
Example: Basic PET Formula Comparison

This example demonstrates how to compare different PET formulas
using synthetic meteorological data.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from pet_comparison.analysis import PETComparison
from pet_comparison.analysis.visualization import (
    plot_timeseries,
    plot_box_comparison,
    plot_correlation_matrix,
    plot_differences_heatmap,
)


def generate_synthetic_data(n_days=365):
    """
    Generate synthetic meteorological data for testing
    
    Parameters:
    -----------
    n_days : int
        Number of days to generate
    
    Returns:
    --------
    pd.DataFrame : Synthetic forcing data
    """
    # Create date range
    dates = pd.date_range(start='2020-01-01', periods=n_days, freq='D')
    
    # Generate synthetic data with seasonal patterns
    day_of_year = np.arange(n_days)
    
    # Temperature (°C) - sinusoidal pattern with annual cycle
    temperature = 15 + 10 * np.sin(2 * np.pi * day_of_year / 365 - np.pi/2)
    
    # Add some random noise
    temperature += np.random.normal(0, 2, n_days)
    
    # Relative humidity (%) - inverse of temperature pattern
    relative_humidity = 70 - 20 * np.sin(2 * np.pi * day_of_year / 365 - np.pi/2)
    relative_humidity += np.random.normal(0, 5, n_days)
    relative_humidity = np.clip(relative_humidity, 30, 95)
    
    # Wind speed (m/s) - with some variability
    wind_speed = 2.5 + 1.0 * np.sin(2 * np.pi * day_of_year / 365)
    wind_speed += np.random.normal(0, 0.5, n_days)
    wind_speed = np.maximum(wind_speed, 0.5)
    
    # Net radiation (MJ m-2 day-1) - seasonal pattern
    net_radiation = 12 + 8 * np.sin(2 * np.pi * day_of_year / 365 - np.pi/2)
    net_radiation = np.maximum(net_radiation, 2)
    
    # LAI (Leaf Area Index) - seasonal vegetation growth
    lai = 3.0 + 1.5 * np.sin(2 * np.pi * day_of_year / 365 - np.pi/2)
    lai = np.maximum(lai, 1.0)
    
    # Soil moisture (0-1) - related to seasonal patterns
    soil_moisture = 0.5 + 0.2 * np.sin(2 * np.pi * day_of_year / 365)
    soil_moisture = np.clip(soil_moisture, 0.3, 0.8)
    
    # CO2 concentration (ppm) - constant for base case
    co2 = np.ones(n_days) * 380
    
    # Create DataFrame
    data = pd.DataFrame({
        'temperature': temperature,
        'relative_humidity': relative_humidity,
        'wind_speed': wind_speed,
        'net_radiation': net_radiation,
        'lai': lai,
        'soil_moisture': soil_moisture,
        'co2': co2,
    }, index=dates)
    
    return data


def main():
    """Main execution function"""
    
    print("=" * 70)
    print("PET Formula Comparison - Basic Example")
    print("=" * 70)
    print()
    
    # Generate synthetic forcing data
    print("Generating synthetic meteorological data...")
    forcing_data = generate_synthetic_data(n_days=365)
    
    print(f"Generated {len(forcing_data)} days of data")
    print("\nData summary:")
    print(forcing_data.describe())
    print()
    
    # Initialize comparison framework
    print("Initializing PET comparison framework...")
    comparison = PETComparison(forcing_data)
    
    # Run all PET formulas
    print("\nRunning all PET formulas...")
    results = comparison.run_all()
    
    # Get results as DataFrame
    results_df = comparison.get_results_dataframe()
    
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    
    # Display statistics
    print("\nStatistics across all formulas:")
    stats = comparison.compute_statistics()
    print(stats)
    
    # Compute correlations
    print("\n" + "-" * 70)
    print("Correlations between formulas:")
    correlations = comparison.compute_correlations()
    print(correlations)
    
    # Compute pairwise differences
    print("\n" + "-" * 70)
    print("Mean absolute differences (mm/day):")
    differences = comparison.compute_pairwise_differences()
    print(differences)
    
    # Create visualizations
    print("\n" + "=" * 70)
    print("GENERATING VISUALIZATIONS")
    print("=" * 70)
    
    # Time series plot
    print("\n1. Time series comparison...")
    fig1 = plot_timeseries(results_df, title="PET Formula Comparison - Time Series")
    fig1.savefig('pet_timeseries.png', dpi=300, bbox_inches='tight')
    plt.close(fig1)
    print("   Saved: pet_timeseries.png")
    
    # Box plot comparison
    print("2. Box plot comparison...")
    fig2 = plot_box_comparison(results_df, title="PET Formula Distribution")
    fig2.savefig('pet_boxplot.png', dpi=300, bbox_inches='tight')
    plt.close(fig2)
    print("   Saved: pet_boxplot.png")
    
    # Correlation heatmap
    print("3. Correlation matrix...")
    fig3 = plot_correlation_matrix(results_df, title="Correlation Between PET Formulas")
    fig3.savefig('pet_correlation.png', dpi=300, bbox_inches='tight')
    plt.close(fig3)
    print("   Saved: pet_correlation.png")
    
    # Differences heatmap
    print("4. Differences heatmap...")
    fig4 = plot_differences_heatmap(differences, title="Mean Absolute Differences")
    fig4.savefig('pet_differences.png', dpi=300, bbox_inches='tight')
    plt.close(fig4)
    print("   Saved: pet_differences.png")
    
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    
    # Identify extreme cases
    print("\nHighest mean PET:")
    print(f"  {results_df.mean().idxmax()}: {results_df.mean().max():.2f} mm/day")
    
    print("\nLowest mean PET:")
    print(f"  {results_df.mean().idxmin()}: {results_df.mean().min():.2f} mm/day")
    
    print("\nMost variable formula (highest std):")
    print(f"  {results_df.std().idxmax()}: {results_df.std().max():.2f} mm/day")
    
    print("\nLeast variable formula (lowest std):")
    print(f"  {results_df.std().idxmin()}: {results_df.std().min():.2f} mm/day")
    
    # Find most similar formulas
    corr_values = correlations.values
    np.fill_diagonal(corr_values, 0)
    max_corr_idx = np.unravel_index(np.argmax(corr_values), corr_values.shape)
    formula1 = correlations.index[max_corr_idx[0]]
    formula2 = correlations.columns[max_corr_idx[1]]
    max_corr = corr_values[max_corr_idx]
    
    print(f"\nMost similar formulas (highest correlation):")
    print(f"  {formula1} vs {formula2}: r = {max_corr:.3f}")
    
    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
