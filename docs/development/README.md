# Development Documentation

This directory contains documentation for developers working on the ODCS Converter project.

## Available Documents

- **[Setup Guide](SETUP.md)** - Environment setup and installation instructions
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[Project Structure](PROJECT_STRUCTURE.md)** - Codebase organization and architecture
- **[ODCS Schema Coverage](ODCS_SCHEMA_COVERAGE.md)** - Comprehensive analysis of ODCS v3.0.2 implementation
- **[Architecture Overview](ARCHITECTURE.md)** - System design *(coming soon)*
- **[API Reference](API.md)** - Detailed API documentation *(coming soon)*

## Quick Start for Developers

### 1. Environment Setup

Follow the [Setup Guide](SETUP.md) to configure your development environment:

```bash
# Clone the repository
git clone https://github.com/thiruselvaa/odcs-converter.git
cd odcs-converter

# Install with uv (recommended)
uv sync --all-extras

# Or install with pip
pip install -e ".[dev,test]"
```

### 2. Run Tests

```bash
# Run all tests
make test

# Run specific test categories
make test-unit
make test-integration
make test-e2e
```

### 3. Code Quality

```bash
# Run linting
make lint

# Apply formatting
make format

# Run type checking
make type-check

# Run all quality checks
make quality
```

### 4. Project Structure

See [Project Structure](PROJECT_STRUCTURE.md) for detailed codebase organization:

```
odcs-converter/
├── src/odcs_converter/     # Main package
│   ├── models.py          # Pydantic models
│   ├── generator.py       # ODCS → Excel
│   ├── excel_parser.py    # Excel → ODCS
│   ├── yaml_converter.py  # YAML utilities
│   └── cli.py            # Command-line interface
├── tests/                 # Test suite
├── docs/                  # Documentation
└── examples/             # Usage examples
```

### 5. Making Changes

Follow the [Contributing Guide](CONTRIBUTING.md) for:
- Code style guidelines
- Branching strategy
- Pull request process
- Testing requirements

## Key Concepts

### Modern CLI Architecture

The CLI has been modernized with Typer + Rich integration:
- **Typer Framework**: Type-safe commands with automatic validation
- **Rich Integration**: Beautiful terminal output with progress bars and tables
- **Command Structure**: Modern subcommand architecture
- **Error Handling**: User-friendly error messages with helpful feedback

### ODCS Schema Coverage

The [ODCS Schema Coverage](ODCS_SCHEMA_COVERAGE.md) document provides:
- Complete field-by-field analysis of ODCS v3.0.2 implementation
- Coverage percentages for each section
- Missing fields and enhancement opportunities
- Recommendations for future development

**Quick Stats:**
- ✅ 100% overall field coverage
- ✅ 100% worksheet coverage (15 sheets)
- ✅ Bidirectional conversion support
- ✅ All 30+ server types supported
- ✅ 237 tests passing (47 CLI + 190 core)

### Architecture Principles

1. **Separation of Concerns**: Models, generation, parsing, and CLI are separate modules
2. **Validation First**: Pydantic models provide strong validation
3. **Bidirectional**: Full support for ODCS ↔ Excel conversion
4. **Modern CLI**: Typer + Rich for beautiful, type-safe command interface
5. **Type Safe**: Comprehensive type hints throughout
6. **Extensible**: Easy to add new fields and features
7. **Test Driven**: 100% test coverage with unit and integration tests

### Development Workflow

```bash
# 1. Create a feature branch
git checkout -b feature/my-feature

# 2. Make changes and write tests
# ... edit files ...

# 3. Run quality checks
make format
make lint
make test

# 4. Commit and push
git commit -m "feat: add my feature"
git push origin feature/my-feature

# 5. Create pull request
# ... on GitHub ...
```

## Common Development Tasks

### Adding a New CLI Command

1. Add command function to `src/odcs_converter/cli.py` with `@app.command()` decorator
2. Define type-safe arguments and options using Typer annotations
3. Add Rich formatting for beautiful output
4. Add unit tests in `tests/unit/test_cli.py`
5. Add integration tests in `tests/integration/`
6. Update CLI documentation

### Adding a New Field

1. Update the Pydantic model in `src/odcs_converter/models.py`
2. Update the Excel generator in `src/odcs_converter/generator.py`
3. Update the Excel parser in `src/odcs_converter/excel_parser.py`
4. Add tests in `tests/unit/test_models.py`
5. Add integration tests
6. Update documentation

### Adding a New Worksheet

1. Create `_create_<name>_sheet()` method in generator
2. Create `_parse_<name>()` method in parser
3. Call methods in `_create_workbook()` and `parse_from_file()`
4. Add tests for generation and parsing
5. Update ODCS Schema Coverage document

### Running Specific Tests

```bash
# Run all CLI tests
pytest tests/unit/test_cli.py tests/integration/test_cli_*.py

# Run tests matching a pattern
pytest -k "test_schema"

# Run tests in a specific file
pytest tests/unit/test_models.py

# Run with coverage
pytest --cov=src/odcs_converter

# Run with verbose output
pytest -v

# Test CLI interactively
python -m pytest tests/unit/test_cli.py::TestCliBasics::test_version_command -v
```

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Using the Python Debugger

```python
import pdb; pdb.set_trace()  # Add breakpoint
```

### Testing with Real Data

```bash
# Modern CLI commands (Typer-based)
python -m odcs_converter.cli to-excel examples/sample_contract.yaml output.xlsx --verbose
python -m odcs_converter.cli to-odcs output.xlsx contract.yaml --validate
python -m odcs_converter.cli convert examples/sample_contract.json result.xlsx --dry-run

# Test CLI help and info commands
python -m odcs_converter.cli --help
python -m odcs_converter.cli version --verbose
python -m odcs_converter.cli formats
```

## Resources

### Internal Documentation
- [Testing Guide](../testing/TESTING.md) - How to write and run tests
- [User Guide](../user/README.md) - End-user documentation
- [Deployment Guide](../deployment/README.md) - Production deployment

### External Resources
- [ODCS Specification](https://bitol-io.github.io/open-data-contract-standard/v3.0.2/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [OpenPyXL Documentation](https://openpyxl.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/thiruselvaa/odcs-converter/issues)
- **Discussions**: [GitHub Discussions](https://github.com/thiruselvaa/odcs-converter/discussions)
- **Email**: thiruselvaa@gmail.com

## Contributing

We welcome contributions! Please see the [Contributing Guide](CONTRIBUTING.md) for details on:
- Code of conduct
- Development process
- Testing requirements
- Documentation standards

## CLI Development

### CLI Architecture

The CLI uses modern Python patterns:
- **Typer**: Type-safe CLI framework built on Click
- **Rich**: Beautiful terminal output with progress bars and tables
- **Enums**: Type-safe format validation
- **Path**: Automatic file path validation
- **Configuration**: JSON config file support

### CLI Testing

The CLI has comprehensive test coverage:
- **Unit Tests**: 33 tests covering all commands and options
- **Integration Tests**: 14 tests with real file operations
- **Mocked Tests**: Isolated testing of CLI logic
- **Error Handling**: Tests for various failure scenarios

### Adding CLI Features

1. Use Typer decorators: `@app.command()`, `@app.option()`, `@app.argument()`
2. Add type hints for automatic validation
3. Use Rich for beautiful output: `console.print()`, `Progress()`, `Table()`
4. Handle errors gracefully with user-friendly messages
5. Add comprehensive tests for new functionality

---

**Last Updated**: 2025-01-27  
**Project Version**: 0.2.0  
**CLI Framework**: Typer + Rich + Click  
**Test Coverage**: 237 tests (100% passing)