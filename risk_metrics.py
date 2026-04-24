"""Risk metrics calculation functions."""

import numpy as np
import pandas as pd
from scipy import stats


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sharpe ratio.
    
    Args:
        returns: Series of returns
        risk_free_rate: Annual risk-free rate (default 2%)
        
    Returns:
        Sharpe ratio
    """
    excess_returns = returns - risk_free_rate / 252
    return np.sqrt(252) * excess_returns.mean() / excess_returns.std()


def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.02, target_return: float = 0.0) -> float:
    """
    Calculate Sortino ratio (focuses on downside volatility).
    
    Args:
        returns: Series of returns
        risk_free_rate: Annual risk-free rate (default 2%)
        target_return: Target return threshold (default 0%)
        
    Returns:
        Sortino ratio
    """
    excess_returns = returns - risk_free_rate / 252
    downside_returns = returns[returns < target_return]
    downside_std = downside_returns.std()
    
    if downside_std == 0:
        return np.inf if excess_returns.mean() > 0 else 0
    
    return np.sqrt(252) * excess_returns.mean() / downside_std


def calculate_volatility(returns: pd.Series, annualized: bool = True) -> float:
    """
    Calculate volatility (standard deviation).
    
    Args:
        returns: Series of returns
        annualized: If True, annualize the volatility
        
    Returns:
        Volatility
    """
    volatility = returns.std()
    if annualized:
        volatility *= np.sqrt(252)
    return volatility


def calculate_var(returns: pd.Series, confidence_level: float = 0.95) -> float:
    """
    Calculate Value at Risk (VaR).
    
    Args:
        returns: Series of returns
        confidence_level: Confidence level (default 95%)
        
    Returns:
        Value at Risk
    """
    return returns.quantile(1 - confidence_level)


def calculate_cvar(returns: pd.Series, confidence_level: float = 0.95) -> float:
    """
    Calculate Conditional Value at Risk (Expected Shortfall).
    
    Args:
        returns: Series of returns
        confidence_level: Confidence level (default 95%)
        
    Returns:
        Conditional Value at Risk
    """
    var = calculate_var(returns, confidence_level)
    return returns[returns <= var].mean()


def calculate_max_drawdown(returns: pd.Series) -> float:
    """
    Calculate maximum drawdown.
    
    Args:
        returns: Series of returns
        
    Returns:
        Maximum drawdown
    """
    cumulative_returns = (1 + returns).cumprod()
    running_max = cumulative_returns.expanding().max()
    drawdown = (cumulative_returns - running_max) / running_max
    return drawdown.min()


def calculate_calmar_ratio(returns: pd.Series) -> float:
    """
    Calculate Calmar ratio (annualized return / max drawdown).
    
    Args:
        returns: Series of returns
        
    Returns:
        Calmar ratio
    """
    annualized_return = returns.mean() * 252
    max_drawdown = calculate_max_drawdown(returns)
    
    if max_drawdown == 0:
        return np.inf if annualized_return > 0 else 0
    
    return annualized_return / abs(max_drawdown)


def calculate_information_ratio(returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """
    Calculate Information ratio (excess return / tracking error).
    
    Args:
        returns: Series of portfolio returns
        benchmark_returns: Series of benchmark returns
        
    Returns:
        Information ratio
    """
    excess_returns = returns - benchmark_returns
    tracking_error = excess_returns.std()
    
    if tracking_error == 0:
        return np.inf if excess_returns.mean() > 0 else 0
    
    return np.sqrt(252) * excess_returns.mean() / tracking_error


def calculate_correlation_matrix(price_data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate correlation matrix for assets.
    
    Args:
        price_data: DataFrame with price columns for each asset
        
    Returns:
        Correlation matrix
    """
    returns = price_data.pct_change().dropna()
    return returns.corr()


def calculate_beta(returns: pd.Series, market_returns: pd.Series) -> float:
    """
    Calculate beta (systematic risk).
    
    Args:
        returns: Series of portfolio/asset returns
        market_returns: Series of market returns
        
    Returns:
        Beta value
    """
    covariance = np.cov(returns, market_returns)[0, 1]
    market_variance = np.var(market_returns)
    
    if market_variance == 0:
        return 0
    
    return covariance / market_variance


def calculate_alpha(returns: pd.Series, market_returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    Calculate Jensen's alpha (excess return after adjusting for systematic risk).
    
    Args:
        returns: Series of portfolio returns
        market_returns: Series of market returns
        risk_free_rate: Annual risk-free rate (default 2%)
        
    Returns:
        Alpha value
    """
    beta = calculate_beta(returns, market_returns)
    portfolio_return = returns.mean() * 252
    market_return = market_returns.mean() * 252
    
    expected_return = risk_free_rate + beta * (market_return - risk_free_rate)
    return portfolio_return - expected_return


def calculate_risk_metrics_summary(returns: pd.Series, benchmark_returns: pd.Series = None) -> dict:
    """
    Calculate comprehensive risk metrics summary.
    
    Args:
        returns: Series of portfolio returns
        benchmark_returns: Series of benchmark returns (optional)
        
    Returns:
        Dictionary with all risk metrics
    """
    metrics = {
        'sharpe_ratio': calculate_sharpe_ratio(returns),
        'sortino_ratio': calculate_sortino_ratio(returns),
        'volatility': calculate_volatility(returns),
        'var_95': calculate_var(returns, 0.95),
        'cvar_95': calculate_cvar(returns, 0.95),
        'max_drawdown': calculate_max_drawdown(returns),
        'calmar_ratio': calculate_calmar_ratio(returns),
        'annualized_return': returns.mean() * 252,
    }
    
    if benchmark_returns is not None:
        metrics['information_ratio'] = calculate_information_ratio(returns, benchmark_returns)
        metrics['beta'] = calculate_beta(returns, benchmark_returns)
        metrics['alpha'] = calculate_alpha(returns, benchmark_returns)
    
    return metrics
