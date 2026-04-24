"""Portfolio analysis utilities."""

import pandas as pd
import numpy as np
from typing import Dict, List


class Portfolio:
    """Portfolio analysis class for managing and analyzing investment portfolios."""
    
    def __init__(self, data: pd.DataFrame, initial_capital: float = 100000):
        """
        Initialize Portfolio object.
        
        Args:
            data: DataFrame with financial data (should have 'date' and price columns)
            initial_capital: Initial investment amount
        """
        self.data = data
        self.initial_capital = initial_capital
        self.positions = {}
        
    def add_position(self, symbol: str, shares: float, price: float) -> None:
        """
        Add a position to the portfolio.
        
        Args:
            symbol: Asset symbol
            shares: Number of shares
            price: Purchase price
        """
        self.positions[symbol] = {
            'shares': shares,
            'purchase_price': price,
            'purchase_value': shares * price
        }
    
    def get_current_value(self) -> float:
        """
        Calculate current portfolio value.
        
        Returns:
            Total current value
        """
        total = sum(pos['purchase_value'] for pos in self.positions.values())
        return total
    
    def summary(self) -> Dict:
        """
        Get portfolio summary statistics.
        
        Returns:
            Dictionary with portfolio metrics
        """
        current_value = self.get_current_value()
        
        return {
            'initial_capital': self.initial_capital,
            'current_value': current_value,
            'total_return': (current_value - self.initial_capital) / self.initial_capital,
            'num_positions': len(self.positions)
        }
