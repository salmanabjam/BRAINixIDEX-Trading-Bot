"""
Streamlit Real-time Dashboard Integration
==========================================
Integration module for real-time price updates in Streamlit dashboard.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Optional
from datetime import datetime
import time

try:
    from ui.websocket_client import get_streamlit_client
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False


def init_realtime_dashboard():
    """
    Initialize real-time dashboard components.
    
    Sets up WebSocket client in session state.
    """
    if not WEBSOCKET_AVAILABLE:
        st.warning("⚠️ WebSocket module not available. Real-time updates disabled.")
        return False
    
    # Initialize WebSocket client in session state
    if 'realtime_client' not in st.session_state:
        st.session_state.realtime_client = get_streamlit_client(st.session_state)
        st.session_state.realtime_enabled = True
        st.session_state.last_update = None
    
    return True


def show_realtime_status():
    """Display real-time connection status indicator."""
    if not WEBSOCKET_AVAILABLE:
        return
    
    client = st.session_state.get('realtime_client')
    if not client:
        return
    
    # Check connection status
    is_connected = client.is_connected()
    
    # Display status
    if is_connected:
        st.success("🟢 Real-time: Connected")
    else:
        st.error("🔴 Real-time: Disconnected")
    
    # Show last update time
    if st.session_state.get('last_update'):
        st.caption(f"Last update: {st.session_state.last_update}")


def show_realtime_price_ticker(symbols: List[str] = None):
    """
    Display real-time price ticker for multiple symbols.
    
    Args:
        symbols: List of symbols to display (default: top coins)
    """
    if not WEBSOCKET_AVAILABLE:
        st.info("💡 Enable WebSocket server for real-time prices")
        return
    
    client = st.session_state.get('realtime_client')
    if not client:
        init_realtime_dashboard()
        client = st.session_state.get('realtime_client')
    
    # Get all prices
    all_prices = client.get_all_prices()
    
    if not all_prices:
        st.info("⏳ Waiting for real-time data...")
        return
    
    # Filter symbols if specified
    if symbols:
        prices = {s: all_prices[s] for s in symbols if s in all_prices}
    else:
        prices = all_prices
    
    if not prices:
        st.warning("No data available for selected symbols")
        return
    
    # Display in columns
    num_cols = min(5, len(prices))
    cols = st.columns(num_cols)
    
    for idx, (symbol, data) in enumerate(list(prices.items())[:num_cols]):
        with cols[idx]:
            price = data.get('price', 0)
            change_24h = data.get('change_24h', 0)
            
            # Color based on change
            delta_color = "normal" if change_24h >= 0 else "inverse"
            
            st.metric(
                label=symbol,
                value=f"${price:,.2f}",
                delta=f"{change_24h:+.2f}%",
                delta_color=delta_color
            )
    
    # Update timestamp
    st.session_state.last_update = datetime.now().strftime("%H:%M:%S")


def show_realtime_price_chart(
    symbol: str,
    timeframe: str = '1m',
    max_points: int = 100
):
    """
    Display real-time updating price chart.
    
    Args:
        symbol: Trading symbol
        timeframe: Chart timeframe
        max_points: Maximum data points to display
    """
    if not WEBSOCKET_AVAILABLE:
        st.info("💡 Enable WebSocket for real-time charts")
        return
    
    # Initialize price history in session state
    if 'price_history' not in st.session_state:
        st.session_state.price_history = {}
    
    if symbol not in st.session_state.price_history:
        st.session_state.price_history[symbol] = {
            'timestamps': [],
            'prices': []
        }
    
    client = st.session_state.get('realtime_client')
    if not client:
        return
    
    # Get latest price
    price = client.get_price(symbol)
    
    if price:
        # Add to history
        history = st.session_state.price_history[symbol]
        history['timestamps'].append(datetime.now())
        history['prices'].append(price)
        
        # Limit history size
        if len(history['prices']) > max_points:
            history['timestamps'] = history['timestamps'][-max_points:]
            history['prices'] = history['prices'][-max_points:]
        
        # Create chart
        if len(history['prices']) > 1:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=history['timestamps'],
                y=history['prices'],
                mode='lines',
                name=symbol,
                line=dict(color='#2962ff', width=2)
            ))
            
            fig.update_layout(
                title=f"{symbol} - Real-time Price",
                xaxis_title="Time",
                yaxis_title="Price (USD)",
                template='plotly_dark',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("⏳ Collecting data points...")
    else:
        st.warning(f"No real-time data for {symbol}")


def show_realtime_orderbook(symbol: str):
    """
    Display real-time order book (if available).
    
    Args:
        symbol: Trading symbol
    """
    st.subheader(f"📊 Order Book - {symbol}")
    
    if not WEBSOCKET_AVAILABLE:
        st.info("💡 WebSocket required for order book")
        return
    
    # Placeholder for order book implementation
    st.info("🚧 Order book visualization coming soon")
    
    # Mock data for demonstration
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🟢 Bids (Buy Orders)**")
        bids_data = pd.DataFrame({
            'Price': [50000, 49990, 49980],
            'Amount': [1.5, 2.3, 0.8],
            'Total': [75000, 114977, 39984]
        })
        st.dataframe(bids_data, hide_index=True)
    
    with col2:
        st.markdown("**🔴 Asks (Sell Orders)**")
        asks_data = pd.DataFrame({
            'Price': [50010, 50020, 50030],
            'Amount': [0.9, 1.2, 2.1],
            'Total': [45009, 60024, 105063]
        })
        st.dataframe(asks_data, hide_index=True)


def show_realtime_trades(symbol: str, max_trades: int = 20):
    """
    Display recent trades in real-time.
    
    Args:
        symbol: Trading symbol
        max_trades: Maximum trades to display
    """
    st.subheader(f"💱 Recent Trades - {symbol}")
    
    if not WEBSOCKET_AVAILABLE:
        st.info("💡 WebSocket required for trade feed")
        return
    
    # Placeholder for trades implementation
    st.info("🚧 Trade feed coming soon")


def create_realtime_tab():
    """
    Create complete real-time monitoring tab.
    
    Returns:
        Streamlit tab content
    """
    st.header("📡 Real-time Market Monitor")
    
    # Initialize
    if init_realtime_dashboard():
        # Status indicator
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### Live Market Data")
        
        with col2:
            show_realtime_status()
        
        # Price ticker
        st.markdown("---")
        st.subheader("🎯 Top Cryptocurrencies")
        show_realtime_price_ticker()
        
        # Refresh control
        st.markdown("---")
        auto_refresh = st.checkbox("Auto-refresh (5 sec)", value=False)
        
        if auto_refresh:
            time.sleep(5)
            st.rerun()
        
        # Manual refresh button
        if st.button("🔄 Refresh Now"):
            st.rerun()
        
        # Symbol selection for detailed view
        st.markdown("---")
        st.subheader("📈 Detailed View")
        
        client = st.session_state.get('realtime_client')
        if client:
            all_prices = client.get_all_prices()
            available_symbols = list(all_prices.keys()) if all_prices else []
            
            if available_symbols:
                selected_symbol = st.selectbox(
                    "Select Symbol",
                    available_symbols,
                    index=0 if 'BTCUSDT' in available_symbols else 0
                )
                
                # Show detailed info
                col1, col2 = st.columns(2)
                
                with col1:
                    show_realtime_price_chart(selected_symbol)
                
                with col2:
                    show_realtime_orderbook(selected_symbol)
                
                # Recent trades
                show_realtime_trades(selected_symbol)
            else:
                st.info("⏳ Waiting for market data...")
    else:
        st.error("❌ Failed to initialize real-time dashboard")
        st.info("💡 Make sure WebSocket server is running:")
        st.code("python src/ui/websocket_server.py", language="bash")


def add_realtime_indicator(label: str, value: float, previous_value: Optional[float] = None):
    """
    Add a real-time indicator with change detection.
    
    Args:
        label: Indicator label
        value: Current value
        previous_value: Previous value for delta calculation
    """
    if previous_value is not None:
        delta = value - previous_value
        delta_pct = (delta / previous_value * 100) if previous_value != 0 else 0
        
        st.metric(
            label=label,
            value=f"{value:.2f}",
            delta=f"{delta_pct:+.2f}%"
        )
    else:
        st.metric(label=label, value=f"{value:.2f}")


if __name__ == "__main__":
    print("📡 Streamlit Real-time Integration Module")
    print("=" * 50)
    print("Functions:")
    print("  ✅ init_realtime_dashboard()")
    print("  ✅ show_realtime_status()")
    print("  ✅ show_realtime_price_ticker()")
    print("  ✅ show_realtime_price_chart()")
    print("  ✅ show_realtime_orderbook()")
    print("  ✅ show_realtime_trades()")
    print("  ✅ create_realtime_tab()")
    print("\nUsage in Streamlit:")
    print("  from ui.streamlit_realtime import create_realtime_tab")
    print("  create_realtime_tab()")
