"""
Export & Report Generation
===========================
Generate PDF/Excel reports for trades and performance.

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

from datetime import datetime
from typing import Dict, Optional
import pandas as pd
from pathlib import Path


class ReportGenerator:
    """Generate trading reports."""
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize report generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_excel(
        self,
        data: Dict[str, pd.DataFrame],
        filename: Optional[str] = None
    ) -> str:
        """Export data to Excel file."""
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = self.output_dir / filename
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for sheet_name, df in data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return str(filepath)
    
    def generate_trade_history_report(
        self,
        trades: pd.DataFrame
    ) -> str:
        """Generate trade history Excel report."""
        data = {
            'Trades': trades,
            'Summary': self._create_trade_summary(trades)
        }
        
        return self.export_to_excel(
            data,
            f"trade_history_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )
    
    def generate_performance_report(
        self,
        performance_data: Dict
    ) -> str:
        """Generate performance report."""
        # Create summary DataFrame
        summary_df = pd.DataFrame([performance_data])
        
        data = {'Performance Summary': summary_df}
        
        return self.export_to_excel(
            data,
            f"performance_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )
    
    def generate_tax_summary(
        self,
        trades: pd.DataFrame,
        year: int
    ) -> str:
        """Generate tax summary report."""
        # Filter trades by year
        if 'timestamp' in trades.columns:
            trades['year'] = pd.to_datetime(trades['timestamp']).dt.year
            yearly_trades = trades[trades['year'] == year].copy()
        else:
            yearly_trades = trades.copy()
        
        # Calculate totals
        if 'pnl' in yearly_trades.columns:
            total_profit = yearly_trades[yearly_trades['pnl'] > 0]['pnl'].sum()
            total_loss = yearly_trades[yearly_trades['pnl'] < 0]['pnl'].sum()
            net_pnl = yearly_trades['pnl'].sum()
        else:
            total_profit = 0
            total_loss = 0
            net_pnl = 0
        
        summary = pd.DataFrame([{
            'Year': year,
            'Total Trades': len(yearly_trades),
            'Total Profit': total_profit,
            'Total Loss': total_loss,
            'Net P&L': net_pnl
        }])
        
        data = {
            'Tax Summary': summary,
            'All Trades': yearly_trades
        }
        
        return self.export_to_excel(
            data,
            f"tax_summary_{year}.xlsx"
        )
    
    def _create_trade_summary(self, trades: pd.DataFrame) -> pd.DataFrame:
        """Create summary statistics from trades."""
        if trades.empty:
            return pd.DataFrame()
        
        summary = {
            'Total Trades': len(trades),
            'Buy Orders': len(trades[trades.get('action') == 'BUY']),
            'Sell Orders': len(trades[trades.get('action') == 'SELL'])
        }
        
        if 'pnl' in trades.columns:
            winning = trades[trades['pnl'] > 0]
            losing = trades[trades['pnl'] < 0]
            
            summary.update({
                'Winning Trades': len(winning),
                'Losing Trades': len(losing),
                'Win Rate %': (len(winning) / len(trades) * 100)
                if len(trades) > 0 else 0,
                'Total P&L': trades['pnl'].sum(),
                'Avg Win': winning['pnl'].mean() if len(winning) > 0 else 0,
                'Avg Loss': losing['pnl'].mean() if len(losing) > 0 else 0
            })
        
        return pd.DataFrame([summary])
    
    def export_to_csv(
        self,
        df: pd.DataFrame,
        filename: Optional[str] = None
    ) -> str:
        """Export DataFrame to CSV."""
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.output_dir / filename
        df.to_csv(filepath, index=False)
        
        return str(filepath)


class PDFReportGenerator:
    """Generate PDF reports (requires reportlab)."""
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize PDF generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_summary_pdf(
        self,
        title: str,
        data: Dict,
        filename: Optional[str] = None
    ) -> str:
        """Generate simple text PDF report."""
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        filepath = self.output_dir / filename
        
        # Simple text file for now (PDF generation requires reportlab)
        with open(filepath.with_suffix('.txt'), 'w') as f:
            f.write(f"{title}\n")
            f.write("=" * 50 + "\n\n")
            
            for key, value in data.items():
                f.write(f"{key}: {value}\n")
            
            f.write(f"\nGenerated: {datetime.now()}\n")
        
        return str(filepath.with_suffix('.txt'))


if __name__ == "__main__":
    gen = ReportGenerator()
    
    # Test data
    trades = pd.DataFrame([
        {'timestamp': datetime.now(), 'action': 'BUY', 'symbol': 'BTC',
         'quantity': 0.1, 'price': 50000, 'pnl': 0},
        {'timestamp': datetime.now(), 'action': 'SELL', 'symbol': 'BTC',
         'quantity': 0.1, 'price': 51000, 'pnl': 100}
    ])
    
    filepath = gen.generate_trade_history_report(trades)
    print(f"Report generated: {filepath}")
