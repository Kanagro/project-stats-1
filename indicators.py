"""Technical indicators for financial analysis."""

import numpy as np
import pandas as pd


def simple_moving_average(prices: pd.Series, window: int = 20) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA).
    
    Args:
        prices: Series of prices
        window: Window size for moving average
        
    Returns:
        Series of SMA values
    """
    return prices.rolling(window=window).mean()


def exponential_moving_average(prices: pd.Series, window: int = 20) -> pd.Series:
    """
    Calculate Exponential Moving Average (EMA).
    
    Args:
        prices: Series of prices
        window: Window size for moving average
        
    Returns:
        Series of EMA values
    """
    return prices.ewm(span=window, adjust=False).mean()


def bollinger_bands(prices: pd.Series, window: int = 20, num_std: float = 2) -> tuple:
    """
    Calculate Bollinger Bands.
    
    Args:
        prices: Series of prices
        window: Window size for moving average
        num_std: Number of standard deviations for bands
        
    Returns:
        Tuple of (upper_band, middle_band, lower_band)
    """
    middle_band = prices.rolling(window=window).mean()
    std = prices.rolling(window=window).std()
    
    upper_band = middle_band + (num_std * std)
    lower_band = middle_band - (num_std * std)
    
    return upper_band, middle_band, lower_band


def relative_strength_index(prices: pd.Series, window: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        prices: Series of prices
        window: Window size for RSI calculation
        
    Returns:
        Series of RSI values (0-100)
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    Args:
        prices: Series of prices
        fast: Fast EMA period
        slow: Slow EMA period
        signal: Signal line period
        
    Returns:
        Tuple of (macd_line, signal_line, histogram)
    """
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def stochastic_oscillator(prices: pd.Series, window: int = 14, smooth_k: int = 3, smooth_d: int = 3) -> tuple:
    """
    Calculate Stochastic Oscillator.
    
    Args:
        prices: Series of prices
        window: Window size for calculation
        smooth_k: Smoothing period for %K
        smooth_d: Smoothing period for %D
        
    Returns:
        Tuple of (k_line, d_line)
    """
    low = prices.rolling(window=window).min()
    high = prices.rolling(window=window).max()
    
    k_line = 100 * ((prices - low) / (high - low))
    k_line = k_line.rolling(window=smooth_k).mean()
    d_line = k_line.rolling(window=smooth_d).mean()
    
    return k_line, d_line


def average_true_range(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    """
    Calculate Average True Range (ATR).
    
    Args:
        high: Series of high prices
        low: Series of low prices
        close: Series of close prices
        window: Window size for ATR
        
    Returns:
        Series of ATR values
    """
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=window).mean()
    
    return atr


def on_balance_volume(close: pd.Series, volume: pd.Series) -> pd.Series:
    """
    Calculate On-Balance Volume (OBV).
    
    Args:
        close: Series of close prices
        volume: Series of volume data
        
    Returns:
        Series of OBV values
    """
    obv = pd.Series(index=close.index, dtype=float)
    obv.iloc[0] = volume.iloc[0]
    
    for i in range(1, len(close)):
        if close.iloc[i] > close.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
        elif close.iloc[i] < close.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i-1]
    
    return obv


def rate_of_change(prices: pd.Series, window: int = 12) -> pd.Series:
    """
    Calculate Rate of Change (ROC).
    
    Args:
        prices: Series of prices
        window: Window size for ROC
        
    Returns:
        Series of ROC values
    """
    return (prices - prices.shift(window)) / prices.shift(window) * 100


def accumulation_distribution_line(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
    """
    Calculate Accumulation/Distribution Line.
    
    Args:
        high: Series of high prices
        low: Series of low prices
        close: Series of close prices
        volume: Series of volume data
        
    Returns:
        Series of A/D line values
    """
    clv = ((close - low) - (high - close)) / (high - low)
    ad = (clv * volume).cumsum()
    
    return ad


def calculate_indicators_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all technical indicators for a price series.
    
    Args:
        df: DataFrame with 'close', 'high', 'low', 'volume' columns
        
    Returns:
        DataFrame with all indicators
    """
    result = df.copy()
    
    # Moving averages
    result['SMA_20'] = simple_moving_average(df['close'], 20)
    result['SMA_50'] = simple_moving_average(df['close'], 50)
    result['EMA_12'] = exponential_moving_average(df['close'], 12)
    result['EMA_26'] = exponential_moving_average(df['close'], 26)
    
    # Bollinger Bands
    bb_upper, bb_middle, bb_lower = bollinger_bands(df['close'], 20, 2)
    result['BB_Upper'] = bb_upper
    result['BB_Middle'] = bb_middle
    result['BB_Lower'] = bb_lower
    
    # RSI
    result['RSI_14'] = relative_strength_index(df['close'], 14)
    
    # MACD
    macd_line, signal_line, histogram = macd(df['close'], 12, 26, 9)
    result['MACD'] = macd_line
    result['MACD_Signal'] = signal_line
    result['MACD_Hist'] = histogram
    
    # Stochastic
    stoch_k, stoch_d = stochastic_oscillator(df['close'], 14, 3, 3)
    result['Stoch_K'] = stoch_k
    result['Stoch_D'] = stoch_d
    
    # ATR
    result['ATR'] = average_true_range(df['high'], df['low'], df['close'], 14)
    
    # OBV
    result['OBV'] = on_balance_volume(df['close'], df['volume'])
    
    # ROC
    result['ROC'] = rate_of_change(df['close'], 12)
    
    # A/D Line
    result['AD'] = accumulation_distribution_line(df['high'], df['low'], df['close'], df['volume'])
    
    return result
