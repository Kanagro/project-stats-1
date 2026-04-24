# Financial Statistics & Analysis Platform 📊

A comprehensive Python platform for financial data analysis, portfolio evaluation, technical indicators, and strategy backtesting.

## Overview

This project provides a complete toolkit for analyzing financial markets and evaluating trading strategies. Whether you're a quantitative analyst, day trader, or investor, this platform offers:

- **Real-time Data Fetching**: Yahoo Finance integration for live market data
- **Technical Indicators**: 17 different indicators (RSI, MACD, Bollinger Bands, etc.)
- **Risk Metrics**: Comprehensive risk analysis (Sharpe, Sortino, VaR, CVaR, etc.)
- **Backtesting Engine**: Test strategies on historical data with realistic simulations
- **Portfolio Analysis**: Multi-asset portfolio evaluation and optimization
- **Visualizations**: Professional charts and analytics dashboards
- **CLI Interface**: Command-line tools for quick analysis and reports

## Features

### 🔍 Technical Indicators (17 total)
- Simple & Exponential Moving Averages (SMA, EMA)
- Bollinger Bands
- Relative Strength Index (RSI)
- MACD (Moving Average Convergence Divergence)
- Stochastic Oscillator
- Average True Range (ATR)
- On-Balance Volume (OBV)
- Rate of Change (ROC)
- Accumulation/Distribution Line

### 📈 Risk Metrics (12 total)
- Sharpe Ratio & Sortino Ratio
- Volatility & Annualized Return
- Value at Risk (VaR) & Conditional VaR (CVaR)
- Maximum Drawdown & Calmar Ratio
- Information Ratio
- Beta & Alpha
- Correlation Matrix

### 💹 Backtesting Framework
- Pre-built strategies: SMA Crossover, RSI, MACD
- Extensible Strategy base class
- Commission and slippage support
- Comprehensive performance metrics

### 📊 Visualizations
- Price history with volume overlay
- Indicator charts (Bollinger Bands, RSI, MACD)
- Cumulative returns & drawdown analysis
- Risk metrics tables
- Correlation heatmaps
- Portfolio composition pie charts

### ⚙️ Command-Line Interface
```bash
# Analyze single ticker
python -m src.cli analyze --ticker AAPL --period 1y

# Run backtest
python -m src.cli backtest --ticker AAPL --strategy sma

# Generate visualizations
python -m src.cli visualize --ticker AAPL --indicator rsi --output chart.png

# Calculate metrics
python -m src.cli metrics --file data.csv --validate

# Portfolio analysis
python -m src.cli portfolio --tickers AAPL,GOOGL,MSFT
```

## Project Structure

```
my-stats-project/
├── src/
│   ├── __init__.py
│   ├── cli.py                      # Command-line interface
│   ├── data_handler.py             # Data fetching & processing
│   ├── portfolio.py                # Portfolio management
│   ├── risk_metrics.py             # Risk calculations
│   ├── indicators.py               # Technical indicators
│   ├── trading_stats.py            # Trade analysis
│   ├── backtest.py                 # Backtesting engine
│   └── visualizations.py           # Charts & dashboards
├── tests/
│   ├── test_portfolio.py
│   ├── test_risk_metrics.py
│   ├── test_indicators.py
│   ├── test_data_handler.py
│   ├── test_data_handler_extended.py
│   ├── test_trading_stats.py
│   ├── test_backtest.py
│   └── test_visualizations.py
├── examples/
│   ├── example_analysis.py
│   ├── example_backtest.py
│   ├── example_visualizations.py
│   └── example_portfolio.py
├── data/
│   └── sample_data.csv
├── requirements.txt
└── README.md
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m pytest tests/ -v
```

## Quick Start

### Python API

```python
from src.data_handler import fetch_yahoo_data, add_returns_to_dataframe
from src.risk_metrics import calculate_risk_metrics_summary
from src.indicators import calculate_indicators_summary

# Fetch data
df = fetch_yahoo_data('AAPL', period='1y')
df = add_returns_to_dataframe(df, 'close')

# Analyze
metrics = calculate_risk_metrics_summary(df['returns'].dropna())
indicators = calculate_indicators_summary(df)

print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
print(f"RSI: {indicators['RSI']:.2f}")
```

### Command Line

```bash
python -m src.cli analyze --ticker AAPL --period 1y --verbose
python -m src.cli backtest --ticker MSFT --strategy macd --output report.json
python -m src.cli visualize --ticker GOOGL --indicator rsi --output rsi.png
```

## Module Overview

### data_handler.py
Data fetching, processing, and validation
- Yahoo Finance integration
- CSV file loading
- Returns calculation
- Data resampling & interpolation
- Missing value handling

### indicators.py
Technical indicator calculations
- 17 different indicators
- Batch calculation function
- Customizable parameters

### risk_metrics.py
Risk analysis and performance metrics
- 12 comprehensive metrics
- Portfolio correlation analysis
- Benchmark comparison (Beta/Alpha)

### backtest.py
Strategy backtesting engine
- Signal generation framework
- Trade tracking
- Performance calculation
- 3 pre-built strategies

### visualizations.py
Professional charting utilities
- 10+ chart types
- Matplotlib-based
- Publication-quality output

### cli.py
Command-line interface
- 5 main commands
- JSON output support
- Progress indicators

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=src --cov-report=term-missing

# Non-integration only
python -m pytest tests/ -k "not integration"
```

**Coverage:** 87% (exceeds 80% target)  
**Tests:** 102 passing

## Examples

See `examples/` directory for complete walkthroughs:
- `example_analysis.py` - Data analysis
- `example_backtest.py` - Strategy testing
- `example_visualizations.py` - Chart generation
- `example_portfolio.py` - Portfolio optimization

## Requirements

- Python 3.8+
- pandas 2.0+
- numpy 2.0+
- scipy 1.13+
- matplotlib 3.9+
- yfinance 0.2+
- pytest 8.4+

## Version

**v0.1.0** - Initial release (April 2026)

## License

MIT License

## Support

For issues and questions, refer to documentation in README or create an issue in the repository.
