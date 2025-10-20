"""
Unit tests for core.risk_manager module
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.risk_manager import RiskManager


class TestRiskManager:
    """Test suite for RiskManager class"""
    
    @pytest.fixture
    def risk_manager(self):
        """Create RiskManager instance"""
        return RiskManager(initial_capital=10000, risk_per_trade=0.02)
    
    def test_init(self):
        """Test RiskManager initialization"""
        rm = RiskManager(initial_capital=10000, risk_per_trade=0.02)
        assert rm.initial_capital == 10000
        assert rm.current_capital == 10000
        assert rm.risk_per_trade == 0.02
    
    def test_calculate_position_size_long(self, risk_manager):
        """Test position size calculation for long position"""
        position = risk_manager.calculate_position_size(
            entry_price=50000,
            atr=500,
            direction='long'
        )
        
        assert 'size' in position
        assert 'value' in position
        assert 'stop_loss' in position
        assert 'take_profit' in position
        assert 'risk_amount' in position
        
        assert position['size'] > 0
        assert position['stop_loss'] < 50000
        assert position['take_profit'] > 50000
    
    def test_calculate_position_size_short(self, risk_manager):
        """Test position size calculation for short position"""
        position = risk_manager.calculate_position_size(
            entry_price=50000,
            atr=500,
            direction='short'
        )
        
        assert position['size'] > 0
        assert position['stop_loss'] > 50000
        assert position['take_profit'] < 50000
    
    def test_position_size_respects_max_position(self, risk_manager):
        """Test that position size doesn't exceed max limit"""
        position = risk_manager.calculate_position_size(
            entry_price=100,
            atr=1,
            direction='long'
        )
        
        max_position_value = risk_manager.current_capital * 0.2
        assert position['value'] <= max_position_value
    
    def test_update_capital(self, risk_manager):
        """Test capital update after trade"""
        initial = risk_manager.current_capital
        risk_manager.update_capital(500)
        
        assert risk_manager.current_capital == initial + 500
    
    def test_update_capital_loss(self, risk_manager):
        """Test capital update with loss"""
        initial = risk_manager.current_capital
        risk_manager.update_capital(-200)
        
        assert risk_manager.current_capital == initial - 200
    
    def test_risk_amount_calculation(self, risk_manager):
        """Test risk amount is correct"""
        position = risk_manager.calculate_position_size(
            entry_price=50000,
            atr=500,
            direction='long'
        )
        
        expected_risk = risk_manager.current_capital * risk_manager.risk_per_trade
        assert abs(position['risk_amount'] - expected_risk) < 1
    
    def test_position_size_with_zero_atr(self, risk_manager):
        """Test position size with zero ATR (edge case)"""
        position = risk_manager.calculate_position_size(
            entry_price=50000,
            atr=0,
            direction='long'
        )
        
        assert position is not None
    
    def test_position_size_with_high_atr(self, risk_manager):
        """Test position size with very high ATR"""
        position = risk_manager.calculate_position_size(
            entry_price=50000,
            atr=10000,
            direction='long'
        )
        
        assert position['size'] > 0
        assert position['value'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=core.risk_manager', '--cov-report=term-missing'])
