"""
Tests for Optimized Backtest Engine
====================================
Tests for parallel processing, caching, and performance improvements.
"""

import pytest
import pandas as pd
import time
from pathlib import Path
import shutil

from analysis.optimized_backtest import OptimizedBacktestEngine
from utils.config import Config


class TestOptimizedBacktestEngine:
    """Test suite for optimized backtest engine."""

    @pytest.fixture
    def engine(self):
        """Create engine instance."""
        engine = OptimizedBacktestEngine(
            use_ml=False,
            cache_indicators=True,
            n_jobs=2
        )
        yield engine
        # Cleanup
        engine.clear_cache()

    @pytest.fixture
    def sample_data(self):
        """Create sample OHLCV data."""
        dates = pd.date_range(start='2025-01-01', periods=100, freq='1h')
        df = pd.DataFrame({
            'timestamp': dates,
            'open': 50000 + pd.Series(range(100)) * 10,
            'high': 50100 + pd.Series(range(100)) * 10,
            'low': 49900 + pd.Series(range(100)) * 10,
            'close': 50000 + pd.Series(range(100)) * 10,
            'volume': 1000 + pd.Series(range(100))
        })
        df.set_index('timestamp', inplace=True)
        return df

    def test_init(self, engine):
        """Test engine initialization."""
        assert engine.use_ml is False
        assert engine.cache_indicators is True
        assert engine.n_jobs == 2
        assert engine.results is None
        assert engine.cache_dir.exists()

    def test_cache_key_generation(self, engine):
        """Test unique cache key generation."""
        key1 = engine._get_cache_key(
            'BTCUSDT', '1h', '2025-01-01', '2025-10-21'
        )
        key2 = engine._get_cache_key(
            'BTCUSDT', '1h', '2025-01-01', '2025-10-21'
        )
        key3 = engine._get_cache_key(
            'ETHUSDT', '1h', '2025-01-01', '2025-10-21'
        )

        # Same params = same key
        assert key1 == key2
        # Different params = different key
        assert key1 != key3
        # Should be MD5 hash (32 chars)
        assert len(key1) == 32

    def test_cache_save_and_load(self, engine, sample_data):
        """Test indicator caching."""
        cache_key = 'test_cache_key'

        # Save to cache
        engine._save_cached_indicators(cache_key, sample_data)

        # Load from cache
        loaded = engine._load_cached_indicators(cache_key)

        assert loaded is not None
        assert len(loaded) == len(sample_data)
        pd.testing.assert_frame_equal(loaded, sample_data)

    def test_cache_disabled(self):
        """Test engine with caching disabled."""
        engine = OptimizedBacktestEngine(cache_indicators=False)

        df = pd.DataFrame({'a': [1, 2, 3]})
        engine._save_cached_indicators('test', df)

        loaded = engine._load_cached_indicators('test')
        assert loaded is None

    def test_prepare_data_with_cache(self, engine):
        """Test data preparation uses cache."""
        # Skip if no API access
        pytest.skip("Requires Binance API access")

        # First call - should fetch and cache
        start = time.time()
        data1 = engine.prepare_data(
            symbol='BTCUSDT',
            timeframe='1h',
            start_date='2025-01-01',
            end_date='2025-01-10',
            use_cache=True
        )
        time1 = time.time() - start

        # Second call - should load from cache (faster)
        start = time.time()
        data2 = engine.prepare_data(
            symbol='BTCUSDT',
            timeframe='1h',
            start_date='2025-01-01',
            end_date='2025-01-10',
            use_cache=True
        )
        time2 = time.time() - start

        assert data1 is not None
        assert data2 is not None
        assert len(data1) == len(data2)
        # Cache should be faster (at least 2x)
        assert time2 < time1 / 2

    def test_clear_cache(self, engine, sample_data):
        """Test cache clearing."""
        cache_key = 'test_clear'
        engine._save_cached_indicators(cache_key, sample_data)

        # Verify cache exists
        cache_file = engine.cache_dir / f"{cache_key}.parquet"
        assert cache_file.exists()

        # Clear cache
        engine.clear_cache()

        # Verify cache is cleared
        assert not cache_file.exists()
        assert engine.cache_dir.exists()  # Directory still exists

    def test_run_backtest(self, engine):
        """Test backtest execution."""
        pytest.skip("Requires prepared data with indicators")

        data = engine.prepare_data(
            symbol='BTCUSDT',
            timeframe='1h',
            start_date='2025-01-01',
            end_date='2025-01-31'
        )

        if data is not None:
            results = engine.run(data=data)
            assert results is not None
            assert '# Trades' in results
            assert 'Return [%]' in results

    def test_get_summary(self, engine):
        """Test summary generation."""
        # No results yet
        summary = engine.get_summary()
        assert summary is None

    def test_print_results_no_data(self, engine, capsys):
        """Test printing when no results."""
        engine.print_results()
        captured = capsys.readouterr()
        assert "No results" in captured.out

    def test_save_results_no_data(self, engine):
        """Test saving when no results."""
        result = engine.save_results()
        assert result is None

    def test_parallel_backtests(self, engine):
        """Test parallel backtest execution."""
        pytest.skip("Requires Binance API access")

        symbols = ['BTCUSDT', 'ETHUSDT']
        results = engine.run_parallel_backtests(
            symbols=symbols,
            timeframe='1h',
            start_date='2025-01-01',
            end_date='2025-01-10'
        )

        assert len(results) == len(symbols)
        for symbol in symbols:
            assert symbol in results

    def test_n_jobs_auto_detect(self):
        """Test automatic CPU count detection."""
        engine = OptimizedBacktestEngine(n_jobs=-1)
        assert engine.n_jobs > 0  # Should detect system CPUs

    def test_n_jobs_custom(self):
        """Test custom CPU count."""
        engine = OptimizedBacktestEngine(n_jobs=4)
        assert engine.n_jobs == 4


class TestBacktestPerformance:
    """Performance comparison tests."""

    @pytest.fixture
    def optimized_engine(self):
        """Optimized engine."""
        engine = OptimizedBacktestEngine(
            use_ml=False,
            cache_indicators=True,
            n_jobs=-1
        )
        yield engine
        engine.clear_cache()

    def test_caching_improves_speed(self, optimized_engine):
        """Test that caching improves performance."""
        pytest.skip("Requires Binance API - manual benchmark test")

        params = {
            'symbol': 'BTCUSDT',
            'timeframe': '1h',
            'start_date': '2025-01-01',
            'end_date': '2025-01-31'
        }

        # First run - no cache
        start = time.time()
        data1 = optimized_engine.prepare_data(**params, use_cache=True)
        time_no_cache = time.time() - start

        # Second run - with cache
        start = time.time()
        data2 = optimized_engine.prepare_data(**params, use_cache=True)
        time_with_cache = time.time() - start

        print(f"\nPerformance comparison:")
        print(f"  No cache: {time_no_cache:.2f}s")
        print(f"  With cache: {time_with_cache:.2f}s")
        print(f"  Speedup: {time_no_cache/time_with_cache:.2f}x")

        # Cache should provide at least 2x speedup
        assert time_with_cache < time_no_cache / 2

    def test_parallel_vs_sequential(self, optimized_engine):
        """Test parallel execution is faster."""
        pytest.skip("Requires Binance API - manual benchmark test")

        symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']

        # Parallel execution
        start = time.time()
        parallel_results = optimized_engine.run_parallel_backtests(
            symbols=symbols,
            timeframe='1h',
            start_date='2025-01-01',
            end_date='2025-01-10'
        )
        parallel_time = time.time() - start

        # Sequential execution (for comparison)
        start = time.time()
        sequential_results = {}
        for symbol in symbols:
            data = optimized_engine.prepare_data(
                symbol=symbol,
                timeframe='1h',
                start_date='2025-01-01',
                end_date='2025-01-10'
            )
            if data is not None:
                result = optimized_engine.run(data=data)
                sequential_results[symbol] = result
        sequential_time = time.time() - start

        print(f"\nParallel vs Sequential:")
        print(f"  Sequential: {sequential_time:.2f}s")
        print(f"  Parallel: {parallel_time:.2f}s")
        print(f"  Speedup: {sequential_time/parallel_time:.2f}x")

        # Parallel should be faster
        assert parallel_time < sequential_time


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
