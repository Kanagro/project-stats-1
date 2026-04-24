"""Command-line interface for financial statistics and analysis."""

import argparse
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

from src.data_handler import (
    load_data,
    fetch_yahoo_data,
    fetch_multiple_tickers,
    add_returns_to_dataframe,
    validate_data,
)
from src.indicators import calculate_indicators_summary
from src.risk_metrics import calculate_risk_metrics_summary
from src.portfolio import Portfolio
from src.backtest import Backtest, SimpleMovingAverageCrossover, RSIStrategy, MACDStrategy
from src.visualizations import (
    plot_price_history,
    plot_bollinger_bands,
    plot_rsi,
    plot_macd,
    plot_cumulative_returns,
    plot_correlation_heatmap,
    plot_risk_metrics,
)


def create_parser():
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        description='Financial Statistics and Analysis Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch and analyze AAPL data
  python -m src.cli analyze --ticker AAPL --period 1y
  
  # Run backtest with SMA crossover strategy
  python -m src.cli backtest --ticker AAPL --strategy sma --period 1y
  
  # Visualize portfolio indicators
  python -m src.cli visualize --ticker AAPL --indicator rsi --output rsi_chart.png
  
  # Load CSV and calculate risk metrics
  python -m src.cli metrics --file data/sample.csv --column close
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze ticker data and calculate metrics')
    analyze_parser.add_argument('--ticker', type=str, required=True, help='Stock ticker symbol (e.g., AAPL)')
    analyze_parser.add_argument('--period', type=str, default='1y', 
                               help='Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)')
    analyze_parser.add_argument('--output', type=str, default=None, help='Output file for results (JSON)')
    analyze_parser.add_argument('--verbose', action='store_true', help='Print detailed output')
    
    # Backtest command
    backtest_parser = subparsers.add_parser('backtest', help='Run strategy backtest')
    backtest_parser.add_argument('--ticker', type=str, required=True, help='Stock ticker symbol')
    backtest_parser.add_argument('--strategy', type=str, choices=['sma', 'rsi', 'macd'], 
                                required=True, help='Strategy to backtest')
    backtest_parser.add_argument('--period', type=str, default='1y', help='Data period')
    backtest_parser.add_argument('--initial-capital', type=float, default=10000, 
                               help='Initial capital for backtest')
    backtest_parser.add_argument('--commission', type=float, default=0.001, help='Commission per trade')
    backtest_parser.add_argument('--output', type=str, default=None, help='Output file for results')
    
    # Visualize command
    visualize_parser = subparsers.add_parser('visualize', help='Generate charts and visualizations')
    visualize_parser.add_argument('--ticker', type=str, required=True, help='Stock ticker symbol')
    visualize_parser.add_argument('--indicator', type=str, 
                                 choices=['price', 'bollinger', 'rsi', 'macd', 'returns', 'heatmap'],
                                 required=True, help='Indicator to visualize')
    visualize_parser.add_argument('--period', type=str, default='1y', help='Data period')
    visualize_parser.add_argument('--output', type=str, required=True, help='Output file for chart (PNG)')
    
    # Metrics command
    metrics_parser = subparsers.add_parser('metrics', help='Calculate metrics from data file')
    metrics_parser.add_argument('--file', type=str, required=True, help='Input CSV file')
    metrics_parser.add_argument('--column', type=str, default='close', help='Price column name')
    metrics_parser.add_argument('--output', type=str, default=None, help='Output file for results')
    metrics_parser.add_argument('--validate', action='store_true', help='Validate data quality')
    
    # Portfolio command
    portfolio_parser = subparsers.add_parser('portfolio', help='Analyze portfolio')
    portfolio_parser.add_argument('--tickers', type=str, required=True, 
                                help='Comma-separated ticker symbols')
    portfolio_parser.add_argument('--weights', type=str, default=None, 
                                help='Comma-separated weights (e.g., 0.5,0.3,0.2)')
    portfolio_parser.add_argument('--period', type=str, default='1y', help='Data period')
    portfolio_parser.add_argument('--output', type=str, default=None, help='Output file for results')
    
    return parser


def format_metrics(metrics_dict, title="Metrics"):
    """Format metrics dictionary for display."""
    output = [f"\n{title}:"]
    output.append("=" * 60)
    for key, value in metrics_dict.items():
        if isinstance(value, float):
            output.append(f"  {key:.<40} {value:>15.4f}")
        elif isinstance(value, dict):
            output.append(f"  {key}:")
            for k, v in value.items():
                if isinstance(v, float):
                    output.append(f"    {k:.<38} {v:>15.4f}")
                else:
                    output.append(f"    {k:.<38} {v}")
        else:
            output.append(f"  {key:.<40} {value:>15}")
    return "\n".join(output)


def analyze_command(args):
    """Execute analyze command."""
    try:
        print(f"\n📊 Fetching data for {args.ticker}...")
        df = fetch_yahoo_data(args.ticker, period=args.period)
        
        if df is None or len(df) == 0:
            print(f"❌ Failed to fetch data for {args.ticker}")
            return 1
        
        print(f"✅ Retrieved {len(df)} trading days of data")
        
        # Add returns
        df = add_returns_to_dataframe(df, 'close')
        
        # Calculate metrics
        risk_metrics = calculate_risk_metrics_summary(df['returns'].dropna())
        indicators = calculate_indicators_summary(df)
        
        # Prepare output
        results = {
            'ticker': args.ticker,
            'period': args.period,
            'data_points': len(df),
            'date_range': f"{df.index[0].date()} to {df.index[-1].date()}",
            'risk_metrics': {k: float(v) if isinstance(v, (int, np.integer, np.floating)) else v 
                           for k, v in risk_metrics.items()},
            'latest_indicators': {k: float(v) if isinstance(v, (int, np.integer, np.floating)) else v 
                                for k, v in indicators.items()},
        }
        
        # Display output
        if args.verbose:
            print(format_metrics(risk_metrics, "Risk Metrics"))
            print(format_metrics(indicators, "Technical Indicators"))
        
        print(f"\n✅ Analysis complete")
        
        # Save if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"💾 Results saved to {args.output}")
        
        return 0
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


def backtest_command(args):
    """Execute backtest command."""
    try:
        print(f"\n🔄 Running {args.strategy.upper()} backtest on {args.ticker}...")
        
        # Fetch data
        df = fetch_yahoo_data(args.ticker, period=args.period)
        if df is None or len(df) == 0:
            print(f"❌ Failed to fetch data for {args.ticker}")
            return 1
        
        # Select strategy
        strategy_map = {
            'sma': SimpleMovingAverageCrossover(fast=20, slow=50),
            'rsi': RSIStrategy(rsi_period=14, oversold=30, overbought=70),
            'macd': MACDStrategy(fast=12, slow=26, signal=9),
        }
        strategy = strategy_map[args.strategy]
        
        # Run backtest
        backtest = Backtest(
            df,
            strategy,
            initial_capital=args.initial_capital,
            commission=args.commission
        )
        results = backtest.run()
        
        # Display results
        print(f"\n{'='*60}")
        print(f"Backtest Results - {args.strategy.upper()} Strategy")
        print(f"{'='*60}")
        print(f"Initial Capital:     ${results['initial_capital']:>15,.2f}")
        print(f"Final Capital:       ${results['final_capital']:>15,.2f}")
        print(f"Total Return:        {results['total_return']:>15.2%}")
        print(f"Total Trades:        {results['total_trades']:>15}")
        print(f"Winning Trades:      {results['winning_trades']:>15}")
        print(f"Losing Trades:       {results['losing_trades']:>15}")
        print(f"Win Rate:            {results['win_rate']:>15.2%}")
        print(f"Avg Win:             {results['avg_win']:>15.4f}")
        print(f"Avg Loss:            {results['avg_loss']:>15.4f}")
        print(f"Profit Factor:       {results['profit_factor']:>15.4f}")
        print(f"Sharpe Ratio:        {results['sharpe_ratio']:>15.4f}")
        print(f"Max Drawdown:        {results['max_drawdown']:>15.2%}")
        
        # Save if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Results saved to {args.output}")
        
        return 0
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


def visualize_command(args):
    """Execute visualize command."""
    try:
        print(f"\n📈 Generating {args.indicator} chart for {args.ticker}...")
        
        # Fetch data
        df = fetch_yahoo_data(args.ticker, period=args.period)
        if df is None or len(df) == 0:
            print(f"❌ Failed to fetch data for {args.ticker}")
            return 1
        
        # Generate chart
        if args.indicator == 'price':
            plot_price_history(df, args.output, title=f'{args.ticker} Price History')
        elif args.indicator == 'bollinger':
            plot_bollinger_bands(df, args.output, title=f'{args.ticker} Bollinger Bands')
        elif args.indicator == 'rsi':
            plot_rsi(df, args.output, title=f'{args.ticker} RSI')
        elif args.indicator == 'macd':
            plot_macd(df, args.output, title=f'{args.ticker} MACD')
        elif args.indicator == 'returns':
            df_with_returns = add_returns_to_dataframe(df, 'close')
            plot_cumulative_returns(df_with_returns, args.output, title=f'{args.ticker} Cumulative Returns')
        elif args.indicator == 'heatmap':
            tickers = [args.ticker]
            plot_correlation_heatmap(tickers, args.output, period=args.period)
        
        print(f"✅ Chart saved to {args.output}")
        return 0
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


def metrics_command(args):
    """Execute metrics command."""
    try:
        print(f"\n📊 Analyzing data from {args.file}...")
        
        # Load data
        if not Path(args.file).exists():
            print(f"❌ File not found: {args.file}")
            return 1
        
        df = load_data(args.file)
        
        # Validate if requested
        if args.validate:
            validation = validate_data(df)
            print(format_metrics(validation, "Data Validation"))
        
        # Calculate metrics on specified column
        if args.column not in df.columns:
            print(f"❌ Column '{args.column}' not found in data")
            return 1
        
        prices = df[args.column]
        returns = prices.pct_change().dropna()
        
        risk_metrics = calculate_risk_metrics_summary(returns)
        
        # Display results
        print(format_metrics(risk_metrics, f"Risk Metrics ({args.column})"))
        
        # Save if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(risk_metrics, f, indent=2, default=str)
            print(f"\n💾 Results saved to {args.output}")
        
        return 0
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


def portfolio_command(args):
    """Execute portfolio command."""
    try:
        # Parse tickers
        tickers = [t.strip().upper() for t in args.tickers.split(',')]
        print(f"\n🎯 Analyzing portfolio: {', '.join(tickers)}...")
        
        # Parse weights if provided
        if args.weights:
            weights = [float(w.strip()) for w in args.weights.split(',')]
            if len(weights) != len(tickers):
                print(f"❌ Number of weights ({len(weights)}) doesn't match tickers ({len(tickers)})")
                return 1
            if not np.isclose(sum(weights), 1.0):
                print(f"❌ Weights must sum to 1.0 (current sum: {sum(weights):.4f})")
                return 1
        else:
            weights = [1.0 / len(tickers)] * len(tickers)
        
        # Fetch data
        print(f"📥 Fetching data for {len(tickers)} assets...")
        portfolio_df = fetch_multiple_tickers(tickers, period=args.period)
        
        if portfolio_df is None or len(portfolio_df) == 0:
            print(f"❌ Failed to fetch portfolio data")
            return 1
        
        # Calculate returns
        portfolio_returns = portfolio_df.pct_change().dropna()
        portfolio_returns_weighted = (portfolio_returns * weights).sum(axis=1)
        
        # Calculate metrics
        risk_metrics = calculate_risk_metrics_summary(portfolio_returns_weighted)
        
        # Display results
        print(f"\n✅ Portfolio Analysis: {len(portfolio_df)} trading days")
        print(f"{'='*60}")
        for ticker, weight in zip(tickers, weights):
            print(f"  {ticker:.<10} {weight:>10.2%}")
        print(format_metrics(risk_metrics, "Portfolio Metrics"))
        
        # Save if requested
        if args.output:
            results = {
                'tickers': tickers,
                'weights': weights,
                'metrics': {k: float(v) if isinstance(v, (int, np.integer, np.floating)) else v 
                          for k, v in risk_metrics.items()},
            }
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Results saved to {args.output}")
        
        return 0
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Route to appropriate command
    command_handlers = {
        'analyze': analyze_command,
        'backtest': backtest_command,
        'visualize': visualize_command,
        'metrics': metrics_command,
        'portfolio': portfolio_command,
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
