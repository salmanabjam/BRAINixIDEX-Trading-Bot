"""
Advanced Charting Tests
=======================
Test advanced charting functionality.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from analysis.advanced_charting import (
    AdvancedTradingChart,
    create_comparison_chart
)


class TestAdvancedCharting(unittest.TestCase):
    """Test advanced charting features."""
    
    def setUp(self):
        """Create sample OHLCV data with indicators."""
        dates = pd.date_range(start='2025-01-01', periods=200, freq='1h')
        
        # Generate realistic price data
        np.random.seed(42)
        base_price = 50000
        price_changes = np.random.randn(200) * 100
        close_prices = base_price + np.cumsum(price_changes)
        
        self.data = pd.DataFrame({
            'timestamp': dates,
            'open': close_prices + np.random.randn(200) * 50,
            'high': close_prices + np.abs(np.random.randn(200) * 100),
            'low': close_prices - np.abs(np.random.randn(200) * 100),
            'close': close_prices,
            'volume': np.random.randint(100, 1000, 200)
        })
        
        self.data.set_index('timestamp', inplace=True)
        
        # Add indicators
        self.data['ema_fast'] = self.data['close'].ewm(span=50).mean()
        self.data['ema_slow'] = self.data['close'].ewm(span=200).mean()
        self.data['rsi'] = 50 + np.random.randn(200) * 10
        
        # MACD
        self.data['macd'] = np.random.randn(200) * 50
        self.data['macd_signal'] = self.data['macd'].ewm(span=9).mean()
        self.data['macd_hist'] = self.data['macd'] - self.data['macd_signal']
        
        # Bollinger Bands
        rolling_mean = self.data['close'].rolling(20).mean()
        rolling_std = self.data['close'].rolling(20).std()
        self.data['bb_middle'] = rolling_mean
        self.data['bb_upper'] = rolling_mean + (rolling_std * 2)
        self.data['bb_lower'] = rolling_mean - (rolling_std * 2)
        
        # Signals
        self.data['signal'] = 0
        self.data.loc[self.data.index[10], 'signal'] = 1   # Buy
        self.data.loc[self.data.index[50], 'signal'] = -1  # Sell
        self.data.loc[self.data.index[100], 'signal'] = 1  # Buy
        
        self.chart = AdvancedTradingChart(self.data, 'BTCUSDT')
    
    def test_chart_initialization(self):
        """Test chart initialization."""
        self.assertEqual(self.chart.symbol, 'BTCUSDT')
        self.assertEqual(len(self.chart.data), 200)
        self.assertIn('close', self.chart.data.columns)
    
    def test_create_full_analysis_chart(self):
        """Test creating full analysis chart."""
        fig = self.chart.create_full_analysis_chart(
            show_ema=True,
            show_bb=True,
            show_signals=True,
            show_support_resistance=True,
            height=1000
        )
        
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data) > 0, True)
        self.assertEqual(fig.layout.height, 1000)
    
    def test_create_simple_chart(self):
        """Test creating simple chart."""
        fig = self.chart.create_simple_chart(
            indicators=['ema', 'volume'],
            height=600
        )
        
        self.assertIsNotNone(fig)
        self.assertEqual(fig.layout.height, 600)
    
    def test_support_resistance_calculation(self):
        """Test support/resistance level calculation."""
        levels = self.chart._calculate_support_resistance()
        
        self.assertIsInstance(levels, list)
        # Should have support and resistance levels
        support_count = sum(1 for l in levels if l[0] == 'support')
        resistance_count = sum(1 for l in levels if l[0] == 'resistance')
        
        self.assertGreater(support_count, 0)
        self.assertGreater(resistance_count, 0)
    
    def test_level_clustering(self):
        """Test level clustering functionality."""
        # Create test levels close to each other
        test_levels = [
            ('support', 50000),
            ('support', 50010),  # Close to first
            ('support', 50005),  # Close to first
            ('resistance', 51000),
            ('resistance', 52000)  # Far from others
        ]
        
        clustered = self.chart._cluster_levels(test_levels)
        
        # Should cluster the close support levels
        self.assertLess(len(clustered), len(test_levels))
    
    def test_chart_with_missing_indicators(self):
        """Test chart creation with missing indicators."""
        # Remove some indicators
        data_incomplete = self.data[['open', 'high', 'low', 'close', 'volume']].copy()
        
        chart = AdvancedTradingChart(data_incomplete, 'ETHUSDT')
        fig = chart.create_full_analysis_chart()
        
        # Should still create chart without errors
        self.assertIsNotNone(fig)
    
    def test_comparison_chart(self):
        """Test comparison chart creation."""
        # Create data for multiple symbols
        data_dict = {
            'BTCUSDT': self.data.copy(),
            'ETHUSDT': self.data.copy() * 0.05,  # Different price level
            'BNBUSDT': self.data.copy() * 0.01
        }
        
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        
        fig = create_comparison_chart(data_dict, symbols, height=600)
        
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 3)  # 3 traces for 3 symbols
    
    def test_chart_colors(self):
        """Test chart color scheme."""
        self.assertIn('up', self.chart.colors)
        self.assertIn('down', self.chart.colors)
        self.assertIn('ema_fast', self.chart.colors)
        self.assertIn('support', self.chart.colors)
        self.assertIn('resistance', self.chart.colors)
    
    def test_empty_data_handling(self):
        """Test handling of empty data."""
        empty_data = pd.DataFrame()
        
        with self.assertRaises(Exception):
            chart = AdvancedTradingChart(empty_data, 'BTCUSDT')
            chart.create_full_analysis_chart()


class TestChartIntegration(unittest.TestCase):
    """Test chart integration features."""
    
    def setUp(self):
        """Setup test data."""
        dates = pd.date_range(start='2025-01-01', periods=100, freq='1h')
        
        self.data = pd.DataFrame({
            'timestamp': dates,
            'open': 50000 + np.random.randn(100) * 100,
            'high': 50100 + np.random.randn(100) * 100,
            'low': 49900 + np.random.randn(100) * 100,
            'close': 50000 + np.random.randn(100) * 100,
            'volume': np.random.randint(100, 1000, 100)
        })
        
        self.data.set_index('timestamp', inplace=True)
    
    def test_data_structure(self):
        """Test data structure requirements."""
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        
        for col in required_columns:
            self.assertIn(col, self.data.columns)
    
    def test_data_completeness(self):
        """Test that data has no missing values."""
        self.assertEqual(self.data.isnull().sum().sum(), 0)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
