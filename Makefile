help:
	@echo "Available commands:"
	@echo ""
	@echo "Setup and Installation:"
	@echo "  install     - Install package with uv"
	@echo "  install-pip - Install package with pip (fallback)"
	@echo "  dev         - Setup development environment"
	@echo ""
	@echo "Testing:"
	@echo "  test        - Run all tests"
	@echo "  test-unit   - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-e2e    - Run end-to-end tests only"
	@echo "  test-fast   - Run fast tests (unit + integration)"
	@echo "  test-slow   - Run slow tests (e2e + performance)"
	@echo "  test-smoke  - Run smoke tests"
	@echo "  test-coverage - Run tests with detailed coverage report"
	@echo "  test-watch  - Run tests in watch mode"
	@echo "  test-parallel - Run tests in parallel"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint        - Run linting with uv"
	@echo "  format      - Format code with uv"
	@echo "  type-check  - Run type checking with uv"
	@echo "  quality     - Run all code quality checks"
	@echo ""
	@echo "Build and Cleanup:"
	@echo "  clean       - Clean build artifacts"
	@echo "  clean-test  - Clean test artifacts"
	@echo "  build       - Build package"

install:
	uv sync

install-pip:
	pip install -e ".[dev]"

dev:
	uv sync
	uv run pre-commit install

# Test commands
test:
	uv run pytest

test-unit:
	@echo "Running unit tests..."
	uv run pytest tests/unit/ -m unit -v

test-integration:
	@echo "Running integration tests..."
	uv run pytest tests/integration/ -m integration -v

test-e2e:
	@echo "Running end-to-end tests..."
	uv run pytest tests/end_to_end/ -m e2e -v

test-fast:
	@echo "Running fast tests (unit + integration)..."
	uv run pytest tests/unit/ tests/integration/ -m "unit or integration" -v

test-slow:
	@echo "Running slow tests (e2e + performance)..."
	uv run pytest tests/end_to_end/ -m "e2e or slow or performance" -v

test-smoke:
	@echo "Running smoke tests..."
	uv run pytest -m smoke -v

test-coverage:
	@echo "Running tests with detailed coverage..."
	uv run pytest --cov=src/odcs_converter --cov-report=html --cov-report=term-missing --cov-report=xml

test-watch:
	@echo "Running tests in watch mode (requires pytest-watch)..."
	uv run ptw -- tests/

test-parallel:
	@echo "Running tests in parallel (requires pytest-xdist)..."
	uv run pytest -n auto

test-debug:
	@echo "Running tests with debugging enabled..."
	uv run pytest -vv --tb=long --showlocals --maxfail=1

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

# Code quality commands
lint:
	@echo "Running linting..."
	uv run ruff check src/ tests/

format:
	@echo "Formatting code..."
	uv run black src/ tests/
	uv run ruff check --fix src/ tests/

type-check:
	@echo "Running type checking..."
	uv run mypy src/

quality: lint type-check
	@echo "All code quality checks completed."

# Build and cleanup commands
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage coverage.xml
	rm -rf junit/ tests/logs/ tests/reports/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

clean-test:
	@echo "Cleaning test artifacts..."
	rm -rf .pytest_cache/ htmlcov/ .coverage coverage.xml
	rm -rf junit/ tests/logs/ tests/reports/
	rm -rf tests/unit/outputs/* tests/integration/outputs/* tests/end_to_end/outputs/*

build:
	@echo "Building package..."
	uv build

# Development setup
setup-test-dirs:
	@echo "Setting up test directories..."
	mkdir -p tests/logs tests/reports junit
	mkdir -p tests/unit/outputs tests/integration/outputs tests/end_to_end/outputs
	mkdir -p tests/test_data/inputs/{json,yaml,excel}
	mkdir -p tests/test_data/expected_outputs/{json,yaml,excel}
