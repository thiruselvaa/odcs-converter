# Makefile Usage Guide for ODCS Converter

This guide provides comprehensive documentation for using the ODCS Converter Makefile, which streamlines development, testing, and deployment workflows.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation and Setup](#installation-and-setup)
- [CLI Operations](#cli-operations)
- [Testing](#testing)
- [Logging and Monitoring](#logging-and-monitoring)
- [Code Quality](#code-quality)
- [Environment Configuration](#environment-configuration)
- [Build and Release](#build-and-release)
- [Cleanup](#cleanup)
- [Common Workflows](#common-workflows)
- [Troubleshooting](#troubleshooting)

## Quick Start

```bash
# Get started quickly
make quickstart       # Complete setup: install, dev environment, test directories
make cli-demo        # See the CLI in action
make test-fast       # Run quick tests
make logs-demo       # Explore logging features
```

## Installation and Setup

### Basic Installation

```bash
make install         # Install with uv (recommended - fast!)
make install-pip     # Alternative: Install with pip
```

### Development Setup

```bash
make dev            # Setup development environment with pre-commit hooks
make dev-clean      # Clean reinstall for development (removes .venv)
make setup-test-dirs # Create necessary test directories
```

### Update Dependencies

```bash
make update-deps    # Update all dependencies to latest versions
```

## CLI Operations

### Basic CLI Commands

```bash
make cli-version    # Show version and system information
make cli-help       # Display comprehensive help
make cli-formats    # List supported file formats
make cli-demo       # Run a demonstration of CLI features
```

### Conversion Examples

```bash
# The cli-convert target shows usage examples
make cli-convert

# Actual conversions (run these directly)
uv run odcs-converter convert input.json output.xlsx
uv run odcs-converter to-excel contract.yaml workbook.xlsx
uv run odcs-converter to-odcs data.xlsx contract.json --validate
```

## Testing

### Test Suites

```bash
make test           # Run all tests (warnings suppressed)
make test-unit      # Unit tests only
make test-integration # Integration tests only
make test-e2e       # End-to-end tests only
```

### Test Categories

```bash
make test-fast      # Quick tests (unit + integration)
make test-slow      # Slow tests (e2e + performance)
make test-smoke     # Smoke tests for basic functionality
make test-cli       # CLI-specific tests
make test-logging   # Logging system tests
```

### Advanced Testing

```bash
make test-coverage  # Generate detailed coverage report (HTML + terminal)
make test-parallel  # Run tests in parallel for speed
make test-watch     # Auto-run tests on file changes
make test-debug     # Run with verbose debugging output
```

### Specific Test Categories

```bash
make test-excel     # Excel file operation tests
make test-yaml      # YAML operation tests
make test-conversion # Data conversion tests
make test-validation # Validation tests
make test-performance # Performance benchmarks
```

## Logging and Monitoring

### Logging Demonstration

```bash
make logs-demo      # Run comprehensive logging demo
make logs-clean     # Clean all log files
make logs-tail      # Tail current log files in real-time
make logs-analyze   # Analyze structured logs with jq
```

### Log Management

```bash
# Clean logs before starting fresh
make logs-clean

# Run your application
make cli-demo

# Analyze the logs
make logs-analyze

# Watch logs in real-time
make logs-tail
```

## Code Quality

### Quality Checks

```bash
make lint           # Run ruff linting
make format         # Format with black and ruff
make type-check     # Type checking with mypy
make quality        # Run all quality checks
make quality-fix    # Auto-fix issues where possible
```

### Check for Warnings

```bash
make check-warnings # Verify no Python warnings in imports or runtime
```

## Environment Configuration

### Environment Setup

```bash
make env-local      # Configure for local development
make env-dev        # Configure for development server
make env-prod       # Configure for production
```

### Show Current Configuration

```bash
make show-config    # Display current environment settings
```

### Environment Files Created

Each environment command creates a `.env` file with appropriate settings:

**Local Environment (`make env-local`)**:
```env
ODCS_ENV=local
ODCS_LOG_LEVEL=DEBUG
ODCS_LOG_DIR=logs
ODCS_LOG_CONSOLE=true
ODCS_LOG_FILE=true
```

**Development Environment (`make env-dev`)**:
```env
ODCS_ENV=dev
ODCS_LOG_LEVEL=DEBUG
ODCS_LOG_DIR=logs
ODCS_LOG_CONSOLE=true
ODCS_LOG_FILE=true
ODCS_LOG_STRUCTURED=true
```

**Production Environment (`make env-prod`)**:
```env
ODCS_ENV=prod
ODCS_LOG_LEVEL=INFO
ODCS_LOG_DIR=/var/log/odcs-converter
ODCS_LOG_CONSOLE=false
ODCS_LOG_FILE=true
ODCS_LOG_STRUCTURED=true
ODCS_LOG_ROTATION=500 MB
ODCS_LOG_RETENTION=90 days
```

## Build and Release

### Building

```bash
make build          # Build distribution packages
make build-check    # Validate package build with twine
```

### Release Process

```bash
make release-dry    # Dry run: quality checks + tests + build
make all           # Complete workflow: quality + test + build
```

## Cleanup

### Selective Cleanup

```bash
make clean          # Clean build artifacts
make clean-test     # Clean test artifacts only
make clean-logs     # Clean log files only
```

### Complete Cleanup

```bash
make clean-all      # Remove everything (artifacts + logs + cache)
```

## Common Workflows

### Daily Development

```bash
# Morning setup
make dev            # Ensure environment is ready
make show-config    # Check configuration

# Before coding
make test-fast      # Run quick tests
make quality        # Check code quality

# After changes
make format         # Format code
make test-unit      # Test your changes
make lint           # Check for issues
```

### Before Committing

```bash
make quality-fix    # Auto-fix formatting issues
make test-fast      # Run tests
make check-warnings # Ensure no warnings
```

### Pre-Release Checklist

```bash
make clean-all      # Start fresh
make dev            # Setup environment
make quality        # Code quality checks
make test           # Full test suite
make test-coverage  # Check coverage metrics
make build-check    # Validate package
make release-dry    # Final validation
```

### Debugging Issues

```bash
# Check for warnings
make check-warnings

# Run specific failing tests with debug info
make test-debug

# Check logging system
make logs-demo
make logs-analyze

# Clean everything and start over
make clean-all
make dev-clean
make test
```

## Troubleshooting

### Common Issues and Solutions

#### Tests Failing with Import Errors

```bash
make clean-all
make install
make test
```

#### Log Files Not Created

```bash
make logs-clean
make setup-test-dirs
make env-local  # or env-dev
make cli-demo
```

#### Warning Messages Appearing

```bash
make check-warnings  # Identify warnings
make quality-fix     # Fix code issues
```

#### Coverage Report Not Generated

```bash
make clean-test
make test-coverage
# Report will be in htmlcov/index.html
```

#### Parallel Tests Failing

```bash
# Install pytest-xdist first
uv add pytest-xdist --dev
make test-parallel
```

### Performance Tips

1. **Use parallel testing** for faster test runs:
   ```bash
   make test-parallel
   ```

2. **Run only relevant tests** during development:
   ```bash
   make test-unit      # When working on business logic
   make test-cli       # When working on CLI
   ```

3. **Use watch mode** for automatic testing:
   ```bash
   make test-watch     # Tests run automatically on file save
   ```

4. **Clean regularly** to avoid stale artifacts:
   ```bash
   make clean-test     # Before running tests
   make clean-logs     # When logs get too large
   ```

## Advanced Usage

### Custom Test Runs

```bash
# Run specific test file
uv run pytest tests/unit/test_models.py -v

# Run tests matching pattern
uv run pytest -k "test_conversion" -v

# Run with specific markers
uv run pytest -m "not slow" -v
```

### Logging Analysis

```bash
# Find all errors in logs
find logs -name "*.log" -exec grep ERROR {} \;

# Analyze performance metrics
cat logs/*structured*.jsonl | \
  jq 'select(.record.extra.performance == true) | 
      {op: .record.extra.operation, ms: .record.extra.duration_ms}' | \
  jq -s 'group_by(.op) | map({op: .[0].op, avg_ms: (map(.ms) | add / length)})'
```

### Environment Variable Overrides

```bash
# Override environment for single command
ODCS_ENV=prod make cli-version

# Set custom log level
ODCS_LOG_LEVEL=DEBUG make cli-demo

# Use custom log directory
ODCS_LOG_DIR=/tmp/odcs-logs make logs-demo
```

## Best Practices

1. **Always run `make quickstart` after cloning** the repository
2. **Use `make test-fast` frequently** during development
3. **Run `make quality-fix` before committing** code
4. **Use `make check-warnings` to ensure** clean output
5. **Run `make all` before releases** for complete validation
6. **Keep logs clean** with regular `make clean-logs`
7. **Use environment-specific configs** (`make env-*`) for different deployments
8. **Monitor performance** with `make test-performance` regularly
9. **Generate coverage reports** with `make test-coverage` to identify gaps
10. **Use `make release-dry` to validate** before actual releases

## Make Target Reference

For a complete list of all available targets, run:

```bash
make help
```

This will display all targets with descriptions, organized by category:
- 🚀 Setup and Installation
- 🧪 Testing
- 📊 CLI Commands
- 📝 Logging and Monitoring
- ✨ Code Quality
- 🏗️ Build and Release
- 🧹 Cleanup
- 🔧 Development Utilities

Each category provides specialized commands for different aspects of the development workflow.