"""Unit tests for risk metrics module."""

import pytest
import pandas as pd
import numpy as np
from src.risk_metrics import (
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_volatility,
    calculate_var,
    calculate_cvar,
    calculate_max_drawdown,
    calculate_calmar_ratio,
    calculate_information_ratio,
    calculate_correlation_matrix,
    calculate_beta,
    calculate_alpha,
    calculate_risk_metrics_summary,
)


@pytest.fixture
def sample_returns():
    """Create sample returns data."""
    np.random.seed(42)
    returns = pd.Series(np.random.normal(0.0005, 0.02, 252))
    return returns


@pytest.fixture
def benchmark_returns():
    """Create sample benchmark returns."""
    np.random.seed(41)
    returns = pd.Series(np.random.normal(0.0004, 0.015, 252))
    return returns


@pytest.fixture
def price_data():
    """Create sample price data for multiple assets."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=252)
    asset1 = 100 * np.exp(np.cumsum(np.random.normal(0.0005, 0.02, 252)))
    asset2 = 100 * np.exp(np.cumsum(np.random.normal(0.0004, 0.015, 252)))
    asset3 = 100 * np.exp(np.cumsum(np.random.normal(0.0006, 0.018, 252)))
    
    return pd.DataFrame({
        'date': dates,
        'asset1': asset1,
        'asset2': asset2,
        'asset3': asset3
    }).set_index('date')


def test_sharpe_ratio(sample_returns):
    """Test Sharpe ratio calculation."""
    sharpe = calculate_sharpe_ratio(sample_returns)
    assert isinstance(sharpe, float)
    assert not np.isnan(sharpe)


def test_sortino_ratio(sample_returns):
    """Test Sortino ratio calculation."""
    sortino = calculate_sortino_ratio(sample_returns)
    assert isinstance(sortino, float)
    assert not np.isnan(sortino)
    # Sortino should typically be higher than Sharpe (only penalizes downside)
    sharpe = calculate_sharpe_ratio(sample_returns)
    assert sortino >= sharpe or np.isclose(sortino, sharpe)


def test_volatility(sample_returns):
    """Test volatility calculation."""
    vol_annual = calculate_volatility(sample_returns, annualized=True)
    vol_daily = calculate_volatility(sample_returns, annualized=False)
    
    assert isinstance(vol_annual, float)
    assert isinstance(vol_daily, float)
    assert vol_annual > vol_daily  # Annualized should be larger


def test_var(sample_returns):
    """Test Value at Risk calculation."""
    var_95 = calculate_var(sample_returns, 0.95)
    var_99 = calculate_var(sample_returns, 0.99)
    
    assert isinstance(var_95, float)
    assert var_95 < 0  # VaR should be negative
    assert var_99 < var_95  # 99% VaR should be worse than 95%


def test_cvar(sample_returns):
    """Test Conditional Value at Risk calculation."""
    cvar_95 = calculate_cvar(sample_returns, 0.95)
    var_95 = calculate_var(sample_returns, 0.95)
    
    assert isinstance(cvar_95, float)
    assert cvar_95 < var_95  # CVaR should be worse than VaR


def test_max_drawdown(sample_returns):
    """Test maximum drawdown calculation."""
    max_dd = calculate_max_drawdown(sample_returns)
    
    assert isinstance(max_dd, float)
    assert max_dd < 0  # Drawdown should be negative
    assert max_dd >= -1  # Drawdown should be >= -100%


def test_calmar_ratio(sample_returns):
    """Test Calmar ratio calculation."""
    calmar = calculate_calmar_ratio(sample_returns)
    assert isinstance(calmar, float)
    assert not np.isnan(calmar)


def test_information_ratio(sample_returns, benchmark_returns):
    """Test Information ratio calculation."""
    ir = calculate_information_ratio(sample_returns, benchmark_returns)
    assert isinstance(ir, float)
    assert not np.isnan(ir)


def test_correlation_matrix(price_data):
    """Test correlation matrix calculation."""
    corr = calculate_correlation_matrix(price_data)
    
    assert isinstance(corr, pd.DataFrame)
    assert corr.shape == (3, 3)
    assert np.allclose(np.diag(corr), 1.0)  # Diagonal should be 1
    # Correlation matrix should be symmetric
    assert np.allclose(corr, corr.T)


def test_beta(sample_returns, benchmark_returns):
    """Test beta calculation."""
    beta = calculate_beta(sample_returns, benchmark_returns)
    assert isinstance(beta, float)
    assert not np.isnan(beta)


def test_alpha(sample_returns, benchmark_returns):
    """Test alpha calculation."""
    alpha = calculate_alpha(sample_returns, benchmark_returns)
    assert isinstance(alpha, float)
    assert not np.isnan(alpha)


def test_risk_metrics_summary(sample_returns, benchmark_returns):
    """Test comprehensive risk metrics summary."""
    summary = calculate_risk_metrics_summary(sample_returns)
    
    assert isinstance(summary, dict)
    assert 'sharpe_ratio' in summary
    assert 'sortino_ratio' in summary
    assert 'volatility' in summary
    assert 'var_95' in summary
    assert 'cvar_95' in summary
    assert 'max_drawdown' in summary
    assert 'calmar_ratio' in summary
    assert 'annualized_return' in summary
    
    # Test with benchmark
    summary_with_bench = calculate_risk_metrics_summary(sample_returns, benchmark_returns)
    assert 'information_ratio' in summary_with_bench
    assert 'beta' in summary_with_bench
    assert 'alpha' in summary_with_bench
