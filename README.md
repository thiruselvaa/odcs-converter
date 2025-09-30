# ODCS Excel Generator

A modern Python project that generates Excel files from ODCS (Open Data Contract Standard) JSON schema with top-level fields organized in separate worksheets.

## Features

- 🚀 Modern Python project setup with best practices
- 📊 Generate Excel files with separate worksheets for each top-level ODCS field
- 🔧 CLI interface with rich output and progress indicators
- 📝 Type hints and comprehensive validation using Pydantic
- 🧪 Full test coverage with pytest
- 🔍 Code quality tools (black, ruff, mypy)
- 📚 Comprehensive documentation
- 🐳 Docker support
- ⚡ GitHub Actions CI/CD pipeline

## Installation

### Using pip

```bash
pip install odcs-excel-generator
```

### From source

```bash
git clone https://github.com/thiruselvaa/odcs-excel-generator.git
cd odcs-excel-generator
pip install -e ".[dev]"
```

## Quick Start

### Command Line Usage

```bash
# Generate Excel from ODCS JSON file
odcs-excel input.json output.xlsx

# Generate Excel from ODCS JSON URL
odcs-excel https://example.com/data-contract.json output.xlsx

# Generate with custom configuration
odcs-excel input.json output.xlsx --config config.yaml

# Show available options
odcs-excel --help
```

### Python API Usage

```python
from odcs_excel_generator import ODCSExcelGenerator

# Initialize generator
generator = ODCSExcelGenerator()

# Generate from file
generator.generate_from_file("input.json", "output.xlsx")

# Generate from URL
generator.generate_from_url("https://example.com/contract.json", "output.xlsx")

# Generate from dictionary
data = {...}  # Your ODCS data
generator.generate_from_dict(data, "output.xlsx")
```

## Excel Output Structure

The generated Excel file contains separate worksheets for each top-level ODCS field:

- **Basic Info**: version, kind, apiVersion, id, name, tenant, status, etc.
- **Tags**: List of tags associated with the contract  
- **Description**: Usage, purpose, limitations, and authoritative definitions
- **Servers**: Data source details and server configurations
- **Schema**: Data schema definitions and properties
- **Support**: Support channels and contact information
- **Pricing**: Cost and pricing information
- **Team**: Team members and their roles
- **Roles**: IAM roles and access permissions
- **SLA Properties**: Service level agreement details
- **Authoritative Definitions**: External references and links
- **Custom Properties**: Additional custom metadata

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/thiruselvaa/odcs-excel-generator.git
cd odcs-excel-generator
```

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/odcs_excel_generator --cov-report=html

# Run specific test
pytest tests/test_generator.py::test_basic_generation
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Open Data Contract Standard (ODCS)](https://github.com/bitol-io/open-data-contract-standard)
- [openpyxl](https://openpyxl.readthedocs.io/) for Excel file manipulation
- [Pydantic](https://docs.pydantic.dev/) for data validation
- [Click](https://click.palletsprojects.com/) for CLI interface
