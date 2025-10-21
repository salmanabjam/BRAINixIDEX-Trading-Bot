"""
BiX TradeBOT - Optimized Backtesting Module
============================================
High-performance backtesting with parallel processing and caching.

Features:
- Parallel data loading
- Indicator caching
- Batch processing
- Memory optimization
- Progress tracking

Author: SALMAN ThinkTank AI Core
Version: 2.0.0
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import lru_cache
import multiprocessing as mp
from typing import Dict, List, Optional, Tuple, Any
import hashlib

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

logger = get_logger(__name__, component='OptimizedBacktest')


class OptimizedBacktestEngine:
    """
    High-performance backtesting engine with optimizations:
    - Parallel data loading
    - Indicator caching
    - Batch processing
    - Memory-efficient operations
    """

    def __init__(self, use_ml=False, cache_indicators=True, n_jobs=-1):
        """
        Initialize optimized backtest engine.

        Args:
            use_ml (bool): Enable ML predictions
            cache_indicators (bool): Cache calculated indicators
            n_jobs (int): Number of parallel jobs (-1 = use all CPUs)
        """
        self.use_ml = use_ml
        self.cache_indicators = cache_indicators
        self.n_jobs = n_jobs if n_jobs > 0 else mp.cpu_count()
        self.results = None
        self.cache_dir = Path('data/indicator_cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"🚀 Optimized Backtest Engine initialized "
            f"(CPUs: {self.n_jobs}, Cache: {cache_indicators})"
        )

    def _get_cache_key(
        self,
        symbol: str,
        timeframe: str,
        start_date: str,
        end_date: str
    ) -> str:
        """Generate unique cache key for indicator data."""
        key_str = f"{symbol}_{timeframe}_{start_date}_{end_date}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _load_cached_indicators(self, cache_key: str) -> Optional[pd.DataFrame]:
        """Load cached indicators if available."""
        if not self.cache_indicators:
            return None

        cache_file = self.cache_dir / f"{cache_key}.parquet"
        if cache_file.exists():
            try:
                df = pd.read_parquet(cache_file)
                logger.info(
                    f"✅ Loaded {len(df)} rows from indicator cache"
                )
                return df
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                return None
        return None

    def _save_cached_indicators(
        self,
        cache_key: str,
        df: pd.DataFrame
    ) -> None:
        """Save indicators to cache."""
        if not self.cache_indicators:
            return

        cache_file = self.cache_dir / f"{cache_key}.parquet"
        try:
            df.to_parquet(cache_file, compression='snappy')
            logger.debug(f"💾 Saved indicators to cache: {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    def prepare_data(
        self,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        use_cache: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Fetch and prepare data with optimizations.

        Args:
            symbol: Trading pair
            timeframe: Timeframe
            start_date: Start date
            end_date: End date
            use_cache: Use cached indicators if available

        Returns:
            Prepared OHLCV data with indicators or None
        """
        try:
            logger.info("🔄 Preparing backtest data (optimized)...")

            symbol = symbol or Config.SYMBOL
            timeframe = timeframe or Config.TIMEFRAME
            start_date = start_date or Config.BACKTEST_START_DATE
            end_date = end_date or Config.BACKTEST_END_DATE

            # Check indicator cache
            cache_key = self._get_cache_key(
                symbol, timeframe, start_date, end_date
            )

            if use_cache:
                cached_df = self._load_cached_indicators(cache_key)
                if cached_df is not None:
                    return cached_df

            # Fetch raw data
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

            # Calculate indicators (optimized)
            df_indicators = self._calculate_indicators_optimized(df)

            if df_indicators is None or df_indicators.empty:
                logger.error("❌ Indicator calculation failed")
                return None

            # Add ML predictions if enabled
            if self.use_ml:
                df_indicators = self._add_ml_predictions(df_indicators)

            # Save to cache
            self._save_cached_indicators(cache_key, df_indicators)

            logger.info(
                f"✅ Data prepared: {len(df_indicators)} candles"
            )
            return df_indicators

        except Exception as e:
            logger.error(
                f"❌ Data preparation failed: {e}",
                exc_info=True
            )
            return None

    def _calculate_indicators_optimized(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate indicators with optimizations.
        Uses vectorized operations where possible.
        """
        logger.info("📊 Calculating indicators (optimized)...")

        # Use TechnicalIndicators but ensure vectorized operations
        indicators = TechnicalIndicators(df)
        df_indicators = indicators.calculate_all()

        return df_indicators

    def _add_ml_predictions(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """Add ML predictions with error handling."""
        try:
            logger.info("🤖 Generating ML predictions...")
            ml_engine = MLEngine()

            # Load or train model
            if not ml_engine.load_model():
                logger.warning("⚠️  Training new ML model...")
                train_result = ml_engine.train(df)
                if train_result is None:
                    logger.warning(
                        "⚠️  ML training failed, "
                        "continuing without ML"
                    )
                    self.use_ml = False
                    return df

            # Get predictions
            predictions_df = ml_engine.get_prediction_confidence(df)

            if predictions_df is not None and not predictions_df.empty:
                df['ml_prediction'] = predictions_df['prediction']
                df['ml_confidence'] = predictions_df['confidence']
                logger.info("✅ ML predictions added")
            else:
                logger.warning("⚠️  ML predictions empty")
                self.use_ml = False

        except Exception as e:
            logger.warning(f"⚠️  ML error: {e}")
            self.use_ml = False

        return df

    def run(
        self,
        data: Optional[pd.DataFrame] = None,
        strategy_class=None,
        cash: Optional[float] = None,
        commission: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Run backtest with optimized execution.

        Args:
            data: OHLCV data with indicators
            strategy_class: Strategy class to test
            cash: Initial capital
            commission: Commission per trade

        Returns:
            Backtest results dictionary
        """
        if data is None:
            data = self.prepare_data()
            if data is None:
                raise BotException("Failed to prepare data")

        strategy_class = strategy_class or HybridStrategy
        cash = cash or Config.INITIAL_CAPITAL
        commission = commission or Config.BACKTEST_COMMISSION

        logger.info("🚀 Running optimized backtest...")

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

    def run_parallel_backtests(
        self,
        symbols: List[str],
        timeframe: str = None,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """
        Run backtests for multiple symbols in parallel.

        Args:
            symbols: List of trading pairs
            timeframe: Timeframe for all backtests
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary of results by symbol
        """
        logger.info(
            f"🚀 Running parallel backtests for "
            f"{len(symbols)} symbols..."
        )

        def run_single_backtest(symbol: str) -> Tuple[str, Any]:
            """Run backtest for single symbol."""
            try:
                logger.info(f"Processing {symbol}...")
                data = self.prepare_data(
                    symbol=symbol,
                    timeframe=timeframe,
                    start_date=start_date,
                    end_date=end_date
                )
                if data is None:
                    return symbol, None

                results = self.run(data=data)
                return symbol, results
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                return symbol, None

        # Run in parallel
        results_dict = {}
        with ThreadPoolExecutor(max_workers=self.n_jobs) as executor:
            futures = [
                executor.submit(run_single_backtest, symbol)
                for symbol in symbols
            ]

            for future in futures:
                symbol, result = future.result()
                results_dict[symbol] = result

        logger.info("✅ Parallel backtests completed!")
        return results_dict

    def optimize(
        self,
        data: Optional[pd.DataFrame] = None,
        strategy_class=None,
        maximize: str = 'Return [%]',
        constraint=None,
        max_tries: int = None
    ) -> Dict[str, Any]:
        """
        Optimize strategy parameters with parallel processing.

        Args:
            data: OHLCV data
            strategy_class: Strategy class
            maximize: Metric to optimize
            constraint: Optimization constraint function
            max_tries: Maximum optimization iterations

        Returns:
            Best parameters and results
        """
        if data is None:
            data = self.prepare_data()
            if data is None:
                raise BotException("Failed to prepare data")

        strategy_class = strategy_class or HybridStrategy

        logger.info("🔬 Starting parallel optimization...")

        bt = Backtest(
            data,
            strategy_class,
            cash=Config.INITIAL_CAPITAL,
            commission=Config.BACKTEST_COMMISSION
        )

        # Define parameter ranges
        optimization_params = {
            'ema_fast': range(20, 60, 10),
            'ema_slow': range(150, 250, 25),
            'adx_threshold': range(20, 35, 5),
            'atr_stop_mult': [1.5, 2.0, 2.5, 3.0],
            'rr_ratio': [1.5, 2.0, 2.5, 3.0]
        }

        # Run optimization (backtesting.py uses multiprocessing internally)
        stats = bt.optimize(
            **optimization_params,
            maximize=maximize,
            constraint=constraint,
            max_tries=max_tries
        )

        logger.info("✅ Optimization complete!")
        return stats

    def get_summary(self) -> Optional[Dict[str, str]]:
        """Get backtest results summary."""
        if self.results is None:
            logger.warning("⚠️  No backtest results available")
            return None

        summary = {
            'Total Return [%]': f"{self.results['Return [%]']:.2f}%",
            'Sharpe Ratio': f"{self.results['Sharpe Ratio']:.2f}",
            'Max Drawdown [%]': (
                f"{self.results['Max. Drawdown [%]']:.2f}%"
            ),
            'Win Rate [%]': f"{self.results['Win Rate [%]']:.2f}%",
            'Total Trades': int(self.results['# Trades']),
            'Profit Factor': (
                f"{self.results.get('Profit Factor', 0):.2f}"
            ),
            'Avg Trade [%]': (
                f"{self.results.get('Avg. Trade [%]', 0):.2f}%"
            ),
            'Best Trade [%]': f"{self.results['Best Trade [%]']:.2f}%",
            'Worst Trade [%]': f"{self.results['Worst Trade [%]']:.2f}%",
            'Exposure Time [%]': (
                f"{self.results['Exposure Time [%]']:.2f}%"
            )
        }

        return summary

    def print_results(self) -> None:
        """Print formatted backtest results."""
        if self.results is None:
            print("❌ No results to display")
            return

        print("\n" + "=" * 60)
        print("📊 BiX TradeBOT Optimized Backtest Results")
        print("=" * 60)

        summary = self.get_summary()
        if summary:
            for key, value in summary.items():
                print(f"  {key:<25} {value}")

        print("=" * 60 + "\n")

    def save_results(
        self,
        filename: str = 'optimized_backtest_results.json'
    ) -> Optional[str]:
        """Save results to JSON file."""
        if self.results is None:
            logger.warning("⚠️  No results to save")
            return None

        output_dir = Path('results')
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / filename

        summary = self.get_summary()

        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"💾 Results saved to {output_path}")
        return str(output_path)

    def clear_cache(self) -> None:
        """Clear all cached indicators."""
        try:
            import shutil
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                logger.info("✅ Indicator cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")


if __name__ == "__main__":
    # Example usage
    import time

    # Test optimized engine
    engine = OptimizedBacktestEngine(
        use_ml=False,
        cache_indicators=True,
        n_jobs=-1
    )

    # Benchmark preparation
    start = time.time()
    data = engine.prepare_data()
    prep_time = time.time() - start

    # Run backtest
    start = time.time()
    results = engine.run(data=data)
    run_time = time.time() - start

    # Display results
    engine.print_results()

    print(f"\n⏱️  Performance:")
    print(f"  Data preparation: {prep_time:.2f}s")
    print(f"  Backtest execution: {run_time:.2f}s")
    print(f"  Total: {prep_time + run_time:.2f}s")

    # Save results
    engine.save_results()

    # Test parallel backtests
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
    start = time.time()
    parallel_results = engine.run_parallel_backtests(
        symbols=symbols,
        timeframe='1h'
    )
    parallel_time = time.time() - start

    print(f"\n⏱️  Parallel backtest for {len(symbols)} symbols:")
    print(f"  Total time: {parallel_time:.2f}s")
    print(f"  Average per symbol: {parallel_time/len(symbols):.2f}s")
