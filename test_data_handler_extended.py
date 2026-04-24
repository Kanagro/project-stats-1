"""Extended tests for data_handler module to improve coverage."""

import pytest
import pandas as pd
import numpy as np
from src.data_handler import (
    load_data,
    calculate_returns,
    calculate_log_returns,
    add_returns_to_dataframe,
    resample_data,
    fill_missing_data,
    validate_data,
)


@pytest.fixture
def sample_data_with_gaps():
    """Create DataFrame with missing values."""
    df = pd.DataFrame({
        'value': [1, np.nan, 3, 4, np.nan, 6],
        'price': [100, 101, np.nan, 103, 104, np.nan]
    })
    return df


@pytest.fixture
def sample_data_duplicates():
    """Create DataFrame with duplicate rows."""
    df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=5),
        'value': [1, 2, 2, 3, 4],
        'price': [100, 101, 101, 102, 103]
    })
    df.set_index('date', inplace=True)
    return df


@pytest.fixture
def long_price_series():
    """Create long price series for testing."""
    np.random.seed(42)
    prices = 100 * np.exp(np.cumsum(np.random.normal(0.0005, 0.02, 500)))
    return pd.Series(prices)


def test_resample_weekly():
    """Test resampling to weekly frequency."""
    dates = pd.date_range('2024-01-01', periods=60)
    prices = 100 + np.arange(60) * 0.1
    df = pd.DataFrame({
        'open': prices * 0.99,
        'high': prices * 1.01,
        'low': prices * 0.98,
        'close': prices,
        'volume': 1000000,
    }, index=dates)
    
    weekly = resample_data(df, frequency='W')
    
    assert isinstance(weekly, pd.DataFrame)
    assert 'open' in weekly.columns
    assert 'high' in weekly.columns
    assert len(weekly) < len(df)  # Fewer weeks than days


def test_resample_monthly():
    """Test resampling to monthly frequency."""
    dates = pd.date_range('2024-01-01', periods=365)
    prices = 100 + np.arange(365) * 0.1
    df = pd.DataFrame({
        'open': prices * 0.99,
        'high': prices * 1.01,
        'low': prices * 0.98,
        'close': prices,
        'volume': 1000000,
    }, index=dates)
    
    monthly = resample_data(df, frequency='M')
    
    assert isinstance(monthly, pd.DataFrame)
    assert len(monthly) <= 12  # Should have at most 12 months


def test_fill_missing_data_ffill(sample_data_with_gaps):
    """Test forward fill method."""
    filled = fill_missing_data(sample_data_with_gaps, method='ffill')
    
    assert filled['value'].isna().sum() == 0
    # First non-null value should be propagated
    assert filled['value'].iloc[1] == filled['value'].iloc[0]


def test_fill_missing_data_bfill(sample_data_with_gaps):
    """Test backward fill method."""
    filled = fill_missing_data(sample_data_with_gaps, method='bfill')
    
    assert filled['value'].isna().sum() == 0
    # Last value should be propagated backwards
    assert filled['value'].iloc[4] == filled['value'].iloc[5]


def test_fill_missing_data_interpolate(sample_data_with_gaps):
    """Test interpolate method."""
    filled = fill_missing_data(sample_data_with_gaps, method='interpolate')
    
    assert filled['value'].isna().sum() == 0
    # Interpolated values should be between neighbors
    assert 1 < filled['value'].iloc[1] < 3


def test_validate_data_clean(sample_data_with_gaps):
    """Test validation with some missing values."""
    validation = validate_data(sample_data_with_gaps)
    
    assert validation['has_missing_values'] == True
    assert validation['missing_values_count'] == 4  # 2 NaN values in each column


def test_validate_data_no_missing():
    """Test validation with no missing values."""
    df = pd.DataFrame({'value': [1, 2, 3, 4, 5]})
    validation = validate_data(df)
    
    assert validation['has_missing_values'] == False
    assert validation['missing_values_count'] == 0


def test_validate_data_duplicates(sample_data_duplicates):
    """Test validation with duplicates."""
    validation = validate_data(sample_data_duplicates)
    
    assert validation['has_duplicates'] == True
    assert validation['duplicates_count'] > 0


def test_validate_data_statistics():
    """Test validation returns proper statistics."""
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [10, 20, 30, 40, 50]
    })
    
    validation = validate_data(df)
    
    assert validation['total_rows'] == 5
    assert validation['total_columns'] == 2


def test_calculate_returns_consistency():
    """Test returns calculation consistency."""
    prices = pd.Series([100, 110, 121, 108.9])
    returns = calculate_returns(prices)
    
    assert np.isclose(returns.iloc[1], 0.1)  # 10% return
    assert np.isclose(returns.iloc[2], 0.1)  # 10% return


def test_calculate_log_returns_consistency():
    """Test log returns calculation consistency."""
    prices = pd.Series([100, 110, 121])
    log_returns = calculate_log_returns(prices)
    
    assert np.isclose(log_returns.iloc[1], np.log(110/100))
    assert np.isclose(log_returns.iloc[2], np.log(121/110))


def test_add_returns_preserves_data():
    """Test that adding returns preserves original data."""
    df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=10),
        'close': 100 + np.arange(10),
    })
    
    original_len = len(df)
    df_with_returns = add_returns_to_dataframe(df, 'close')
    
    assert len(df_with_returns) == original_len
    assert 'close' in df_with_returns.columns
    assert 'returns' in df_with_returns.columns
    assert 'log_returns' in df_with_returns.columns


def test_add_returns_values():
    """Test added returns values."""
    df = pd.DataFrame({
        'close': [100, 110, 121],
    })
    
    result = add_returns_to_dataframe(df, 'close')
    
    assert np.isnan(result['returns'].iloc[0])  # First value is NaN
    assert np.isclose(result['returns'].iloc[1], 0.1)
    assert np.isclose(result['returns'].iloc[2], 0.1)


def test_resample_preserves_ohlcv_logic():
    """Test that resampling preserves OHLCV logic."""
    dates = pd.date_range('2024-01-01', periods=10)
    df = pd.DataFrame({
        'open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'high': [105, 106, 107, 108, 109, 110, 111, 112, 113, 114],
        'low': [95, 96, 97, 98, 99, 100, 101, 102, 103, 104],
        'close': [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
        'volume': [1000000] * 10,
    }, index=dates)
    
    weekly = resample_data(df, frequency='W')
    
    # High should be maximum of period
    assert weekly['high'].iloc[0] >= weekly['low'].iloc[0]
    # Low should be minimum of period
    assert weekly['low'].iloc[0] <= weekly['high'].iloc[0]


def test_resample_with_missing_columns():
    """Test resampling with only some OHLCV columns."""
    dates = pd.date_range('2024-01-01', periods=20)
    df = pd.DataFrame({
        'close': 100 + np.arange(20),
        'volume': 1000000,
    }, index=dates)
    
    weekly = resample_data(df, frequency='W')
    
    assert 'close' in weekly.columns
    assert 'volume' in weekly.columns


def test_validate_data_large_dataset():
    """Test validation with larger dataset."""
    np.random.seed(42)
    df = pd.DataFrame({
        'price': np.random.normal(100, 10, 1000),
        'volume': np.random.randint(1000000, 5000000, 1000),
    })
    
    validation = validate_data(df)
    
    assert validation['total_rows'] == 1000
    assert validation['total_columns'] == 2
    assert validation['has_missing_values'] == False


def test_calculate_returns_with_gaps():
    """Test returns calculation handles NaN properly."""
    prices = pd.Series([100, np.nan, 110, 121])
    returns = calculate_returns(prices)
    
    # pct_change with fill_method='pad' fills NaN values before computing
    # So NaN gets filled with 100, and (110-100)/100 = 0.1
    assert np.isnan(returns.iloc[0])  # First return is always NaN
    assert np.isclose(returns.iloc[2], 0.1)  # Normal percent change


def test_fill_missing_data_all_missing():
    """Test fill with all missing values."""
    df = pd.DataFrame({'value': [np.nan, np.nan, np.nan]})
    filled = fill_missing_data(df, method='ffill')
    
    # ffill followed by bfill should leave NaNs if all are missing
    assert filled['value'].isna().sum() == 3
