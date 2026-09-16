import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Tuple
import ccxt

logger = logging.getLogger(__name__)

class DataLoader:
    """
    Load historical OHLCV data from MEXC
    """
    
    def __init__(self):
        self.exchange = ccxt.mexc({
            'enableRateLimit': True,
            'options': {'defaultType': 'swap'}
        })
    
    def fetch_historical_data(self, symbol: str, timeframe: str, 
                            start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Fetch historical OHLCV data
        """
        logger.info(f"Fetching {symbol} data from {start_date} to {end_date}")
        
        all_ohlcv = []
        current_date = start_date
        
        while current_date < end_date:
            try:
                # Fetch data
                ohlcv = self.exchange.fetch_ohlcv(
                    symbol, 
                    timeframe, 
                    since=int(current_date.timestamp() * 1000),
                    limit=1000
                )
                
                if not ohlcv:
                    break
                
                all_ohlcv.extend(ohlcv)
                
                # Update date for next batch
                last_timestamp = ohlcv[-1][0]
                current_date = datetime.fromtimestamp(last_timestamp / 1000)
                
                logger.debug(f"Fetched {len(ohlcv)} candles up to {current_date}")
                
            except Exception as e:
                logger.error(f"Error fetching data: {e}")
                break
        
        # Convert to DataFrame
        df = pd.DataFrame(
            all_ohlcv,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        
        # Convert timestamp to datetime
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('datetime').reset_index(drop=True)
        
        logger.info(f"Loaded {len(df)} candles for {symbol}")
        return df
    
    def load_csv(self, filepath: str) -> pd.DataFrame:
        """
        Load data from CSV file
        """
        try:
            df = pd.read_csv(filepath)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.sort_values('datetime').reset_index(drop=True)
            logger.info(f"Loaded {len(df)} rows from {filepath}")
            return df
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            return pd.DataFrame()
    
    def save_csv(self, df: pd.DataFrame, filepath: str):
        """
        Save data to CSV
        """
        try:
            df.to_csv(filepath, index=False)
            logger.info(f"Saved {len(df)} rows to {filepath}")
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")
