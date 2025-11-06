"""
Visualization utilities for PET comparison
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional


def plot_timeseries(results_df: pd.DataFrame, title: str = "PET Comparison", figsize=(14, 8)):
    """
    Plot time series of PET estimates from different formulas
    
    Parameters:
    -----------
    results_df : pd.DataFrame
        DataFrame with PET estimates from different formulas
    title : str
        Plot title
    figsize : tuple
        Figure size
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    for column in results_df.columns:
        ax.plot(results_df.index, results_df[column], label=column, alpha=0.7, linewidth=1.5)
    
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('PET (mm/day)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_box_comparison(results_df: pd.DataFrame, title: str = "PET Distribution Comparison", figsize=(12, 6)):
    """
    Box plot comparison of PET formulas
    
    Parameters:
    -----------
    results_df : pd.DataFrame
        DataFrame with PET estimates from different formulas
    title : str
        Plot title
    figsize : tuple
        Figure size
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    results_df.boxplot(ax=ax, rot=45)
    ax.set_ylabel('PET (mm/day)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig


def plot_correlation_matrix(results_df: pd.DataFrame, title: str = "PET Formula Correlations", figsize=(10, 8)):
    """
    Plot correlation matrix heatmap
    
    Parameters:
    -----------
    results_df : pd.DataFrame
        DataFrame with PET estimates from different formulas
    title : str
        Plot title
    figsize : tuple
        Figure size
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    corr = results_df.corr()
    
    sns.heatmap(corr, annot=True, fmt='.3f', cmap='coolwarm', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig


def plot_scatter_matrix(results_df: pd.DataFrame, formulas: Optional[List[str]] = None, figsize=(12, 12)):
    """
    Plot scatter matrix comparing formulas
    
    Parameters:
    -----------
    results_df : pd.DataFrame
        DataFrame with PET estimates from different formulas
    formulas : List[str], optional
        List of formulas to compare (default: all)
    figsize : tuple
        Figure size
    """
    if formulas is None:
        formulas = results_df.columns.tolist()
    
    df_subset = results_df[formulas]
    
    fig = pd.plotting.scatter_matrix(df_subset, figsize=figsize, alpha=0.5, diagonal='hist')
    
    plt.suptitle('Pairwise Scatter Plots', fontsize=14, fontweight='bold', y=1.0)
    plt.tight_layout()
    
    return fig


def plot_differences_heatmap(differences_df: pd.DataFrame, title: str = "Mean Absolute Differences (mm/day)", figsize=(10, 8)):
    """
    Plot heatmap of pairwise differences
    
    Parameters:
    -----------
    differences_df : pd.DataFrame
        DataFrame with pairwise differences
    title : str
        Plot title
    figsize : tuple
        Figure size
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    sns.heatmap(differences_df, annot=True, fmt='.3f', cmap='YlOrRd',
                square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig


def plot_seasonal_comparison(results_df: pd.DataFrame, title: str = "Seasonal PET Comparison", figsize=(14, 6)):
    """
    Plot seasonal comparison (monthly averages)
    
    Parameters:
    -----------
    results_df : pd.DataFrame
        DataFrame with PET estimates (index should be datetime)
    title : str
        Plot title
    figsize : tuple
        Figure size
    """
    # Calculate monthly means
    monthly_means = results_df.groupby(results_df.index.month).mean()
    
    fig, ax = plt.subplots(figsize=figsize)
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for column in monthly_means.columns:
        ax.plot(monthly_means.index, monthly_means[column], marker='o', label=column, linewidth=2)
    
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(months)
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('PET (mm/day)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_sensitivity_analysis(
    base_results: pd.DataFrame,
    varied_results: Dict[str, pd.DataFrame],
    parameter_name: str,
    figsize=(14, 8)
):
    """
    Plot sensitivity analysis results
    
    Parameters:
    -----------
    base_results : pd.DataFrame
        Base case results
    varied_results : Dict[str, pd.DataFrame]
        Dictionary of results with varied parameter values
    parameter_name : str
        Name of the varied parameter
    figsize : tuple
        Figure size
    """
    n_formulas = len(base_results.columns)
    n_variations = len(varied_results)
    
    fig, axes = plt.subplots(1, n_formulas, figsize=figsize, sharey=True)
    
    if n_formulas == 1:
        axes = [axes]
    
    for idx, formula in enumerate(base_results.columns):
        ax = axes[idx]
        
        # Plot base case
        base_mean = base_results[formula].mean()
        ax.axhline(y=base_mean, color='black', linestyle='--', linewidth=2, label='Base')
        
        # Plot variations
        param_values = []
        means = []
        
        for param_value, results in varied_results.items():
            param_values.append(float(param_value))
            means.append(results[formula].mean())
        
        ax.plot(param_values, means, marker='o', linewidth=2, markersize=8)
        
        ax.set_xlabel(parameter_name, fontsize=11)
        if idx == 0:
            ax.set_ylabel('Mean PET (mm/day)', fontsize=11)
        ax.set_title(formula, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    plt.suptitle(f'Sensitivity to {parameter_name}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    return fig


def plot_co2_response(
    results_dict: Dict[float, float],
    formula_name: str,
    title: str = "CO2 Response",
    figsize=(10, 6)
):
    """
    Plot PET response to CO2 concentration
    
    Parameters:
    -----------
    results_dict : Dict[float, float]
        Dictionary mapping CO2 concentrations to PET values
    formula_name : str
        Name of the formula
    title : str
        Plot title
    figsize : tuple
        Figure size
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    co2_values = sorted(results_dict.keys())
    pet_values = [results_dict[co2] for co2 in co2_values]
    
    ax.plot(co2_values, pet_values, marker='o', linewidth=2, markersize=8)
    
    ax.set_xlabel('CO2 Concentration (ppm)', fontsize=12)
    ax.set_ylabel('PET (mm/day)', fontsize=12)
    ax.set_title(f'{title} - {formula_name}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Add reference line at 380 ppm
    ax.axvline(x=380, color='red', linestyle='--', alpha=0.5, label='Reference (380 ppm)')
    ax.legend()
    
    plt.tight_layout()
    return fig
