import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List
import random
from config.settings import TRADING_CONFIG, BACKTEST_CONFIG

logger = logging.getLogger(__name__)

class BacktestEngine:
    """
    Backtesting engine for trading strategies
    """
    
    def __init__(self, df: pd.DataFrame, start_capital: float = 10000):
        self.df = df.copy()
        self.start_capital = start_capital
        self.current_capital = start_capital
        self.trades = []
        self.position = None  # Current position info
        self.entry_idx = None  # Index of entry candle
    
    def run_backtest(self, strategy) -> Dict:
        """
        Run backtest with given strategy
        """
        logger.info(f"Running backtest on {len(self.df)} candles")
        logger.info(f"Start capital: ${self.start_capital}")
        
        # Add strategy indicators
        self.df = strategy.calculate_indicators(self.df)
        
        # Process each candle
        for idx, row in self.df.iterrows():
            current_price = row['close']
            
            # Monitor existing position
            if self.position:
                self.check_exit_signal(idx, row, strategy)
            
            # Look for entry signals
            if not self.position:
                signal = strategy.get_signal(self.df, idx)
                if signal:
                    self.open_position(idx, signal, current_price)
        
        # Close any remaining position at end
        if self.position and len(self.df) > 0:
            last_row = self.df.iloc[-1]
            self.close_position(len(self.df) - 1, last_row['close'], 'end_of_backtest')
        
        return self.get_results()
    
    def open_position(self, idx: int, signal: str, price: float):
        """
        Open new position
        """
        if self.position:
            return
        
        # Calculate position size (all-in)
        position_size = self.current_capital / price
        
        self.position = {
            'side': signal,
            'entry_idx': idx,
            'entry_price': price,
            'size': position_size,
            'entry_time': self.df.iloc[idx]['datetime'],
        }
        
        logger.debug(f"[{idx}] Opened {signal} position: {position_size:.6f} @ ${price}")
    
    def close_position(self, idx: int, price: float, reason: str) -> float:
        """
        Close current position and calculate PnL
        Returns: PnL in dollars
        """
        if not self.position:
            return 0
        
        # Calculate exit value
        exit_value = self.position['size'] * price
        
        # Apply commission
        commission = exit_value * BACKTEST_CONFIG['commission']
        exit_value -= commission
        
        # Calculate PnL
        entry_value = self.position['size'] * self.position['entry_price']
        pnl = exit_value - entry_value
        pnl_percent = (pnl / entry_value) * 100 if entry_value > 0 else 0
        
        # Update capital
        self.current_capital += pnl
        
        # Record trade
        trade = {
            'entry_idx': self.position['entry_idx'],
            'exit_idx': idx,
            'entry_time': self.position['entry_time'],
            'exit_time': self.df.iloc[idx]['datetime'],
            'side': self.position['side'],
            'entry_price': self.position['entry_price'],
            'exit_price': price,
            'size': self.position['size'],
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'reason': reason,
        }
        self.trades.append(trade)
        
        logger.debug(f"[{idx}] Closed position: PnL ${pnl:.2f} ({pnl_percent:.3f}%) - {reason}")
        
        self.position = None
        return pnl
    
    def check_exit_signal(self, idx: int, row: pd.Series, strategy):
        """
        Check if should exit current position
        """
        current_price = row['close']
        entry_price = self.position['entry_price']
        
        # Calculate PnL
        if self.position['side'] == 'buy':
            pnl_percent = ((current_price - entry_price) / entry_price) * 100
        else:  # sell
            pnl_percent = ((entry_price - current_price) / entry_price) * 100
        
        # Check take profit
        if pnl_percent >= TRADING_CONFIG['profit_target_percent']:
            self.close_position(idx, current_price, 'take_profit')
            return
        
        # Check stop loss
        if pnl_percent <= -TRADING_CONFIG['stop_loss_percent']:
            self.close_position(idx, current_price, 'stop_loss')
            return
        
        # Check timeout
        duration_candles = idx - self.position['entry_idx']
        # Assuming 5-minute candles
        duration_minutes = duration_candles * 5
        if duration_minutes >= TRADING_CONFIG['max_trade_duration_minutes']:
            self.close_position(idx, current_price, 'timeout')
            return
    
    def get_results(self) -> Dict:
        """
        Calculate final backtest results
        """
        if not self.trades:
            logger.warning("No trades executed during backtest")
            return {}
        
        trades_df = pd.DataFrame(self.trades)
        
        total_trades = len(self.trades)
        wins = len(trades_df[trades_df['pnl'] > 0])
        losses = len(trades_df[trades_df['pnl'] < 0])
        total_pnl = trades_df['pnl'].sum()
        total_pnl_percent = trades_df['pnl_percent'].sum()
        avg_pnl_percent = trades_df['pnl_percent'].mean()
        max_win = trades_df['pnl'].max()
        max_loss = trades_df['pnl'].min()
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        # Calculate final return
        final_return_percent = ((self.current_capital - self.start_capital) / self.start_capital) * 100
        
        results = {
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate_percent': win_rate,
            'total_pnl_dollars': total_pnl,
            'total_pnl_percent': total_pnl_percent,
            'avg_pnl_percent': avg_pnl_percent,
            'max_win_dollars': max_win,
            'max_loss_dollars': max_loss,
            'start_capital': self.start_capital,
            'final_capital': self.current_capital,
            'final_return_percent': final_return_percent,
            'trades': self.trades,
        }
        
        logger.info(f"Backtest Results:")
        logger.info(f"  Total Trades: {total_trades}")
        logger.info(f"  Win Rate: {win_rate:.1f}%")
        logger.info(f"  Total PnL: ${total_pnl:.2f} ({total_pnl_percent:.2f}%)")
        logger.info(f"  Final Capital: ${self.current_capital:.2f}")
        logger.info(f"  Final Return: {final_return_percent:.2f}%")
        
        return results
