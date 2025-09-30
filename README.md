# ODCS Converter

A modern Python toolkit for bidirectional conversion between ODCS (Open Data Contract Standard) and Excel formats. Convert ODCS JSON/YAML to Excel spreadsheets and vice versa, with full support for ODCS v3.0.2 schema validation.

## Features

- 🔄 **Bidirectional Conversion**: ODCS JSON/YAML ↔ Excel spreadsheets
- 📊 **Smart Excel Generation**: Separate worksheets for each top-level ODCS field
- 📋 **Excel Parsing**: Convert Excel back to valid ODCS JSON/YAML format
- ✅ **ODCS v3.0.2 Compliance**: Full schema validation and type checking
- ⚡ **Ultra-fast with uv**: Lightning-fast dependency management and execution
- 🔧 **Rich CLI Interface**: Progress indicators, validation, and format detection
- 📝 **Type-safe**: Complete type hints and Pydantic validation
- 🧪 **Comprehensive Testing**: Full test coverage with pytest
- 🔍 **Code Quality**: Black, Ruff, MyPy integration
- 🐳 **Docker Ready**: Containerized deployment support
- ⚙️ **CI/CD Pipeline**: GitHub Actions with automated testing

## Installation

### Using pip

```bash
pip install odcs-converter
```

### Using uv (Recommended - Ultra Fast!)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the package
uv pip install odcs-converter
```

### From source

```bash
git clone https://github.com/thiruselvaa/odcs-converter.git
cd odcs-converter

# Using uv (recommended - 10-100x faster!)
uv sync

# Or using pip
pip install -e ".[dev]"
```

## Quick Start

### Command Line Usage

```bash
# 🔄 Bidirectional conversion (auto-detects direction from file extensions)

# ODCS → Excel: Generate Excel from ODCS JSON/YAML
odcs-converter contract.json output.xlsx
odcs-converter contract.yaml output.xlsx
odcs-converter https://example.com/contract.json output.xlsx

# Excel → ODCS: Convert Excel back to ODCS JSON/YAML  
odcs-converter data.xlsx contract.json
odcs-converter data.xlsx contract.yaml --validate

# 🎯 Specific conversion commands
odcs-converter to-excel contract.json output.xlsx
odcs-converter to-odcs data.xlsx contract.yaml --validate

# Show help
odcs-converter --help
```

### Python API Usage

```python
from odcs_converter import ODCSToExcelConverter, ExcelToODCSParser, YAMLConverter

# 📊 ODCS → Excel conversion
converter = ODCSToExcelConverter()
converter.generate_from_file("contract.json", "output.xlsx")
converter.generate_from_url("https://example.com/contract.json", "output.xlsx")

# 📋 Excel → ODCS conversion  
parser = ExcelToODCSParser()
odcs_data = parser.parse_from_file("data.xlsx")

# 📝 YAML utilities
YAMLConverter.dict_to_yaml(odcs_data, "contract.yaml")
yaml_data = YAMLConverter.yaml_to_dict("contract.yaml")
```

## Bidirectional Conversion Features

### 📊 ODCS → Excel (Structured Worksheets)

Each Excel file contains separate, organized worksheets:

- **Basic Information**: Core metadata (version, kind, apiVersion, id, name, etc.)
- **Tags**: Contract tags and labels
- **Description**: Usage, purpose, limitations, authoritative definitions
- **Servers**: Data source configurations and connection details
- **Schema**: Data structure definitions and properties
- **Support**: Contact information and support channels
- **Pricing**: Cost and billing information
- **Team**: Team members, roles, and responsibilities
- **Roles**: IAM roles and access permissions
- **SLA Properties**: Service level agreements and KPIs
- **Authoritative Definitions**: External references and documentation
- **Custom Properties**: Additional metadata and extensions

### 📋 Excel → ODCS (Smart Parsing)

- **Automatic Type Detection**: Converts Excel values to appropriate JSON/YAML types
- **Schema Validation**: Optional validation against ODCS v3.0.2 specification
- **Data Cleaning**: Removes empty cells and normalizes data structure
- **Format Flexibility**: Supports both JSON and YAML output formats
- **Error Handling**: Graceful handling of malformed or incomplete Excel data

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/thiruselvaa/odcs-converter.git
cd odcs-converter

# Using uv (recommended - ultra fast!)
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or using pip (fallback)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"

# Install pre-commit hooks
uv run pre-commit install
```

### Running Tests

```bash
# With uv (recommended)
uv run pytest

# Run with coverage
uv run pytest --cov=src/odcs_converter --cov-report=html

# Run specific tests
uv run pytest tests/test_generator.py::test_odcs_to_excel
uv run pytest tests/test_excel_parser.py::test_excel_to_odcs

# Traditional way
pytest
pytest --cov=src/odcs_converter --cov-report=html
pytest tests/test_generator.py::test_bidirectional_conversion
```

### Code Quality

```bash
# With uv (recommended)
uv run black src/ tests/
uv run ruff check src/ tests/
uv run mypy src/

# Using make commands
make format      # Format and lint code
make lint        # Run linting only
make type-check  # Run type checking
make test        # Run tests with coverage

# Traditional way
black src/ tests/
ruff check src/ tests/
mypy src/
```

## Use Cases

### 📊 Data Teams
- **Contract Visualization**: Convert ODCS contracts to Excel for easy review and collaboration
- **Template Creation**: Use Excel to design data contracts, then convert to ODCS format
- **Stakeholder Communication**: Share contracts in familiar Excel format with business users

### 🔄 DevOps & Automation
- **CI/CD Integration**: Validate Excel-based contracts in your pipeline
- **Bulk Operations**: Convert multiple contracts between formats programmatically
- **Migration**: Move from Excel-based processes to ODCS standard

### 📋 Data Governance
- **Audit Trails**: Track contract changes across Excel and ODCS formats  
- **Compliance Reporting**: Generate Excel reports from ODCS contracts
- **Schema Validation**: Ensure Excel data meets ODCS v3.0.2 standards

## Performance

Thanks to **uv**, this tool is exceptionally fast:
- **10-100x faster** dependency resolution vs pip
- **Lightning-fast CLI execution** with `uv run`
- **Instant environment setup** with `uv sync`
- **Reproducible builds** with uv.lock


## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

### For Users
- **[User Guide](docs/user/USER_GUIDE.md)** - Complete usage instructions *(coming soon)*
- **[CLI Reference](docs/user/CLI.md)** - Command-line interface documentation *(coming soon)*
- **[Examples](docs/user/EXAMPLES.md)** - Code examples and tutorials *(coming soon)*
- **[User README](docs/user/README.md)** - User documentation index

### For Developers
- **[Setup Guide](docs/development/SETUP.md)** - Development environment setup
- **[Contributing Guide](docs/development/CONTRIBUTING.md)** - How to contribute
- **[Project Structure](docs/development/PROJECT_STRUCTURE.md)** - Codebase organization
- **[Architecture](docs/development/ARCHITECTURE.md)** - System design overview *(coming soon)*
- **[API Reference](docs/development/API.md)** - Detailed API documentation *(coming soon)*

### For Testing
- **[Testing Guide](docs/testing/TESTING.md)** - How to write and run tests
- **[Test Fixes Summary](docs/testing/TEST_FIXES_SUMMARY.md)** - Recent test improvements
- **[Coverage Report](docs/testing/COVERAGE.md)** - Current test coverage *(coming soon)*

### For Deployment
- **[Deployment README](docs/deployment/README.md)** - Deployment documentation index
- **[Deployment Guide](docs/deployment/DEPLOYMENT.md)** - How to deploy *(coming soon)*
- **[Docker Guide](docs/deployment/DOCKER.md)** - Container usage *(coming soon)*
- **[Configuration](docs/deployment/CONFIGURATION.md)** - Configuration options *(coming soon)*

### Project Management
- **[Project Management README](docs/project-management/README.md)** - Management docs index
- **[Organization Summary](docs/project-management/ORGANIZATION_SUMMARY.md)** - Project organization
- **[Rename Summary](docs/project-management/RENAME_SUMMARY.md)** - Project rename details
- **[Changelog](docs/project-management/CHANGELOG.md)** - Version history *(coming soon)*

### Utility Scripts
- **[Scripts Documentation](scripts/README.md)** - Available utility scripts
  - `scripts/setup_tests.py` - Initialize test structure
  - `scripts/run_checks.sh` - Run all quality checks

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Open Data Contract Standard (ODCS)](https://github.com/bitol-io/open-data-contract-standard) - The foundation specification
- [uv](https://github.com/astral-sh/uv) - Ultra-fast Python package manager  
- [openpyxl](https://openpyxl.readthedocs.io/) - Excel file manipulation
- [Pydantic](https://docs.pydantic.dev/) - Data validation and serialization
- [Click](https://click.palletsprojects.com/) - CLI interface framework
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal output
- [PyYAML](https://pyyaml.org/) - YAML processing
- [Pandas](https://pandas.pydata.org/) - Excel data parsing
