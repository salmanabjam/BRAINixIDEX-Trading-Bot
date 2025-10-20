"""
BiX TradeBOT - WebSocket Server for Real-Time Data Streaming
=============================================================

Provides WebSocket endpoint for dashboard and external clients to receive
live cryptocurrency price updates.

Features:
- Real-time price broadcasting to multiple clients
- JSON message format
- Auto-reconnection support
- Low latency (<100ms)

Author: BiX TradeBOT Team
License: Educational Use Only
"""

import asyncio
import json
import logging
from typing import Set
from datetime import datetime
import websockets
from websockets.server import WebSocketServerProtocol

from analysis.live_feed import LiveDataFeed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSocketServer:
    """
    WebSocket server for broadcasting live market data.
    """
    
    def __init__(self, host: str = 'localhost', port: int = 8765, top_n_coins: int = 50):
        """
        Initialize WebSocket server.
        
        Args:
            host: Server host address
            port: Server port
            top_n_coins: Number of top coins to track
        """
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.feed = LiveDataFeed(top_n_coins=top_n_coins, update_interval=5)
        
        logger.info(f"🌐 WebSocket server initialized: ws://{host}:{port}")
    
    async def register_client(self, websocket: WebSocketServerProtocol):
        """Register a new client connection."""
        self.clients.add(websocket)
        logger.info(f"✅ Client connected: {websocket.remote_address} (Total: {len(self.clients)})")
    
    async def unregister_client(self, websocket: WebSocketServerProtocol):
        """Unregister a disconnected client."""
        self.clients.discard(websocket)
        logger.info(f"❌ Client disconnected: {websocket.remote_address} (Total: {len(self.clients)})")
    
    async def broadcast_data(self, data):
        """
        Broadcast data to all connected clients.
        
        Args:
            data: Market data to broadcast
        """
        if not self.clients:
            return
        
        message = {
            'type': 'market_update',
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        json_message = json.dumps(message)
        
        # Send to all clients
        disconnected_clients = set()
        for client in self.clients:
            try:
                await client.send(json_message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            await self.unregister_client(client)
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """
        Handle individual client connection.
        
        Args:
            websocket: WebSocket connection
            path: Connection path
        """
        await self.register_client(websocket)
        
        try:
            # Send initial data
            if self.feed.latest_data:
                await websocket.send(json.dumps({
                    'type': 'initial_data',
                    'timestamp': datetime.now().isoformat(),
                    'data': self.feed.latest_data
                }))
            
            # Listen for client messages (ping/pong, etc.)
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    if data.get('type') == 'ping':
                        await websocket.send(json.dumps({'type': 'pong'}))
                    
                    elif data.get('type') == 'request_status':
                        status = self.feed.get_system_status()
                        await websocket.send(json.dumps({
                            'type': 'status',
                            'data': status
                        }))
                    
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from client: {message}")
        
        except websockets.exceptions.ConnectionClosed:
            pass
        
        finally:
            await self.unregister_client(websocket)
    
    async def start(self):
        """Start the WebSocket server and data feed."""
        logger.info(f"🚀 Starting WebSocket server on ws://{self.host}:{self.port}")
        
        # Start the live data feed with broadcast callback
        feed_task = asyncio.create_task(
            self.feed.start_continuous_feed(callback=self.broadcast_data)
        )
        
        # Start WebSocket server
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info(f"✅ WebSocket server running! Connect at ws://{self.host}:{self.port}")
            await feed_task


async def main():
    """Main entry point."""
    server = WebSocketServer(host='0.0.0.0', port=8765, top_n_coins=50)
    await server.start()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
