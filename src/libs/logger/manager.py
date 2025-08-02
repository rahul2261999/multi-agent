"""manager.py

Public interface (facade) for the advanced logging system.
Hides the internal Loguru configuration from callers and offers a clean
API that can be imported as::

    from src.libs.logger import get_logger, setup_logger

Keeping the facade separate from the setup logic makes the package easy
to reason about and test.
"""

from __future__ import annotations

from typing import Optional

from .enums import LogLevel
from ._setup import LoggerSetup

__all__ = [
    "LoggerManager",
    "get_logger",
    "setup_logger",
    # convenience wrappers
    "trace",
    "debug",
    "info",
    "success",
    "warning",
    "error",
    "critical",
    "exception",
]


class LoggerManager:
    """Facade exposing user-friendly helper methods."""

    def __init__(self) -> None:
        self._setup = LoggerSetup()
        self._logger = self._setup.get_logger()

    # ------------------------------------------------------------------
    # Retrieval helpers
    # ------------------------------------------------------------------
    def get_logger(self, name: Optional[str] = None):  # type: ignore[return-type]
        return self._setup.get_logger(name)

    # ------------------------------------------------------------------
    # Convenience wrappers – delegate to underlying Loguru logger
    # ------------------------------------------------------------------
    def trace(self, message: str, **kwargs):
        self._logger.trace(message, **kwargs)

    def debug(self, message: str, **kwargs):
        self._logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs):
        self._logger.info(message, **kwargs)

    def success(self, message: str, **kwargs):
        self._logger.success(message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        self._logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs):
        self._logger.critical(message, **kwargs)

    def exception(self, message: str, **kwargs):
        self._logger.exception(message, **kwargs)

    # ------------------------------------------------------------------
    # Dynamic configuration helpers
    # ------------------------------------------------------------------
    def set_log_level(self, level: LogLevel):
        self._setup.update_log_level(level)

    def log_startup_info(self):
        self._setup.log_system_info()


# ----------------------------------------------------------------------
# Global, lazily initialised manager instance (singleton)
# ----------------------------------------------------------------------
_logger_manager: LoggerManager | None = None


def _get_manager() -> LoggerManager:
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
        _logger_manager.log_startup_info()
    return _logger_manager


# ----------------------------------------------------------------------
# Public factory helpers
# ----------------------------------------------------------------------

def get_logger(name: Optional[str] = None):  # type: ignore[return-type]
    """Factory helper returning a correctly configured logger instance."""
    return _get_manager().get_logger(name)


def setup_logger() -> LoggerManager:
    """Explicitly initialise the logging subsystem.

    While unnecessary in most cases (lazy initialisation), it can be
    useful in *scripts* where you want the logger ready **before** any
    other imports happen.
    """
    return _get_manager()


# ----------------------------------------------------------------------
# Convenience functions (module-level) ---------------------------------
# ----------------------------------------------------------------------

def trace(message: str, **kwargs):
    _get_manager().trace(message, **kwargs)


def debug(message: str, **kwargs):
    _get_manager().debug(message, **kwargs)


def info(message: str, **kwargs):
    _get_manager().info(message, **kwargs)


def success(message: str, **kwargs):
    _get_manager().success(message, **kwargs)


def warning(message: str, **kwargs):
    _get_manager().warning(message, **kwargs)


def error(message: str, **kwargs):
    _get_manager().error(message, **kwargs)


def critical(message: str, **kwargs):
    _get_manager().critical(message, **kwargs)


def exception(message: str, **kwargs):
    _get_manager().exception(message, **kwargs)
