"""
Theme Manager - Dark/Light Mode Toggle
=======================================
Theme management system with persistent user preferences.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import streamlit as st
import json
from pathlib import Path
from typing import Dict, Literal

ThemeType = Literal['dark', 'light']


THEMES: Dict[ThemeType, Dict] = {
    'dark': {
        'name': 'Dark Mode',
        'primaryColor': '#2962ff',
        'backgroundColor': '#0e1117',
        'secondaryBackgroundColor': '#262730',
        'textColor': '#fafafa',
        'font': 'Vazirmatn, sans-serif',
        'chart_template': 'plotly_dark',
        'success_color': '#00ff00',
        'error_color': '#ff0000',
        'warning_color': '#ffa500'
    },
    'light': {
        'name': 'Light Mode',
        'primaryColor': '#1f77b4',
        'backgroundColor': '#ffffff',
        'secondaryBackgroundColor': '#f0f2f6',
        'textColor': '#31333F',
        'font': 'Vazirmatn, sans-serif',
        'chart_template': 'plotly_white',
        'success_color': '#00cc00',
        'error_color': '#cc0000',
        'warning_color': '#ff8800'
    }
}


class ThemeManager:
    """Manage application themes."""
    
    def __init__(self, config_path: str = "config/theme.json"):
        """Initialize theme manager."""
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.current_theme = self.load_theme()
    
    def load_theme(self) -> ThemeType:
        """Load saved theme preference."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('theme', 'dark')
            except:
                pass
        return 'dark'
    
    def save_theme(self, theme: ThemeType):
        """Save theme preference."""
        with open(self.config_path, 'w') as f:
            json.dump({'theme': theme}, f)
        self.current_theme = theme
    
    def toggle_theme(self):
        """Toggle between dark and light."""
        new_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.save_theme(new_theme)
        return new_theme
    
    def get_theme(self) -> Dict:
        """Get current theme config."""
        return THEMES[self.current_theme]
    
    def apply_theme(self):
        """Apply theme to Streamlit."""
        theme = self.get_theme()
        
        css = f"""
        <style>
        :root {{
            --primary-color: {theme['primaryColor']};
            --background-color: {theme['backgroundColor']};
            --secondary-bg-color: {theme['secondaryBackgroundColor']};
            --text-color: {theme['textColor']};
        }}
        
        .stApp {{
            background-color: {theme['backgroundColor']};
            color: {theme['textColor']};
        }}
        
        section[data-testid="stSidebar"] {{
            background-color: {theme['secondaryBackgroundColor']};
        }}
        
        .success-text {{
            color: {theme['success_color']};
        }}
        
        .error-text {{
            color: {theme['error_color']};
        }}
        
        .warning-text {{
            color: {theme['warning_color']};
        }}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
    
    def get_chart_template(self) -> str:
        """Get Plotly chart template for current theme."""
        return self.get_theme()['chart_template']


def create_theme_toggle():
    """Create theme toggle widget."""
    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()
    
    theme_manager = st.session_state.theme_manager
    current = theme_manager.current_theme
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        icon = "🌙" if current == 'dark' else "☀️"
        label = "حالت روز" if current == 'dark' else "حالت شب"
        
        if st.button(f"{icon} {label}", use_container_width=True):
            new_theme = theme_manager.toggle_theme()
            st.rerun()
    
    theme_manager.apply_theme()
    
    return theme_manager


if __name__ == "__main__":
    print("Theme Manager")
    tm = ThemeManager()
    print(f"Current theme: {tm.current_theme}")
    print(f"Theme config: {tm.get_theme()}")
