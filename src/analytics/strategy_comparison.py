"""
Strategy Comparison Tool
=========================
Compare multiple strategies side-by-side.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

from typing import Dict, List
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class StrategyComparison:
    """Compare multiple trading strategies."""
    
    def __init__(self):
        """Initialize comparator."""
        self.strategies: Dict[str, Dict] = {}
    
    def add_strategy(
        self,
        name: str,
        backtest_results: Dict,
        description: str = ""
    ):
        """Add strategy results."""
        self.strategies[name] = {
            'results': backtest_results,
            'description': description
        }
    
    def get_comparison_table(self) -> pd.DataFrame:
        """Generate comparison table."""
        data = []
        
        for name, strategy in self.strategies.items():
            results = strategy['results']
            data.append({
                'Strategy': name,
                'Total Return %': results.get('total_return_pct', 0),
                'Win Rate %': results.get('win_rate', 0),
                'Sharpe Ratio': results.get('sharpe_ratio', 0),
                'Max Drawdown %': results.get('max_drawdown_pct', 0),
                'Total Trades': results.get('total_trades', 0),
                'Profit Factor': results.get('profit_factor', 0)
            })
        
        return pd.DataFrame(data)
    
    def create_comparison_chart(self):
        """Create side-by-side comparison chart."""
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                'Total Return',
                'Win Rate',
                'Sharpe Ratio',
                'Max Drawdown'
            )
        )
        
        strategies = list(self.strategies.keys())
        
        # Total Return
        returns = [
            self.strategies[s]['results'].get('total_return_pct', 0)
            for s in strategies
        ]
        fig.add_trace(
            go.Bar(x=strategies, y=returns, name='Return %'),
            row=1, col=1
        )
        
        # Win Rate
        win_rates = [
            self.strategies[s]['results'].get('win_rate', 0)
            for s in strategies
        ]
        fig.add_trace(
            go.Bar(x=strategies, y=win_rates, name='Win Rate %'),
            row=1, col=2
        )
        
        # Sharpe Ratio
        sharpe = [
            self.strategies[s]['results'].get('sharpe_ratio', 0)
            for s in strategies
        ]
        fig.add_trace(
            go.Bar(x=strategies, y=sharpe, name='Sharpe'),
            row=2, col=1
        )
        
        # Max Drawdown
        drawdowns = [
            self.strategies[s]['results'].get('max_drawdown_pct', 0)
            for s in strategies
        ]
        fig.add_trace(
            go.Bar(x=strategies, y=drawdowns, name='Drawdown %'),
            row=2, col=2
        )
        
        fig.update_layout(
            title='Strategy Comparison',
            showlegend=False,
            height=600
        )
        
        return fig
    
    def get_best_strategy(self, metric: str = 'total_return_pct') -> str:
        """Get best performing strategy by metric."""
        if not self.strategies:
            return None
        
        best_name = None
        best_value = float('-inf')
        
        for name, strategy in self.strategies.items():
            value = strategy['results'].get(metric, 0)
            if value > best_value:
                best_value = value
                best_name = name
        
        return best_name
    
    def get_rankings(self) -> Dict[str, List[str]]:
        """Get rankings by different metrics."""
        metrics = [
            'total_return_pct',
            'win_rate',
            'sharpe_ratio',
            'profit_factor'
        ]
        
        rankings = {}
        for metric in metrics:
            sorted_strategies = sorted(
                self.strategies.items(),
                key=lambda x: x[1]['results'].get(metric, 0),
                reverse=True
            )
            rankings[metric] = [s[0] for s in sorted_strategies]
        
        return rankings


if __name__ == "__main__":
    comp = StrategyComparison()
    
    # Add test strategies
    comp.add_strategy('Strategy A', {
        'total_return_pct': 25.5,
        'win_rate': 65.0,
        'sharpe_ratio': 1.8,
        'max_drawdown_pct': -12.3,
        'total_trades': 150
    })
    
    comp.add_strategy('Strategy B', {
        'total_return_pct': 18.2,
        'win_rate': 72.0,
        'sharpe_ratio': 2.1,
        'max_drawdown_pct': -8.5,
        'total_trades': 120
    })
    
    print(comp.get_comparison_table())
    print(f"Best: {comp.get_best_strategy()}")
