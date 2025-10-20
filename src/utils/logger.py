"""
BiX TradeBOT - Advanced Logging System
Author: SALMAN ThinkTank
"""

import logging
from datetime import datetime
from pathlib import Path
import json
from typing import Dict, List, Optional
import traceback


class TradeBotLogger:
    """Advanced logging system for trading bot"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create separate log files
        self.main_log = self.log_dir / "trading_bot.log"
        self.error_log = self.log_dir / "errors.log"
        self.trade_log = self.log_dir / "trades.log"
        self.system_log = self.log_dir / "system.log"
        
        # Initialize loggers
        self._setup_loggers()
        
        # Error tracking
        self.error_history: List[Dict] = []
        self.max_error_history = 100
        
    def _setup_loggers(self):
        """Setup multiple loggers for different purposes"""
        
        # Main logger
        self.logger = logging.getLogger("TradeBOT")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler with colors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler for main logs
        file_handler = logging.FileHandler(self.main_log, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Error file handler
        error_handler = logging.FileHandler(self.error_log, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        
    def info(self, message: str, component: str = "SYSTEM"):
        """Log info message"""
        self.logger.info(f"[{component}] {message}")
        
    def warning(self, message: str, component: str = "SYSTEM"):
        """Log warning message"""
        self.logger.warning(f"[{component}] {message}")
        
    def error(self, message: str, component: str = "SYSTEM", 
              exception: Optional[Exception] = None):
        """Log error message with exception tracking"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'component': component,
            'message': message,
            'type': type(exception).__name__ if exception else 'Error',
            'traceback': traceback.format_exc() if exception else None
        }
        
        # Add to error history
        self.error_history.append(error_data)
        if len(self.error_history) > self.max_error_history:
            self.error_history.pop(0)
        
        # Log to file
        self.logger.error(f"[{component}] {message}")
        if exception:
            self.logger.error(f"Exception: {str(exception)}")
            self.logger.error(traceback.format_exc())
            
    def trade(self, action: str, symbol: str, price: float, 
              quantity: float, reason: str):
        """Log trade execution"""
        trade_data = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'symbol': symbol,
            'price': price,
            'quantity': quantity,
            'reason': reason
        }
        
        # Write to trade log
        with open(self.trade_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(trade_data) + '\n')
            
        self.logger.info(f"[TRADE] {action} {quantity} {symbol} @ ${price:,.2f} | {reason}")
        
    def system(self, event: str, details: Dict):
        """Log system events"""
        system_data = {
            'timestamp': datetime.now().isoformat(),
            'event': event,
            'details': details
        }
        
        with open(self.system_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(system_data) + '\n')
            
        self.logger.info(f"[SYSTEM] {event}")
        
    def get_recent_errors(self, limit: int = 20) -> List[Dict]:
        """Get recent errors"""
        return self.error_history[-limit:]
    
    def get_error_stats(self) -> Dict:
        """Get error statistics"""
        if not self.error_history:
            return {
                'total_errors': 0,
                'error_types': {},
                'components': {}
            }
            
        error_types = {}
        components = {}
        
        for error in self.error_history:
            # Count error types
            error_type = error.get('type', 'Unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1
            
            # Count by component
            component = error.get('component', 'Unknown')
            components[component] = components.get(component, 0) + 1
            
        return {
            'total_errors': len(self.error_history),
            'error_types': error_types,
            'components': components,
            'last_error': self.error_history[-1] if self.error_history else None
        }
    
    def clear_old_logs(self, days: int = 7):
        """Clear logs older than specified days"""
        cutoff_time = datetime.now().timestamp() - (days * 86400)
        
        for log_file in [self.main_log, self.error_log, self.trade_log, self.system_log]:
            if log_file.exists():
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    self.info(f"Cleared old log: {log_file.name}")


# Global logger instance
_logger_instance = None

def get_logger() -> TradeBotLogger:
    """Get global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = TradeBotLogger()
    return _logger_instance
