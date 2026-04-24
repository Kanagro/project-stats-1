"""Unit tests for portfolio module."""

import pytest
import pandas as pd
import numpy as np
from src.portfolio import Portfolio


def test_portfolio_initialization():
    """Test portfolio initialization."""
    data = pd.DataFrame({'date': pd.date_range('2024-01-01', periods=10)})
    portfolio = Portfolio(data)
    
    assert portfolio.initial_capital == 100000
    assert len(portfolio.positions) == 0


def test_add_position():
    """Test adding a position to portfolio."""
    data = pd.DataFrame({'date': pd.date_range('2024-01-01', periods=10)})
    portfolio = Portfolio(data)
    
    portfolio.add_position('AAPL', 10, 150.0)
    
    assert 'AAPL' in portfolio.positions
    assert portfolio.positions['AAPL']['shares'] == 10
    assert portfolio.positions['AAPL']['purchase_price'] == 150.0


def test_get_current_value():
    """Test getting current portfolio value."""
    data = pd.DataFrame({'date': pd.date_range('2024-01-01', periods=10)})
    portfolio = Portfolio(data)
    
    portfolio.add_position('AAPL', 10, 150.0)
    portfolio.add_position('GOOGL', 5, 200.0)
    
    expected_value = (10 * 150.0) + (5 * 200.0)
    assert portfolio.get_current_value() == expected_value


def test_portfolio_summary():
    """Test portfolio summary."""
    data = pd.DataFrame({'date': pd.date_range('2024-01-01', periods=10)})
    portfolio = Portfolio(data, initial_capital=50000)
    
    portfolio.add_position('AAPL', 10, 150.0)
    
    summary = portfolio.summary()
    
    assert summary['initial_capital'] == 50000
    assert summary['num_positions'] == 1
    assert 'current_value' in summary
    assert 'total_return' in summary
