# ODCS Converter Makefile
# Comprehensive build, test, and development targets
# All Python/CLI invocations run inside the uv-managed virtualenv via $(RUN)

# uv tool and virtualenv runner
UV := uv
RUN := $(UV) run
PY  := $(RUN) python

.PHONY: help
help:
	@echo "╭─────────────────────────────────────────────────────────────────╮"
	@echo "│                    ODCS Converter Makefile                      │"
	@echo "╰─────────────────────────────────────────────────────────────────╯"
	@echo ""
	@echo "🚀 Setup and Installation:"
	@echo "  install          - Install package with uv (recommended)"
	@echo "  install-pip      - Install package with pip (fallback)"
	@echo "  dev              - Setup complete development environment"
	@echo "  dev-clean        - Clean install for development"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test             - Run all tests without warnings"
	@echo "  test-unit        - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-e2e         - Run end-to-end tests only"
	@echo "  test-fast        - Run fast tests (unit + integration)"
	@echo "  test-slow        - Run slow tests (e2e + performance)"
	@echo "  test-smoke       - Run smoke tests"
	@echo "  test-coverage    - Run tests with detailed coverage report"
	@echo "  test-watch       - Run tests in watch mode"
	@echo "  test-parallel    - Run tests in parallel"
	@echo "  test-logging     - Test logging system specifically"
	@echo ""
	@echo "📊 CLI Commands:"
	@echo "  cli-version      - Show ODCS Converter version"
	@echo "  cli-help         - Show comprehensive help"
	@echo "  cli-formats      - Show supported file formats"
	@echo "  cli-demo         - Run CLI demonstration"
	@echo "  cli-convert      - Interactive conversion helper"
	@echo ""
	@echo "📝 Logging and Monitoring:"
	@echo "  logs-demo        - Run comprehensive logging demonstration"
	@echo "  logs-clean       - Clean all log files"
	@echo "  logs-tail        - Tail current log files"
	@echo "  logs-analyze     - Analyze structured logs with jq"
	@echo ""
	@echo "✨ Code Quality:"
	@echo "  lint             - Run linting with ruff"
	@echo "  format           - Format code with black and ruff"
	@echo "  type-check       - Run type checking with mypy"
	@echo "  quality          - Run all code quality checks"
	@echo "  quality-fix      - Auto-fix quality issues where possible"
	@echo ""
	@echo "🏗️ Build and Release:"
	@echo "  build            - Build package distribution"
	@echo "  build-check      - Check package build"
	@echo "  release-dry      - Dry run of release process"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  clean            - Clean all build artifacts"
	@echo "  clean-test       - Clean test artifacts only"
	@echo "  clean-logs       - Clean log files"
	@echo "  clean-all        - Complete cleanup (artifacts + logs + cache)"
	@echo ""
	@echo "🔧 Development Utilities:"
	@echo "  env-local        - Setup local environment"
	@echo "  env-dev          - Setup development environment"
	@echo "  env-prod         - Setup production environment"
	@echo "  check-warnings   - Check for any Python warnings"
	@echo "  update-deps      - Update all dependencies with uv"

# ============================================================================
# Setup and Installation
# ============================================================================

.PHONY: install
install:
	@echo "📦 Installing ODCS Converter with uv..."
	uv sync
	@echo "✅ Installation complete!"

.PHONY: install-pip
install-pip:
	@echo "📦 Installing ODCS Converter with pip..."
	pip install -e ".[dev]"
	@echo "✅ Installation complete!"

.PHONY: dev
dev:
	@echo "🔧 Setting up development environment..."
	uv sync
	uv run pre-commit install
	@mkdir -p logs demo_logs test_logs
	@echo "✅ Development environment ready!"

.PHONY: dev-clean
dev-clean: clean-all
	@echo "🧹 Clean development setup..."
	rm -rf .venv
	uv venv
	uv sync
	uv run pre-commit install
	@echo "✅ Clean development environment ready!"

# ============================================================================
# CLI Commands
# ============================================================================

.PHONY: cli-version
cli-version:
	@uv run odcs-converter version --verbose

.PHONY: cli-help
cli-help:
	@uv run odcs-converter help

.PHONY: cli-formats
cli-formats:
	@uv run odcs-converter formats

.PHONY: cli-demo
cli-demo:
	@echo "🎯 Running CLI demonstration..."
	@uv run odcs-converter version
	@echo ""
	@uv run odcs-converter formats
	@echo ""
	@echo "✅ CLI demonstration complete!"

.PHONY: cli-convert
cli-convert:
	@echo "🔄 Interactive ODCS Converter"
	@echo "Example usage:"
	@echo "  odcs-converter convert input.json output.xlsx"
	@echo "  odcs-converter to-excel contract.yaml workbook.xlsx"
	@echo "  odcs-converter to-odcs data.xlsx contract.json --validate"

# ============================================================================
# Logging and Monitoring
# ============================================================================

.PHONY: logs-demo
logs-demo:
	@echo "📊 Running comprehensive logging demonstration..."
	@ODCS_ENV=local uv run python scripts/logging_demo.py
	@echo "✅ Logging demonstration complete! Check demo_logs/ directory."

.PHONY: logs-clean
logs-clean:
	@echo "🧹 Cleaning log files..."
	@rm -rf logs/ demo_logs/ test_logs/
	@mkdir -p logs demo_logs test_logs
	@echo "✅ Log files cleaned!"

.PHONY: logs-tail
logs-tail:
	@echo "📜 Tailing current log files..."
	@tail -f logs/*.log 2>/dev/null || echo "No log files found. Run 'make cli-demo' first."

.PHONY: logs-analyze
logs-analyze:
	@echo "🔍 Analyzing structured logs..."
	@if [ -f logs/*structured*.jsonl ]; then \
		echo "Recent errors:"; \
		cat logs/*structured*.jsonl | jq 'select(.record.level.name == "ERROR") | .record.message' 2>/dev/null | tail -5; \
		echo ""; \
		echo "Performance metrics:"; \
		cat logs/*structured*.jsonl | jq 'select(.record.extra.performance == true) | {operation: .record.extra.operation, duration_ms: .record.extra.duration_ms}' 2>/dev/null | tail -5; \
	else \
		echo "No structured logs found. Run 'make logs-demo' first."; \
	fi

# ============================================================================
# Environment Configuration
# ============================================================================

.PHONY: env-local
env-local:
	@echo "🏠 Setting up local environment..."
	@echo "ODCS_ENV=local" > .env
	@echo "ODCS_LOG_LEVEL=DEBUG" >> .env
	@echo "ODCS_LOG_DIR=logs" >> .env
	@echo "ODCS_LOG_CONSOLE=true" >> .env
	@echo "ODCS_LOG_FILE=true" >> .env
	@echo "✅ Local environment configured!"

.PHONY: env-dev
env-dev:
	@echo "🔧 Setting up development environment..."
	@echo "ODCS_ENV=dev" > .env
	@echo "ODCS_LOG_LEVEL=DEBUG" >> .env
	@echo "ODCS_LOG_DIR=logs" >> .env
	@echo "ODCS_LOG_CONSOLE=true" >> .env
	@echo "ODCS_LOG_FILE=true" >> .env
	@echo "ODCS_LOG_STRUCTURED=true" >> .env
	@echo "✅ Development environment configured!"

.PHONY: env-prod
env-prod:
	@echo "🚀 Setting up production environment..."
	@echo "ODCS_ENV=prod" > .env
	@echo "ODCS_LOG_LEVEL=INFO" >> .env
	@echo "ODCS_LOG_DIR=/var/log/odcs-converter" >> .env
	@echo "ODCS_LOG_CONSOLE=false" >> .env
	@echo "ODCS_LOG_FILE=true" >> .env
	@echo "ODCS_LOG_STRUCTURED=true" >> .env
	@echo "ODCS_LOG_ROTATION=500 MB" >> .env
	@echo "ODCS_LOG_RETENTION=90 days" >> .env
	@echo "✅ Production environment configured!"

# ============================================================================
# Testing (Enhanced with warning suppression)
# ============================================================================

.PHONY: test
test:
	@echo "🧪 Running all tests (warnings suppressed)..."
	@uv run pytest -W ignore::pytest.PytestUnknownMarkWarning -W ignore::DeprecationWarning

.PHONY: test-unit
test-unit:
	@echo "🧪 Running unit tests..."
	@uv run pytest tests/unit/ -v -W ignore::pytest.PytestUnknownMarkWarning

.PHONY: test-integration
test-integration:
	@echo "🧪 Running integration tests..."
	@uv run pytest tests/integration/ -v -W ignore::pytest.PytestUnknownMarkWarning

.PHONY: test-e2e
test-e2e:
	@echo "🧪 Running end-to-end tests..."
	@uv run pytest tests/end_to_end/ -m e2e -v -W ignore::pytest.PytestUnknownMarkWarning

.PHONY: test-fast
test-fast:
	@echo "⚡ Running fast tests (unit + integration)..."
	@uv run pytest tests/unit/ tests/integration/ -v -W ignore::pytest.PytestUnknownMarkWarning

.PHONY: test-slow
test-slow:
	@echo "🐌 Running slow tests (e2e + performance)..."
	@uv run pytest tests/end_to_end/ -m "e2e or slow or performance" -v

.PHONY: test-smoke
test-smoke:
	@echo "💨 Running smoke tests..."
	@uv run pytest -m smoke -v -W ignore::pytest.PytestUnknownMarkWarning

.PHONY: test-coverage
test-coverage:
	@echo "📊 Running tests with detailed coverage..."
	@uv run pytest --cov=src/odcs_converter --cov-report=html --cov-report=term-missing --cov-report=xml -W ignore::pytest.PytestUnknownMarkWarning
	@echo "📈 Coverage report generated in htmlcov/index.html"

.PHONY: test-watch
test-watch:
	@echo "👀 Running tests in watch mode..."
	@uv run ptw -- tests/ -W ignore::pytest.PytestUnknownMarkWarning

.PHONY: test-parallel
test-parallel:
	@echo "⚡ Running tests in parallel..."
	@uv run pytest -n auto -W ignore::pytest.PytestUnknownMarkWarning

.PHONY: test-debug
test-debug:
	@echo "🔍 Running tests with debugging enabled..."
	@uv run pytest -vv --tb=long --showlocals --maxfail=1

.PHONY: test-logging
test-logging:
	@echo "📊 Testing logging system..."
	@uv run pytest tests/unit/test_logging.py tests/integration/test_logging_integration.py -v

# Test specific categories
test-cli:
	@echo "Running CLI tests..."
	uv run pytest -m cli -v

test-excel:
	@echo "Running Excel-specific tests..."
	uv run pytest -m excel -v

test-yaml:
	@echo "Running YAML-specific tests..."
	uv run pytest -m yaml -v

test-conversion:
	@echo "Running conversion tests..."
	uv run pytest -m conversion -v

test-validation:
	@echo "Running validation tests..."
	uv run pytest -m validation -v

test-performance:
	@echo "Running performance tests..."
	uv run pytest -m performance -v --durations=0

# ============================================================================
# Code Quality
# ============================================================================

.PHONY: lint
lint:
	@echo "🔍 Running linting with ruff..."
	@uv run ruff check src/ tests/

.PHONY: format
format:
	@echo "🎨 Formatting code..."
	@uv run black src/ tests/
	@uv run ruff check --fix src/ tests/
	@echo "✅ Code formatted!"

.PHONY: type-check
type-check:
	@echo "📝 Running type checking with mypy..."
	@uv run mypy src/ --ignore-missing-imports

.PHONY: quality
quality: lint type-check
	@echo "✅ All code quality checks passed!"

.PHONY: quality-fix
quality-fix:
	@echo "🔧 Auto-fixing code quality issues..."
	@uv run black src/ tests/
	@uv run ruff check --fix src/ tests/
	@echo "✅ Code quality issues fixed!"

.PHONY: check-warnings
check-warnings:
	@echo "⚠️ Checking for Python warnings..."
	@PYTHONWARNINGS=all uv run python -c "from src.odcs_converter.cli import main; print('✅ No import warnings!')"
	@PYTHONWARNINGS=all uv run odcs-converter version --quiet 2>&1 | grep -i warning || echo "✅ No runtime warnings!"

# ============================================================================
# Build and Release
# ============================================================================

.PHONY: build
build:
	@echo "🏗️ Building package distribution..."
	@uv build
	@echo "✅ Package built! Check dist/ directory."

.PHONY: build-check
build-check: build
	@echo "🔍 Checking package build..."
	@uv run twine check dist/*
	@echo "✅ Package build is valid!"

.PHONY: release-dry
release-dry: quality test build-check
	@echo "🚀 Dry run of release process..."
	@echo "Would release version: $$(uv run python -c 'from src.odcs_converter import __version__; print(__version__)')"
	@echo "✅ Release dry run complete!"

# ============================================================================
# Cleanup
# ============================================================================

.PHONY: clean
clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage coverage.xml
	@rm -rf junit/ tests/logs/ tests/reports/
	@rm -rf .mypy_cache/ .ruff_cache/ .ropeproject/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".coverage.*" -delete
	@find . -type f -name "=*" -delete 2>/dev/null || true
	@echo "✅ Build artifacts cleaned!"

.PHONY: clean-test
clean-test:
	@echo "🧹 Cleaning test artifacts..."
	@rm -rf .pytest_cache/ htmlcov/ .coverage coverage.xml
	@rm -rf junit/ tests/logs/ tests/reports/
	@rm -rf tests/unit/outputs/* tests/integration/outputs/* tests/end_to_end/outputs/* 2>/dev/null || true
	@echo "✅ Test artifacts cleaned!"

.PHONY: clean-logs
clean-logs:
	@echo "🧹 Cleaning log files..."
	@rm -rf logs/ demo_logs/ test_logs/ *.log
	@mkdir -p logs demo_logs test_logs
	@echo "✅ Log files cleaned!"

.PHONY: clean-all
clean-all: clean clean-test clean-logs
	@echo "🧹 Complete cleanup (keeping .venv)..."
	@echo "✅ All artifacts cleaned!"

# ============================================================================
# Development Utilities
# ============================================================================

.PHONY: setup-test-dirs
setup-test-dirs:
	@echo "📁 Setting up test directories..."
	@mkdir -p tests/logs tests/reports junit
	@mkdir -p tests/unit/outputs tests/integration/outputs tests/end_to_end/outputs
	@mkdir -p tests/test_data/inputs/{json,yaml,excel}
	@mkdir -p tests/test_data/expected_outputs/{json,yaml,excel}
	@mkdir -p logs demo_logs test_logs
	@echo "✅ Test directories ready!"

.PHONY: update-deps
update-deps:
	@echo "📦 Updating dependencies with uv..."
	@uv sync --upgrade
	@echo "✅ Dependencies updated!"

.PHONY: show-config
show-config:
	@echo "⚙️ Current Configuration:"
	@echo "Environment: $${ODCS_ENV:-local}"
	@echo "Log Level: $${ODCS_LOG_LEVEL:-INFO}"
	@echo "Log Directory: $${ODCS_LOG_DIR:-logs}"
	@echo "Python Version: $$(uv run python --version)"
	@echo "ODCS Version: $$(uv run python -c 'from src.odcs_converter import __version__; print(__version__)')"

# ============================================================================
# Quick Start Commands
# ============================================================================

.PHONY: quickstart
quickstart: install dev setup-test-dirs
	@echo "🚀 Quick Start Complete!"
	@echo ""
	@echo "Try these commands:"
	@echo "  make cli-demo      - Run CLI demonstration"
	@echo "  make test-fast     - Run quick tests"
	@echo "  make logs-demo     - See logging in action"
	@echo ""
	@echo "For more options: make help"

.PHONY: all
all: quality test build
	@echo "✅ All checks passed! Ready for deployment."

# Default target
.DEFAULT_GOAL := help
