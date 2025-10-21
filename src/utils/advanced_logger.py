"""
Advanced logging system with rotation and structured logging
"""
import logging
import logging.handlers
import json
from pathlib import Path
from datetime import datetime
from typing import Optional


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields
        if hasattr(record, 'component'):
            log_data['component'] = record.component
        if hasattr(record, 'symbol'):
            log_data['symbol'] = record.symbol
        if hasattr(record, 'timeframe'):
            log_data['timeframe'] = record.timeframe
        if hasattr(record, 'action'):
            log_data['action'] = record.action
        if hasattr(record, 'error_code'):
            log_data['error_code'] = record.error_code
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


class ColoredConsoleFormatter(logging.Formatter):
    """Colored console formatter"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m'    # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format with colors"""
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger(
    name: str,
    log_dir: str = "logs",
    level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console: bool = True,
    json_format: bool = False
) -> logging.Logger:
    """
    Setup advanced logger with rotation
    
    Args:
        name: Logger name
        log_dir: Directory for log files
        level: Logging level
        max_bytes: Max size per log file
        backup_count: Number of backup files
        console: Enable console logging
        json_format: Use JSON format
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    
    # Create log directory
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # File handler with rotation
    log_file = Path(log_dir) / f"{name}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    
    # JSON log file
    if json_format:
        json_file = Path(log_dir) / f"{name}_structured.json"
        json_handler = logging.handlers.RotatingFileHandler(
            json_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        json_handler.setFormatter(StructuredFormatter())
        logger.addHandler(json_handler)
    
    # Regular format
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_formatter = ColoredConsoleFormatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger


class ContextLogger:
    """Logger with context support"""
    
    def __init__(self, logger: logging.Logger, **default_context):
        """
        Initialize context logger
        
        Args:
            logger: Base logger
            **default_context: Default context fields
        """
        self.logger = logger
        self.default_context = default_context
    
    def _log(self, level: int, msg: str, **context):
        """Log with context"""
        extra = {**self.default_context, **context}
        self.logger.log(level, msg, extra=extra)
    
    def debug(self, msg: str, **context):
        """Debug log with context"""
        self._log(logging.DEBUG, msg, **context)
    
    def info(self, msg: str, **context):
        """Info log with context"""
        self._log(logging.INFO, msg, **context)
    
    def warning(self, msg: str, **context):
        """Warning log with context"""
        self._log(logging.WARNING, msg, **context)
    
    def error(self, msg: str, **context):
        """Error log with context"""
        self._log(logging.ERROR, msg, **context)
    
    def critical(self, msg: str, **context):
        """Critical log with context"""
        self._log(logging.CRITICAL, msg, **context)
    
    def exception(self, msg: str, **context):
        """Log exception with context"""
        extra = {**self.default_context, **context}
        self.logger.exception(msg, extra=extra)


def get_logger(
    name: str,
    component: Optional[str] = None,
    **context
) -> ContextLogger:
    """
    Get or create logger with context
    
    Args:
        name: Logger name
        component: Component name
        **context: Additional context
    
    Returns:
        ContextLogger instance
    """
    logger = setup_logger(name, json_format=True)
    
    default_context = {}
    if component:
        default_context['component'] = component
    default_context.update(context)
    
    return ContextLogger(logger, **default_context)


# Audit logger for trades and critical events
def setup_audit_logger(log_dir: str = "logs/audit") -> logging.Logger:
    """
    Setup audit logger for critical events
    
    Args:
        log_dir: Audit log directory
    
    Returns:
        Audit logger
    """
    logger = logging.getLogger('audit')
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Daily rotating file handler
    log_file = Path(log_dir) / "audit.log"
    handler = logging.handlers.TimedRotatingFileHandler(
        log_file,
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    
    formatter = StructuredFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
