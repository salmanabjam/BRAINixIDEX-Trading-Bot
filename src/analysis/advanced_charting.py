"""
Advanced Charting Module
========================
Professional trading charts with indicators, signals, and support/resistance.

Author: SALMAN ThinkTank AI Core (NOVA - UI/UX Designer)
Version: 2.0.0
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class AdvancedTradingChart:
    """
    Professional trading chart with multiple indicators and overlays.
    
    Features:
    - Candlestick charts with volume
    - Multiple indicators (EMA, RSI, MACD, BB, ATR)
    - Buy/Sell signal markers
    - Support/Resistance levels
    - Interactive tooltips
    - Dark theme optimized
    """
    
    def __init__(self, data: pd.DataFrame, symbol: str = 'BTCUSDT'):
        """
        Initialize chart with data.
        
        Args:
            data: OHLCV DataFrame with indicators
            symbol: Trading symbol
        """
        self.data = data.copy()
        self.symbol = symbol
        self.colors = {
            'up': '#26a69a',      # Green for bullish
            'down': '#ef5350',    # Red for bearish
            'ema_fast': '#2962ff', # Blue for fast EMA
            'ema_slow': '#ff6d00', # Orange for slow EMA
            'volume': '#78909c',   # Gray for volume
            'rsi': '#9c27b0',      # Purple for RSI
            'macd': '#00bcd4',     # Cyan for MACD
            'signal': '#ff9800',   # Orange for signal line
            'bb_upper': '#4caf50', # Green for BB upper
            'bb_lower': '#f44336', # Red for BB lower
            'support': '#4caf50',  # Green for support
            'resistance': '#f44336' # Red for resistance
        }
    
    def create_full_analysis_chart(
        self,
        show_ema: bool = True,
        show_bb: bool = True,
        show_signals: bool = True,
        show_support_resistance: bool = True,
        height: int = 1000
    ) -> go.Figure:
        """
        Create comprehensive analysis chart with all features.
        
        Args:
            show_ema: Show EMA lines
            show_bb: Show Bollinger Bands
            show_signals: Show buy/sell signals
            show_support_resistance: Show S/R levels
            height: Chart height in pixels
            
        Returns:
            Plotly figure object
        """
        # Create subplots
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(
                f'{self.symbol} - Price & Indicators',
                'Volume',
                'RSI',
                'MACD'
            ),
            row_heights=[0.5, 0.15, 0.15, 0.2]
        )
        
        # 1. Main Price Chart
        self._add_candlestick(fig, row=1)
        
        if show_ema:
            self._add_ema_lines(fig, row=1)
        
        if show_bb:
            self._add_bollinger_bands(fig, row=1)
        
        if show_signals:
            self._add_buy_sell_signals(fig, row=1)
        
        if show_support_resistance:
            self._add_support_resistance(fig, row=1)
        
        # 2. Volume Chart
        self._add_volume(fig, row=2)
        
        # 3. RSI Chart
        self._add_rsi(fig, row=3)
        
        # 4. MACD Chart
        self._add_macd(fig, row=4)
        
        # Update layout
        fig.update_layout(
            title={
                'text': f'📊 {self.symbol} - Advanced Technical Analysis',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#ffffff'}
            },
            height=height,
            template='plotly_dark',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis_rangeslider_visible=False,
            hovermode='x unified'
        )
        
        # Update axes
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#2a2a2a')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#2a2a2a')
        
        return fig
    
    def _add_candlestick(self, fig: go.Figure, row: int):
        """Add candlestick chart."""
        fig.add_trace(
            go.Candlestick(
                x=self.data.index,
                open=self.data['open'],
                high=self.data['high'],
                low=self.data['low'],
                close=self.data['close'],
                name='Price',
                increasing_line_color=self.colors['up'],
                decreasing_line_color=self.colors['down'],
                showlegend=False
            ),
            row=row, col=1
        )
    
    def _add_ema_lines(self, fig: go.Figure, row: int):
        """Add EMA lines."""
        if 'ema_fast' in self.data.columns:
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data['ema_fast'],
                    name='EMA Fast',
                    line=dict(color=self.colors['ema_fast'], width=2),
                    opacity=0.8
                ),
                row=row, col=1
            )
        
        if 'ema_slow' in self.data.columns:
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data['ema_slow'],
                    name='EMA Slow',
                    line=dict(color=self.colors['ema_slow'], width=2),
                    opacity=0.8
                ),
                row=row, col=1
            )
    
    def _add_bollinger_bands(self, fig: go.Figure, row: int):
        """Add Bollinger Bands."""
        if all(col in self.data.columns for col in ['bb_upper', 'bb_middle', 'bb_lower']):
            # Upper band
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data['bb_upper'],
                    name='BB Upper',
                    line=dict(color=self.colors['bb_upper'], width=1, dash='dot'),
                    opacity=0.5
                ),
                row=row, col=1
            )
            
            # Middle band
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data['bb_middle'],
                    name='BB Middle',
                    line=dict(color='#ffffff', width=1, dash='dot'),
                    opacity=0.3
                ),
                row=row, col=1
            )
            
            # Lower band with fill
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data['bb_lower'],
                    name='BB Lower',
                    line=dict(color=self.colors['bb_lower'], width=1, dash='dot'),
                    fill='tonexty',
                    fillcolor='rgba(128, 128, 128, 0.1)',
                    opacity=0.5
                ),
                row=row, col=1
            )
    
    def _add_buy_sell_signals(self, fig: go.Figure, row: int):
        """Add buy/sell signal markers."""
        # Buy signals
        if 'signal' in self.data.columns:
            buy_signals = self.data[self.data['signal'] == 1]
            if not buy_signals.empty:
                fig.add_trace(
                    go.Scatter(
                        x=buy_signals.index,
                        y=buy_signals['low'] * 0.995,  # Slightly below low
                        mode='markers',
                        name='Buy Signal',
                        marker=dict(
                            symbol='triangle-up',
                            size=15,
                            color=self.colors['up'],
                            line=dict(color='white', width=2)
                        )
                    ),
                    row=row, col=1
                )
            
            # Sell signals
            sell_signals = self.data[self.data['signal'] == -1]
            if not sell_signals.empty:
                fig.add_trace(
                    go.Scatter(
                        x=sell_signals.index,
                        y=sell_signals['high'] * 1.005,  # Slightly above high
                        mode='markers',
                        name='Sell Signal',
                        marker=dict(
                            symbol='triangle-down',
                            size=15,
                            color=self.colors['down'],
                            line=dict(color='white', width=2)
                        )
                    ),
                    row=row, col=1
                )
    
    def _add_support_resistance(self, fig: go.Figure, row: int):
        """Add support/resistance levels."""
        levels = self._calculate_support_resistance()
        
        for level_type, price in levels:
            color = self.colors['support'] if level_type == 'support' else self.colors['resistance']
            name = f'{"Support" if level_type == "support" else "Resistance"}: {price:.2f}'
            
            fig.add_trace(
                go.Scatter(
                    x=[self.data.index[0], self.data.index[-1]],
                    y=[price, price],
                    mode='lines',
                    name=name,
                    line=dict(
                        color=color,
                        width=2,
                        dash='dash'
                    ),
                    opacity=0.6,
                    showlegend=True
                ),
                row=row, col=1
            )
    
    def _calculate_support_resistance(self) -> List[Tuple[str, float]]:
        """
        Calculate support and resistance levels using pivot points.
        
        Returns:
            List of (type, price) tuples
        """
        levels = []
        
        # Use recent data (last 100 candles)
        recent_data = self.data.tail(100)
        
        # Find local maxima (resistance)
        highs = recent_data['high'].values
        for i in range(2, len(highs) - 2):
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and \
               highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                levels.append(('resistance', highs[i]))
        
        # Find local minima (support)
        lows = recent_data['low'].values
        for i in range(2, len(lows) - 2):
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and \
               lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                levels.append(('support', lows[i]))
        
        # Cluster nearby levels (within 0.5% of each other)
        levels = self._cluster_levels(levels)
        
        # Return top 3 support and resistance levels
        support_levels = sorted([l for l in levels if l[0] == 'support'], 
                               key=lambda x: x[1], reverse=True)[:3]
        resistance_levels = sorted([l for l in levels if l[0] == 'resistance'], 
                                   key=lambda x: x[1])[:3]
        
        return support_levels + resistance_levels
    
    def _cluster_levels(self, levels: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """Cluster nearby support/resistance levels."""
        if not levels:
            return []
        
        clustered = []
        levels = sorted(levels, key=lambda x: x[1])
        
        current_cluster = [levels[0]]
        
        for i in range(1, len(levels)):
            if abs(levels[i][1] - current_cluster[0][1]) / current_cluster[0][1] < 0.005:
                current_cluster.append(levels[i])
            else:
                # Average the cluster
                avg_price = np.mean([l[1] for l in current_cluster])
                clustered.append((current_cluster[0][0], avg_price))
                current_cluster = [levels[i]]
        
        # Add last cluster
        if current_cluster:
            avg_price = np.mean([l[1] for l in current_cluster])
            clustered.append((current_cluster[0][0], avg_price))
        
        return clustered
    
    def _add_volume(self, fig: go.Figure, row: int):
        """Add volume bars."""
        colors = [self.colors['up'] if close >= open else self.colors['down'] 
                  for close, open in zip(self.data['close'], self.data['open'])]
        
        fig.add_trace(
            go.Bar(
                x=self.data.index,
                y=self.data['volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.6,
                showlegend=False
            ),
            row=row, col=1
        )
    
    def _add_rsi(self, fig: go.Figure, row: int):
        """Add RSI indicator."""
        if 'rsi' in self.data.columns:
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data['rsi'],
                    name='RSI',
                    line=dict(color=self.colors['rsi'], width=2),
                    showlegend=False
                ),
                row=row, col=1
            )
            
            # Add overbought/oversold lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", 
                         opacity=0.5, row=row, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", 
                         opacity=0.5, row=row, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color="gray", 
                         opacity=0.3, row=row, col=1)
            
            # Update y-axis range
            fig.update_yaxes(range=[0, 100], row=row, col=1)
    
    def _add_macd(self, fig: go.Figure, row: int):
        """Add MACD indicator."""
        if all(col in self.data.columns for col in ['macd', 'macd_signal', 'macd_hist']):
            # MACD line
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data['macd'],
                    name='MACD',
                    line=dict(color=self.colors['macd'], width=2),
                    showlegend=False
                ),
                row=row, col=1
            )
            
            # Signal line
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data['macd_signal'],
                    name='Signal',
                    line=dict(color=self.colors['signal'], width=2),
                    showlegend=False
                ),
                row=row, col=1
            )
            
            # Histogram
            colors = [self.colors['up'] if val >= 0 else self.colors['down'] 
                     for val in self.data['macd_hist']]
            
            fig.add_trace(
                go.Bar(
                    x=self.data.index,
                    y=self.data['macd_hist'],
                    name='Histogram',
                    marker_color=colors,
                    opacity=0.6,
                    showlegend=False
                ),
                row=row, col=1
            )
            
            # Add zero line
            fig.add_hline(y=0, line_dash="dash", line_color="gray", 
                         opacity=0.5, row=row, col=1)
    
    def create_simple_chart(
        self,
        indicators: List[str] = None,
        height: int = 600
    ) -> go.Figure:
        """
        Create simple price chart with selected indicators.
        
        Args:
            indicators: List of indicators to show ['ema', 'bb', 'volume']
            height: Chart height
            
        Returns:
            Plotly figure
        """
        if indicators is None:
            indicators = ['ema', 'volume']
        
        rows = 1 + (1 if 'volume' in indicators else 0)
        
        fig = make_subplots(
            rows=rows, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3] if rows == 2 else [1.0]
        )
        
        # Candlestick
        self._add_candlestick(fig, row=1)
        
        if 'ema' in indicators:
            self._add_ema_lines(fig, row=1)
        
        if 'bb' in indicators:
            self._add_bollinger_bands(fig, row=1)
        
        if 'volume' in indicators and rows == 2:
            self._add_volume(fig, row=2)
        
        fig.update_layout(
            title=f'{self.symbol} - Price Chart',
            height=height,
            template='plotly_dark',
            showlegend=True,
            xaxis_rangeslider_visible=False
        )
        
        return fig


def create_comparison_chart(
    data_dict: Dict[str, pd.DataFrame],
    symbols: List[str],
    height: int = 600
) -> go.Figure:
    """
    Create comparison chart for multiple symbols.
    
    Args:
        data_dict: Dictionary of symbol -> DataFrame
        symbols: List of symbols to compare
        height: Chart height
        
    Returns:
        Plotly figure with normalized prices
    """
    fig = go.Figure()
    
    colors = ['#2962ff', '#ff6d00', '#00bcd4', '#9c27b0', '#4caf50']
    
    for i, symbol in enumerate(symbols):
        if symbol in data_dict:
            data = data_dict[symbol]
            
            # Normalize to percentage change from start
            normalized = (data['close'] / data['close'].iloc[0] - 1) * 100
            
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=normalized,
                    name=symbol,
                    line=dict(color=colors[i % len(colors)], width=2)
                )
            )
    
    fig.update_layout(
        title='📊 Symbol Comparison (% Change)',
        height=height,
        template='plotly_dark',
        yaxis_title='% Change',
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig


if __name__ == "__main__":
    # Example usage
    print("📊 Advanced Charting Module")
    print("=" * 50)
    print("Features:")
    print("  ✅ Candlestick charts")
    print("  ✅ Multiple indicators (EMA, RSI, MACD, BB)")
    print("  ✅ Buy/Sell signals")
    print("  ✅ Support/Resistance levels")
    print("  ✅ Volume analysis")
    print("  ✅ Interactive tooltips")
    print("  ✅ Dark theme optimized")
    print("\nUsage:")
    print("  chart = AdvancedTradingChart(data, 'BTCUSDT')")
    print("  fig = chart.create_full_analysis_chart()")
    print("  fig.show()")
