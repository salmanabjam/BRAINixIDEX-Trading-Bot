"""
Tests for Portfolio Analytics
==============================
"""

import pytest
from datetime import datetime
from src.analytics.portfolio import Portfolio, Position


class TestPosition:
    """Test Position class."""
    
    def test_position_value(self):
        """Test position value calculation."""
        pos = Position(
            symbol='BTCUSDT',
            quantity=0.1,
            entry_price=50000,
            current_price=51000,
            entry_time=datetime.now()
        )
        assert pos.value == 5100
    
    def test_position_pnl(self):
        """Test P&L calculation."""
        pos = Position(
            symbol='BTCUSDT',
            quantity=0.1,
            entry_price=50000,
            current_price=51000,
            entry_time=datetime.now()
        )
        assert pos.pnl == 100
    
    def test_position_pnl_percent(self):
        """Test P&L percentage."""
        pos = Position(
            symbol='BTCUSDT',
            quantity=0.1,
            entry_price=50000,
            current_price=51000,
            entry_time=datetime.now()
        )
        assert pos.pnl_percent == pytest.approx(2.0, rel=0.01)


class TestPortfolio:
    """Test Portfolio class."""
    
    def test_init(self):
        """Test portfolio initialization."""
        portfolio = Portfolio(10000)
        assert portfolio.initial_balance == 10000
        assert portfolio.cash == 10000
        assert len(portfolio.positions) == 0
    
    def test_add_position(self):
        """Test adding position."""
        portfolio = Portfolio(10000)
        pos = Position(
            symbol='BTCUSDT',
            quantity=0.1,
            entry_price=50000,
            current_price=50000,
            entry_time=datetime.now()
        )
        portfolio.add_position(pos)
        
        assert len(portfolio.positions) == 1
        assert portfolio.cash == 5000
    
    def test_add_position_insufficient_funds(self):
        """Test insufficient funds."""
        portfolio = Portfolio(1000)
        pos = Position(
            symbol='BTCUSDT',
            quantity=0.1,
            entry_price=50000,
            current_price=50000,
            entry_time=datetime.now()
        )
        with pytest.raises(ValueError):
            portfolio.add_position(pos)
    
    def test_close_position(self):
        """Test closing position."""
        portfolio = Portfolio(10000)
        pos = Position(
            symbol='BTCUSDT',
            quantity=0.1,
            entry_price=50000,
            current_price=50000,
            entry_time=datetime.now()
        )
        portfolio.add_position(pos)
        portfolio.close_position('BTCUSDT', 51000)
        
        assert len(portfolio.positions) == 0
        assert portfolio.cash == 10100
    
    def test_get_total_value(self):
        """Test total value calculation."""
        portfolio = Portfolio(10000)
        pos = Position(
            symbol='BTCUSDT',
            quantity=0.1,
            entry_price=50000,
            current_price=51000,
            entry_time=datetime.now()
        )
        portfolio.add_position(pos)
        
        total = portfolio.get_total_value()
        assert total == 10100
    
    def test_get_total_pnl(self):
        """Test total P&L."""
        portfolio = Portfolio(10000)
        pos = Position(
            symbol='BTCUSDT',
            quantity=0.1,
            entry_price=50000,
            current_price=51000,
            entry_time=datetime.now()
        )
        portfolio.add_position(pos)
        
        pnl = portfolio.get_total_pnl()
        assert pnl == 100
    
    def test_get_distribution(self):
        """Test asset distribution."""
        portfolio = Portfolio(10000)
        pos = Position(
            symbol='BTCUSDT',
            quantity=0.1,
            entry_price=50000,
            current_price=50000,
            entry_time=datetime.now()
        )
        portfolio.add_position(pos)
        
        dist = portfolio.get_distribution()
        assert 'CASH' in dist
        assert 'BTCUSDT' in dist
        assert dist['CASH'] == pytest.approx(50.0, rel=0.01)
    
    def test_get_performance_summary(self):
        """Test performance summary."""
        portfolio = Portfolio(10000)
        summary = portfolio.get_performance_summary()
        
        assert 'initial_balance' in summary
        assert 'current_value' in summary
        assert 'total_pnl' in summary
        assert summary['initial_balance'] == 10000
    
    def test_get_positions_df(self):
        """Test positions DataFrame."""
        portfolio = Portfolio(10000)
        pos = Position(
            symbol='BTCUSDT',
            quantity=0.1,
            entry_price=50000,
            current_price=51000,
            entry_time=datetime.now()
        )
        portfolio.add_position(pos)
        
        df = portfolio.get_positions_df()
        assert len(df) == 1
        assert 'Symbol' in df.columns
        assert df.iloc[0]['Symbol'] == 'BTCUSDT'
