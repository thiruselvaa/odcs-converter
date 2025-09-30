# ODCS Excel Generator - Setup Guide

## Project Overview

This modern Python project generates Excel files from ODCS (Open Data Contract Standard) JSON schema with top-level fields organized in separate worksheets.

## Project Structure

```
odcs-excel-generator/
├── src/odcs_excel_generator/     # Main package source
│   ├── __init__.py              # Package initialization
│   ├── models.py                # Pydantic models for ODCS validation
│   ├── generator.py             # Main Excel generation logic
│   └── cli.py                   # Command-line interface
├── tests/                       # Test suite
│   ├── __init__.py
│   └── test_generator.py        # Comprehensive tests
├── examples/                    # Usage examples
│   ├── example_contract.json    # Sample ODCS contract
│   └── example_usage.py         # Python API example
├── docs/                        # Documentation (future)
├── .github/workflows/           # CI/CD pipeline
│   └── ci.yml                   # GitHub Actions workflow
├── pyproject.toml              # Modern Python packaging
├── requirements.txt            # Core dependencies
├── requirements-dev.txt        # Development dependencies
├── Dockerfile                  # Container support
├── docker-compose.yml          # Development environment
├── Makefile                    # Development commands  
├── .pre-commit-config.yaml     # Code quality hooks
├── .gitignore                  # Git ignore rules
├── .env.example               # Environment template
├── LICENSE                     # MIT license
└── README.md                   # Project documentation
```

## Setup Instructions

### 1. Local Development Setup

```bash
# Clone or navigate to the project
cd odcs-excel-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 2. Using Make Commands

```bash
make help          # Show available commands
make install       # Install package
make test          # Run tests with coverage
make lint          # Run code linting
make format        # Format code
make clean         # Clean build artifacts
make build         # Build package
```

### 3. Using Docker

```bash
# Build image
docker build -t odcs-excel-generator .

# Run with mounted data directory
docker run --rm -v $(pwd)/data:/app/data odcs-excel-generator examples/example_contract.json output.xlsx

# Development with docker-compose
docker-compose run dev
```

## Usage Examples

### Command Line

```bash
# Generate from local file
odcs-excel examples/example_contract.json output.xlsx

# Generate from URL
odcs-excel https://example.com/contract.json output.xlsx

# With verbose logging
odcs-excel input.json output.xlsx --verbose
```

### Python API

```python
from odcs_excel_generator import ODCSExcelGenerator

generator = ODCSExcelGenerator()

# From file
generator.generate_from_file("contract.json", "output.xlsx")

# From URL  
generator.generate_from_url("https://example.com/contract.json", "output.xlsx")

# From dictionary
data = {...}  # Your ODCS data
generator.generate_from_dict(data, "output.xlsx")
```

## Excel Output

The generated Excel file contains these worksheets:
- **Basic Information**: Core contract metadata
- **Tags**: Contract tags and labels
- **Description**: Usage, purpose, and limitations
- **Servers**: Data source configurations
- **Schema**: Data structure definitions
- **Support**: Contact and support information
- **Pricing**: Cost and billing details
- **Team**: Team members and roles
- **Roles**: Access permissions and IAM roles
- **SLA Properties**: Service level agreements
- **Authoritative Definitions**: External references
- **Custom Properties**: Additional metadata

## Testing

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=src/odcs_excel_generator --cov-report=html

# Run specific test
pytest tests/test_generator.py::TestODCSExcelGenerator::test_generate_from_dict
```

## Code Quality

This project uses modern Python tooling:
- **Black**: Code formatting
- **Ruff**: Fast linting and import sorting
- **MyPy**: Static type checking
- **Pytest**: Testing framework with coverage
- **Pre-commit**: Git hooks for code quality

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run quality checks: `make lint && make test`
5. Commit with pre-commit hooks
6. Submit a pull request

## Modern Python Features

- **PEP 621**: Metadata in pyproject.toml
- **Type hints**: Full type annotation coverage
- **Pydantic v2**: Data validation and serialization
- **Rich**: Beautiful console output
- **Click/Typer**: Modern CLI framework
- **Hatch**: Modern build backend
- **src/ layout**: Best practice project structure
- **GitHub Actions**: Automated CI/CD
- **Docker**: Containerized deployment

This project follows all modern Python best practices for 2024!

