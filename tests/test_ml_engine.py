"""
Unit tests for core.ml_engine module
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.ml_engine import MLEngine


class TestMLEngine:
    """Test suite for MLEngine class"""
    
    @pytest.fixture
    def sample_data_with_indicators(self):
        """Generate sample data with indicators"""
        dates = pd.date_range(start='2025-01-01', periods=500, freq='1H')
        np.random.seed(42)
        
        close_prices = np.cumsum(np.random.randn(500)) + 100
        data = {
            'open': close_prices + np.random.uniform(-1, 1, 500),
            'high': close_prices + np.random.uniform(0, 2, 500),
            'low': close_prices - np.random.uniform(0, 2, 500),
            'close': close_prices,
            'volume': np.random.uniform(1000, 10000, 500),
            'ema_fast': close_prices * 0.99,
            'ema_slow': close_prices * 0.98,
            'rsi': np.random.uniform(30, 70, 500),
            'macd': np.random.uniform(-1, 1, 500),
            'macd_signal': np.random.uniform(-1, 1, 500),
            'atr': np.random.uniform(0.5, 2, 500),
            'adx': np.random.uniform(20, 40, 500),
            'bb_upper': close_prices * 1.02,
            'bb_middle': close_prices,
            'bb_lower': close_prices * 0.98,
            'donchian_upper': close_prices * 1.03,
            'donchian_lower': close_prices * 0.97,
            'di_plus': np.random.uniform(15, 35, 500),
            'di_minus': np.random.uniform(15, 35, 500),
            'trend_signal': np.random.choice([0, 1, 2], 500),
            'breakout_signal': np.random.choice([0, 1, 2], 500),
            'pullback_signal': np.random.choice([0, 1, 2], 500),
            'combined_signal': np.random.choice([0, 1, 2], 500)
        }
        df = pd.DataFrame(data, index=dates)
        return df
    
    @pytest.fixture
    def ml_engine(self):
        """Create MLEngine instance"""
        return MLEngine(timeframe='1h')
    
    def test_init(self, ml_engine):
        """Test MLEngine initialization"""
        assert ml_engine.timeframe == '1h'
        assert ml_engine.model is None
    
    def test_train(self, ml_engine, sample_data_with_indicators):
        """Test model training"""
        metrics = ml_engine.train(sample_data_with_indicators)
        
        assert 'accuracy' in metrics
        assert 'train_size' in metrics
        assert 'test_size' in metrics
        assert ml_engine.model is not None
    
    def test_predict(self, ml_engine, sample_data_with_indicators):
        """Test prediction"""
        ml_engine.train(sample_data_with_indicators)
        predictions = ml_engine.predict(sample_data_with_indicators)
        
        assert predictions is not None
        assert len(predictions) > 0
        assert all(p in [-1, 0, 1] for p in predictions)
    
    def test_get_prediction_confidence(self, ml_engine, sample_data_with_indicators):
        """Test prediction with confidence"""
        ml_engine.train(sample_data_with_indicators)
        result = ml_engine.get_prediction_confidence(sample_data_with_indicators)
        
        assert 'prediction' in result.columns
        assert 'confidence' in result.columns
        assert (result['confidence'] >= 0).all()
        assert (result['confidence'] <= 1).all()
    
    def test_save_and_load_model(self, ml_engine, sample_data_with_indicators, tmp_path):
        """Test saving and loading model"""
        ml_engine.model_dir = tmp_path
        ml_engine.train(sample_data_with_indicators)
        
        # Save model
        saved = ml_engine.save_model()
        assert saved is True
        
        # Create new engine and load
        new_engine = MLEngine(timeframe='1h')
        new_engine.model_dir = tmp_path
        loaded = new_engine.load_model()
        
        assert loaded is True
        assert new_engine.model is not None
    
    def test_feature_engineering(self, ml_engine, sample_data_with_indicators):
        """Test feature engineering"""
        ml_engine.train(sample_data_with_indicators)
        
        # Features should be created
        assert hasattr(ml_engine, 'feature_columns')
        assert len(ml_engine.feature_columns) > 0
    
    def test_predict_without_training(self, tmp_path, sample_data_with_indicators):
        """Test prediction without training (should load existing model or fail)"""
        # Create fresh MLEngine with non-existent model path
        ml_engine = MLEngine(timeframe='test_nonexistent')
        ml_engine.model_path = tmp_path / 'nonexistent_model.pkl'
        
        predictions = ml_engine.predict(sample_data_with_indicators)
        # Should return None when no model exists
        assert predictions is None
    
    def test_train_with_insufficient_data(self, ml_engine):
        """Test training with insufficient data"""
        small_df = pd.DataFrame({
            'close': [100, 101, 102],
            'volume': [1000, 1100, 1200]
        })
        
        with pytest.raises(Exception):
            ml_engine.train(small_df)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=core.ml_engine', '--cov-report=term-missing'])
