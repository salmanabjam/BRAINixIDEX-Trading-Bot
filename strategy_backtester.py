"""
📊 Strategy Backtester with Visualization
Backtest trading strategies and visualize signals on charts

Features:
- Historical signal visualization
- Win/Loss statistics
- Performance metrics
- Future signal prediction
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class StrategyBacktester:
    """Backtest trading strategy and visualize results"""
    
    def __init__(self, initial_capital: float = 10000):
        """
        Initialize backtester
        
        Args:
            initial_capital: Starting capital in USD
        """
        self.initial_capital = initial_capital
        self.trades = []
        self.equity_curve = []
    
    def run_backtest(
        self,
        df: pd.DataFrame,
        predictions: np.ndarray,
        commission: float = 0.001
    ) -> Dict:
        """
        Run backtest on historical data
        
        Args:
            df: DataFrame with OHLCV data
            predictions: Array of predictions (-1, 0, 1)
            commission: Trading commission (0.1% = 0.001)
            
        Returns:
            Dictionary with backtest results
        """
        # Align predictions with dataframe
        # Predictions might be shorter due to indicator calculation
        df = df.copy()
        
        # Reset index to get timestamp as column
        if 'timestamp' not in df.columns:
            df = df.reset_index()
        
        # Pad predictions with 0 (HOLD) at the beginning
        if len(predictions) < len(df):
            padding = np.zeros(len(df) - len(predictions))
            predictions = np.concatenate([padding, predictions])
        
        df['prediction'] = predictions[:len(df)]
        
        capital = self.initial_capital
        position = 0  # 0 = no position, 1 = long, -1 = short
        entry_price = 0
        entry_time = None
        trades = []
        equity = [capital]
        
        for i in range(len(df)):
            current_price = df.iloc[i]['close']
            signal = df.iloc[i]['prediction']
            
            # Close existing position if signal changes
            if position != 0 and signal != position:
                # Calculate profit/loss
                if position == 1:  # Close long
                    profit = (current_price - entry_price) / entry_price
                else:  # Close short
                    profit = (entry_price - current_price) / entry_price
                
                # Apply commission
                profit -= commission * 2  # Entry + exit
                
                capital *= (1 + profit)
                
                trades.append({
                    'entry_time': entry_time,
                    'exit_time': df.iloc[i]['timestamp'],
                    'entry_price': entry_price,
                    'exit_price': current_price,
                    'position': 'LONG' if position == 1 else 'SHORT',
                    'profit_pct': profit * 100,
                    'profit_usd': capital - equity[-1],
                    'result': 'WIN' if profit > 0 else 'LOSS'
                })
                
                position = 0
            
            # Open new position
            if position == 0 and signal != 0:
                position = signal
                entry_price = current_price
                entry_time = df.iloc[i]['timestamp']
            
            equity.append(capital)
        
        # Close final position if open
        if position != 0:
            current_price = df.iloc[-1]['close']
            if position == 1:
                profit = (current_price - entry_price) / entry_price
            else:
                profit = (entry_price - current_price) / entry_price
            
            profit -= commission * 2
            capital *= (1 + profit)
            
            trades.append({
                'entry_time': entry_time,
                'exit_time': df.iloc[-1]['timestamp'],
                'entry_price': entry_price,
                'exit_price': current_price,
                'position': 'LONG' if position == 1 else 'SHORT',
                'profit_pct': profit * 100,
                'profit_usd': capital - equity[-1],
                'result': 'WIN' if profit > 0 else 'LOSS'
            })
        
        self.trades = trades
        self.equity_curve = equity
        
        # Calculate metrics
        if len(trades) > 0:
            wins = [t for t in trades if t['result'] == 'WIN']
            losses = [t for t in trades if t['result'] == 'LOSS']
            
            win_rate = len(wins) / len(trades) * 100
            avg_win = np.mean([t['profit_pct'] for t in wins]) if wins else 0
            avg_loss = np.mean([t['profit_pct'] for t in losses]) if losses else 0
            
            total_return = (capital - self.initial_capital) / self.initial_capital * 100
            
            # Sharpe ratio approximation
            returns = [t['profit_pct'] for t in trades]
            sharpe = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
            
            # Max drawdown
            equity_array = np.array(equity)
            running_max = np.maximum.accumulate(equity_array)
            drawdown = (equity_array - running_max) / running_max * 100
            max_drawdown = np.min(drawdown)
            
            results = {
                'total_trades': len(trades),
                'winning_trades': len(wins),
                'losing_trades': len(losses),
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'total_return': total_return,
                'final_capital': capital,
                'sharpe_ratio': sharpe,
                'max_drawdown': max_drawdown,
                'trades': trades,
                'equity_curve': equity
            }
        else:
            results = {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'total_return': 0,
                'final_capital': self.initial_capital,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'trades': [],
                'equity_curve': equity
            }
        
        return results
    
    def create_chart(
        self,
        df: pd.DataFrame,
        predictions: np.ndarray,
        backtest_results: Dict,
        symbol: str = "BTCUSDT"
    ) -> go.Figure:
        """
        Create interactive chart with signals and backtest results
        
        Args:
            df: DataFrame with OHLCV data
            predictions: Array of predictions
            backtest_results: Results from run_backtest()
            symbol: Trading symbol
            
        Returns:
            Plotly figure
        """
        df = df.copy()
        
        # Reset index to get timestamp
        if 'timestamp' not in df.columns:
            df = df.reset_index()
        
        # Align predictions
        if len(predictions) < len(df):
            padding = np.zeros(len(df) - len(predictions))
            predictions = np.concatenate([padding, predictions])
        
        df['prediction'] = predictions[:len(df)]
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            row_heights=[0.5, 0.25, 0.25],
            subplot_titles=(
                f'{symbol} - Price & Signals',
                'Win/Loss Distribution',
                'Equity Curve'
            ),
            vertical_spacing=0.08
        )
        
        # 1. Candlestick chart with signals
        fig.add_trace(
            go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='Price',
                increasing_line_color='green',
                decreasing_line_color='red'
            ),
            row=1, col=1
        )
        
        # Add BUY signals
        buy_signals = df[df['prediction'] == 1]
        fig.add_trace(
            go.Scatter(
                x=buy_signals['timestamp'],
                y=buy_signals['low'] * 0.998,
                mode='markers',
                name='BUY Signal',
                marker=dict(
                    symbol='triangle-up',
                    size=12,
                    color='lime',
                    line=dict(color='green', width=1)
                )
            ),
            row=1, col=1
        )
        
        # Add SELL signals
        sell_signals = df[df['prediction'] == -1]
        fig.add_trace(
            go.Scatter(
                x=sell_signals['timestamp'],
                y=sell_signals['high'] * 1.002,
                mode='markers',
                name='SELL Signal',
                marker=dict(
                    symbol='triangle-down',
                    size=12,
                    color='red',
                    line=dict(color='darkred', width=1)
                )
            ),
            row=1, col=1
        )
        
        # 2. Win/Loss bar chart
        trades = backtest_results['trades']
        if len(trades) > 0:
            trade_nums = list(range(1, len(trades) + 1))
            profits = [t['profit_pct'] for t in trades]
            colors = ['green' if p > 0 else 'red' for p in profits]
            
            fig.add_trace(
                go.Bar(
                    x=trade_nums,
                    y=profits,
                    name='Trade P&L',
                    marker_color=colors,
                    showlegend=False
                ),
                row=2, col=1
            )
        
        # 3. Equity curve
        equity = backtest_results['equity_curve']
        fig.add_trace(
            go.Scatter(
                x=list(range(len(equity))),
                y=equity,
                name='Equity',
                line=dict(color='blue', width=2),
                fill='tozeroy',
                fillcolor='rgba(0,100,255,0.1)'
            ),
            row=3, col=1
        )
        
        # Add initial capital line
        fig.add_hline(
            y=self.initial_capital,
            line_dash="dash",
            line_color="gray",
            row=3, col=1
        )
        
        # Update layout
        fig.update_xaxes(title_text="Date", row=1, col=1)
        fig.update_xaxes(title_text="Trade #", row=2, col=1)
        fig.update_xaxes(title_text="Time", row=3, col=1)
        
        fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
        fig.update_yaxes(title_text="Profit %", row=2, col=1)
        fig.update_yaxes(title_text="Capital (USD)", row=3, col=1)
        
        fig.update_layout(
            height=1000,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='x unified'
        )
        
        return fig
    
    def print_summary(self, results: Dict):
        """Print backtest summary"""
        print("\n" + "="*70)
        print("📊 BACKTEST RESULTS SUMMARY")
        print("="*70)
        
        print(f"\n💼 Trading Performance:")
        print(f"   Total Trades:     {results['total_trades']}")
        print(f"   Winning Trades:   {results['winning_trades']} ✅")
        print(f"   Losing Trades:    {results['losing_trades']} ❌")
        print(f"   Win Rate:         {results['win_rate']:.2f}%")
        
        print(f"\n💰 Profit/Loss:")
        print(f"   Total Return:     {results['total_return']:.2f}%")
        print(f"   Initial Capital:  ${self.initial_capital:,.2f}")
        print(f"   Final Capital:    ${results['final_capital']:,.2f}")
        print(f"   Net Profit:       ${results['final_capital'] - self.initial_capital:,.2f}")
        
        print(f"\n📈 Trade Analysis:")
        print(f"   Avg Win:          {results['avg_win']:.2f}%")
        print(f"   Avg Loss:         {results['avg_loss']:.2f}%")
        print(f"   Sharpe Ratio:     {results['sharpe_ratio']:.2f}")
        print(f"   Max Drawdown:     {results['max_drawdown']:.2f}%")
        
        print("\n" + "="*70)


if __name__ == "__main__":
    # Test backtester
    from data_handler import DataHandler
    from indicators import TechnicalIndicators
    from ml_engine import MLEngine
    
    print("📊 Testing Strategy Backtester...\n")
    
    # Fetch data
    handler = DataHandler()
    df = handler.fetch_ohlcv(symbol="BTCUSDT", timeframe="1h", limit=500)
    
    # Calculate indicators
    indicators = TechnicalIndicators(df)
    df_with_indicators = indicators.calculate_all()
    
    # Get predictions
    ml_engine = MLEngine(timeframe="1h")
    ml_engine.auto_load_or_train(df_with_indicators)
    predictions = ml_engine.predict(df_with_indicators)
    
    # Run backtest
    backtester = StrategyBacktester(initial_capital=10000)
    results = backtester.run_backtest(df_with_indicators, predictions)
    
    # Print summary
    backtester.print_summary(results)
    
    # Create chart
    fig = backtester.create_chart(df_with_indicators, predictions, results)
    fig.write_html("backtest_chart.html")
    print("\n✅ Chart saved to: backtest_chart.html")
