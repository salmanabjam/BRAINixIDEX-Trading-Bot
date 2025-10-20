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
        signal = strategy.generate_signal(sample_data)
        
        assert signal is not None
        assert signal in ['BUY', 'SELL', 'HOLD']
    
    def test_get_signal_strength(self, strategy, sample_data):
        """Test signal strength calculation"""
        strength = strategy.get_signal_strength(sample_data)
        
        assert strength is not None
        assert 0 <= strength <= 100


class TestRiskManager:
    """Test RiskManager class"""
    
    @pytest.fixture
    def risk_manager(self):
        """Create RiskManager instance"""
        return RiskManager(initial_capital=10000)
    
    def test_init(self, risk_manager):
        """Test initialization"""
        assert risk_manager is not None
        assert risk_manager.capital == 10000
    
    def test_calculate_position_size(self, risk_manager):
        """Test position size calculation"""
        size = risk_manager.calculate_position_size(
            current_price=100,
            stop_loss=95,
            atr=2.0
        )
        
        assert size is not None
        assert size > 0
        assert size <= risk_manager.capital * Config.MAX_POSITION_SIZE
    
    def test_set_stop_loss(self, risk_manager):
        """Test stop loss calculation"""
        stop_loss = risk_manager.set_stop_loss(
            entry_price=100,
            side='BUY',
            atr=2.0
        )
        
        assert stop_loss is not None
        assert stop_loss < 100  # For BUY, stop loss should be below entry
    
    def test_set_take_profit(self, risk_manager):
        """Test take profit calculation"""
        take_profit = risk_manager.set_take_profit(
            entry_price=100,
            stop_loss=95,
            side='BUY'
        )
        
        assert take_profit is not None
        assert take_profit > 100  # For BUY, take profit should be above entry


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
    print(f"✅ Calculated indicators")
    
    # 3. Generate signal
    strategy = SimpleHybridStrategy()
    signal = strategy.generate_signal(df)
    assert signal in ['BUY', 'SELL', 'HOLD']
    print(f"✅ Generated signal: {signal}")
    
    # 4. Calculate position size
    rm = RiskManager(initial_capital=10000)
    if signal != 'HOLD':
        position_size = rm.calculate_position_size(
            current_price=df['close'].iloc[-1],
            stop_loss=df['close'].iloc[-1] * 0.98,
            atr=df['atr'].iloc[-1]
        )
        assert position_size > 0
        print(f"✅ Position size: ${position_size:.2f}")
    
    print("✅ Integration test passed!")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
