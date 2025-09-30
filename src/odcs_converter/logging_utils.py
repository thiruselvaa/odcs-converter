"""
Logging utilities for ODCS Converter.

This module provides utilities for loading YAML configuration,
performance tracking, and advanced logging features.
"""

import os
import re
import time
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Callable, Union
from functools import wraps

from loguru import logger


class LoggingConfigLoader:
    """Load and manage logging configuration from YAML files."""

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """Initialize configuration loader.

        Args:
            config_path: Path to logging configuration YAML file
        """
        if config_path is None:
            # Look for config in multiple locations
            possible_paths = [
                Path.cwd() / "config" / "logging.yaml",
                Path.cwd() / "logging.yaml",
                Path(__file__).parent.parent.parent / "config" / "logging.yaml",
                Path.home() / ".odcs-converter" / "logging.yaml",
            ]

            for path in possible_paths:
                if path.exists():
                    config_path = path
                    break

        self.config_path = Path(config_path) if config_path else None
        self._config = None
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path or not self.config_path.exists():
            # Use default configuration
            self._config = self._get_default_config()
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f)
        except Exception as e:
            logger.warning(
                f"Failed to load logging config from {self.config_path}: {e}"
            )
            self._config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when YAML file is not available."""
        return {
            "defaults": {
                "app_name": "odcs-converter",
                "log_dir": "logs",
                "correlation_id_length": 8,
                "max_string_length": 1000,
            },
            "environments": {
                "local": {
                    "level": "DEBUG",
                    "console": {"enabled": True, "colorize": True},
                    "file": {
                        "enabled": True,
                        "rotation": "10 MB",
                        "retention": "7 days",
                    },
                    "structured": {"enabled": False},
                    "features": {"backtrace": True, "diagnose": True},
                }
            },
        }

    def get_environment_config(self, environment: str) -> Dict[str, Any]:
        """Get configuration for specific environment.

        Args:
            environment: Environment name

        Returns:
            Environment configuration dictionary
        """
        env_config = self._config.get("environments", {}).get(
            environment, self._config.get("environments", {}).get("local", {})
        )

        # Apply environment variable overrides
        return self._apply_env_overrides(env_config)

    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration.

        Args:
            config: Base configuration

        Returns:
            Configuration with environment variable overrides applied
        """
        env_mappings = self._config.get("env_vars", {})

        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_value(config, config_path, value)

        return config

    def _set_nested_value(self, config: Dict[str, Any], path: str, value: str) -> None:
        """Set nested configuration value using dot notation.

        Args:
            config: Configuration dictionary
            path: Dot-notation path (e.g., "console.enabled")
            value: Value to set
        """
        keys = path.split(".")
        current = config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Convert string values to appropriate types
        final_key = keys[-1]
        if value.lower() in ("true", "false"):
            current[final_key] = value.lower() == "true"
        elif value.isdigit():
            current[final_key] = int(value)
        else:
            current[final_key] = value

    def get_defaults(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return self._config.get("defaults", {})

    def get_file_patterns(self) -> Dict[str, str]:
        """Get file naming patterns."""
        return self._config.get("file_patterns", {})

    def get_security_config(self) -> Dict[str, Any]:
        """Get security-related configuration."""
        return self._config.get("security", {})


class SensitiveDataMasker:
    """Mask sensitive data in log messages."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize data masker.

        Args:
            config: Security configuration
        """
        self.config = config or {}
        self.enabled = self.config.get("mask_sensitive_fields", True)
        self.patterns = self.config.get("sensitive_patterns", [])
        self.mask_char = self.config.get("mask_character", "*")
        self.max_length = self.config.get("max_field_length", 100)

        # Compile regex patterns
        self.compiled_patterns = []
        for pattern in self.patterns:
            try:
                self.compiled_patterns.append(
                    re.compile(
                        rf'\b{pattern}\b["\']?\s*[:=]\s*["\']?([^"\'\s,}}]+)',
                        re.IGNORECASE,
                    )
                )
            except re.error:
                logger.warning(
                    f"Invalid regex pattern for sensitive data masking: {pattern}"
                )

    def mask_message(self, message: str) -> str:
        """Mask sensitive data in log message.

        Args:
            message: Original log message

        Returns:
            Message with sensitive data masked
        """
        if not self.enabled:
            return message

        masked_message = message
        for pattern in self.compiled_patterns:
            masked_message = pattern.sub(
                lambda m: m.group(0).replace(
                    m.group(1), self.mask_char * min(len(m.group(1)), 8)
                ),
                masked_message,
            )

        return masked_message

    def mask_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data in dictionary.

        Args:
            data: Dictionary that may contain sensitive data

        Returns:
            Dictionary with sensitive values masked
        """
        if not self.enabled:
            return data

        masked_data = {}
        for key, value in data.items():
            if any(pattern.lower() in key.lower() for pattern in self.patterns):
                if isinstance(value, str):
                    masked_data[key] = self.mask_char * min(len(value), 8)
                else:
                    masked_data[key] = self.mask_char * 8
            elif isinstance(value, dict):
                masked_data[key] = self.mask_dict(value)
            elif isinstance(value, str) and len(value) > self.max_length:
                masked_data[key] = value[: self.max_length] + "..."
            else:
                masked_data[key] = value

        return masked_data


class PerformanceTracker:
    """Track and log performance metrics."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize performance tracker.

        Args:
            config: Performance configuration
        """
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.threshold_ms = self.config.get("threshold_ms", 1000)
        self.include_args = self.config.get("include_args", False)
        self.include_result = self.config.get("include_result", False)

    def track_performance(
        self,
        operation_name: Optional[str] = None,
        log_args: bool = None,
        log_result: bool = None,
        threshold_ms: Optional[float] = None,
    ):
        """Decorator to track function performance.

        Args:
            operation_name: Custom operation name (defaults to function name)
            log_args: Whether to log function arguments
            log_result: Whether to log function result
            threshold_ms: Custom threshold for logging (in milliseconds)
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)

                op_name = operation_name or f"{func.__module__}.{func.__name__}"
                should_log_args = (
                    log_args if log_args is not None else self.include_args
                )
                should_log_result = (
                    log_result if log_result is not None else self.include_result
                )
                threshold = (
                    threshold_ms if threshold_ms is not None else self.threshold_ms
                )

                start_time = time.perf_counter()

                try:
                    result = func(*args, **kwargs)
                    success = True
                except Exception:
                    result = None
                    success = False
                    raise
                finally:
                    end_time = time.perf_counter()
                    duration_ms = (end_time - start_time) * 1000

                    if duration_ms >= threshold:
                        log_data = {
                            "operation": op_name,
                            "duration_ms": round(duration_ms, 2),
                            "success": success,
                            "performance": True,
                        }

                        if should_log_args and args:
                            log_data["args"] = (
                                str(args)[:200] + "..."
                                if len(str(args)) > 200
                                else str(args)
                            )

                        if should_log_args and kwargs:
                            log_data["kwargs"] = {
                                k: str(v)[:100] + "..." if len(str(v)) > 100 else v
                                for k, v in kwargs.items()
                            }

                        if should_log_result and success and result is not None:
                            log_data["result_type"] = type(result).__name__
                            if hasattr(result, "__len__"):
                                log_data["result_size"] = len(result)

                        logger.info(
                            f"Performance: {op_name} took {duration_ms:.2f}ms",
                            **log_data,
                        )

                return result

            return wrapper

        return decorator


class LogFormatter:
    """Custom log formatters with advanced features."""

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    @staticmethod
    def format_duration(duration_seconds: float) -> str:
        """Format duration in human-readable format.

        Args:
            duration_seconds: Duration in seconds

        Returns:
            Formatted duration string
        """
        if duration_seconds < 1:
            return f"{duration_seconds * 1000:.1f}ms"
        elif duration_seconds < 60:
            return f"{duration_seconds:.1f}s"
        elif duration_seconds < 3600:
            minutes = int(duration_seconds // 60)
            seconds = duration_seconds % 60
            return f"{minutes}m {seconds:.1f}s"
        else:
            hours = int(duration_seconds // 3600)
            minutes = int((duration_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"

    @staticmethod
    def truncate_string(text: str, max_length: int = 200) -> str:
        """Truncate string with ellipsis if too long.

        Args:
            text: Text to truncate
            max_length: Maximum length

        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."

    @staticmethod
    def format_exception_chain(exc: Exception) -> str:
        """Format exception chain for logging.

        Args:
            exc: Exception to format

        Returns:
            Formatted exception chain
        """
        messages = []
        current_exc = exc

        while current_exc:
            messages.append(f"{type(current_exc).__name__}: {current_exc}")
            current_exc = current_exc.__cause__ or current_exc.__context__
            if current_exc in messages:  # Avoid infinite loops
                break

        return " -> ".join(messages)


class ContextualLogger:
    """Logger with automatic context enrichment."""

    def __init__(self, name: str):
        """Initialize contextual logger.

        Args:
            name: Logger name
        """
        self.name = name
        self.base_logger = logger.bind(logger_name=name)

    def with_context(self, **context) -> "ContextualLogger":
        """Create logger with additional context.

        Args:
            **context: Context fields to add

        Returns:
            New logger instance with context
        """
        new_logger = ContextualLogger(self.name)
        new_logger.base_logger = self.base_logger.bind(**context)
        return new_logger

    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        self.base_logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message with context."""
        self.base_logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        self.base_logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with context."""
        self.base_logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message with context."""
        self.base_logger.critical(message, **kwargs)

    def exception(self, message: str, **kwargs):
        """Log exception with context."""
        self.base_logger.exception(message, **kwargs)


# Utility functions
def get_log_file_size(log_file: Path) -> int:
    """Get log file size in bytes.

    Args:
        log_file: Path to log file

    Returns:
        File size in bytes, 0 if file doesn't exist
    """
    try:
        return log_file.stat().st_size if log_file.exists() else 0
    except OSError:
        return 0


def cleanup_old_logs(log_dir: Path, retention_days: int = 30):
    """Clean up old log files.

    Args:
        log_dir: Directory containing log files
        retention_days: Number of days to retain logs
    """
    if not log_dir.exists():
        return

    cutoff_time = time.time() - (retention_days * 24 * 60 * 60)

    for log_file in log_dir.glob("*.log*"):
        try:
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                logger.debug(f"Removed old log file: {log_file}")
        except OSError as e:
            logger.warning(f"Failed to remove old log file {log_file}: {e}")


def get_caller_info(skip_frames: int = 2) -> Dict[str, str]:
    """Get information about the calling function.

    Args:
        skip_frames: Number of frames to skip

    Returns:
        Dictionary with caller information
    """
    import inspect

    try:
        frame = inspect.currentframe()
        for _ in range(skip_frames):
            frame = frame.f_back
            if frame is None:
                break

        if frame:
            return {
                "filename": frame.f_code.co_filename,
                "function": frame.f_code.co_name,
                "line": frame.f_lineno,
                "module": frame.f_globals.get("__name__", "unknown"),
            }
    except Exception:
        pass

    return {
        "filename": "unknown",
        "function": "unknown",
        "line": 0,
        "module": "unknown",
    }
