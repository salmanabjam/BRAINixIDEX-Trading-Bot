"""
BRAINixIDEX Trading Bot - Unified Entry Point
==============================================
Professional command-line interface for the trading bot.

Usage:
    python run.py analyze [--symbol BTCUSDT] [--timeframe 1h]
    python run.py backtest [--symbol BTCUSDT] [--timeframe 1h]
    python run.py train [--symbol BTCUSDT] [--timeframe 1h]
    python run.py price [--live]
    python run.py test [--ai-only]
    python run.py dashboard [--port 8080]

Author: SALMAN ThinkTank AI Core
Version: 2.0.0
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from colorama import init, Fore, Style

init(autoreset=True)


def print_banner():
    """Display application banner"""
    banner = f"""
{Fore.CYAN}{'='*70}
{'🚀 BRAINixIDEX Trading Bot v2.0':^70}
{'SALMAN ThinkTank AI Core':^70}
{'='*70}{Style.RESET_ALL}
"""
    print(banner)


def cmd_analyze(args):
    """Run live market analysis"""
    from core.bot import TradingBot
    
    print(f"\n{Fore.YELLOW}📡 Starting Live Analysis...{Style.RESET_ALL}\n")
    bot = TradingBot(symbol=args.symbol, timeframe=args.timeframe)
    bot.analyze()


def cmd_backtest(args):
    """Run strategy backtesting"""
    from analysis.backtester import StrategyBacktester
    
    print(f"\n{Fore.YELLOW}📊 Starting Backtesting...{Style.RESET_ALL}\n")
    backtester = StrategyBacktester()
    backtester.run(symbol=args.symbol, timeframe=args.timeframe)


def cmd_train(args):
    """Train machine learning models"""
    from core.ml_engine import MLEngine
    
    print(f"\n{Fore.YELLOW}🎓 Training ML Models...{Style.RESET_ALL}\n")
    engine = MLEngine(timeframe=args.timeframe)
    engine.train_all()


def cmd_price(args):
    """Show live price information"""
    if args.live:
        from scripts.price_monitor import main as monitor
        monitor()
    else:
        from scripts.price_checker import main as checker
        checker()


def cmd_test(args):
    """Run system tests"""
    if args.ai_only:
        from tests.test_models import main as test_ai
        test_ai()
    else:
        from tests.test_system import main as test_all
        test_all()


def cmd_dashboard(args):
    """Start web dashboard"""
    from ui.dashboard import app
    
    print(f"\n{Fore.YELLOW}🌐 Starting Dashboard on port {args.port}...{Style.RESET_ALL}\n")
    app.run(host='0.0.0.0', port=args.port, debug=False)


def main():
    """Main entry point"""
    print_banner()
    
    parser = argparse.ArgumentParser(
        description='BRAINixIDEX Trading Bot - Advanced AI Trading System',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run live market analysis')
    analyze_parser.add_argument('--symbol', default='BTCUSDT', help='Trading pair')
    analyze_parser.add_argument('--timeframe', default='1h', help='Timeframe')
    
    # Backtest command
    backtest_parser = subparsers.add_parser('backtest', help='Run strategy backtest')
    backtest_parser.add_argument('--symbol', default='BTCUSDT', help='Trading pair')
    backtest_parser.add_argument('--timeframe', default='1h', help='Timeframe')
    
    # Train command
    train_parser = subparsers.add_parser('train', help='Train ML models')
    train_parser.add_argument('--symbol', default='BTCUSDT', help='Trading pair')
    train_parser.add_argument('--timeframe', default='1h', help='Timeframe')
    
    # Price command
    price_parser = subparsers.add_parser('price', help='Show price information')
    price_parser.add_argument('--live', action='store_true', help='Live monitor mode')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('--ai-only', action='store_true', help='Test AI models only')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Start web dashboard')
    dashboard_parser.add_argument('--port', type=int, default=5000, help='Port number')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    commands = {
        'analyze': cmd_analyze,
        'backtest': cmd_backtest,
        'train': cmd_train,
        'price': cmd_price,
        'test': cmd_test,
        'dashboard': cmd_dashboard
    }
    
    try:
        commands[args.command](args)
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️  Interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == '__main__':
    main()
