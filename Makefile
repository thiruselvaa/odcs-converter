help:
	@echo "Available commands:"
	@echo "  install     - Install package"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo "  clean       - Clean build artifacts"
	@echo "  build       - Build package"

install:
	pip install -e ".[dev]"

test:
	pytest --cov=src/odcs_excel_generator --cov-report=html

lint:
	ruff check src/ tests/

format:
	black src/ tests/

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/

build:
	python -m build
