#!/usr/bin/env python3
"""
Comprehensive logging demonstration for ODCS Converter.

This script demonstrates all the logging features including:
- Environment-specific configurations
- Performance tracking
- Correlation ID tracking
- Structured logging
- Sensitive data masking
- Operation lifecycle logging
- Error handling and stack traces
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from odcs_converter.logging_config import (
    setup_logging,
    get_logger,
    set_correlation_id,
    get_correlation_id,
    LogContext,
    log_operation_start,
    log_operation_end,
    log_performance,
)
from odcs_converter.logging_utils import (
    PerformanceTracker,
    SensitiveDataMasker,
    LogFormatter,
    ContextualLogger,
    cleanup_old_logs,
)


def demo_environment_configurations():
    """Demonstrate different environment configurations."""
    print("🌍 Testing Different Environment Configurations")
    print("=" * 60)

    environments = ["local", "dev", "test", "stage", "prod"]

    for env in environments:
        print(f"\n📁 Testing {env.upper()} environment:")

        # Create environment-specific log directory
        log_dir = Path(f"demo_logs/{env}")
        log_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging for this environment
        setup_logging(environment=env, log_dir=str(log_dir))

        # Get logger and test
        logger = get_logger(f"demo.{env}")
        logger.info(f"Testing {env} environment", environment=env)
        logger.debug(f"Debug message for {env}")
        logger.warning(f"Warning message for {env}")

        # Check created files
        log_files = list(log_dir.glob("*.log*"))
        print(f"  Log files created: {len(log_files)}")
        for log_file in log_files:
            size = log_file.stat().st_size
            print(f"    - {log_file.name}: {LogFormatter.format_file_size(size)}")


def demo_correlation_id_tracking():
    """Demonstrate correlation ID tracking across operations."""
    print("\n🔗 Testing Correlation ID Tracking")
    print("=" * 60)

    log_dir = Path("demo_logs/correlation")
    log_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(environment="dev", log_dir=str(log_dir))

    # Test automatic correlation ID
    logger = get_logger("correlation_demo")
    logger.info("Message with auto-generated correlation ID")

    # Test custom correlation ID
    custom_id = "USER-REQUEST-12345"
    old_id = set_correlation_id(custom_id)
    logger.info(
        "Message with custom correlation ID", user_id="john_doe", action="login"
    )

    # Test correlation ID context manager
    with LogContext("BATCH-PROCESS-001", operation="data_import", batch_size=1000):
        logger.info("Starting batch process")
        time.sleep(0.1)
        logger.info("Batch process completed successfully")

    # Restore original correlation ID
    set_correlation_id(old_id)
    logger.info("Back to original correlation ID")

    print(f"  Current correlation ID: {get_correlation_id()}")


def demo_performance_tracking():
    """Demonstrate performance tracking capabilities."""
    print("\n⚡ Testing Performance Tracking")
    print("=" * 60)

    log_dir = Path("demo_logs/performance")
    log_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(environment="dev", log_dir=str(log_dir))

    # Initialize performance tracker
    tracker = PerformanceTracker(
        {
            "enabled": True,
            "threshold_ms": 50,  # Log operations taking > 50ms
            "include_args": True,
            "include_result": True,
        }
    )

    @tracker.track_performance("fast_operation")
    def fast_function(message):
        """A fast operation."""
        time.sleep(0.02)  # 20ms
        return f"Processed: {message}"

    @tracker.track_performance("slow_operation")
    def slow_function(data_size):
        """A slow operation that will be logged."""
        time.sleep(0.1)  # 100ms
        return {"processed_items": data_size, "status": "success"}

    @tracker.track_performance("failing_operation")
    def failing_function():
        """An operation that fails."""
        time.sleep(0.05)
        raise ValueError("Simulated error for demo")

    # Test the functions
    print("  Running fast operation (won't be logged due to threshold)...")
    result1 = fast_function("Hello World")

    print("  Running slow operation (will be logged)...")
    result2 = slow_function(500)

    print("  Running failing operation (will be logged with error)...")
    try:
        failing_function()
    except ValueError as e:
        print(f"    Caught expected error: {e}")

    # Manual performance logging
    log_performance("manual_operation", 250.5, items_processed=100, success=True)


def demo_sensitive_data_masking():
    """Demonstrate sensitive data masking."""
    print("\n🔐 Testing Sensitive Data Masking")
    print("=" * 60)

    log_dir = Path("demo_logs/security")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure security settings
    os.environ.update(
        {
            "ODCS_SECURITY_MASK_SENSITIVE": "true",
            "ODCS_SECURITY_SENSITIVE_PATTERNS": "password,token,key,secret,auth,credential,api_key",
            "ODCS_SECURITY_MASK_CHARACTER": "*",
        }
    )

    setup_logging(environment="prod", log_dir=str(log_dir))

    masker = SensitiveDataMasker(
        {
            "mask_sensitive_fields": True,
            "sensitive_patterns": ["password", "token", "key", "secret"],
            "mask_character": "*",
        }
    )

    # Test message masking
    sensitive_message = "User logged in with password=secret123 and api_token=abc456xyz"
    masked_message = masker.mask_message(sensitive_message)

    print(f"  Original: {sensitive_message}")
    print(f"  Masked:   {masked_message}")

    # Test dictionary masking
    sensitive_data = {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "super_secret_password",
        "api_key": "sk-1234567890abcdef",
        "user_preferences": {"theme": "dark", "notifications": True},
        "auth_token": "bearer_token_xyz789",
    }

    masked_data = masker.mask_dict(sensitive_data)

    print("\n  Original data:")
    print(f"    {json.dumps(sensitive_data, indent=2)}")
    print("\n  Masked data:")
    print(f"    {json.dumps(masked_data, indent=2)}")

    # Log both versions
    logger = get_logger("security_demo")
    logger.info("Processing user data", **sensitive_data)


def demo_operation_lifecycle():
    """Demonstrate operation lifecycle logging."""
    print("\n🔄 Testing Operation Lifecycle Logging")
    print("=" * 60)

    log_dir = Path("demo_logs/operations")
    log_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(environment="dev", log_dir=str(log_dir))

    logger = get_logger("operation_demo")

    # Successful operation
    op_id1 = log_operation_start(
        "data_conversion",
        input_file="contract.json",
        output_file="contract.xlsx",
        user="demo_user",
    )

    with LogContext(op_id1, operation="data_conversion"):
        logger.info("Loading input file")
        time.sleep(0.05)
        logger.info("Processing data contract")
        time.sleep(0.1)
        logger.info("Generating Excel workbook")
        time.sleep(0.08)
        logger.info("Saving output file")

    log_operation_end(
        "data_conversion",
        op_id1,
        success=True,
        records_processed=150,
        output_size="2.3 MB",
    )

    # Failed operation
    op_id2 = log_operation_start("validation", schema_version="3.0.2", strict_mode=True)

    with LogContext(op_id2, operation="validation"):
        logger.info("Starting schema validation")
        time.sleep(0.03)
        logger.error(
            "Validation failed: Missing required field 'dataContractSpecification'"
        )

    log_operation_end(
        "validation",
        op_id2,
        success=False,
        error="Schema validation failed",
        validation_errors=3,
    )


def demo_contextual_logging():
    """Demonstrate contextual logging with rich context."""
    print("\n📝 Testing Contextual Logging")
    print("=" * 60)

    log_dir = Path("demo_logs/contextual")
    log_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(environment="dev", log_dir=str(log_dir))

    # Create contextual logger
    base_logger = ContextualLogger("contextual_demo")

    # Add user context
    user_logger = base_logger.with_context(
        user_id="user_123", session_id="sess_abc789", ip_address="192.168.1.100"
    )

    user_logger.info("User started conversion process")

    # Add request context
    request_logger = user_logger.with_context(
        request_id="req_456def", endpoint="/api/convert", method="POST"
    )

    request_logger.info("Processing conversion request")
    request_logger.debug("Request payload validated")

    # Add processing context
    process_logger = request_logger.with_context(
        process_id="proc_789ghi", worker_id="worker_001", queue_name="conversion_queue"
    )

    process_logger.info("Starting background processing")
    process_logger.warning("High memory usage detected", memory_usage="85%")
    process_logger.info("Processing completed successfully")


def demo_error_handling():
    """Demonstrate error handling and stack traces."""
    print("\n❌ Testing Error Handling and Stack Traces")
    print("=" * 60)

    log_dir = Path("demo_logs/errors")
    log_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(environment="dev", log_dir=str(log_dir))

    logger = get_logger("error_demo")

    def nested_function_level_3():
        """Third level function that raises an error."""
        raise ValueError("This is a nested error for demonstration")

    def nested_function_level_2():
        """Second level function."""
        logger.debug("Entering nested function level 2")
        nested_function_level_3()

    def nested_function_level_1():
        """First level function."""
        logger.info("Starting complex operation")
        try:
            nested_function_level_2()
        except ValueError as e:
            logger.error("Error in nested operation", error=str(e))
            raise RuntimeError("Complex operation failed") from e

    # Test exception logging
    try:
        nested_function_level_1()
    except RuntimeError as e:
        logger.exception("Top-level error caught", operation="demo_error_handling")

        # Demonstrate exception chain formatting
        formatter = LogFormatter()
        chain = formatter.format_exception_chain(e)
        logger.error("Exception chain", chain=chain)


def demo_structured_logging_analysis():
    """Demonstrate structured logging for analysis."""
    print("\n📊 Testing Structured Logging for Analysis")
    print("=" * 60)

    log_dir = Path("demo_logs/analysis")
    log_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(environment="prod", log_dir=str(log_dir))

    logger = get_logger("analysis_demo")

    # Simulate various events for analysis
    events = [
        {"event": "user_login", "user": "alice", "success": True, "duration_ms": 150},
        {
            "event": "data_upload",
            "user": "alice",
            "file_size_mb": 2.5,
            "success": True,
            "duration_ms": 1200,
        },
        {
            "event": "conversion",
            "user": "alice",
            "input_format": "json",
            "output_format": "excel",
            "success": True,
            "duration_ms": 3500,
        },
        {
            "event": "user_login",
            "user": "bob",
            "success": False,
            "error": "invalid_credentials",
            "duration_ms": 50,
        },
        {"event": "user_login", "user": "bob", "success": True, "duration_ms": 120},
        {
            "event": "conversion",
            "user": "bob",
            "input_format": "excel",
            "output_format": "yaml",
            "success": False,
            "error": "invalid_schema",
            "duration_ms": 800,
        },
    ]

    for event in events:
        logger.info(f"Event: {event['event']}", **event)

    # Show analysis example
    structured_file = (
        log_dir / f"odcs-converter-structured-{datetime.now().strftime('%Y%m%d')}.jsonl"
    )
    if structured_file.exists():
        print(f"\n  Structured log file created: {structured_file.name}")
        print(
            f"  File size: {LogFormatter.format_file_size(structured_file.stat().st_size)}"
        )
        print("\n  Sample analysis (using jq):")
        print("    # Count events by type:")
        print("    cat logs/*.jsonl | jq -r '.record.extra.event' | sort | uniq -c")
        print("\n    # Average duration by event type:")
        print(
            "    cat logs/*.jsonl | jq -r 'select(.record.extra.duration_ms) | [.record.extra.event, .record.extra.duration_ms] | @csv'"
        )


def demo_log_rotation_and_cleanup():
    """Demonstrate log rotation and cleanup."""
    print("\n🔄 Testing Log Rotation and Cleanup")
    print("=" * 60)

    log_dir = Path("demo_logs/rotation")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Set small rotation size for demo
    os.environ.update(
        {
            "ODCS_LOG_ROTATION": "1 KB",
            "ODCS_LOG_RETENTION": "1 day",
        }
    )

    setup_logging(environment="dev", log_dir=str(log_dir))
    logger = get_logger("rotation_demo")

    # Generate lots of log messages to trigger rotation
    print("  Generating log messages to trigger rotation...")
    for i in range(50):
        logger.info(
            f"Log message {i:03d} with some additional content to increase size",
            iteration=i,
            timestamp=datetime.now().isoformat(),
        )

    # Show created files
    log_files = sorted(log_dir.glob("*.log*"))
    print(f"\n  Log files after rotation ({len(log_files)} files):")
    for log_file in log_files:
        size = log_file.stat().st_size
        print(f"    - {log_file.name}: {LogFormatter.format_file_size(size)}")

    # Demo cleanup
    print("\n  Testing cleanup function...")
    cleanup_old_logs(log_dir, retention_days=0)  # Remove all files for demo

    remaining_files = list(log_dir.glob("*.log*"))
    print(f"  Files after cleanup: {len(remaining_files)}")


def main():
    """Run all logging demonstrations."""
    print("🚀 ODCS Converter Logging System Demonstration")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Create main demo directory
    demo_dir = Path("demo_logs")
    demo_dir.mkdir(exist_ok=True)

    try:
        # Run all demonstrations
        demo_environment_configurations()
        demo_correlation_id_tracking()
        demo_performance_tracking()
        demo_sensitive_data_masking()
        demo_operation_lifecycle()
        demo_contextual_logging()
        demo_error_handling()
        demo_structured_logging_analysis()
        demo_log_rotation_and_cleanup()

        print("\n" + "=" * 80)
        print("✅ All logging demonstrations completed successfully!")
        print(f"📁 Log files created in: {demo_dir.absolute()}")

        # Summary of created files
        total_files = sum(1 for _ in demo_dir.rglob("*.log*"))
        total_size = sum(f.stat().st_size for f in demo_dir.rglob("*.log*"))

        print(f"📊 Summary:")
        print(f"   - Total log files: {total_files}")
        print(f"   - Total size: {LogFormatter.format_file_size(total_size)}")
        print(f"   - Environments tested: local, dev, test, stage, prod")
        print(f"   - Features demonstrated: 8 major features")

        print(f"\n🔍 To explore the logs:")
        print(f"   find {demo_dir} -name '*.log*' -exec ls -lh {{}} \\;")
        print(f"   find {demo_dir} -name '*.jsonl' -exec head -1 {{}} \\; | jq")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
