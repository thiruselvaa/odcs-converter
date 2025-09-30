"""
Advanced logging configuration for ODCS Converter using loguru.

This module provides flexible, environment-aware logging configuration
supporting multiple output formats, structured logging, and correlation tracking.
"""

import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
from contextvars import ContextVar

from loguru import logger
import json

# Context variable for correlation IDs
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")


class LogConfig:
    """Centralized logging configuration for different environments."""

    # Environment definitions
    ENVIRONMENTS = {
        "local": {
            "level": "DEBUG",
            "console_format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
            "file_format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {extra[correlation_id]} | {message}",
            "console_enabled": True,
            "file_enabled": True,
            "structured_enabled": False,
            "rotation": "10 MB",
            "retention": "7 days",
            "compression": "zip",
        },
        "dev": {
            "level": "DEBUG",
            "console_format": "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>",
            "file_format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {extra[correlation_id]} | {message}",
            "console_enabled": True,
            "file_enabled": True,
            "structured_enabled": True,
            "rotation": "50 MB",
            "retention": "14 days",
            "compression": "zip",
        },
        "test": {
            "level": "WARNING",
            "console_format": "{time:HH:mm:ss} | {level: <8} | {name} | {message}",
            "file_format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {extra[correlation_id]} | {message}",
            "console_enabled": False,
            "file_enabled": True,
            "structured_enabled": False,
            "rotation": "20 MB",
            "retention": "3 days",
            "compression": "gz",
        },
        "stage": {
            "level": "INFO",
            "console_format": "{time:HH:mm:ss} | {level: <8} | {message}",
            "file_format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {extra[correlation_id]} | {message}",
            "console_enabled": True,
            "file_enabled": True,
            "structured_enabled": True,
            "rotation": "100 MB",
            "retention": "30 days",
            "compression": "gz",
        },
        "prod": {
            "level": "INFO",
            "console_format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            "file_format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {extra[correlation_id]} | {message}",
            "console_enabled": False,
            "file_enabled": True,
            "structured_enabled": True,
            "rotation": "500 MB",
            "retention": "90 days",
            "compression": "gz",
        },
    }

    def __init__(
        self,
        environment: str = None,
        log_dir: str = None,
        app_name: str = "odcs-converter",
    ):
        """Initialize logging configuration.

        Args:
            environment: Environment name (local, dev, test, stage, prod)
            log_dir: Directory for log files
            app_name: Application name for log files
        """
        self.environment = environment or os.getenv("ODCS_ENV", "local")
        self.log_dir = Path(log_dir or os.getenv("ODCS_LOG_DIR", "logs"))
        self.app_name = app_name
        # Create a copy to avoid mutating the class variable
        self.config = self.ENVIRONMENTS.get(
            self.environment, self.ENVIRONMENTS["local"]
        ).copy()

        # Override with environment variables
        self._apply_env_overrides()

        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _apply_env_overrides(self):
        """Apply environment variable overrides to configuration."""
        env_overrides = {
            "ODCS_LOG_LEVEL": "level",
            "ODCS_LOG_CONSOLE": "console_enabled",
            "ODCS_LOG_FILE": "file_enabled",
            "ODCS_LOG_STRUCTURED": "structured_enabled",
            "ODCS_LOG_ROTATION": "rotation",
            "ODCS_LOG_RETENTION": "retention",
        }

        for env_var, config_key in env_overrides.items():
            value = os.getenv(env_var)
            if value is not None:
                if config_key in [
                    "console_enabled",
                    "file_enabled",
                    "structured_enabled",
                ]:
                    self.config[config_key] = value.lower() in (
                        "true",
                        "1",
                        "yes",
                        "on",
                    )
                else:
                    self.config[config_key] = value

    def get_log_files(self) -> Dict[str, Path]:
        """Get log file paths for different log types."""
        timestamp = datetime.now().strftime("%Y%m%d")
        return {
            "main": self.log_dir / f"{self.app_name}-{timestamp}.log",
            "error": self.log_dir / f"{self.app_name}-error-{timestamp}.log",
            "structured": self.log_dir
            / f"{self.app_name}-structured-{timestamp}.jsonl",
        }


def setup_logging(
    environment: str = None,
    log_dir: str = None,
    app_name: str = "odcs-converter",
    correlation_id_value: str = None,
) -> None:
    """Setup comprehensive logging configuration.

    Args:
        environment: Environment name (local, dev, test, stage, prod)
        log_dir: Directory for log files
        app_name: Application name for log files
        correlation_id_value: Custom correlation ID (auto-generated if None)
    """
    # Remove default logger
    logger.remove()

    # Initialize configuration
    log_config = LogConfig(environment, log_dir, app_name)
    log_files = log_config.get_log_files()

    # Set correlation ID
    if correlation_id_value is None:
        correlation_id_value = str(uuid.uuid4())[:8]
    correlation_id.set(correlation_id_value)

    # Add correlation ID to all log records
    logger.configure(extra={"correlation_id": correlation_id_value})

    # Console handler
    if log_config.config["console_enabled"]:
        logger.add(
            sys.stderr,
            format=log_config.config["console_format"],
            level=log_config.config["level"],
            colorize=True,
            backtrace=True,
            diagnose=True,
        )

    # File handlers
    if log_config.config["file_enabled"]:
        # Main log file
        logger.add(
            str(log_files["main"]),
            format=log_config.config["file_format"],
            level=log_config.config["level"],
            rotation=log_config.config["rotation"],
            retention=log_config.config["retention"],
            compression=log_config.config["compression"],
            backtrace=True,
            diagnose=True,
        )

        # Error-only log file
        logger.add(
            str(log_files["error"]),
            format=log_config.config["file_format"],
            level="ERROR",
            rotation=log_config.config["rotation"],
            retention=log_config.config["retention"],
            compression=log_config.config["compression"],
            backtrace=True,
            diagnose=True,
        )

    # Structured logging (JSON Lines format)
    if log_config.config["structured_enabled"]:
        logger.add(
            str(log_files["structured"]),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name} | {message}",
            level=log_config.config["level"],
            rotation=log_config.config["rotation"],
            retention=log_config.config["retention"],
            compression=log_config.config["compression"],
            serialize=True,  # Use loguru's built-in JSON serialization
            enqueue=True,  # Use background thread for performance
        )

    # Log initialization
    logger.info(
        "Logging initialized",
        environment=log_config.environment,
        level=log_config.config["level"],
        log_dir=str(log_config.log_dir),
        correlation_id=correlation_id_value,
    )


def _simple_json_formatter(record) -> str:
    """Simple JSON formatter for structured logging."""
    from datetime import datetime

    # Basic log entry with safe access
    try:
        log_entry = {
            "timestamp": str(record["time"]),
            "level": str(record["level"].name),
            "logger": record["name"],
            "message": record["message"],
            "correlation_id": record["extra"].get("correlation_id", ""),
        }

        # Add safe extra fields
        for key, value in record["extra"].items():
            if key not in log_entry and key != "correlation_id":
                log_entry[key] = str(value)

        return json.dumps(log_entry) + "\n"
    except Exception:
        # Fallback format
        return f'{{"timestamp": "{datetime.now()}", "level": "ERROR", "message": "Logging format error"}}\n'


def get_logger(name: str = None) -> Any:
    """Get a logger instance with correlation ID context.

    Args:
        name: Logger name (defaults to caller's module)

    Returns:
        Configured logger instance
    """
    if name is None:
        import inspect

        frame = inspect.currentframe().f_back
        name = frame.f_globals.get("__name__", "unknown")

    # Bind correlation ID to logger
    current_correlation_id = correlation_id.get("")
    return logger.bind(correlation_id=current_correlation_id, logger_name=name)


def set_correlation_id(new_id: str) -> str:
    """Set a new correlation ID for the current context.

    Args:
        new_id: New correlation ID

    Returns:
        The previous correlation ID
    """
    old_id = correlation_id.get("")
    correlation_id.set(new_id)

    # Update logger configuration
    logger.configure(extra={"correlation_id": new_id})

    return old_id


def get_correlation_id() -> str:
    """Get the current correlation ID."""
    return correlation_id.get("")


class LogContext:
    """Context manager for scoped logging with custom correlation ID."""

    def __init__(self, correlation_id_value: str = None, **extra_fields):
        """Initialize log context.

        Args:
            correlation_id_value: Custom correlation ID
            **extra_fields: Additional fields to include in log records
        """
        self.correlation_id_value = correlation_id_value or str(uuid.uuid4())[:8]
        self.extra_fields = extra_fields
        self.previous_correlation_id = None
        self.previous_extra = {}

    def __enter__(self):
        """Enter the logging context."""
        self.previous_correlation_id = correlation_id.get("")
        correlation_id.set(self.correlation_id_value)

        # Store current extra fields and set new ones
        current_extra = logger._core.extra.copy()
        self.previous_extra = current_extra

        new_extra = current_extra.copy()
        new_extra.update(self.extra_fields)
        new_extra["correlation_id"] = self.correlation_id_value

        logger.configure(extra=new_extra)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the logging context."""
        correlation_id.set(self.previous_correlation_id)
        logger.configure(extra=self.previous_extra)


# Convenience functions for different log levels with rich context
def log_operation_start(operation: str, **context) -> str:
    """Log the start of an operation with context.

    Args:
        operation: Operation name
        **context: Additional context fields

    Returns:
        Generated correlation ID for the operation
    """
    op_id = str(uuid.uuid4())[:8]
    with LogContext(op_id, operation=operation, **context):
        logger.info(f"Starting operation: {operation}", **context)
    return op_id


def log_operation_end(
    operation: str, correlation_id_value: str, success: bool = True, **context
):
    """Log the end of an operation.

    Args:
        operation: Operation name
        correlation_id_value: Correlation ID from operation start
        success: Whether the operation was successful
        **context: Additional context fields
    """
    with LogContext(correlation_id_value, operation=operation, **context):
        status = "completed successfully" if success else "failed"
        logger.info(f"Operation {operation} {status}", success=success, **context)


def log_performance(operation: str, duration_ms: float, **context):
    """Log performance metrics.

    Args:
        operation: Operation name
        duration_ms: Duration in milliseconds
        **context: Additional context fields
    """
    logger.info(
        f"Performance: {operation}",
        operation=operation,
        duration_ms=duration_ms,
        performance=True,
        **context,
    )


# Environment-specific setup functions
def setup_local_logging():
    """Setup logging for local development."""
    setup_logging("local")


def setup_dev_logging():
    """Setup logging for development environment."""
    setup_logging("dev")


def setup_test_logging():
    """Setup logging for test environment."""
    setup_logging("test")


def setup_stage_logging():
    """Setup logging for staging environment."""
    setup_logging("stage")


def setup_prod_logging():
    """Setup logging for production environment."""
    setup_logging("prod")


# Export main logger instance
__all__ = [
    "setup_logging",
    "get_logger",
    "set_correlation_id",
    "get_correlation_id",
    "LogContext",
    "log_operation_start",
    "log_operation_end",
    "log_performance",
    "setup_local_logging",
    "setup_dev_logging",
    "setup_test_logging",
    "setup_stage_logging",
    "setup_prod_logging",
    "logger",
]
