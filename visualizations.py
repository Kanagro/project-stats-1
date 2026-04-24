"""Visualization module for financial data and analysis."""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from typing import Optional, List, Tuple


def plot_price_history(
    data: pd.DataFrame,
    title: str = "Price History",
    figsize: Tuple[int, int] = (12, 6),
    show_volume: bool = True
) -> plt.Figure:
    """
    Plot historical price data with optional volume.
    
    Args:
        data: DataFrame with 'date', 'close', and optional 'volume' columns
        title: Plot title
        figsize: Figure size (width, height)
        show_volume: Whether to display volume subplot
        
    Returns:
        Matplotlib figure object
    """
    if show_volume and 'volume' in data.columns:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, gridspec_kw={'height_ratios': [3, 1]})
    else:
        fig, ax1 = plt.subplots(figsize=figsize)
    
    # Plot price
    if 'date' in data.columns:
        dates = data['date']
    else:
        dates = data.index
    
    ax1.plot(dates, data['close'], linewidth=2, color='#1f77b4', label='Close Price')
    
    # Add SMA if available
    if 'SMA_20' in data.columns:
        ax1.plot(dates, data['SMA_20'], linewidth=1.5, color='#ff7f0e', alpha=0.7, label='SMA 20')
    if 'SMA_50' in data.columns:
        ax1.plot(dates, data['SMA_50'], linewidth=1.5, color='#2ca02c', alpha=0.7, label='SMA 50')
    
    ax1.set_title(title, fontsize=14, fontweight='bold')
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Plot volume if requested
    if show_volume and 'volume' in data.columns:
        ax2.bar(dates, data['volume'], color='#7f7f7f', alpha=0.3)
        ax2.set_ylabel('Volume', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.grid(True, alpha=0.3)
    else:
        ax1.set_xlabel('Date', fontsize=12)
    
    plt.tight_layout()
    return fig


def plot_bollinger_bands(
    data: pd.DataFrame,
    title: str = "Bollinger Bands",
    figsize: Tuple[int, int] = (12, 6)
) -> plt.Figure:
    """
    Plot price with Bollinger Bands.
    
    Args:
        data: DataFrame with 'close', 'BB_Upper', 'BB_Middle', 'BB_Lower'
        title: Plot title
        figsize: Figure size
        
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    if 'date' in data.columns:
        dates = data['date']
    else:
        dates = data.index
    
    # Plot bands
    if 'BB_Upper' in data.columns:
        ax.fill_between(dates, data['BB_Upper'], data['BB_Lower'], alpha=0.2, color='#1f77b4', label='Bollinger Bands')
        ax.plot(dates, data['BB_Upper'], linewidth=1, color='#1f77b4', linestyle='--', alpha=0.5)
        ax.plot(dates, data['BB_Lower'], linewidth=1, color='#1f77b4', linestyle='--', alpha=0.5)
    
    # Plot middle band and price
    if 'BB_Middle' in data.columns:
        ax.plot(dates, data['BB_Middle'], linewidth=1.5, color='#ff7f0e', label='Middle Band (SMA 20)')
    ax.plot(dates, data['close'], linewidth=2, color='#2ca02c', label='Close Price')
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price ($)', fontsize=12)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_rsi(
    data: pd.DataFrame,
    title: str = "Relative Strength Index (RSI)",
    figsize: Tuple[int, int] = (12, 6)
) -> plt.Figure:
    """
    Plot RSI indicator with overbought/oversold zones.
    
    Args:
        data: DataFrame with 'RSI_14' column
        title: Plot title
        figsize: Figure size
        
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    if 'date' in data.columns:
        dates = data['date']
    else:
        dates = data.index
    
    # Plot RSI
    if 'RSI_14' in data.columns:
        ax.plot(dates, data['RSI_14'], linewidth=2, color='#1f77b4', label='RSI 14')
    
    # Add overbought/oversold zones
    ax.axhline(y=70, color='r', linestyle='--', linewidth=1, alpha=0.5, label='Overbought (70)')
    ax.axhline(y=30, color='g', linestyle='--', linewidth=1, alpha=0.5, label='Oversold (30)')
    ax.fill_between(dates, 70, 100, alpha=0.1, color='red')
    ax.fill_between(dates, 0, 30, alpha=0.1, color='green')
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('RSI', fontsize=12)
    ax.set_ylim(0, 100)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_macd(
    data: pd.DataFrame,
    title: str = "MACD",
    figsize: Tuple[int, int] = (12, 6)
) -> plt.Figure:
    """
    Plot MACD indicator.
    
    Args:
        data: DataFrame with 'MACD', 'MACD_Signal', 'MACD_Hist'
        title: Plot title
        figsize: Figure size
        
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    if 'date' in data.columns:
        dates = data['date']
    else:
        dates = data.index
    
    # Plot MACD line and signal
    if 'MACD' in data.columns:
        ax.plot(dates, data['MACD'], linewidth=2, color='#1f77b4', label='MACD')
    if 'MACD_Signal' in data.columns:
        ax.plot(dates, data['MACD_Signal'], linewidth=2, color='#ff7f0e', label='Signal')
    
    # Plot histogram
    if 'MACD_Hist' in data.columns:
        colors = ['g' if x > 0 else 'r' for x in data['MACD_Hist']]
        ax.bar(dates, data['MACD_Hist'], color=colors, alpha=0.3, label='Histogram')
    
    ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.5)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('MACD', fontsize=12)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_cumulative_returns(
    returns: pd.Series,
    title: str = "Cumulative Returns",
    figsize: Tuple[int, int] = (12, 6),
    benchmark: Optional[pd.Series] = None
) -> plt.Figure:
    """
    Plot cumulative returns.
    
    Args:
        returns: Series of returns
        title: Plot title
        figsize: Figure size
        benchmark: Optional benchmark returns series for comparison
        
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    cumulative = (1 + returns).cumprod()
    ax.plot(cumulative.index, (cumulative - 1) * 100, linewidth=2, color='#1f77b4', label='Portfolio')
    
    if benchmark is not None:
        cumulative_bench = (1 + benchmark).cumprod()
        ax.plot(cumulative_bench.index, (cumulative_bench - 1) * 100, linewidth=2, 
                color='#ff7f0e', alpha=0.7, label='Benchmark')
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Cumulative Return (%)', fontsize=12)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_drawdown(
    returns: pd.Series,
    title: str = "Drawdown",
    figsize: Tuple[int, int] = (12, 6)
) -> plt.Figure:
    """
    Plot drawdown over time.
    
    Args:
        returns: Series of returns
        title: Plot title
        figsize: Figure size
        
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max * 100
    
    ax.fill_between(drawdown.index, drawdown, 0, alpha=0.3, color='r')
    ax.plot(drawdown.index, drawdown, linewidth=2, color='r', label='Drawdown')
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Drawdown (%)', fontsize=12)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_returns_distribution(
    returns: pd.Series,
    title: str = "Returns Distribution",
    figsize: Tuple[int, int] = (10, 6),
    bins: int = 50
) -> plt.Figure:
    """
    Plot histogram of returns distribution.
    
    Args:
        returns: Series of returns
        title: Plot title
        figsize: Figure size
        bins: Number of histogram bins
        
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    returns_clean = returns.dropna()
    ax.hist(returns_clean * 100, bins=bins, alpha=0.7, color='#1f77b4', edgecolor='black')
    
    # Add mean and std lines
    mean = returns_clean.mean() * 100
    std = returns_clean.std() * 100
    ax.axvline(mean, color='r', linestyle='--', linewidth=2, label=f'Mean: {mean:.2f}%')
    ax.axvline(mean + std, color='orange', linestyle='--', linewidth=1, alpha=0.7, label=f'±1 Std Dev: {std:.2f}%')
    ax.axvline(mean - std, color='orange', linestyle='--', linewidth=1, alpha=0.7)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Daily Return (%)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig


def plot_risk_metrics(
    risk_metrics: dict,
    title: str = "Risk Metrics Summary",
    figsize: Tuple[int, int] = (10, 8)
) -> plt.Figure:
    """
    Plot risk metrics as a summary table/bar chart.
    
    Args:
        risk_metrics: Dictionary of risk metrics
        title: Plot title
        figsize: Figure size
        
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    
    # Prepare data for table
    metrics_display = {
        'Annual Return': f"{risk_metrics.get('annualized_return', 0):.2%}",
        'Volatility': f"{risk_metrics.get('volatility', 0):.2%}",
        'Sharpe Ratio': f"{risk_metrics.get('sharpe_ratio', 0):.4f}",
        'Sortino Ratio': f"{risk_metrics.get('sortino_ratio', 0):.4f}",
        'Max Drawdown': f"{risk_metrics.get('max_drawdown', 0):.2%}",
        'Calmar Ratio': f"{risk_metrics.get('calmar_ratio', 0):.4f}",
        'VaR (95%)': f"{risk_metrics.get('var_95', 0):.2%}",
        'CVaR (95%)': f"{risk_metrics.get('cvar_95', 0):.2%}",
    }
    
    if 'beta' in risk_metrics:
        metrics_display['Beta'] = f"{risk_metrics['beta']:.4f}"
    if 'alpha' in risk_metrics:
        metrics_display['Alpha'] = f"{risk_metrics['alpha']:.2%}"
    if 'information_ratio' in risk_metrics:
        metrics_display['Information Ratio'] = f"{risk_metrics['information_ratio']:.4f}"
    
    # Create table
    table_data = [[metric, value] for metric, value in metrics_display.items()]
    table = ax.table(cellText=table_data, colLabels=['Metric', 'Value'], 
                     cellLoc='center', loc='center', colWidths=[0.6, 0.4])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2)
    
    # Style header
    for i in range(2):
        table[(0, i)].set_facecolor('#1f77b4')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(table_data) + 1):
        for j in range(2):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#f0f0f0')
            else:
                table[(i, j)].set_facecolor('#ffffff')
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    return fig


def plot_correlation_heatmap(
    corr_matrix: pd.DataFrame,
    title: str = "Correlation Heatmap",
    figsize: Tuple[int, int] = (10, 8),
    cmap: str = 'coolwarm'
) -> plt.Figure:
    """
    Plot correlation matrix as heatmap.
    
    Args:
        corr_matrix: Correlation matrix DataFrame
        title: Plot title
        figsize: Figure size
        cmap: Colormap name
        
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    im = ax.imshow(corr_matrix, cmap=cmap, aspect='auto', vmin=-1, vmax=1)
    
    # Set ticks and labels
    ax.set_xticks(np.arange(len(corr_matrix.columns)))
    ax.set_yticks(np.arange(len(corr_matrix.columns)))
    ax.set_xticklabels(corr_matrix.columns, rotation=45, ha='right')
    ax.set_yticklabels(corr_matrix.columns)
    
    # Add correlation values
    for i in range(len(corr_matrix)):
        for j in range(len(corr_matrix)):
            text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                          ha="center", va="center", color="black", fontsize=10)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Correlation', rotation=270, labelpad=20)
    
    plt.tight_layout()
    return fig


def plot_portfolio_composition(
    weights: dict,
    title: str = "Portfolio Composition",
    figsize: Tuple[int, int] = (10, 8)
) -> plt.Figure:
    """
    Plot portfolio weights as pie chart.
    
    Args:
        weights: Dictionary of asset weights
        title: Plot title
        figsize: Figure size
        
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    labels = list(weights.keys())
    sizes = list(weights.values())
    colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                        startangle=90, textprops={'fontsize': 11})
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig


def save_figure(fig: plt.Figure, filename: str, dpi: int = 300) -> None:
    """
    Save figure to file.
    
    Args:
        fig: Matplotlib figure object
        filename: Output filename (with extension: .png, .pdf, .jpg)
        dpi: Resolution in dots per inch
    """
    fig.savefig(filename, dpi=dpi, bbox_inches='tight')
    print(f"Figure saved to {filename}")


def show_figure(fig: plt.Figure) -> None:
    """
    Display figure.
    
    Args:
        fig: Matplotlib figure object
    """
    plt.show()
