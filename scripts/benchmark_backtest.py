"""
Backtest Performance Benchmark
===============================
Compare performance of standard vs optimized backtest engines.

Run this script to measure:
- Data preparation time
- Indicator calculation time
- Cache effectiveness
- Parallel processing speedup
- Memory usage

Usage:
    python scripts/benchmark_backtest.py
"""

import time
import tracemalloc
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from analysis.backtest import BacktestEngine
from analysis.optimized_backtest import OptimizedBacktestEngine
from utils.advanced_logger import get_logger

logger = get_logger(__name__, component='Benchmark')


def format_time(seconds: float) -> str:
    """Format time in human-readable format."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}m {secs:.1f}s"


def format_memory(bytes_val: int) -> str:
    """Format memory in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.2f} TB"


def benchmark_data_preparation():
    """Benchmark data preparation with and without cache."""
    print("\n" + "="*70)
    print("📊 BENCHMARK: Data Preparation")
    print("="*70)

    params = {
        'symbol': 'BTCUSDT',
        'timeframe': '1h',
        'start_date': '2025-01-01',
        'end_date': '2025-01-31'
    }

    # Standard engine
    print("\n🔵 Standard BacktestEngine:")
    standard = BacktestEngine(use_ml=False)
    
    tracemalloc.start()
    start = time.time()
    data_standard = standard.prepare_data(**params)
    time_standard = time.time() - start
    current, peak_standard = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"  ⏱️  Time: {format_time(time_standard)}")
    print(f"  💾 Memory: {format_memory(peak_standard)}")
    if data_standard is not None:
        print(f"  📊 Rows: {len(data_standard):,}")

    # Optimized engine - First run (no cache)
    print("\n🟢 Optimized BacktestEngine (First run - no cache):")
    optimized = OptimizedBacktestEngine(
        use_ml=False,
        cache_indicators=True,
        n_jobs=-1
    )
    optimized.clear_cache()  # Ensure clean start

    tracemalloc.start()
    start = time.time()
    data_opt1 = optimized.prepare_data(**params, use_cache=True)
    time_opt1 = time.time() - start
    current, peak_opt1 = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"  ⏱️  Time: {format_time(time_opt1)}")
    print(f"  💾 Memory: {format_memory(peak_opt1)}")
    if data_opt1 is not None:
        print(f"  📊 Rows: {len(data_opt1):,}")

    # Optimized engine - Second run (with cache)
    print("\n🟢 Optimized BacktestEngine (Second run - with cache):")
    
    tracemalloc.start()
    start = time.time()
    data_opt2 = optimized.prepare_data(**params, use_cache=True)
    time_opt2 = time.time() - start
    current, peak_opt2 = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"  ⏱️  Time: {format_time(time_opt2)}")
    print(f"  💾 Memory: {format_memory(peak_opt2)}")
    if data_opt2 is not None:
        print(f"  📊 Rows: {len(data_opt2):,}")

    # Summary
    print("\n📈 SUMMARY:")
    print(f"  Cache speedup: {time_opt1/time_opt2:.2f}x faster")
    if time_standard > 0 and time_opt2 > 0:
        print(
            f"  Optimized vs Standard: "
            f"{time_standard/time_opt2:.2f}x faster (with cache)"
        )
    print(
        f"  Memory efficiency: "
        f"{peak_opt2/peak_standard:.2%} of standard"
    )

    # Cleanup
    optimized.clear_cache()


def benchmark_parallel_backtests():
    """Benchmark parallel backtest execution."""
    print("\n" + "="*70)
    print("🔄 BENCHMARK: Parallel vs Sequential Backtests")
    print("="*70)

    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
    params = {
        'timeframe': '1h',
        'start_date': '2025-01-01',
        'end_date': '2025-01-10'
    }

    optimized = OptimizedBacktestEngine(
        use_ml=False,
        cache_indicators=True,
        n_jobs=-1
    )
    optimized.clear_cache()

    # Sequential execution
    print(f"\n🔵 Sequential execution ({len(symbols)} symbols):")
    start = time.time()
    sequential_results = {}
    for symbol in symbols:
        print(f"  Processing {symbol}...")
        data = optimized.prepare_data(symbol=symbol, **params)
        if data is not None:
            result = optimized.run(data=data)
            sequential_results[symbol] = result
    time_sequential = time.time() - start

    print(f"  ⏱️  Total time: {format_time(time_sequential)}")
    print(
        f"  ⏱️  Avg per symbol: "
        f"{format_time(time_sequential/len(symbols))}"
    )

    # Parallel execution
    print(f"\n🟢 Parallel execution ({len(symbols)} symbols):")
    start = time.time()
    parallel_results = optimized.run_parallel_backtests(
        symbols=symbols,
        **params
    )
    time_parallel = time.time() - start

    print(f"  ⏱️  Total time: {format_time(time_parallel)}")
    print(
        f"  ⏱️  Avg per symbol: "
        f"{format_time(time_parallel/len(symbols))}"
    )

    # Summary
    print("\n📈 SUMMARY:")
    speedup = time_sequential / time_parallel if time_parallel > 0 else 0
    print(f"  Speedup: {speedup:.2f}x faster")
    print(f"  Time saved: {format_time(time_sequential - time_parallel)}")
    efficiency = (speedup / optimized.n_jobs) * 100
    print(
        f"  Parallel efficiency: {efficiency:.1f}% "
        f"(using {optimized.n_jobs} CPUs)"
    )

    # Cleanup
    optimized.clear_cache()


def benchmark_full_backtest():
    """Benchmark complete backtest execution."""
    print("\n" + "="*70)
    print("🚀 BENCHMARK: Full Backtest Execution")
    print("="*70)

    params = {
        'symbol': 'BTCUSDT',
        'timeframe': '1h',
        'start_date': '2025-01-01',
        'end_date': '2025-01-31'
    }

    # Standard engine
    print("\n🔵 Standard BacktestEngine:")
    standard = BacktestEngine(use_ml=False)
    
    start = time.time()
    data = standard.prepare_data(**params)
    if data is not None:
        results = standard.run(data=data)
        time_standard = time.time() - start
        
        print(f"  ⏱️  Total time: {format_time(time_standard)}")
        if results is not None:
            print(f"  📊 Trades: {results['# Trades']}")
            print(f"  💰 Return: {results['Return [%]']:.2f}%")

    # Optimized engine
    print("\n🟢 Optimized BacktestEngine:")
    optimized = OptimizedBacktestEngine(
        use_ml=False,
        cache_indicators=True,
        n_jobs=-1
    )
    optimized.clear_cache()

    start = time.time()
    data = optimized.prepare_data(**params, use_cache=True)
    if data is not None:
        results = optimized.run(data=data)
        time_opt = time.time() - start
        
        print(f"  ⏱️  Total time: {format_time(time_opt)}")
        if results is not None:
            print(f"  📊 Trades: {results['# Trades']}")
            print(f"  💰 Return: {results['Return [%]']:.2f}%")

    # Summary
    print("\n📈 SUMMARY:")
    if time_standard > 0 and time_opt > 0:
        print(f"  Overall speedup: {time_standard/time_opt:.2f}x faster")
        print(
            f"  Time saved: "
            f"{format_time(time_standard - time_opt)}"
        )

    # Cleanup
    optimized.clear_cache()


def main():
    """Run all benchmarks."""
    print("\n" + "="*70)
    print("⚡ BiX TradeBOT - Backtest Performance Benchmark")
    print("="*70)
    print("\nThis will compare:")
    print("  • Standard vs Optimized backtest engines")
    print("  • Cache effectiveness")
    print("  • Parallel processing performance")
    print("  • Memory usage")
    print("\n⚠️  Note: This requires Binance API access")
    print("="*70)

    input("\nPress Enter to start benchmarks...")

    try:
        # Run benchmarks
        benchmark_data_preparation()
        benchmark_parallel_backtests()
        benchmark_full_backtest()

        print("\n" + "="*70)
        print("✅ All benchmarks completed!")
        print("="*70)

    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
