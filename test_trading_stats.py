"""Expanded unit tests for trading stats module."""

import pytest
import pandas as pd
import numpy as np
from src.trading_stats import (
    calculate_win_rate,
    calculate_profit_factor,
    analyze_trades,
)


@pytest.fixture
def sample_trades():
    """Create sample trade data."""
    return pd.DataFrame({
        'pnl': [100, -50, 200, -30, 150, -20, 80, -10],
    })


@pytest.fixture
def all_winning_trades():
    """Create all winning trades."""
    return pd.DataFrame({
        'pnl': [100, 50, 200, 150, 80, 120],
    })


@pytest.fixture
def all_losing_trades():
    """Create all losing trades."""
    return pd.DataFrame({
        'pnl': [-100, -50, -200, -150, -80, -120],
    })


@pytest.fixture
def empty_trades():
    """Create empty trades DataFrame."""
    return pd.DataFrame({
        'pnl': [],
    })


def test_calculate_win_rate(sample_trades):
    """Test win rate calculation."""
    win_rate = calculate_win_rate(sample_trades)
    
    assert isinstance(win_rate, float)
    assert 0 <= win_rate <= 1
    # 4 winning trades out of 8 = 50%
    assert np.isclose(win_rate, 0.5)


def test_calculate_win_rate_all_winning(all_winning_trades):
    """Test win rate with all winning trades."""
    win_rate = calculate_win_rate(all_winning_trades)
    
    assert win_rate == 1.0


def test_calculate_win_rate_all_losing(all_losing_trades):
    """Test win rate with all losing trades."""
    win_rate = calculate_win_rate(all_losing_trades)
    
    assert win_rate == 0.0


def test_calculate_win_rate_empty(empty_trades):
    """Test win rate with empty trades."""
    win_rate = calculate_win_rate(empty_trades)
    
    assert win_rate == 0.0


def test_calculate_profit_factor(sample_trades):
    """Test profit factor calculation."""
    pf = calculate_profit_factor(sample_trades)
    
    assert isinstance(pf, float)
    assert pf > 0
    # Gross profit: 100 + 200 + 150 + 80 = 530
    # Gross loss: 50 + 30 + 20 + 10 = 110
    # PF: 530 / 110 ≈ 4.82
    assert np.isclose(pf, 530 / 110)


def test_calculate_profit_factor_all_winning(all_winning_trades):
    """Test profit factor with all winning trades."""
    pf = calculate_profit_factor(all_winning_trades)
    
    assert pf == float('inf')


def test_calculate_profit_factor_all_losing(all_losing_trades):
    """Test profit factor with all losing trades."""
    pf = calculate_profit_factor(all_losing_trades)
    
    assert pf == 0


def test_calculate_profit_factor_empty(empty_trades):
    """Test profit factor with empty trades."""
    pf = calculate_profit_factor(empty_trades)
    
    assert pf == 0


def test_analyze_trades(sample_trades):
    """Test comprehensive trade analysis."""
    analysis = analyze_trades(sample_trades)
    
    assert isinstance(analysis, dict)
    assert 'total_trades' in analysis
    assert 'win_rate' in analysis
    assert 'profit_factor' in analysis
    assert 'avg_win' in analysis
    assert 'avg_loss' in analysis
    assert 'total_pnl' in analysis
    
    assert analysis['total_trades'] == 8
    assert 0 <= analysis['win_rate'] <= 1
    assert analysis['profit_factor'] >= 0


def test_analyze_trades_values(sample_trades):
    """Test trade analysis values."""
    analysis = analyze_trades(sample_trades)
    
    # Total PnL: 100 - 50 + 200 - 30 + 150 - 20 + 80 - 10 = 420
    assert analysis['total_pnl'] == 420
    
    # Average win: (100 + 200 + 150 + 80) / 4 = 132.5
    assert np.isclose(analysis['avg_win'], 132.5)
    
    # Average loss: (-50 - 30 - 20 - 10) / 4 = -27.5
    assert np.isclose(analysis['avg_loss'], -27.5)


def test_analyze_trades_all_winning(all_winning_trades):
    """Test analysis with all winning trades."""
    analysis = analyze_trades(all_winning_trades)
    
    assert analysis['win_rate'] == 1.0
    assert analysis['profit_factor'] == float('inf')
    # When there are no losses, avg_loss should be NaN
    assert np.isnan(analysis['avg_loss']) or analysis['avg_loss'] == 0


def test_analyze_trades_all_losing(all_losing_trades):
    """Test analysis with all losing trades."""
    analysis = analyze_trades(all_losing_trades)
    
    assert analysis['win_rate'] == 0.0
    assert analysis['profit_factor'] == 0
    # When there are no wins, avg_win should be NaN
    assert np.isnan(analysis['avg_win']) or analysis['avg_win'] == 0


def test_analyze_trades_empty(empty_trades):
    """Test analysis with empty trades."""
    analysis = analyze_trades(empty_trades)
    
    assert analysis['total_trades'] == 0
    assert analysis['win_rate'] == 0.0


def test_calculate_win_rate_single_trade():
    """Test win rate with single trade."""
    single_win = pd.DataFrame({'pnl': [100]})
    assert calculate_win_rate(single_win) == 1.0
    
    single_loss = pd.DataFrame({'pnl': [-100]})
    assert calculate_win_rate(single_loss) == 0.0


def test_calculate_profit_factor_break_even():
    """Test profit factor at break-even."""
    trades = pd.DataFrame({'pnl': [100, -100]})
    pf = calculate_profit_factor(trades)
    
    assert pf == 1.0


def test_analyze_trades_mixed_outcomes():
    """Test analysis with various mixed outcomes."""
    trades = pd.DataFrame({
        'pnl': [50, 100, -25, 75, -50, 200, -10]
    })
    
    analysis = analyze_trades(trades)
    
    # 4 winning trades out of 7 ≈ 57.14%
    assert np.isclose(analysis['win_rate'], 4/7)
    
    # Total PnL: 50 + 100 - 25 + 75 - 50 + 200 - 10 = 340
    assert analysis['total_pnl'] == 340
    
    # Check positive total PnL
    assert analysis['total_pnl'] > 0
