"""
Real-Time Live Price Monitor
=============================
Display current Bitcoin price with automatic refresh.
"""

import requests
import time
from datetime import datetime
from colorama import init, Fore, Style
import os

init(autoreset=True)


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_live_price():
    """Get current Bitcoin price from Binance"""
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        return {
            'price': float(data['lastPrice']),
            'high_24h': float(data['highPrice']),
            'low_24h': float(data['lowPrice']),
            'volume': float(data['volume']),
            'price_change_pct': float(data['priceChangePercent'])
        }
    except Exception as e:
        return None


def display_price(data):
    """Display price information"""
    clear_screen()
    
    print("=" * 70)
    print(f"{Fore.CYAN}{'🔴 LIVE':<10} Bitcoin Price Monitor{Style.RESET_ALL}")
    print("=" * 70)
    print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if data:
        # Color based on 24h change
        if data['price_change_pct'] > 0:
            price_color = Fore.GREEN
            arrow = "📈"
        elif data['price_change_pct'] < 0:
            price_color = Fore.RED
            arrow = "📉"
        else:
            price_color = Fore.YELLOW
            arrow = "➡️"
        
        print(f"\n{price_color}{'='*70}{Style.RESET_ALL}")
        print(f"{price_color}💰 BTC/USDT: ${data['price']:,.2f}{Style.RESET_ALL}")
        print(f"{price_color}{'='*70}{Style.RESET_ALL}")
        
        print(f"\n📊 24h Statistics:")
        print(f"   {arrow} Change: {data['price_change_pct']:+.2f}%")
        print(f"   🔼 High:   ${data['high_24h']:,.2f}")
        print(f"   🔽 Low:    ${data['low_24h']:,.2f}")
        print(f"   📦 Volume: {data['volume']:,.2f} BTC")
        
    else:
        print(f"\n{Fore.RED}❌ Unable to fetch price{Style.RESET_ALL}")
    
    print("\n" + "=" * 70)
    print(f"{Fore.YELLOW}💡 Press Ctrl+C to stop{Style.RESET_ALL}")
    print("=" * 70)


def main():
    """Main loop"""
    print(f"{Fore.CYAN}Starting Live Price Monitor...{Style.RESET_ALL}")
    time.sleep(1)
    
    try:
        while True:
            data = get_live_price()
            display_price(data)
            time.sleep(5)  # Update every 5 seconds
            
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}📴 Stopped by user{Style.RESET_ALL}")
        print("=" * 70)


if __name__ == "__main__":
    main()
