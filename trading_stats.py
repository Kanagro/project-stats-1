"""Trading statistics analysis utilities."""

import pandas as pd
import numpy as np


def calculate_win_rate(trades: pd.DataFrame) -> float:
    """
    Calculate win rate from trades.
    
    Args:
        trades: DataFrame with 'pnl' column
        
    Returns:
        Win rate as percentage
    """
    if len(trades) == 0:
        return 0.0
    
    winning_trades = (trades['pnl'] > 0).sum()
    return winning_trades / len(trades)


def calculate_profit_factor(trades: pd.DataFrame) -> float:
    """
    Calculate profit factor.
    
    Args:
        trades: DataFrame with 'pnl' column
        
    Returns:
        Profit factor (gross profit / gross loss)
    """
    gross_profit = trades[trades['pnl'] > 0]['pnl'].sum()
    gross_loss = abs(trades[trades['pnl'] < 0]['pnl'].sum())
    
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0
    
    return gross_profit / gross_loss


def analyze_trades(trades: pd.DataFrame) -> dict:
    """
    Comprehensive trade analysis.
    
    Args:
        trades: DataFrame with trade data
        
    Returns:
        Dictionary with trade statistics
    """
    return {
        'total_trades': len(trades),
        'win_rate': calculate_win_rate(trades),
        'profit_factor': calculate_profit_factor(trades),
        'avg_win': trades[trades['pnl'] > 0]['pnl'].mean(),
        'avg_loss': trades[trades['pnl'] < 0]['pnl'].mean(),
        'total_pnl': trades['pnl'].sum()
    }
