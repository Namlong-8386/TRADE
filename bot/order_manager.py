import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from bot.mexc_client import MEXCClient
from config.settings import TRADING_CONFIG

logger = logging.getLogger(__name__)

class OrderManager:
    """
    Manages trade lifecycle: entry, monitoring, and exit
    """
    
    def __init__(self, client: MEXCClient):
        self.client = client
        self.current_position = None  # Active trade info
        self.entry_price = 0
        self.entry_time = None
        self.order_id = None
        self.position_size = 0
    
    def open_position(self, symbol: str, side: str, amount: float) -> bool:
        """
        Open new position (buy or sell)
        """
        if self.current_position:
            logger.warning("Already have open position, close it first")
            return False
        
        order = self.client.place_market_order(symbol, side, amount)
        if order:
            self.current_position = side
            self.entry_price = order.get('average', 0)
            self.entry_time = datetime.now()
            self.order_id = order.get('id')
            self.position_size = amount
            logger.info(f"Position opened: {side} {amount} @ {self.entry_price}")
            return True
        return False
    
    def close_position(self, symbol: str, current_price: float) -> Dict:
        """
        Close current position and calculate PnL
        """
        if not self.current_position:
            logger.warning("No open position to close")
            return {}
        
        # Opposite side to close position
        side = 'sell' if self.current_position == 'buy' else 'buy'
        
        # Calculate PnL before closing
        pnl_percent = self.calculate_pnl_percent(current_price)
        
        # Close position
        order = self.client.place_market_order(symbol, side, self.position_size)
        
        if order:
            exit_price = order.get('average', current_price)
            trade_result = {
                'entry_price': self.entry_price,
                'exit_price': exit_price,
                'pnl_percent': pnl_percent,
                'trade_duration': (datetime.now() - self.entry_time).total_seconds() / 60,
                'side': self.current_position,
            }
            logger.info(f"Position closed: PnL {pnl_percent:.3f}%")
            
            # Reset
            self.current_position = None
            self.entry_price = 0
            self.entry_time = None
            self.order_id = None
            self.position_size = 0
            
            return trade_result
        return {}
    
    def calculate_pnl_percent(self, current_price: float) -> float:
        """
        Calculate current PnL percentage
        """
        if self.entry_price == 0:
            return 0
        
        if self.current_position == 'buy':
            return ((current_price - self.entry_price) / self.entry_price) * 100
        else:  # sell
            return ((self.entry_price - current_price) / self.entry_price) * 100
    
    def check_take_profit(self, current_price: float) -> bool:
        """
        Check if profit target reached
        """
        if not self.current_position:
            return False
        
        pnl_percent = self.calculate_pnl_percent(current_price)
        target = TRADING_CONFIG['profit_target_percent']
        
        if pnl_percent >= target:
            logger.info(f"Take profit reached: {pnl_percent:.3f}% >= {target}%")
            return True
        return False
    
    def check_stop_loss(self, current_price: float) -> bool:
        """
        Check if stop loss triggered
        """
        if not self.current_position:
            return False
        
        pnl_percent = self.calculate_pnl_percent(current_price)
        stop = -TRADING_CONFIG['stop_loss_percent']
        
        if pnl_percent <= stop:
            logger.warning(f"Stop loss triggered: {pnl_percent:.3f}% <= {stop}%")
            return True
        return False
    
    def check_timeout(self) -> bool:
        """
        Check if trade exceeded max duration
        """
        if not self.entry_time:
            return False
        
        duration_minutes = (datetime.now() - self.entry_time).total_seconds() / 60
        max_duration = TRADING_CONFIG['max_trade_duration_minutes']
        
        if duration_minutes >= max_duration:
            logger.info(f"Trade timeout: {duration_minutes:.1f}m >= {max_duration}m")
            return True
        return False
    
    def has_open_position(self) -> bool:
        """
        Check if there's an open position
        """
        return self.current_position is not None
