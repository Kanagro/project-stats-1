"""Unit tests for technical indicators module."""

import pytest
import pandas as pd
import numpy as np
from src.indicators import (
    simple_moving_average,
    exponential_moving_average,
    bollinger_bands,
    relative_strength_index,
    macd,
    stochastic_oscillator,
    average_true_range,
    on_balance_volume,
    rate_of_change,
    accumulation_distribution_line,
    calculate_indicators_summary,
)


@pytest.fixture
def price_series():
    """Create sample price series."""
    np.random.seed(42)
    prices = 100 * np.exp(np.cumsum(np.random.normal(0.0005, 0.02, 100)))
    return pd.Series(prices)


@pytest.fixture
def ohlcv_data():
    """Create sample OHLCV data."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100)
    
    close_prices = 100 * np.exp(np.cumsum(np.random.normal(0.0005, 0.02, 100)))
    high_prices = close_prices * (1 + np.abs(np.random.normal(0, 0.01, 100)))
    low_prices = close_prices * (1 - np.abs(np.random.normal(0, 0.01, 100)))
    volume = np.random.randint(1000000, 5000000, 100)
    
    return pd.DataFrame({
        'date': dates,
        'open': close_prices * 0.99,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volume
    }).set_index('date')


def test_simple_moving_average(price_series):
    """Test SMA calculation."""
    sma = simple_moving_average(price_series, window=20)
    
    assert isinstance(sma, pd.Series)
    assert len(sma) == len(price_series)
    assert sma.isna().sum() == 19  # First 19 values should be NaN
    assert not sma[19:].isna().any()  # No NaN after window


def test_exponential_moving_average(price_series):
    """Test EMA calculation."""
    ema = exponential_moving_average(price_series, window=20)
    
    assert isinstance(ema, pd.Series)
    assert len(ema) == len(price_series)
    assert ema.isna().sum() == 0  # EMA doesn't have NaN
    
    # EMA should follow prices but be smoother
    assert ema.std() < price_series.std()


def test_bollinger_bands(price_series):
    """Test Bollinger Bands calculation."""
    upper, middle, lower = bollinger_bands(price_series, window=20, num_std=2)
    
    assert isinstance(upper, pd.Series)
    assert isinstance(middle, pd.Series)
    assert isinstance(lower, pd.Series)
    
    assert len(upper) == len(price_series)
    # Upper band should be above middle, middle above lower
    assert (upper > middle).sum() > 0
    assert (middle > lower).sum() > 0


def test_relative_strength_index(price_series):
    """Test RSI calculation."""
    rsi = relative_strength_index(price_series, window=14)
    
    assert isinstance(rsi, pd.Series)
    assert len(rsi) == len(price_series)
    # RSI should be between 0 and 100
    valid_rsi = rsi.dropna()
    assert (valid_rsi >= 0).all()
    assert (valid_rsi <= 100).all()


def test_macd(price_series):
    """Test MACD calculation."""
    macd_line, signal_line, histogram = macd(price_series)
    
    assert isinstance(macd_line, pd.Series)
    assert isinstance(signal_line, pd.Series)
    assert isinstance(histogram, pd.Series)
    
    assert len(macd_line) == len(price_series)
    # Histogram should be MACD - Signal
    assert np.allclose(histogram, macd_line - signal_line, equal_nan=True)


def test_stochastic_oscillator(price_series):
    """Test Stochastic Oscillator calculation."""
    k_line, d_line = stochastic_oscillator(price_series, window=14)
    
    assert isinstance(k_line, pd.Series)
    assert isinstance(d_line, pd.Series)
    
    # Stochastic values should be between 0-100
    valid_k = k_line.dropna()
    valid_d = d_line.dropna()
    assert (valid_k >= 0).all()
    assert (valid_k <= 100).all()
    assert (valid_d >= 0).all()
    assert (valid_d <= 100).all()


def test_average_true_range(ohlcv_data):
    """Test ATR calculation."""
    atr = average_true_range(
        ohlcv_data['high'],
        ohlcv_data['low'],
        ohlcv_data['close'],
        window=14
    )
    
    assert isinstance(atr, pd.Series)
    assert len(atr) == len(ohlcv_data)
    assert (atr > 0).sum() > 0  # ATR should be positive


def test_on_balance_volume(ohlcv_data):
    """Test OBV calculation."""
    obv = on_balance_volume(ohlcv_data['close'], ohlcv_data['volume'])
    
    assert isinstance(obv, pd.Series)
    assert len(obv) == len(ohlcv_data)
    # OBV should generally increase over time (cumulative)
    assert obv.iloc[-1] != obv.iloc[0]


def test_rate_of_change(price_series):
    """Test ROC calculation."""
    roc = rate_of_change(price_series, window=12)
    
    assert isinstance(roc, pd.Series)
    assert len(roc) == len(price_series)
    assert roc.isna().sum() == 12  # First 12 values should be NaN


def test_accumulation_distribution_line(ohlcv_data):
    """Test A/D Line calculation."""
    ad = accumulation_distribution_line(
        ohlcv_data['high'],
        ohlcv_data['low'],
        ohlcv_data['close'],
        ohlcv_data['volume']
    )
    
    assert isinstance(ad, pd.Series)
    assert len(ad) == len(ohlcv_data)
    # A/D line is cumulative
    assert ad.iloc[-1] != ad.iloc[0]


def test_calculate_indicators_summary(ohlcv_data):
    """Test complete indicators summary calculation."""
    result = calculate_indicators_summary(ohlcv_data)
    
    assert isinstance(result, pd.DataFrame)
    # Check that all indicators are present
    indicators = [
        'SMA_20', 'SMA_50', 'EMA_12', 'EMA_26',
        'BB_Upper', 'BB_Middle', 'BB_Lower',
        'RSI_14', 'MACD', 'MACD_Signal', 'MACD_Hist',
        'Stoch_K', 'Stoch_D', 'ATR', 'OBV', 'ROC', 'AD'
    ]
    
    for indicator in indicators:
        assert indicator in result.columns
        assert len(result[indicator]) == len(ohlcv_data)
