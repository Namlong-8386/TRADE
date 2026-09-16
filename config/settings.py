import os
from dotenv import load_dotenv

load_dotenv()

# MEXC API Config
MEXC_API_KEY = os.getenv('MEXC_API_KEY', '')
MEXC_API_SECRET = os.getenv('MEXC_API_SECRET', '')

# Trading Strategy Config
TRADING_CONFIG = {
    'symbol': 'BTC/USDT',  # Trading pair
    'timeframe': '5m',  # 5 minute candles
    'position_size_percent': 1.0,  # 100% all-in
    'profit_target_percent': 0.3,  # 0.3% profit target
    'stop_loss_percent': 0.5,  # 0.5% stop loss
    'max_trade_duration_minutes': 20,  # Close after 20 min
    'min_trade_interval_minutes': 40,  # Trade every 40-89 min
    'max_trade_interval_minutes': 89,
}

# Telegram Bot Config
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# Backtest Config
BACKTEST_CONFIG = {
    'start_capital': 10000,  # Starting USDT
    'commission': 0.0005,  # 0.05% commission
    'slippage_percent': 0.01,  # 0.01% slippage
}

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = 'logs/trading.log'

# Data
DATA_PATH = 'data/historical/'
