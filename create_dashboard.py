"""Create Ultimate Dashboard"""
from pathlib import Path

dashboard_code = """\"\"\"
BiX TradeBOT Ultimate Dashboard
\"\"\"
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from utils.config import Config
from data.handler import DataHandler
from data.indicators import TechnicalIndicators
from core.ml_engine import MLEngine
from analysis.advanced_chart import AdvancedChartAnalysis

try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False

st.set_page_config(
    page_title='BiX TradeBOT Ultimate',
    page_icon='🤖',
    layout='wide'
)

st.markdown(\"\"\"
<style>
    @import url("https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v30.1.0/dist/font-face.css");
    * { font-family: Vazir, Tahoma, sans-serif !important; direction: rtl !important; }
</style>
\"\"\", unsafe_allow_html=True)

if "initialized" not in st.session_state:
    st.session_state.config = Config()
    st.session_state.data_handler = DataHandler()
    st.session_state.indicators = TechnicalIndicators()
    st.session_state.ml_engine = MLEngine()
    st.session_state.symbol = "BTCUSDT"
    st.session_state.timeframe = "1h"
    st.session_state.initialized = True

st.markdown("<h1 style='text-align:center'>🤖 BiX TradeBOT - داشبورد نهایی</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ⚙️ تنظیمات")
    st.session_state.symbol = st.selectbox("جفت ارز", ["BTCUSDT", "ETHUSDT", "BNBUSDT"])
    st.session_state.timeframe = st.selectbox("تایم فریم", ["1m", "5m", "15m", "1h", "4h"])

end_date = datetime.now()
start_date = end_date - timedelta(days=90)
df = st.session_state.data_handler.get_data(
    symbol=st.session_state.symbol,
    timeframe=st.session_state.timeframe,
    start_date=start_date.strftime("%Y-%m-%d"),
    end_date=end_date.strftime("%Y-%m-%d")
)

if df is not None and not df.empty:
    st.success(f"✅ {len(df)} کندل بارگذاری شد")
    
    analyzer = AdvancedChartAnalysis(df)
    levels = analyzer.find_support_resistance()
    
    st.markdown("### 📊 سطوح حمایت و مقاومت")
    col1, col2 = st.columns(2)
    with col1:
        st.write("🟢 حمایت:", levels.get("support", []))
    with col2:
        st.write("🔴 مقاومت:", levels.get("resistance", []))
    
    st.markdown("### 📈 نمودار قیمت")
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"]
    )])
    fig.update_layout(height=600, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("❌ داده‌ای یافت نشد")

st.markdown("---")
st.markdown("<p style='text-align:center'>BiX TradeBOT v2.0 Ultimate</p>", unsafe_allow_html=True)
"""

# Write dashboard file
dashboard_path = Path("src/ui/dashboard.py")
dashboard_path.write_text(dashboard_code, encoding='utf-8')
print(f"✅ Dashboard created: {dashboard_path}")
