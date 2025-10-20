"""
BiX TradeBOT - Risk Management Module
======================================
Position sizing, stop loss, and capital allocation logic.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import pandas as pd
import logging
from config import Config

logger = logging.getLogger(__name__)


class RiskManager:
    """
    Manages trading risk with ATR-based position sizing
    and dynamic stop loss.
    """

    def __init__(self, initial_capital=None):
        """
        Initialize risk manager.

        Args:
            initial_capital (float): Starting capital in USD
        """
        self.initial_capital = initial_capital or Config.INITIAL_CAPITAL
        self.current_equity = self.initial_capital
        self.positions = []
        self.trade_history = []

        logger.info(
            f"💼 Risk Manager initialized with "
            f"${self.initial_capital:,.2f} capital"
        )

    def calculate_position_size(self, entry_price, atr, direction='long'):
        """
        Calculate position size based on ATR and risk per trade.

        Formula:
        Position Size = (Equity × Risk%) / (ATR × Stop Multiplier)

        Args:
            entry_price (float): Entry price for the trade
            atr (float): Current Average True Range
            direction (str): 'long' or 'short'

        Returns:
            dict: {
                'size': position size in base currency,
                'value': position value in USD,
                'stop_loss': stop loss price,
                'take_profit': take profit price
            }
        """
        # Risk amount in USD
        risk_amount = self.current_equity * Config.RISK_PER_TRADE

        # Stop loss distance
        stop_distance = atr * Config.ATR_STOP_MULTIPLIER

        # Position size calculation
        position_size = risk_amount / stop_distance

        # Position value
        position_value = position_size * entry_price

        # Apply max position size constraint
        max_position_value = self.current_equity * Config.MAX_POSITION_SIZE
        if position_value > max_position_value:
            position_value = max_position_value
            position_size = position_value / entry_price
            logger.warning(
                f"⚠️  Position size capped at "
                f"{Config.MAX_POSITION_SIZE*100}% of equity"
            )

        # Calculate stop loss and take profit
        if direction == 'long':
            stop_loss = entry_price - stop_distance
            take_profit = entry_price + (
                stop_distance * Config.RISK_REWARD_RATIO
            )
        else:  # short
            stop_loss = entry_price + stop_distance
            take_profit = entry_price - (
                stop_distance * Config.RISK_REWARD_RATIO
            )

        result = {
            'size': round(position_size, 6),
            'value': round(position_value, 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit': round(take_profit, 2),
            'risk_amount': round(risk_amount, 2)
        }

        logger.debug(
            f"📊 Position: {result['size']} units "
            f"(${result['value']:,.2f}) | "
            f"SL: ${result['stop_loss']:,.2f} | "
            f"TP: ${result['take_profit']:,.2f}"
        )

        return result

    def open_position(self, symbol, entry_price, size, direction,
                      stop_loss, take_profit):
        """
        Record a new position.

        Args:
            symbol (str): Trading pair
            entry_price (float): Entry price
            size (float): Position size
            direction (str): 'long' or 'short'
            stop_loss (float): Stop loss price
            take_profit (float): Take profit price

        Returns:
            dict: Position details
        """
        position = {
            'symbol': symbol,
            'entry_price': entry_price,
            'size': size,
            'direction': direction,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'entry_time': pd.Timestamp.now(),
            'status': 'open'
        }

        self.positions.append(position)
        logger.info(
            f"🟢 Opened {direction.upper()} position: "
            f"{size} {symbol} @ ${entry_price:,.2f}"
        )

        return position

    def close_position(self, position_index, exit_price, exit_reason=''):
        """
        Close an existing position and update equity.

        Args:
            position_index (int): Index of position to close
            exit_price (float): Exit price
            exit_reason (str): Reason for exit (e.g., 'stop_loss')

        Returns:
            dict: Closed trade details
        """
        if position_index >= len(self.positions):
            logger.error(f"❌ Invalid position index: {position_index}")
            return None

        position = self.positions[position_index]

        # Calculate P&L
        if position['direction'] == 'long':
            pnl = (exit_price - position['entry_price']) * position['size']
        else:  # short
            pnl = (position['entry_price'] - exit_price) * position['size']

        # Update equity
        self.current_equity += pnl

        # Record trade
        trade = {
            **position,
            'exit_price': exit_price,
            'exit_time': pd.Timestamp.now(),
            'pnl': round(pnl, 2),
            'pnl_percent': round(
                (pnl / (position['entry_price'] * position['size'])) * 100,
                2
            ),
            'exit_reason': exit_reason,
            'equity_after': round(self.current_equity, 2)
        }

        self.trade_history.append(trade)
        self.positions.pop(position_index)

        pnl_emoji = "💚" if pnl > 0 else "❤️"
        logger.info(
            f"{pnl_emoji} Closed {position['direction'].upper()} position: "
            f"P&L ${pnl:,.2f} ({trade['pnl_percent']}%) | "
            f"Equity: ${self.current_equity:,.2f}"
        )

        return trade

    def check_stop_loss_take_profit(self, current_price):
        """
        Check if any open positions hit stop loss or take profit.

        Args:
            current_price (float): Current market price

        Returns:
            list: Positions to close
        """
        to_close = []

        for i, position in enumerate(self.positions):
            if position['direction'] == 'long':
                if current_price <= position['stop_loss']:
                    to_close.append((i, 'stop_loss'))
                elif current_price >= position['take_profit']:
                    to_close.append((i, 'take_profit'))
            else:  # short
                if current_price >= position['stop_loss']:
                    to_close.append((i, 'stop_loss'))
                elif current_price <= position['take_profit']:
                    to_close.append((i, 'take_profit'))

        return to_close

    def get_performance_stats(self):
        """
        Calculate performance statistics.

        Returns:
            dict: Performance metrics
        """
        if not self.trade_history:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_pnl': 0,
                'profit_factor': 0,
                'equity_return': 0
            }

        df = pd.DataFrame(self.trade_history)

        winning_trades = df[df['pnl'] > 0]
        losing_trades = df[df['pnl'] < 0]

        total_wins = len(winning_trades)
        total_losses = len(losing_trades)
        total_trades = len(df)

        win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0

        gross_profit = winning_trades['pnl'].sum() if total_wins > 0 else 0
        gross_loss = abs(losing_trades['pnl'].sum()) if total_losses > 0 else 1

        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        stats = {
            'total_trades': total_trades,
            'winning_trades': total_wins,
            'losing_trades': total_losses,
            'win_rate': round(win_rate, 2),
            'total_pnl': round(df['pnl'].sum(), 2),
            'avg_win': round(
                winning_trades['pnl'].mean(), 2
            ) if total_wins > 0 else 0,
            'avg_loss': round(
                losing_trades['pnl'].mean(), 2
            ) if total_losses > 0 else 0,
            'profit_factor': round(profit_factor, 2),
            'current_equity': round(self.current_equity, 2),
            'equity_return': round(
                ((self.current_equity - self.initial_capital) /
                 self.initial_capital) * 100,
                2
            )
        }

        return stats

    def export_trade_log(self, filename='trade_log.csv'):
        """Export trade history to CSV"""
        if not self.trade_history:
            logger.warning("⚠️  No trades to export")
            return None

        df = pd.DataFrame(self.trade_history)
        output_path = f"results/{filename}"
        df.to_csv(output_path, index=False)
        logger.info(f"💾 Trade log exported to {output_path}")
        return output_path


if __name__ == "__main__":
    # Test risk manager
    logger.setLevel(logging.DEBUG)

    rm = RiskManager(initial_capital=10000)

    # Calculate position size
    pos_info = rm.calculate_position_size(
        entry_price=50000,
        atr=1000,
        direction='long'
    )

    print("\n📊 Position Sizing:")
    for key, value in pos_info.items():
        print(f"  {key}: {value}")

    # Simulate opening a position
    rm.open_position(
        symbol='BTCUSDT',
        entry_price=50000,
        size=pos_info['size'],
        direction='long',
        stop_loss=pos_info['stop_loss'],
        take_profit=pos_info['take_profit']
    )

    # Simulate closing with profit
    rm.close_position(0, exit_price=52000, exit_reason='take_profit')

    # Performance stats
    stats = rm.get_performance_stats()
    print("\n📈 Performance Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
