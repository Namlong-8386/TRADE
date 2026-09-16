import logging
import ccxt
import time
from typing import Dict, List, Optional
from config.settings import MEXC_API_KEY, MEXC_API_SECRET

logger = logging.getLogger(__name__)

class MEXCClient:
    """
    MEXC Futures Trading Client
    Handles API connections, data fetching, and order placement
    """
    
    def __init__(self):
        self.exchange = ccxt.mexc({
            'apiKey': MEXC_API_KEY,
            'secret': MEXC_API_SECRET,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'swap',  # Futures
            }
        })
        logger.info("MEXC Client initialized")
    
    def fetch_ohlcv(self, symbol: str, timeframe: str = '5m', limit: int = 100) -> List:
        """
        Fetch OHLCV data from MEXC
        Returns: List of [timestamp, open, high, low, close, volume]
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            logger.debug(f"Fetched {len(ohlcv)} candles for {symbol}")
            return ohlcv
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return []
    
    def get_balance(self) -> Dict:
        """
        Get account balance
        Returns: {currency: {free, used, total}}
        """
        try:
            balance = self.exchange.fetch_balance()
            logger.info(f"Balance fetched")
            return balance
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return {}
    
    def place_market_order(self, symbol: str, side: str, amount: float) -> Optional[Dict]:
        """
        Place market order
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            side: 'buy' or 'sell'
            amount: Quantity to trade
        Returns: Order dict or None
        """
        try:
            order = self.exchange.create_market_order(symbol, side, amount)
            logger.info(f"Order placed: {side} {amount} {symbol} at market price")
            logger.info(f"Order ID: {order.get('id')}")
            return order
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def place_limit_order(self, symbol: str, side: str, amount: float, price: float) -> Optional[Dict]:
        """
        Place limit order
        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            amount: Quantity
            price: Limit price
        Returns: Order dict or None
        """
        try:
            order = self.exchange.create_limit_order(symbol, side, amount, price)
            logger.info(f"Limit order placed: {side} {amount} {symbol} @ {price}")
            logger.info(f"Order ID: {order.get('id')}")
            return order
        except Exception as e:
            logger.error(f"Error placing limit order: {e}")
            return None
    
    def cancel_order(self, order_id: str, symbol: str) -> Optional[Dict]:
        """
        Cancel open order
        """
        try:
            result = self.exchange.cancel_order(order_id, symbol)
            logger.info(f"Order {order_id} cancelled")
            return result
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return None
    
    def get_open_orders(self, symbol: str) -> List:
        """
        Get all open orders for symbol
        """
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            logger.debug(f"Found {len(orders)} open orders for {symbol}")
            return orders
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            return []
    
    def get_order_status(self, order_id: str, symbol: str) -> Optional[Dict]:
        """
        Get order status
        """
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return order
        except Exception as e:
            logger.error(f"Error fetching order status: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current price
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['close']
            logger.debug(f"Current price for {symbol}: {price}")
            return price
        except Exception as e:
            logger.error(f"Error fetching ticker: {e}")
            return None
