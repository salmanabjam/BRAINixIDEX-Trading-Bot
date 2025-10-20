"""
Pytest configuration and shared fixtures
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


@pytest.fixture(scope='session')
def test_data_dir():
    """Test data directory"""
    return Path(__file__).parent / 'test_data'


@pytest.fixture(scope='session')
def mock_config():
    """Mock configuration for tests"""
    class MockConfig:
        SYMBOL = 'BTCUSDT'
        TIMEFRAME = '1h'
        INITIAL_CAPITAL = 10000
        RISK_PER_TRADE = 0.02
        ML_ENABLED = True
        LOG_LEVEL = 'INFO'
        DATA_CACHE_DIR = 'data/cache'
        BINANCE_TESTNET = True
        BINANCE_API_KEY = 'test_key'
        BINANCE_API_SECRET = 'test_secret'
    
    return MockConfig()
