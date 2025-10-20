"""
BiX TradeBOT - Main Orchestration Script
=========================================
Main entry point for the trading bot.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
import argparse

from utils.config import Config
from data.handler import DataHandler
from data.indicators import TechnicalIndicators
from core.ml_engine import MLEngine
from core.strategy import SimpleHybridStrategy
from core.risk_manager import RiskManager
from analysis.backtest import BacktestEngine

# Setup logging
log_file = f"logs/bix_tradebot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class BiXTradeBOT:
    """
    Main trading bot orchestrator.
    Coordinates all modules for live trading or backtesting.
    """

    def __init__(self, mode='backtest'):
        """
        Initialize BiX TradeBOT.

        Args:
            mode (str): 'backtest', 'live', or 'paper'
        """
        self.mode = mode
        logger.info("=" * 60)
        logger.info("🚀 BiX TradeBOT v1.0 - SALMAN ThinkTank AI Core")
        logger.info("=" * 60)
        logger.info(f"Mode: {mode.upper()}")

        # Validate configuration
        try:
            Config.validate()
        except ValueError as e:
            logger.error(f"❌ Configuration error: {e}")
            sys.exit(1)

        # Initialize modules
        self.data_handler = DataHandler()
        self.ml_engine = MLEngine() if Config.ML_ENABLED else None
        self.strategy = SimpleHybridStrategy(use_ml=Config.ML_ENABLED)
        self.risk_manager = RiskManager()

        logger.info("✅ All modules initialized")

    def run_backtest(self, plot_results=True):
        """
        Run backtesting mode.

        Args:
            plot_results (bool): Show interactive plot
        """
        logger.info("\n" + "=" * 60)
        logger.info("📊 Starting Backtest Mode")
        logger.info("=" * 60)

        engine = BacktestEngine(use_ml=Config.ML_ENABLED)

        # Prepare data
        data = engine.prepare_data(
            symbol=Config.SYMBOL,
            timeframe=Config.TIMEFRAME,
            start_date=Config.BACKTEST_START_DATE,
            end_date=Config.BACKTEST_END_DATE
        )

        # Run backtest
        results = engine.run(data=data)

        # Display results
        engine.print_results()

        # Save results
        engine.save_results(
            f"backtest_{Config.SYMBOL}_{Config.TIMEFRAME}_"
            f"{datetime.now().strftime('%Y%m%d')}.json"
        )

        if plot_results:
            logger.info("📈 To view interactive plot, use backtest.py directly")

        return results

    def run_live_analysis(self):
        """
        Run live market analysis (no actual trading).
        Shows current signals and recommendations.
        """
        logger.info("\n" + "=" * 60)
        logger.info("📡 Live Market Analysis")
        logger.info("=" * 60)

        # Fetch latest data
        df = self.data_handler.fetch_ohlcv(
            symbol=Config.SYMBOL,
            timeframe=Config.TIMEFRAME,
            limit=500
        )

        # Calculate indicators
        indicators = TechnicalIndicators(df)
        df_indicators = indicators.calculate_all()

        # Get latest signals
        latest_signals = indicators.get_latest_signals()

        # ML prediction
        ml_pred = None
        ml_conf = None
        if self.ml_engine:
            # Load or train model
            if not self.ml_engine.load_model():
                logger.warning("⚠️  Training ML model (this may take a minute)...")
                self.ml_engine.train(df_indicators)

            # Get prediction - use full dataframe if tail is empty
            df_for_pred = df_indicators if len(df_indicators) > 0 else df_indicators
            if len(df_for_pred) > 0:
                predictions = self.ml_engine.get_prediction_confidence(
                    df_for_pred
                )
                ml_pred = predictions['prediction'].iloc[-1]
                ml_conf = predictions['confidence'].iloc[-1]
            else:
                logger.warning("⚠️  No data available for ML prediction")

        # Generate signal
        signal = self.strategy.generate_signal(
            latest_signals,
            ml_prediction=ml_pred,
            ml_confidence=ml_conf
        )

        # Display analysis
        self._print_analysis(latest_signals, signal, ml_pred, ml_conf)

        # Calculate position size if signal is strong
        if signal['action'] in ['BUY', 'SELL']:
            direction = 'long' if signal['action'] == 'BUY' else 'short'
            position_info = self.risk_manager.calculate_position_size(
                entry_price=latest_signals['close'],
                atr=latest_signals['atr'],
                direction=direction
            )
            self._print_position_info(position_info, direction)

        return signal

    def _print_analysis(self, indicators, signal, ml_pred, ml_conf):
        """Print formatted market analysis"""
        print("\n" + "=" * 60)
        print(f"📊 Market Analysis - {Config.SYMBOL} ({Config.TIMEFRAME})")
        print("=" * 60)

        print(f"\n💰 Current Price: ${indicators['close']:,.2f}")
        print(f"📅 Timestamp: {indicators['timestamp']}")

        print("\n📈 Technical Indicators:")
        print(f"  EMA Fast (50):  ${indicators['ema_fast']:,.2f}")
        print(f"  EMA Slow (200): ${indicators['ema_slow']:,.2f}")
        print(f"  RSI:            {indicators['rsi']:.2f}")
        print(f"  ATR:            ${indicators['atr']:,.2f}")
        print(f"  ADX:            {indicators['adx']:.2f}")

        print("\n🎯 Strategy Signals:")
        signal_emoji = {1: "🟢", -1: "🔴", 0: "⚪"}
        print(f"  Trend:     {signal_emoji[indicators['trend_signal']]} "
              f"{indicators['trend_signal']}")
        print(f"  Breakout:  {signal_emoji[indicators['breakout_signal']]} "
              f"{indicators['breakout_signal']}")
        print(f"  Pullback:  {signal_emoji[indicators['pullback_signal']]} "
              f"{indicators['pullback_signal']}")
        print(f"  Combined:  {indicators['combined_signal']}")

        if ml_pred is not None:
            print(f"\n🤖 ML Prediction:")
            pred_text = {1: "BULLISH 🟢", -1: "BEARISH 🔴", 0: "NEUTRAL ⚪"}
            print(f"  Signal:     {pred_text.get(ml_pred, 'UNKNOWN')}")
            print(f"  Confidence: {ml_conf:.2%}")

        print(f"\n🚦 RECOMMENDATION:")
        action_emoji = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '⚪'}
        print(f"  Action:   {action_emoji[signal['action']]} "
              f"{signal['action']}")
        print(f"  Strength: {'⭐' * signal['strength']}")
        print(f"  Reason:   {signal['reason']}")
        print("=" * 60 + "\n")

    def _print_position_info(self, position_info, direction):
        """Print position sizing information"""
        print("💼 Suggested Position:")
        print(f"  Direction:    {direction.upper()}")
        print(f"  Size:         {position_info['size']} units")
        print(f"  Value:        ${position_info['value']:,.2f}")
        print(f"  Stop Loss:    ${position_info['stop_loss']:,.2f}")
        print(f"  Take Profit:  ${position_info['take_profit']:,.2f}")
        print(f"  Risk Amount:  ${position_info['risk_amount']:,.2f} "
              f"({Config.RISK_PER_TRADE*100}%)")
        print("=" * 60 + "\n")

    def run_training(self):
        """Train or retrain ML model"""
        logger.info("\n" + "=" * 60)
        logger.info("🎓 ML Model Training")
        logger.info("=" * 60)

        if not self.ml_engine:
            logger.error("❌ ML is disabled in config")
            return

        # Fetch data
        df = self.data_handler.fetch_ohlcv(limit=2000)

        # Calculate indicators
        indicators = TechnicalIndicators(df)
        df_indicators = indicators.calculate_all()

        # Train
        metrics = self.ml_engine.train(df_indicators)

        print("\n✅ Training Complete!")
        print(f"  Accuracy:      {metrics['accuracy']:.4f}")
        print(f"  Training Size: {metrics['train_size']}")
        print(f"  Test Size:     {metrics['test_size']}")
        print(f"  Features:      {metrics['features']}")
        print("=" * 60 + "\n")


def main():
    """Main entry point with CLI argument parsing"""
    parser = argparse.ArgumentParser(
        description='BiX TradeBOT - AI-Powered Automated Trading Bot'
    )

    parser.add_argument(
        'mode',
        choices=['backtest', 'analyze', 'train'],
        help='Operation mode: backtest, analyze (live), or train (ML model)'
    )

    parser.add_argument(
        '--symbol',
        type=str,
        help=f'Trading pair (default: {Config.SYMBOL})'
    )

    parser.add_argument(
        '--timeframe',
        type=str,
        help=f'Timeframe (default: {Config.TIMEFRAME})'
    )

    args = parser.parse_args()

    # Override config if specified
    if args.symbol:
        Config.SYMBOL = args.symbol
    if args.timeframe:
        Config.TIMEFRAME = args.timeframe

    # Initialize bot
    bot = BiXTradeBOT(mode=args.mode)

    # Execute based on mode
    if args.mode == 'backtest':
        bot.run_backtest()
    elif args.mode == 'analyze':
        bot.run_live_analysis()
    elif args.mode == 'train':
        bot.run_training()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⚠️  Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
