"""
Unit tests for data.indicators module
"""
import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data.indicators import TechnicalIndicators


class TestTechnicalIndicators:
    """Test suite for TechnicalIndicators class"""
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample OHLCV data"""
        dates = pd.date_range(start='2025-01-01', periods=300, freq='1H')
        np.random.seed(42)
        
        close_prices = np.cumsum(np.random.randn(300)) + 100
        data = {
            'open': close_prices + np.random.uniform(-1, 1, 300),
            'high': close_prices + np.random.uniform(0, 2, 300),
            'low': close_prices - np.random.uniform(0, 2, 300),
            'close': close_prices,
            'volume': np.random.uniform(1000, 10000, 300)
        }
        df = pd.DataFrame(data, index=dates)
        df.index.name = 'timestamp'
        return df
    
    @pytest.fixture
    def indicators(self, sample_data):
        """Create TechnicalIndicators instance"""
        return TechnicalIndicators(sample_data)
    
    def test_init(self, sample_data):
        """Test TechnicalIndicators initialization"""
        ti = TechnicalIndicators(sample_data)
        assert ti.df is not None
        assert len(ti.df) == 300
    
    def test_calculate_all(self, indicators):
        """Test calculating all indicators"""
        df = indicators.calculate_all()
        
        required_columns = [
            'ema_fast', 'ema_slow', 'rsi', 'macd', 'macd_signal',
            'bb_upper', 'bb_middle', 'bb_lower', 'atr', 'adx'
        ]
        
        for col in required_columns:
            assert col in df.columns
        
        assert len(df) > 0
    
    def test_rsi_range(self, indicators):
        """Test RSI values are in valid range [0, 100]"""
        df = indicators.calculate_all()
        rsi_values = df['rsi'].dropna()
        
        assert (rsi_values >= 0).all()
        assert (rsi_values <= 100).all()
    
    def test_ema_calculation(self, indicators):
        """Test EMA calculation"""
        df = indicators.calculate_all()
        
        assert 'ema_fast' in df.columns
        assert 'ema_slow' in df.columns
        assert not df['ema_fast'].isna().all()
        assert not df['ema_slow'].isna().all()
    
    def test_macd_calculation(self, indicators):
        """Test MACD calculation"""
        df = indicators.calculate_all()
        
        assert 'macd' in df.columns
        assert 'macd_signal' in df.columns
        assert not df['macd'].isna().all()
    
    def test_bollinger_bands(self, indicators):
        """Test Bollinger Bands calculation"""
        df = indicators.calculate_all()
        
        assert 'bb_upper' in df.columns
        assert 'bb_middle' in df.columns
        assert 'bb_lower' in df.columns
        
        valid_data = df[['bb_upper', 'bb_middle', 'bb_lower']].dropna()
        assert (valid_data['bb_upper'] >= valid_data['bb_middle']).all()
        assert (valid_data['bb_middle'] >= valid_data['bb_lower']).all()
    
    def test_atr_positive(self, indicators):
        """Test ATR values are positive"""
        df = indicators.calculate_all()
        atr_values = df['atr'].dropna()
        
        assert (atr_values > 0).all()
    
    def test_adx_range(self, indicators):
        """Test ADX values are in valid range [0, 100]"""
        df = indicators.calculate_all()
        adx_values = df['adx'].dropna()
        
        assert (adx_values >= 0).all()
        assert (adx_values <= 100).all()
    
    def test_get_latest_signals(self, indicators):
        """Test getting latest signals"""
        indicators.calculate_all()
        signals = indicators.get_latest_signals()
        
        required_keys = [
            'timestamp', 'close', 'ema_fast', 'ema_slow',
            'rsi', 'atr', 'adx', 'trend_signal', 'breakout_signal',
            'pullback_signal', 'combined_signal'
        ]
        
        for key in required_keys:
            assert key in signals
    
    def test_trend_signal_values(self, indicators):
        """Test trend signal values are -1, 0, or 1"""
        indicators.calculate_all()
        signals = indicators.get_latest_signals()
        
        assert signals['trend_signal'] in [-1, 0, 1]
    
    def test_breakout_signal_values(self, indicators):
        """Test breakout signal values are -1, 0, or 1"""
        indicators.calculate_all()
        signals = indicators.get_latest_signals()
        
        assert signals['breakout_signal'] in [-1, 0, 1]
    
    def test_pullback_signal_values(self, indicators):
        """Test pullback signal values are -1, 0, or 1"""
        indicators.calculate_all()
        signals = indicators.get_latest_signals()
        
        assert signals['pullback_signal'] in [-1, 0, 1]
    
    def test_with_minimal_data(self):
        """Test with minimal data (edge case)"""
        dates = pd.date_range(start='2025-01-01', periods=50, freq='1H')
        data = {
            'open': [100] * 50,
            'high': [101] * 50,
            'low': [99] * 50,
            'close': [100] * 50,
            'volume': [1000] * 50
        }
        df = pd.DataFrame(data, index=dates)
        
        ti = TechnicalIndicators(df)
        result = ti.calculate_all()
        
        assert result is not None
        assert len(result) == 50


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=data.indicators', '--cov-report=term-missing'])
