import logging
import time
import random
from datetime import datetime
from bot.mexc_client import MEXCClient
from bot.trader import Trader
from config.settings import TRADING_CONFIG

logger = logging.getLogger(__name__)

class TradingScheduler:
    """
    Schedule trades at 40-89 minute intervals
    """
    
    def __init__(self, symbol: str = 'BTC/USDT'):
        self.client = MEXCClient()
        self.trader = Trader(self.client)
        self.symbol = symbol
        self.is_running = False
    
    def get_next_trade_delay(self) -> int:
        """
        Get random delay between min and max interval (in seconds)
        """
        min_minutes = TRADING_CONFIG['min_trade_interval_minutes']
        max_minutes = TRADING_CONFIG['max_trade_interval_minutes']
        delay_minutes = random.randint(min_minutes, max_minutes)
        delay_seconds = delay_minutes * 60
        
        logger.info(f"Next trade scheduled in {delay_minutes} minutes ({delay_seconds}s)")
        return delay_seconds
    
    def run(self):
        """
        Main loop: execute trades and monitor positions
        """
        self.is_running = True
        logger.info(f"Trading scheduler started for {self.symbol}")
        
        try:
            while self.is_running:
                # Try to execute new trade
                self.trader.execute_trade(self.symbol)
                
                # Monitor existing position
                self.trader.monitor_position(self.symbol)
                
                # Print statistics
                stats = self.trader.get_statistics()
                if stats:
                    logger.info(f"Stats: {stats['total_trades']} trades, "
                              f"{stats['win_rate']:.1f}% win rate, "
                              f"{stats['total_pnl_percent']:.2f}% total PnL")
                
                # Wait before checking again
                time.sleep(60)  # Check every minute
        
        except KeyboardInterrupt:
            logger.info("Trading scheduler stopped by user")
        except Exception as e:
            logger.error(f"Trading scheduler error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """
        Stop the scheduler
        """
        self.is_running = False
        logger.info("Trading scheduler stopped")
