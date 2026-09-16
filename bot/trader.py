import logging
import random
from datetime import datetime, timedelta
from bot.mexc_client import MEXCClient
from bot.order_manager import OrderManager
from config.settings import TRADING_CONFIG, BACKTEST_CONFIG

logger = logging.getLogger(__name__)

class Trader:
    """
    Main trading logic and decision making
    """
    
    def __init__(self, client: MEXCClient):
        self.client = client
        self.order_manager = OrderManager(client)
        self.last_trade_time = None
        self.trade_history = []
    
    def should_trade(self) -> bool:
        """
        Check if enough time has passed since last trade
        Interval: 40-89 minutes
        """
        if self.last_trade_time is None:
            return True
        
        elapsed_minutes = (datetime.now() - self.last_trade_time).total_seconds() / 60
        min_interval = TRADING_CONFIG['min_trade_interval_minutes']
        max_interval = TRADING_CONFIG['max_trade_interval_minutes']
        
        if elapsed_minutes >= max_interval:
            return True
        
        if elapsed_minutes >= min_interval and self.random_trigger():
            return True
        
        return False
    
    def random_trigger(self) -> bool:
        """
        Random trigger between min and max interval
        """
        min_interval = TRADING_CONFIG['min_trade_interval_minutes']
        max_interval = TRADING_CONFIG['max_trade_interval_minutes']
        random_interval = random.randint(min_interval, max_interval)
        
        elapsed_minutes = (datetime.now() - self.last_trade_time).total_seconds() / 60
        return elapsed_minutes >= random_interval
    
    def calculate_position_size(self, balance: float, price: float) -> float:
        """
        Calculate position size (all-in strategy)
        """
        size_percent = TRADING_CONFIG['position_size_percent']
        amount = (balance * size_percent) / price
        return amount
    
    def get_entry_signal(self, symbol: str) -> str:
        """
        Generate entry signal (buy/sell)
        Simple version: randomize direction
        Can be replaced with actual strategy logic
        """
        # Fetch latest candles for analysis
        ohlcv = self.client.fetch_ohlcv(symbol, TRADING_CONFIG['timeframe'], limit=20)
        
        if not ohlcv:
            logger.warning("Cannot fetch OHLCV data")
            return None
        
        # Simple signal: if last candle is green (close > open), buy; else sell
        last_candle = ohlcv[-1]
        open_price = last_candle[1]
        close_price = last_candle[4]
        
        if close_price > open_price:
            logger.info("Buy signal generated")
            return 'buy'
        else:
            logger.info("Sell signal generated")
            return 'sell'
    
    def execute_trade(self, symbol: str) -> bool:
        """
        Execute complete trade cycle:
        1. Check interval
        2. Generate signal
        3. Open position
        4. Monitor until exit
        5. Close position
        """
        if not self.should_trade():
            return False
        
        # Get balance
        balance_dict = self.client.get_balance()
        usdt_balance = balance_dict.get('USDT', {}).get('free', 0)
        
        if usdt_balance <= 0:
            logger.error("Insufficient balance")
            return False
        
        # Get current price
        current_price = self.client.get_current_price(symbol)
        if not current_price:
            logger.error("Cannot fetch current price")
            return False
        
        # Generate entry signal
        signal = self.get_entry_signal(symbol)
        if not signal:
            return False
        
        # Calculate position size (all-in)
        position_size = self.calculate_position_size(usdt_balance, current_price)
        
        # Open position
        if not self.order_manager.open_position(symbol, signal, position_size):
            return False
        
        self.last_trade_time = datetime.now()
        logger.info(f"Trade started: {signal} {position_size:.6f} @ {current_price}")
        
        return True
    
    def monitor_position(self, symbol: str) -> bool:
        """
        Monitor open position and decide exit
        Returns True if position was closed
        """
        if not self.order_manager.has_open_position():
            return False
        
        current_price = self.client.get_current_price(symbol)
        if not current_price:
            return False
        
        # Check exit conditions
        if (self.order_manager.check_take_profit(current_price) or
            self.order_manager.check_stop_loss(current_price) or
            self.order_manager.check_timeout()):
            
            trade_result = self.order_manager.close_position(symbol, current_price)
            if trade_result:
                self.trade_history.append(trade_result)
                logger.info(f"Trade closed with {trade_result['pnl_percent']:.3f}% PnL")
                return True
        
        return False
    
    def get_statistics(self) -> dict:
        """
        Calculate trading statistics
        """
        if not self.trade_history:
            return {}
        
        total_trades = len(self.trade_history)
        wins = sum(1 for t in self.trade_history if t['pnl_percent'] > 0)
        losses = sum(1 for t in self.trade_history if t['pnl_percent'] < 0)
        total_pnl = sum(t['pnl_percent'] for t in self.trade_history)
        avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'total_pnl_percent': total_pnl,
            'avg_pnl_percent': avg_pnl,
        }
