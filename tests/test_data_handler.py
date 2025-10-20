"""
Unit tests for data.handler module
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data.handler import DataHandler


class TestDataHandler:
    """Test suite for DataHandler class"""
    
    @pytest.fixture
    def handler(self):
        """Create a DataHandler instance for testing"""
        with patch('data.handler.Client'):
            return DataHandler(use_ccxt=False)
    
    @pytest.fixture
    def sample_ohlcv_data(self):
        """Generate sample OHLCV data for testing"""
        dates = pd.date_range(start='2025-01-01', periods=100, freq='1H')
        data = {
            'open': np.random.uniform(100, 110, 100),
            'high': np.random.uniform(110, 120, 100),
            'low': np.random.uniform(90, 100, 100),
            'close': np.random.uniform(100, 110, 100),
            'volume': np.random.uniform(1000, 10000, 100)
        }
        df = pd.DataFrame(data, index=dates)
        df.index.name = 'timestamp'
        return df
    
    def test_init_binance_client(self):
        """Test DataHandler initialization with Binance client"""
        with patch('data.handler.Client') as mock_client:
            handler = DataHandler(use_ccxt=False)
            assert handler.use_ccxt is False
            mock_client.assert_called_once()
    
    def test_init_ccxt_client(self):
        """Test DataHandler initialization with CCXT client"""
        with patch('data.handler.ccxt') as mock_ccxt:
            handler = DataHandler(use_ccxt=True)
            assert handler.use_ccxt is True
    
    def test_validate_data_valid(self, handler, sample_ohlcv_data):
        """Test data validation with valid data"""
        result = handler.validate_data(sample_ohlcv_data)
        assert result is True
    
    def test_validate_data_empty(self, handler):
        """Test data validation with empty DataFrame"""
        empty_df = pd.DataFrame()
        result = handler.validate_data(empty_df)
        assert result is False
    
    def test_validate_data_null_values(self, handler, sample_ohlcv_data):
        """Test data validation with null values"""
        sample_ohlcv_data.loc[sample_ohlcv_data.index[0], 'close'] = np.nan
        result = handler.validate_data(sample_ohlcv_data)
        assert result is False
    
    def test_validate_data_negative_prices(self, handler, sample_ohlcv_data):
        """Test data validation with negative prices"""
        sample_ohlcv_data.loc[sample_ohlcv_data.index[0], 'close'] = -100
        result = handler.validate_data(sample_ohlcv_data)
        assert result is False
    
    def test_validate_data_invalid_high_low(self, handler, sample_ohlcv_data):
        """Test data validation with high < low"""
        sample_ohlcv_data.loc[sample_ohlcv_data.index[0], 'high'] = 50
        sample_ohlcv_data.loc[sample_ohlcv_data.index[0], 'low'] = 100
        result = handler.validate_data(sample_ohlcv_data)
        assert result is False
    
    @patch('data.handler.Client')
    def test_fetch_latest_price(self, mock_client):
        """Test fetching latest price"""
        mock_instance = mock_client.return_value
        mock_instance.get_symbol_ticker.return_value = {'price': '50000.00'}
        
        handler = DataHandler(use_ccxt=False)
        price = handler.fetch_latest_price('BTCUSDT')
        
        assert price == 50000.00
        mock_instance.get_symbol_ticker.assert_called_once_with(symbol='BTCUSDT')
    
    def test_cache_filename_generation(self, handler):
        """Test cache filename generation"""
        filename = handler._get_cache_filename(
            'BTCUSDT', '1h', '2025-01-01', '2025-01-31'
        )
        expected = handler.cache_dir / 'BTCUSDT_1h_2025-01-01_2025-01-31.csv'
        assert filename == expected
    
    @patch('data.handler.Client')
    def test_fetch_ohlcv_with_cache(self, mock_client, handler, sample_ohlcv_data, tmp_path):
        """Test fetching OHLCV data from cache"""
        # Setup cache
        handler.cache_dir = tmp_path
        cache_file = handler._get_cache_filename('BTCUSDT', '1h', '2025-01-01', '2025-01-31')
        sample_ohlcv_data.to_csv(cache_file)
        
        # Fetch data
        df = handler.fetch_ohlcv('BTCUSDT', '1h', '2025-01-01', '2025-01-31', use_cache=True)
        
        assert df is not None
        assert len(df) == 100
        assert list(df.columns) == ['open', 'high', 'low', 'close', 'volume']
    
    @patch('data.handler.Client')
    def test_fetch_ohlcv_no_cache(self, mock_client, handler):
        """Test fetching OHLCV data from API"""
        # Mock API response
        mock_klines = [
            [1609459200000, '29000', '29500', '28500', '29200', '1000', 1609462799999, '29100000', 100, '500', '14550000', '0'],
            [1609462800000, '29200', '29600', '28800', '29400', '1200', 1609466399999, '35280000', 120, '600', '17640000', '0']
        ]
        
        mock_instance = mock_client.return_value
        mock_instance.get_historical_klines.return_value = mock_klines
        
        handler = DataHandler(use_ccxt=False)
        df = handler.fetch_ohlcv('BTCUSDT', '1h', '2025-01-01', '2025-01-31', use_cache=False)
        
        assert df is not None
        assert len(df) == 2
        assert 'close' in df.columns
    
    @patch('data.handler.Client')
    def test_get_account_balance(self, mock_client):
        """Test getting account balance"""
        mock_instance = mock_client.return_value
        mock_instance.get_account.return_value = {
            'balances': [
                {'asset': 'BTC', 'free': '1.5', 'locked': '0.0'},
                {'asset': 'USDT', 'free': '10000.0', 'locked': '0.0'},
                {'asset': 'ETH', 'free': '0.0', 'locked': '0.0'}
            ]
        }
        
        handler = DataHandler(use_ccxt=False)
        balance = handler.get_account_balance()
        
        assert 'BTC' in balance
        assert balance['BTC'] == 1.5
        assert 'USDT' in balance
        assert balance['USDT'] == 10000.0
        assert 'ETH' not in balance  # Zero balance should not be included
    
    def test_fetch_ohlcv_error_handling(self, handler):
        """Test error handling in fetch_ohlcv"""
        with patch.object(handler, '_fetch_binance', side_effect=Exception("API Error")):
            with pytest.raises(Exception):
                handler.fetch_ohlcv('BTCUSDT', '1h', use_cache=False)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=data.handler', '--cov-report=term-missing'])
