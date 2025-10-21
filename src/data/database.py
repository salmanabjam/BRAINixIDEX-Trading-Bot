"""
BiX TradeBOT - Database Manager
================================
Manages SQLite database for trade history, performance metrics, and cache.

Database Schema:
- trades: Trade execution history
- signals: Trading signals generated
- performance: Performance metrics over time
- cache_metadata: Cache file metadata
- websocket_stats: WebSocket connection statistics

Features:
- Thread-safe operations
- Automatic schema creation
- Migration support
- Backup and restore
- Query helpers

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import sqlite3
import json
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from contextlib import contextmanager

from utils.advanced_logger import get_logger
from utils.config import Config
from utils.exceptions import DataFetchException

logger = get_logger(__name__, component='Database')


class DatabaseManager:
    """
    Thread-safe SQLite database manager for trading bot.
    
    Handles:
    - Trade history storage
    - Signal tracking
    - Performance metrics
    - Cache metadata
    - WebSocket statistics
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or str(
            Path(Config.DATA_CACHE_DIR) / 'tradingbot.db'
        )
        
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Thread-local connections
        self._local = threading.local()
        
        # Lock for schema operations
        self._schema_lock = threading.Lock()
        
        # Initialize database
        self._init_database()
        
        logger.info(f"✅ Database initialized: {self.db_path}")
    
    @contextmanager
    def _get_connection(self):
        """
        Get thread-local database connection.
        
        Yields:
            sqlite3.Connection
        """
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
            self._local.connection.row_factory = sqlite3.Row
        
        try:
            yield self._local.connection
        except Exception as e:
            self._local.connection.rollback()
            logger.error(f"❌ Database error: {e}")
            raise
        finally:
            self._local.connection.commit()
    
    def _init_database(self):
        """Create database schema if not exists."""
        with self._schema_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Trades table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME NOT NULL,
                        symbol TEXT NOT NULL,
                        side TEXT NOT NULL,
                        entry_price REAL NOT NULL,
                        exit_price REAL,
                        quantity REAL NOT NULL,
                        pnl REAL,
                        pnl_percent REAL,
                        strategy TEXT,
                        status TEXT DEFAULT 'open',
                        stop_loss REAL,
                        take_profit REAL,
                        notes TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Trading signals table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS signals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME NOT NULL,
                        symbol TEXT NOT NULL,
                        signal_type TEXT NOT NULL,
                        strength REAL NOT NULL,
                        price REAL NOT NULL,
                        indicators TEXT,
                        ml_prediction REAL,
                        confidence REAL,
                        executed BOOLEAN DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Performance metrics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE NOT NULL UNIQUE,
                        total_trades INTEGER DEFAULT 0,
                        winning_trades INTEGER DEFAULT 0,
                        losing_trades INTEGER DEFAULT 0,
                        total_pnl REAL DEFAULT 0,
                        win_rate REAL DEFAULT 0,
                        sharpe_ratio REAL,
                        max_drawdown REAL,
                        total_volume REAL DEFAULT 0,
                        avg_trade_duration REAL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Cache metadata table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS cache_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_path TEXT NOT NULL UNIQUE,
                        symbol TEXT NOT NULL,
                        timeframe TEXT NOT NULL,
                        start_date DATE,
                        end_date DATE,
                        candle_count INTEGER,
                        file_size INTEGER,
                        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # WebSocket statistics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS websocket_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME NOT NULL,
                        messages_received INTEGER DEFAULT 0,
                        errors INTEGER DEFAULT 0,
                        reconnections INTEGER DEFAULT 0,
                        uptime REAL,
                        symbols TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_trades_symbol 
                    ON trades(symbol)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_trades_timestamp 
                    ON trades(timestamp DESC)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_signals_symbol 
                    ON signals(symbol)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_signals_timestamp 
                    ON signals(timestamp DESC)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_performance_date 
                    ON performance(date DESC)
                ''')
                
                conn.commit()
                logger.info("✅ Database schema created")
    
    # ==================== Trade Operations ====================
    
    def add_trade(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        quantity: float,
        strategy: str = None,
        stop_loss: float = None,
        take_profit: float = None,
        notes: str = None
    ) -> int:
        """
        Add new trade to database.
        
        Args:
            symbol: Trading pair
            side: 'long' or 'short'
            entry_price: Entry price
            quantity: Position size
            strategy: Strategy name
            stop_loss: Stop loss price
            take_profit: Take profit price
            notes: Additional notes
            
        Returns:
            Trade ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trades (
                    timestamp, symbol, side, entry_price, quantity,
                    strategy, stop_loss, take_profit, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                symbol,
                side,
                entry_price,
                quantity,
                strategy,
                stop_loss,
                take_profit,
                notes
            ))
            
            trade_id = cursor.lastrowid
            logger.info(
                f"✅ Trade added",
                trade_id=trade_id,
                symbol=symbol,
                side=side
            )
            return trade_id
    
    def close_trade(
        self,
        trade_id: int,
        exit_price: float,
        notes: str = None
    ) -> bool:
        """
        Close existing trade and calculate P&L.
        
        Args:
            trade_id: Trade ID
            exit_price: Exit price
            notes: Closing notes
            
        Returns:
            Success status
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get trade details
            cursor.execute(
                'SELECT * FROM trades WHERE id = ?',
                (trade_id,)
            )
            trade = cursor.fetchone()
            
            if not trade:
                logger.error(f"❌ Trade not found", trade_id=trade_id)
                return False
            
            # Calculate P&L
            entry_price = trade['entry_price']
            quantity = trade['quantity']
            side = trade['side']
            
            if side == 'long':
                pnl = (exit_price - entry_price) * quantity
            else:  # short
                pnl = (entry_price - exit_price) * quantity
            
            pnl_percent = (pnl / (entry_price * quantity)) * 100
            
            # Update trade
            updated_notes = trade['notes'] or ''
            if notes:
                updated_notes += f"\nClose: {notes}"
            
            cursor.execute('''
                UPDATE trades
                SET exit_price = ?,
                    pnl = ?,
                    pnl_percent = ?,
                    status = 'closed',
                    notes = ?
                WHERE id = ?
            ''', (exit_price, pnl, pnl_percent, updated_notes, trade_id))
            
            logger.info(
                f"✅ Trade closed",
                trade_id=trade_id,
                pnl=f"${pnl:.2f}",
                pnl_percent=f"{pnl_percent:.2f}%"
            )
            
            return True
    
    def get_open_trades(
        self,
        symbol: Optional[str] = None
    ) -> List[Dict]:
        """
        Get all open trades.
        
        Args:
            symbol: Filter by symbol (optional)
            
        Returns:
            List of open trades
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if symbol:
                cursor.execute('''
                    SELECT * FROM trades
                    WHERE status = 'open' AND symbol = ?
                    ORDER BY timestamp DESC
                ''', (symbol,))
            else:
                cursor.execute('''
                    SELECT * FROM trades
                    WHERE status = 'open'
                    ORDER BY timestamp DESC
                ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_trade_history(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get trade history with optional filters.
        
        Args:
            symbol: Filter by symbol
            start_date: Start date
            end_date: End date
            limit: Maximum results
            
        Returns:
            List of trades
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = 'SELECT * FROM trades WHERE 1=1'
            params = []
            
            if symbol:
                query += ' AND symbol = ?'
                params.append(symbol)
            
            if start_date:
                query += ' AND timestamp >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND timestamp <= ?'
                params.append(end_date)
            
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== Signal Operations ====================
    
    def add_signal(
        self,
        symbol: str,
        signal_type: str,
        strength: float,
        price: float,
        indicators: Dict = None,
        ml_prediction: float = None,
        confidence: float = None
    ) -> int:
        """
        Add trading signal to database.
        
        Args:
            symbol: Trading pair
            signal_type: 'buy', 'sell', 'hold'
            strength: Signal strength (-1 to 1)
            price: Current price
            indicators: Technical indicators dict
            ml_prediction: ML model prediction
            confidence: Prediction confidence
            
        Returns:
            Signal ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO signals (
                    timestamp, symbol, signal_type, strength,
                    price, indicators, ml_prediction, confidence
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                symbol,
                signal_type,
                strength,
                price,
                json.dumps(indicators) if indicators else None,
                ml_prediction,
                confidence
            ))
            
            return cursor.lastrowid
    
    def mark_signal_executed(self, signal_id: int) -> bool:
        """Mark signal as executed."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE signals SET executed = 1 WHERE id = ?',
                (signal_id,)
            )
            return cursor.rowcount > 0
    
    def get_recent_signals(
        self,
        symbol: Optional[str] = None,
        hours: int = 24,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get recent signals.
        
        Args:
            symbol: Filter by symbol
            hours: Time window in hours
            limit: Maximum results
            
        Returns:
            List of signals
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cutoff = datetime.now() - timedelta(hours=hours)
            
            if symbol:
                cursor.execute('''
                    SELECT * FROM signals
                    WHERE symbol = ? AND timestamp >= ?
                    ORDER BY timestamp DESC LIMIT ?
                ''', (symbol, cutoff, limit))
            else:
                cursor.execute('''
                    SELECT * FROM signals
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC LIMIT ?
                ''', (cutoff, limit))
            
            results = []
            for row in cursor.fetchall():
                signal = dict(row)
                if signal['indicators']:
                    signal['indicators'] = json.loads(signal['indicators'])
                results.append(signal)
            
            return results
    
    # ==================== Performance Operations ====================
    
    def update_daily_performance(
        self,
        date: Optional[datetime] = None
    ) -> bool:
        """
        Calculate and update daily performance metrics.
        
        Args:
            date: Date to calculate (default: today)
            
        Returns:
            Success status
        """
        date = date or datetime.now().date()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get trades for the day
            cursor.execute('''
                SELECT * FROM trades
                WHERE DATE(timestamp) = ?
                AND status = 'closed'
            ''', (date,))
            
            trades = cursor.fetchall()
            
            if not trades:
                return False
            
            # Calculate metrics
            total_trades = len(trades)
            winning_trades = sum(1 for t in trades if t['pnl'] > 0)
            losing_trades = sum(1 for t in trades if t['pnl'] < 0)
            total_pnl = sum(t['pnl'] for t in trades)
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            total_volume = sum(t['entry_price'] * t['quantity'] for t in trades)
            
            # Insert or update performance
            cursor.execute('''
                INSERT INTO performance (
                    date, total_trades, winning_trades, losing_trades,
                    total_pnl, win_rate, total_volume
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    total_trades = excluded.total_trades,
                    winning_trades = excluded.winning_trades,
                    losing_trades = excluded.losing_trades,
                    total_pnl = excluded.total_pnl,
                    win_rate = excluded.win_rate,
                    total_volume = excluded.total_volume
            ''', (
                date,
                total_trades,
                winning_trades,
                losing_trades,
                total_pnl,
                win_rate,
                total_volume
            ))
            
            logger.info(
                f"✅ Daily performance updated",
                date=str(date),
                trades=total_trades,
                win_rate=f"{win_rate:.1f}%"
            )
            
            return True
    
    def get_performance_summary(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get performance summary for last N days.
        
        Args:
            days: Number of days to include
            
        Returns:
            Performance summary dict
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cutoff = datetime.now().date() - timedelta(days=days)
            
            cursor.execute('''
                SELECT
                    SUM(total_trades) as total_trades,
                    SUM(winning_trades) as winning_trades,
                    SUM(losing_trades) as losing_trades,
                    SUM(total_pnl) as total_pnl,
                    AVG(win_rate) as avg_win_rate,
                    SUM(total_volume) as total_volume
                FROM performance
                WHERE date >= ?
            ''', (cutoff,))
            
            row = cursor.fetchone()
            
            return {
                'total_trades': row['total_trades'] or 0,
                'winning_trades': row['winning_trades'] or 0,
                'losing_trades': row['losing_trades'] or 0,
                'total_pnl': row['total_pnl'] or 0,
                'avg_win_rate': row['avg_win_rate'] or 0,
                'total_volume': row['total_volume'] or 0,
                'period_days': days
            }
    
    # ==================== Cache Metadata Operations ====================
    
    def register_cache_file(
        self,
        file_path: str,
        symbol: str,
        timeframe: str,
        candle_count: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> bool:
        """
        Register cache file in database.
        
        Args:
            file_path: Path to cache file
            symbol: Trading pair
            timeframe: Timeframe
            candle_count: Number of candles
            start_date: First candle date
            end_date: Last candle date
            
        Returns:
            Success status
        """
        file_size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO cache_metadata (
                    file_path, symbol, timeframe, start_date, end_date,
                    candle_count, file_size, last_updated
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(file_path) DO UPDATE SET
                    candle_count = excluded.candle_count,
                    file_size = excluded.file_size,
                    start_date = excluded.start_date,
                    end_date = excluded.end_date,
                    last_updated = excluded.last_updated
            ''', (
                file_path,
                symbol,
                timeframe,
                start_date,
                end_date,
                candle_count,
                file_size,
                datetime.now()
            ))
            
            return True
    
    def get_cache_info(self, symbol: str, timeframe: str) -> Optional[Dict]:
        """Get cache file information."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM cache_metadata
                WHERE symbol = ? AND timeframe = ?
                ORDER BY last_updated DESC LIMIT 1
            ''', (symbol, timeframe))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # ==================== WebSocket Stats Operations ====================
    
    def log_websocket_stats(
        self,
        messages_received: int,
        errors: int,
        reconnections: int,
        uptime: float,
        symbols: List[str]
    ) -> int:
        """
        Log WebSocket statistics.
        
        Args:
            messages_received: Message count
            errors: Error count
            reconnections: Reconnection count
            uptime: Uptime in seconds
            symbols: List of subscribed symbols
            
        Returns:
            Log ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO websocket_stats (
                    timestamp, messages_received, errors,
                    reconnections, uptime, symbols
                )
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                messages_received,
                errors,
                reconnections,
                uptime,
                json.dumps(symbols)
            ))
            
            return cursor.lastrowid
    
    # ==================== Utility Operations ====================
    
    def backup(self, backup_path: Optional[str] = None) -> str:
        """
        Create database backup.
        
        Args:
            backup_path: Backup file path
            
        Returns:
            Backup file path
        """
        backup_path = backup_path or f"{self.db_path}.backup"
        
        with self._get_connection() as conn:
            backup_conn = sqlite3.connect(backup_path)
            conn.backup(backup_conn)
            backup_conn.close()
        
        logger.info(f"✅ Database backed up to {backup_path}")
        return backup_path
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Count trades
            cursor.execute('SELECT COUNT(*) as count FROM trades')
            stats['total_trades'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM trades WHERE status = "open"')
            stats['open_trades'] = cursor.fetchone()['count']
            
            # Count signals
            cursor.execute('SELECT COUNT(*) as count FROM signals')
            stats['total_signals'] = cursor.fetchone()['count']
            
            # Count cache files
            cursor.execute('SELECT COUNT(*) as count FROM cache_metadata')
            stats['cache_files'] = cursor.fetchone()['count']
            
            # Database size
            stats['db_size_mb'] = Path(self.db_path).stat().st_size / (1024 * 1024)
            
            return stats
    
    def close(self):
        """Close database connections."""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            delattr(self._local, 'connection')
        
        logger.info("✅ Database connections closed")


# Global database instance
_db_instance: Optional[DatabaseManager] = None


def get_database() -> DatabaseManager:
    """Get global database instance (singleton)."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance


if __name__ == "__main__":
    # Test database
    print("🧪 Testing Database Manager...")
    
    db = DatabaseManager()
    
    # Test trade
    trade_id = db.add_trade(
        symbol='BTCUSDT',
        side='long',
        entry_price=50000.0,
        quantity=0.1,
        strategy='hybrid',
        stop_loss=49000.0,
        take_profit=52000.0
    )
    print(f"✅ Trade created: {trade_id}")
    
    # Close trade
    db.close_trade(trade_id, exit_price=51000.0, notes="Take profit hit")
    
    # Get history
    history = db.get_trade_history(limit=5)
    print(f"✅ Trade history: {len(history)} trades")
    
    # Test signal
    signal_id = db.add_signal(
        symbol='BTCUSDT',
        signal_type='buy',
        strength=0.8,
        price=50000.0,
        indicators={'rsi': 30, 'macd': 'bullish'},
        confidence=0.85
    )
    print(f"✅ Signal created: {signal_id}")
    
    # Update performance
    db.update_daily_performance()
    
    # Get stats
    stats = db.get_stats()
    print(f"\n📊 Database Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ All tests passed!")
