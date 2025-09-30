# Logging Guide for ODCS Converter

The ODCS Converter features a comprehensive logging system built on [loguru](https://loguru.readthedocs.io/), providing flexible, environment-aware logging with advanced features like performance tracking, sensitive data masking, and structured logging.

## Table of Contents

- [Quick Start](#quick-start)
- [Environment Configuration](#environment-configuration)
- [Log Levels and Verbosity](#log-levels-and-verbosity)
- [Log Output Formats](#log-output-formats)
- [Performance Tracking](#performance-tracking)
- [Sensitive Data Protection](#sensitive-data-protection)
- [Configuration Files](#configuration-files)
- [Environment Variables](#environment-variables)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Basic Usage

The simplest way to control logging is through CLI flags:

```bash
# Default logging (INFO level)
odcs-converter convert input.json output.xlsx

# Verbose logging (DEBUG level)
odcs-converter convert input.json output.xlsx --verbose

# Quiet logging (ERROR level only)
odcs-converter convert input.json output.xlsx --quiet

# Specify environment
odcs-converter convert input.json output.xlsx --env prod
```

### Environment-Based Configuration

Set the environment to automatically configure logging:

```bash
# Set environment variable
export ODCS_ENV=dev
odcs-converter convert input.json output.xlsx

# Or use CLI flag
odcs-converter convert input.json output.xlsx --env dev
```

## Environment Configuration

The logging system supports five predefined environments, each optimized for different use cases:

### Local Development (`local`)
- **Level**: DEBUG
- **Console**: Enabled with colors and detailed formatting
- **File**: Enabled with rotation (10 MB) and 7-day retention
- **Structured**: Disabled
- **Features**: Full backtraces and diagnostics

```bash
export ODCS_ENV=local
# or
odcs-converter --env local [command]
```

### Development (`dev`)
- **Level**: DEBUG
- **Console**: Enabled with colors
- **File**: Enabled with rotation (50 MB) and 14-day retention
- **Structured**: Enabled (JSON format)
- **Features**: Full backtraces and diagnostics

### Test (`test`)
- **Level**: WARNING
- **Console**: Disabled
- **File**: Enabled with rotation (20 MB) and 3-day retention
- **Structured**: Disabled
- **Features**: Minimal diagnostics, queued logging

### Staging (`stage`)
- **Level**: INFO
- **Console**: Enabled (no colors)
- **File**: Enabled with rotation (100 MB) and 30-day retention
- **Structured**: Enabled
- **Features**: Backtraces enabled, queued logging

### Production (`prod`)
- **Level**: INFO
- **Console**: Disabled
- **File**: Enabled with rotation (500 MB) and 90-day retention
- **Structured**: Enabled
- **Features**: No diagnostics, queued logging for performance

## Log Levels and Verbosity

### Available Log Levels

| Level | Description | When to Use |
|-------|-------------|-------------|
| `DEBUG` | Detailed diagnostic information | Development, troubleshooting |
| `INFO` | General operational messages | Normal operation tracking |
| `WARNING` | Warning messages for potential issues | Non-critical problems |
| `ERROR` | Error messages for failures | Failed operations |
| `CRITICAL` | Critical errors requiring immediate attention | System failures |

### Controlling Verbosity

```bash
# Debug level - most verbose
odcs-converter convert input.json output.xlsx --verbose

# Info level - standard verbosity
odcs-converter convert input.json output.xlsx

# Error level only - minimal output
odcs-converter convert input.json output.xlsx --quiet

# Override via environment variable
export ODCS_LOG_LEVEL=DEBUG
odcs-converter convert input.json output.xlsx
```

## Log Output Formats

### Console Output

Console logs feature rich formatting with colors and structured information:

```
2024-01-15 10:30:45 | INFO     | odcs_converter.cli:convert:285 | Starting conversion
2024-01-15 10:30:45 | DEBUG    | odcs_converter.generator:generate_from_file:45 | Loading ODCS file
2024-01-15 10:30:46 | INFO     | odcs_converter.cli:convert:320 | Conversion completed successfully
```

### File Output

File logs include correlation IDs for request tracking:

```
2024-01-15 10:30:45.123 | INFO     | odcs_converter.cli:convert:285 | abc12345 | Starting conversion
```

### Structured Output (JSON Lines)

When structured logging is enabled, logs are written in JSON Lines format:

```json
{"timestamp": "2024-01-15T10:30:45.123456", "level": "INFO", "logger": "odcs_converter.cli", "function": "convert", "line": 285, "message": "Starting conversion", "correlation_id": "abc12345", "operation": "convert", "input_source": "input.json"}
```

## Performance Tracking

The logging system automatically tracks performance of key operations:

### Automatic Performance Logging

Operations taking longer than the threshold (default: 1000ms) are automatically logged:

```
2024-01-15 10:30:47 | INFO | Performance: generator.generate_from_dict took 1250.50ms
```

### Configuration

```bash
# Enable performance tracking
export ODCS_PERFORMANCE_ENABLED=true

# Set threshold (operations slower than this will be logged)
export ODCS_PERFORMANCE_THRESHOLD_MS=500

# Include function arguments in performance logs
export ODCS_PERFORMANCE_LOG_ARGS=true

# Include function results in performance logs
export ODCS_PERFORMANCE_LOG_RESULT=true
```

### Performance Metrics

The system tracks:
- **Duration**: Execution time in milliseconds
- **Success/Failure**: Whether the operation completed successfully
- **Operation Name**: Hierarchical operation identifier
- **Arguments**: Function parameters (if enabled)
- **Results**: Function output metadata (if enabled)

## Sensitive Data Protection

The logging system automatically masks sensitive information:

### Automatic Masking

Sensitive patterns are automatically detected and masked:

```bash
# Before masking
"User authenticated with password=secret123 and token=abc456xyz"

# After masking
"User authenticated with password=******** and token=********"
```

### Configuration

```bash
# Enable sensitive data masking
export ODCS_SECURITY_MASK_SENSITIVE=true

# Define sensitive patterns (comma-separated)
export ODCS_SECURITY_SENSITIVE_PATTERNS=password,token,key,secret,auth,credential

# Set masking character
export ODCS_SECURITY_MASK_CHARACTER="*"

# Set maximum field length
export ODCS_SECURITY_MAX_FIELD_LENGTH=100
```

### Default Sensitive Patterns

The system automatically masks fields containing:
- `password`
- `token`
- `key`
- `secret`
- `auth`
- `credential`

## Configuration Files

### YAML Configuration

Create a `config/logging.yaml` file for advanced configuration:

```yaml
defaults:
  app_name: "odcs-converter"
  log_dir: "logs"

environments:
  custom:
    level: "INFO"
    console:
      enabled: true
      format: "{time:HH:mm:ss} | {level} | {message}"
      colorize: true
    file:
      enabled: true
      format: "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}"
      rotation: "100 MB"
      retention: "30 days"
      compression: "gz"
    structured:
      enabled: true
      format: "json"
    features:
      backtrace: true
      diagnose: true
      enqueue: false
```

### Custom Formatters

Define custom log formats:

```yaml
formatters:
  simple: "{time:HH:mm:ss} | {level} | {message}"
  detailed: "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}"
  json_compact: '{"time":"{time:ISO8601}","level":"{level}","message":"{message}"}'
```

## Environment Variables

### Core Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `ODCS_ENV` | Environment name | `local` | `prod` |
| `ODCS_LOG_LEVEL` | Log level | `INFO` | `DEBUG` |
| `ODCS_LOG_DIR` | Log directory | `logs` | `/var/log/odcs` |
| `ODCS_LOG_CONSOLE` | Enable console logging | `true` | `false` |
| `ODCS_LOG_FILE` | Enable file logging | `true` | `false` |
| `ODCS_LOG_STRUCTURED` | Enable structured logging | `false` | `true` |

### File Management

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `ODCS_LOG_ROTATION` | Log rotation size | `10 MB` | `100 MB` |
| `ODCS_LOG_RETENTION` | Log retention period | `7 days` | `30 days` |
| `ODCS_LOG_COMPRESSION` | Compression format | `zip` | `gz` |

### Complete Example

```bash
# Production environment configuration
export ODCS_ENV=prod
export ODCS_LOG_LEVEL=INFO
export ODCS_LOG_DIR=/var/log/odcs-converter
export ODCS_LOG_CONSOLE=false
export ODCS_LOG_FILE=true
export ODCS_LOG_STRUCTURED=true
export ODCS_LOG_ROTATION="500 MB"
export ODCS_LOG_RETENTION="90 days"
export ODCS_LOG_COMPRESSION=gz
export ODCS_PERFORMANCE_ENABLED=true
export ODCS_PERFORMANCE_THRESHOLD_MS=2000
export ODCS_SECURITY_MASK_SENSITIVE=true
```

## Advanced Features

### Correlation ID Tracking

Each operation gets a unique correlation ID for request tracking:

```bash
# Set custom correlation ID
export ODCS_LOG_CORRELATION_ID=my-custom-id-123

# View correlation ID in logs
odcs-converter convert input.json output.xlsx --verbose
```

Log output includes the correlation ID:
```
2024-01-15 10:30:45.123 | INFO | odcs_converter.cli:convert:285 | my-custom-id-123 | Starting conversion
```

### Operation Lifecycle Tracking

The system automatically tracks operation start and end:

```
2024-01-15 10:30:45 | INFO | Starting operation: convert
2024-01-15 10:30:47 | INFO | Operation convert completed successfully
```

### Rich Console Integration

The logging system integrates with Rich for beautiful console output:

```bash
# Enable Rich integration
export ODCS_RICH_ENABLED=true
export ODCS_RICH_FORCE_TERMINAL=true
```

### Log File Structure

Logs are organized into multiple files:

```
logs/
├── odcs-converter-20240115.log          # Main application log
├── odcs-converter-error-20240115.log    # Error-only log
├── odcs-converter-structured-20240115.jsonl  # Structured logs
└── odcs-converter-performance-20240115.log   # Performance metrics
```

## Troubleshooting

### Common Issues

#### Logs Not Appearing

1. **Check log level**: Ensure the log level allows your messages
   ```bash
   export ODCS_LOG_LEVEL=DEBUG
   ```

2. **Verify log directory**: Ensure the log directory is writable
   ```bash
   export ODCS_LOG_DIR=./logs
   mkdir -p ./logs
   ```

3. **Check console logging**: Enable console output for immediate feedback
   ```bash
   export ODCS_LOG_CONSOLE=true
   ```

#### Performance Issues

1. **Disable structured logging** in high-throughput scenarios:
   ```bash
   export ODCS_LOG_STRUCTURED=false
   ```

2. **Increase performance threshold**:
   ```bash
   export ODCS_PERFORMANCE_THRESHOLD_MS=5000
   ```

3. **Enable queued logging**:
   ```bash
   export ODCS_ENV=prod  # Uses queued logging by default
   ```

#### File Permission Issues

1. **Check directory permissions**:
   ```bash
   ls -la logs/
   chmod 755 logs/
   ```

2. **Use user-writable directory**:
   ```bash
   export ODCS_LOG_DIR=$HOME/.odcs-converter/logs
   ```

### Debug Mode

Enable comprehensive debugging:

```bash
export ODCS_ENV=local
export ODCS_LOG_LEVEL=DEBUG
export ODCS_PERFORMANCE_ENABLED=true
export ODCS_PERFORMANCE_THRESHOLD_MS=0
odcs-converter convert input.json output.xlsx --verbose
```

### Log Analysis

#### Parsing Structured Logs

Use `jq` to analyze JSON logs:

```bash
# View all error messages
cat logs/odcs-converter-structured-*.jsonl | jq 'select(.level == "ERROR") | .message'

# View performance metrics
cat logs/odcs-converter-structured-*.jsonl | jq 'select(.performance == true) | {operation, duration_ms}'

# Find operations by correlation ID
cat logs/odcs-converter-structured-*.jsonl | jq 'select(.correlation_id == "abc12345")'
```

#### Log Rotation Monitoring

Check log file sizes:

```bash
# View current log files
ls -lh logs/

# Monitor log rotation
watch "ls -lh logs/"
```

### Getting Help

If you encounter logging issues:

1. **Enable debug logging**: `export ODCS_LOG_LEVEL=DEBUG`
2. **Check environment variables**: `env | grep ODCS_`
3. **Verify configuration**: Review your `config/logging.yaml`
4. **Test basic functionality**: `odcs-converter version --verbose`

For additional support, include log output when reporting issues.

## Best Practices

### Development
- Use `local` or `dev` environment
- Enable console logging with colors
- Set DEBUG level for detailed information
- Enable performance tracking with low threshold

### Testing
- Use `test` environment
- Disable console logging
- Set WARNING level to reduce noise
- Enable file logging for CI/CD analysis

### Production
- Use `prod` environment
- Disable console logging
- Enable structured logging for analysis
- Set appropriate rotation and retention policies
- Enable sensitive data masking
- Monitor log file sizes and rotation

### Performance
- Use queued logging in high-throughput scenarios
- Set appropriate performance thresholds
- Disable argument/result logging in production
- Monitor log file sizes and implement rotation

The ODCS Converter logging system provides comprehensive observability into your data conversion operations while maintaining performance and security best practices.