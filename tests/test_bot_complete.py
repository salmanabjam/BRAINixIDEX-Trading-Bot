"""
BiX TradeBOT - Unit Tests
==========================
Comprehensive test suite for core modules.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import modules to test
from data.handler import DataHandler
from data.indicators import TechnicalIndicators
from core.strategy import SimpleHybridStrategy
from core.risk_manager import RiskManager
from utils.config import Config


class TestDataHandler:
    """Test DataHandler class"""
    
    def test_init(self):
        """Test initialization"""
        dh = DataHandler()
        assert dh is not None
        assert dh.client is not None
    
    def test_fetch_ohlcv(self):
        """Test fetching OHLCV data"""
        dh = DataHandler()
        df = dh.fetch_ohlcv(symbol='BTCUSDT', timeframe='1h', limit=100)
        
        assert df is not None
        assert len(df) > 0
        assert 'close' in df.columns
        assert 'volume' in df.columns
        assert df['close'].dtype == float
    
    def test_fetch_latest_price(self):
        """Test fetching latest price"""
        dh = DataHandler()
        price = dh.fetch_latest_price('BTCUSDT')
        
        assert price is not None
        assert isinstance(price, float)
        assert price > 0


class TestTechnicalIndicators:
    """Test TechnicalIndicators class"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample OHLCV data"""
        dates = pd.date_range(start='2025-01-01', periods=300, freq='1H')
        df = pd.DataFrame({
            'open': np.random.uniform(100, 110, 300),
            'high': np.random.uniform(110, 120, 300),
            'low': np.random.uniform(90, 100, 300),
            'close': np.random.uniform(100, 110, 300),
            'volume': np.random.uniform(1000, 2000, 300)
        }, index=dates)
        return df
    
    def test_init(self, sample_data):
        """Test initialization"""
        indicators = TechnicalIndicators(sample_data)
        assert indicators is not None
    
    def test_calculate_all(self, sample_data):
        """Test calculating all indicators"""
        indicators = TechnicalIndicators(sample_data)
        df = indicators.calculate_all()
        
        assert 'ema_fast' in df.columns
        assert 'ema_slow' in df.columns
        assert 'rsi' in df.columns
        assert 'adx' in df.columns
        assert 'atr' in df.columns
        
        # Check RSI range
        assert df['rsi'].min() >= 0
        assert df['rsi'].max() <= 100
    
    def test_signals(self, sample_data):
        """Test trading signals"""
        indicators = TechnicalIndicators(sample_data)
        df = indicators.calculate_all()
        
        assert 'trend_signal' in df.columns
        assert 'breakout_signal' in df.columns
        assert 'pullback_signal' in df.columns
        assert 'combined_signal' in df.columns
        
        # Signals should be -1, 0, or 1
        assert df['trend_signal'].isin([-1, 0, 1]).all()


class TestStrategy:
    """Test SimpleHybridStrategy class"""
    
    @pytest.fixture
    def strategy(self):
        """Create strategy instance"""
        return SimpleHybridStrategy()
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data with indicators"""
        dates = pd.date_range(start='2025-01-01', periods=300, freq='1H')
        df = pd.DataFrame({
            'close': np.random.uniform(100, 110, 300),
            'ema_fast': np.random.uniform(100, 110, 300),
            'ema_slow': np.random.uniform(100, 110, 300),
            'rsi': np.random.uniform(30, 70, 300),
            'adx': np.random.uniform(10, 40, 300),
            'atr': np.random.uniform(1, 5, 300),
            'trend_signal': np.random.choice([-1, 0, 1], 300),
            'breakout_signal': np.random.choice([-1, 0, 1], 300),
            'pullback_signal': np.random.choice([-1, 0, 1], 300),
            'combined_signal': np.random.choice([-1, 0, 1], 300)
        }, index=dates)
        return df
    
    def test_init(self, strategy):
        """Test initialization"""
        assert strategy is not None
    
    def test_generate_signal(self, strategy, sample_data):
        """Test signal generation"""
        # Create indicators dict from sample data
        indicators = {
            'combined_signal': sample_data['combined_signal'].iloc[-1],
            'trend_signal': sample_data['trend_signal'].iloc[-1],
            'breakout_signal': sample_data['breakout_signal'].iloc[-1],
            'pullback_signal': sample_data['pullback_signal'].iloc[-1]
        }
        
        signal = strategy.generate_signal(indicators)
        
        assert signal is not None
        assert isinstance(signal, dict)
        assert 'action' in signal
        assert signal['action'] in ['BUY', 'SELL', 'HOLD']
        assert 'strength' in signal
        assert 'reason' in signal
    
    def test_signal_strength(self, strategy, sample_data):
        """Test that strategy can process data"""
        # Create indicators dict from sample data
        indicators = {
            'combined_signal': sample_data['combined_signal'].iloc[-1],
            'trend_signal': sample_data['trend_signal'].iloc[-1],
            'breakout_signal': sample_data['breakout_signal'].iloc[-1],
            'pullback_signal': sample_data['pullback_signal'].iloc[-1]
        }
        
        signal = strategy.generate_signal(indicators)
        assert signal is not None
        assert 'strength' in signal
        assert isinstance(signal['strength'], (int, float))


class TestRiskManager:
    """Test RiskManager class"""
    
    @pytest.fixture
    def risk_manager(self):
        """Create RiskManager instance"""
        return RiskManager(initial_capital=10000)
    
    def test_init(self, risk_manager):
        """Test initialization"""
        assert risk_manager is not None
        assert risk_manager.initial_capital == 10000
        assert risk_manager.current_equity == 10000
    
    def test_calculate_position_size(self, risk_manager):
        """Test position size calculation"""
        result = risk_manager.calculate_position_size(
            entry_price=100,
            atr=2.0,
            direction='long'
        )
        
        assert result is not None
        assert 'size' in result
        assert 'value' in result
        assert 'stop_loss' in result
        assert 'take_profit' in result
        assert result['size'] > 0
        assert result['value'] <= risk_manager.current_equity * Config.MAX_POSITION_SIZE
        assert result['stop_loss'] < 100  # For long, SL should be below entry
        assert result['take_profit'] > 100  # For long, TP should be above entry


class TestConfig:
    """Test Config class"""
    
    def test_config_validation(self):
        """Test configuration validation"""
        try:
            Config.validate()
            assert True
        except ValueError:
            pytest.fail("Config validation failed")
    
    def test_api_keys_exist(self):
        """Test API keys are configured"""
        assert Config.BINANCE_API_KEY is not None
        assert Config.BINANCE_API_SECRET is not None
    
    def test_trading_parameters(self):
        """Test trading parameters are valid"""
        assert Config.RISK_PER_TRADE > 0
        assert Config.RISK_PER_TRADE <= 0.05
        assert Config.MAX_POSITION_SIZE > 0
        assert Config.MAX_POSITION_SIZE <= 1.0


def test_integration_full_analysis():
    """Integration test: Full market analysis"""
    print("\n🧪 Running integration test...")
    
    # 1. Fetch data
    dh = DataHandler()
    df = dh.fetch_ohlcv(symbol='BTCUSDT', timeframe='1h', limit=500)
    assert len(df) > 0
    print(f"✅ Fetched {len(df)} candles")
    
    # 2. Calculate indicators
    indicators = TechnicalIndicators(df)
    df = indicators.calculate_all()
    assert 'ema_fast' in df.columns
    print("✅ Calculated indicators")
    
    # 3. Generate signal
    strategy = SimpleHybridStrategy()
    indicators_dict = {
        'combined_signal': float(df['combined_signal'].iloc[-1]),
        'trend_signal': float(df['trend_signal'].iloc[-1]),
        'breakout_signal': float(df['breakout_signal'].iloc[-1]),
        'pullback_signal': float(df['pullback_signal'].iloc[-1])
    }
    signal_result = strategy.generate_signal(indicators_dict)
    assert signal_result is not None
    assert 'action' in signal_result
    assert signal_result['action'] in ['BUY', 'SELL', 'HOLD']
    print(f"✅ Generated signal: {signal_result['action']}")
    
    # 4. Calculate position size
    rm = RiskManager(initial_capital=10000)
    if signal_result['action'] != 'HOLD':
        position = rm.calculate_position_size(
            entry_price=float(df['close'].iloc[-1]),
            atr=float(df['atr'].iloc[-1]),
            direction='long' if signal_result['action'] == 'BUY' else 'short'
        )
        assert position is not None
        assert 'size' in position
        assert 'value' in position
        assert position['size'] > 0
        print(f"✅ Position size: {position['size']:.6f} "
              f"(${position['value']:.2f})")
    
    print("✅ Integration test passed!")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
