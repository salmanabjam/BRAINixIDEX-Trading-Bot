"""
Get Latest Real-Time Market Data
=================================
Fetch the most recent market data with accurate timestamp.
"""

from data.handler import DataHandler
from datetime import datetime, timedelta
from colorama import init, Fore, Style

init(autoreset=True)


def main():
    print("=" * 70)
    print(f"{Fore.CYAN}📡 Fetching Latest Market Data{Style.RESET_ALL}")
    print("=" * 70)
    
    # Initialize data handler
    dh = DataHandler()
    
    # Get last 24 hours of data
    end = datetime.now()
    start = end - timedelta(hours=24)
    
    print(f"\n{Fore.YELLOW}📥 Fetching last 24 hours...{Style.RESET_ALL}")
    
    try:
        df = dh.fetch_ohlcv(
            symbol='BTCUSDT',
            timeframe='1h',
            start_date=start.strftime('%Y-%m-%d'),
            end_date=end.strftime('%Y-%m-%d'),
            use_cache=False,
            limit=24
        )
        
        print(f"{Fore.GREEN}✅ Success!{Style.RESET_ALL}\n")
        print(f"{'='*70}")
        print(f"{Fore.CYAN}📊 Latest Data:{Style.RESET_ALL}")
        print(f"{'='*70}")
        print(f"\n{Fore.GREEN}💰 Current Price: ${df['close'].iloc[-1]:,.2f}{Style.RESET_ALL}")
        print(f"📅 Timestamp: {df.index[-1]}")
        print(f"📈 24h High: ${df['high'].max():,.2f}")
        print(f"📉 24h Low: ${df['low'].min():,.2f}")
        print(f"📊 24h Volume: {df['volume'].sum():,.2f} BTC")
        
        # Calculate price change
        price_change = df['close'].iloc[-1] - df['open'].iloc[0]
        price_change_pct = (price_change / df['open'].iloc[0]) * 100
        
        if price_change > 0:
            color = Fore.GREEN
            arrow = "📈"
        else:
            color = Fore.RED
            arrow = "📉"
        
        print(f"{color}{arrow} 24h Change: ${price_change:,.2f} ({price_change_pct:+.2f}%){Style.RESET_ALL}")
        
        print(f"\n{'='*70}")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
