help:
	@echo "Available commands:"
	@echo "  install     - Install package with uv"
	@echo "  install-pip - Install package with pip (fallback)"
	@echo "  test        - Run tests with uv"
	@echo "  lint        - Run linting with uv"
	@echo "  format      - Format code with uv"
	@echo "  type-check  - Run type checking with uv"
	@echo "  clean       - Clean build artifacts"
	@echo "  build       - Build package"
	@echo "  dev         - Setup development environment"

install:
	uv sync

install-pip:
	pip install -e ".[dev]"

dev:
	uv sync
	uv run pre-commit install

test:
	uv run pytest --cov=src/odcs_excel_generator --cov-report=html

lint:
	uv run ruff check src/ tests/

format:
	uv run black src/ tests/
	uv run ruff check --fix src/ tests/

type-check:
	uv run mypy src/

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .venv/

build:
	uv build
