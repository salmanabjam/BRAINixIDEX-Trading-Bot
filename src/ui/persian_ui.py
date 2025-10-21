"""
Persian UI Enhancement Module
==============================
RTL layout, Persian fonts, and number formatting for Streamlit dashboard.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import streamlit as st
from typing import Optional, Dict, Any
import re


# Persian digit mapping
PERSIAN_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
ENGLISH_DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')


def to_persian_numbers(text: str) -> str:
    """Convert English numbers to Persian."""
    return str(text).translate(PERSIAN_DIGITS)


def to_english_numbers(text: str) -> str:
    """Convert Persian numbers to English."""
    return str(text).translate(ENGLISH_DIGITS)


def format_price_persian(price: float, decimals: int = 2) -> str:
    """Format price with Persian numbers and separators."""
    formatted = f"{price:,.{decimals}f}"
    return to_persian_numbers(formatted)


def inject_persian_css():
    """Inject CSS for Persian/RTL support."""
    st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');
    
    /* RTL Support */
    .rtl {
        direction: rtl;
        text-align: right;
    }
    
    /* Persian Font */
    .persian-text, .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, div {
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
    }
    
    /* Sidebar RTL */
    section[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        text-align: right;
    }
    
    /* Metrics RTL */
    div[data-testid="stMetric"] {
        direction: rtl;
        text-align: right;
    }
    
    div[data-testid="stMetricLabel"] {
        text-align: right;
    }
    
    /* Tables RTL */
    .dataframe {
        direction: rtl;
    }
    
    /* Buttons RTL */
    .stButton button {
        font-family: 'Vazirmatn', sans-serif;
    }
    
    /* Selectbox RTL */
    .stSelectbox label {
        text-align: right;
    }
    
    /* Input RTL */
    .stTextInput label {
        text-align: right;
    }
    
    /* Tabs RTL */
    .stTabs [data-baseweb="tab-list"] {
        direction: rtl;
    }
    
    /* Custom Persian Numbers */
    .persian-number {
        font-family: 'Vazirmatn', sans-serif;
        font-variant-numeric: lining-nums;
    }
    
    /* Chart Titles */
    .js-plotly-plot .plotly .gtitle {
        font-family: 'Vazirmatn', sans-serif !important;
    }
    </style>
    """, unsafe_allow_html=True)


def create_persian_metric(
    label: str,
    value: Any,
    delta: Optional[str] = None,
    delta_color: str = "normal"
):
    """Create metric with Persian formatting."""
    # Convert numbers to Persian
    if isinstance(value, (int, float)):
        value_str = format_price_persian(value)
    else:
        value_str = to_persian_numbers(str(value))
    
    if delta:
        delta_str = to_persian_numbers(str(delta))
    else:
        delta_str = None
    
    st.metric(
        label=label,
        value=value_str,
        delta=delta_str,
        delta_color=delta_color
    )


def persian_dataframe(df, **kwargs):
    """Display DataFrame with Persian numbers."""
    import pandas as pd
    
    df_display = df.copy()
    
    # Convert numeric columns to Persian
    for col in df_display.select_dtypes(include=['number']).columns:
        df_display[col] = df_display[col].apply(
            lambda x: format_price_persian(x) if pd.notna(x) else ''
        )
    
    st.dataframe(df_display, **kwargs)


class PersianUI:
    """Persian UI helper class."""
    
    @staticmethod
    def initialize():
        """Initialize Persian UI."""
        inject_persian_css()
        
        # Set page config if not set
        try:
            st.set_page_config(
                page_title="داشبورد BiX TradeBOT",
                page_icon="📊",
                layout="wide",
                initial_sidebar_state="expanded"
            )
        except:
            pass
    
    @staticmethod
    def header(text: str, level: int = 1):
        """Display Persian header."""
        tag = f"h{level}"
        st.markdown(
            f'<{tag} class="rtl persian-text">{text}</{tag}>',
            unsafe_allow_html=True
        )
    
    @staticmethod
    def text(text: str):
        """Display Persian text."""
        st.markdown(
            f'<p class="rtl persian-text">{text}</p>',
            unsafe_allow_html=True
        )
    
    @staticmethod
    def metric(label: str, value: Any, delta: Optional[str] = None):
        """Display Persian metric."""
        create_persian_metric(label, value, delta)
    
    @staticmethod
    def success(text: str):
        """Display success message in Persian."""
        st.success(f"✅ {text}")
    
    @staticmethod
    def error(text: str):
        """Display error message in Persian."""
        st.error(f"❌ {text}")
    
    @staticmethod
    def warning(text: str):
        """Display warning message in Persian."""
        st.warning(f"⚠️ {text}")
    
    @staticmethod
    def info(text: str):
        """Display info message in Persian."""
        st.info(f"💡 {text}")


if __name__ == "__main__":
    print("Persian UI Module")
    print("Test conversions:")
    print(f"123456 -> {to_persian_numbers('123456')}")
    print(f"۱۲۳۴۵۶ -> {to_english_numbers('۱۲۳۴۵۶')}")
    print(f"$50,000.00 -> {format_price_persian(50000)}")
