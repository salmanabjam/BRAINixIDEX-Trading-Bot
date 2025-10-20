"""
Real-Time Price Comparison Tool
================================
Compare prices from different sources to verify data accuracy.
"""

import requests
from binance.client import Client
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

def get_binance_price():
    """Get current price from Binance"""
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['price'])
    except Exception as e:
        return f"Error: {e}"

def get_coinmarketcap_price():
    """Get current price from CoinMarketCap (via their public API)"""
    try:
        # Using CoinGecko as alternative (free, no API key required)
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['bitcoin']['usd'])
    except Exception as e:
        return f"Error: {e}"

def get_cached_price():
    """Get last price from cache"""
    try:
        import pandas as pd
        df = pd.read_csv('data/cache/BTCUSDT_1h_2024-01-01_2025-10-20.csv')
        last_row = df.iloc[-1]
        timestamp = last_row['timestamp']
        price = float(last_row['close'])
        return price, timestamp
    except Exception as e:
        return None, f"Error: {e}"

def main():
    print("=" * 70)
    print(f"{Fore.CYAN}🔍 Real-Time Price Comparison - BTC/USDT{Style.RESET_ALL}")
    print("=" * 70)
    print(f"\n⏰ Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Get prices
    print(f"{Fore.YELLOW}📡 Fetching prices...{Style.RESET_ALL}\n")
    
    binance_price = get_binance_price()
    coingecko_price = get_coinmarketcap_price()
    cached_price, cached_time = get_cached_price()
    
    # Display results
    print(f"{Fore.GREEN}1️⃣  Binance (Real-Time):{Style.RESET_ALL}")
    if isinstance(binance_price, float):
        print(f"   💰 ${binance_price:,.2f}")
    else:
        print(f"   ❌ {binance_price}")
    
    print(f"\n{Fore.GREEN}2️⃣  CoinGecko (Real-Time):{Style.RESET_ALL}")
    if isinstance(coingecko_price, float):
        print(f"   💰 ${coingecko_price:,.2f}")
        if isinstance(binance_price, float):
            diff = coingecko_price - binance_price
            diff_pct = (diff / binance_price) * 100
            print(f"   📊 Difference: ${diff:,.2f} ({diff_pct:+.2f}%)")
    else:
        print(f"   ❌ {coingecko_price}")
    
    print(f"\n{Fore.BLUE}3️⃣  Bot Cache (Historical):{Style.RESET_ALL}")
    if cached_price:
        print(f"   💰 ${cached_price:,.2f}")
        print(f"   📅 Last Update: {cached_time}")
        if isinstance(binance_price, float):
            diff = cached_price - binance_price
            diff_pct = (diff / binance_price) * 100
            time_diff = datetime.now() - datetime.strptime(cached_time, '%Y-%m-%d %H:%M:%S')
            hours_old = time_diff.total_seconds() / 3600
            print(f"   📊 Difference: ${diff:,.2f} ({diff_pct:+.2f}%)")
            print(f"   ⏱️  Data Age: {hours_old:.1f} hours old")
    else:
        print(f"   ❌ {cached_time}")
    
    print("\n" + "=" * 70)
    print(f"{Fore.YELLOW}💡 Explanation:{Style.RESET_ALL}")
    print("   • Bot uses CACHED data (1-hour candles)")
    print("   • Cache updates when you fetch new data")
    print("   • Real-time prices change every second")
    print("   • Difference is NORMAL for historical analysis")
    print("\n" + "=" * 70)
    print(f"\n{Fore.CYAN}🔄 To update cache with latest data:{Style.RESET_ALL}")
    print(f"   python -c \"from data.handler import DataHandler; dh = DataHandler(); dh.fetch_ohlcv(use_cache=False)\"")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
