# Backtesting Optimization Guide

## Overview

BiX TradeBOT now includes an **Optimized Backtest Engine** that provides significant performance improvements through:

- ⚡ **Parallel Processing** - Multi-threaded execution for multiple symbols
- 💾 **Indicator Caching** - Parquet-based caching for calculated indicators
- 🔄 **Batch Operations** - Efficient data loading and processing
- 📊 **Memory Optimization** - Reduced memory footprint
- 🎯 **Progress Tracking** - Better visibility into long-running operations

## Performance Improvements

Expected speedups:

| Operation | Standard | Optimized | Speedup |
|-----------|----------|-----------|---------|
| Data preparation (first run) | ~5s | ~5s | 1x |
| Data preparation (cached) | ~5s | **~0.5s** | **10x** |
| Multi-symbol backtest (3 symbols) | ~45s | **~20s** | **2.3x** |
| Full backtest execution | ~10s | **~6s** | **1.7x** |

*Note: Actual performance depends on system specs, data size, and network speed.*

## Quick Start

### Basic Usage

```python
from analysis.optimized_backtest import OptimizedBacktestEngine

# Create optimized engine
engine = OptimizedBacktestEngine(
    use_ml=False,
    cache_indicators=True,  # Enable caching
    n_jobs=-1               # Use all CPU cores
)

# Prepare data (will cache indicators)
data = engine.prepare_data(
    symbol='BTCUSDT',
    timeframe='1h',
    start_date='2025-01-01',
    end_date='2025-01-31'
)

# Run backtest
results = engine.run(data=data)

# Display results
engine.print_results()
```

### Parallel Multi-Symbol Backtests

```python
# Backtest multiple symbols in parallel
symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT']

results = engine.run_parallel_backtests(
    symbols=symbols,
    timeframe='1h',
    start_date='2025-01-01',
    end_date='2025-01-31'
)

# Results is a dictionary: {symbol: backtest_results}
for symbol, result in results.items():
    if result is not None:
        print(f"{symbol}: {result['Return [%]']:.2f}% return")
```

## Features

### 1. Indicator Caching

The optimized engine caches calculated indicators to disk using Parquet format for fast reloading.

**How it works:**
- Generates unique cache key from symbol, timeframe, and date range
- Saves indicators to `data/indicator_cache/`
- Automatically loads from cache on subsequent runs
- Provides ~10x speedup for repeated backtests

**Cache management:**

```python
# Clear all cached indicators
engine.clear_cache()

# Disable caching (if needed)
engine = OptimizedBacktestEngine(cache_indicators=False)

# Force fresh calculation (ignore cache)
data = engine.prepare_data(..., use_cache=False)
```

**Cache location:**
- Path: `data/indicator_cache/`
- Format: Parquet (compressed)
- Naming: MD5 hash of parameters

### 2. Parallel Processing

Use all CPU cores for multi-symbol backtests.

**Configuration:**

```python
# Auto-detect CPU count (default)
engine = OptimizedBacktestEngine(n_jobs=-1)

# Use specific number of cores
engine = OptimizedBacktestEngine(n_jobs=4)

# Disable parallel processing (use 1 core)
engine = OptimizedBacktestEngine(n_jobs=1)
```

**Best practices:**
- Use `n_jobs=-1` for maximum performance
- Leave some cores free for system operations
- Monitor CPU usage during execution

### 3. Memory Optimization

The optimized engine uses memory-efficient operations:

- Parquet compression for cache files
- Vectorized indicator calculations
- Efficient DataFrame operations
- Minimal data copying

**Memory usage comparison:**

| Engine | Peak Memory (1 month, 1h data) |
|--------|--------------------------------|
| Standard | ~250 MB |
| Optimized (first run) | ~250 MB |
| Optimized (cached) | **~50 MB** |

## Benchmarking

Use the included benchmark script to measure performance on your system:

```bash
python scripts/benchmark_backtest.py
```

This will compare:
- Data preparation time (with/without cache)
- Parallel vs sequential execution
- Memory usage
- Full backtest performance

**Sample output:**

```
📊 BENCHMARK: Data Preparation
======================================================================
🔵 Standard BacktestEngine:
  ⏱️  Time: 4.85s
  💾 Memory: 245.32 MB
  📊 Rows: 744

🟢 Optimized BacktestEngine (First run - no cache):
  ⏱️  Time: 4.92s
  💾 Memory: 248.15 MB
  📊 Rows: 744

🟢 Optimized BacktestEngine (Second run - with cache):
  ⏱️  Time: 0.45s
  💾 Memory: 52.18 MB
  📊 Rows: 744

📈 SUMMARY:
  Cache speedup: 10.93x faster
  Optimized vs Standard: 10.78x faster (with cache)
  Memory efficiency: 21.28% of standard
```

## Advanced Usage

### Custom Optimization Parameters

```python
# Optimize strategy parameters with parallel search
engine = OptimizedBacktestEngine()
data = engine.prepare_data()

best_params = engine.optimize(
    data=data,
    maximize='Sharpe Ratio',  # Optimize for Sharpe Ratio
    max_tries=100,            # Limit search iterations
    constraint=lambda p: p['Sharpe Ratio'] > 1.0  # Min Sharpe > 1
)

print(f"Best parameters: {best_params._strategy}")
```

### Batch Processing Multiple Timeframes

```python
symbols = ['BTCUSDT']
timeframes = ['15m', '1h', '4h']

for tf in timeframes:
    print(f"\n{'='*50}")
    print(f"Backtesting {tf} timeframe...")
    print(f"{'='*50}")
    
    data = engine.prepare_data(
        symbol='BTCUSDT',
        timeframe=tf,
        start_date='2025-01-01',
        end_date='2025-01-31'
    )
    
    results = engine.run(data=data)
    engine.print_results()
```

### Integration with Database

```python
from data.database import get_database

db = get_database()
engine = OptimizedBacktestEngine()

# Run backtest
data = engine.prepare_data()
results = engine.run(data=data)

# Store performance in database
db.update_daily_performance(
    date='2025-01-31',
    total_trades=results['# Trades'],
    winning_trades=results['# Trades'] * results['Win Rate [%]'] / 100,
    total_pnl=results['Return [%]'] * 10000 / 100,  # Assuming $10k capital
    win_rate=results['Win Rate [%]'],
    sharpe_ratio=results['Sharpe Ratio'],
    max_drawdown=results['Max. Drawdown [%]']
)
```

## Comparison: Standard vs Optimized

| Feature | Standard Engine | Optimized Engine |
|---------|----------------|------------------|
| Data caching | ❌ No | ✅ Yes (Parquet) |
| Parallel execution | ❌ No | ✅ Yes (multi-core) |
| Memory usage | High | **Low** |
| Cache management | ❌ No | ✅ Yes (auto) |
| Multi-symbol support | ❌ Sequential only | ✅ Parallel |
| Benchmark tools | ❌ No | ✅ Yes |
| Progress tracking | ⚠️ Basic | ✅ Detailed |

## When to Use Each Engine

### Use **Standard Engine** when:
- Running single backtest
- Testing/debugging
- Limited system resources
- No need for repeated runs

### Use **Optimized Engine** when:
- Running multiple backtests
- Testing multiple symbols
- Repeated backtests with same data
- Production/automated backtesting
- Need maximum performance

## Configuration

### Cache Directory

Default: `data/indicator_cache/`

Change cache location:

```python
engine = OptimizedBacktestEngine()
engine.cache_dir = Path('custom/cache/path')
engine.cache_dir.mkdir(parents=True, exist_ok=True)
```

### CPU Core Allocation

```python
import multiprocessing as mp

# Get system CPU count
cpu_count = mp.cpu_count()
print(f"System has {cpu_count} CPU cores")

# Use all cores
engine = OptimizedBacktestEngine(n_jobs=-1)

# Use half of cores
engine = OptimizedBacktestEngine(n_jobs=cpu_count // 2)

# Use specific count
engine = OptimizedBacktestEngine(n_jobs=4)
```

## Troubleshooting

### Cache Issues

**Problem:** Cache not working / slow performance

**Solutions:**
```python
# Clear corrupted cache
engine.clear_cache()

# Verify cache directory exists
print(f"Cache dir: {engine.cache_dir}")
print(f"Exists: {engine.cache_dir.exists()}")

# Check cache file size
import os
cache_files = list(engine.cache_dir.glob('*.parquet'))
for f in cache_files:
    size_mb = os.path.getsize(f) / (1024 * 1024)
    print(f"{f.name}: {size_mb:.2f} MB")
```

### Memory Issues

**Problem:** Out of memory errors

**Solutions:**
```python
# Reduce parallel workers
engine = OptimizedBacktestEngine(n_jobs=2)

# Process symbols sequentially instead of parallel
for symbol in symbols:
    data = engine.prepare_data(symbol=symbol)
    results = engine.run(data=data)
    # Process results immediately
    del data, results  # Free memory
```

### Performance Not Improved

**Problem:** Optimized engine not faster

**Checklist:**
1. ✅ Cache enabled? `cache_indicators=True`
2. ✅ Using cache? `use_cache=True` in prepare_data()
3. ✅ Second run? (First run builds cache)
4. ✅ Same parameters? (Different params = different cache)
5. ✅ Parallel enabled? `n_jobs=-1`

## Best Practices

1. **Enable caching by default**
   ```python
   engine = OptimizedBacktestEngine(cache_indicators=True)
   ```

2. **Use all CPU cores for parallel operations**
   ```python
   engine = OptimizedBacktestEngine(n_jobs=-1)
   ```

3. **Clear cache periodically**
   ```python
   # Clear weekly/monthly to prevent stale data
   engine.clear_cache()
   ```

4. **Monitor memory usage**
   ```python
   import tracemalloc
   tracemalloc.start()
   # ... run backtest ...
   current, peak = tracemalloc.get_traced_memory()
   print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
   tracemalloc.stop()
   ```

5. **Use batch processing for multiple symbols**
   ```python
   # Parallel processing is faster than loops
   results = engine.run_parallel_backtests(symbols=['BTC', 'ETH', 'ADA'])
   ```

## Migration Guide

### From Standard to Optimized

**Before:**
```python
from analysis.backtest import BacktestEngine

engine = BacktestEngine(use_ml=False)
data = engine.prepare_data()
results = engine.run(data=data)
engine.print_results()
```

**After:**
```python
from analysis.optimized_backtest import OptimizedBacktestEngine

engine = OptimizedBacktestEngine(
    use_ml=False,
    cache_indicators=True,
    n_jobs=-1
)
data = engine.prepare_data(use_cache=True)  # Added use_cache
results = engine.run(data=data)
engine.print_results()
```

**Changes:**
- Import from `optimized_backtest` instead of `backtest`
- Add `cache_indicators=True` and `n_jobs=-1`
- Add `use_cache=True` to `prepare_data()`
- All other API remains the same!

## Performance Tips

1. **Warm up the cache first**
   - Run once to build cache
   - Subsequent runs will be 10x faster

2. **Use SSD for cache storage**
   - Parquet I/O is disk-bound
   - SSD provides better performance

3. **Limit date ranges**
   - Smaller datasets = faster processing
   - Use specific date ranges instead of full history

4. **Disable ML when not needed**
   - ML predictions add overhead
   - Set `use_ml=False` for faster backtests

5. **Batch similar backtests**
   - Same timeframe/dates = cache reuse
   - Group backtests to maximize cache hits

---

**Author:** SALMAN ThinkTank AI Core  
**Version:** 2.0.0  
**Last Updated:** 2025-10-21
