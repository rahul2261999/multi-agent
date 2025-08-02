"""
Multi-Agents Logging Package

A comprehensive logging solution using loguru with:
- Daily file rotation
- Configurable log levels  
- Color-coded console output
- Error tracing
- Environment-based configuration

Usage:
    from src.libs.logger import get_logger, setup_logger, LogLevel
    
    # Setup logger (call once at application startup)
    logger_manager = setup_logger()
    
    # Get logger instance
    logger = get_logger("my_module")
    
    # Use logger
    logger.info("Application started")
    logger.error("Something went wrong")
    
    # Or use convenience functions
    from src.libs.logger import info, error, debug
    info("This is an info message")
    error("This is an error message")
"""

from .manager import (
    # Main facade & helpers
    LoggerManager,
    get_logger,
    setup_logger,
    trace,
    debug,
    info,
    success,
    warning,
    error,
    critical,
    exception,
)

from ._setup import LoggerSetup
from .config import LoggerConfig
from .enums import LogLevel

__all__ = [
    # Main classes
    "LoggerManager",
    "LoggerSetup", 
    "LoggerConfig",
    "LogLevel",
    
    # Factory functions
    "get_logger",
    "setup_logger",
    
    # Convenience functions
    "trace",
    "debug",
    "info", 
    "success",
    "warning",
    "error",
    "critical",
    "exception",
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Multi-Agents Team"
__description__ = "Advanced logging system with loguru and pydantic configuration"