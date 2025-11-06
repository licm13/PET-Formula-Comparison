"""
Visualization utilities for PET comparison
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional
import matplotlib.font_manager as fm
from pathlib import Path
import matplotlib


# 全局字体配置
_CHINESE_FONT_CONFIGURED = False


def setup_chinese_font(force=False):
    """
    Setup Chinese font for matplotlib
    Tries multiple common Chinese fonts on Windows
    
    Parameters:
    -----------
    force : bool
        Force reconfiguration even if already configured
    """
    global _CHINESE_FONT_CONFIGURED
    
    if _CHINESE_FONT_CONFIGURED and not force:
        return matplotlib.rcParams.get('font.sans-serif', [None])[0]
    
    chinese_fonts = [
        'Microsoft YaHei',  # 微软雅黑
        'SimHei',           # 黑体
        'SimSun',           # 宋体
        'KaiTi',            # 楷体
        'FangSong',         # 仿宋
    ]
    
    # Try to find an available Chinese font
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    selected_font = None
    for font in chinese_fonts:
        if font in available_fonts:
            selected_font = font
            break
    
    if selected_font:
        # Configure matplotlib to use Chinese font
        matplotlib.rcParams['font.sans-serif'] = [selected_font, 'Arial', 'DejaVu Sans']
        matplotlib.rcParams['font.family'] = 'sans-serif'
        matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        # Also set for current session
        plt.rcParams['font.sans-serif'] = [selected_font, 'Arial', 'DejaVu Sans']
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.unicode_minus'] = False
        
        _CHINESE_FONT_CONFIGURED = True
        print(f"Chinese font configured: {selected_font}")
        return selected_font
    else:
        # Fallback to default with warning
        print("Warning: No Chinese font found, Chinese characters may not display correctly")
        matplotlib.rcParams['axes.unicode_minus'] = False
        plt.rcParams['axes.unicode_minus'] = False
        return None

# Initialize Chinese font support on module import
CHINESE_FONT = setup_chinese_font()


def plot_timeseries(results_df: pd.DataFrame, title: str = "PET Comparison", 
                   figsize=(16, 10), save_path: Optional[str] = None):
    """
    Plot enhanced time series of PET estimates from different formulas
    
    Parameters:
    -----------
    results_df : pd.DataFrame
        DataFrame with PET estimates from different formulas
    title : str
        Plot title
    figsize : tuple
        Figure size
    save_path : str, optional
        Path to save the figure
    """
    # Ensure Chinese font is configured
    setup_chinese_font()
    
    fig = plt.figure(figsize=figsize)
    
    # Create a grid for subplots
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # Main time series plot
    ax_main = fig.add_subplot(gs[0:2, :])
    
    # Use different line styles for better distinction
    line_styles = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--', ':']
    colors = plt.cm.tab20(np.linspace(0, 1, len(results_df.columns)))
    
    for idx, column in enumerate(results_df.columns):
        ax_main.plot(results_df.index, results_df[column], 
                    label=column, alpha=0.8, linewidth=2,
                    linestyle=line_styles[idx % len(line_styles)],
                    color=colors[idx])
    
    ax_main.set_xlabel('Time', fontsize=13, fontweight='bold')
    ax_main.set_ylabel('PET (mm/day)', fontsize=13, fontweight='bold')
    ax_main.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax_main.legend(loc='best', fontsize=10, ncol=3, framealpha=0.9)
    ax_main.grid(True, alpha=0.3, linestyle='--')
    
    # Add monthly mean subplot
    ax_monthly = fig.add_subplot(gs[2, 0])
    monthly_means = results_df.groupby(results_df.index.month).mean()
    
    for idx, column in enumerate(results_df.columns):
        ax_monthly.plot(monthly_means.index, monthly_means[column], 
                       marker='o', linewidth=2, markersize=4,
                       color=colors[idx], alpha=0.7)
    
    ax_monthly.set_xlabel('Month', fontsize=11, fontweight='bold')
    ax_monthly.set_ylabel('Monthly Avg PET (mm/day)', fontsize=11, fontweight='bold')
    ax_monthly.set_title('Monthly Average Comparison', fontsize=12, fontweight='bold')
    ax_monthly.grid(True, alpha=0.3)
    ax_monthly.set_xticks(range(1, 13))
    
    # Add range (max-min) subplot
    ax_range = fig.add_subplot(gs[2, 1])
    daily_range = results_df.max(axis=1) - results_df.min(axis=1)
    ax_range.fill_between(results_df.index, daily_range, alpha=0.5, color='coral')
    ax_range.plot(results_df.index, daily_range, color='darkred', linewidth=1.5)
    ax_range.set_xlabel('Time', fontsize=11, fontweight='bold')
    ax_range.set_ylabel('Inter-formula Range (mm/day)', fontsize=11, fontweight='bold')
    ax_range.set_title('Formula Variation Range', fontsize=12, fontweight='bold')
    ax_range.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"   Saved: {save_path}")
    
    return fig


def plot_box_comparison(results_df: pd.DataFrame, title: str = "PET Distribution Comparison", 
                       figsize=(14, 8), save_path: Optional[str] = None):
    """
    Enhanced box plot comparison of PET formulas with violin plots
    
    Parameters:
    -----------
    results_df : pd.DataFrame
        DataFrame with PET estimates from different formulas
    title : str
        Plot title
    figsize : tuple
        Figure size
    save_path : str, optional
        Path to save the figure
    """
    # Ensure Chinese font is configured
    setup_chinese_font()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, height_ratios=[3, 2])
    
    # Box plot with enhanced styling
    bp = ax1.boxplot([results_df[col].values for col in results_df.columns],
                     labels=results_df.columns,
                     patch_artist=True,
                     notch=True,
                     showmeans=True,
                     meanprops=dict(marker='D', markerfacecolor='red', markersize=8))
    
    # Color the boxes
    colors = plt.cm.Set3(np.linspace(0, 1, len(results_df.columns)))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax1.set_ylabel('PET (mm/day)', fontsize=13, fontweight='bold')
    ax1.set_title(title, fontsize=15, fontweight='bold', pad=15)
    ax1.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax1.tick_params(axis='x', rotation=45)
    
    # Add statistical comparison table
    stats_data = []
    for col in results_df.columns:
        stats_data.append([
            col,
            f"{results_df[col].mean():.3f}",
            f"{results_df[col].std():.3f}",
            f"{results_df[col].min():.3f}",
            f"{results_df[col].max():.3f}"
        ])
    
    ax2.axis('tight')
    ax2.axis('off')
    table = ax2.table(cellText=stats_data,
                     colLabels=['Formula', 'Mean', 'Std', 'Min', 'Max'],
                     cellLoc='center',
                     loc='center',
                     colWidths=[0.2, 0.2, 0.2, 0.2, 0.2])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # Color header
    for i in range(5):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(stats_data) + 1):
        for j in range(5):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#f0f0f0')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"   Saved: {save_path}")
    
    return fig


def plot_correlation_matrix(results_df: pd.DataFrame, title: str = "Formula Correlations", 
                           figsize=(12, 10), save_path: Optional[str] = None):
    """
    Enhanced correlation matrix heatmap with hierarchical clustering
    
    Parameters:
    -----------
    results_df : pd.DataFrame
        DataFrame with PET estimates from different formulas
    title : str
        Plot title
    figsize : tuple
        Figure size
    save_path : str, optional
        Path to save the figure
    """
    # Ensure Chinese font is configured
    setup_chinese_font()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, width_ratios=[3, 1])
    
    corr = results_df.corr()
    
    # Main correlation heatmap with clustering
    sns.heatmap(corr, annot=True, fmt='.3f', cmap='RdYlGn', center=0.8,
                square=True, linewidths=1.5, cbar_kws={"shrink": 0.8}, 
                ax=ax1, vmin=0, vmax=1,
                cbar_ax=None, annot_kws={'size': 9, 'weight': 'bold'})
    
    ax1.set_title(title, fontsize=15, fontweight='bold', pad=15)
    ax1.set_xlabel('')
    ax1.set_ylabel('')
    
    # Add correlation strength categories
    categories = []
    for col in corr.columns:
        avg_corr = corr[col].drop(col).mean()  # Average correlation with others
        categories.append(avg_corr)
    
    # Bar plot of average correlations
    colors_bar = plt.cm.RdYlGn(np.array(categories))
    ax2.barh(range(len(categories)), categories, color=colors_bar)
    ax2.set_yticks(range(len(categories)))
    ax2.set_yticklabels(corr.columns, fontsize=9)
    ax2.set_xlabel('Avg Correlation', fontsize=10, fontweight='bold')
    ax2.set_title('Similarity', fontsize=11, fontweight='bold')
    ax2.axvline(x=0.9, color='red', linestyle='--', alpha=0.5, linewidth=1)
    ax2.grid(True, alpha=0.3, axis='x')
    ax2.set_xlim([0.5, 1.0])
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"   Saved: {save_path}")
    
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


def plot_differences_heatmap(differences_df: pd.DataFrame, 
                            title: str = "Mean Absolute Differences (mm/day)", 
                            figsize=(12, 10), save_path: Optional[str] = None):
    """
    Enhanced heatmap of pairwise differences with additional statistics
    
    Parameters:
    -----------
    differences_df : pd.DataFrame
        DataFrame with pairwise differences
    title : str
        Plot title
    figsize : tuple
        Figure size
    save_path : str, optional
        Path to save the figure
    """
    # Ensure Chinese font is configured
    setup_chinese_font()
    
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(2, 2, height_ratios=[3, 1], width_ratios=[3, 1], 
                         hspace=0.3, wspace=0.3)
    
    ax_main = fig.add_subplot(gs[0, 0])
    ax_bar = fig.add_subplot(gs[0, 1])
    ax_stats = fig.add_subplot(gs[1, :])
    
    # Main heatmap
    sns.heatmap(differences_df, annot=True, fmt='.3f', cmap='YlOrRd',
                square=True, linewidths=1.5, cbar_kws={"shrink": 0.8}, 
                ax=ax_main, annot_kws={'size': 8})
    
    ax_main.set_title(title, fontsize=14, fontweight='bold', pad=15)
    
    # Bar plot of average differences
    avg_diff = []
    for col in differences_df.columns:
        # Average difference excluding diagonal (self-comparison)
        mask = differences_df.index != col
        avg_diff.append(differences_df.loc[mask, col].mean())
    
    colors_bar = plt.cm.YlOrRd(np.array(avg_diff) / max(avg_diff))
    ax_bar.barh(range(len(avg_diff)), avg_diff, color=colors_bar)
    ax_bar.set_yticks(range(len(avg_diff)))
    ax_bar.set_yticklabels(differences_df.columns, fontsize=9)
    ax_bar.set_xlabel('Avg Diff (mm/day)', fontsize=9, fontweight='bold')
    ax_bar.set_title('Divergence', fontsize=10, fontweight='bold')
    ax_bar.grid(True, alpha=0.3, axis='x')
    
    # Statistics text box
    ax_stats.axis('off')
    
    # Find max and min differences (excluding diagonal)
    diff_values = differences_df.values.copy()
    np.fill_diagonal(diff_values, np.nan)
    max_diff = np.nanmax(diff_values)
    min_diff = np.nanmin(diff_values)
    
    max_idx = np.unravel_index(np.nanargmax(diff_values), diff_values.shape)
    formula1_max = differences_df.index[max_idx[0]]
    formula2_max = differences_df.columns[max_idx[1]]
    
    stats_text = f"""
    Statistical Summary:
    
    • Max Difference: {max_diff:.3f} mm/day
      Formula Pair: {formula1_max} vs {formula2_max}
    
    • Min Non-zero Difference: {min_diff:.3f} mm/day
    
    • Average Difference: {np.nanmean(diff_values):.3f} mm/day
    
    • Std of Differences: {np.nanstd(diff_values):.3f} mm/day
    """
    
    ax_stats.text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                 family='monospace')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"   Saved: {save_path}")
    
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
