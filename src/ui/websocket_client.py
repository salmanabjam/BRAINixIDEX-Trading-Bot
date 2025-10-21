"""
Real-time WebSocket Client for Streamlit Dashboard
===================================================
Client module to connect to WebSocket server and receive live market data.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import asyncio
import json
import logging
from typing import Dict, Optional, Callable
from datetime import datetime
import websockets
from threading import Thread
import queue

logger = logging.getLogger(__name__)


class WebSocketClient:
    """
    WebSocket client for receiving real-time market data.
    
    Features:
    - Auto-reconnection on disconnect
    - Message queue for thread-safe access
    - Callback support for live updates
    - Connection status monitoring
    """
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 8765,
        auto_reconnect: bool = True
    ):
        """
        Initialize WebSocket client.
        
        Args:
            host: Server host
            port: Server port
            auto_reconnect: Enable auto-reconnection
        """
        self.uri = f"ws://{host}:{port}"
        self.auto_reconnect = auto_reconnect
        self.websocket = None
        self.connected = False
        self.latest_data = {}
        self.message_queue = queue.Queue(maxsize=100)
        self.callbacks = []
        self._thread = None
        self._stop_event = asyncio.Event()
        
        logger.info(f"📡 WebSocket client initialized: {self.uri}")
    
    def add_callback(self, callback: Callable):
        """
        Add callback function for new data.
        
        Args:
            callback: Function to call with new data
        """
        self.callbacks.append(callback)
    
    async def connect(self):
        """Connect to WebSocket server."""
        try:
            self.websocket = await websockets.connect(self.uri)
            self.connected = True
            logger.info(f"✅ Connected to WebSocket: {self.uri}")
            return True
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from server."""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("🔌 Disconnected from WebSocket")
    
    async def receive_messages(self):
        """Receive and process messages from server."""
        while not self._stop_event.is_set():
            try:
                if not self.connected:
                    connected = await self.connect()
                    if not connected:
                        await asyncio.sleep(5)  # Wait before retry
                        continue
                
                # Receive message
                message = await self.websocket.recv()
                data = json.loads(message)
                
                # Process message
                await self._process_message(data)
                
            except websockets.exceptions.ConnectionClosed:
                logger.warning("⚠️ Connection closed")
                self.connected = False
                
                if self.auto_reconnect:
                    logger.info("🔄 Attempting to reconnect...")
                    await asyncio.sleep(5)
                else:
                    break
            
            except Exception as e:
                logger.error(f"❌ Error receiving message: {e}")
                await asyncio.sleep(1)
    
    async def _process_message(self, data: Dict):
        """
        Process received message.
        
        Args:
            data: Parsed JSON message
        """
        msg_type = data.get('type')
        
        if msg_type == 'market_update':
            self.latest_data = data.get('data', {})
            
            # Add to queue
            try:
                self.message_queue.put_nowait(self.latest_data)
            except queue.Full:
                # Remove oldest item
                try:
                    self.message_queue.get_nowait()
                    self.message_queue.put_nowait(self.latest_data)
                except queue.Empty:
                    pass
            
            # Call callbacks
            for callback in self.callbacks:
                try:
                    callback(self.latest_data)
                except Exception as e:
                    logger.error(f"Callback error: {e}")
        
        elif msg_type == 'initial_data':
            self.latest_data = data.get('data', {})
            logger.info("📊 Received initial data")
        
        elif msg_type == 'pong':
            logger.debug("🏓 Pong received")
    
    async def send_ping(self):
        """Send ping to server."""
        if self.connected and self.websocket:
            try:
                await self.websocket.send(json.dumps({'type': 'ping'}))
            except Exception as e:
                logger.error(f"Ping failed: {e}")
    
    async def request_status(self):
        """Request system status from server."""
        if self.connected and self.websocket:
            try:
                await self.websocket.send(json.dumps({
                    'type': 'request_status'
                }))
            except Exception as e:
                logger.error(f"Status request failed: {e}")
    
    def get_latest_data(self) -> Dict:
        """
        Get latest market data.
        
        Returns:
            Latest data dictionary
        """
        return self.latest_data.copy()
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get latest price for a symbol.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            
        Returns:
            Latest price or None
        """
        if symbol in self.latest_data:
            return self.latest_data[symbol].get('price')
        return None
    
    def is_connected(self) -> bool:
        """Check if connected to server."""
        return self.connected
    
    def start_background(self):
        """Start client in background thread."""
        if self._thread and self._thread.is_alive():
            logger.warning("Client already running")
            return
        
        def run_client():
            asyncio.run(self.receive_messages())
        
        self._thread = Thread(target=run_client, daemon=True)
        self._thread.start()
        logger.info("🚀 WebSocket client started in background")
    
    def stop(self):
        """Stop the client."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("🛑 WebSocket client stopped")


class StreamlitWebSocketClient:
    """
    Streamlit-optimized WebSocket client with session state.
    
    Designed for use in Streamlit apps with proper state management.
    """
    
    def __init__(self, session_state):
        """
        Initialize Streamlit client.
        
        Args:
            session_state: Streamlit session state object
        """
        self.session_state = session_state
        
        # Initialize client in session state
        if 'ws_client' not in session_state:
            session_state.ws_client = WebSocketClient()
            session_state.ws_client.start_background()
            session_state.ws_connected = False
            session_state.ws_latest_data = {}
    
    def get_client(self) -> WebSocketClient:
        """Get WebSocket client from session."""
        return self.session_state.ws_client
    
    def update_state(self):
        """Update session state with latest data."""
        client = self.get_client()
        self.session_state.ws_connected = client.is_connected()
        self.session_state.ws_latest_data = client.get_latest_data()
    
    def get_price(self, symbol: str) -> Optional[float]:
        """
        Get latest price for symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Latest price or None
        """
        client = self.get_client()
        return client.get_latest_price(symbol)
    
    def get_all_prices(self) -> Dict:
        """
        Get all latest prices.
        
        Returns:
            Dictionary of symbol -> data
        """
        self.update_state()
        return self.session_state.ws_latest_data
    
    def is_connected(self) -> bool:
        """Check connection status."""
        self.update_state()
        return self.session_state.ws_connected


# Singleton instance for Streamlit
_streamlit_client = None


def get_streamlit_client(session_state) -> StreamlitWebSocketClient:
    """
    Get or create Streamlit WebSocket client.
    
    Args:
        session_state: Streamlit session state
        
    Returns:
        StreamlitWebSocketClient instance
    """
    global _streamlit_client
    
    if _streamlit_client is None:
        _streamlit_client = StreamlitWebSocketClient(session_state)
    
    return _streamlit_client


if __name__ == "__main__":
    # Test client
    async def test_client():
        client = WebSocketClient()
        
        def on_data(data):
            print(f"📊 Received: {len(data)} symbols")
            for symbol, info in list(data.items())[:3]:
                print(f"  {symbol}: ${info.get('price', 0):,.2f}")
        
        client.add_callback(on_data)
        
        await client.receive_messages()
    
    print("📡 Testing WebSocket Client")
    print("=" * 50)
    print("Connecting to ws://localhost:8765")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        asyncio.run(test_client())
    except KeyboardInterrupt:
        print("\n🛑 Test stopped")
