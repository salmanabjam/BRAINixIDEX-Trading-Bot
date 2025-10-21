"""
BiX TradeBOT - Backtesting Module
==================================
Backtest trading strategies using historical data.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import pandas as pd
import json
from backtesting import Backtest
from core.strategy import HybridStrategy
from data.handler import DataHandler
from data.indicators import TechnicalIndicators
from core.ml_engine import MLEngine
from utils.config import Config
from utils.advanced_logger import get_logger
from utils.exceptions import (
    DataFetchException, ModelPredictionException, BotException
)

logger = get_logger(__name__, component='BacktestEngine')


class BacktestEngine:
    """
    Backtesting engine for BiX TradeBOT strategies.
    """

    def __init__(self, use_ml=False):
        """
        Initialize backtest engine.

        Args:
            use_ml (bool): Enable ML predictions in backtest
        """
        self.use_ml = use_ml
        self.results = None
        logger.info("📊 Backtest Engine initialized")

    def prepare_data(self, symbol=None, timeframe=None,
                     start_date=None, end_date=None):
        """
        Fetch and prepare data for backtesting.

        Args:
            symbol (str): Trading pair
            timeframe (str): Timeframe
            start_date (str): Start date
            end_date (str): End date

        Returns:
            pd.DataFrame: Prepared OHLCV data with indicators or None
        """
        try:
            logger.info("🔄 Preparing backtest data...")

            # Fetch data
            handler = DataHandler()
            df = handler.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date
            )

            if df is None or df.empty:
                logger.error("❌ No data fetched")
                return None

            # Calculate indicators
            indicators = TechnicalIndicators(df)
            df_indicators = indicators.calculate_all()

            if df_indicators is None or df_indicators.empty:
                logger.error("❌ Indicator calculation failed")
                return None

            # Add ML predictions if enabled
            if self.use_ml:
                try:
                    logger.info("🤖 Generating ML predictions...")
                    ml_engine = MLEngine()

                    # Try to load existing model or train new one
                    if not ml_engine.load_model():
                        logger.warning(
                            "⚠️  No trained model found. "
                            "Training new model..."
                        )
                        train_result = ml_engine.train(df_indicators)
                        if train_result is None:
                            logger.warning(
                                "⚠️  ML training failed, "
                                "continuing without ML"
                            )
                            self.use_ml = False
                            return df_indicators

                    # Get predictions with confidence
                    predictions_df = ml_engine.get_prediction_confidence(
                        df_indicators
                    )

                    if predictions_df is not None and not predictions_df.empty:
                        df_indicators['ml_prediction'] = (
                            predictions_df['prediction']
                        )
                        df_indicators['ml_confidence'] = (
                            predictions_df['confidence']
                        )
                        logger.info("✅ ML predictions added")
                    else:
                        logger.warning("⚠️  ML predictions empty")
                        self.use_ml = False

                except ModelPredictionException as e:
                    logger.warning(f"⚠️  ML prediction failed: {e}")
                    self.use_ml = False
                except Exception as e:
                    logger.warning(f"⚠️  ML error: {e}")
                    self.use_ml = False

            logger.info(f"✅ Data prepared: {len(df_indicators)} candles")
            return df_indicators

        except DataFetchException as e:
            logger.error(f"❌ Data fetch error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Data preparation failed: {e}", exc_info=True)
            return None

            df_indicators['ml_prediction'] = predictions_df['prediction']
            df_indicators['ml_confidence'] = predictions_df['confidence']

        # Rename columns for backtesting.py compatibility
        df_backtest = df_indicators.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        })

        logger.info(f"✅ Data prepared: {len(df_backtest)} candles")
        return df_backtest

    def run(self, data=None, strategy_class=None, cash=None,
            commission=None):
        """
        Run backtest.

        Args:
            data (pd.DataFrame): OHLCV data with indicators
            strategy_class: Strategy class to test
            cash (float): Initial capital
            commission (float): Commission per trade

        Returns:
            dict: Backtest results
        """
        # Default parameters
        if data is None:
            data = self.prepare_data()

        strategy_class = strategy_class or HybridStrategy
        cash = cash or Config.INITIAL_CAPITAL
        commission = commission or Config.BACKTEST_COMMISSION

        logger.info("🚀 Running backtest...")

        # Create backtest instance
        bt = Backtest(
            data,
            strategy_class,
            cash=cash,
            commission=commission,
            exclusive_orders=True
        )

        # Run backtest
        self.results = bt.run()

        logger.info("✅ Backtest completed!")
        return self.results

    def optimize(self, data=None, strategy_class=None,
                 maximize='Return [%]', constraint=None):
        """
        Optimize strategy parameters.

        Args:
            data (pd.DataFrame): OHLCV data
            strategy_class: Strategy class
            maximize (str): Metric to optimize
            constraint: Optimization constraint function

        Returns:
            dict: Best parameters and results
        """
        if data is None:
            data = self.prepare_data()

        strategy_class = strategy_class or HybridStrategy

        logger.info("🔬 Starting strategy optimization...")

        bt = Backtest(
            data,
            strategy_class,
            cash=Config.INITIAL_CAPITAL,
            commission=Config.BACKTEST_COMMISSION
        )

        # Define parameter ranges to optimize
        optimization_params = {
            'ema_fast': range(20, 60, 10),
            'ema_slow': range(150, 250, 25),
            'adx_threshold': range(20, 35, 5),
            'atr_stop_mult': [1.5, 2.0, 2.5, 3.0],
            'rr_ratio': [1.5, 2.0, 2.5, 3.0]
        }

        stats = bt.optimize(
            **optimization_params,
            maximize=maximize,
            constraint=constraint
        )

        logger.info("✅ Optimization complete!")
        return stats

    def get_summary(self):
        """
        Get backtest results summary.

        Returns:
            dict: Key performance metrics
        """
        if self.results is None:
            logger.warning("⚠️  No backtest results available")
            return None

        summary = {
            'Total Return [%]': f"{self.results['Return [%]']:.2f}%",
            'Sharpe Ratio': f"{self.results['Sharpe Ratio']:.2f}",
            'Max Drawdown [%]': f"{self.results['Max. Drawdown [%]']:.2f}%",
            'Win Rate [%]': f"{self.results['Win Rate [%]']:.2f}%",
            'Total Trades': int(self.results['# Trades']),
            'Profit Factor': f"{self.results.get('Profit Factor', 0):.2f}",
            'Avg Trade [%]': f"{self.results.get('Avg. Trade [%]', 0):.2f}%",
            'Best Trade [%]': f"{self.results['Best Trade [%]']:.2f}%",
            'Worst Trade [%]': f"{self.results['Worst Trade [%]']:.2f}%",
            'Exposure Time [%]': f"{self.results['Exposure Time [%]']:.2f}%"
        }

        return summary

    def print_results(self):
        """Print formatted backtest results"""
        if self.results is None:
            print("❌ No results to display")
            return

        print("\n" + "=" * 60)
        print("📊 BiX TradeBOT Backtest Results")
        print("=" * 60)

        summary = self.get_summary()
        for key, value in summary.items():
            print(f"  {key:<25} {value}")

        print("=" * 60 + "\n")

    def plot_results(self):
        """Plot backtest equity curve and trades"""
        if self.results is None:
            logger.warning("⚠️  No results to plot")
            return

        try:
            from backtesting import Backtest
            # The plot is generated automatically
            logger.info("📈 Opening interactive plot...")
            # Note: This will open in browser
        except Exception as e:
            logger.error(f"❌ Failed to plot: {e}")

    def save_results(self, filename='backtest_results.json'):
        """Save results to JSON file"""
        if self.results is None:
            logger.warning("⚠️  No results to save")
            return None

        output_path = f"results/{filename}"
        summary = self.get_summary()

        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"💾 Results saved to {output_path}")
        return output_path


if __name__ == "__main__":
    # Run backtest
    logger.setLevel(logging.INFO)

    # Initialize engine
    engine = BacktestEngine(use_ml=Config.ML_ENABLED)

    # Prepare data
    data = engine.prepare_data()

    # Run backtest
    results = engine.run(data=data)

    # Display results
    engine.print_results()

    # Save results
    engine.save_results()

    # Show detailed stats
    print("\n📋 Detailed Statistics:")
    print(results)
