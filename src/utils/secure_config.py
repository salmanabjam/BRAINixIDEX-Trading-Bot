"""
BiX TradeBOT - Secure Configuration Module
===========================================
Centralized configuration management with encrypted secrets support.

Author: SALMAN ThinkTank AI Core
Version: 2.0.0 - Security Enhanced
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()


class Config:
    """
    Main configuration class for BiX TradeBOT.
    
    Supports both:
    - Environment variables (.env) - for development
    - Encrypted secrets - for production
    """
    
    # ============= API Configuration =============
    # These will be loaded from encrypted secrets if available,
    # otherwise from environment variables
    _BINANCE_API_KEY: Optional[str] = None
    _BINANCE_API_SECRET: Optional[str] = None
    
    BINANCE_TESTNET = os.getenv('BINANCE_TESTNET', 'True').lower() == 'true'
    
    # ============= Trading Symbol =============
    TRADING_SYMBOL = 'BTCUSDT'  # Used by WebSocket
    SYMBOL = 'BTCUSDT'  # Used by trading logic
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
    BACKTEST_START_DATE = '2025-09-10'  # Recent 40 days
    BACKTEST_END_DATE = '2025-10-20'
    BACKTEST_COMMISSION = 0.001  # 0.1% per trade
    
    # ============= Data Management =============
    DATA_CACHE_DIR = 'data/cache'
    LOG_DIR = 'logs'
    RESULTS_DIR = 'results'
    
    # ============= Security =============
    USE_ENCRYPTED_SECRETS = os.getenv(
        'USE_ENCRYPTED_SECRETS',
        'False'
    ).lower() == 'true'
    SECRETS_CONFIG_DIR = os.getenv('SECRETS_CONFIG_DIR', 'config')
    
    # ============= System Settings =============
    DEBUG_MODE = True
    LOG_LEVEL = 'INFO'  # Options: DEBUG, INFO, WARNING, ERROR
    SAVE_TRADES = True
    
    @classmethod
    def load_credentials(
        cls,
        use_encrypted: bool = None,
        password: Optional[str] = None
    ) -> None:
        """
        Load API credentials from encrypted secrets or environment.
        
        Args:
            use_encrypted: Force encrypted secrets (overrides config)
            password: Master password for encrypted secrets
        """
        if use_encrypted is None:
            use_encrypted = cls.USE_ENCRYPTED_SECRETS
        
        if use_encrypted:
            # Load from encrypted secrets
            from utils.security import SecretManager
            
            try:
                manager = SecretManager(cls.SECRETS_CONFIG_DIR)
                manager.load(password)
                creds = manager.get_binance_credentials()
                
                cls._BINANCE_API_KEY = creds['api_key']
                cls._BINANCE_API_SECRET = creds['api_secret']
                
                print("✅ Loaded credentials from encrypted secrets")
            except Exception as e:
                print(f"❌ Failed to load encrypted secrets: {e}")
                print("⚠️  Falling back to environment variables")
                cls._load_from_env()
        else:
            # Load from environment variables
            cls._load_from_env()
    
    @classmethod
    def _load_from_env(cls) -> None:
        """Load credentials from environment variables."""
        cls._BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
        cls._BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
        
        if cls._BINANCE_API_KEY and cls._BINANCE_API_SECRET:
            print("✅ Loaded credentials from environment variables")
        else:
            print("⚠️  API credentials not found in environment")
    
    @classmethod
    @property
    def BINANCE_API_KEY(cls) -> str:
        """Get Binance API key."""
        if cls._BINANCE_API_KEY is None:
            cls.load_credentials()
        return cls._BINANCE_API_KEY or ''
    
    @classmethod
    @property
    def BINANCE_API_SECRET(cls) -> str:
        """Get Binance API secret."""
        if cls._BINANCE_API_SECRET is None:
            cls.load_credentials()
        return cls._BINANCE_API_SECRET or ''
    
    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration parameters."""
        errors = []
        
        # Ensure credentials are loaded
        api_key = cls.BINANCE_API_KEY
        api_secret = cls.BINANCE_API_SECRET
        
        if not api_key or not api_secret:
            errors.append(
                "API credentials not configured. "
                "Either set BINANCE_API_KEY and BINANCE_API_SECRET "
                "in .env file, or use encrypted secrets."
            )
        
        if cls.RISK_PER_TRADE <= 0 or cls.RISK_PER_TRADE > 0.05:
            errors.append(
                f"RISK_PER_TRADE ({cls.RISK_PER_TRADE}) "
                f"should be between 0 and 0.05 (5%)"
            )
        
        if cls.EMA_FAST >= cls.EMA_SLOW:
            errors.append("EMA_FAST must be less than EMA_SLOW")
        
        if errors:
            raise ValueError(
                "Configuration validation failed:\n" +
                "\n".join(f"- {e}" for e in errors)
            )
        
        return True
    
    @classmethod
    def get_safe_summary(cls) -> dict:
        """
        Get configuration summary with sensitive data masked.
        
        Returns:
            Dictionary with configuration (API keys masked)
        """
        api_key = cls.BINANCE_API_KEY
        api_secret = cls.BINANCE_API_SECRET
        
        return {
            'api_key': f"{api_key[:8]}...{api_key[-4:]}" if api_key else "Not set",
            'api_secret': "***" if api_secret else "Not set",
            'testnet': cls.BINANCE_TESTNET,
            'symbol': cls.SYMBOL,
            'timeframe': cls.TIMEFRAME,
            'risk_per_trade': f"{cls.RISK_PER_TRADE*100}%",
            'ml_enabled': cls.ML_ENABLED,
            'use_encrypted_secrets': cls.USE_ENCRYPTED_SECRETS
        }


# Auto-load credentials on import (fallback to env if encrypted fails)
try:
    Config.load_credentials()
except Exception:
    pass  # Will retry when accessed


if __name__ == "__main__":
    # Test configuration
    print("🔧 BiX TradeBOT - Configuration Test")
    print("=" * 50)
    
    # Show safe summary
    print("\n📋 Configuration Summary:")
    summary = Config.get_safe_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Validate
    print("\n🔍 Validating configuration...")
    try:
        Config.validate()
        print("✅ Configuration validated successfully")
    except ValueError as e:
        print(f"❌ Configuration error:\n{e}")
