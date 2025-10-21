"""
Tests for Binance WebSocket Client
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data.binance_websocket import (
    BinanceWebSocketClient,
    BinanceKlineWebSocket
)


class TestBinanceWebSocketClient:
    """Test WebSocket client"""
    
    def test_init(self):
        """Test initialization"""
        client = BinanceWebSocketClient(
            symbols=['BTCUSDT', 'ETHUSDT'],
            testnet=False
        )
        
        assert client.symbols == ['BTCUSDT', 'ETHUSDT']
        assert client.testnet is False
        assert client.is_running is False
        assert client.reconnect_attempts == 0
    
    def test_get_stream_url_single_symbol(self):
        """Test stream URL for single symbol"""
        client = BinanceWebSocketClient(symbols=['BTCUSDT'])
        url = client.get_stream_url('ticker')
        
        assert 'btcusdt@ticker' in url
        assert 'stream.binance.com' in url
    
    def test_get_stream_url_multiple_symbols(self):
        """Test stream URL for multiple symbols"""
        client = BinanceWebSocketClient(
            symbols=['BTCUSDT', 'ETHUSDT']
        )
        url = client.get_stream_url('ticker')
        
        assert 'btcusdt@ticker' in url
        assert 'ethusdt@ticker' in url
        assert 'stream?streams=' in url
    
    def test_get_stream_url_testnet(self):
        """Test testnet URL"""
        client = BinanceWebSocketClient(
            symbols=['BTCUSDT'],
            testnet=True
        )
        url = client.get_stream_url('ticker')
        
        assert 'testnet.binance.vision' in url
    
    @pytest.mark.asyncio
    async def test_handle_message_ticker(self):
        """Test ticker message handling"""
        client = BinanceWebSocketClient(symbols=['BTCUSDT'])
        
        # Simulate ticker message
        message = '''{
            "e": "24hrTicker",
            "s": "BTCUSDT",
            "c": "50000.00",
            "P": "2.5",
            "v": "1000000"
        }'''
        
        await client._handle_message(message)
        
        assert client.stats['messages_received'] == 1
        assert 'BTCUSDT' in client.latest_data
        assert client.latest_data['BTCUSDT']['c'] == '50000.00'
    
    @pytest.mark.asyncio
    async def test_handle_message_multi_stream(self):
        """Test multi-stream message handling"""
        client = BinanceWebSocketClient(
            symbols=['BTCUSDT', 'ETHUSDT']
        )
        
        # Simulate multi-stream message
        message = '''{
            "stream": "btcusdt@ticker",
            "data": {
                "e": "24hrTicker",
                "s": "BTCUSDT",
                "c": "50000.00"
            }
        }'''
        
        await client._handle_message(message)
        
        assert 'BTCUSDT' in client.latest_data
        assert client.latest_data['BTCUSDT']['c'] == '50000.00'
    
    @pytest.mark.asyncio
    async def test_handle_message_invalid_json(self):
        """Test invalid JSON handling"""
        client = BinanceWebSocketClient(symbols=['BTCUSDT'])
        
        await client._handle_message('invalid json')
        
        assert client.stats['errors'] == 1
    
    @pytest.mark.asyncio
    async def test_handle_message_with_callback(self):
        """Test message callback"""
        callback = AsyncMock()
        client = BinanceWebSocketClient(
            symbols=['BTCUSDT'],
            on_message=callback
        )
        
        message = '{"e": "24hrTicker", "s": "BTCUSDT", "c": "50000"}'
        await client._handle_message(message)
        
        callback.assert_called_once()
    
    def test_get_latest_price(self):
        """Test getting latest price"""
        client = BinanceWebSocketClient(symbols=['BTCUSDT'])
        
        # Set test data
        client.latest_data['BTCUSDT'] = {'c': '50000.00'}
        
        price = client.get_latest_price('BTCUSDT')
        assert price == 50000.00
    
    def test_get_latest_price_not_found(self):
        """Test getting price for non-existent symbol"""
        client = BinanceWebSocketClient(symbols=['BTCUSDT'])
        
        price = client.get_latest_price('ETHUSDT')
        assert price is None
    
    def test_get_all_prices(self):
        """Test getting all prices"""
        client = BinanceWebSocketClient(
            symbols=['BTCUSDT', 'ETHUSDT']
        )
        
        # Set test data
        client.latest_data['BTCUSDT'] = {'c': '50000.00'}
        client.latest_data['ETHUSDT'] = {'c': '3000.00'}
        
        prices = client.get_all_prices()
        
        assert len(prices) == 2
        assert prices['BTCUSDT'] == 50000.00
        assert prices['ETHUSDT'] == 3000.00
    
    def test_get_stats(self):
        """Test statistics retrieval"""
        client = BinanceWebSocketClient(symbols=['BTCUSDT'])
        
        client.stats['messages_received'] = 100
        client.stats['errors'] = 2
        client.stats['reconnections'] = 1
        client.stats['uptime_start'] = datetime.now()
        
        stats = client.get_stats()
        
        assert stats['messages_received'] == 100
        assert stats['errors'] == 2
        assert stats['reconnections'] == 1
        assert 'uptime' in stats
        assert 'messages_per_second' in stats


class TestBinanceKlineWebSocket:
    """Test Kline WebSocket client"""
    
    def test_init(self):
        """Test initialization"""
        client = BinanceKlineWebSocket(
            symbols=['BTCUSDT'],
            interval='5m'
        )
        
        assert client.interval == '5m'
        assert client.symbols == ['BTCUSDT']
    
    def test_get_stream_url(self):
        """Test kline stream URL"""
        client = BinanceKlineWebSocket(
            symbols=['BTCUSDT'],
            interval='1h'
        )
        
        url = client.get_stream_url()
        assert 'kline_1h' in url
    
    @pytest.mark.asyncio
    async def test_handle_kline(self):
        """Test kline message handling"""
        callback = AsyncMock()
        client = BinanceKlineWebSocket(
            symbols=['BTCUSDT'],
            interval='1m',
            on_kline=callback
        )
        
        # Simulate kline message
        data = {
            'k': {
                's': 'BTCUSDT',
                't': 1640000000000,
                'o': '50000',
                'h': '50500',
                'l': '49800',
                'c': '50200',
                'v': '100',
                'x': True
            }
        }
        
        await client._handle_kline(data)
        
        callback.assert_called_once()
        call_args = callback.call_args[0][0]
        assert call_args['symbol'] == 'BTCUSDT'
        assert call_args['open'] == 50000.0
        assert call_args['close'] == 50200.0
        assert call_args['is_closed'] is True


class TestWebSocketIntegration:
    """Integration tests for WebSocket"""
    
    @pytest.mark.asyncio
    async def test_connection_lifecycle(self):
        """Test connection, message handling, and disconnection"""
        client = BinanceWebSocketClient(symbols=['BTCUSDT'])
        
        # Should start disconnected
        assert client.is_running is False
        assert client.ws is None
        
        # Stats should be initialized
        stats = client.get_stats()
        assert stats['messages_received'] == 0
        assert stats['errors'] == 0
    
    @pytest.mark.asyncio
    async def test_message_queue(self):
        """Test message queue functionality"""
        client = BinanceWebSocketClient(symbols=['BTCUSDT'])
        
        # Add multiple messages
        for i in range(5):
            message = f'{{"e": "ticker", "s": "BTCUSDT", "c": "{50000 + i}"}}'
            await client._handle_message(message)
        
        assert client.stats['messages_received'] == 5
        assert len(client.message_queue) == 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
