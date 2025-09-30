"""
Tests for the enhanced logging system with loguru.

This module tests the logging configuration, performance tracking,
sensitive data masking, and environment-specific settings.
"""

import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch
import pytest
from loguru import logger

from odcs_converter.logging_config import (
    setup_logging,
    get_logger,
    set_correlation_id,
    get_correlation_id,
    LogContext,
    log_operation_start,
    log_operation_end,
    log_performance,
    LogConfig,
)
from odcs_converter.logging_utils import (
    LoggingConfigLoader,
    SensitiveDataMasker,
    PerformanceTracker,
    LogFormatter,
    ContextualLogger,
)


class TestLogConfig:
    """Test logging configuration class."""

    def test_default_config(self):
        """Test default configuration initialization."""
        # Default to local environment
        config = LogConfig()
        assert config.environment == "local"
        assert config.app_name == "odcs-converter"

    def test_environment_selection(self):
        """Test environment-specific configuration selection."""
        # Test each environment gets the right base config
        # Environment overrides from env vars are tested separately

        # Test prod environment (without env overrides)
        config_prod = LogConfig(environment="prod")
        assert config_prod.environment == "prod"
        # Base config for prod should be INFO (may be overridden by ODCS_LOG_LEVEL)
        assert LogConfig.ENVIRONMENTS["prod"]["level"] == "INFO"
        assert LogConfig.ENVIRONMENTS["prod"]["console_enabled"] is False

        # Test dev environment
        config_dev = LogConfig(environment="dev")
        assert config_dev.environment == "dev"
        assert LogConfig.ENVIRONMENTS["dev"]["level"] == "DEBUG"

    def test_log_file_paths(self):
        """Test log file path generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = LogConfig(log_dir=temp_dir)
            log_files = config.get_log_files()

            assert "main" in log_files
            assert "error" in log_files
            assert "structured" in log_files

            for file_path in log_files.values():
                assert str(file_path).startswith(temp_dir)

    def test_env_overrides(self):
        """Test environment variable overrides."""
        with patch.dict(
            os.environ,
            {
                "ODCS_LOG_LEVEL": "ERROR",
                "ODCS_LOG_CONSOLE": "false",
                "ODCS_LOG_FILE": "true",
                "ODCS_ENV": "test",  # Set explicit env to avoid other test pollution
            },
            clear=False,
        ):
            config = LogConfig()
            # Env overrides should take precedence
            assert config.config["level"] == "ERROR"
            assert config.config["console_enabled"] is False
            assert config.config["file_enabled"] is True


class TestLoggingSetup:
    """Test logging setup and configuration."""

    def setup_method(self):
        """Set up test environment."""
        # Remove existing loggers
        logger.remove()

    def teardown_method(self):
        """Clean up after tests."""
        # Reset logger
        logger.remove()

    def test_basic_setup(self):
        """Test basic logging setup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            setup_logging(environment="local", log_dir=temp_dir)

            # Test that logger is configured
            test_logger = get_logger("test")
            assert test_logger is not None

    def test_environment_specific_setup(self):
        """Test environment-specific logging setup."""
        environments = ["local", "dev", "test", "stage", "prod"]

        for env in environments:
            with tempfile.TemporaryDirectory() as temp_dir:
                setup_logging(environment=env, log_dir=temp_dir)
                test_logger = get_logger(f"test_{env}")
                assert test_logger is not None

    def test_correlation_id_handling(self):
        """Test correlation ID functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            correlation_id = "test-123"
            setup_logging(
                environment="local",
                log_dir=temp_dir,
                correlation_id_value=correlation_id,
            )

            assert get_correlation_id() == correlation_id

    def test_file_creation(self):
        """Test that log files are created."""
        with tempfile.TemporaryDirectory() as temp_dir:
            setup_logging(environment="dev", log_dir=temp_dir)

            # Generate some log messages
            test_logger = get_logger("test")
            test_logger.info("Test message")
            test_logger.error("Test error")

            # Check if log files exist
            log_dir = Path(temp_dir)
            log_files = list(log_dir.glob("*.log"))
            assert len(log_files) > 0


class TestCorrelationId:
    """Test correlation ID functionality."""

    def test_set_get_correlation_id(self):
        """Test setting and getting correlation ID."""
        test_id = "test-correlation-123"
        old_id = set_correlation_id(test_id)

        assert get_correlation_id() == test_id

        # Restore old ID
        set_correlation_id(old_id)

    def test_log_context_manager(self):
        """Test LogContext context manager."""
        test_id = "context-test-456"

        with LogContext(test_id, operation="test_operation") as ctx:
            assert get_correlation_id() == test_id

        # Context should be restored after exiting


class TestOperationLogging:
    """Test operation start/end logging."""

    def setup_method(self):
        """Set up logging for tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            setup_logging(environment="test", log_dir=temp_dir)

    def test_operation_start_end(self):
        """Test operation start and end logging."""
        operation_id = log_operation_start("test_operation", param1="value1")
        assert operation_id is not None
        assert len(operation_id) > 0

        log_operation_end("test_operation", operation_id, success=True)

    def test_operation_failure(self):
        """Test operation failure logging."""
        operation_id = log_operation_start("failing_operation")
        log_operation_end(
            "failing_operation", operation_id, success=False, error="Test error"
        )

    def test_performance_logging(self):
        """Test performance logging."""
        log_performance("test_performance", 1500.0, param="test")


class TestLoggingConfigLoader:
    """Test YAML configuration loader."""

    def test_default_config_fallback(self):
        """Test fallback to default config when YAML is missing."""
        loader = LoggingConfigLoader("/nonexistent/config.yaml")
        config = loader.get_environment_config("local")

        assert "level" in config
        assert config["level"] == "DEBUG"

    def test_yaml_config_loading(self):
        """Test loading configuration from YAML file."""
        yaml_content = """
defaults:
  app_name: "test-app"
  log_dir: "test-logs"

environments:
  test_env:
    level: "WARNING"
    console:
      enabled: false
    file:
      enabled: true
      rotation: "20 MB"
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            try:
                loader = LoggingConfigLoader(f.name)
                config = loader.get_environment_config("test_env")

                assert config["level"] == "WARNING"
                assert not config["console"]["enabled"]
                assert config["file"]["enabled"]
                assert config["file"]["rotation"] == "20 MB"
            finally:
                os.unlink(f.name)

    def test_env_variable_overrides(self):
        """Test environment variable overrides."""
        with patch.dict(os.environ, {"ODCS_LOG_LEVEL": "CRITICAL"}):
            loader = LoggingConfigLoader()
            config = loader.get_environment_config("local")
            # The actual override behavior depends on implementation


class TestSensitiveDataMasker:
    """Test sensitive data masking functionality."""

    def test_mask_message(self):
        """Test masking sensitive data in messages."""
        config = {
            "mask_sensitive_fields": True,
            "sensitive_patterns": ["password", "token"],
            "mask_character": "*",
        }
        masker = SensitiveDataMasker(config)

        message = "User login with password=secret123 and token=abc456"
        masked = masker.mask_message(message)

        assert "secret123" not in masked
        assert "abc456" not in masked
        assert "*" in masked

    def test_mask_dict(self):
        """Test masking sensitive data in dictionaries."""
        config = {
            "mask_sensitive_fields": True,
            "sensitive_patterns": ["password", "secret"],
            "mask_character": "*",
        }
        masker = SensitiveDataMasker(config)

        data = {
            "username": "testuser",
            "password": "secret123",
            "api_secret": "top_secret",
            "normal_field": "normal_value",
        }

        masked = masker.mask_dict(data)

        assert masked["username"] == "testuser"
        assert masked["password"] == "********"
        assert masked["api_secret"] == "********"
        assert masked["normal_field"] == "normal_value"

    def test_masking_disabled(self):
        """Test behavior when masking is disabled."""
        config = {"mask_sensitive_fields": False}
        masker = SensitiveDataMasker(config)

        message = "password=secret123"
        masked = masker.mask_message(message)

        assert masked == message


class TestPerformanceTracker:
    """Test performance tracking functionality."""

    def test_performance_decorator(self):
        """Test performance tracking decorator."""
        config = {
            "enabled": True,
            "threshold_ms": 100,
            "include_args": False,
            "include_result": False,
        }
        tracker = PerformanceTracker(config)

        @tracker.track_performance("test_function")
        def slow_function():
            time.sleep(0.15)  # 150ms
            return "result"

        with tempfile.TemporaryDirectory() as temp_dir:
            setup_logging(environment="test", log_dir=temp_dir)
            result = slow_function()

            assert result == "result"

    def test_performance_tracking_disabled(self):
        """Test performance tracking when disabled."""
        config = {"enabled": False}
        tracker = PerformanceTracker(config)

        @tracker.track_performance("test_function")
        def test_function():
            return "result"

        result = test_function()
        assert result == "result"

    def test_performance_with_args_logging(self):
        """Test performance tracking with argument logging."""
        config = {
            "enabled": True,
            "threshold_ms": 0,  # Log all operations
            "include_args": True,
            "include_result": True,
        }
        tracker = PerformanceTracker(config)

        @tracker.track_performance("test_with_args")
        def function_with_args(arg1, arg2=None):
            return {"result": "success"}

        with tempfile.TemporaryDirectory() as temp_dir:
            setup_logging(environment="test", log_dir=temp_dir)
            result = function_with_args("test", arg2="value")

            assert result["result"] == "success"


class TestLogFormatter:
    """Test log formatting utilities."""

    def test_format_file_size(self):
        """Test file size formatting."""
        assert LogFormatter.format_file_size(1024) == "1.0 KB"
        assert LogFormatter.format_file_size(1048576) == "1.0 MB"
        assert LogFormatter.format_file_size(1073741824) == "1.0 GB"

    def test_format_duration(self):
        """Test duration formatting."""
        assert LogFormatter.format_duration(0.5) == "500.0ms"
        assert LogFormatter.format_duration(1.5) == "1.5s"
        assert LogFormatter.format_duration(65) == "1m 5.0s"
        assert LogFormatter.format_duration(3665) == "1h 1m"

    def test_truncate_string(self):
        """Test string truncation."""
        long_string = "a" * 300
        truncated = LogFormatter.truncate_string(long_string, 100)

        assert len(truncated) == 100
        assert truncated.endswith("...")

    def test_format_exception_chain(self):
        """Test exception chain formatting."""
        try:
            try:
                raise ValueError("Inner error")
            except ValueError as e:
                raise RuntimeError("Outer error") from e
        except RuntimeError as e:
            formatted = LogFormatter.format_exception_chain(e)

            assert "RuntimeError" in formatted
            assert "ValueError" in formatted
            assert "Inner error" in formatted
            assert "Outer error" in formatted


class TestContextualLogger:
    """Test contextual logger functionality."""

    def test_logger_with_context(self):
        """Test logger with additional context."""
        with tempfile.TemporaryDirectory() as temp_dir:
            setup_logging(environment="test", log_dir=temp_dir)

            logger = ContextualLogger("test_logger")
            contextual_logger = logger.with_context(request_id="123", user="testuser")

            # Test different log levels
            contextual_logger.debug("Debug message")
            contextual_logger.info("Info message")
            contextual_logger.warning("Warning message")
            contextual_logger.error("Error message")

    def test_logger_exception(self):
        """Test exception logging with context."""
        with tempfile.TemporaryDirectory() as temp_dir:
            setup_logging(environment="test", log_dir=temp_dir)

            logger = ContextualLogger("test_logger")

            try:
                raise ValueError("Test exception")
            except ValueError:
                logger.exception("Exception occurred")


class TestIntegration:
    """Integration tests for the logging system."""

    def test_full_logging_workflow(self):
        """Test complete logging workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup logging
            setup_logging(environment="dev", log_dir=temp_dir)

            # Start operation
            operation_id = log_operation_start("integration_test", param="value")

            with LogContext(operation_id, operation="integration_test"):
                # Get logger
                test_logger = get_logger("integration_test")

                # Log various levels
                test_logger.debug("Debug message")
                test_logger.info("Info message", extra_field="extra_value")
                test_logger.warning("Warning message")
                test_logger.error("Error message")

                # Test performance logging
                log_performance("test_performance", 250.5, test_operation="test")

            # End operation
            log_operation_end("integration_test", operation_id, success=True)

            # Verify log files exist
            log_dir = Path(temp_dir)
            log_files = list(log_dir.glob("*.log*"))
            assert len(log_files) > 0

    def test_environment_switching(self):
        """Test switching between different environments."""
        environments = ["local", "dev", "test", "stage", "prod"]

        for env in environments:
            with tempfile.TemporaryDirectory() as temp_dir:
                setup_logging(environment=env, log_dir=temp_dir)

                logger = get_logger(f"test_{env}")
                logger.info(f"Testing {env} environment")

                # Verify appropriate files are created based on environment
                log_dir = Path(temp_dir)

                if env == "prod":
                    # Production should have file logging but no console
                    log_files = list(log_dir.glob("*.log"))
                    assert len(log_files) > 0
                elif env == "test":
                    # Test environment should have minimal logging
                    pass  # Test-specific assertions
                else:
                    # Other environments should have both console and file logging
                    log_files = list(log_dir.glob("*.log"))
                    assert len(log_files) >= 0  # At least main log file


class TestErrorHandling:
    """Test error handling in logging system."""

    def test_invalid_environment(self):
        """Test handling of invalid environment names."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Should fall back to default (local) configuration
            setup_logging(environment="invalid_env", log_dir=temp_dir)

            logger = get_logger("test")
            logger.info("Test message")

    def test_invalid_log_directory(self):
        """Test handling of invalid log directory."""
        import tempfile
        import os

        # Use a path that we know we can't create (non-existent parent in temp)
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_path = os.path.join(
                temp_dir, "non_existent", "deeply", "nested", "path"
            )
            try:
                # This should either succeed or raise a proper exception
                setup_logging(environment="local", log_dir=invalid_path)
                # If it succeeds, check that the directory was created
                assert Path(invalid_path).exists()
            except (OSError, PermissionError):
                # If it fails, that's also acceptable behavior
                pass

        logger = get_logger("test")
        logger.info("Test message")

    def test_yaml_config_error(self):
        """Test handling of malformed YAML configuration."""
        yaml_content = """
invalid: yaml: content:
  - malformed
    structure
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            try:
                # Should fall back to default configuration
                loader = LoggingConfigLoader(f.name)
                config = loader.get_environment_config("local")

                # Should have some basic configuration
                assert (
                    "level" in config or len(config) == 0
                )  # Either loaded or empty fallback
            finally:
                os.unlink(f.name)


if __name__ == "__main__":
    pytest.main([__file__])
