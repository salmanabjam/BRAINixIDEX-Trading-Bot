"""
Update Market Data Cache
=========================
Fetch latest market data and update cache.
"""

from data.handler import DataHandler
from colorama import init, Fore, Style
from datetime import datetime

init(autoreset=True)

def main():
    print("=" * 70)
    print(f"{Fore.CYAN}🔄 Updating Market Data Cache{Style.RESET_ALL}")
    print("=" * 70)
    print(f"\n⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize data handler
    print(f"{Fore.YELLOW}📡 Initializing Data Handler...{Style.RESET_ALL}")
    dh = DataHandler()
    
    # Fetch latest data (bypassing cache)
    print(f"\n{Fore.YELLOW}📥 Fetching latest BTCUSDT data...{Style.RESET_ALL}")
    print("   This may take a minute...\n")
    
    try:
        df = dh.fetch_ohlcv(
            symbol='BTCUSDT',
            timeframe='1h',
            use_cache=False,  # Force fresh data
            limit=1000
        )
        
        print(f"{Fore.GREEN}✅ Data fetched successfully!{Style.RESET_ALL}")
        print(f"\n📊 Data Summary:")
        print(f"   Total Candles: {len(df)}")
        if 'timestamp' in df.columns:
            print(f"   Date Range: {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
        print(f"   Latest Close: ${df['close'].iloc[-1]:,.2f}")
        
        print("\n" + "=" * 70)
        print(f"{Fore.GREEN}✅ Cache updated successfully!{Style.RESET_ALL}")
        print("=" * 70)
        
        print(f"\n{Fore.CYAN}🚀 Now run the bot again:{Style.RESET_ALL}")
        print("   python main.py analyze --symbol BTCUSDT --timeframe 1h")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error updating cache: {e}{Style.RESET_ALL}")
        return False
    
    return True

if __name__ == "__main__":
    main()
