"""
BiX TradeBOT - Configuration Module
====================================
Centralized configuration management for trading bot parameters.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Main configuration class for BiX TradeBOT"""
    
    # ============= API Configuration =============
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
    BINANCE_TESTNET = os.getenv('BINANCE_TESTNET', 'True').lower() == 'true'
    
    # ============= Trading Parameters =============
    SYMBOL = 'BTCUSDT'
    TIMEFRAME = '1h'  # Options: 1m, 5m, 15m, 30m, 1h, 4h, 1d
    INITIAL_CAPITAL = 10000  # USD
    
    # Multi-Timeframe Analysis
    MULTI_TIMEFRAME_ENABLED = True
    TIMEFRAME_HIERARCHY = {
        '1m': ['5m', '15m'],    # 1m confirmed by 5m & 15m
        '5m': ['15m', '1h'],    # 5m confirmed by 15m & 1h
        '15m': ['1h', '4h'],    # 15m confirmed by 1h & 4h
        '30m': ['1h', '4h'],    # 30m confirmed by 1h & 4h
        '1h': ['4h', '1d'],     # 1h confirmed by 4h & 1d
        '4h': ['1d'],           # 4h confirmed by 1d
        '1d': []                # 1d (highest, no confirmation needed)
    }
    CONFIRMATION_THRESHOLD = 0.6  # 60% of higher TFs must agree
    
    # ============= Risk Management =============
    RISK_PER_TRADE = 0.015  # 1.5% max risk per trade
    MAX_POSITION_SIZE = 0.20  # 20% of total capital max per position
    ATR_STOP_MULTIPLIER = 2.0  # Stop loss = ATR * multiplier
    RISK_REWARD_RATIO = 2.0  # Target profit = risk * ratio
    
    # ============= Strategy Parameters =============
    # Trend Following
    EMA_FAST = 50
    EMA_SLOW = 200
    
    # Breakout Detection
    DONCHIAN_PERIOD = 20
    
    # Pullback/Reversal
    RSI_PERIOD = 14
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    
    # Volatility & Trend Strength
    ATR_PERIOD = 14
    ADX_PERIOD = 14
    ADX_THRESHOLD = 25  # Strong trend above this value
    
    # ============= Machine Learning =============
    ML_ENABLED = True
    ML_MODEL = 'lightgbm'  # Options: lightgbm, xgboost, randomforest
    ML_LOOKBACK = 100  # Number of bars for feature engineering
    ML_TRAIN_RATIO = 0.8
    ML_FEATURE_COUNT = 15
    
    # Model paths
    MODEL_SAVE_PATH = 'models/trained_model.pkl'
    SCALER_SAVE_PATH = 'models/scaler.pkl'
    
    # ============= Backtesting =============
    BACKTEST_START_DATE = '2025-09-10'  # Recent 40 days for latest data
    BACKTEST_END_DATE = '2025-10-20'
    BACKTEST_COMMISSION = 0.001  # 0.1% per trade
    
    # ============= Data Management =============
    DATA_CACHE_DIR = 'data/cache'
    LOG_DIR = 'logs'
    RESULTS_DIR = 'results'
    
    # ============= System Settings =============
    DEBUG_MODE = True
    LOG_LEVEL = 'INFO'  # Options: DEBUG, INFO, WARNING, ERROR
    SAVE_TRADES = True
    
    @classmethod
    def validate(cls):
        """Validate critical configuration parameters"""
        errors = []
        
        if not cls.BINANCE_API_KEY or not cls.BINANCE_API_SECRET:
            errors.append("API credentials not configured. Set BINANCE_API_KEY and BINANCE_API_SECRET in .env file")
        
        if cls.RISK_PER_TRADE <= 0 or cls.RISK_PER_TRADE > 0.05:
            errors.append(f"RISK_PER_TRADE ({cls.RISK_PER_TRADE}) should be between 0 and 0.05 (5%)")
        
        if cls.EMA_FAST >= cls.EMA_SLOW:
            errors.append("EMA_FAST must be less than EMA_SLOW")
        
        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"- {e}" for e in errors))
        
        return True


if __name__ == "__main__":
    # Test configuration
    try:
        Config.validate()
        print("✅ Configuration validated successfully")
    except ValueError as e:
        print(f"❌ Configuration error:\n{e}")
