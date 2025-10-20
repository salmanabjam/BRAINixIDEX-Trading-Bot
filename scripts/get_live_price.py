"""
Get Live Price from Binance - Real-time Market Data
====================================================
Fetches current live price directly from Binance API
"""

import sys
from pathlib import Path

# Add src to path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / 'src'))

from data.handler import DataHandler
from datetime import datetime

def get_live_price():
    """Fetch and display live price from Binance"""
    print("=" * 70)
    print("💰 BiX TradeBOT - LIVE PRICE CHECKER")
    print("=" * 70)
    print()
    
    # Initialize data handler
    dh = DataHandler()
    
    # Symbols to check
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
    
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("📊 LIVE MARKET PRICES:")
    print("-" * 70)
    
    for symbol in symbols:
        try:
            price = dh.fetch_latest_price(symbol)
            print(f"  {symbol:12} → ${price:,.2f}")
        except Exception as e:
            print(f"  {symbol:12} → Error: {str(e)}")
    
    print("=" * 70)
    print()
    
    # Get detailed info for BTC
    print("📈 BTC/USDT DETAILED INFO:")
    print("-" * 70)
    
    try:
        # Fetch last 10 candles
        df = dh.fetch_ohlcv('BTCUSDT', '1h', limit=10)
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        price_change = latest['close'] - prev['close']
        price_change_pct = (price_change / prev['close']) * 100
        
        print(f"  Current Price:    ${latest['close']:,.2f}")
        print(f"  24h High:         ${df['high'].tail(24).max():,.2f}")
        print(f"  24h Low:          ${df['low'].tail(24).min():,.2f}")
        print(f"  Last Hour Change: ${price_change:+,.2f} ({price_change_pct:+.2f}%)")
        print(f"  Volume (1h):      ${latest['volume']:,.2f}")
        print(f"  Timestamp:        {latest['timestamp']}")
        
    except Exception as e:
        print(f"  Error: {str(e)}")
    
    print("=" * 70)

if __name__ == "__main__":
    get_live_price()
