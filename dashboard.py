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

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from data_handler import DataHandler
from indicators import TechnicalIndicators
from ml_engine import MLEngine
from strategy_backtester import StrategyBacktester
from risk_manager import RiskManager
from strategy import SimpleHybridStrategy

# Import live data feed system
try:
    from live_data_feed import LiveDataFeed
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

# Header
st.markdown('<h1 class="main-header">🤖 BiX TradeBOT</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Trading Dashboard | SALMAN ThinkTank</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/667eea/ffffff?text=BiX+TradeBOT", use_container_width=True)
    
    st.markdown("### ⚙️ Configuration")
    
    symbol = st.selectbox(
        "Trading Pair",
        ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOGEUSDT"],
        index=0
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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Live Analysis",
    "🌐 Live Market Feed",
    "📈 Backtest",
    "🤖 ML Training",
    "📋 Settings"
])

# Tab 1: Live Analysis
with tab1:
    st.markdown("## 🎯 Real-Time Market Analysis")
    
    if st.button("▶️ Analyze Market", type="primary"):
        with st.spinner(f"Fetching {symbol} data..."):
            try:
                # Initialize data handler
                if st.session_state.data_handler is None:
                    st.session_state.data_handler = DataHandler(use_ccxt=False)
                
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
                
                # Calculate indicators
                indicators = TechnicalIndicators(df)
                df_indicators = indicators.calculate_all()
                
                # Get latest signals
                latest_signals = indicators.get_latest_signals()
                
                # ML prediction
                ml_pred = None
                ml_conf = None
                if enable_ml:
                    if st.session_state.ml_engine is None:
                        st.session_state.ml_engine = MLEngine()
                    
                    if not st.session_state.ml_engine.load_model():
                        st.warning("⚠️ No trained model found. Train model in ML Training tab.")
                    else:
                        predictions = st.session_state.ml_engine.get_prediction_confidence(
                            df_indicators.tail(1)
                        )
                        ml_pred = predictions['prediction'].iloc[-1]
                        ml_conf = predictions['confidence'].iloc[-1]
                
                # Generate signal
                strategy = SimpleHybridStrategy(use_ml=enable_ml)
                signal = strategy.generate_signal(
                    latest_signals,
                    ml_prediction=ml_pred,
                    ml_confidence=ml_conf
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
                st.error(f"❌ Error: {str(e)}")
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
            if st.button("🔄 Run Backtest on Current Data", type="primary"):
                with st.spinner("Running backtest..."):
                    try:
                        # Get predictions from ML model
                        if st.session_state.ml_engine and st.session_state.ml_engine.is_trained:
                            predictions = st.session_state.ml_engine.predict(data['df'])
                            
                            # Run backtest
                            backtester = StrategyBacktester(initial_capital=10000)
                            backtest_results = backtester.run_backtest(
                                df=data['df'],
                                predictions=predictions,
                                commission=0.001
                            )
                            
                            # Display metrics in columns
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric(
                                    "Total Return",
                                    f"{backtest_results['total_return']:.2f}%",
                                    delta=f"${backtest_results['final_capital'] - 10000:,.2f}"
                                )
                            
                            with col2:
                                st.metric(
                                    "Win Rate",
                                    f"{backtest_results['win_rate']:.1f}%",
                                    delta=f"{backtest_results['winning_trades']}/{backtest_results['total_trades']}"
                                )
                            
                            with col3:
                                st.metric(
                                    "Sharpe Ratio",
                                    f"{backtest_results['sharpe_ratio']:.2f}",
                                    delta="Risk-adjusted return"
                                )
                            
                            with col4:
                                st.metric(
                                    "Max Drawdown",
                                    f"{backtest_results['max_drawdown']:.2f}%",
                                    delta="Worst loss"
                                )
                            
                            # Display detailed stats
                            st.markdown("#### 📈 Detailed Statistics")
                            
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                stats_df = pd.DataFrame({
                                    'Metric': [
                                        'Total Trades',
                                        'Winning Trades',
                                        'Losing Trades',
                                        'Average Win',
                                        'Average Loss'
                                    ],
                                    'Value': [
                                        backtest_results['total_trades'],
                                        f"{backtest_results['winning_trades']} ✅",
                                        f"{backtest_results['losing_trades']} ❌",
                                        f"{backtest_results['avg_win']:.2f}%",
                                        f"{backtest_results['avg_loss']:.2f}%"
                                    ]
                                })
                                st.dataframe(stats_df, use_container_width=True, hide_index=True)
                            
                            with col_b:
                                capital_df = pd.DataFrame({
                                    'Metric': [
                                        'Initial Capital',
                                        'Final Capital',
                                        'Net Profit/Loss',
                                        'Total Return %',
                                        'Profit Factor'
                                    ],
                                    'Value': [
                                        f"${10000:,.2f}",
                                        f"${backtest_results['final_capital']:,.2f}",
                                        f"${backtest_results['final_capital'] - 10000:,.2f}",
                                        f"{backtest_results['total_return']:.2f}%",
                                        f"{abs(backtest_results['avg_win'] / backtest_results['avg_loss']) if backtest_results['avg_loss'] != 0 else 'N/A'}"
                                    ]
                                })
                                st.dataframe(capital_df, use_container_width=True, hide_index=True)
                            
                            # Create backtest chart
                            st.markdown("#### 📊 Backtest Visualization")
                            backtest_fig = backtester.create_chart(
                                df=data['df'],
                                predictions=predictions,
                                backtest_results=backtest_results,
                                symbol=symbol
                            )
                            st.plotly_chart(backtest_fig, use_container_width=True)
                            
                            # Trade history
                            if len(backtest_results['trades']) > 0:
                                st.markdown("#### 📋 Trade History")
                                trades_df = pd.DataFrame(backtest_results['trades'])
                                trades_df['profit_pct'] = trades_df['profit_pct'].apply(lambda x: f"{x:.2f}%")
                                trades_df['profit_usd'] = trades_df['profit_usd'].apply(lambda x: f"${x:.2f}")
                                st.dataframe(trades_df, use_container_width=True, hide_index=True)
                            
                            st.success("✅ Backtest complete!")
                        else:
                            st.warning("⚠️ Please train ML model first (ML Training tab)")
                            
                    except Exception as e:
                        st.error(f"❌ Backtest failed: {str(e)}")

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
                from live_data_feed import LiveDataFeed
                
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
                from backtest import BacktestEngine
                
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
        from ai_models_config import ModelType, AIModelsConfig
        
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

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Version:** 1.0.0")

with col2:
    st.markdown("**Status:** 🟢 Online")

with col3:
    st.markdown("**Made with ❤️ by SALMAN ThinkTank**")
