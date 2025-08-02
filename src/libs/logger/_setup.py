"""_setup.py

This **internal** module performs the heavy lifting of configuring
Loguru. The leading underscore indicates that end-users should not
import from here directly.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from .config import LoggerConfig
from .enums import LogLevel

__all__ = ["LoggerSetup"]


class LoggerSetup:
    """Singleton that sets up the underlying Loguru instance."""

    _instance: Optional["LoggerSetup"] = None
    _initialised: bool = False

    def __new__(cls) -> "LoggerSetup":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def __init__(self) -> None:  # noqa: D401 – not documenting self
        if LoggerSetup._initialised:
            return

        self.config = LoggerConfig()
        self._setup_logger()
        LoggerSetup._initialised = True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _setup_logger(self) -> None:
        logger.remove()

        if self.config.enable_console_logging:
            logger.add(
                sys.stdout,
                format=self._console_format(),
                level=self.config.log_level.value,
                colorize=self.config.colorize_console,
                backtrace=True,
                diagnose=True,
                catch=True,
            )

        if self.config.enable_file_logging:
            self._setup_file_sinks()

        logger.configure(
            extra={
                "app_name": self.config.app_name,
                "environment": os.getenv("ENVIRONMENT", "development"),
            }
        )

    # ------------------------------------------------------------------
    # Sink configuration helpers
    # ------------------------------------------------------------------
    def _setup_file_sinks(self) -> None:
        log_dir = Path(self.config.log_directory)

        # Main application log
        logger.add(
            str(log_dir / f"{self.config.app_name}.log"),
            format=self._file_format(),
            level=self.config.log_level.value,
            rotation=self.config.rotation_time,
            retention=f"{self.config.retention_days} days",
            compression="zip",
            backtrace=True,
            diagnose=True,
            catch=True,
            enqueue=True,
        )

        # Error-only log
        logger.add(
            str(log_dir / f"{self.config.app_name}_errors.log"),
            format=self._file_format(),
            level="ERROR",
            rotation=self.config.max_file_size,
            retention=f"{self.config.retention_days} days",
            compression="zip",
            backtrace=True,
            diagnose=True,
            catch=True,
            enqueue=True,
        )

        # Daily logs nested by date
        daily_pattern = (
            log_dir / "{time:YYYY-MM-DD}" / f"{self.config.app_name}_{{time:YYYY-MM-DD}}.log"
        )
        logger.add(
            str(daily_pattern),
            format=self._file_format(),
            level=self.config.log_level.value,
            rotation="1 day",
            retention=f"{self.config.retention_days} days",
            compression="zip",
            backtrace=True,
            diagnose=True,
            catch=True,
            enqueue=True,
        )

    # ------------------------------------------------------------------
    # Formatting helpers
    # ------------------------------------------------------------------
    def _console_format(self) -> str:
        if not self.config.colorize_console:
            return self.config.log_format

        return (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    def _file_format(self) -> str:
        return f"{self.config.log_format} | {{extra}}"

    # ------------------------------------------------------------------
    # Dynamic configuration helpers
    # ------------------------------------------------------------------
    def update_log_level(self, level: LogLevel) -> None:
        self.config.log_level = level
        self._setup_logger()

    def get_logger(self, name: Optional[str] = None):  # type: ignore[return-type]
        return logger.bind(name=name) if name else logger

    def log_system_info(self) -> None:
        l = self.get_logger("logger.setup")
        l.info("Logger system initialised")
        l.info("Log level        : {}", self.config.log_level.value)
        l.info("Log directory    : {}", self.config.log_directory)
        l.info("File logging     : {}", self.config.enable_file_logging)
        l.info("Console logging  : {}", self.config.enable_console_logging)
        l.info("App name         : {}", self.config.app_name)
