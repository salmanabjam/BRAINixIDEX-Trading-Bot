"""
Portfolio Analytics Module
===========================
Track P&L, asset distribution, performance metrics.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass
import pandas as pd


@dataclass
class Position:
    """Trading position."""
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    entry_time: datetime
    
    @property
    def value(self) -> float:
        """Current position value."""
        return self.quantity * self.current_price
    
    @property
    def pnl(self) -> float:
        """Profit/Loss."""
        return (self.current_price - self.entry_price) * self.quantity
    
    @property
    def pnl_percent(self) -> float:
        """P&L percentage."""
        if self.entry_price == 0:
            return 0
        return ((self.current_price / self.entry_price) - 1) * 100


class Portfolio:
    """Portfolio analytics."""
    
    def __init__(self, initial_balance: float = 10000):
        """Initialize portfolio."""
        self.initial_balance = initial_balance
        self.cash = initial_balance
        self.positions: List[Position] = []
        self.trade_history: List[Dict] = []
    
    def add_position(self, position: Position):
        """Add new position."""
        cost = position.quantity * position.entry_price
        if cost > self.cash:
            raise ValueError("Insufficient funds")
        
        self.cash -= cost
        self.positions.append(position)
        
        self.trade_history.append({
            'timestamp': position.entry_time,
            'action': 'BUY',
            'symbol': position.symbol,
            'quantity': position.quantity,
            'price': position.entry_price,
            'cost': cost
        })
    
    def close_position(self, symbol: str, close_price: float):
        """Close position."""
        position = next((p for p in self.positions if p.symbol == symbol),
                       None)
        if not position:
            raise ValueError(f"No position for {symbol}")
        
        value = position.quantity * close_price
        self.cash += value
        self.positions.remove(position)
        
        self.trade_history.append({
            'timestamp': datetime.now(),
            'action': 'SELL',
            'symbol': symbol,
            'quantity': position.quantity,
            'price': close_price,
            'value': value,
            'pnl': position.quantity * (close_price - position.entry_price)
        })
    
    def get_total_value(self) -> float:
        """Get total portfolio value."""
        positions_value = sum(p.value for p in self.positions)
        return self.cash + positions_value
    
    def get_total_pnl(self) -> float:
        """Get total P&L."""
        return self.get_total_value() - self.initial_balance
    
    def get_total_pnl_percent(self) -> float:
        """Get total P&L percentage."""
        return (self.get_total_pnl() / self.initial_balance) * 100
    
    def get_distribution(self) -> Dict[str, float]:
        """Get asset distribution."""
        total = self.get_total_value()
        if total == 0:
            return {}
        
        distribution = {'CASH': (self.cash / total) * 100}
        for pos in self.positions:
            distribution[pos.symbol] = (pos.value / total) * 100
        
        return distribution
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary."""
        return {
            'initial_balance': self.initial_balance,
            'current_value': self.get_total_value(),
            'cash': self.cash,
            'positions_value': sum(p.value for p in self.positions),
            'total_pnl': self.get_total_pnl(),
            'total_pnl_percent': self.get_total_pnl_percent(),
            'num_positions': len(self.positions),
            'num_trades': len(self.trade_history)
        }
    
    def get_positions_df(self) -> pd.DataFrame:
        """Get positions as DataFrame."""
        if not self.positions:
            return pd.DataFrame()
        
        data = []
        for pos in self.positions:
            data.append({
                'Symbol': pos.symbol,
                'Quantity': pos.quantity,
                'Entry Price': pos.entry_price,
                'Current Price': pos.current_price,
                'Value': pos.value,
                'P&L': pos.pnl,
                'P&L %': pos.pnl_percent
            })
        
        return pd.DataFrame(data)
    
    def get_trades_df(self) -> pd.DataFrame:
        """Get trade history as DataFrame."""
        if not self.trade_history:
            return pd.DataFrame()
        
        return pd.DataFrame(self.trade_history)


if __name__ == "__main__":
    portfolio = Portfolio(10000)
    
    # Test position
    pos = Position(
        symbol='BTCUSDT',
        quantity=0.1,
        entry_price=50000,
        current_price=51000,
        entry_time=datetime.now()
    )
    
    portfolio.add_position(pos)
    print("Portfolio Summary:")
    print(portfolio.get_performance_summary())
