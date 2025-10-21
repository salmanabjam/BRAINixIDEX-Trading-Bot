"""
Tests for Strategy Comparison
==============================
"""

import pytest
from src.analytics.strategy_comparison import StrategyComparison


class TestStrategyComparison:
    """Test StrategyComparison class."""
    
    def test_init(self):
        """Test initialization."""
        comp = StrategyComparison()
        assert len(comp.strategies) == 0
    
    def test_add_strategy(self):
        """Test adding strategy."""
        comp = StrategyComparison()
        comp.add_strategy('Test', {
            'total_return_pct': 25.0,
            'win_rate': 60.0
        })
        assert 'Test' in comp.strategies
    
    def test_get_comparison_table(self):
        """Test comparison table generation."""
        comp = StrategyComparison()
        comp.add_strategy('A', {
            'total_return_pct': 25.0,
            'win_rate': 60.0,
            'sharpe_ratio': 1.5
        })
        comp.add_strategy('B', {
            'total_return_pct': 20.0,
            'win_rate': 65.0,
            'sharpe_ratio': 1.8
        })
        
        table = comp.get_comparison_table()
        assert len(table) == 2
        assert 'Strategy' in table.columns
        assert 'Total Return %' in table.columns
    
    def test_create_comparison_chart(self):
        """Test chart creation."""
        comp = StrategyComparison()
        comp.add_strategy('A', {
            'total_return_pct': 25.0,
            'win_rate': 60.0,
            'sharpe_ratio': 1.5,
            'max_drawdown_pct': -10.0
        })
        
        fig = comp.create_comparison_chart()
        assert fig is not None
        assert fig.layout.title.text == 'Strategy Comparison'
    
    def test_get_best_strategy(self):
        """Test best strategy selection."""
        comp = StrategyComparison()
        comp.add_strategy('A', {'total_return_pct': 25.0})
        comp.add_strategy('B', {'total_return_pct': 30.0})
        
        best = comp.get_best_strategy('total_return_pct')
        assert best == 'B'
    
    def test_get_rankings(self):
        """Test strategy rankings."""
        comp = StrategyComparison()
        comp.add_strategy('A', {
            'total_return_pct': 25.0,
            'win_rate': 60.0,
            'sharpe_ratio': 1.5
        })
        comp.add_strategy('B', {
            'total_return_pct': 20.0,
            'win_rate': 65.0,
            'sharpe_ratio': 1.8
        })
        
        rankings = comp.get_rankings()
        assert 'total_return_pct' in rankings
        assert rankings['total_return_pct'][0] == 'A'
        assert rankings['win_rate'][0] == 'B'
