"""
BiX TradeBOT - Data Handler Module
===================================
Handles market data fetching from Binance API with caching and error handling.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from binance.client import Client
from binance.exceptions import BinanceAPIException
import ccxt
from config import Config
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataHandler:
    """
    Manages market data retrieval, caching, and preprocessing.
    Supports both Binance official API and CCXT for multi-exchange compatibility.
    """
    
    def __init__(self, use_ccxt=False):
        """
        Initialize data handler with API clients.
        
        Args:
            use_ccxt (bool): Use CCXT library instead of python-binance
        """
        self.use_ccxt = use_ccxt
        self.cache_dir = Path(Config.DATA_CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize API client
        try:
            if use_ccxt:
                self.client = self._init_ccxt_client()
            else:
                self.client = self._init_binance_client()
            logger.info(f"✅ API client initialized ({'CCXT' if use_ccxt else 'Binance'})")
        except Exception as e:
            logger.error(f"❌ Failed to initialize API client: {e}")
            raise
    
    def _init_binance_client(self):
        """Initialize Binance official client"""
        if Config.BINANCE_TESTNET:
            client = Client(Config.BINANCE_API_KEY, Config.BINANCE_API_SECRET, testnet=True)
            logger.info("🔧 Using Binance TESTNET")
        else:
            client = Client(Config.BINANCE_API_KEY, Config.BINANCE_API_SECRET)
            logger.warning("⚠️  Using Binance MAINNET - Real funds at risk!")
        return client
    
    def _init_ccxt_client(self):
        """Initialize CCXT client for multi-exchange support"""
        exchange_class = getattr(ccxt, 'binance')
        client = exchange_class({
            'apiKey': Config.BINANCE_API_KEY,
            'secret': Config.BINANCE_API_SECRET,
            'enableRateLimit': True,
            'options': {'defaultType': 'future' if Config.BINANCE_TESTNET else 'spot'}
        })
        
        if Config.BINANCE_TESTNET:
            client.set_sandbox_mode(True)
        
        return client
    
    def fetch_ohlcv(self, symbol=None, timeframe=None, start_date=None, end_date=None, 
                     use_cache=True, limit=1000):
        """
        Fetch OHLCV (Open, High, Low, Close, Volume) data.
        
        Args:
            symbol (str): Trading pair (e.g., 'BTCUSDT')
            timeframe (str): Candle interval (e.g., '1h', '4h', '1d')
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str): End date in 'YYYY-MM-DD' format
            use_cache (bool): Load from cache if available
            limit (int): Maximum number of candles to fetch
            
        Returns:
            pd.DataFrame: OHLCV data with columns [timestamp, open, high, low, close, volume]
        """
        symbol = symbol or Config.SYMBOL
        timeframe = timeframe or Config.TIMEFRAME
        start_date = start_date or Config.BACKTEST_START_DATE
        end_date = end_date or Config.BACKTEST_END_DATE
        
        # Check cache
        cache_file = self._get_cache_filename(symbol, timeframe, start_date, end_date)
        if use_cache and cache_file.exists():
            logger.info(f"📦 Loading data from cache: {cache_file.name}")
            return pd.read_csv(cache_file, index_col=0, parse_dates=True)
        
        logger.info(f"🔍 Fetching {symbol} {timeframe} data from {start_date} to {end_date}")
        
        try:
            if self.use_ccxt:
                df = self._fetch_ccxt(symbol, timeframe, start_date, end_date, limit)
            else:
                df = self._fetch_binance(symbol, timeframe, start_date, end_date, limit)
            
            # Save to cache
            if use_cache:
                df.to_csv(cache_file)
                logger.info(f"💾 Data cached to {cache_file.name}")
            
            logger.info(f"✅ Fetched {len(df)} candles")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error fetching data: {e}")
            raise
    
    def _fetch_binance(self, symbol, timeframe, start_date, end_date, limit):
        """Fetch data using Binance official API"""
        interval_map = {
            '1m': Client.KLINE_INTERVAL_1MINUTE,
            '5m': Client.KLINE_INTERVAL_5MINUTE,
            '15m': Client.KLINE_INTERVAL_15MINUTE,
            '1h': Client.KLINE_INTERVAL_1HOUR,
            '4h': Client.KLINE_INTERVAL_4HOUR,
            '1d': Client.KLINE_INTERVAL_1DAY
        }
        
        klines = self.client.get_historical_klines(
            symbol,
            interval_map[timeframe],
            start_date,
            end_date,
            limit=limit
        )
        
        # Convert to DataFrame
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        # Clean and format
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        
        return df
    
    def _fetch_ccxt(self, symbol, timeframe, start_date, end_date, limit):
        """Fetch data using CCXT"""
        since = int(pd.Timestamp(start_date).timestamp() * 1000)
        until = int(pd.Timestamp(end_date).timestamp() * 1000)
        
        all_ohlcv = []
        current = since
        
        while current < until:
            ohlcv = self.client.fetch_ohlcv(symbol, timeframe, since=current, limit=limit)
            if not ohlcv:
                break
            all_ohlcv.extend(ohlcv)
            current = ohlcv[-1][0] + 1
        
        # Convert to DataFrame
        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        return df
    
    def fetch_latest_price(self, symbol=None):
        """
        Fetch latest price for a symbol.
        
        Args:
            symbol (str): Trading pair
            
        Returns:
            float: Latest price
        """
        symbol = symbol or Config.SYMBOL
        
        try:
            if self.use_ccxt:
                ticker = self.client.fetch_ticker(symbol)
                return ticker['last']
            else:
                ticker = self.client.get_symbol_ticker(symbol=symbol)
                return float(ticker['price'])
        except Exception as e:
            logger.error(f"❌ Error fetching latest price: {e}")
            raise
    
    def get_account_balance(self):
        """
        Fetch account balance.
        
        Returns:
            dict: Balance information
        """
        try:
            if self.use_ccxt:
                balance = self.client.fetch_balance()
                return balance
            else:
                account = self.client.get_account()
                balances = {item['asset']: float(item['free']) for item in account['balances'] if float(item['free']) > 0}
                return balances
        except Exception as e:
            logger.error(f"❌ Error fetching balance: {e}")
            return {}
    
    def _get_cache_filename(self, symbol, timeframe, start_date, end_date):
        """Generate cache filename"""
        filename = f"{symbol}_{timeframe}_{start_date}_{end_date}.csv"
        return self.cache_dir / filename
    
    def validate_data(self, df):
        """
        Validate OHLCV data integrity.
        
        Args:
            df (pd.DataFrame): OHLCV data
            
        Returns:
            bool: True if valid
        """
        checks = {
            'not_empty': len(df) > 0,
            'no_nulls': not df.isnull().any().any(),
            'positive_prices': (df[['open', 'high', 'low', 'close']] > 0).all().all(),
            'high_low_valid': (df['high'] >= df['low']).all(),
            'ohlc_valid': ((df['high'] >= df['open']) & (df['high'] >= df['close']) &
                           (df['low'] <= df['open']) & (df['low'] <= df['close'])).all()
        }
        
        for check_name, passed in checks.items():
            if not passed:
                logger.error(f"❌ Data validation failed: {check_name}")
                return False
        
        logger.info("✅ Data validation passed")
        return True


if __name__ == "__main__":
    # Test data handler
    handler = DataHandler(use_ccxt=False)
    
    # Fetch sample data
    df = handler.fetch_ohlcv(limit=100)
    print("\n📊 Sample Data:")
    print(df.head())
    print(f"\n📈 Shape: {df.shape}")
    
    # Validate
    handler.validate_data(df)
    
    # Latest price
    price = handler.fetch_latest_price()
    print(f"\n💰 Latest {Config.SYMBOL} price: ${price:,.2f}")
