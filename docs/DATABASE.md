# Database Integration Guide

## Overview

BiX TradeBOT uses SQLite for persistent storage of trading data, signals, performance metrics, cache metadata, and WebSocket statistics.

## Database Location

Default: `data/trading.db`

## Schema

### 1. Trades Table
Stores all trade execution history.

```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,           -- 'long' or 'short'
    entry_price REAL NOT NULL,
    exit_price REAL,
    quantity REAL NOT NULL,
    pnl REAL,                      -- Profit/Loss in USD
    pnl_percent REAL,              -- P&L percentage
    strategy TEXT,                 -- Strategy name
    status TEXT DEFAULT 'open',    -- 'open' or 'closed'
    stop_loss REAL,
    take_profit REAL,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

**Indexes:**
- `idx_trades_symbol` - Fast symbol filtering
- `idx_trades_timestamp` - Time-based queries

### 2. Signals Table
Records all trading signals generated.

```sql
CREATE TABLE signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    symbol TEXT NOT NULL,
    signal_type TEXT NOT NULL,     -- 'buy', 'sell', 'hold'
    strength INTEGER NOT NULL,     -- Signal strength (0-5)
    price REAL NOT NULL,
    indicators TEXT,               -- JSON: Technical indicators
    ml_prediction REAL,            -- ML model prediction
    confidence REAL,               -- ML confidence score
    executed INTEGER DEFAULT 0,    -- 1 if signal was executed
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

**Indexes:**
- `idx_signals_symbol` - Fast symbol filtering
- `idx_signals_timestamp` - Time-based queries

### 3. Performance Table
Daily aggregated performance metrics.

```sql
CREATE TABLE performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT UNIQUE NOT NULL,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    total_pnl REAL DEFAULT 0,
    win_rate REAL DEFAULT 0,
    sharpe_ratio REAL DEFAULT 0,
    max_drawdown REAL DEFAULT 0,
    total_volume REAL DEFAULT 0,
    avg_trade_duration REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

**Index:**
- `idx_performance_date` - Fast date lookups

### 4. Cache Metadata Table
Tracks all cache files for efficient data management.

```sql
CREATE TABLE cache_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    candle_count INTEGER,
    file_size INTEGER,
    last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

### 5. WebSocket Stats Table
Logs WebSocket connection statistics.

```sql
CREATE TABLE websocket_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    messages_received INTEGER DEFAULT 0,
    errors INTEGER DEFAULT 0,
    reconnections INTEGER DEFAULT 0,
    uptime REAL DEFAULT 0,
    symbols TEXT,                  -- JSON: List of symbols
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

## Usage Examples

### Getting Database Instance

```python
from data.database import get_database

db = get_database()
```

### Adding a Trade

```python
trade_id = db.add_trade(
    symbol='BTCUSDT',
    side='long',
    entry_price=50000.0,
    quantity=0.1,
    stop_loss=49000.0,
    take_profit=52000.0,
    strategy='HybridStrategy'
)
```

### Closing a Trade

```python
db.close_trade(
    trade_id=1,
    exit_price=51500.0,
    notes='Take profit hit'
)
# Automatically calculates P&L and P&L percentage
```

### Recording Signals

```python
db.add_signal(
    symbol='BTCUSDT',
    signal_type='buy',
    strength=4,
    price=50000.0,
    indicators={
        'rsi': 35.5,
        'ema_fast': 49800.0,
        'ema_slow': 48500.0,
        'adx': 28.0
    },
    ml_prediction=1,
    confidence=0.85
)
```

### Marking Signal as Executed

```python
db.mark_signal_executed(signal_id=1)
```

### Getting Recent Signals

```python
# Last 10 signals
signals = db.get_recent_signals(limit=10)

# Last 10 signals for specific symbol
signals = db.get_recent_signals(symbol='BTCUSDT', limit=10)
```

### Updating Daily Performance

```python
db.update_daily_performance(
    date='2025-10-21',
    total_trades=15,
    winning_trades=10,
    losing_trades=5,
    total_pnl=1250.50,
    win_rate=66.67,
    sharpe_ratio=1.85,
    max_drawdown=-3.2,
    total_volume=750000.0,
    avg_trade_duration=125.5
)
```

### Getting Performance Summary

```python
# Last 30 days
summary = db.get_performance_summary(days=30)

print(f"Win Rate: {summary['win_rate']:.2f}%")
print(f"Total P&L: ${summary['total_pnl']:,.2f}")
print(f"Sharpe Ratio: {summary['sharpe_ratio']:.2f}")
```

### Registering Cache Files

```python
db.register_cache_file(
    file_path='data/cache/BTCUSDT_1h_2024-01-01_2025-10-20.csv',
    symbol='BTCUSDT',
    timeframe='1h',
    start_date='2024-01-01',
    end_date='2025-10-20',
    candle_count=8500,
    file_size=1245678
)
```

### Getting Cache Info

```python
# All cache files
cache_files = db.get_cache_info()

# Specific symbol
cache_files = db.get_cache_info(symbol='BTCUSDT')
```

### Logging WebSocket Stats

```python
db.log_websocket_stats(
    messages_received=15678,
    errors=3,
    reconnections=1,
    uptime=3600.5,
    symbols=['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
)
```

### Getting Open Trades

```python
# All open trades
open_trades = db.get_open_trades()

# Open trades for specific symbol
open_trades = db.get_open_trades(symbol='BTCUSDT')
```

### Getting Trade History

```python
# All trades
history = db.get_trade_history()

# Specific symbol
history = db.get_trade_history(symbol='BTCUSDT')

# Date range
history = db.get_trade_history(
    start_date='2025-01-01',
    end_date='2025-10-21'
)

# Limit results
history = db.get_trade_history(limit=50)
```

### Backing Up Database

```python
backup_path = db.backup('backup_20251021.db')
print(f"Database backed up to: {backup_path}")
```

### Getting Database Statistics

```python
stats = db.get_stats()
print(f"Total Trades: {stats['total_trades']}")
print(f"Open Trades: {stats['open_trades']}")
print(f"Signals: {stats['signals']}")
print(f"Cache Files: {stats['cache_files']}")
```

## Automatic Integration

The database is automatically integrated with core components:

### Strategy
When `SimpleHybridStrategy.generate_signal()` is called, signals are automatically logged to the database.

### RiskManager
- `open_position()` automatically logs trades to database
- `close_position()` automatically updates trades with exit price and P&L

### DataHandler
- `fetch_ohlcv()` automatically registers cache files in database
- Cache metadata is updated on every cache write

### WebSocket
- `get_stats()` automatically logs WebSocket statistics to database

## Thread Safety

The DatabaseManager uses thread-local connections and locks to ensure thread-safe operations:

```python
# Safe for multi-threaded access
from concurrent.futures import ThreadPoolExecutor

def worker():
    db = get_database()
    db.add_signal(...)

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(worker) for _ in range(100)]
```

## Best Practices

1. **Use Singleton Pattern**: Always use `get_database()` to get the instance
2. **Backup Regularly**: Schedule periodic database backups
3. **Monitor Size**: Check database size and clean old data if needed
4. **Use Indexes**: All key fields are indexed for fast queries
5. **Thread Safety**: The database handles multi-threaded access automatically

## Backup Strategy

```python
from datetime import datetime
from data.database import get_database

def daily_backup():
    db = get_database()
    filename = f"backup_{datetime.now().strftime('%Y%m%d')}.db"
    db.backup(filename)
    print(f"✅ Backup created: {filename}")

# Schedule this function daily
```

## Database Size Management

```python
# Check database file size
import os
db_path = 'data/trading.db'
size_mb = os.path.getsize(db_path) / (1024 * 1024)
print(f"Database size: {size_mb:.2f} MB")

# Clean old data (example: keep last 90 days)
# You can implement custom cleanup logic
```

## Migration from Cache Files

If you have existing cache files, they will be automatically registered when accessed:

```python
from data.handler import DataHandler

dh = DataHandler()
df = dh.fetch_ohlcv(
    symbol='BTCUSDT',
    timeframe='1h',
    use_cache=True
)
# Cache metadata is automatically registered in database
```

## Troubleshooting

### Database Locked Error
If you get "database is locked" errors:
- Ensure all connections are closed properly
- Check for long-running transactions
- Use `db.close()` when done

### Performance Issues
- Check if indexes exist: `db.get_stats()`
- Optimize queries with proper WHERE clauses
- Limit result sets with LIMIT

### Corruption
If database is corrupted:
1. Restore from backup: `cp backup_20251021.db data/trading.db`
2. If no backup, delete and recreate: Schema auto-creates on first use

## Future Enhancements

Planned features:
- PostgreSQL support for production
- Database migration tools
- Advanced analytics queries
- Performance optimization
- Automated cleanup policies

---

**Author:** SALMAN ThinkTank AI Core  
**Version:** 1.0.0  
**Last Updated:** 2025-10-21
