"""
Tests for Report Generator
===========================
"""

import pytest
import pandas as pd
from datetime import datetime
from pathlib import Path
from src.reports.report_generator import (
    ReportGenerator,
    PDFReportGenerator
)


class TestReportGenerator:
    """Test ReportGenerator class."""
    
    @pytest.fixture
    def generator(self, tmp_path):
        """Create generator with temp directory."""
        return ReportGenerator(str(tmp_path))
    
    @pytest.fixture
    def sample_trades(self):
        """Create sample trades."""
        return pd.DataFrame([
            {
                'timestamp': datetime.now(),
                'action': 'BUY',
                'symbol': 'BTC',
                'quantity': 0.1,
                'price': 50000,
                'pnl': 0
            },
            {
                'timestamp': datetime.now(),
                'action': 'SELL',
                'symbol': 'BTC',
                'quantity': 0.1,
                'price': 51000,
                'pnl': 100
            }
        ])
    
    def test_init(self, generator):
        """Test initialization."""
        assert generator.output_dir.exists()
    
    def test_export_to_excel(self, generator):
        """Test Excel export."""
        data = {
            'Sheet1': pd.DataFrame({'A': [1, 2, 3]})
        }
        filepath = generator.export_to_excel(data, 'test.xlsx')
        assert Path(filepath).exists()
    
    def test_generate_trade_history_report(self, generator, sample_trades):
        """Test trade history report."""
        filepath = generator.generate_trade_history_report(sample_trades)
        assert Path(filepath).exists()
        assert 'trade_history' in filepath
    
    def test_generate_performance_report(self, generator):
        """Test performance report."""
        data = {
            'total_return': 25.5,
            'win_rate': 65.0,
            'sharpe_ratio': 1.8
        }
        filepath = generator.generate_performance_report(data)
        assert Path(filepath).exists()
    
    def test_generate_tax_summary(self, generator, sample_trades):
        """Test tax summary report."""
        filepath = generator.generate_tax_summary(
            sample_trades,
            datetime.now().year
        )
        assert Path(filepath).exists()
    
    def test_export_to_csv(self, generator):
        """Test CSV export."""
        df = pd.DataFrame({'A': [1, 2, 3]})
        filepath = generator.export_to_csv(df, 'test.csv')
        assert Path(filepath).exists()


class TestPDFReportGenerator:
    """Test PDFReportGenerator class."""
    
    @pytest.fixture
    def generator(self, tmp_path):
        """Create PDF generator."""
        return PDFReportGenerator(str(tmp_path))
    
    def test_init(self, generator):
        """Test initialization."""
        assert generator.output_dir.exists()
    
    def test_generate_summary_pdf(self, generator):
        """Test PDF generation."""
        data = {'metric1': 100, 'metric2': 200}
        filepath = generator.generate_summary_pdf(
            'Test Report',
            data,
            'test.pdf'
        )
        # Currently generates .txt file
        assert Path(filepath).exists()
