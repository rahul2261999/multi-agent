"""config.py

Pydantic-based configuration model for the logging system.
Separated into its own module to respect SRP (configuration logic
lives here, independent of the actual logging implementation).
"""

from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

from .enums import LogLevel


class LoggerConfig(BaseSettings):
    """Configuration options for the advanced logger.

    Values can be overridden from environment variables at runtime which
    makes the logger fully **12-factor-app** compliant.
    """

    # ---------------------------------------------------------------------
    # Log-level configuration
    # ---------------------------------------------------------------------
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Minimum log level to capture",
        alias="LOG_LEVEL",
    )

    # ------------------------------------------------------------------
    # Console output configuration
    # ------------------------------------------------------------------
    enable_console_logging: bool = Field(
        default=True,
        description="Whether log records should also be emitted to the console",
        alias="ENABLE_CONSOLE_LOGGING",
    )
    colorize_console: bool = Field(
        default=True,
        description="Whether console output should be colorised (if supported)",
        alias="COLORIZE_CONSOLE",
    )

    # ------------------------------------------------------------------
    # File-logging configuration
    # ------------------------------------------------------------------
    enable_file_logging: bool = Field(
        default=True,
        description="Whether log records should be persisted to disk",
        alias="ENABLE_FILE_LOGGING",
    )
    log_directory: str = Field(
        default="logs",
        description="Directory where log files should be written",
        alias="LOG_DIRECTORY",
    )
    rotation_time: str = Field(
        default="00:00",
        description="HH:MM – time of day when daily log should rotate",
        alias="LOG_ROTATION_TIME",
    )
    retention_days: int = Field(
        default=30,
        description="Number of days to keep old log files",
        alias="LOG_RETENTION_DAYS",
    )
    max_file_size: str = Field(
        default="100 MB",
        description="Maximum size of a single log file before rotation",
        alias="LOG_MAX_FILE_SIZE",
    )

    # ------------------------------------------------------------------
    # Miscellaneous
    # ------------------------------------------------------------------
    log_format: str = Field(
        default="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        description="Loguru-style format string for both console and file output",
        alias="LOG_FORMAT",
    )
    app_name: str = Field(
        default="multi-agents",
        description="Logical application name that will be added to each record",
        alias="APP_NAME",
    )

    # ------------------------------------------------------------------
    # Validators / post-processing
    # ------------------------------------------------------------------
    @field_validator("log_level", mode="before")
    @classmethod
    def _validate_log_level(cls, v: Any) -> LogLevel:  # type: ignore[override]
        """Accept either enum value or a raw string from the environment."""
        if isinstance(v, LogLevel):
            return v
        if isinstance(v, str):
            try:
                return LogLevel(v.upper())
            except ValueError as exc:
                raise ValueError(f"Invalid log level: {v}") from exc
        raise TypeError("LOG_LEVEL must be a string or LogLevel enum member")

    @field_validator("log_directory", mode="after")
    @classmethod
    def _ensure_log_directory_exists(cls, v: str) -> str:  # noqa: D401 – imperative mood
        """Create the directory if it does not yet exist."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path.absolute())

    # ------------------------------------------------------------------
    # Pydantic-settings configuration
    # ------------------------------------------------------------------
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # allow undefined env vars like ENVIRONMENT
    }
