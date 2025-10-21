"""
BiX TradeBOT - Main Orchestration Script
=========================================
Main entry point for the trading bot.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import sys
from pathlib import Path
from datetime import datetime
import argparse

from utils.config import Config
from utils.advanced_logger import get_logger, setup_audit_logger
from utils.exceptions import (
    BotException, DataFetchException, ModelPredictionException,
    StrategyException, RiskManagementException
)
from data.handler import DataHandler
from data.indicators import TechnicalIndicators
from core.ml_engine import MLEngine
from core.strategy import SimpleHybridStrategy
from core.risk_manager import RiskManager
from analysis.backtest import BacktestEngine

# Setup main logger
logger = get_logger('BiXTradeBOT', component='MainBot')
audit_logger = setup_audit_logger()


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
        
        Returns:
            dict: Backtest results or None on error
        """
        logger.info("\n" + "=" * 60)
        logger.info("📊 Starting Backtest Mode")
        logger.info("=" * 60)

        try:
            engine = BacktestEngine(use_ml=Config.ML_ENABLED)

            # Prepare data
            data = engine.prepare_data(
                symbol=Config.SYMBOL,
                timeframe=Config.TIMEFRAME,
                start_date=Config.BACKTEST_START_DATE,
                end_date=Config.BACKTEST_END_DATE
            )

            if data is None or data.empty:
                logger.error("❌ No data available for backtesting")
                return None

            # Run backtest
            results = engine.run(data=data)

            if results is None:
                logger.error("❌ Backtest execution failed")
                return None

            # Display results
            engine.print_results()

            # Save results
            try:
                filename = (
                    f"backtest_{Config.SYMBOL}_{Config.TIMEFRAME}_"
                    f"{datetime.now().strftime('%Y%m%d')}.json"
                )
                engine.save_results(filename)
                logger.info(f"💾 Results saved to {filename}")
            except Exception as e:
                logger.warning(f"⚠️  Failed to save results: {e}")

            if plot_results:
                logger.info("📈 To view interactive plot, use backtest.py")

            audit_logger.info("Backtest completed", extra={
                'symbol': Config.SYMBOL,
                'timeframe': Config.TIMEFRAME,
                'total_trades': results.get('total_trades', 0)
            })

            return results

        except DataFetchException as e:
            logger.error(f"❌ Data fetch error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Backtest failed: {e}", exc_info=True)
            return None

    def run_live_analysis(self):
        """
        Run live market analysis (no actual trading).
        Shows current signals and recommendations.
        
        Returns:
            dict: Signal information or None on error
        """
        logger.info("\n" + "=" * 60)
        logger.info("📡 Live Market Analysis")
        logger.info("=" * 60)

        try:
            # Fetch latest data
            df = self.data_handler.fetch_ohlcv(
                symbol=Config.SYMBOL,
                timeframe=Config.TIMEFRAME,
                limit=500
            )

            if df is None or df.empty:
                logger.error("❌ No market data available")
                return None

            # Calculate indicators
            indicators = TechnicalIndicators(df)
            df_indicators = indicators.calculate_all()

            if df_indicators is None or df_indicators.empty:
                logger.error("❌ Failed to calculate indicators")
                return None

            # Get latest signals
            latest_signals = indicators.get_latest_signals()

            if latest_signals is None:
                logger.error("❌ Failed to get latest signals")
                return None

            # ML prediction
            ml_pred = None
            ml_conf = None
            if self.ml_engine:
                try:
                    # Load or train model
                    if not self.ml_engine.load_model():
                        logger.warning(
                            "⚠️  Training ML model "
                            "(this may take a minute)..."
                        )
                        self.ml_engine.train(df_indicators)

                    # Get prediction
                    if len(df_indicators) > 0:
                        predictions = self.ml_engine.get_prediction_confidence(
                            df_indicators
                        )
                        if predictions is not None and not predictions.empty:
                            ml_pred = predictions['prediction'].iloc[-1]
                            ml_conf = predictions['confidence'].iloc[-1]
                        else:
                            logger.warning(
                                "⚠️  ML prediction returned empty"
                            )
                    else:
                        logger.warning("⚠️  No data for ML prediction")

                except ModelPredictionException as e:
                    logger.warning(f"⚠️  ML prediction failed: {e}")
                except Exception as e:
                    logger.warning(f"⚠️  ML error: {e}")

            # Generate signal
            try:
                signal = self.strategy.generate_signal(
                    latest_signals,
                    ml_prediction=ml_pred,
                    ml_confidence=ml_conf
                )
            except StrategyException as e:
                logger.error(f"❌ Strategy error: {e}")
                return None

            # Display analysis
            self._print_analysis(latest_signals, signal, ml_pred, ml_conf)

            # Calculate position size if signal is strong
            if signal['action'] in ['BUY', 'SELL']:
                try:
                    direction = 'long' if signal['action'] == 'BUY' else 'short'
                    position_info = self.risk_manager.calculate_position_size(
                        entry_price=latest_signals['close'],
                        atr=latest_signals['atr'],
                        direction=direction
                    )
                    self._print_position_info(position_info, direction)
                except RiskManagementException as e:
                    logger.warning(f"⚠️  Position sizing failed: {e}")

            audit_logger.info("Live analysis completed", extra={
                'symbol': Config.SYMBOL,
                'action': signal.get('action', 'UNKNOWN'),
                'strength': signal.get('strength', 0)
            })

            return signal

        except DataFetchException as e:
            logger.error(f"❌ Data fetch error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Live analysis failed: {e}", exc_info=True)
            return None

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
        """
        Train or retrain ML model
        
        Returns:
            dict: Training metrics or None on error
        """
        logger.info("\n" + "=" * 60)
        logger.info("🎓 ML Model Training")
        logger.info("=" * 60)

        if not self.ml_engine:
            logger.error("❌ ML is disabled in config")
            return None

        try:
            # Fetch data
            df = self.data_handler.fetch_ohlcv(limit=2000)

            if df is None or df.empty:
                logger.error("❌ No data available for training")
                return None

            # Calculate indicators
            indicators = TechnicalIndicators(df)
            df_indicators = indicators.calculate_all()

            if df_indicators is None or df_indicators.empty:
                logger.error("❌ Failed to calculate indicators")
                return None

            # Train
            metrics = self.ml_engine.train(df_indicators)

            if metrics is None:
                logger.error("❌ Training failed")
                return None

            print("\n✅ Training Complete!")
            print(f"  Accuracy:      {metrics.get('accuracy', 0):.4f}")
            print(f"  Training Size: {metrics.get('train_size', 0)}")
            print(f"  Test Size:     {metrics.get('test_size', 0)}")
            print(f"  Features:      {metrics.get('features', 0)}")
            print("=" * 60 + "\n")

            audit_logger.info("ML model trained", extra={
                'accuracy': metrics.get('accuracy', 0),
                'features': metrics.get('features', 0)
            })

            return metrics

        except DataFetchException as e:
            logger.error(f"❌ Data fetch error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Training failed: {e}", exc_info=True)
            return None


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
