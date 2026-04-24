"""Unit tests for visualizations module."""

import pytest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src.visualizations import (
    plot_price_history,
    plot_bollinger_bands,
    plot_rsi,
    plot_macd,
    plot_cumulative_returns,
    plot_drawdown,
    plot_returns_distribution,
    plot_risk_metrics,
    plot_correlation_heatmap,
    plot_portfolio_composition,
)


@pytest.fixture
def sample_data():
    """Create sample OHLCV data with indicators."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100)
    close_prices = pd.Series(100 * np.exp(np.cumsum(np.random.normal(0.0005, 0.02, 100))))
    
    data = pd.DataFrame({
        'date': dates,
        'open': (close_prices * 0.99).values,
        'high': (close_prices * 1.01).values,
        'low': (close_prices * 0.98).values,
        'close': close_prices.values,
        'volume': np.random.randint(1000000, 5000000, 100),
        'SMA_20': close_prices.rolling(20).mean().values,
        'SMA_50': close_prices.rolling(50).mean().values,
        'BB_Upper': (close_prices.rolling(20).mean() + 2 * close_prices.rolling(20).std()).values,
        'BB_Middle': close_prices.rolling(20).mean().values,
        'BB_Lower': (close_prices.rolling(20).mean() - 2 * close_prices.rolling(20).std()).values,
        'RSI_14': 50 + np.random.normal(0, 15, 100),
        'MACD': np.random.normal(0, 0.5, 100),
        'MACD_Signal': np.random.normal(0, 0.5, 100),
        'MACD_Hist': np.random.normal(0, 0.2, 100),
    })
    
    return data


@pytest.fixture
def sample_returns():
    """Create sample returns series."""
    np.random.seed(42)
    returns = pd.Series(np.random.normal(0.0005, 0.02, 100),
                       index=pd.date_range('2024-01-01', periods=100))
    return returns


@pytest.fixture
def sample_risk_metrics():
    """Create sample risk metrics."""
    return {
        'annualized_return': 0.15,
        'volatility': 0.18,
        'sharpe_ratio': 0.83,
        'sortino_ratio': 1.2,
        'max_drawdown': -0.12,
        'calmar_ratio': 1.25,
        'var_95': -0.025,
        'cvar_95': -0.035,
        'beta': 1.1,
        'alpha': 0.05,
        'information_ratio': 0.75,
    }


@pytest.fixture
def sample_corr_matrix():
    """Create sample correlation matrix."""
    return pd.DataFrame(
        np.array([
            [1.0, 0.6, 0.5],
            [0.6, 1.0, 0.7],
            [0.5, 0.7, 1.0]
        ]),
        index=['AAPL', 'GOOGL', 'MSFT'],
        columns=['AAPL', 'GOOGL', 'MSFT']
    )


def test_plot_price_history(sample_data):
    """Test price history plot."""
    fig = plot_price_history(sample_data, show_volume=True)
    
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 2  # Price and volume
    
    plt.close(fig)


def test_plot_price_history_no_volume(sample_data):
    """Test price history plot without volume."""
    fig = plot_price_history(sample_data, show_volume=False)
    
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    
    plt.close(fig)


def test_plot_bollinger_bands(sample_data):
    """Test Bollinger Bands plot."""
    fig = plot_bollinger_bands(sample_data)
    
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    
    plt.close(fig)


def test_plot_rsi(sample_data):
    """Test RSI plot."""
    fig = plot_rsi(sample_data)
    
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    
    plt.close(fig)


def test_plot_macd(sample_data):
    """Test MACD plot."""
    fig = plot_macd(sample_data)
    
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    
    plt.close(fig)


def test_plot_cumulative_returns(sample_returns):
    """Test cumulative returns plot."""
    fig = plot_cumulative_returns(sample_returns)
    
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    
    plt.close(fig)


def test_plot_cumulative_returns_with_benchmark(sample_returns):
    """Test cumulative returns plot with benchmark."""
    benchmark = sample_returns * 0.8
    fig = plot_cumulative_returns(sample_returns, benchmark=benchmark)
    
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    
    plt.close(fig)


def test_plot_drawdown(sample_returns):
    """Test drawdown plot."""
    fig = plot_drawdown(sample_returns)
    
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    
    plt.close(fig)


def test_plot_returns_distribution(sample_returns):
    """Test returns distribution plot."""
    fig = plot_returns_distribution(sample_returns)
    
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    
    plt.close(fig)


def test_plot_risk_metrics(sample_risk_metrics):
    """Test risk metrics plot."""
    fig = plot_risk_metrics(sample_risk_metrics)
    
    assert isinstance(fig, plt.Figure)
    
    plt.close(fig)


def test_plot_correlation_heatmap(sample_corr_matrix):
    """Test correlation heatmap plot."""
    fig = plot_correlation_heatmap(sample_corr_matrix)
    
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) >= 1
    
    plt.close(fig)


def test_plot_portfolio_composition():
    """Test portfolio composition plot."""
    weights = {'AAPL': 0.3, 'GOOGL': 0.4, 'MSFT': 0.3}
    fig = plot_portfolio_composition(weights)
    
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    
    plt.close(fig)


def test_plot_portfolio_composition_different_weights():
    """Test portfolio composition with various weights."""
    weights = {'Stock1': 0.2, 'Stock2': 0.3, 'Stock3': 0.15, 'Stock4': 0.35}
    fig = plot_portfolio_composition(weights)
    
    assert isinstance(fig, plt.Figure)
    
    plt.close(fig)


def test_all_figures_close_properly():
    """Test that all figures can be properly closed."""
    # This ensures memory management
    np.random.seed(42)
    data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=50),
        'close': 100 * np.exp(np.cumsum(np.random.normal(0.0005, 0.02, 50))),
        'volume': np.random.randint(1000000, 5000000, 50),
    })
    
    figs = []
    figs.append(plot_price_history(data))
    figs.append(plot_cumulative_returns(data['close'].pct_change()))
    figs.append(plot_returns_distribution(data['close'].pct_change()))
    
    for fig in figs:
        plt.close(fig)
    
    assert True
