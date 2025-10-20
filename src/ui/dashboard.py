"""
BiX TradeBOT - Web Dashboard UI
================================
Interactive Streamlit dashboard for bot control and monitoring.

Author: SALMAN ThinkTank AI Core (NOVA - UI/UX Visionary)
Version: 1.0.0
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime
import sys
import os
from pathlib import Path

# Add src directory to path (go up 2 levels from ui/dashboard.py to root, then into src)
current_dir = Path(__file__).parent  # ui directory
src_dir = current_dir.parent  # src directory
root_dir = src_dir.parent  # root directory
sys.path.insert(0, str(src_dir))

from utils.config import Config
from data.handler import DataHandler
from data.indicators import TechnicalIndicators
from core.ml_engine import MLEngine
from core.risk_manager import RiskManager
from core.strategy import SimpleHybridStrategy
from utils.logger import get_logger

# Import backtester (optional - may not exist in all versions)
try:
    from analysis.backtester import BacktestEngine
    BACKTESTER_AVAILABLE = True
except ImportError:
    BACKTESTER_AVAILABLE = False
    print("⚠️ Backtester module not available")

# Import live data feed system
try:
    from analysis.live_feed import LiveDataFeed
    LIVE_FEED_AVAILABLE = True
except ImportError:
    LIVE_FEED_AVAILABLE = False
    st.warning("⚠️ Live data feed module not available")

# Page configuration
st.set_page_config(
    page_title="BiX TradeBOT",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #00d2ff 0%, #3a47d5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        text-align: center;
        color: #888;
        margin-top: -10px;
        margin-bottom: 30px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_handler' not in st.session_state:
    st.session_state.data_handler = None
if 'latest_data' not in st.session_state:
    st.session_state.latest_data = None
if 'ml_engine' not in st.session_state:
    st.session_state.ml_engine = None
if 'risk_manager' not in st.session_state:
    st.session_state.risk_manager = RiskManager()
if 'logger' not in st.session_state:
    st.session_state.logger = get_logger()

# Header
st.markdown('<h1 class="main-header">🤖 BiX TradeBOT</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Trading Dashboard | SALMAN ThinkTank</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🤖 BiX TradeBOT")
    st.markdown("### AI-Powered Trading")
    st.markdown("---")
    
    st.markdown("### ⚙️ Configuration")
    
    symbol = st.selectbox(
        "Trading Pair",
        ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"],
        index=0,
        help="Select trading pair (BTCUSDT recommended)"
    )
    
    timeframe = st.selectbox(
        "Timeframe",
        ["1m", "5m", "15m", "1h", "4h", "1d"],
        index=3
    )
    
    use_testnet = st.checkbox("Use Testnet", value=True)
    enable_ml = st.checkbox("Enable ML Predictions", value=True)
    
    st.markdown("---")
    
    st.markdown("### 💼 Capital Management")
    initial_capital = st.number_input(
        "Initial Capital ($)",
        min_value=100,
        max_value=1000000,
        value=10000,
        step=1000
    )
    
    risk_per_trade = st.slider(
        "Risk per Trade (%)",
        min_value=0.5,
        max_value=5.0,
        value=1.5,
        step=0.1
    )
    
    st.markdown("---")
    
    if st.button("🔄 Refresh Data"):
        st.session_state.latest_data = None
        st.rerun()

# Main content
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Live Analysis",
    "🌐 Live Market Feed",
    "📈 Backtest",
    "🤖 ML Training",
    "📋 Settings",
    "🔍 System Logs",
    "🧪 System Testing"
])

# Tab 1: Live Analysis
with tab1:
    st.markdown("## 🎯 Real-Time Market Analysis")
    
    if st.button("▶️ Analyze Market", type="primary"):
        with st.spinner(f"Fetching {symbol} data..."):
            try:
                # Log analysis start
                st.session_state.logger.info(
                    f"Starting market analysis for {symbol} {timeframe}",
                    component="ANALYSIS"
                )
                
                # Initialize data handler
                if st.session_state.data_handler is None:
                    st.session_state.data_handler = DataHandler(use_ccxt=False)
                    st.session_state.logger.info(
                        "DataHandler initialized",
                        component="SYSTEM"
                    )
                
                # Update config
                Config.SYMBOL = symbol
                Config.TIMEFRAME = timeframe
                Config.BINANCE_TESTNET = use_testnet
                Config.ML_ENABLED = enable_ml
                Config.INITIAL_CAPITAL = initial_capital
                Config.RISK_PER_TRADE = risk_per_trade / 100
                
                # Fetch data
                df = st.session_state.data_handler.fetch_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    limit=500
                )
                
                # Check if we have data
                if df is None or len(df) == 0:
                    error_msg = (
                        f"No data available for {symbol}. "
                        "Please try another symbol (BTCUSDT recommended)"
                    )
                    st.session_state.logger.error(
                        error_msg,
                        component="DATA_HANDLER"
                    )
                    st.error(f"❌ {error_msg}")
                    st.stop()
                
                if len(df) < 100:
                    warning_msg = (
                        f"Limited data available ({len(df)} candles). "
                        "Results may be less accurate."
                    )
                    st.session_state.logger.warning(
                        warning_msg,
                        component="DATA_HANDLER"
                    )
                    st.warning(f"⚠️ {warning_msg}")
                
                st.session_state.logger.info(
                    f"Fetched {len(df)} candles successfully",
                    component="DATA_HANDLER"
                )
                
                # Calculate indicators
                indicators = TechnicalIndicators(df)
                df_indicators = indicators.calculate_all()
                
                # Check if indicators calculated successfully
                if df_indicators is None or len(df_indicators) == 0:
                    error_msg = (
                        "Failed to calculate technical indicators. "
                        "Please try again."
                    )
                    st.session_state.logger.error(
                        error_msg,
                        component="INDICATORS"
                    )
                    st.error(f"❌ {error_msg}")
                    st.stop()
                
                st.session_state.logger.info(
                    "Technical indicators calculated successfully",
                    component="INDICATORS"
                )
                
                # Get latest signals
                latest_signals = indicators.get_latest_signals()
                
                # ML prediction
                ml_pred = None
                ml_conf = None
                if enable_ml:
                    if st.session_state.ml_engine is None:
                        st.session_state.ml_engine = MLEngine()
                    
                    if not st.session_state.ml_engine.load_model():
                        st.session_state.logger.warning(
                            "No trained ML model found",
                            component="ML_ENGINE"
                        )
                        st.warning(
                            "⚠️ No trained model found. "
                            "Train model in ML Training tab."
                        )
                    else:
                        try:
                            # For ML predictions, we need full dataframe
                            # not just last row, to calculate features
                            predictions = (
                                st.session_state.ml_engine
                                .get_prediction_confidence(df_indicators)
                            )
                            
                            if predictions is not None and len(predictions) > 0:
                                ml_pred = predictions['prediction'].iloc[-1]
                                ml_conf = predictions['confidence'].iloc[-1]
                                
                                st.session_state.logger.info(
                                    f"ML prediction: {ml_pred} "
                                    f"(confidence: {ml_conf:.2%})",
                                    component="ML_ENGINE"
                                )
                            else:
                                st.session_state.logger.warning(
                                    "ML predictions returned empty",
                                    component="ML_ENGINE"
                                )
                                st.warning(
                                    "⚠️ ML predictions unavailable. "
                                    "Using technical analysis only."
                                )
                        except Exception as ml_error:
                            st.session_state.logger.error(
                                f"ML prediction failed: {str(ml_error)}",
                                component="ML_ENGINE",
                                exception=ml_error
                            )
                            st.warning(
                                f"⚠️ ML Error: {str(ml_error)}. "
                                "Using technical analysis only."
                            )
                
                # Generate signal
                strategy = SimpleHybridStrategy(use_ml=enable_ml)
                signal = strategy.generate_signal(
                    latest_signals,
                    ml_prediction=ml_pred,
                    ml_confidence=ml_conf
                )
                
                st.session_state.logger.info(
                    f"Signal generated: {signal}",
                    component="STRATEGY"
                )
                
                st.session_state.latest_data = {
                    'df': df_indicators,
                    'signals': latest_signals,
                    'signal': signal,
                    'ml_pred': ml_pred,
                    'ml_conf': ml_conf
                }
                
                st.success("✅ Analysis complete!")
                
            except Exception as e:
                st.session_state.logger.error(
                    f"Market analysis failed: {str(e)}",
                    component="ANALYSIS",
                    exception=e
                )
                st.error(f"❌ Error: {str(e)}")
                st.error(
                    "Check 'System Logs' tab for detailed error information"
                )
                st.stop()
    
    # Display results
    if st.session_state.latest_data is not None:
        data = st.session_state.latest_data
        signals = data['signals']
        signal = data['signal']
        
        # Metrics row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("💰 Current Price", f"${signals['close']:,.2f}")
        
        with col2:
            signal_colors = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '⚪'}
            st.metric(
                "🎯 Signal",
                f"{signal_colors[signal['action']]} {signal['action']}",
                delta=None
            )
        
        with col3:
            st.metric("⭐ Strength", f"{'⭐' * signal['strength']}")
        
        with col4:
            st.metric("📊 RSI", f"{signals['rsi']:.2f}")
        
        with col5:
            st.metric("💪 ADX", f"{signals['adx']:.2f}")
        
        st.markdown("---")
        
        # Two columns for details
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("### 📈 Technical Indicators")
            
            indicators_df = pd.DataFrame({
                'Indicator': ['EMA Fast', 'EMA Slow', 'RSI', 'ATR', 'ADX'],
                'Value': [
                    f"${signals['ema_fast']:,.2f}",
                    f"${signals['ema_slow']:,.2f}",
                    f"{signals['rsi']:.2f}",
                    f"${signals['atr']:,.2f}",
                    f"{signals['adx']:.2f}"
                ]
            })
            st.dataframe(indicators_df, use_container_width=True, hide_index=True)
            
            st.markdown("### 🎯 Strategy Signals")
            signal_emoji = {1: "🟢 Long", -1: "🔴 Short", 0: "⚪ Neutral"}
            signals_df = pd.DataFrame({
                'Strategy': ['Trend', 'Breakout', 'Pullback', 'Combined'],
                'Signal': [
                    signal_emoji[signals['trend_signal']],
                    signal_emoji[signals['breakout_signal']],
                    signal_emoji[signals['pullback_signal']],
                    f"Score: {signals['combined_signal']}"
                ]
            })
            st.dataframe(signals_df, use_container_width=True, hide_index=True)
        
        with col_right:
            if data['ml_pred'] is not None:
                st.markdown("### 🤖 ML Prediction")
                pred_text = {1: "🟢 BULLISH", -1: "🔴 BEARISH", 0: "⚪ NEUTRAL"}
                
                st.markdown(f"**Prediction:** {pred_text.get(data['ml_pred'], 'UNKNOWN')}")
                st.progress(data['ml_conf'])
                st.markdown(f"**Confidence:** {data['ml_conf']:.1%}")
            
            st.markdown("### 💡 Recommendation")
            st.info(f"**Action:** {signal['action']}\n\n**Reason:** {signal['reason']}")
            
            if signal['action'] in ['BUY', 'SELL']:
                direction = 'long' if signal['action'] == 'BUY' else 'short'
                position_info = st.session_state.risk_manager.calculate_position_size(
                    entry_price=signals['close'],
                    atr=signals['atr'],
                    direction=direction
                )
                
                st.markdown("### 💼 Position Sizing")
                pos_df = pd.DataFrame({
                    'Parameter': ['Size', 'Value', 'Stop Loss', 'Take Profit', 'Risk'],
                    'Value': [
                        f"{position_info['size']:.6f}",
                        f"${position_info['value']:,.2f}",
                        f"${position_info['stop_loss']:,.2f}",
                        f"${position_info['take_profit']:,.2f}",
                        f"${position_info['risk_amount']:,.2f}"
                    ]
                })
                st.dataframe(pos_df, use_container_width=True, hide_index=True)
        
        # Price chart
        st.markdown("---")
        st.markdown("### 📊 Price Chart")
        
        df_chart = data['df'].tail(100).copy()
        
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.5, 0.25, 0.25],
            subplot_titles=('Price & Indicators', 'RSI', 'Volume')
        )
        
        # Candlestick
        fig.add_trace(
            go.Candlestick(
                x=df_chart.index,
                open=df_chart['open'],
                high=df_chart['high'],
                low=df_chart['low'],
                close=df_chart['close'],
                name='Price'
            ),
            row=1, col=1
        )
        
        # EMA lines
        fig.add_trace(
            go.Scatter(
                x=df_chart.index,
                y=df_chart['ema_fast'],
                name='EMA 50',
                line=dict(color='blue', width=1)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df_chart.index,
                y=df_chart['ema_slow'],
                name='EMA 200',
                line=dict(color='red', width=1)
            ),
            row=1, col=1
        )
        
        # RSI
        fig.add_trace(
            go.Scatter(
                x=df_chart.index,
                y=df_chart['rsi'],
                name='RSI',
                line=dict(color='purple', width=2)
            ),
            row=2, col=1
        )
        
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # Volume
        colors = ['red' if df_chart['close'].iloc[i] < df_chart['open'].iloc[i] 
                  else 'green' for i in range(len(df_chart))]
        
        fig.add_trace(
            go.Bar(
                x=df_chart.index,
                y=df_chart['volume'],
                name='Volume',
                marker_color=colors
            ),
            row=3, col=1
        )
        
        fig.update_layout(
            height=800,
            xaxis_rangeslider_visible=False,
            showlegend=True,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add Backtest Section
        st.markdown("---")
        st.markdown("### 🎯 Strategy Backtest & Performance")
        
        with st.expander("📊 View Backtest Results", expanded=False):
            st.info("💡 Use the dedicated **Backtest tab (Tab 3)** for full backtesting capabilities")
            st.markdown("""
            **Available Features in Backtest Tab:**
            - � Custom date range selection
            - 📊 Comprehensive performance metrics
            - � Visual charts and trade history
            - 🎯 Sharpe Ratio and Max Drawdown analysis
            """)

# Tab 2: Live Market Feed
with tab2:
    st.markdown("## 🌐 Real-Time Cryptocurrency Market Feed")
    st.info("🚀 Multi-Agent Live Data Integration System - Top 50 Coins by Volume")
    
    # Control buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("▶️ Start Live Feed", type="primary"):
            st.session_state.live_feed_running = True
    
    with col2:
        if st.button("⏹️ Stop Feed"):
            st.session_state.live_feed_running = False
    
    with col3:
        top_n = st.slider("Top N Coins", 10, 50, 20, 5)
    
    # Initialize live feed state
    if 'live_feed_running' not in st.session_state:
        st.session_state.live_feed_running = False
    if 'live_feed_data' not in st.session_state:
        st.session_state.live_feed_data = None
    
    # Display live data
    if st.session_state.live_feed_running or st.button("🔄 Fetch Once"):
        with st.spinner("Fetching live market data..."):
            try:
                import asyncio
                from analysis.live_feed import LiveDataFeed
                
                # Create feed instance
                feed = LiveDataFeed(top_n_coins=top_n, update_interval=5)
                
                # Fetch data once
                data = asyncio.run(feed.fetch_and_process())
                
                if data:
                    st.session_state.live_feed_data = data
                    
                    # Display timestamp
                    st.markdown(f"**Last Update:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Create DataFrame
                    df_live = pd.DataFrame(data)
                    
                    # Display metrics
                    st.markdown("### 📊 Market Overview")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        avg_change = df_live['24h_change_percent'].mean()
                        st.metric(
                            "Avg 24h Change",
                            f"{avg_change:+.2f}%",
                            delta=f"{avg_change:.2f}%"
                        )
                    
                    with col2:
                        gainers = len(df_live[df_live['24h_change_percent'] > 0])
                        st.metric("Gainers", gainers, delta=f"{gainers}/{len(df_live)}")
                    
                    with col3:
                        losers = len(df_live[df_live['24h_change_percent'] < 0])
                        st.metric("Losers", losers, delta=f"-{losers}/{len(df_live)}")
                    
                    with col4:
                        total_volume = df_live['volume_usd'].sum() / 1e9
                        st.metric("Total Volume", f"${total_volume:.2f}B")
                    
                    # Top gainers and losers
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 🚀 Top 5 Gainers")
                        top_gainers = df_live.nlargest(5, '24h_change_percent')[
                            ['symbol', 'price_usd', '24h_change_percent']
                        ]
                        for idx, row in top_gainers.iterrows():
                            st.success(
                                f"**{row['symbol']}**: ${row['price_usd']:.2f} "
                                f"({row['24h_change_percent']:+.2f}%)"
                            )
                    
                    with col2:
                        st.markdown("#### 📉 Top 5 Losers")
                        top_losers = df_live.nsmallest(5, '24h_change_percent')[
                            ['symbol', 'price_usd', '24h_change_percent']
                        ]
                        for idx, row in top_losers.iterrows():
                            st.error(
                                f"**{row['symbol']}**: ${row['price_usd']:.2f} "
                                f"({row['24h_change_percent']:+.2f}%)"
                            )
                    
                    # Full market table
                    st.markdown("---")
                    st.markdown("### 📋 Complete Market Data")
                    
                    # Format for display
                    display_df = df_live[[
                        'rank', 'symbol', 'coin_name', 'price_usd',
                        '24h_change_percent', 'volume_usd', 'source'
                    ]].copy()
                    
                    display_df.columns = [
                        'Rank', 'Symbol', 'Name', 'Price (USD)',
                        '24h Change %', 'Volume (USD)', 'Source'
                    ]
                    
                    # Format numbers
                    display_df['Price (USD)'] = display_df['Price (USD)'].apply(
                        lambda x: f"${x:,.2f}" if x >= 1 else f"${x:.6f}"
                    )
                    display_df['24h Change %'] = display_df['24h Change %'].apply(
                        lambda x: f"{x:+.2f}%"
                    )
                    display_df['Volume (USD)'] = display_df['Volume (USD)'].apply(
                        lambda x: f"${x/1e6:.2f}M"
                    )
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True,
                        height=400
                    )
                    
                    # Heat map visualization
                    st.markdown("---")
                    st.markdown("### 🔥 Market Heat Map")
                    
                    fig = go.Figure(data=[go.Bar(
                        x=df_live['symbol'],
                        y=df_live['24h_change_percent'],
                        marker_color=df_live['24h_change_percent'].apply(
                            lambda x: 'green' if x > 0 else 'red'
                        ),
                        text=df_live['24h_change_percent'].apply(lambda x: f"{x:+.1f}%"),
                        textposition='outside'
                    )])
                    
                    fig.update_layout(
                        title=f"24h Price Changes - Top {top_n} Cryptocurrencies",
                        xaxis_title="Symbol",
                        yaxis_title="24h Change (%)",
                        height=500,
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # System status
                    st.markdown("---")
                    st.markdown("### 🛠️ System Status")
                    
                    system_status = feed.get_system_status()
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.info(f"**Status:** {'🟢 Running' if system_status['is_running'] else '🔴 Stopped'}")
                    
                    with col2:
                        st.info(f"**Coins Tracked:** {system_status['coins_tracked']}")
                    
                    with col3:
                        st.info(f"**History Size:** {system_status['history_size']} samples")
                    
                    # API health
                    if system_status.get('api_status'):
                        st.markdown("#### API Health Status")
                        for api_name, status in system_status['api_status'].items():
                            uptime = (status['successful_requests'] / status['total_requests'] * 100) if status['total_requests'] > 0 else 0
                            st.metric(
                                f"{api_name.upper()}",
                                f"{uptime:.1f}% uptime",
                                delta=status['status']
                            )
                    
                    st.success("✅ Live data feed operational!")
                    
                else:
                    st.error("❌ Failed to fetch market data. Check API connectivity.")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.exception(e)
    
    elif st.session_state.live_feed_data:
        st.markdown("### 📊 Cached Market Data")
        st.info("Click 'Fetch Once' to refresh data")
        
        df_cached = pd.DataFrame(st.session_state.live_feed_data)
        st.dataframe(
            df_cached[['symbol', 'price_usd', '24h_change_percent', 'volume_usd']],
            use_container_width=True,
            hide_index=True
        )
    
    else:
        st.warning("⚠️ No data available. Click 'Fetch Once' or 'Start Live Feed' to begin.")
        
        # Instructions
        st.markdown("""
        ### 📖 How to Use
        
        **Features:**
        - 🔄 **Real-time tracking** of top 10-50 cryptocurrencies
        - 📊 **Multi-API support** (CoinGecko + Binance) with automatic failover
        - 🛡️ **Quality control** with anomaly detection
        - 🌐 **Multilingual support** (English/Persian)
        - 📈 **Market overview** with gainers/losers analysis
        - 🔥 **Interactive visualizations** and heat maps
        
        **Getting Started:**
        1. Select the number of top coins to track (10-50)
        2. Click "▶️ Start Live Feed" for continuous updates
        3. Or click "🔄 Fetch Once" for a single snapshot
        4. View real-time prices, 24h changes, and volumes
        5. Analyze market trends with visual charts
        
        **Data Sources:**
        - **CoinGecko API** (Primary): No authentication required
        - **Binance API** (Fallback): Real-time market data
        
        **Update Frequency:** Every 5 seconds when live feed is active
        """)

# Tab 3: Backtest
with tab3:
    st.markdown("## 📈 Strategy Backtesting")
    
    col1, col2 = st.columns(2)
    
    with col1:
        backtest_start = st.date_input(
            "Start Date",
            value=pd.to_datetime("2024-01-01")
        )
    
    with col2:
        backtest_end = st.date_input(
            "End Date",
            value=pd.to_datetime("2025-10-20")
        )
    
    if st.button("🚀 Run Backtest", type="primary"):
        with st.spinner("Running backtest... This may take a minute."):
            try:
                from analysis.backtest import BacktestEngine
                
                Config.SYMBOL = symbol
                Config.TIMEFRAME = timeframe
                Config.BACKTEST_START_DATE = backtest_start.strftime("%Y-%m-%d")
                Config.BACKTEST_END_DATE = backtest_end.strftime("%Y-%m-%d")
                Config.ML_ENABLED = enable_ml
                Config.INITIAL_CAPITAL = initial_capital
                
                engine = BacktestEngine(use_ml=enable_ml)
                data = engine.prepare_data()
                results = engine.run(data=data)
                
                # Display results
                st.success("✅ Backtest complete!")
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Return", f"{results['Return [%]']:.2f}%")
                
                with col2:
                    st.metric("Sharpe Ratio", f"{results['Sharpe Ratio']:.2f}")
                
                with col3:
                    st.metric("Max Drawdown", f"{results['Max. Drawdown [%]']:.2f}%")
                
                with col4:
                    st.metric("Win Rate", f"{results['Win Rate [%]']:.2f}%")
                
                # Full stats
                st.markdown("### 📊 Detailed Statistics")
                summary = engine.get_summary()
                
                summary_df = pd.DataFrame([
                    {"Metric": k, "Value": v} for k, v in summary.items()
                ])
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
                
            except Exception as e:
                st.error(f"❌ Error running backtest: {str(e)}")

# Tab 4: ML Training
with tab4:
    st.markdown("## 🤖 Machine Learning Model Training")
    
    st.info("🎯 Train a LightGBM model to enhance trading signals with AI predictions.")
    
    # Show current model status
    try:
        from pathlib import Path
        model_path = Path(f'models/model_{timeframe}.pkl')
        if model_path.exists():
            st.success(f"✅ Model exists for {timeframe} timeframe")
            model_size = model_path.stat().st_size / 1024
            st.caption(f"📦 Model size: {model_size:.1f} KB")
        else:
            st.warning(f"⚠️ No model found for {timeframe} timeframe")
    except:
        pass
    
    col1, col2 = st.columns(2)
    
    with col1:
        training_samples = st.slider(
            "Training Data Size (candles)",
            min_value=500,
            max_value=5000,
            value=2000,
            step=500
        )
    
    with col2:
        use_cache = st.checkbox("Use Cached Data", value=True, 
                                help="Uncheck to fetch fresh data from Binance")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🎓 Train Model (Quick)", type="primary", use_container_width=True):
            with st.spinner("Training ML model... This may take a few minutes."):
                try:
                    Config.SYMBOL = symbol
                    Config.TIMEFRAME = timeframe
                    
                    # Fetch data
                    handler = DataHandler()
                    df = handler.fetch_ohlcv(limit=training_samples, use_cache=use_cache)
                    
                    # Calculate indicators
                    indicators = TechnicalIndicators(df)
                    df_indicators = indicators.calculate_all()
                    
                    # Train ML model
                    ml_engine = MLEngine(timeframe=timeframe)
                    metrics = ml_engine.train(df_indicators)
                    
                    st.session_state.ml_engine = ml_engine
                    
                    st.success("✅ Model training complete!")
                    
                    # Display metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Accuracy", f"{metrics['accuracy']:.2%}")
                    
                    with col2:
                        st.metric("Training Size", metrics['train_size'])
                    
                    with col3:
                        st.metric("Test Size", metrics['test_size'])
                    
                    with col4:
                        st.metric("Features", metrics['features'])
                    
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Error training model: {str(e)}")
    
    with col_btn2:
        if st.button("🔄 Train with Fresh Data", type="secondary", use_container_width=True,
                     help="Fetch new data from Binance and train model (better accuracy)"):
            with st.spinner("📥 Fetching fresh data and training... Please wait."):
                try:
                    Config.SYMBOL = symbol
                    Config.TIMEFRAME = timeframe
                    
                    # Force fresh data fetch
                    handler = DataHandler()
                    df = handler.fetch_ohlcv(limit=training_samples, use_cache=False)
                    
                    st.info(f"✅ Fetched {len(df)} fresh candles from Binance")
                    
                    # Calculate indicators
                    indicators = TechnicalIndicators(df)
                    df_indicators = indicators.calculate_all()
                    
                    # Train ML model
                    ml_engine = MLEngine(timeframe=timeframe)
                    metrics = ml_engine.train(df_indicators)
                    
                    st.session_state.ml_engine = ml_engine
                    
                    st.success("✅ Model trained with fresh data!")
                    
                    # Display metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Accuracy", f"{metrics['accuracy']:.2%}")
                    
                    with col2:
                        st.metric("Training Size", metrics['train_size'])
                    
                    with col3:
                        st.metric("Test Size", metrics['test_size'])
                    
                    with col4:
                        st.metric("Features", metrics['features'])
                    
                    st.balloons()
                    st.info("💡 Tip: Fresh data usually gives better accuracy!")
                    
                except Exception as e:
                    st.error(f"❌ Error training with fresh data: {str(e)}")

# Tab 5: Settings
with tab5:
    st.markdown("## ⚙️ Bot Settings")
    
    # AI Model Selection
    with st.expander("🤖 AI Model Selection", expanded=True):
        from ai.models_config import ModelType, AIModelsConfig
        
        st.markdown("### Select AI Model for Predictions")
        
        # Get available models
        models = AIModelsConfig.list_available_models()
        
        # Create model selection
        model_names = [m['name'] for m in models]
        model_types = [m['type'] for m in models]
        
        # Try to load saved preference
        try:
            saved_model = AIModelsConfig.load_preference()
            default_idx = model_types.index(saved_model.value)
        except:
            default_idx = 0
        
        selected_model_name = st.selectbox(
            "Choose AI Model:",
            model_names,
            index=default_idx,
            help="Select the AI model for trading predictions"
        )
        
        # Get selected model details
        selected_idx = model_names.index(selected_model_name)
        selected_model = models[selected_idx]
        
        # Display model info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Speed", selected_model['speed'])
        with col2:
            st.metric("Cost", selected_model['cost'])
        with col3:
            st.metric("Accuracy", selected_model['accuracy'])
        
        st.info(f"📝 {selected_model['description']}")
        
        # Check API configuration
        model_type_enum = ModelType(selected_model['type'])
        if AIModelsConfig.is_api_configured(model_type_enum):
            st.success("✅ Model is ready to use")
        else:
            st.warning("⚠️ This model requires API setup")
            st.code(AIModelsConfig.get_setup_instructions(model_type_enum))
        
        # Save preference button
        if st.button("💾 Save Model Preference", type="primary"):
            AIModelsConfig.save_preference(model_type_enum)
            st.success(f"✅ Saved {selected_model_name} as default model")
            st.balloons()
    
    with st.expander("📝 API Configuration"):
        st.markdown("**Current Status:**")
        
        if Config.BINANCE_API_KEY and Config.BINANCE_API_SECRET:
            st.success("✅ Binance API credentials configured")
        else:
            st.warning("⚠️ Binance API credentials not set. Edit `.env` file.")
        
        st.code("""
# .env file example:
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
BINANCE_TESTNET=True

# Optional: For GitHub Models (Free tier available)
GITHUB_TOKEN=ghp_your_github_personal_access_token

# Optional: For Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your_api_key
        """)
    
    with st.expander("🎯 Strategy Parameters"):
        st.markdown("**Current Configuration:**")
        
        params_df = pd.DataFrame({
            'Parameter': [
                'EMA Fast', 'EMA Slow', 'RSI Period', 'ATR Period',
                'ADX Threshold', 'Risk/Reward Ratio'
            ],
            'Value': [
                Config.EMA_FAST, Config.EMA_SLOW, Config.RSI_PERIOD,
                Config.ATR_PERIOD, Config.ADX_THRESHOLD, Config.RISK_REWARD_RATIO
            ]
        })
        st.dataframe(params_df, use_container_width=True, hide_index=True)
        
        st.info("💡 To modify these, edit `config.py` file.")
    
    with st.expander("📚 Documentation"):
        st.markdown("""
        ### Quick Links
        - 📖 [README.md](README.md) - Full documentation
        - 🚀 [QUICKSTART.md](QUICKSTART.md) - 5-minute guide
        - 📊 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Technical overview
        
        ### Support
        - GitHub Issues
        - Email: support@example.com
        """)

# Tab 6: System Logs & Error Monitoring
with tab6:
    st.markdown("### 🔍 System Logs & Error Monitoring")
    
    # Real-time status
    col1, col2, col3, col4 = st.columns(4)
    
    logger = st.session_state.logger
    error_stats = logger.get_error_stats()
    
    with col1:
        st.metric(
            "Total Errors",
            error_stats.get('total_errors', 0),
            delta=None,
            delta_color="inverse"
        )
    
    with col2:
        component_count = len(error_stats.get('components', {}))
        st.metric("Affected Components", component_count)
    
    with col3:
        error_type_count = len(error_stats.get('error_types', {}))
        st.metric("Error Types", error_type_count)
    
    with col4:
        if error_stats.get('last_error'):
            try:
                last_time = datetime.fromisoformat(
                    error_stats['last_error']['timestamp']
                )
                time_ago = (datetime.now() - last_time).seconds
                st.metric("Last Error", f"{time_ago}s ago")
            except (KeyError, ValueError):
                st.metric("Last Error", "Unknown")
        else:
            st.metric("Last Error", "None")
    
    st.markdown("---")
    
    # Tabs for different log views
    log_tab1, log_tab2, log_tab3, log_tab4 = st.tabs([
        "🔴 Error History",
        "📊 Error Statistics",
        "📝 System Logs",
        "💰 Trade Logs"
    ])
    
    # Error History Tab
    with log_tab1:
        st.markdown("#### Recent Errors")
        
        error_limit = st.slider("Show last N errors", 5, 50, 20)
        recent_errors = logger.get_recent_errors(limit=error_limit)
        
        if not recent_errors:
            st.success("✅ No errors recorded! System running smoothly.")
        else:
            for idx, error in enumerate(reversed(recent_errors)):
                with st.expander(
                    f"❌ {error['type']} - {error['component']} | "
                    f"{error['timestamp']}"
                ):
                    st.markdown(f"**Message:** {error['message']}")
                    st.markdown(f"**Component:** `{error['component']}`")
                    st.markdown(f"**Type:** `{error['type']}`")
                    st.markdown(f"**Time:** {error['timestamp']}")
                    
                    if error.get('traceback'):
                        st.markdown("**Traceback:**")
                        st.code(error['traceback'], language='python')
    
    # Error Statistics Tab
    with log_tab2:
        st.markdown("#### Error Analysis")
        
        if error_stats.get('total_errors', 0) == 0:
            st.info("📊 No errors to analyze yet.")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Errors by Type:**")
                error_types = error_stats.get('error_types', {})
                if error_types:
                    type_df = pd.DataFrame([
                        {"Error Type": k, "Count": v}
                        for k, v in error_types.items()
                    ])
                    st.dataframe(
                        type_df,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No error types recorded.")
            
            with col2:
                st.markdown("**Errors by Component:**")
                components = error_stats.get('components', {})
                if components:
                    comp_df = pd.DataFrame([
                        {"Component": k, "Count": v}
                        for k, v in components.items()
                    ])
                    st.dataframe(
                        comp_df,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No components recorded.")
            
            # Error trend chart (if we have timestamps)
            st.markdown("**Error Timeline:**")
            recent_errors = logger.get_recent_errors(limit=50)
            if recent_errors:
                error_times = [
                    datetime.fromisoformat(e['timestamp'])
                    for e in recent_errors
                ]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=error_times,
                    y=list(range(1, len(error_times) + 1)),
                    mode='lines+markers',
                    name='Cumulative Errors',
                    line=dict(color='red', width=2),
                    marker=dict(size=8)
                ))
                
                fig.update_layout(
                    title="Error Accumulation Over Time",
                    xaxis_title="Time",
                    yaxis_title="Cumulative Error Count",
                    height=400,
                    template="plotly_dark"
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    # System Logs Tab
    with log_tab3:
        st.markdown("#### System Event Logs")
        
        log_file = Path("logs/system.log")
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = f.readlines()
            
            # Show last N lines
            num_lines = st.slider("Show last N lines", 10, 100, 50)
            
            st.code('\n'.join(logs[-num_lines:]), language='log')
            
            if st.button("📥 Download System Logs"):
                st.download_button(
                    label="Download",
                    data=''.join(logs),
                    file_name="system_logs.txt",
                    mime="text/plain"
                )
        else:
            st.info("📝 No system logs available yet.")
    
    # Trade Logs Tab
    with log_tab4:
        st.markdown("#### Trade Execution Logs")
        
        trade_file = Path("logs/trades.log")
        if trade_file.exists():
            trades = []
            with open(trade_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        trades.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
            
            if trades:
                trade_df = pd.DataFrame(trades)
                
                # Show summary
                st.metric("Total Trades", len(trades))
                
                # Display table
                st.dataframe(
                    trade_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                if st.button("📥 Download Trade Logs"):
                    st.download_button(
                        label="Download",
                        data=trade_df.to_csv(index=False),
                        file_name="trade_logs.csv",
                        mime="text/csv"
                    )
            else:
                st.info("💰 No trades executed yet.")
        else:
            st.info("💰 No trade logs available yet.")
    
    st.markdown("---")
    
    # Log Management
    st.markdown("#### 🗑️ Log Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧹 Clear Old Logs (>7 days)"):
            logger.clear_old_logs(days=7)
            st.success("✅ Old logs cleared successfully!")
    
    with col2:
        if st.button("🔄 Refresh Error Stats"):
            st.rerun()

# Tab 7: System Testing & Simulation
with tab7:
    st.markdown("### 🧪 System Testing & Simulation")
    st.markdown("Comprehensive testing of all bot components")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("▶️ Run All Tests", type="primary", use_container_width=True):
            from utils.system_simulator import SystemSimulator
            
            with st.spinner("Running comprehensive system tests..."):
                simulator = SystemSimulator()
                results = simulator.run_all_tests()
                
                # Store in session state
                st.session_state['test_results'] = results
                
                st.success("✅ Tests completed!")
                st.rerun()
    
    with col2:
        if st.button("📥 Download Report", use_container_width=True):
            if 'test_results' in st.session_state:
                from utils.system_simulator import SystemSimulator
                simulator = SystemSimulator()
                report = simulator.generate_report(
                    st.session_state['test_results']
                )
                
                st.download_button(
                    label="Download TXT Report",
                    data=report,
                    file_name=f"system_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            else:
                st.warning("Run tests first!")
    
    st.markdown("---")
    
    # Display results if available
    if 'test_results' in st.session_state:
        results = st.session_state['test_results']
        summary = results['summary']
        
        # Summary Metrics
        st.markdown("#### 📊 Test Summary")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Tests", summary['total_tests'])
        
        with col2:
            st.metric("✅ Passed", summary['passed'], 
                     delta=f"{summary['success_rate']:.1f}%")
        
        with col3:
            st.metric("❌ Failed", summary['failed'],
                     delta=None if summary['failed'] == 0 else f"-{summary['failed']}",
                     delta_color="inverse")
        
        with col4:
            st.metric("⚠️ Warnings", summary['warnings'])
        
        with col5:
            st.metric("⏱️ Duration", f"{summary['total_duration']:.2f}s")
        
        # Progress bar
        if summary['total_tests'] > 0:
            progress = summary['passed'] / summary['total_tests']
            st.progress(progress)
        
        st.markdown("---")
        
        # Individual test results
        st.markdown("#### 🔍 Detailed Results")
        
        for test in results['tests']:
            # Status badge
            status_colors = {
                'PASS': '🟢',
                'FAIL': '🔴',
                'WARN': '🟡',
                'SKIP': '⚪'
            }
            
            status_icon = status_colors.get(test['status'], '❓')
            
            with st.expander(
                f"{status_icon} {test['name']} - {test['status']} "
                f"({test['duration']:.2f}s)"
            ):
                st.markdown(f"**Message:** {test['message']}")
                
                if test['details']:
                    st.markdown("**Details:**")
                    
                    # Convert details to dataframe if possible
                    details_items = []
                    for key, value in test['details'].items():
                        if isinstance(value, dict):
                            # Nested dict - expand
                            for k, v in value.items():
                                details_items.append({
                                    'Property': f"{key}.{k}",
                                    'Value': str(v)
                                })
                        elif isinstance(value, list):
                            details_items.append({
                                'Property': key,
                                'Value': ', '.join(str(v) for v in value[:3]) + 
                                        (f' (+{len(value)-3} more)' if len(value) > 3 else '')
                            })
                        else:
                            details_items.append({
                                'Property': key,
                                'Value': str(value)
                            })
                    
                    if details_items:
                        details_df = pd.DataFrame(details_items)
                        st.dataframe(
                            details_df,
                            use_container_width=True,
                            hide_index=True
                        )
        
        st.markdown("---")
        
        # Test coverage visualization
        st.markdown("#### 📈 Test Coverage")
        
        test_names = [t['name'] for t in results['tests']]
        test_statuses = [t['status'] for t in results['tests']]
        test_durations = [t['duration'] for t in results['tests']]
        
        # Status distribution pie chart
        col1, col2 = st.columns(2)
        
        with col1:
            status_counts = pd.DataFrame({
                'Status': test_statuses
            })['Status'].value_counts()
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                hole=0.3,
                marker=dict(colors=['green', 'red', 'yellow', 'gray'])
            )])
            
            fig_pie.update_layout(
                title="Test Status Distribution",
                height=300
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Duration bar chart
            fig_bar = go.Figure(data=[go.Bar(
                x=test_names,
                y=test_durations,
                marker_color='lightblue'
            )])
            
            fig_bar.update_layout(
                title="Test Duration (seconds)",
                xaxis_title="Test Name",
                yaxis_title="Duration (s)",
                height=300,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Component health status
        st.markdown("#### 🏥 Component Health Status")
        
        component_status = []
        for test in results['tests']:
            health_score = 100 if test['status'] == 'PASS' else (
                50 if test['status'] == 'WARN' else 
                25 if test['status'] == 'SKIP' else 0
            )
            
            component_status.append({
                'Component': test['name'],
                'Status': test['status'],
                'Health': health_score,
                'Duration': f"{test['duration']:.2f}s",
                'Message': test['message'][:50] + '...' if len(test['message']) > 50 else test['message']
            })
        
        status_df = pd.DataFrame(component_status)
        
        # Display without styling (simpler approach)
        st.dataframe(status_df, use_container_width=True, hide_index=True)
        
    else:
        # No results yet
        st.info("👆 Click 'Run All Tests' to start system diagnostics")
        
        st.markdown("#### 🎯 What Will Be Tested:")
        
        test_info = [
            ("📊 DataHandler", "Market data fetching, caching, API connectivity"),
            ("📈 Technical Indicators", "EMA, RSI, ATR, ADX calculations"),
            ("🤖 ML Engine", "Model loading, predictions, confidence scores"),
            ("💰 Risk Manager", "Position sizing, risk calculations"),
            ("🎯 Trading Strategy", "Signal generation, decision logic"),
            ("⚙️ Configuration", "Config loading, parameter validation"),
            ("📝 Logger System", "Log files, error tracking"),
            ("💾 Cache System", "Cache files, data persistence")
        ]
        
        for name, desc in test_info:
            with st.expander(name):
                st.markdown(f"**Tests:** {desc}")
                st.markdown("**Purpose:** Ensure component is working correctly")
                st.markdown("**Expected:** PASS status")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Version:** 1.0.0")

with col2:
    st.markdown("**Status:** 🟢 Online")

with col3:
    st.markdown("**Made with ❤️ by SALMAN ThinkTank**")
