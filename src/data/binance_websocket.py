"""
BiX TradeBOT - Binance WebSocket Client
========================================
Real-time market data streaming from Binance WebSocket API.

Binance WebSocket Streams:
- Individual symbol ticker: {symbol}@ticker
- All market tickers: !ticker@arr
- Kline/Candlestick: {symbol}@kline_{interval}
- Aggregate trades: {symbol}@aggTrade
- Order book depth: {symbol}@depth

Features:
- Auto-reconnection with exponential backoff
- Thread-safe data updates
- Multiple stream subscriptions
- Rate limiting compliance
- Error recovery and logging

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import asyncio
import json
import threading
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import websockets
from collections import deque
from websockets.exceptions import (
    ConnectionClosed,
    ConnectionClosedError,
    ConnectionClosedOK
)

from utils.advanced_logger import get_logger
from utils.exceptions import DataFetchException
from utils.config import Config
from data.database import get_database

logger = get_logger(__name__, component='BinanceWebSocket')
db = get_database()


class BinanceWebSocketClient:
    """
    Binance WebSocket client for real-time market data streaming.
    
    Supports multiple stream types:
    - Ticker: 24hr price statistics
    - Kline: Candlestick data
    - Trade: Individual trades
    - Depth: Order book updates
    """
    
    # WebSocket endpoints
    WS_BASE_URL = "wss://stream.binance.com:9443/ws"
    WS_TESTNET_URL = "wss://testnet.binance.vision/ws"
    
    def __init__(
        self,
        symbols: Optional[List[str]] = None,
        on_message: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        testnet: bool = False
    ):
        """
        Initialize WebSocket client.
        
        Args:
            symbols: List of trading pairs (e.g., ['BTCUSDT', 'ETHUSDT'])
            on_message: Callback for incoming messages
            on_error: Callback for errors
            testnet: Use testnet endpoint
        """
        self.symbols = symbols or [Config.TRADING_SYMBOL]
        self.on_message = on_message
        self.on_error = on_error
        self.testnet = testnet
        
        # Connection state
        self.ws = None
        self.is_running = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        
        # Data storage
        self.latest_data: Dict[str, Any] = {}
        self.message_queue = deque(maxlen=1000)
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'messages_received': 0,
            'errors': 0,
            'reconnections': 0,
            'last_message_time': None,
            'uptime_start': None
        }
        
        logger.info(
            f"🌐 WebSocket client initialized for "
            f"{len(self.symbols)} symbols: {', '.join(self.symbols[:3])}..."
        )
    
    def get_stream_url(self, stream_type: str = 'ticker') -> str:
        """
        Build WebSocket stream URL.
        
        Args:
            stream_type: Type of stream (ticker, kline, trade, depth)
            
        Returns:
            WebSocket URL
        """
        base_url = self.WS_TESTNET_URL if self.testnet else self.WS_BASE_URL
        
        # Multiple symbols stream
        if len(self.symbols) > 1:
            streams = [
                f"{symbol.lower()}@{stream_type}"
                for symbol in self.symbols
            ]
            return f"{base_url}/stream?streams={'/'.join(streams)}"
        
        # Single symbol stream
        symbol = self.symbols[0].lower()
        return f"{base_url}/{symbol}@{stream_type}"
    
    async def _connect(self, stream_type: str = 'ticker'):
        """
        Establish WebSocket connection.
        
        Args:
            stream_type: Stream type to subscribe
        """
        url = self.get_stream_url(stream_type)
        
        try:
            logger.info(f"🔌 Connecting to {url}")
            self.ws = await websockets.connect(
                url,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=10
            )
            
            self.stats['uptime_start'] = datetime.now()
            logger.info("✅ WebSocket connected successfully")
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            raise DataFetchException(f"WebSocket connection failed: {e}")
    
    async def _handle_message(self, message: str):
        """
        Process incoming WebSocket message.
        
        Args:
            message: Raw WebSocket message
        """
        try:
            data = json.loads(message)
            
            # Update statistics
            with self.lock:
                self.stats['messages_received'] += 1
                self.stats['last_message_time'] = datetime.now()
            
            # Multi-stream format
            if 'stream' in data and 'data' in data:
                stream_name = data['stream']
                payload = data['data']
                symbol = stream_name.split('@')[0].upper()
                
                with self.lock:
                    self.latest_data[symbol] = payload
                    self.message_queue.append({
                        'symbol': symbol,
                        'data': payload,
                        'timestamp': datetime.now()
                    })
            
            # Single stream format
            elif 'e' in data:  # Event type exists
                event_type = data['e']
                symbol = data.get('s', 'UNKNOWN')
                
                with self.lock:
                    self.latest_data[symbol] = data
                    self.message_queue.append({
                        'symbol': symbol,
                        'data': data,
                        'timestamp': datetime.now()
                    })
            
            # Custom callback
            if self.on_message:
                try:
                    await self.on_message(data)
                except Exception as e:
                    logger.error(f"⚠️  Message callback error: {e}")
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON: {e}")
            with self.lock:
                self.stats['errors'] += 1
        
        except Exception as e:
            logger.error(f"❌ Message handling error: {e}")
            with self.lock:
                self.stats['errors'] += 1
            
            if self.on_error:
                await self.on_error(e)
    
    async def _reconnect(self, stream_type: str = 'ticker'):
        """
        Reconnect with exponential backoff.
        
        Args:
            stream_type: Stream type to reconnect
        """
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(
                f"❌ Max reconnection attempts ({self.max_reconnect_attempts}) "
                f"reached. Stopping."
            )
            self.is_running = False
            return
        
        # Exponential backoff: 1, 2, 4, 8, 16, 32 seconds (max 60)
        delay = min(2 ** self.reconnect_attempts, 60)
        
        logger.warning(
            f"🔄 Reconnecting in {delay}s (attempt "
            f"{self.reconnect_attempts + 1}/{self.max_reconnect_attempts})"
        )
        
        await asyncio.sleep(delay)
        
        try:
            await self._connect(stream_type)
            self.reconnect_attempts = 0
            with self.lock:
                self.stats['reconnections'] += 1
            logger.info("✅ Reconnection successful")
            
        except Exception as e:
            logger.error(f"❌ Reconnection failed: {e}")
            self.reconnect_attempts += 1
            await self._reconnect(stream_type)
    
    async def start(self, stream_type: str = 'ticker'):
        """
        Start WebSocket streaming.
        
        Args:
            stream_type: Type of stream (ticker, kline_1m, trade, depth)
        """
        self.is_running = True
        self.reconnect_attempts = 0
        
        logger.info(f"🚀 Starting WebSocket stream: {stream_type}")
        
        try:
            await self._connect(stream_type)
            
            while self.is_running:
                try:
                    # Receive messages
                    async for message in self.ws:
                        if not self.is_running:
                            break
                        
                        await self._handle_message(message)
                
                except ConnectionClosedOK:
                    logger.info("🔌 Connection closed gracefully")
                    if self.is_running:
                        await self._reconnect(stream_type)
                
                except ConnectionClosedError as e:
                    logger.error(f"❌ Connection closed with error: {e}")
                    if self.is_running:
                        await self._reconnect(stream_type)
                
                except ConnectionClosed as e:
                    logger.warning(f"⚠️  Connection closed: {e}")
                    if self.is_running:
                        await self._reconnect(stream_type)
        
        except asyncio.CancelledError:
            logger.info("🛑 WebSocket task cancelled")
        
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            raise
        
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop WebSocket streaming and close connection."""
        logger.info("🛑 Stopping WebSocket client...")
        self.is_running = False
        
        if self.ws and not self.ws.closed:
            try:
                await self.ws.close()
                logger.info("✅ WebSocket closed successfully")
            except Exception as e:
                logger.error(f"⚠️  Error closing WebSocket: {e}")
        
        # Log final statistics
        uptime = None
        if self.stats['uptime_start']:
            uptime = (
                datetime.now() - self.stats['uptime_start']
            ).total_seconds()
        
        logger.info(
            f"📊 Final stats: {self.stats['messages_received']} messages, "
            f"{self.stats['reconnections']} reconnections, "
            f"{self.stats['errors']} errors, "
            f"uptime: {uptime:.1f}s" if uptime else "uptime: N/A"
        )
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get latest price for a symbol.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            
        Returns:
            Latest price or None
        """
        with self.lock:
            data = self.latest_data.get(symbol)
            if not data:
                return None
            
            # Ticker stream format
            if 'c' in data:  # Close price
                return float(data['c'])
            
            # Trade stream format
            if 'p' in data:  # Price
                return float(data['p'])
            
            return None
    
    def get_latest_data(self, symbol: str) -> Optional[Dict]:
        """
        Get latest full data for a symbol.
        
        Args:
            symbol: Trading pair
            
        Returns:
            Latest data dictionary or None
        """
        with self.lock:
            return self.latest_data.get(symbol)
    
    def get_all_prices(self) -> Dict[str, float]:
        """
        Get latest prices for all subscribed symbols.
        
        Returns:
            Dictionary of {symbol: price}
        """
        prices = {}
        with self.lock:
            for symbol, data in self.latest_data.items():
                if 'c' in data:
                    prices[symbol] = float(data['c'])
                elif 'p' in data:
                    prices[symbol] = float(data['p'])
        
        return prices
    
    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket statistics and log to database."""
        with self.lock:
            stats = self.stats.copy()
        
        # Calculate uptime
        if stats.get('uptime_start'):
            stats['uptime'] = (
                datetime.now() - stats['uptime_start']
            ).total_seconds()
        else:
            stats['uptime'] = 0
        
        # Calculate messages per second
        if stats.get('uptime', 0) > 0:
            stats['messages_per_second'] = (
                stats['messages_received'] / stats['uptime']
            )
        else:
            stats['messages_per_second'] = 0

        # Log to database
        try:
            db.log_websocket_stats(
                messages_received=stats['messages_received'],
                errors=stats['errors'],
                reconnections=stats['reconnections'],
                uptime=stats['uptime'],
                symbols=self.symbols
            )
            logger.debug("WebSocket stats logged to database")
        except Exception as e:
            logger.warning(f"Failed to log WebSocket stats: {e}")
        
        return stats


class BinanceKlineWebSocket(BinanceWebSocketClient):
    """
    Specialized WebSocket client for Kline/Candlestick data.
    """
    
    def __init__(
        self,
        symbols: Optional[List[str]] = None,
        interval: str = '1m',
        on_kline: Optional[Callable] = None,
        testnet: bool = False
    ):
        """
        Initialize Kline WebSocket.
        
        Args:
            symbols: Trading pairs
            interval: Kline interval (1m, 5m, 15m, 1h, 4h, 1d)
            on_kline: Callback for kline updates
            testnet: Use testnet
        """
        self.interval = interval
        self.on_kline = on_kline
        
        super().__init__(
            symbols=symbols,
            on_message=self._handle_kline,
            testnet=testnet
        )
        
        logger.info(f"📊 Kline WebSocket initialized: interval={interval}")
    
    async def _handle_kline(self, data: Dict):
        """Handle kline-specific data."""
        if 'k' in data:  # Kline data
            kline = data['k']
            symbol = kline['s']
            
            # Extract OHLCV
            ohlcv = {
                'symbol': symbol,
                'timestamp': datetime.fromtimestamp(kline['t'] / 1000),
                'open': float(kline['o']),
                'high': float(kline['h']),
                'low': float(kline['l']),
                'close': float(kline['c']),
                'volume': float(kline['v']),
                'is_closed': kline['x']  # Is kline closed?
            }
            
            # Custom callback
            if self.on_kline:
                try:
                    await self.on_kline(ohlcv)
                except Exception as e:
                    logger.error(f"⚠️  Kline callback error: {e}")
    
    def get_stream_url(self, stream_type: str = None) -> str:
        """Override to use kline stream."""
        return super().get_stream_url(f'kline_{self.interval}')
    
    async def start(self):
        """Start kline streaming."""
        await super().start(f'kline_{self.interval}')


# Example usage and testing
async def main():
    """Test WebSocket client."""
    
    # Callback for price updates
    async def on_price_update(data):
        if 'c' in data:  # Ticker data
            symbol = data.get('s', 'UNKNOWN')
            price = float(data['c'])
            change_24h = float(data['P'])
            volume_24h = float(data['v'])
            
            print(
                f"💰 {symbol}: ${price:,.2f} "
                f"({change_24h:+.2f}%) "
                f"Vol: ${volume_24h:,.0f}"
            )
    
    # Test ticker stream
    print("🚀 Starting Binance WebSocket test...")
    
    client = BinanceWebSocketClient(
        symbols=['BTCUSDT', 'ETHUSDT', 'BNBUSDT'],
        on_message=on_price_update,
        testnet=False
    )
    
    try:
        # Run for 30 seconds
        task = asyncio.create_task(client.start('ticker'))
        await asyncio.sleep(30)
        await client.stop()
        
        # Show statistics
        stats = client.get_stats()
        print("\n📊 Statistics:")
        print(f"  Messages: {stats['messages_received']}")
        print(f"  Errors: {stats['errors']}")
        print(f"  Reconnections: {stats['reconnections']}")
        print(f"  Uptime: {stats.get('uptime', 0):.1f}s")
        print(f"  Msg/sec: {stats.get('messages_per_second', 0):.2f}")
        
        # Show latest prices
        print("\n💰 Latest Prices:")
        for symbol, price in client.get_all_prices().items():
            print(f"  {symbol}: ${price:,.2f}")
    
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
        await client.stop()


if __name__ == "__main__":
    asyncio.run(main())
