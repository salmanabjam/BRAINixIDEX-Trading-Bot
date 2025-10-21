"""
Dashboard Chart Integration
============================
Integration module for advanced charts in Streamlit dashboard.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import streamlit as st
import pandas as pd
from typing import Dict, List
from analysis.advanced_charting import AdvancedTradingChart, create_comparison_chart
from data.indicators import TechnicalIndicators


def show_advanced_chart_tab(data: pd.DataFrame, symbol: str):
    """
    Display advanced charting tab in dashboard.
    
    Args:
        data: OHLCV DataFrame with indicators
        symbol: Trading symbol
    """
    st.header("📈 Advanced Technical Charts")
    
    # Chart configuration
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_ema = st.checkbox("Show EMA Lines", value=True)
        show_bb = st.checkbox("Show Bollinger Bands", value=True)
    
    with col2:
        show_signals = st.checkbox("Show Buy/Sell Signals", value=True)
        show_sr = st.checkbox("Show Support/Resistance", value=True)
    
    with col3:
        chart_height = st.slider("Chart Height", 600, 1500, 1000, 50)
    
    # Create chart
    try:
        chart = AdvancedTradingChart(data, symbol)
        fig = chart.create_full_analysis_chart(
            show_ema=show_ema,
            show_bb=show_bb,
            show_signals=show_signals,
            show_support_resistance=show_sr,
            height=chart_height
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Chart insights
        st.subheader("📊 Chart Insights")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            current_price = data['close'].iloc[-1]
            st.metric("Current Price", f"${current_price:,.2f}")
        
        with col2:
            if 'ema_fast' in data.columns and 'ema_slow' in data.columns:
                ema_cross = "Bullish ⬆️" if data['ema_fast'].iloc[-1] > data['ema_slow'].iloc[-1] else "Bearish ⬇️"
                st.metric("EMA Trend", ema_cross)
        
        with col3:
            if 'rsi' in data.columns:
                rsi = data['rsi'].iloc[-1]
                rsi_status = "Overbought 🔴" if rsi > 70 else "Oversold 🟢" if rsi < 30 else "Neutral ⚪"
                st.metric("RSI Status", rsi_status, f"{rsi:.1f}")
        
        with col4:
            if 'volume' in data.columns:
                avg_volume = data['volume'].tail(20).mean()
                current_volume = data['volume'].iloc[-1]
                volume_change = ((current_volume - avg_volume) / avg_volume) * 100
                st.metric("Volume vs Avg", f"{volume_change:+.1f}%")
        
    except Exception as e:
        st.error(f"Error creating chart: {e}")


def show_simple_chart(data: pd.DataFrame, symbol: str, indicators: List[str] = None):
    """
    Display simple chart with basic indicators.
    
    Args:
        data: OHLCV DataFrame
        symbol: Trading symbol
        indicators: List of indicators to show
    """
    if indicators is None:
        indicators = ['ema', 'volume']
    
    try:
        chart = AdvancedTradingChart(data, symbol)
        fig = chart.create_simple_chart(indicators=indicators, height=600)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating chart: {e}")


def show_comparison_chart(data_dict: Dict[str, pd.DataFrame], symbols: List[str]):
    """
    Display comparison chart for multiple symbols.
    
    Args:
        data_dict: Dictionary of symbol -> DataFrame
        symbols: List of symbols to compare
    """
    st.header("📊 Symbol Comparison")
    
    try:
        fig = create_comparison_chart(data_dict, symbols, height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance table
        st.subheader("Performance Metrics")
        
        performance_data = []
        for symbol in symbols:
            if symbol in data_dict:
                data = data_dict[symbol]
                change = ((data['close'].iloc[-1] / data['close'].iloc[0]) - 1) * 100
                performance_data.append({
                    'Symbol': symbol,
                    'Start Price': f"${data['close'].iloc[0]:,.2f}",
                    'End Price': f"${data['close'].iloc[-1]:,.2f}",
                    'Change %': f"{change:+.2f}%"
                })
        
        st.table(pd.DataFrame(performance_data))
        
    except Exception as e:
        st.error(f"Error creating comparison chart: {e}")


def calculate_chart_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all indicators needed for advanced charts.
    
    Args:
        data: OHLCV DataFrame
        
    Returns:
        DataFrame with indicators
    """
    indicators = TechnicalIndicators()
    
    # Calculate all indicators
    data = indicators.add_ema(data, 50, 'ema_fast')
    data = indicators.add_ema(data, 200, 'ema_slow')
    data = indicators.add_rsi(data, 14)
    data = indicators.add_macd(data)
    data = indicators.add_bollinger_bands(data, 20)
    data = indicators.add_atr(data, 14)
    
    return data


if __name__ == "__main__":
    print("📊 Dashboard Chart Integration Module")
    print("=" * 50)
    print("Features:")
    print("  ✅ Advanced chart tab for dashboard")
    print("  ✅ Simple chart display")
    print("  ✅ Symbol comparison")
    print("  ✅ Auto indicator calculation")
    print("  ✅ Chart insights display")
