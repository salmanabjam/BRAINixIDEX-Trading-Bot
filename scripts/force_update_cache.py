"""
Force Update Cache with Latest Data
====================================
Fetches the most recent 1000 candles from Binance.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data.handler import DataHandler
from colorama import init, Fore, Style
from datetime import datetime, timedelta

init(autoreset=True)


def main():
    print("=" * 70)
    print(f"{Fore.CYAN}🚀 Force Update Cache with Latest Data{Style.RESET_ALL}")
    print("=" * 70)
    
    # Calculate dates for last 1000 hours (41 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=1000)
    
    print(f"\n📅 Fetching data:")
    print(f"   Start: {start_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"   End:   {end_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"   Total: 1000 hourly candles (last 41 days)\n")
    
    # Initialize data handler
    print(f"{Fore.YELLOW}📡 Initializing Data Handler...{Style.RESET_ALL}")
    dh = DataHandler()
    
    try:
        # Fetch with specific date range
        df = dh.fetch_ohlcv(
            symbol='BTCUSDT',
            timeframe='1h',
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            use_cache=False,
            limit=1000
        )
        
        print(f"\n{Fore.GREEN}✅ Data fetched successfully!{Style.RESET_ALL}")
        print(f"\n📊 Data Summary:")
        print(f"   Total Candles: {len(df)}")
        
        # Reset index to access timestamp
        df_reset = df.reset_index()
        if 'timestamp' in df_reset.columns:
            first_date = df_reset['timestamp'].iloc[0]
            last_date = df_reset['timestamp'].iloc[-1]
            print(f"   First Candle: {first_date}")
            print(f"   Last Candle:  {last_date}")
        
        print(f"   Latest Close: ${df['close'].iloc[-1]:,.2f}")
        print(f"   Latest High:  ${df['high'].iloc[-1]:,.2f}")
        print(f"   Latest Low:   ${df['low'].iloc[-1]:,.2f}")
        
        print("\n" + "=" * 70)
        print(f"{Fore.GREEN}✅ Cache updated with latest market data!{Style.RESET_ALL}")
        print("=" * 70)
        
        print(f"\n{Fore.CYAN}🚀 Now run the bot again:{Style.RESET_ALL}")
        print("   python main.py analyze --symbol BTCUSDT --timeframe 1h")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    main()
