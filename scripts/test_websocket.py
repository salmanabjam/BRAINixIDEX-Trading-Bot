"""
Test WebSocket Integration
===========================
Tests real-time price updates from Binance WebSocket.

This script will:
1. Connect to Binance WebSocket
2. Subscribe to BTCUSDT ticker stream
3. Print real-time price updates for 30 seconds
4. Show statistics

Author: SALMAN ThinkTank AI Core
"""

import sys
import asyncio
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data.binance_websocket import BinanceWebSocketClient
from utils.advanced_logger import get_logger

logger = get_logger(__name__, component='WebSocketTest')


async def test_websocket_basic():
    """Test basic WebSocket functionality."""
    print("=" * 60)
    print("📡 Binance WebSocket Integration Test")
    print("=" * 60)
    
    # Track updates
    update_count = 0
    last_prices = {}
    
    async def on_price_update(data):
        """Callback for price updates."""
        nonlocal update_count, last_prices
        
        # Extract ticker data
        if 'c' in data:  # Close price (24hr ticker)
            symbol = data.get('s', 'UNKNOWN')
            price = float(data['c'])
            change_24h = float(data.get('P', 0))
            volume_24h = float(data.get('v', 0))
            high_24h = float(data.get('h', 0))
            low_24h = float(data.get('l', 0))
            
            update_count += 1
            last_prices[symbol] = price
            
            # Print every 5th update to avoid spam
            if update_count % 5 == 0:
                print(
                    f"\n💰 {symbol}: ${price:,.2f} "
                    f"({change_24h:+.2f}%)"
                )
                print(
                    f"   📊 24h High: ${high_24h:,.2f} | "
                    f"Low: ${low_24h:,.2f} | "
                    f"Vol: ${volume_24h:,.0f}"
                )
    
    # Test 1: Single symbol
    print("\n🔹 Test 1: Single Symbol (BTCUSDT)")
    print("-" * 60)
    
    client = BinanceWebSocketClient(
        symbols=['BTCUSDT'],
        on_message=on_price_update,
        testnet=False
    )
    
    try:
        # Start WebSocket
        task = asyncio.create_task(client.start('ticker'))
        
        # Run for 15 seconds
        print("🟢 Listening for 15 seconds...")
        await asyncio.sleep(15)
        
        # Stop
        await client.stop()
        
        # Show stats
        stats = client.get_stats()
        print("\n📊 Statistics (Test 1):")
        print(f"   Messages received: {stats['messages_received']}")
        print(f"   Errors: {stats['errors']}")
        print(f"   Reconnections: {stats['reconnections']}")
        print(f"   Uptime: {stats.get('uptime', 0):.1f}s")
        print(f"   Msg/sec: {stats.get('messages_per_second', 0):.2f}")
        
        # Show latest price
        if last_prices:
            print("\n💵 Latest Prices:")
            for symbol, price in last_prices.items():
                print(f"   {symbol}: ${price:,.2f}")
    
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
        await client.stop()
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Test failed: {e}")
        await client.stop()
    
    # Test 2: Multiple symbols
    print("\n\n🔹 Test 2: Multiple Symbols (BTC, ETH, BNB)")
    print("-" * 60)
    
    update_count = 0
    last_prices = {}
    
    client2 = BinanceWebSocketClient(
        symbols=['BTCUSDT', 'ETHUSDT', 'BNBUSDT'],
        on_message=on_price_update,
        testnet=False
    )
    
    try:
        # Start WebSocket
        task2 = asyncio.create_task(client2.start('ticker'))
        
        # Run for 15 seconds
        print("🟢 Listening for 15 seconds...")
        await asyncio.sleep(15)
        
        # Stop
        await client2.stop()
        
        # Show stats
        stats2 = client2.get_stats()
        print("\n📊 Statistics (Test 2):")
        print(f"   Messages received: {stats2['messages_received']}")
        print(f"   Errors: {stats2['errors']}")
        print(f"   Reconnections: {stats2['reconnections']}")
        print(f"   Uptime: {stats2.get('uptime', 0):.1f}s")
        print(f"   Msg/sec: {stats2.get('messages_per_second', 0):.2f}")
        
        # Show latest prices
        if last_prices:
            print("\n💵 Latest Prices (All Symbols):")
            for symbol, price in sorted(last_prices.items()):
                print(f"   {symbol}: ${price:,.2f}")
    
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
        await client2.stop()
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Test failed: {e}")
        await client2.stop()
    
    print("\n" + "=" * 60)
    print("✅ WebSocket Integration Test Complete")
    print("=" * 60)


async def test_datahandler_websocket():
    """Test DataHandler with WebSocket integration."""
    print("\n\n" + "=" * 60)
    print("🔌 DataHandler WebSocket Integration Test")
    print("=" * 60)
    
    from data.handler import DataHandler
    
    # Test DataHandler with WebSocket
    print("\n🔹 Creating DataHandler with WebSocket enabled...")
    
    handler = DataHandler(
        use_ccxt=False,
        enable_websocket=True
    )
    
    try:
        # Wait for connection
        print("⏳ Waiting 3 seconds for WebSocket to connect...")
        await asyncio.sleep(3)
        
        # Check WebSocket stats
        stats = handler.get_websocket_stats()
        if stats:
            print("\n📊 WebSocket Stats:")
            print(f"   Messages: {stats['messages_received']}")
            print(f"   Errors: {stats['errors']}")
            print(f"   Uptime: {stats.get('uptime', 0):.1f}s")
        
        # Get real-time price
        print("\n💰 Fetching real-time prices...")
        for _ in range(5):
            price = handler.get_websocket_price('BTCUSDT')
            if price:
                print(f"   BTCUSDT: ${price:,.2f}")
            await asyncio.sleep(2)
        
        # Stop WebSocket
        print("\n🛑 Stopping WebSocket...")
        handler.stop_websocket()
        
        print("✅ Test complete")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"DataHandler test failed: {e}")
        handler.stop_websocket()
    
    print("=" * 60)


async def main():
    """Run all tests."""
    try:
        # Test 1: Basic WebSocket
        await test_websocket_basic()
        
        # Test 2: DataHandler integration
        await test_datahandler_websocket()
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logger.error(f"Test suite failed: {e}")


if __name__ == "__main__":
    print("\n🚀 Starting WebSocket tests...")
    print("Press Ctrl+C to stop\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Tests stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
