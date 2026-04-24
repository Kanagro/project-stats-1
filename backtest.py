"""Backtesting framework for strategy evaluation."""

import pandas as pd
import numpy as np
from typing import Optional, Callable, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class Signal(Enum):
    """Trading signal types."""
    BUY = 1
    SELL = -1
    HOLD = 0


@dataclass
class Trade:
    """Represents a single trade."""
    entry_date: pd.Timestamp
    entry_price: float
    entry_signal: Signal
    exit_date: Optional[pd.Timestamp] = None
    exit_price: Optional[float] = None
    exit_signal: Optional[Signal] = None
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    
    def close_trade(self, exit_date: pd.Timestamp, exit_price: float, exit_signal: Signal) -> None:
        """Close the trade."""
        self.exit_date = exit_date
        self.exit_price = exit_price
        self.exit_signal = exit_signal
        self.pnl = exit_price - self.entry_price
        self.pnl_pct = self.pnl / self.entry_price


class Strategy:
    """Base class for trading strategies."""
    
    def __init__(self, name: str = "Strategy"):
        """Initialize strategy."""
        self.name = name
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals.
        
        Args:
            data: DataFrame with price data
            
        Returns:
            Series of Signal values
        """
        raise NotImplementedError("Subclasses must implement generate_signals")


class SimpleMovingAverageCrossover(Strategy):
    """SMA Crossover strategy."""
    
    def __init__(self, fast_window: int = 20, slow_window: int = 50):
        """Initialize SMA crossover strategy."""
        super().__init__(name="SMA Crossover")
        self.fast_window = fast_window
        self.slow_window = slow_window
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on SMA crossover."""
        close = data['close']
        fast_ma = close.rolling(self.fast_window).mean()
        slow_ma = close.rolling(self.slow_window).mean()
        
        signals = pd.Series(0, index=data.index, dtype=int)
        
        # BUY when fast MA > slow MA
        signals[fast_ma > slow_ma] = 1
        # SELL when fast MA < slow MA
        signals[fast_ma < slow_ma] = -1
        
        return signals.map({1: Signal.BUY, -1: Signal.SELL, 0: Signal.HOLD})


class RSIStrategy(Strategy):
    """RSI-based mean reversion strategy."""
    
    def __init__(self, rsi_window: int = 14, oversold: int = 30, overbought: int = 70):
        """Initialize RSI strategy."""
        super().__init__(name="RSI Strategy")
        self.rsi_window = rsi_window
        self.oversold = oversold
        self.overbought = overbought
    
    def _calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """Calculate RSI."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(self.rsi_window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.rsi_window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on RSI."""
        rsi = self._calculate_rsi(data['close'])
        
        signals = pd.Series(Signal.HOLD, index=data.index)
        signals[rsi < self.oversold] = Signal.BUY  # Oversold, buy
        signals[rsi > self.overbought] = Signal.SELL  # Overbought, sell
        
        return signals


class MACDStrategy(Strategy):
    """MACD-based trend following strategy."""
    
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        """Initialize MACD strategy."""
        super().__init__(name="MACD Strategy")
        self.fast = fast
        self.slow = slow
        self.signal = signal
    
    def _calculate_macd(self, prices: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD."""
        ema_fast = prices.ewm(span=self.fast, adjust=False).mean()
        ema_slow = prices.ewm(span=self.slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=self.signal, adjust=False).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on MACD."""
        macd, signal_line, histogram = self._calculate_macd(data['close'])
        
        signals = pd.Series(Signal.HOLD, index=data.index)
        signals[histogram > 0] = Signal.BUY  # MACD above signal line
        signals[histogram < 0] = Signal.SELL  # MACD below signal line
        
        return signals


class Backtest:
    """Backtesting engine."""
    
    def __init__(
        self,
        strategy: Strategy,
        initial_capital: float = 100000,
        commission: float = 0.001,
        slippage: float = 0.0
    ):
        """
        Initialize backtester.
        
        Args:
            strategy: Trading strategy object
            initial_capital: Starting capital
            commission: Commission per trade (0.1% = 0.001)
            slippage: Slippage per trade (0.1% = 0.001)
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        self.capital = initial_capital
        self.position = 0  # Number of shares held
        self.entry_price = 0
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = []
        self.cash: List[float] = []
        self.dates: List[pd.Timestamp] = []
        
    def run(self, data: pd.DataFrame) -> 'Backtest':
        """
        Run the backtest.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Self for method chaining
        """
        signals = self.strategy.generate_signals(data)
        
        # Track current open trade
        open_trade: Optional[Trade] = None
        
        for idx, (date, row) in enumerate(data.iterrows()):
            price = row['close']
            signal = signals.iloc[idx]
            
            # Close existing trade if signal changes
            if open_trade is not None and signal != Signal.HOLD and signal != open_trade.entry_signal:
                # Exit trade
                exit_price = price * (1 + self.slippage)
                open_trade.close_trade(date, exit_price, signal)
                
                # Update capital
                pnl = open_trade.pnl
                self.capital += pnl * self.position - (abs(pnl) * self.commission)
                self.position = 0
                self.trades.append(open_trade)
                open_trade = None
            
            # Enter new trade
            if signal == Signal.BUY and self.position == 0:
                entry_price = price * (1 + self.slippage)
                self.capital -= entry_price * 100  # Buy 100 shares
                self.position = 100
                open_trade = Trade(date, entry_price, signal)
            
            elif signal == Signal.SELL and self.position > 0:
                exit_price = price * (1 - self.slippage)
                pnl = (exit_price - self.entry_price) * self.position
                self.capital += pnl - (abs(pnl) * self.commission)
                self.position = 0
                if open_trade:
                    open_trade.close_trade(date, exit_price, signal)
                    self.trades.append(open_trade)
                    open_trade = None
            
            # Record equity
            current_equity = self.capital + (self.position * price)
            self.equity_curve.append(current_equity)
            self.cash.append(self.capital)
            self.dates.append(date)
        
        # Close any open trade at end
        if open_trade is not None:
            final_price = data.iloc[-1]['close']
            open_trade.close_trade(data.index[-1], final_price, Signal.HOLD)
            self.trades.append(open_trade)
        
        return self
    
    def get_results(self) -> Dict:
        """Get backtest results."""
        equity = np.array(self.equity_curve)
        total_return = (equity[-1] - self.initial_capital) / self.initial_capital
        
        # Calculate drawdown
        cummax = np.maximum.accumulate(equity)
        drawdown = (equity - cummax) / cummax
        max_drawdown = np.min(drawdown)
        
        # Calculate Sharpe ratio
        returns = np.diff(equity) / equity[:-1]
        annual_return = (equity[-1] / self.initial_capital) ** (252 / len(equity)) - 1
        annual_std = np.std(returns) * np.sqrt(252)
        sharpe = annual_return / annual_std if annual_std > 0 else 0
        
        # Win rate
        closed_trades = [t for t in self.trades if t.pnl is not None]
        winning_trades = [t for t in closed_trades if t.pnl > 0]
        win_rate = len(winning_trades) / len(closed_trades) if closed_trades else 0
        
        # Profit factor
        gross_profit = sum([t.pnl for t in closed_trades if t.pnl > 0])
        gross_loss = abs(sum([t.pnl for t in closed_trades if t.pnl < 0]))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'annual_volatility': annual_std,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'final_equity': equity[-1],
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(closed_trades) - len(winning_trades),
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_win': np.mean([t.pnl for t in winning_trades]) if winning_trades else 0,
            'avg_loss': np.mean([t.pnl for t in closed_trades if t.pnl < 0]) if closed_trades else 0,
        }
    
    def get_equity_curve(self) -> pd.DataFrame:
        """Get equity curve as DataFrame."""
        return pd.DataFrame({
            'date': self.dates,
            'equity': self.equity_curve,
            'cash': self.cash,
            'position_value': [self.position * price if self.position > 0 else 0 
                              for price in [self.equity_curve[i] - self.cash[i] 
                                          for i in range(len(self.equity_curve))]]
        })
    
    def get_trades(self) -> pd.DataFrame:
        """Get trades as DataFrame."""
        trades_data = []
        for trade in self.trades:
            if trade.exit_date is not None:
                trades_data.append({
                    'entry_date': trade.entry_date,
                    'entry_price': trade.entry_price,
                    'exit_date': trade.exit_date,
                    'exit_price': trade.exit_price,
                    'pnl': trade.pnl,
                    'pnl_pct': trade.pnl_pct,
                })
        
        return pd.DataFrame(trades_data)
    
    def print_results(self) -> None:
        """Print backtest results."""
        results = self.get_results()
        
        print("\n" + "=" * 60)
        print(f"BACKTEST RESULTS - {self.strategy.name}")
        print("=" * 60)
        print(f"\nInitial Capital: ${self.initial_capital:,.2f}")
        print(f"Final Equity: ${results['final_equity']:,.2f}")
        print(f"Total Return: {results['total_return']:.2%}")
        print(f"Annual Return: {results['annual_return']:.2%}")
        print(f"Annual Volatility: {results['annual_volatility']:.2%}")
        print(f"Sharpe Ratio: {results['sharpe_ratio']:.4f}")
        print(f"Max Drawdown: {results['max_drawdown']:.2%}")
        
        print(f"\nTotal Trades: {results['total_trades']}")
        print(f"Winning Trades: {results['winning_trades']}")
        print(f"Losing Trades: {results['losing_trades']}")
        print(f"Win Rate: {results['win_rate']:.2%}")
        print(f"Profit Factor: {results['profit_factor']:.2f}")
        print(f"Avg Win: ${results['avg_win']:.2f}")
        print(f"Avg Loss: ${results['avg_loss']:.2f}")
        print("=" * 60)


def compare_strategies(
    data: pd.DataFrame,
    strategies: List[Strategy],
    initial_capital: float = 100000
) -> Dict[str, Dict]:
    """
    Compare multiple strategies on the same data.
    
    Args:
        data: DataFrame with OHLCV data
        strategies: List of strategy objects
        initial_capital: Starting capital
        
    Returns:
        Dictionary with results for each strategy
    """
    results = {}
    
    for strategy in strategies:
        backtest = Backtest(strategy, initial_capital)
        backtest.run(data)
        results[strategy.name] = backtest.get_results()
    
    return results
