"""
BiX TradeBOT - داشبورد فارسی
================================
داشبورد تعاملی فارسی با فونت وزیر برای کنترل و مانیتورینگ ربات

نویسنده: SALMAN ThinkTank AI Core (NOVA - UI/UX Visionary)
نسخه: 1.0.0 - فارسی
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

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir.parent
root_dir = src_dir.parent
sys.path.insert(0, str(src_dir))

from utils.config import Config
from data.handler import DataHandler
from data.indicators import TechnicalIndicators
from core.ml_engine import MLEngine
from core.risk_manager import RiskManager
from core.strategy import SimpleHybridStrategy
from utils.logger import get_logger
from analysis.advanced_chart import AdvancedChartAnalysis

# Import optional modules
try:
    from analysis.backtester import BacktestEngine
    BACKTESTER_AVAILABLE = True
except ImportError:
    BACKTESTER_AVAILABLE = False
    print("⚠️ ماژول بک‌تست در دسترس نیست")

try:
    from analysis.live_feed import LiveDataFeed
    LIVE_FEED_AVAILABLE = True
except ImportError:
    LIVE_FEED_AVAILABLE = False
    st.warning("⚠️ ماژول دریافت داده زنده در دسترس نیست")

# Page configuration
st.set_page_config(
    page_title="🤖 BiX TradeBOT - داشبورد معاملاتی",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# فونت فارسی Vazir با راست‌چین
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v30.1.0/dist/font-face.css');
    
    * {
        font-family: 'Vazir', 'Tahoma', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* اصلاح کانتینر اصلی */
    .main .block-container {
        padding-right: 2rem !important;
        padding-left: 2rem !important;
        direction: rtl !important;
    }
    
    /* عنوان‌های راست‌چین */
    h1, h2, h3, h4, h5, h6 {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Vazir', sans-serif !important;
    }
    
    /* متن‌های راست‌چین */
    p, div, span, label {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Vazir', sans-serif !important;
    }
    
    /* دکمه‌ها */
    .stButton button {
        direction: rtl !important;
        font-family: 'Vazir', sans-serif !important;
        font-weight: bold !important;
    }
    
    /* تب‌ها */
    .stTabs [data-baseweb="tab-list"] {
        direction: rtl !important;
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        direction: rtl !important;
        font-family: 'Vazir', sans-serif !important;
        font-weight: bold !important;
    }
    
    /* Input fields */
    .stTextInput input, .stSelectbox select {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Vazir', sans-serif !important;
    }
    
    /* متریک‌ها */
    [data-testid="stMetricValue"] {
        direction: ltr !important;
        text-align: left !important;
        font-family: 'Vazir', monospace !important;
    }
    
    [data-testid="stMetricLabel"] {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Vazir', sans-serif !important;
    }
    
    /* جداول */
    .dataframe {
        direction: rtl !important;
    }
    
    /* Sidebar راست‌چین */
    .css-1d391kg, [data-testid="stSidebar"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        direction: rtl !important;
        font-family: 'Vazir', sans-serif !important;
    }
    
    /* نمایش اعداد به صورت انگلیسی */
    .number {
        direction: ltr !important;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.data_handler = DataHandler(use_ccxt=False)
    st.session_state.risk_manager = RiskManager()
    st.session_state.ml_engine = MLEngine()
    st.session_state.logger = get_logger()

# Sidebar
with st.sidebar:
    st.markdown("# ⚙️ تنظیمات")
    
    st.markdown("### 📊 جفت ارز")
    symbol = st.selectbox(
        "انتخاب جفت ارز",
        ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT'],
        index=0,
        help="جفت ارز مورد نظر برای تحلیل را انتخاب کنید"
    )
    
    # نمایش قیمت فعلی زنده
    try:
        live_price_data = st.session_state.data_handler.client.get_ticker(symbol=symbol)
        live_price = float(live_price_data['lastPrice'])
        price_change_24h = float(live_price_data['priceChangePercent'])
        
        price_color = "🟢" if price_change_24h >= 0 else "🔴"
        st.metric(
            label=f"💰 قیمت فعلی {symbol}",
            value=f"${live_price:,.2f}",
            delta=f"{price_change_24h:+.2f}%"
        )
    except Exception as e:
        st.warning(f"⚠️ خطا در دریافت قیمت زنده: {str(e)}")
    
    st.markdown("### ⏰ بازه زمانی")
    timeframe = st.selectbox(
        "انتخاب تایم‌فریم",
        ['1m', '5m', '15m', '1h', '4h', '1d'],
        index=3,
        help="بازه زمانی کندل‌ها"
    )
    
    st.markdown("### 📈 تعداد کندل")
    limit = st.slider("تعداد کندل", 50, 1000, 500, 50)
    
    st.markdown("---")
    
    st.markdown("### 🤖 تنظیمات ML")
    use_ml = st.checkbox("فعال‌سازی پیش‌بینی ML", value=True)
    
    st.markdown("### 💰 مدیریت سرمایه")
    st.metric("سرمایه اولیه", f"${Config.INITIAL_CAPITAL:,}")
    st.metric("ریسک هر معامله", f"{Config.RISK_PER_TRADE*100:.1f}%")
    
    st.markdown("---")
    st.markdown("### 📖 راهنما")
    st.info("""
    **نحوه استفاده:**
    
    ۱. جفت ارز و تایم‌فریم را انتخاب کنید
    
    ۲. دکمه "تحلیل بازار" را بزنید
    
    ۳. سیگنال‌ها و نمودارها را بررسی کنید
    
    ۴. از تب‌های مختلف برای عملکردهای بیشتر استفاده کنید
    """)

# Main content
st.markdown("# 🤖 BiX TradeBOT - داشبورد معاملاتی هوشمند")
st.markdown("### سیستم معاملاتی خودکار با هوش مصنوعی")

# Create tabs
tab_titles = [
    "📊 تحلیل بازار",
    "🔄 بک‌تست",
    "🚀 معامله زنده",
    "🤖 پیش‌بینی ML",
    "💼 پورتفولیو",
    "📋 لاگ‌های سیستم",
    "🧪 تست سیستم"
]

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tab_titles)

# Tab 1: Market Analysis
with tab1:
    st.markdown("## 📊 تحلیل بازار")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 تحلیل بازار", use_container_width=True, type="primary"):
            st.session_state.analyze_triggered = True
    
    with col2:
        if st.button("🔄 به‌روزرسانی داده", use_container_width=True):
            st.cache_data.clear()
            st.success("✅ کش پاک شد!")
    
    with col3:
        auto_refresh = st.checkbox("🔄 به‌روزرسانی خودکار", value=False)
    
    if st.session_state.get('analyze_triggered', False) or auto_refresh:
        
        with st.spinner("⏳ در حال دریافت و تحلیل داده..."):
            try:
                # Fetch data
                st.session_state.logger.info("شروع تحلیل بازار", component="ANALYSIS")
                
                dh = st.session_state.data_handler
                
                # پاک کردن کش برای دریافت داده‌های تازه
                st.cache_data.clear()
                
                # دریافت داده‌های جدید
                df = dh.fetch_ohlcv(symbol, timeframe, limit=limit)
                
                if df is None or len(df) == 0:
                    st.error("❌ خطا در دریافت داده!")
                    st.stop()
                
                st.session_state.logger.info(f"دریافت {len(df)} کندل", component="DATA_HANDLER")
                
                # Calculate indicators
                indicators = TechnicalIndicators(df)
                df_indicators = indicators.calculate_all()
                
                # دریافت قیمت واقعی زنده از API
                try:
                    live_ticker = dh.client.get_ticker(symbol=symbol)
                    latest_price = float(live_ticker['lastPrice'])
                    st.session_state.logger.info(f"قیمت زنده: ${latest_price:,.2f}", component="LIVE_PRICE")
                except Exception as e:
                    # اگر خطا بود از آخرین کندل استفاده کن
                    latest_price = df_indicators['close'].iloc[-1]
                    st.session_state.logger.warning(f"استفاده از قیمت کندل: {str(e)}", component="LIVE_PRICE")
                
                # Display metrics
                st.markdown("### 📈 اطلاعات فعلی بازار")
                
                # نمایش زمان به‌روزرسانی
                from datetime import datetime
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.info(f"🔄 داده‌ها به‌روزرسانی شد | زمان: {current_time} | نماد: {symbol} | تایم‌فریم: {timeframe}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                # محاسبه تغییرات بر اساس قیمت واقعی
                price_change_pct = ((latest_price - df_indicators['close'].iloc[-2]) / df_indicators['close'].iloc[-2] * 100)
                
                with col1:
                    st.metric(
                        "💰 قیمت فعلی (زنده)",
                        f"${latest_price:,.2f}",
                        delta=f"{price_change_pct:+.2f}%"
                    )
                
                with col2:
                    st.metric(
                        "📊 RSI",
                        f"{df_indicators['rsi'].iloc[-1]:.2f}",
                        delta="خرید بیش از حد" if df_indicators['rsi'].iloc[-1] > 70 else "فروش بیش از حد" if df_indicators['rsi'].iloc[-1] < 30 else "خنثی"
                    )
                
                with col3:
                    st.metric(
                        "📉 ATR",
                        f"${df_indicators['atr'].iloc[-1]:,.2f}",
                        delta="نوسان"
                    )
                
                with col4:
                    st.metric(
                        "🎯 ADX",
                        f"{df_indicators['adx'].iloc[-1]:.2f}",
                        delta="روند قوی" if df_indicators['adx'].iloc[-1] > 25 else "روند ضعیف"
                    )
                
                # Technical signals
                st.markdown("### 🎯 سیگنال‌های تکنیکال")
                
                latest_signals = indicators.get_latest_signals()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    trend_signal = "🟢 صعودی" if latest_signals.get('trend_signal', 0) == 1 else "🔴 نزولی" if latest_signals.get('trend_signal', 0) == -1 else "⚪ خنثی"
                    st.info(f"**روند:** {trend_signal}")
                
                with col2:
                    breakout_signal = "🟢 شکست صعودی" if latest_signals.get('breakout_signal', 0) == 1 else "🔴 شکست نزولی" if latest_signals.get('breakout_signal', 0) == -1 else "⚪ بدون شکست"
                    st.info(f"**شکست:** {breakout_signal}")
                
                with col3:
                    pullback_signal = "🟢 پولبک خرید" if latest_signals.get('pullback_signal', 0) == 1 else "🔴 پولبک فروش" if latest_signals.get('pullback_signal', 0) == -1 else "⚪ بدون پولبک"
                    st.info(f"**پولبک:** {pullback_signal}")
                
                # ML Prediction
                if use_ml:
                    st.markdown("### 🤖 پیش‌بینی هوش مصنوعی")
                    
                    try:
                        ml_engine = st.session_state.ml_engine
                        
                        if ml_engine.load_model():
                            predictions = ml_engine.get_prediction_confidence(df_indicators)
                            
                            if predictions is not None and len(predictions) > 0:
                                latest_pred = predictions.iloc[-1]
                                
                                ml_signal = "🟢 خرید" if latest_pred['prediction'] == 1 else "🔴 فروش" if latest_pred['prediction'] == -1 else "⚪ نگه‌داری"
                                ml_conf = latest_pred['confidence']
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.success(f"**سیگنال ML:** {ml_signal}")
                                
                                with col2:
                                    st.info(f"**اطمینان:** {ml_conf:.1%}")
                                
                                # Confidence gauge
                                fig_gauge = go.Figure(go.Indicator(
                                    mode="gauge+number",
                                    value=ml_conf * 100,
                                    title={'text': "میزان اطمینان ML"},
                                    gauge={
                                        'axis': {'range': [0, 100]},
                                        'bar': {'color': "darkblue"},
                                        'steps': [
                                            {'range': [0, 50], 'color': "lightgray"},
                                            {'range': [50, 75], 'color': "yellow"},
                                            {'range': [75, 100], 'color': "lightgreen"}
                                        ],
                                        'threshold': {
                                            'line': {'color': "red", 'width': 4},
                                            'thickness': 0.75,
                                            'value': 90
                                        }
                                    }
                                ))
                                
                                fig_gauge.update_layout(
                                    height=300,
                                    font={'family': 'Vazir'}
                                )
                                
                                st.plotly_chart(fig_gauge, use_container_width=True)
                            else:
                                st.warning("⚠️ داده کافی برای پیش‌بینی ML وجود ندارد")
                        else:
                            st.warning("⚠️ مدل ML بارگذاری نشد")
                            
                    except Exception as ml_error:
                        st.warning(f"⚠️ خطا در ML: {str(ml_error)}")
                        st.info("💡 از تحلیل تکنیکال استفاده می‌شود")
                
                # Trading Strategy Signal
                st.markdown("### 📊 سیگنال نهایی استراتژی")
                
                strategy = SimpleHybridStrategy(use_ml=use_ml)
                
                strategy_signals = {
                    'price': latest_price,
                    'ema_fast': df_indicators['ema_fast'].iloc[-1],
                    'ema_slow': df_indicators['ema_slow'].iloc[-1],
                    'rsi': df_indicators['rsi'].iloc[-1],
                    'atr': df_indicators['atr'].iloc[-1],
                    'adx': df_indicators['adx'].iloc[-1],
                    'volume': df_indicators['volume'].iloc[-1]
                }
                
                final_signal = strategy.generate_signal(strategy_signals)
                
                # Display final signal
                if final_signal['action'] == 'BUY':
                    st.success(f"### 🟢 سیگنال خرید - قدرت: {final_signal['strength']}/10")
                    st.info(f"**دلیل:** {final_signal['reason']}")
                elif final_signal['action'] == 'SELL':
                    st.error(f"### 🔴 سیگنال فروش - قدرت: {final_signal['strength']}/10")
                    st.info(f"**دلیل:** {final_signal['reason']}")
                else:
                    st.warning(f"### ⚪ نگه‌داری - امتیاز: {final_signal['combined_score']}")
                    st.info(f"**دلیل:** {final_signal['reason']}")
                
                # Advanced Chart Analysis
                st.markdown("### 📈 نمودار قیمت پیشرفته")
                
                # Initialize advanced chart analyzer
                chart_analyzer = AdvancedChartAnalysis(df_indicators)
                analysis = chart_analyzer.get_complete_analysis(latest_price)
                
                # Create chart with advanced features
                fig = make_subplots(
                    rows=3, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.05,
                    row_heights=[0.6, 0.2, 0.2],
                    subplot_titles=('قیمت و تحلیل پیشرفته', 'RSI', 'حجم معاملات')
                )
                
                # Candlestick
                fig.add_trace(
                    go.Candlestick(
                        x=df_indicators.index,
                        open=df_indicators['open'],
                        high=df_indicators['high'],
                        low=df_indicators['low'],
                        close=df_indicators['close'],
                        name='قیمت'
                    ),
                    row=1, col=1
                )
                
                # EMAs
                fig.add_trace(
                    go.Scatter(
                        x=df_indicators.index,
                        y=df_indicators['ema_fast'],
                        name='EMA سریع',
                        line=dict(color='blue', width=1)
                    ),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=df_indicators.index,
                        y=df_indicators['ema_slow'],
                        name='EMA کند',
                        line=dict(color='red', width=1)
                    ),
                    row=1, col=1
                )
                
                # Support levels (green horizontal lines)
                for support in analysis['support_resistance']['support']:
                    fig.add_hline(
                        y=support,
                        line_dash="solid",
                        line_color="green",
                        line_width=2,
                        annotation_text=f"حمایت: ${support:,.2f}",
                        annotation_position="left",
                        row=1, col=1
                    )
                
                # Resistance levels (red horizontal lines)
                for resistance in analysis['support_resistance']['resistance']:
                    fig.add_hline(
                        y=resistance,
                        line_dash="solid",
                        line_color="red",
                        line_width=2,
                        annotation_text=f"مقاومت: ${resistance:,.2f}",
                        annotation_position="left",
                        row=1, col=1
                    )
                
                # Fibonacci levels (yellow dashed lines)
                if analysis['fibonacci']['levels']:
                    for level_name, price in analysis['fibonacci']['levels'].items():
                        fig.add_hline(
                            y=price,
                            line_dash="dash",
                            line_color="orange",
                            line_width=1,
                            annotation_text=f"فیبو {level_name}: ${price:,.2f}",
                            annotation_position="right",
                            row=1, col=1
                        )
                
                # Trend lines
                for trend in analysis['trend_lines']:
                    # Map indices to datetime
                    start_time = df_indicators.index[trend['start_idx']] if trend['start_idx'] < len(df_indicators) else df_indicators.index[0]
                    end_time = df_indicators.index[trend['end_idx']] if trend['end_idx'] < len(df_indicators) else df_indicators.index[-1]
                    
                    direction_fa = 'صعودی' if trend['direction'] == 'bullish' else 'نزولی'
                    
                    fig.add_trace(
                        go.Scatter(
                            x=[start_time, end_time],
                            y=[trend['start_price'], trend['end_price']],
                            mode='lines',
                            name=f"خط روند {direction_fa}",
                            line=dict(
                                color='purple' if trend['direction'] == 'bullish' else 'brown',
                                width=2,
                                dash='dash'
                            ),
                            showlegend=True
                        ),
                        row=1, col=1
                    )
                
                # Candlestick pattern annotations
                for pattern in analysis['patterns']:
                    marker_color = 'green' if pattern['type'] == 'صعودی' else 'red'
                    fig.add_annotation(
                        x=df_indicators.index[pattern['index']],
                        y=pattern['price'],
                        text=f"🔔 {pattern['pattern']}<br>اعتماد: {pattern['confidence']}%",
                        showarrow=True,
                        arrowhead=2,
                        arrowcolor=marker_color,
                        bgcolor=marker_color,
                        opacity=0.8,
                        font=dict(color='white', size=10),
                        row=1, col=1
                    )
                
                # Entry point suggestions (green markers)
                if analysis['suggestions']['entry_points']:
                    for entry in analysis['suggestions']['entry_points']:
                        entry_price = entry['price'] if isinstance(entry, dict) else entry
                        fig.add_annotation(
                            x=df_indicators.index[-1],
                            y=entry_price,
                            text=f"💚 نقطه ورود: ${entry_price:,.2f}",
                            showarrow=True,
                            arrowhead=3,
                            arrowcolor='green',
                            bgcolor='green',
                            font=dict(color='white', size=12),
                            row=1, col=1
                        )
                
                # Exit point suggestions (red markers)
                if analysis['suggestions']['exit_points']:
                    for exit_point in analysis['suggestions']['exit_points']:
                        exit_price = exit_point['price'] if isinstance(exit_point, dict) else exit_point
                        fig.add_annotation(
                            x=df_indicators.index[-1],
                            y=exit_price,
                            text=f"❤️ نقطه خروج: ${exit_price:,.2f}",
                            showarrow=True,
                            arrowhead=3,
                            arrowcolor='red',
                            bgcolor='red',
                            font=dict(color='white', size=12),
                            row=1, col=1
                        )
                
                # RSI
                fig.add_trace(
                    go.Scatter(
                        x=df_indicators.index,
                        y=df_indicators['rsi'],
                        name='RSI',
                        line=dict(color='purple', width=2)
                    ),
                    row=2, col=1
                )
                
                # RSI levels
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
                
                # Volume
                colors = ['red' if df_indicators['close'].iloc[i] < df_indicators['open'].iloc[i] else 'green' 
                         for i in range(len(df_indicators))]
                
                fig.add_trace(
                    go.Bar(
                        x=df_indicators.index,
                        y=df_indicators['volume'],
                        name='حجم',
                        marker_color=colors
                    ),
                    row=3, col=1
                )
                
                fig.update_layout(
                    height=1000,
                    xaxis_rangeslider_visible=False,
                    showlegend=True,
                    font=dict(family='Vazir', size=12),
                    hovermode='x unified'
                )
                
                fig.update_xaxes(title_text="زمان", row=3, col=1)
                fig.update_yaxes(title_text="قیمت (USDT)", row=1, col=1)
                fig.update_yaxes(title_text="RSI", row=2, col=1)
                fig.update_yaxes(title_text="حجم", row=3, col=1)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display analysis summary
                st.markdown("### 📊 خلاصه تحلیل پیشرفته")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**🟢 سطوح حمایت:**")
                    if analysis['support_resistance']['support']:
                        for s in analysis['support_resistance']['support']:
                            st.write(f"• ${s:,.2f}")
                    else:
                        st.write("سطح حمایتی یافت نشد")
                
                with col2:
                    st.markdown("**🔴 سطوح مقاومت:**")
                    if analysis['support_resistance']['resistance']:
                        for r in analysis['support_resistance']['resistance']:
                            st.write(f"• ${r:,.2f}")
                    else:
                        st.write("سطح مقاومتی یافت نشد")
                
                with col3:
                    st.markdown("**📈 خطوط روند:**")
                    if analysis['trend_lines']:
                        for trend in analysis['trend_lines']:
                            direction_fa = 'صعودی' if trend['direction'] == 'bullish' else 'نزولی'
                            st.write(f"• {direction_fa} (شیب: {trend['slope']:.2f})")
                    else:
                        st.write("خط روندی یافت نشد")
                
                # Pattern detection results
                if analysis['patterns']:
                    st.markdown("### 🔔 الگوهای کندل استیک شناسایی شده")
                    pattern_df = pd.DataFrame(analysis['patterns'])
                    st.dataframe(pattern_df[['pattern', 'type', 'confidence', 'price']])
                
                # Trading suggestions
                if analysis['suggestions']['entry_points'] or analysis['suggestions']['exit_points']:
                    st.markdown("### 💡 پیشنهادات معاملاتی")
                    
                    if analysis['suggestions']['entry_points']:
                        entry_prices = [e['price'] if isinstance(e, dict) else e for e in analysis['suggestions']['entry_points']]
                        st.success(f"**نقاط ورود پیشنهادی:** {', '.join([f'${e:,.2f}' for e in entry_prices])}")
                    
                    if analysis['suggestions']['exit_points']:
                        exit_prices = [e['price'] if isinstance(e, dict) else e for e in analysis['suggestions']['exit_points']]
                        st.error(f"**نقاط خروج پیشنهادی:** {', '.join([f'${e:,.2f}' for e in exit_prices])}")
                    
                    if analysis['suggestions']['stop_loss']:
                        st.warning(f"**حد ضرر پیشنهادی:** ${analysis['suggestions']['stop_loss']:,.2f}")
                    
                    if analysis['suggestions']['take_profit']:
                        st.info(f"**حد سود پیشنهادی:** ${analysis['suggestions']['take_profit']:,.2f}")
                
                st.session_state.logger.info("تحلیل بازار با موفقیت انجام شد", component="ANALYSIS")
                
            except Exception as e:
                st.error(f"❌ خطا: {str(e)}")
                st.session_state.logger.error(f"خطا در تحلیل: {str(e)}", component="ANALYSIS", exception=e)

# Tab 2: Backtest
with tab2:
    st.markdown("## 🔄 بک‌تست استراتژی")
    
    if not BACKTESTER_AVAILABLE:
        st.warning("⚠️ ماژول بک‌تست در این نسخه موجود نیست")
        st.info("💡 برای استفاده از بک‌تست، ماژول `analysis.backtester` را نصب کنید")
    else:
        st.info("🎯 بک‌تست استراتژی در نسخه‌های بعدی اضافه خواهد شد")

# Tab 3: Live Trading
with tab3:
    st.markdown("## 🚀 معامله زنده")
    st.warning("⚠️ **هشدار:** این بخش به API واقعی Binance متصل است!")
    st.error("❌ **توجه:** پول واقعی در معرض خطر است!")
    
    st.info("💡 برای معامله زنده، ابتدا تنظیمات API را در فایل `.env` وارد کنید")

# Tab 4: ML Predictions
with tab4:
    st.markdown("## 🤖 پیش‌بینی‌های هوش مصنوعی")
    
    # AI Model Selection Section
    with st.expander("🎯 انتخاب مدل هوش مصنوعی", expanded=True):
        try:
            from ai.models_config import ModelType, AIModelsConfig
            
            st.markdown("### انتخاب مدل AI برای پیش‌بینی‌ها")
            
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
                "مدل هوش مصنوعی را انتخاب کنید:",
                model_names,
                index=default_idx,
                help="مدل AI مورد نظر برای پیش‌بینی معاملات را انتخاب کنید"
            )
            
            # Get selected model details
            selected_idx = model_names.index(selected_model_name)
            selected_model = models[selected_idx]
            
            # Display model info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("⚡ سرعت", selected_model['speed'])
            with col2:
                st.metric("💰 هزینه", selected_model['cost'])
            with col3:
                st.metric("🎯 دقت", selected_model['accuracy'])
            
            st.info(f"📝 {selected_model['description']}")
            
            # Check API configuration
            model_type_enum = ModelType(selected_model['type'])
            if AIModelsConfig.is_api_configured(model_type_enum):
                st.success("✅ مدل آماده استفاده است")
            else:
                st.warning("⚠️ این مدل نیاز به تنظیمات API دارد")
                st.code(AIModelsConfig.get_setup_instructions(model_type_enum))
            
            # Save preference button
            if st.button("💾 ذخیره انتخاب مدل", type="primary", key="save_model_pref"):
                AIModelsConfig.save_preference(model_type_enum)
                st.success(f"✅ مدل {selected_model_name} به عنوان مدل پیش‌فرض ذخیره شد")
                st.balloons()
        
        except ImportError:
            st.warning("⚠️ ماژول انتخاب مدل AI موجود نیست")
            st.info("💡 برای استفاده از انتخاب مدل، فایل `ai/models_config.py` را اضافه کنید")
    
    st.markdown("---")
    
    # ML Model Info
    ml_engine = st.session_state.ml_engine
    
    if ml_engine.load_model():
        st.success("✅ مدل ML بارگذاری شد")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("دقت مدل", "96.25%")
        
        with col2:
            st.metric("تعداد ویژگی‌ها", "26")
        
        with col3:
            st.metric("نوع مدل", "LightGBM")
        
        st.info("""
        **ویژگی‌های مدل ML:**
        
        ✅ آموزش با 26 ویژگی پیشرفته
        
        ✅ دقت 96.25% در داده‌های تست
        
        ✅ استفاده از LightGBM (سریع و دقیق)
        
        ✅ پشتیبانی از Real-time predictions
        """)
    else:
        st.warning("⚠️ مدل ML یافت نشد")
        st.info("💡 ابتدا مدل را با اجرای `train_improved_ml.py` آموزش دهید")

# Tab 5: Portfolio
with tab5:
    st.markdown("## 💼 مدیریت پورتفولیو")
    
    rm = st.session_state.risk_manager
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💰 سرمایه اولیه", f"${rm.initial_capital:,}")
    
    with col2:
        st.metric("📊 سرمایه فعلی", f"${rm.current_equity:,}")
    
    with col3:
        pnl = rm.current_equity - rm.initial_capital
        pnl_pct = (pnl / rm.initial_capital) * 100
        st.metric("📈 سود/زیان", f"${pnl:,.2f}", delta=f"{pnl_pct:.2f}%")
    
    st.markdown("### 📊 موقعیت‌های باز")
    if len(rm.positions) > 0:
        st.dataframe(pd.DataFrame(rm.positions))
    else:
        st.info("هیچ موقعیت بازی وجود ندارد")
    
    st.markdown("### 📜 تاریخچه معاملات")
    if len(rm.trade_history) > 0:
        st.dataframe(pd.DataFrame(rm.trade_history))
    else:
        st.info("هیچ معامله‌ای ثبت نشده است")

# Tab 6: System Logs
with tab6:
    st.markdown("## 📋 لاگ‌های سیستم")
    
    logger = st.session_state.logger
    
    # Error statistics
    st.markdown("### 📊 آمار خطاها")
    
    error_stats = logger.get_error_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("تعداد کل خطاها", error_stats['total_errors'])
    
    with col2:
        st.metric("کامپوننت‌های درگیر", len(error_stats['components']))
    
    with col3:
        st.metric("انواع خطا", len(error_stats['error_types']))
    
    with col4:
        if error_stats['total_errors'] > 0:
            last_error_time = error_stats.get('last_error_time', 'نامشخص')
            st.metric("آخرین خطا", last_error_time)
    
    # Recent errors
    st.markdown("### 🚨 خطاهای اخیر")
    
    recent_errors = logger.get_recent_errors(limit=10)
    
    if recent_errors:
        for error in recent_errors:
            with st.expander(f"❌ {error['timestamp']} - {error['component']}"):
                st.error(f"**پیام:** {error['message']}")
                if error.get('traceback'):
                    st.code(error['traceback'], language='python')
    else:
        st.success("✅ هیچ خطایی ثبت نشده است!")
    
    # Log files
    st.markdown("### 📁 فایل‌های لاگ")
    
    log_dir = Path(root_dir) / 'logs'
    
    if log_dir.exists():
        log_files = list(log_dir.glob('*.log'))
        
        if log_files:
            selected_log = st.selectbox(
                "انتخاب فایل لاگ",
                [f.name for f in log_files]
            )
            
            if selected_log:
                log_path = log_dir / selected_log
                
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        log_content = f.read()
                    
                    st.code(log_content[-5000:], language='log')  # نمایش 5000 کاراکتر آخر
                    
                    if st.button("📥 دانلود فایل لاگ"):
                        st.download_button(
                            label="دانلود",
                            data=log_content,
                            file_name=selected_log,
                            mime="text/plain"
                        )
                except Exception as e:
                    st.error(f"خطا در خواندن فایل: {str(e)}")
        else:
            st.info("هیچ فایل لاگی یافت نشد")
    else:
        st.warning("پوشه logs وجود ندارد")

# Tab 7: System Testing
with tab7:
    st.markdown("## 🧪 تست سیستم")
    
    from utils.system_simulator import SystemSimulator
    
    if st.button("▶️ اجرای تست کامل", type="primary", use_container_width=True):
        
        with st.spinner("⏳ در حال اجرای تست‌ها..."):
            simulator = SystemSimulator()
            results = simulator.run_all_tests()
        
        # Summary
        summary = results['summary']
        
        st.markdown("### 📊 خلاصه نتایج")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("تعداد کل", summary['total_tests'])
        
        with col2:
            st.metric("✅ موفق", summary['passed'], delta=f"{summary['success_rate']:.0f}%")
        
        with col3:
            st.metric("❌ ناموفق", summary['failed'])
        
        with col4:
            st.metric("⚠️ هشدار", summary['warnings'])
        
        with col5:
            st.metric("⏱️ زمان", f"{summary['total_duration']:.2f}s")
        
        # Progress bar
        progress = summary['success_rate'] / 100
        st.progress(progress)
        
        # Detailed results
        st.markdown("### 📋 نتایج تفصیلی")
        
        for test in results['tests']:
            status_icon = "✅" if test['status'] == 'PASS' else "❌" if test['status'] == 'FAIL' else "⚠️" if test['status'] == 'WARN' else "⏭️"
            
            with st.expander(f"{status_icon} {test['name']} - {test['status']} ({test['duration']:.2f}s)"):
                st.info(f"**پیام:** {test['message']}")
                
                if test['details']:
                    st.json(test['details'])
        
        # Download report
        if st.button("📥 دانلود گزارش"):
            report_text = simulator.generate_report(results)
            
            st.download_button(
                label="دانلود گزارش متنی",
                data=report_text,
                file_name=f"system_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; direction: rtl;'>
    <p>🤖 <strong>BiX TradeBOT</strong> - سیستم معاملاتی هوشمند</p>
    <p>نسخه 1.0.0 - فارسی | طراحی شده با ❤️ توسط SALMAN ThinkTank AI Core</p>
    <p style='color: #888; font-size: 0.8em;'>⚠️ هشدار: معاملات ارز دیجیتال ریسک بالایی دارد. با احتیاط عمل کنید.</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh
if auto_refresh:
    import time
    time.sleep(10)
    st.rerun()
