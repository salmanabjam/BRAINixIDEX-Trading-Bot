"""
Tests for Database Manager
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data.database import DatabaseManager


class TestDatabaseManager:
    """Test database manager"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        db = DatabaseManager(db_path)
        yield db
        
        # Cleanup
        db.close()
        if os.path.exists(db_path):
            os.remove(db_path)
    
    def test_init(self, temp_db):
        """Test database initialization"""
        assert temp_db.db_path is not None
        assert Path(temp_db.db_path).exists()
    
    def test_add_trade(self, temp_db):
        """Test adding a trade"""
        trade_id = temp_db.add_trade(
            symbol='BTCUSDT',
            side='long',
            entry_price=50000.0,
            quantity=0.1,
            strategy='test_strategy'
        )
        
        assert trade_id > 0
    
    def test_close_trade(self, temp_db):
        """Test closing a trade"""
        # Add trade
        trade_id = temp_db.add_trade(
            symbol='BTCUSDT',
            side='long',
            entry_price=50000.0,
            quantity=0.1
        )
        
        # Close trade
        success = temp_db.close_trade(trade_id, exit_price=51000.0)
        assert success is True
        
        # Verify trade history
        history = temp_db.get_trade_history(limit=1)
        assert len(history) == 1
        assert history[0]['id'] == trade_id
        assert history[0]['status'] == 'closed'
        assert history[0]['pnl'] > 0
    
    def test_close_trade_pnl_calculation(self, temp_db):
        """Test P&L calculation for long and short"""
        # Long trade (profit)
        long_id = temp_db.add_trade(
            symbol='BTCUSDT',
            side='long',
            entry_price=50000.0,
            quantity=0.1
        )
        temp_db.close_trade(long_id, exit_price=51000.0)
        
        history = temp_db.get_trade_history(limit=1)
        assert history[0]['pnl'] == 100.0  # (51000 - 50000) * 0.1
        assert history[0]['pnl_percent'] == pytest.approx(2.0, rel=0.01)
        
        # Short trade (profit)
        short_id = temp_db.add_trade(
            symbol='ETHUSDT',
            side='short',
            entry_price=3000.0,
            quantity=1.0
        )
        temp_db.close_trade(short_id, exit_price=2900.0)
        
        history = temp_db.get_trade_history(symbol='ETHUSDT', limit=1)
        assert history[0]['pnl'] == 100.0  # (3000 - 2900) * 1.0
    
    def test_get_open_trades(self, temp_db):
        """Test getting open trades"""
        # Add some trades
        temp_db.add_trade(
            symbol='BTCUSDT',
            side='long',
            entry_price=50000.0,
            quantity=0.1
        )
        
        trade_id2 = temp_db.add_trade(
            symbol='ETHUSDT',
            side='short',
            entry_price=3000.0,
            quantity=1.0
        )
        
        # Close one
        temp_db.close_trade(trade_id2, exit_price=2900.0)
        
        # Get open trades
        open_trades = temp_db.get_open_trades()
        assert len(open_trades) == 1
        assert open_trades[0]['symbol'] == 'BTCUSDT'
        assert open_trades[0]['status'] == 'open'
    
    def test_get_open_trades_by_symbol(self, temp_db):
        """Test filtering open trades by symbol"""
        temp_db.add_trade('BTCUSDT', 'long', 50000.0, 0.1)
        temp_db.add_trade('ETHUSDT', 'long', 3000.0, 1.0)
        
        btc_trades = temp_db.get_open_trades(symbol='BTCUSDT')
        assert len(btc_trades) == 1
        assert btc_trades[0]['symbol'] == 'BTCUSDT'
    
    def test_get_trade_history(self, temp_db):
        """Test getting trade history"""
        # Add multiple trades
        for i in range(5):
            trade_id = temp_db.add_trade(
                symbol='BTCUSDT',
                side='long',
                entry_price=50000.0 + i * 100,
                quantity=0.1
            )
            temp_db.close_trade(trade_id, exit_price=51000.0 + i * 100)
        
        # Get history
        history = temp_db.get_trade_history(limit=10)
        assert len(history) == 5
        
        # Test limit
        limited = temp_db.get_trade_history(limit=3)
        assert len(limited) == 3
    
    def test_add_signal(self, temp_db):
        """Test adding trading signal"""
        signal_id = temp_db.add_signal(
            symbol='BTCUSDT',
            signal_type='buy',
            strength=0.8,
            price=50000.0,
            indicators={'rsi': 30, 'macd': 'bullish'},
            ml_prediction=0.75,
            confidence=0.85
        )
        
        assert signal_id > 0
    
    def test_mark_signal_executed(self, temp_db):
        """Test marking signal as executed"""
        signal_id = temp_db.add_signal(
            symbol='BTCUSDT',
            signal_type='buy',
            strength=0.8,
            price=50000.0
        )
        
        success = temp_db.mark_signal_executed(signal_id)
        assert success is True
    
    def test_get_recent_signals(self, temp_db):
        """Test getting recent signals"""
        # Add signals
        for i in range(5):
            temp_db.add_signal(
                symbol='BTCUSDT',
                signal_type='buy' if i % 2 == 0 else 'sell',
                strength=0.5 + i * 0.1,
                price=50000.0 + i * 100
            )
        
        # Get recent signals
        signals = temp_db.get_recent_signals(hours=24, limit=10)
        assert len(signals) == 5
        
        # Test symbol filter
        temp_db.add_signal('ETHUSDT', 'buy', 0.7, 3000.0)
        btc_signals = temp_db.get_recent_signals(symbol='BTCUSDT')
        assert all(s['symbol'] == 'BTCUSDT' for s in btc_signals)
    
    def test_update_daily_performance(self, temp_db):
        """Test updating daily performance"""
        # Add and close some trades
        for i in range(3):
            trade_id = temp_db.add_trade(
                symbol='BTCUSDT',
                side='long',
                entry_price=50000.0,
                quantity=0.1
            )
            # 2 winners, 1 loser
            exit_price = 51000.0 if i < 2 else 49000.0
            temp_db.close_trade(trade_id, exit_price=exit_price)
        
        # Update performance
        success = temp_db.update_daily_performance()
        assert success is True
        
        # Get summary
        summary = temp_db.get_performance_summary(days=1)
        assert summary['total_trades'] == 3
        assert summary['winning_trades'] == 2
        assert summary['losing_trades'] == 1
        assert summary['avg_win_rate'] == pytest.approx(66.67, rel=0.1)
    
    def test_get_performance_summary(self, temp_db):
        """Test getting performance summary"""
        summary = temp_db.get_performance_summary(days=30)
        
        assert 'total_trades' in summary
        assert 'total_pnl' in summary
        assert 'avg_win_rate' in summary
        assert summary['period_days'] == 30
    
    def test_register_cache_file(self, temp_db):
        """Test registering cache file"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            cache_path = f.name
            f.write(b"test data")
        
        try:
            success = temp_db.register_cache_file(
                file_path=cache_path,
                symbol='BTCUSDT',
                timeframe='1h',
                candle_count=100,
                start_date=datetime.now() - timedelta(days=7),
                end_date=datetime.now()
            )
            
            assert success is True
            
            # Get cache info
            info = temp_db.get_cache_info('BTCUSDT', '1h')
            assert info is not None
            assert info['candle_count'] == 100
            assert info['file_size'] > 0
        
        finally:
            if os.path.exists(cache_path):
                os.remove(cache_path)
    
    def test_log_websocket_stats(self, temp_db):
        """Test logging WebSocket statistics"""
        log_id = temp_db.log_websocket_stats(
            messages_received=1000,
            errors=2,
            reconnections=1,
            uptime=3600.0,
            symbols=['BTCUSDT', 'ETHUSDT']
        )
        
        assert log_id > 0
    
    def test_backup(self, temp_db):
        """Test database backup"""
        # Add some data
        temp_db.add_trade('BTCUSDT', 'long', 50000.0, 0.1)
        
        # Create backup
        backup_path = temp_db.backup()
        
        assert os.path.exists(backup_path)
        assert os.path.getsize(backup_path) > 0
        
        # Cleanup
        if os.path.exists(backup_path):
            os.remove(backup_path)
    
    def test_get_stats(self, temp_db):
        """Test getting database statistics"""
        # Add some data
        temp_db.add_trade('BTCUSDT', 'long', 50000.0, 0.1)
        temp_db.add_signal('BTCUSDT', 'buy', 0.8, 50000.0)
        
        stats = temp_db.get_stats()
        
        assert 'total_trades' in stats
        assert 'total_signals' in stats
        assert 'db_size_mb' in stats
        assert stats['total_trades'] >= 1
        assert stats['total_signals'] >= 1
    
    def test_thread_safety(self, temp_db):
        """Test thread-safe operations"""
        import threading
        
        def add_trades():
            for _ in range(10):
                temp_db.add_trade('BTCUSDT', 'long', 50000.0, 0.1)
        
        # Create multiple threads
        threads = [threading.Thread(target=add_trades) for _ in range(3)]
        
        # Start threads
        for t in threads:
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Verify all trades were added
        history = temp_db.get_trade_history(limit=100)
        assert len(history) == 30  # 3 threads * 10 trades each


class TestDatabaseIntegration:
    """Integration tests for database"""
    
    def test_complete_trading_workflow(self):
        """Test complete workflow: signal -> trade -> close -> performance"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        try:
            db = DatabaseManager(db_path)
            
            # 1. Generate signal
            signal_id = db.add_signal(
                symbol='BTCUSDT',
                signal_type='buy',
                strength=0.9,
                price=50000.0,
                confidence=0.85
            )
            
            # 2. Execute trade based on signal
            trade_id = db.add_trade(
                symbol='BTCUSDT',
                side='long',
                entry_price=50000.0,
                quantity=0.1,
                notes=f"Based on signal {signal_id}"
            )
            
            # 3. Mark signal as executed
            db.mark_signal_executed(signal_id)
            
            # 4. Close trade
            db.close_trade(trade_id, exit_price=51000.0)
            
            # 5. Update performance
            db.update_daily_performance()
            
            # 6. Verify everything
            signals = db.get_recent_signals(hours=1)
            assert len(signals) == 1
            assert signals[0]['executed'] == 1
            
            history = db.get_trade_history(limit=1)
            assert len(history) == 1
            assert history[0]['status'] == 'closed'
            assert history[0]['pnl'] > 0
            
            summary = db.get_performance_summary(days=1)
            assert summary['total_trades'] == 1
            assert summary['winning_trades'] == 1
            
            db.close()
        
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
