"""Data loading and processing utilities for financial data."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime, timedelta

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False


def load_data(filepath: str) -> pd.DataFrame:
    """
    Load financial data from a CSV file.
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        DataFrame with financial data
    """
    if not Path(filepath).exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")
    
    df = pd.read_csv(filepath, parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)
    return df


def fetch_yahoo_data(
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interval: str = '1d'
) -> pd.DataFrame:
    """
    Fetch real-time data from Yahoo Finance.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
        start_date: Start date (format: 'YYYY-MM-DD'). Default: 1 year ago
        end_date: End date (format: 'YYYY-MM-DD'). Default: today
        interval: Data interval ('1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo')
        
    Returns:
        DataFrame with OHLCV data
        
    Raises:
        ImportError: If yfinance is not installed
        ValueError: If ticker is invalid
    """
    if not HAS_YFINANCE:
        raise ImportError("yfinance is required. Install with: pip install yfinance")
    
    # Set default dates
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    try:
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval, progress=False)
        
        if data.empty:
            raise ValueError(f"No data found for ticker: {ticker}")
        
        # Reset index to have date as a column
        data.reset_index(inplace=True)
        
        # Flatten column names if MultiIndex (for single ticker, we shouldn't have MultiIndex)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        # Convert to lowercase
        data.columns = [col.lower() if isinstance(col, str) else col for col in data.columns]
        
        # Rename columns for consistency
        rename_map = {
            'date': 'date',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'adj close': 'adj_close',
            'volume': 'volume'
        }
        data = data.rename(columns=rename_map)
        
        # Add ticker column
        data['ticker'] = ticker
        
        # Reorder columns
        cols = ['date', 'ticker', 'open', 'high', 'low', 'close', 'adj_close', 'volume']
        data = data[[col for col in cols if col in data.columns]]
        
        return data
        
    except Exception as e:
        raise ValueError(f"Error fetching data for {ticker}: {str(e)}")


def fetch_multiple_tickers(
    tickers: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interval: str = '1d'
) -> Dict[str, pd.DataFrame]:
    """
    Fetch data for multiple tickers from Yahoo Finance.
    
    Args:
        tickers: List of stock ticker symbols
        start_date: Start date (format: 'YYYY-MM-DD')
        end_date: End date (format: 'YYYY-MM-DD')
        interval: Data interval
        
    Returns:
        Dictionary with ticker as key and DataFrame as value
    """
    data_dict = {}
    
    for ticker in tickers:
        try:
            data_dict[ticker] = fetch_yahoo_data(ticker, start_date, end_date, interval)
        except Exception as e:
            print(f"Warning: Could not fetch data for {ticker}: {str(e)}")
    
    return data_dict


def combine_ticker_data(data_dict: Dict[str, pd.DataFrame], column: str = 'close') -> pd.DataFrame:
    """
    Combine price data from multiple tickers into a single DataFrame.
    
    Args:
        data_dict: Dictionary of DataFrames from fetch_multiple_tickers
        column: Which column to extract ('open', 'high', 'low', 'close', 'volume')
        
    Returns:
        DataFrame with dates as index and tickers as columns
    """
    combined = pd.DataFrame()
    
    for ticker, df in data_dict.items():
        if 'date' in df.columns:
            combined[ticker] = df.set_index('date')[column]
        else:
            combined[ticker] = df[column]
    
    return combined.dropna()


def calculate_returns(prices: pd.Series) -> pd.Series:
    """
    Calculate simple returns from price data.
    
    Args:
        prices: Series of prices
        
    Returns:
        Series of returns
    """
    return prices.pct_change()


def calculate_log_returns(prices: pd.Series) -> pd.Series:
    """
    Calculate logarithmic returns from price data.
    
    Args:
        prices: Series of prices
        
    Returns:
        Series of log returns
    """
    return np.log(prices / prices.shift(1))


def add_returns_to_dataframe(df: pd.DataFrame, price_column: str = 'close') -> pd.DataFrame:
    """
    Add return columns to a DataFrame.
    
    Args:
        df: DataFrame with price data
        price_column: Name of the price column
        
    Returns:
        DataFrame with added 'returns' and 'log_returns' columns
    """
    df = df.copy()
    df['returns'] = calculate_returns(df[price_column])
    df['log_returns'] = calculate_log_returns(df[price_column])
    return df


def resample_data(df: pd.DataFrame, frequency: str = 'W') -> pd.DataFrame:
    """
    Resample OHLCV data to different frequency.
    
    Args:
        df: DataFrame with OHLCV data (must have datetime index)
        frequency: Frequency code ('D', 'W', 'M', 'Q', 'Y')
        
    Returns:
        Resampled DataFrame
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        if 'date' in df.columns:
            df = df.set_index('date')
        else:
            raise ValueError("DataFrame must have datetime index or 'date' column")
    
    resampled = pd.DataFrame()
    
    if 'open' in df.columns:
        resampled['open'] = df['open'].resample(frequency).first()
    if 'high' in df.columns:
        resampled['high'] = df['high'].resample(frequency).max()
    if 'low' in df.columns:
        resampled['low'] = df['low'].resample(frequency).min()
    if 'close' in df.columns:
        resampled['close'] = df['close'].resample(frequency).last()
    if 'volume' in df.columns:
        resampled['volume'] = df['volume'].resample(frequency).sum()
    
    return resampled.dropna()


def fill_missing_data(df: pd.DataFrame, method: str = 'ffill') -> pd.DataFrame:
    """
    Fill missing data in a DataFrame.
    
    Args:
        df: DataFrame with potential missing values
        method: Method to fill ('ffill' for forward fill, 'bfill' for backward fill, 'interpolate')
        
    Returns:
        DataFrame with filled missing values
    """
    if method == 'ffill':
        return df.ffill().bfill()
    elif method == 'bfill':
        return df.bfill().ffill()
    elif method == 'interpolate':
        return df.interpolate(method='linear')
    else:
        raise ValueError(f"Unknown fill method: {method}")


def validate_data(df: pd.DataFrame) -> Dict[str, bool]:
    """
    Validate data quality.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Dictionary with validation results
    """
    return {
        'has_missing_values': df.isnull().sum().sum() > 0,
        'missing_values_count': df.isnull().sum().sum(),
        'has_duplicates': df.duplicated().sum() > 0,
        'duplicates_count': df.duplicated().sum(),
        'date_range': f"{df.index.min() if isinstance(df.index, pd.DatetimeIndex) else 'N/A'} to {df.index.max() if isinstance(df.index, pd.DatetimeIndex) else 'N/A'}",
        'total_rows': len(df),
        'total_columns': len(df.columns)
    }
