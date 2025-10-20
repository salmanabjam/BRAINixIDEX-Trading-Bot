"""
Custom exceptions for BRAINixIDEX Trading Bot
"""


class BotException(Exception):
    """Base exception for all bot errors"""
    pass


class DataFetchException(BotException):
    """Raised when data fetching fails"""
    pass


class DataValidationException(BotException):
    """Raised when data validation fails"""
    pass


class ModelTrainingException(BotException):
    """Raised when ML model training fails"""
    pass


class ModelPredictionException(BotException):
    """Raised when ML model prediction fails"""
    pass


class StrategyException(BotException):
    """Raised when strategy execution fails"""
    pass


class RiskManagementException(BotException):
    """Raised when risk management calculation fails"""
    pass


class ConfigurationException(BotException):
    """Raised when configuration is invalid"""
    pass


class APIException(BotException):
    """Raised when API call fails"""
    pass


class CacheException(BotException):
    """Raised when cache operations fail"""
    pass


class InsufficientDataException(BotException):
    """Raised when insufficient data is available"""
    pass
