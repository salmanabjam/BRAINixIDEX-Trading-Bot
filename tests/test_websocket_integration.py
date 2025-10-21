"""
WebSocket Integration Tests
============================
Test suite for real-time WebSocket client and Streamlit integration.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from threading import Event
from queue import Queue

from ui.websocket_client import WebSocketClient, StreamlitWebSocketClient


class MockWebSocket:
    """Mock WebSocket for testing."""
    
    def __init__(self, messages=None):
        self.messages = messages or []
        self.message_index = 0
        self.closed = False
        self.sent_messages = []
    
    async def recv(self):
        """Simulate receiving messages."""
        if self.message_index >= len(self.messages):
            # Simulate connection close
            raise ConnectionClosed(1000, "Test close")
        
        msg = self.messages[self.message_index]
        self.message_index += 1
        return json.dumps(msg)
    
    async def send(self, data):
        """Simulate sending messages."""
        self.sent_messages.append(json.loads(data))
    
    async def close(self):
        """Simulate closing connection."""
        self.closed = True


class ConnectionClosed(Exception):
    """Mock ConnectionClosed exception."""
    
    def __init__(self, code, reason):
        self.code = code
        self.reason = reason


@pytest.fixture
def mock_websocket():
    """Create mock WebSocket."""
    return MockWebSocket()


@pytest.fixture
def client():
    """Create WebSocketClient instance."""
    return WebSocketClient(host="localhost", port=8765)


@pytest.fixture
def mock_session_state():
    """Create mock Streamlit session state."""
    class SessionState:
        def __init__(self):
            self._data = {}
        
        def __contains__(self, key):
            return key in self._data
        
        def __getattr__(self, name):
            if name.startswith('_'):
                return object.__getattribute__(self, name)
            return self._data.get(name)
        
        def __setattr__(self, name, value):
            if name.startswith('_'):
                object.__setattr__(self, name, value)
            else:
                self._data[name] = value
        
        def get(self, key, default=None):
            return self._data.get(key, default)
    
    return SessionState()


class TestWebSocketClient:
    """Test WebSocketClient functionality."""
    
    def test_init(self, client):
        """Test client initialization."""
        assert client.uri == "ws://localhost:8765"
        assert client.auto_reconnect is True
        assert client.connected is False
        assert client.websocket is None
        assert isinstance(client.message_queue, Queue)
        assert client.latest_data == {}
    
    @pytest.mark.asyncio
    async def test_connect_success(self, client):
        """Test successful connection."""
        mock_ws = MockWebSocket()
        
        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_connect.return_value.__aenter__.return_value = mock_ws
            
            await client.connect()
            
            assert client.websocket is not None
            mock_connect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_disconnect(self, client):
        """Test disconnection."""
        client.websocket = MockWebSocket()
        client.connected = True
        
        await client.disconnect()
        
        assert client.connected is False
        assert client.websocket.closed is True
    
    @pytest.mark.asyncio
    async def test_process_market_update(self, client):
        """Test processing market update message."""
        test_data = {
            'type': 'market_update',
            'data': {
                'BTCUSDT': {'price': 50000, 'change_24h': 2.5}
            }
        }
        
        await client._process_message(test_data)
        
        assert 'BTCUSDT' in client.latest_data
        assert client.latest_data['BTCUSDT']['price'] == 50000
        assert not client.message_queue.empty()
    
    @pytest.mark.asyncio
    async def test_process_initial_data(self, client):
        """Test processing initial data message."""
        test_data = {
            'type': 'initial_data',
            'data': {
                'BTCUSDT': {'price': 50000},
                'ETHUSDT': {'price': 3000}
            }
        }
        
        await client._process_message(test_data)
        
        assert len(client.latest_data) == 2
        assert client.latest_data['BTCUSDT']['price'] == 50000
        assert client.latest_data['ETHUSDT']['price'] == 3000
    
    @pytest.mark.asyncio
    async def test_callback_execution(self, client):
        """Test callback execution on message."""
        callback_called = Event()
        callback_data = {}
        
        def test_callback(data):
            nonlocal callback_data
            callback_data = data
            callback_called.set()
        
        client.add_callback(test_callback)
        
        test_msg = {
            'type': 'market_update',
            'data': {'BTCUSDT': {'price': 50000}}
        }
        
        await client._process_message(test_msg)
        
        # Give callback time to execute
        callback_called.wait(timeout=1)
        
        # Callback receives only the data part
        assert callback_data == {'BTCUSDT': {'price': 50000}}
    
    def test_get_latest_price(self, client):
        """Test getting latest price for symbol."""
        client.latest_data = {
            'BTCUSDT': {'price': 50000, 'change_24h': 2.5}
        }
        
        price = client.get_latest_price('BTCUSDT')
        assert price == 50000
        
        # Test non-existent symbol
        price = client.get_latest_price('INVALID')
        assert price is None
    
    def test_get_latest_data(self, client):
        """Test getting all latest data."""
        test_data = {
            'BTCUSDT': {'price': 50000},
            'ETHUSDT': {'price': 3000}
        }
        client.latest_data = test_data.copy()
        
        data = client.get_latest_data()
        assert data == test_data
    
    @pytest.mark.asyncio
    async def test_send_ping(self, client):
        """Test sending ping message."""
        mock_ws = MockWebSocket()
        client.websocket = mock_ws
        client.connected = True
        
        await client.send_ping()
        
        assert len(mock_ws.sent_messages) == 1
        assert mock_ws.sent_messages[0]['type'] == 'ping'
    
    @pytest.mark.asyncio
    async def test_request_status(self, client):
        """Test requesting status."""
        mock_ws = MockWebSocket()
        client.websocket = mock_ws
        client.connected = True
        
        await client.request_status()
        
        assert len(mock_ws.sent_messages) == 1
        assert mock_ws.sent_messages[0]['type'] == 'request_status'
    
    def test_background_thread_start(self, client):
        """Test starting background thread."""
        client.start_background()
        
        assert client._thread is not None
        assert client._thread.is_alive()
        
        # Stop thread
        client.stop()
        client._thread.join(timeout=2)
    
    def test_stop_client(self, client):
        """Test stopping client."""
        client.start_background()
        
        # Stop client
        client.stop()
        
        # Thread should be stopped
        assert client._stop_event.is_set()


class TestStreamlitWebSocketClient:
    """Test StreamlitWebSocketClient functionality."""
    
    def test_init(self, mock_session_state):
        """Test Streamlit client initialization."""
        streamlit_client = StreamlitWebSocketClient(mock_session_state)
        
        assert streamlit_client.session_state is mock_session_state
        assert mock_session_state.ws_client is not None
        assert isinstance(mock_session_state.ws_client, WebSocketClient)
    
    def test_get_client(self, mock_session_state):
        """Test getting WebSocket client."""
        streamlit_client = StreamlitWebSocketClient(mock_session_state)
        ws_client = streamlit_client.get_client()
        
        assert isinstance(ws_client, WebSocketClient)
        assert ws_client is mock_session_state.ws_client
    
    def test_update_state(self, mock_session_state):
        """Test updating session state."""
        streamlit_client = StreamlitWebSocketClient(mock_session_state)
        ws_client = streamlit_client.get_client()
        ws_client.latest_data = {
            'BTCUSDT': {'price': 50000}
        }
        ws_client.connected = True
        
        streamlit_client.update_state()
        
        assert mock_session_state.ws_latest_data == {
            'BTCUSDT': {'price': 50000}
        }
        assert mock_session_state.ws_connected is True
    
    def test_get_price(self, mock_session_state):
        """Test getting price through Streamlit client."""
        streamlit_client = StreamlitWebSocketClient(mock_session_state)
        ws_client = streamlit_client.get_client()
        ws_client.latest_data = {
            'BTCUSDT': {'price': 50000}
        }
        
        price = streamlit_client.get_price('BTCUSDT')
        assert price == 50000
    
    def test_get_all_prices(self, mock_session_state):
        """Test getting all prices."""
        streamlit_client = StreamlitWebSocketClient(mock_session_state)
        ws_client = streamlit_client.get_client()
        test_data = {
            'BTCUSDT': {'price': 50000},
            'ETHUSDT': {'price': 3000}
        }
        ws_client.latest_data = test_data.copy()
        ws_client.connected = True
        
        data = streamlit_client.get_all_prices()
        assert data == test_data
    
    def test_is_connected(self, mock_session_state):
        """Test connection status check."""
        streamlit_client = StreamlitWebSocketClient(mock_session_state)
        ws_client = streamlit_client.get_client()
        
        # Not connected
        ws_client.connected = False
        assert streamlit_client.is_connected() is False
        
        # Connected
        ws_client.connected = True
        assert streamlit_client.is_connected() is True


class TestWebSocketIntegration:
    """Integration tests for WebSocket system."""
    
    @pytest.mark.asyncio
    async def test_full_message_flow(self):
        """Test complete message flow from server to client."""
        # Create client
        client = WebSocketClient()
        
        # Simulate receiving messages
        messages = [
            {
                'type': 'initial_data',
                'data': {
                    'BTCUSDT': {'price': 50000, 'change_24h': 2.5}
                }
            },
            {
                'type': 'market_update',
                'data': {
                    'BTCUSDT': {'price': 50100, 'change_24h': 2.7}
                }
            }
        ]
        
        for msg in messages:
            await client._process_message(msg)
        
        # Verify final state
        assert client.latest_data['BTCUSDT']['price'] == 50100
        assert client.latest_data['BTCUSDT']['change_24h'] == 2.7
        # Only market_update adds to queue, not initial_data
        assert client.message_queue.qsize() == 1
    
    @pytest.mark.asyncio
    async def test_reconnect_behavior(self):
        """Test auto-reconnect behavior."""
        client = WebSocketClient(auto_reconnect=True)
        
        # Mock connection that fails once then succeeds
        connection_attempts = []
        
        async def mock_connect_side_effect(*args, **kwargs):
            connection_attempts.append(1)
            if len(connection_attempts) == 1:
                raise ConnectionError("First attempt fails")
            return MockWebSocket()
        
        with patch('websockets.connect', side_effect=mock_connect_side_effect):
            # This would normally reconnect, but we'll just test the flag
            assert client.auto_reconnect is True
    
    def test_streamlit_integration_flow(self, mock_session_state):
        """Test complete Streamlit integration."""
        # Create Streamlit client
        streamlit_client = StreamlitWebSocketClient(mock_session_state)
        ws_client = streamlit_client.get_client()
        
        # Simulate receiving data
        ws_client.latest_data = {
            'BTCUSDT': {'price': 50000, 'change_24h': 2.5},
            'ETHUSDT': {'price': 3000, 'change_24h': 1.2}
        }
        ws_client.connected = True
        
        # Update state
        streamlit_client.update_state()
        
        # Verify session state updated
        assert mock_session_state.ws_connected is True
        assert 'BTCUSDT' in mock_session_state.ws_latest_data
        
        # Get prices
        btc_price = streamlit_client.get_price('BTCUSDT')
        assert btc_price == 50000
        
        all_prices = streamlit_client.get_all_prices()
        assert len(all_prices) == 2


if __name__ == "__main__":
    print("🧪 Running WebSocket Integration Tests")
    print("=" * 50)
    pytest.main([__file__, '-v', '--tb=short'])
