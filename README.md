# TRADE - Automated Futures Trading Bot

Automated Telegram Bot for MEXC Futures trading with AI-powered backtesting and risk management.

## 🎯 Trading Strategy

- **Trade Frequency:** Every 40-89 minutes
- **Position Size:** All-in (100% available capital)
- **Profit Target:** 0.1-0.5% per trade
- **Trade Duration:** 5-20 minutes
- **Goal:** Consistent daily profitability (few % daily gains)

## 📊 Backtesting Timeframes

- 7 days
- 30 days
- 1 year
- 2 years
- 3 years

## 🏗️ Project Structure

```
TRADE/
├── config/
│   └── settings.py          # API keys & trading params
├── bot/
│   ├── mexc_client.py       # MEXC API wrapper
│   ├── trader.py            # Core trading logic
│   ├── scheduler.py         # 40-89 min scheduler
│   └── order_manager.py     # Order execution
├── backtest/
│   ├── engine.py            # Backtest simulator
│   ├── strategies.py        # Strategy definitions
│   └── data_loader.py       # OHLCV data fetching
├── strategies/
│   ├── scalping.py          # Scalping strategy
│   ├── rsi_ema.py           # RSI-EMA strategy (67.9% win rate)
│   └── trend_follow.py      # Trend following
├── data/
│   └── historical/          # Downloaded OHLCV data
├── tests/
│   └── test_backtest.py
├── main.py                  # Live bot entry point
├── run_backtest.py          # Backtest entry point
├── requirements.txt         # Python dependencies
└── .gitignore
```

## 🚀 Quick Start

### 1. Setup
```bash
pip install -r requirements.txt
```

### 2. Configuration
Edit `config/settings.py` with your MEXC API keys

### 3. Backtest
```bash
python run_backtest.py --strategy rsi_ema --days 30
```

### 4. Live Trading
```bash
python main.py
```

## 📝 License

MIT
