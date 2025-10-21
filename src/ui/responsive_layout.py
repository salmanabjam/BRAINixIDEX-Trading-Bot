"""
Responsive Layout System
=========================
Mobile and tablet responsive design for Streamlit dashboard.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import streamlit as st
from typing import Literal


DeviceType = Literal['mobile', 'tablet', 'desktop']


def inject_responsive_css():
    """Inject responsive CSS."""
    st.markdown("""
    <style>
    /* Mobile First Approach */
    
    /* Base Mobile Styles */
    @media (max-width: 768px) {
        /* Hide sidebar by default on mobile */
        section[data-testid="stSidebar"] {
            display: none;
        }
        
        /* Stack columns */
        .row-widget.stHorizontal {
            flex-direction: column !important;
        }
        
        /* Full width elements */
        .element-container {
            width: 100% !important;
        }
        
        /* Larger touch targets */
        button {
            min-height: 44px !important;
            padding: 12px 20px !important;
        }
        
        /* Responsive charts */
        .js-plotly-plot {
            width: 100% !important;
        }
        
        /* Compact metrics */
        div[data-testid="stMetric"] {
            padding: 8px !important;
        }
        
        /* Smaller fonts */
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
    }
    
    /* Tablet Styles */
    @media (min-width: 769px) and (max-width: 1024px) {
        section[data-testid="stSidebar"] {
            width: 200px !important;
        }
        
        /* 2-column layout */
        .row-widget.stHorizontal > div {
            flex: 1 1 48% !important;
        }
    }
    
    /* Desktop Styles */
    @media (min-width: 1025px) {
        section[data-testid="stSidebar"] {
            width: 280px !important;
        }
    }
    
    /* Touch-friendly */
    @media (hover: none) and (pointer: coarse) {
        button, a, .stSelectbox {
            min-height: 44px !important;
        }
    }
    
    /* Landscape mode */
    @media (orientation: landscape) and (max-height: 500px) {
        section[data-testid="stSidebar"] {
            display: none !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def get_device_type() -> DeviceType:
    """Detect device type (simplified)."""
    # In real app, use JavaScript to detect actual screen size
    # For now, return desktop
    return 'desktop'


def responsive_columns(mobile: int = 1, tablet: int = 2, desktop: int = 3):
    """Create responsive columns based on device."""
    device = get_device_type()
    
    if device == 'mobile':
        return st.columns(mobile)
    elif device == 'tablet':
        return st.columns(tablet)
    else:
        return st.columns(desktop)


def mobile_friendly_chart(fig, height: int = 400):
    """Display chart with mobile-friendly settings."""
    device = get_device_type()
    
    if device == 'mobile':
        height = 300
        fig.update_layout(
            margin=dict(l=10, r=10, t=30, b=10),
            font=dict(size=10)
        )
    
    st.plotly_chart(fig, use_container_width=True, height=height)


class ResponsiveLayout:
    """Responsive layout helper."""
    
    @staticmethod
    def initialize():
        """Initialize responsive layout."""
        inject_responsive_css()
    
    @staticmethod
    def columns(mobile: int = 1, tablet: int = 2, desktop: int = 3):
        """Create responsive columns."""
        return responsive_columns(mobile, tablet, desktop)
    
    @staticmethod
    def chart(fig, mobile_height: int = 300, desktop_height: int = 500):
        """Display responsive chart."""
        device = get_device_type()
        height = mobile_height if device == 'mobile' else desktop_height
        mobile_friendly_chart(fig, height)
    
    @staticmethod
    def show_mobile_menu():
        """Show mobile hamburger menu."""
        if st.button("☰ منو", key="mobile_menu"):
            st.session_state.show_sidebar = not st.session_state.get(
                'show_sidebar', False
            )


if __name__ == "__main__":
    print("Responsive Layout System")
    print(f"Device: {get_device_type()}")
