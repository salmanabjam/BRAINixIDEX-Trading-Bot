"""
Unit tests for core.strategy module
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.strategy import SimpleHybridStrategy


class TestSimpleHybridStrategy:
    """Test suite for SimpleHybridStrategy class"""
    
    @pytest.fixture
    def strategy(self):
        """Create strategy instance"""
        return SimpleHybridStrategy(use_ml=False)
    
    @pytest.fixture
    def strategy_with_ml(self):
        """Create strategy with ML enabled"""
        return SimpleHybridStrategy(use_ml=True)
    
    @pytest.fixture
    def bullish_signals(self):
        """Sample bullish market signals"""
        return {
            'price': 50000,
            'ema_fast': 49000,
            'ema_slow': 48000,
            'rsi': 65,
            'atr': 500,
            'adx': 30,
            'volume': 10000,
            'trend_signal': 1,
            'breakout_signal': 1,
            'pullback_signal': 0
        }
    
    @pytest.fixture
    def bearish_signals(self):
        """Sample bearish market signals"""
        return {
            'price': 50000,
            'ema_fast': 51000,
            'ema_slow': 52000,
            'rsi': 35,
            'atr': 500,
            'adx': 30,
            'volume': 10000,
            'trend_signal': -1,
            'breakout_signal': -1,
            'pullback_signal': 0
        }
    
    @pytest.fixture
    def neutral_signals(self):
        """Sample neutral market signals"""
        return {
            'price': 50000,
            'ema_fast': 50000,
            'ema_slow': 50000,
            'rsi': 50,
            'atr': 500,
            'adx': 15,
            'volume': 10000,
            'trend_signal': 0,
            'breakout_signal': 0,
            'pullback_signal': 0
        }
    
    def test_init(self):
        """Test strategy initialization"""
        strategy = SimpleHybridStrategy(use_ml=False)
        assert strategy.use_ml is False
        
        strategy_ml = SimpleHybridStrategy(use_ml=True)
        assert strategy_ml.use_ml is True
    
    def test_generate_signal_bullish(self, strategy, bullish_signals):
        """Test signal generation for bullish market"""
        signal = strategy.generate_signal(bullish_signals)
        
        assert 'action' in signal
        assert 'strength' in signal
        assert 'reason' in signal
        assert 'combined_score' in signal
        
        assert signal['action'] in ['BUY', 'SELL', 'HOLD']
        assert 0 <= signal['strength'] <= 10
    
    def test_generate_signal_bearish(self, strategy, bearish_signals):
        """Test signal generation for bearish market"""
        signal = strategy.generate_signal(bearish_signals)
        
        assert signal['action'] in ['BUY', 'SELL', 'HOLD']
        assert 0 <= signal['strength'] <= 10
    
    def test_generate_signal_neutral(self, strategy, neutral_signals):
        """Test signal generation for neutral market"""
        signal = strategy.generate_signal(neutral_signals)
        
        assert signal['action'] == 'HOLD'
    
    def test_generate_signal_with_ml(self, strategy_with_ml, bullish_signals):
        """Test signal generation with ML prediction"""
        signal = strategy_with_ml.generate_signal(
            bullish_signals,
            ml_prediction=1,
            ml_confidence=0.8
        )
        
        assert signal is not None
        assert 'action' in signal
    
    def test_strong_buy_signal(self, strategy):
        """Test strong buy signal conditions"""
        strong_buy = {
            'price': 50000,
            'ema_fast': 48000,
            'ema_slow': 46000,
            'rsi': 70,
            'atr': 500,
            'adx': 35,
            'volume': 20000,
            'trend_signal': 1,
            'breakout_signal': 1,
            'pullback_signal': 1,
            'combined_signal': 3  # Strong combined signal
        }
        
        signal = strategy.generate_signal(strong_buy)
        assert signal['action'] == 'BUY'
        assert signal['strength'] >= 2  # At least moderate strength
    
    def test_strong_sell_signal(self, strategy):
        """Test strong sell signal conditions"""
        strong_sell = {
            'price': 50000,
            'ema_fast': 52000,
            'ema_slow': 54000,
            'rsi': 30,
            'atr': 500,
            'adx': 35,
            'volume': 20000,
            'trend_signal': -1,
            'breakout_signal': -1,
            'pullback_signal': -1,
            'combined_signal': -3  # Strong combined signal
        }
        
        signal = strategy.generate_signal(strong_sell)
        assert signal['action'] == 'SELL'
        assert signal['strength'] >= 2  # At least moderate strength
    
    def test_overbought_condition(self, strategy):
        """Test overbought RSI condition"""
        overbought = {
            'price': 50000,
            'ema_fast': 49000,
            'ema_slow': 48000,
            'rsi': 75,
            'atr': 500,
            'adx': 30,
            'volume': 10000,
            'trend_signal': 1,
            'breakout_signal': 0,
            'pullback_signal': 0
        }
        
        signal = strategy.generate_signal(overbought)
        assert signal is not None
    
    def test_oversold_condition(self, strategy):
        """Test oversold RSI condition"""
        oversold = {
            'price': 50000,
            'ema_fast': 51000,
            'ema_slow': 52000,
            'rsi': 25,
            'atr': 500,
            'adx': 30,
            'volume': 10000,
            'trend_signal': -1,
            'breakout_signal': 0,
            'pullback_signal': 0
        }
        
        signal = strategy.generate_signal(oversold)
        assert signal is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=core.strategy', '--cov-report=term-missing'])
