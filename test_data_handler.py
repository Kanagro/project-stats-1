"""Unit tests for data handler module with Yahoo Finance integration."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.data_handler import (
    load_data,
    fetch_yahoo_data,
    fetch_multiple_tickers,
    combine_ticker_data,
    calculate_returns,
    calculate_log_returns,
    add_returns_to_dataframe,
    resample_data,
    fill_missing_data,
    validate_data,
)


@pytest.fixture
def sample_csv_path():
    """Return path to sample data CSV."""
    return 'data/sample_data.csv'


@pytest.fixture
def sample_dataframe():
    """Create sample OHLCV DataFrame."""
    dates = pd.date_range('2024-01-01', periods=30)
    np.random.seed(42)
    close_prices = 100 * np.exp(np.cumsum(np.random.normal(0.0005, 0.02, 30)))
    
    return pd.DataFrame({
        'date': dates,
        'open': close_prices * 0.99,
        'high': close_prices * 1.01,
        'low': close_prices * 0.98,
        'close': close_prices,
        'volume': np.random.randint(1000000, 5000000, 30)
    }).set_index('date')


def test_load_data(sample_csv_path):
    """Test loading data from CSV."""
    df = load_data(sample_csv_path)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert 'date' in df.columns


def test_load_data_file_not_found():
    """Test loading non-existent file."""
    with pytest.raises(FileNotFoundError):
        load_data('data/nonexistent.csv')


def test_calculate_returns():
    """Test returns calculation."""
    prices = pd.Series([100, 101, 102, 101, 103])
    returns = calculate_returns(prices)
    
    assert isinstance(returns, pd.Series)
    assert len(returns) == len(prices)
    assert returns.iloc[0] != returns.iloc[0]  # First value is NaN
    assert np.isclose(returns.iloc[1], 0.01, rtol=0.01)  # Second value ~1%


def test_calculate_log_returns():
    """Test log returns calculation."""
    prices = pd.Series([100, 101, 102, 101, 103])
    log_returns = calculate_log_returns(prices)
    
    assert isinstance(log_returns, pd.Series)
    assert len(log_returns) == len(prices)
    assert np.isnan(log_returns.iloc[0])  # First value is NaN


def test_add_returns_to_dataframe(sample_dataframe):
    """Test adding returns columns to DataFrame."""
    result = add_returns_to_dataframe(sample_dataframe, 'close')
    
    assert 'returns' in result.columns
    assert 'log_returns' in result.columns
    assert len(result) == len(sample_dataframe)


def test_resample_data(sample_dataframe):
    """Test resampling OHLCV data."""
    resampled = resample_data(sample_dataframe, frequency='W')
    
    assert isinstance(resampled, pd.DataFrame)
    assert 'open' in resampled.columns
    assert 'high' in resampled.columns
    assert 'low' in resampled.columns
    assert 'close' in resampled.columns
    assert len(resampled) < len(sample_dataframe)


def test_fill_missing_data():
    """Test filling missing data."""
    df = pd.DataFrame({
        'value': [1, np.nan, 3, np.nan, 5]
    })
    
    # Test forward fill
    filled_ffill = fill_missing_data(df, method='ffill')
    assert filled_ffill['value'].isna().sum() == 0
    
    # Test backward fill
    filled_bfill = fill_missing_data(df, method='bfill')
    assert filled_bfill['value'].isna().sum() == 0
    
    # Test interpolate
    filled_interp = fill_missing_data(df, method='interpolate')
    assert filled_interp['value'].isna().sum() == 0


def test_fill_missing_data_invalid_method():
    """Test fill_missing_data with invalid method."""
    df = pd.DataFrame({'value': [1, np.nan, 3]})
    
    with pytest.raises(ValueError):
        fill_missing_data(df, method='invalid')


def test_validate_data(sample_dataframe):
    """Test data validation."""
    validation = validate_data(sample_dataframe)
    
    assert isinstance(validation, dict)
    assert 'has_missing_values' in validation
    assert 'missing_values_count' in validation
    assert 'has_duplicates' in validation
    assert 'duplicates_count' in validation
    assert 'total_rows' in validation
    assert 'total_columns' in validation


def test_validate_data_with_missing_values():
    """Test validation with missing values."""
    df = pd.DataFrame({
        'A': [1, 2, np.nan, 4],
        'B': [1, np.nan, 3, 4]
    })
    
    validation = validate_data(df)
    assert validation['has_missing_values'] == True
    assert validation['missing_values_count'] == 2


@pytest.mark.integration
def test_fetch_yahoo_data():
    """Test fetching real-time data from Yahoo Finance."""
    # Use a short date range to avoid rate limiting
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
    
    df = fetch_yahoo_data('AAPL', start_date=start_date, end_date=end_date)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert 'date' in df.columns
    assert 'close' in df.columns
    assert 'volume' in df.columns
    assert df['ticker'].iloc[0] == 'AAPL'


@pytest.mark.integration
def test_fetch_yahoo_data_invalid_ticker():
    """Test fetching data with invalid ticker."""
    with pytest.raises(ValueError):
        fetch_yahoo_data('INVALID_TICKER_XYZ')


@pytest.mark.integration
def test_fetch_multiple_tickers():
    """Test fetching data for multiple tickers."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
    
    tickers = ['AAPL', 'GOOGL', 'MSFT']
    data_dict = fetch_multiple_tickers(tickers, start_date=start_date, end_date=end_date)
    
    assert isinstance(data_dict, dict)
    assert len(data_dict) > 0


@pytest.mark.integration
def test_combine_ticker_data():
    """Test combining data from multiple tickers."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
    
    tickers = ['AAPL', 'GOOGL']
    data_dict = fetch_multiple_tickers(tickers, start_date=start_date, end_date=end_date)
    
    if len(data_dict) >= 2:
        combined = combine_ticker_data(data_dict, column='close')
        
        assert isinstance(combined, pd.DataFrame)
        assert len(combined.columns) >= 1
        assert len(combined) > 0
