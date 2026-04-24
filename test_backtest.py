"""Unit tests for backtesting module."""

import pytest
import pandas as pd
import numpy as np
from src.backtest import (
    Signal,
    Trade,
    Strategy,
    SimpleMovingAverageCrossover,
    RSIStrategy,
    MACDStrategy,
    Backtest,
    compare_strategies,
)


@pytest.fixture
def sample_data():
    """Create sample price data for backtesting."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=252)  # 1 year of daily data
    prices = 100 * np.exp(np.cumsum(np.random.normal(0.0005, 0.02, 252)))
    
    data = pd.DataFrame({
        'date': dates,
        'open': prices * 0.99,
        'high': prices * 1.01,
        'low': prices * 0.98,
        'close': prices,
        'volume': np.random.randint(1000000, 5000000, 252),
    })
    data.set_index('date', inplace=True)
    
    return data


@pytest.fixture
def trending_data():
    """Create uptrending data."""
    dates = pd.date_range('2024-01-01', periods=100)
    prices = 100 + np.arange(100) * 0.5  # Strong uptrend
    
    data = pd.DataFrame({
        'date': dates,
        'open': prices * 0.99,
        'high': prices * 1.01,
        'low': prices * 0.98,
        'close': prices,
        'volume': 1000000,
    })
    data.set_index('date', inplace=True)
    
    return data


def test_signal_enum():
    """Test Signal enum."""
    assert Signal.BUY.value == 1
    assert Signal.SELL.value == -1
    assert Signal.HOLD.value == 0


def test_trade_creation():
    """Test Trade creation."""
    date = pd.Timestamp('2024-01-01')
    trade = Trade(date, 100.0, Signal.BUY)
    
    assert trade.entry_date == date
    assert trade.entry_price == 100.0
    assert trade.entry_signal == Signal.BUY
    assert trade.pnl is None


def test_trade_close():
    """Test closing a trade."""
    entry_date = pd.Timestamp('2024-01-01')
    exit_date = pd.Timestamp('2024-01-05')
    trade = Trade(entry_date, 100.0, Signal.BUY)
    
    trade.close_trade(exit_date, 105.0, Signal.SELL)
    
    assert trade.exit_date == exit_date
    assert trade.exit_price == 105.0
    assert trade.pnl == 5.0
    assert trade.pnl_pct == 0.05


def test_sma_strategy_signals(sample_data):
    """Test SMA crossover strategy."""
    strategy = SimpleMovingAverageCrossover(fast_window=10, slow_window=20)
    signals = strategy.generate_signals(sample_data)
    
    assert isinstance(signals, pd.Series)
    assert len(signals) == len(sample_data)
    assert all(s in [Signal.BUY, Signal.SELL, Signal.HOLD] for s in signals)


def test_rsi_strategy_signals(sample_data):
    """Test RSI strategy."""
    strategy = RSIStrategy(rsi_window=14, oversold=30, overbought=70)
    signals = strategy.generate_signals(sample_data)
    
    assert isinstance(signals, pd.Series)
    assert len(signals) == len(sample_data)
    assert all(s in [Signal.BUY, Signal.SELL, Signal.HOLD] for s in signals)


def test_macd_strategy_signals(sample_data):
    """Test MACD strategy."""
    strategy = MACDStrategy(fast=12, slow=26, signal=9)
    signals = strategy.generate_signals(sample_data)
    
    assert isinstance(signals, pd.Series)
    assert len(signals) == len(sample_data)
    assert all(s in [Signal.BUY, Signal.SELL, Signal.HOLD] for s in signals)


def test_backtest_initialization():
    """Test Backtest initialization."""
    strategy = SimpleMovingAverageCrossover()
    backtest = Backtest(strategy, initial_capital=50000)
    
    assert backtest.initial_capital == 50000
    assert backtest.capital == 50000
    assert backtest.position == 0


def test_backtest_run(sample_data):
    """Test running backtest."""
    strategy = SimpleMovingAverageCrossover()
    backtest = Backtest(strategy)
    backtest.run(sample_data)
    
    assert len(backtest.equity_curve) == len(sample_data)
    assert len(backtest.dates) == len(sample_data)
    assert backtest.equity_curve[-1] > 0


def test_backtest_get_results(sample_data):
    """Test getting backtest results."""
    strategy = SimpleMovingAverageCrossover()
    backtest = Backtest(strategy)
    backtest.run(sample_data)
    
    results = backtest.get_results()
    
    assert 'total_return' in results
    assert 'sharpe_ratio' in results
    assert 'max_drawdown' in results
    assert 'total_trades' in results
    assert 'win_rate' in results
    assert 'profit_factor' in results


def test_backtest_get_equity_curve(sample_data):
    """Test getting equity curve."""
    strategy = SimpleMovingAverageCrossover()
    backtest = Backtest(strategy)
    backtest.run(sample_data)
    
    equity_curve = backtest.get_equity_curve()
    
    assert isinstance(equity_curve, pd.DataFrame)
    assert 'date' in equity_curve.columns
    assert 'equity' in equity_curve.columns
    assert len(equity_curve) == len(sample_data)


def test_backtest_get_trades(sample_data):
    """Test getting closed trades."""
    strategy = SimpleMovingAverageCrossover()
    backtest = Backtest(strategy)
    backtest.run(sample_data)
    
    trades = backtest.get_trades()
    
    assert isinstance(trades, pd.DataFrame)
    if len(trades) > 0:
        assert 'entry_date' in trades.columns
        assert 'exit_date' in trades.columns
        assert 'pnl' in trades.columns


def test_backtest_with_commission(sample_data):
    """Test backtest with commission."""
    strategy = SimpleMovingAverageCrossover()
    backtest_no_commission = Backtest(strategy, commission=0)
    backtest_with_commission = Backtest(strategy, commission=0.001)
    
    backtest_no_commission.run(sample_data)
    backtest_with_commission.run(sample_data)
    
    # Backtest with commission should have lower final equity
    results_no_comm = backtest_no_commission.get_results()
    results_comm = backtest_with_commission.get_results()
    
    assert results_no_comm['final_equity'] >= results_comm['final_equity']


def test_backtest_with_slippage(sample_data):
    """Test backtest with slippage."""
    strategy = SimpleMovingAverageCrossover()
    backtest_no_slippage = Backtest(strategy, slippage=0)
    backtest_with_slippage = Backtest(strategy, slippage=0.001)
    
    backtest_no_slippage.run(sample_data)
    backtest_with_slippage.run(sample_data)
    
    # Both should still show some returns (prices trending up in sample)
    results_no_slip = backtest_no_slippage.get_results()
    results_slip = backtest_with_slippage.get_results()
    
    assert results_no_slip['total_trades'] == results_slip['total_trades']


def test_backtest_on_trending_data(trending_data):
    """Test backtest on strongly trending data."""
    strategy = SimpleMovingAverageCrossover(fast_window=5, slow_window=10)
    backtest = Backtest(strategy)
    backtest.run(trending_data)
    
    results = backtest.get_results()
    
    # Should make money on strong uptrend
    assert results['total_return'] > 0
    assert results['max_drawdown'] >= -1.0  # Drawdown should be at most -100%


def test_compare_strategies(sample_data):
    """Test comparing multiple strategies."""
    strategies = [
        SimpleMovingAverageCrossover(fast_window=10, slow_window=20),
        RSIStrategy(),
        MACDStrategy(),
    ]
    
    results = compare_strategies(sample_data, strategies)
    
    assert len(results) == 3
    for strategy_name, strategy_results in results.items():
        assert 'total_return' in strategy_results
        assert 'sharpe_ratio' in strategy_results
        assert 'total_trades' in strategy_results


def test_strategy_name():
    """Test strategy names."""
    sma_strategy = SimpleMovingAverageCrossover()
    rsi_strategy = RSIStrategy()
    macd_strategy = MACDStrategy()
    
    assert sma_strategy.name == "SMA Crossover"
    assert rsi_strategy.name == "RSI Strategy"
    assert macd_strategy.name == "MACD Strategy"


def test_backtest_metrics_sanity(sample_data):
    """Test that backtest metrics are reasonable."""
    strategy = SimpleMovingAverageCrossover()
    backtest = Backtest(strategy)
    backtest.run(sample_data)
    
    results = backtest.get_results()
    
    # Basic sanity checks
    assert results['final_equity'] > 0
    assert -1.0 <= results['max_drawdown'] <= 0
    assert 0 <= results['win_rate'] <= 1
    assert results['profit_factor'] >= 0
    assert results['total_trades'] >= 0
