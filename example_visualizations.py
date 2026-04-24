"""
Example script demonstrating visualization capabilities.
"""

from datetime import datetime, timedelta
from src.data_handler import fetch_yahoo_data, add_returns_to_dataframe, fetch_multiple_tickers, combine_ticker_data
from src.indicators import calculate_indicators_summary
from src.risk_metrics import calculate_risk_metrics_summary
from src.visualizations import (
    plot_price_history,
    plot_bollinger_bands,
    plot_rsi,
    plot_macd,
    plot_cumulative_returns,
    plot_drawdown,
    plot_returns_distribution,
    plot_risk_metrics,
    plot_correlation_heatmap,
)
import matplotlib.pyplot as plt


def main():
    """Run visualization examples."""
    
    print("=" * 60)
    print("FINTECH STATS - VISUALIZATION EXAMPLES")
    print("=" * 60)
    
    # Fetch data
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    print(f"\nFetching AAPL data ({start_date} to {end_date})...")
    aapl = fetch_yahoo_data('AAPL', start_date=start_date, end_date=end_date)
    
    # Add indicators
    print("Calculating indicators...")
    aapl_with_indicators = calculate_indicators_summary(aapl)
    
    # Calculate returns and metrics
    aapl_with_returns = add_returns_to_dataframe(aapl, 'close')
    returns = aapl_with_returns['returns'].dropna()
    risk_metrics = calculate_risk_metrics_summary(returns)
    
    # Create visualizations
    print("\nGenerating visualizations...")
    
    # 1. Price history
    print("1. Price History with Volume...")
    fig1 = plot_price_history(aapl_with_indicators, title='AAPL Price History (90 days)')
    fig1.savefig('plots/01_price_history.png', dpi=150, bbox_inches='tight')
    plt.close(fig1)
    
    # 2. Bollinger Bands
    print("2. Bollinger Bands...")
    fig2 = plot_bollinger_bands(aapl_with_indicators, title='AAPL with Bollinger Bands')
    fig2.savefig('plots/02_bollinger_bands.png', dpi=150, bbox_inches='tight')
    plt.close(fig2)
    
    # 3. RSI
    print("3. RSI Indicator...")
    fig3 = plot_rsi(aapl_with_indicators, title='AAPL RSI (14)')
    fig3.savefig('plots/03_rsi.png', dpi=150, bbox_inches='tight')
    plt.close(fig3)
    
    # 4. MACD
    print("4. MACD Indicator...")
    fig4 = plot_macd(aapl_with_indicators, title='AAPL MACD')
    fig4.savefig('plots/04_macd.png', dpi=150, bbox_inches='tight')
    plt.close(fig4)
    
    # 5. Cumulative Returns
    print("5. Cumulative Returns...")
    fig5 = plot_cumulative_returns(returns, title='AAPL Cumulative Returns')
    fig5.savefig('plots/05_cumulative_returns.png', dpi=150, bbox_inches='tight')
    plt.close(fig5)
    
    # 6. Drawdown
    print("6. Drawdown...")
    fig6 = plot_drawdown(returns, title='AAPL Drawdown')
    fig6.savefig('plots/06_drawdown.png', dpi=150, bbox_inches='tight')
    plt.close(fig6)
    
    # 7. Returns Distribution
    print("7. Returns Distribution...")
    fig7 = plot_returns_distribution(returns, title='AAPL Daily Returns Distribution')
    fig7.savefig('plots/07_returns_distribution.png', dpi=150, bbox_inches='tight')
    plt.close(fig7)
    
    # 8. Risk Metrics
    print("8. Risk Metrics Summary...")
    fig8 = plot_risk_metrics(risk_metrics, title='AAPL Risk Metrics')
    fig8.savefig('plots/08_risk_metrics.png', dpi=150, bbox_inches='tight')
    plt.close(fig8)
    
    # 9. Correlation Heatmap
    print("9. Portfolio Correlation...")
    tickers = ['AAPL', 'GOOGL', 'MSFT']
    data_dict = fetch_multiple_tickers(tickers, start_date=start_date, end_date=end_date)
    combined = combine_ticker_data(data_dict, column='close')
    corr_matrix = combined.corr()
    
    fig9 = plot_correlation_heatmap(corr_matrix, title='Correlation Matrix (AAPL, GOOGL, MSFT)')
    fig9.savefig('plots/09_correlation_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close(fig9)
    
    print("\n" + "=" * 60)
    print("✓ All visualizations saved to plots/ directory")
    print("=" * 60)
    
    # Print summary
    print("\nRisk Metrics Summary:")
    print(f"  Annual Return: {risk_metrics['annualized_return']:.2%}")
    print(f"  Volatility: {risk_metrics['volatility']:.2%}")
    print(f"  Sharpe Ratio: {risk_metrics['sharpe_ratio']:.4f}")
    print(f"  Max Drawdown: {risk_metrics['max_drawdown']:.2%}")


if __name__ == '__main__':
    # Create plots directory if it doesn't exist
    import os
    os.makedirs('plots', exist_ok=True)
    
    main()
