"""
BiX TradeBOT - Data Handler Module
===================================
Handles market data fetching from Binance API with caching and error handling.

Author: SALMAN ThinkTank AI Core
Version: 1.1.0 - Added WebSocket support
"""

import os
import json
import pandas as pd
import numpy as np
import asyncio
import threading
from datetime import datetime, timedelta
from binance.client import Client
from binance.exceptions import BinanceAPIException
import ccxt
from typing import Optional, Callable, Dict, Any
from utils.config import Config
from utils.advanced_logger import get_logger
from utils.retry import retry
from utils.exceptions import DataFetchException, ValidationException
from utils.rate_limiter import get_rate_limiter, rate_limited
from pathlib import Path
from data.database import get_database

# Setup logger with context
logger = get_logger(__name__, component='DataHandler')
db = get_database()


class DataHandler:
    """
    Manages market data retrieval, caching, and preprocessing.
    Supports both Binance official API and CCXT for multi-exchange compatibility.
    """
    
    def __init__(self, use_ccxt=False, enable_websocket=False):
        """
        Initialize data handler with API clients.
        
        Args:
            use_ccxt (bool): Use CCXT library instead of python-binance
            enable_websocket (bool): Enable WebSocket for real-time updates
        """
        self.use_ccxt = use_ccxt
        self.cache_dir = Path(Config.DATA_CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # WebSocket support
        self.enable_websocket = enable_websocket
        self.ws_client = None
        self.ws_thread = None
        self.ws_loop = None
        
        # Initialize API client
        try:
            if use_ccxt:
                self.client = self._init_ccxt_client()
            else:
                self.client = self._init_binance_client()
            logger.info(
                f"✅ API client initialized "
                f"({'CCXT' if use_ccxt else 'Binance'})"
            )
        except Exception as e:
            logger.error(f"❌ Failed to initialize API client: {e}")
            raise
        
        # Start WebSocket if enabled
        if enable_websocket:
            self.start_websocket()
    
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
    
    @retry(max_attempts=3, delay=2.0)
    def fetch_ohlcv(
        self,
        symbol=None,
        timeframe=None,
        start_date=None,
        end_date=None,
        use_cache=True,
        limit=1000
    ):
        """
        Fetch OHLCV (Open, High, Low, Close, Volume) data.
        Rate-limited automatically.
        
        Args:
            symbol (str): Trading pair (e.g., 'BTCUSDT')
            timeframe (str): Candle interval (e.g., '1h', '4h', '1d')
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str): End date in 'YYYY-MM-DD' format
            use_cache (bool): Load from cache if available
            limit (int): Maximum number of candles to fetch
            
        Returns:
            pd.DataFrame: OHLCV data with columns
                [timestamp, open, high, low, close, volume]
        """
        symbol = symbol or Config.SYMBOL
        timeframe = timeframe or Config.TIMEFRAME
        start_date = start_date or Config.BACKTEST_START_DATE
        end_date = end_date or Config.BACKTEST_END_DATE
        
        # Check cache
        cache_file = self._get_cache_filename(
            symbol, timeframe, start_date, end_date
        )
        if use_cache and cache_file.exists():
            logger.info(
                f"Loading data from cache",
                symbol=symbol,
                timeframe=timeframe
            )
            return pd.read_csv(cache_file, index_col=0, parse_dates=True)
        
        # Apply rate limiting
        rate_limiter = get_rate_limiter()
        rate_limiter.consume_weight('klines', wait=True)
        
        logger.info(
            f"Fetching market data",
            symbol=symbol,
            timeframe=timeframe,
            action='fetch_data'
        )
        
        try:
            if self.use_ccxt:
                data = self._fetch_ccxt(
                    symbol, timeframe, start_date, end_date, limit
                )
            else:
                data = self._fetch_binance(
                    symbol, timeframe, start_date, end_date, limit
                )
            
            # Save to cache
            if use_cache:
                data.to_csv(cache_file)
                logger.info(f"Data cached successfully", symbol=symbol)

                # Register cache in database
                try:
                    file_size = cache_file.stat().st_size
                    db.register_cache_file(
                        file_path=str(cache_file),
                        symbol=symbol,
                        timeframe=timeframe,
                        start_date=start_date,
                        end_date=end_date,
                        candle_count=len(data),
                        file_size=file_size
                    )
                    logger.debug(
                        f"Cache metadata registered: "
                        f"{len(data)} candles, {file_size} bytes"
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to register cache metadata: {e}"
                    )
            
            logger.info(
                f"Fetched candles",
                symbol=symbol,
                candle_count=len(data)
            )
            return data
            
        except BinanceAPIException as e:
            logger.error(
                f"Binance API error",
                symbol=symbol,
                error_code=e.code
            )
            raise DataFetchException(f"Failed to fetch {symbol} data: {e}")
        except Exception as e:
            logger.error(f"Data fetch failed", symbol=symbol)
            raise DataFetchException(f"Error fetching data: {e}")
    
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
    
    @retry(max_attempts=3, delay=2.0)
    def fetch_latest_price(self, symbol=None):
        """
        Fetch latest price for a symbol with rate limiting.
        
        Args:
            symbol (str): Trading pair
            
        Returns:
            float: Latest price
        """
        symbol = symbol or Config.SYMBOL
        
        # Apply rate limiting
        rate_limiter = get_rate_limiter()
        rate_limiter.consume_weight('ticker/price', wait=True)
        
        try:
            if self.use_ccxt:
                ticker = self.client.fetch_ticker(symbol)
                price = ticker['last']
            else:
                ticker = self.client.get_symbol_ticker(symbol=symbol)
                price = float(ticker['price'])
            
            logger.info("Latest price fetched", symbol=symbol, price=price)
            return price
            
        except BinanceAPIException as e:
            logger.error(
                "Price fetch failed",
                symbol=symbol,
                error_code=e.code
            )
            raise DataFetchException(f"Failed to fetch {symbol} price: {e}")
        except Exception as e:
            logger.error("Price fetch error", symbol=symbol)
            raise DataFetchException(f"Error fetching price: {e}")
    
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
    
    def validate_data(self, data):
        """
        Validate OHLCV data integrity.
        
        Args:
            data (pd.DataFrame): OHLCV data
            
        Returns:
            bool: True if valid
            
        Raises:
            ValidationException: If validation fails
        """
        # Check not empty first
        if len(data) == 0:
            logger.error("Validation failed", check='not_empty')
            raise ValidationException("Data validation failed: empty dataset")
        
        # Check required columns exist
        required_cols = ['open', 'high', 'low', 'close']
        missing_cols = [c for c in required_cols if c not in data.columns]
        if missing_cols:
            logger.error("Missing columns", columns=missing_cols)
            raise ValidationException(
                f"Missing columns: {missing_cols}"
            )
        
        # Perform checks
        checks = {
            'no_nulls': not data.isnull().any().any(),
            'positive_prices': (
                data[['open', 'high', 'low', 'close']] > 0
            ).all().all(),
            'high_low_valid': (data['high'] >= data['low']).all(),
            'ohlc_valid': (
                (data['high'] >= data['open']) &
                (data['high'] >= data['close']) &
                (data['low'] <= data['open']) &
                (data['low'] <= data['close'])
            ).all()
        }
        
        for check_name, passed in checks.items():
            if not passed:
                logger.error("Validation failed", check=check_name)
                raise ValidationException(
                    f"Data validation failed: {check_name}"
                )
        
        logger.info("Data validation passed")
        return True
    
    def start_websocket(
        self,
        symbols: Optional[list] = None,
        on_update: Optional[Callable] = None
    ):
        """
        Start WebSocket client for real-time price updates.
        
        Args:
            symbols: List of symbols to track (default: Config.TRADING_SYMBOL)
            on_update: Callback function for price updates
        """
        if self.ws_client:
            logger.warning("WebSocket already running")
            return
        
        try:
            from data.binance_websocket import BinanceWebSocketClient
            
            symbols = symbols or [Config.TRADING_SYMBOL]
            
            logger.info(f"🚀 Starting WebSocket for {len(symbols)} symbols")
            
            # Create WebSocket client
            self.ws_client = BinanceWebSocketClient(
                symbols=symbols,
                on_message=on_update,
                testnet=Config.BINANCE_TESTNET
            )
            
            # Run in separate thread
            def run_websocket():
                self.ws_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.ws_loop)
                try:
                    self.ws_loop.run_until_complete(
                        self.ws_client.start('ticker')
                    )
                except Exception as e:
                    logger.error(f"❌ WebSocket error: {e}")
            
            self.ws_thread = threading.Thread(
                target=run_websocket,
                daemon=True
            )
            self.ws_thread.start()
            
            logger.info("✅ WebSocket started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start WebSocket: {e}")
            raise
    
    def stop_websocket(self):
        """Stop WebSocket client."""
        if not self.ws_client:
            logger.warning("WebSocket not running")
            return
        
        try:
            logger.info("🛑 Stopping WebSocket...")
            
            # Stop WebSocket
            if self.ws_loop and self.ws_loop.is_running():
                self.ws_loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(self.ws_client.stop())
                )
            
            # Wait for thread
            if self.ws_thread and self.ws_thread.is_alive():
                self.ws_thread.join(timeout=5)
            
            self.ws_client = None
            self.ws_thread = None
            self.ws_loop = None
            
            logger.info("✅ WebSocket stopped")
            
        except Exception as e:
            logger.error(f"⚠️  Error stopping WebSocket: {e}")
    
    def get_websocket_price(self, symbol: str) -> Optional[float]:
        """
        Get real-time price from WebSocket.
        
        Args:
            symbol: Trading pair
            
        Returns:
            Latest price or None if WebSocket not active
        """
        if not self.ws_client:
            return None
        
        return self.ws_client.get_latest_price(symbol)
    
    def get_websocket_stats(self) -> Optional[Dict[str, Any]]:
        """Get WebSocket connection statistics."""
        if not self.ws_client:
            return None
        
        return self.ws_client.get_stats()


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
