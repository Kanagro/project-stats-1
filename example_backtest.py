"""
Example script demonstrating backtesting capabilities.
"""

from datetime import datetime, timedelta
from src.data_handler import fetch_yahoo_data
from src.backtest import (
    SimpleMovingAverageCrossover,
    RSIStrategy,
    MACDStrategy,
    Backtest,
    compare_strategies,
)


def main():
    """Run backtesting examples."""
    
    print("=" * 70)
    print("FINTECH STATS - BACKTESTING EXAMPLES")
    print("=" * 70)
    
    # Fetch data
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    print(f"\nFetching AAPL data ({start_date} to {end_date})...")
    data = fetch_yahoo_data('AAPL', start_date=start_date, end_date=end_date)
    data.set_index('date', inplace=True)
    print(f"✓ Retrieved {len(data)} trading days")
    
    # 1. Test individual strategies
    print("\n" + "=" * 70)
    print("INDIVIDUAL STRATEGY BACKTESTS")
    print("=" * 70)
    
    initial_capital = 100000
    
    # SMA Crossover Strategy
    print("\n1. SMA Crossover Strategy (20/50)")
    sma_strategy = SimpleMovingAverageCrossover(fast_window=20, slow_window=50)
    sma_backtest = Backtest(sma_strategy, initial_capital=initial_capital)
    sma_backtest.run(data)
    sma_backtest.print_results()
    
    # RSI Strategy
    print("\n2. RSI Strategy (14, oversold=30, overbought=70)")
    rsi_strategy = RSIStrategy()
    rsi_backtest = Backtest(rsi_strategy, initial_capital=initial_capital)
    rsi_backtest.run(data)
    rsi_backtest.print_results()
    
    # MACD Strategy
    print("\n3. MACD Strategy (12/26/9)")
    macd_strategy = MACDStrategy()
    macd_backtest = Backtest(macd_strategy, initial_capital=initial_capital)
    macd_backtest.run(data)
    macd_backtest.print_results()
    
    # 2. Compare strategies
    print("\n" + "=" * 70)
    print("STRATEGY COMPARISON")
    print("=" * 70)
    
    strategies = [
        SimpleMovingAverageCrossover(fast_window=20, slow_window=50),
        RSIStrategy(),
        MACDStrategy(),
    ]
    
    comparison = compare_strategies(data, strategies, initial_capital)
    
    print("\nComparative Results:")
    print("-" * 70)
    print(f"{'Strategy':<20} {'Return':<12} {'Sharpe':<10} {'Win Rate':<12} {'Trades':<8}")
    print("-" * 70)
    
    for strategy_name, results in comparison.items():
        print(f"{strategy_name:<20} {results['total_return']:>10.2%}  {results['sharpe_ratio']:>8.4f}  "
              f"{results['win_rate']:>10.2%}  {results['total_trades']:>6}")
    
    # 3. Commission and slippage impact
    print("\n" + "=" * 70)
    print("COMMISSION & SLIPPAGE IMPACT")
    print("=" * 70)
    
    print("\nSMA Strategy Performance with Different Costs:")
    print("-" * 70)
    print(f"{'Scenario':<25} {'Final Equity':<15} {'Return':<12} {'Impact':<12}")
    print("-" * 70)
    
    scenarios = [
        ("No costs", 0, 0),
        ("Commission only (0.1%)", 0.001, 0),
        ("Slippage only (0.1%)", 0, 0.001),
        ("Both (0.1% each)", 0.001, 0.001),
    ]
    
    base_results = None
    base_equity = None
    
    for scenario_name, commission, slippage in scenarios:
        backtest = Backtest(
            SimpleMovingAverageCrossover(),
            initial_capital=initial_capital,
            commission=commission,
            slippage=slippage
        )
        backtest.run(data)
        results = backtest.get_results()
        
        if base_equity is None:
            base_equity = results['final_equity']
            base_results = results
        
        impact = results['final_equity'] - base_equity
        print(f"{scenario_name:<25} ${results['final_equity']:>13,.0f}  "
              f"{results['total_return']:>10.2%}  ${impact:>10,.0f}")
    
    # 4. Top 5 trades
    print("\n" + "=" * 70)
    print("TOP TRADES (SMA STRATEGY)")
    print("=" * 70)
    
    trades_df = sma_backtest.get_trades()
    if len(trades_df) > 0:
        trades_df_sorted = trades_df.nlargest(5, 'pnl')
        print("\nTop 5 Profitable Trades:")
        print("-" * 70)
        print(f"{'Entry Date':<12} {'Exit Date':<12} {'Profit':<12} {'Return':<10}")
        print("-" * 70)
        
        for idx, trade in trades_df_sorted.iterrows():
            print(f"{str(trade['entry_date'].date()):<12} {str(trade['exit_date'].date()):<12} "
                  f"${trade['pnl']:>10,.2f}  {trade['pnl_pct']:>8.2%}")
    
    print("\n" + "=" * 70)
    print("Backtesting completed!")
    print("=" * 70)


if __name__ == '__main__':
    main()
