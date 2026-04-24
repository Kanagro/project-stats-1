"""
Example script demonstrating fintech stats project capabilities.
Shows how to fetch real-time data and perform analysis.
"""

from datetime import datetime, timedelta
from src.data_handler import fetch_yahoo_data, fetch_multiple_tickers, combine_ticker_data, add_returns_to_dataframe
from src.indicators import calculate_indicators_summary
from src.risk_metrics import calculate_risk_metrics_summary
import pandas as pd


def main():
    """Run example analysis."""
    
    # 1. Fetch real-time data from Yahoo Finance
    print("=" * 60)
    print("FINTECH STATS PROJECT - EXAMPLE ANALYSIS")
    print("=" * 60)
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    
    print(f"\nFetching data from {start_date} to {end_date}")
    
    # Fetch single ticker
    print("\n1. Fetching single ticker (AAPL)...")
    aapl = fetch_yahoo_data('AAPL', start_date=start_date, end_date=end_date)
    print(f"   ✓ Retrieved {len(aapl)} records")
    
    # Fetch multiple tickers
    print("\n2. Fetching multiple tickers (AAPL, GOOGL, MSFT)...")
    tickers = ['AAPL', 'GOOGL', 'MSFT']
    data_dict = fetch_multiple_tickers(tickers, start_date=start_date, end_date=end_date)
    print(f"   ✓ Retrieved {len(data_dict)} tickers")
    
    # Combine data
    print("\n3. Combining ticker close prices...")
    combined = combine_ticker_data(data_dict, column='close')
    print(f"   ✓ Combined data shape: {combined.shape}")
    
    # 2. Calculate returns
    print("\n4. Calculating returns...")
    aapl_with_returns = add_returns_to_dataframe(aapl, 'close')
    returns = aapl_with_returns['returns'].dropna()
    print(f"   ✓ Calculated {len(returns)} daily returns")
    
    # 3. Calculate technical indicators
    print("\n5. Calculating technical indicators for AAPL...")
    aapl_with_indicators = calculate_indicators_summary(aapl)
    print(f"   ✓ Added 17 technical indicators")
    print(f"   Indicators: SMA_20, SMA_50, EMA_12, EMA_26, BB_Upper/Middle/Lower,")
    print(f"              RSI_14, MACD, MACD_Signal, MACD_Hist, Stoch_K/D,")
    print(f"              ATR, OBV, ROC, AD")
    
    # 4. Calculate risk metrics
    print("\n6. Calculating risk metrics for AAPL...")
    risk_metrics = calculate_risk_metrics_summary(returns)
    
    print("\n   Risk Metrics Summary:")
    print(f"   - Annual Return: {risk_metrics['annualized_return']:.2%}")
    print(f"   - Volatility: {risk_metrics['volatility']:.2%}")
    print(f"   - Sharpe Ratio: {risk_metrics['sharpe_ratio']:.4f}")
    print(f"   - Sortino Ratio: {risk_metrics['sortino_ratio']:.4f}")
    print(f"   - Max Drawdown: {risk_metrics['max_drawdown']:.2%}")
    print(f"   - Calmar Ratio: {risk_metrics['calmar_ratio']:.4f}")
    print(f"   - VaR (95%): {risk_metrics['var_95']:.2%}")
    print(f"   - CVaR (95%): {risk_metrics['cvar_95']:.2%}")
    
    # 5. Display latest data
    print("\n7. Latest AAPL Data:")
    print("\n   Recent prices with indicators:")
    display_cols = ['date', 'close', 'SMA_20', 'RSI_14', 'BB_Upper', 'BB_Lower']
    latest = aapl_with_indicators[display_cols].tail(5)
    print(latest.to_string())
    
    # 6. Portfolio correlation
    print("\n8. Portfolio Correlation (AAPL, GOOGL, MSFT):")
    print("\n" + combined.corr().round(4).to_string())
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
