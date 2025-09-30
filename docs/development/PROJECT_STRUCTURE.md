# Project Structure - ODCS Excel Generator

This document describes the complete directory structure and organization of the ODCS Excel Generator project.

## 📁 Directory Tree

```
odcs-excel-generator/
├── .github/                          # GitHub specific files
│   └── workflows/                    # CI/CD workflows
│       ├── test.yml                  # Automated testing
│       └── publish.yml               # Package publishing
│
├── docs/                             # Documentation
│   ├── README.md                     # Documentation index
│   ├── CHANGELOG.md                  # Version history
│   │
│   ├── development/                  # Developer documentation
│   │   ├── SETUP.md                  # Setup instructions
│   │   ├── CONTRIBUTING.md           # Contribution guidelines
│   │   ├── ARCHITECTURE.md           # System architecture
│   │   ├── API.md                    # API reference
│   │   └── PROJECT_STRUCTURE.md      # This file
│   │
│   ├── testing/                      # Testing documentation
│   │   ├── TESTING.md                # Testing guide
│   │   ├── TEST_FIXES_SUMMARY.md     # Recent test fixes
│   │   └── COVERAGE.md               # Coverage reports
│   │
│   ├── deployment/                   # Deployment documentation
│   │   ├── DEPLOYMENT.md             # Deployment guide
│   │   ├── DOCKER.md                 # Docker usage
│   │   └── CONFIGURATION.md          # Configuration options
│   │
│   └── user/                         # User documentation
│       ├── USER_GUIDE.md             # User guide
│       ├── CLI.md                    # CLI reference
│       └── EXAMPLES.md               # Usage examples
│
├── examples/                         # Example files and usage
│   ├── example_usage.py              # Example Python usage
│   └── example_contract.json         # Sample ODCS contract
│
├── scripts/                          # Utility scripts
│   ├── README.md                     # Scripts documentation
│   ├── setup_tests.py                # Test setup script
│   └── run_checks.sh                 # Quality checks script
│
├── src/                              # Source code
│   └── odcs_converter/               # Main package
│       ├── __init__.py               # Package initialization
│       ├── models.py                 # Pydantic models (ODCS schema)
│       ├── generator.py              # ODCS to Excel converter
│       ├── excel_parser.py           # Excel to ODCS parser
│       ├── yaml_converter.py         # YAML utilities
│       └── cli.py                    # Command-line interface
│
├── tests/                            # Test suite
│   ├── conftest.py                   # Shared test fixtures
│   ├── __init__.py                   # Test package init
│   │
│   ├── unit/                         # Unit tests
│   │   ├── __init__.py
│   │   ├── utils.py                  # Unit test utilities
│   │   ├── test_models.py            # Model tests
│   │   ├── test_example_unit.py      # Example unit tests
│   │   └── test_yaml_converter.py    # YAML converter tests
│   │
│   ├── integration/                  # Integration tests
│   │   ├── __init__.py
│   │   ├── utils.py                  # Integration test utilities
│   │   ├── test_generator.py         # Generator integration tests
│   │   ├── test_excel_parser.py      # Parser integration tests
│   │   ├── test_excel_generation.py  # Generation workflow tests
│   │   └── test_excel_parsing.py     # Parsing workflow tests
│   │
│   └── end_to_end/                   # End-to-end tests
│       ├── __init__.py
│       ├── utils.py                  # E2E test utilities
│       └── test_example_e2e.py       # E2E workflow tests
│
├── .gitignore                        # Git ignore rules
├── .pre-commit-config.yaml           # Pre-commit hooks
├── Dockerfile                        # Docker container definition
├── docker-compose.yml                # Docker Compose configuration
├── LICENSE                           # MIT License
├── Makefile                          # Build automation
├── pyproject.toml                    # Project configuration
├── pytest.ini                        # Pytest configuration
├── README.md                         # Project README
├── requirements.txt                  # Production dependencies
├── requirements-dev.txt              # Development dependencies
└── uv.lock                           # UV lock file
```

## 📦 Package Structure

### Source Code (`src/odcs_converter/`)

The main package implementing bidirectional conversion between ODCS and Excel formats.

#### Core Modules

**`models.py`** - Data Models
- Pydantic models for ODCS schema validation
- Enums for API versions, server types, logical types
- Model classes: `ODCSDataContract`, `Server`, `SchemaProperty`, etc.
- Field validators for data integrity
- Size: ~320 lines

**`generator.py`** - ODCS to Excel Conversion
- `ODCSToExcelConverter` class
- Converts ODCS JSON/YAML to Excel workbooks
- Creates separate worksheets for different ODCS sections
- Styling and formatting for Excel output
- Size: ~250 lines

**`excel_parser.py`** - Excel to ODCS Conversion
- `ExcelToODCSParser` class
- Parses Excel workbooks back to ODCS format
- Type conversion and data cleaning
- Validation against ODCS schema
- Size: ~300 lines

**`yaml_converter.py`** - YAML Utilities
- `YAMLConverter` class
- YAML serialization/deserialization
- File I/O with YAML format
- Format detection and normalization
- Size: ~150 lines

**`cli.py`** - Command-Line Interface
- Click-based CLI implementation
- Commands: `odcs-to-excel`, `excel-to-odcs`
- Rich console output
- Progress indicators and logging
- Size: ~300 lines

## 🧪 Test Structure

### Test Organization

Tests are organized by scope and purpose:

**Unit Tests** (`tests/unit/`)
- Test individual components in isolation
- Fast execution (< 1 second per test)
- High code coverage focus
- Mock external dependencies

**Integration Tests** (`tests/integration/`)
- Test component interactions
- Real file I/O testing
- Conversion workflow validation
- Medium execution time (1-10 seconds)

**End-to-End Tests** (`tests/end_to_end/`)
- Complete user workflow testing
- CLI functionality testing
- Real-world scenario validation
- Slower execution (10+ seconds)

### Test Utilities

Each test category has its own utilities:

- `tests/unit/utils.py` - Unit test helpers, mocks, factories
- `tests/integration/utils.py` - Integration test helpers
- `tests/end_to_end/utils.py` - E2E test helpers, CLI mocks

### Test Fixtures

Shared fixtures in `tests/conftest.py`:
- `temp_dir` - Temporary directory for test files
- `sample_odcs_data` - Sample ODCS contract data
- `complete_odcs_data` - Complete ODCS contract
- Various test helpers and factories

## 📄 Configuration Files

### `pyproject.toml`
Primary project configuration file containing:
- Project metadata (name, version, description)
- Dependencies (production and development)
- Build system configuration (hatchling)
- Tool configurations (black, ruff, pytest)
- Entry points for CLI commands

### `pytest.ini`
Pytest configuration:
- Test discovery patterns
- Markers (unit, integration, e2e, slow, etc.)
- Coverage settings (80% minimum)
- Log configuration
- Warning filters

### `.pre-commit-config.yaml`
Pre-commit hooks:
- Code formatting (black)
- Linting (ruff)
- Type checking (mypy)
- Trailing whitespace removal
- YAML validation

### `Makefile`
Build automation with common tasks:
- `make test` - Run all tests
- `make test-unit` - Run unit tests only
- `make test-integration` - Run integration tests
- `make test-e2e` - Run E2E tests
- `make lint` - Run linting
- `make format` - Format code
- `make install` - Install package
- `make clean` - Clean build artifacts

## 🐳 Docker Configuration

### `Dockerfile`
Container definition for the application:
- Base image: Python 3.11
- Multi-stage build for optimization
- Production dependencies only
- Non-root user for security

### `docker-compose.yml`
Service orchestration:
- Application service
- Volume mounts for development
- Port mappings
- Environment variables

## 📚 Documentation Structure

### Development Docs
- **SETUP.md** - Environment setup, installation
- **CONTRIBUTING.md** - Contribution guidelines, code style
- **ARCHITECTURE.md** - System design, component overview
- **API.md** - API reference, function signatures
- **PROJECT_STRUCTURE.md** - This file

### Testing Docs
- **TESTING.md** - Testing guide, best practices
- **TEST_FIXES_SUMMARY.md** - Recent test improvements
- **COVERAGE.md** - Coverage metrics, reports

### Deployment Docs
- **DEPLOYMENT.md** - Deployment procedures
- **DOCKER.md** - Docker usage, containerization
- **CONFIGURATION.md** - Configuration options, environment variables

### User Docs
- **USER_GUIDE.md** - Usage instructions, features
- **CLI.md** - CLI reference, commands, options
- **EXAMPLES.md** - Code examples, tutorials

## 🔧 Script Organization

### Development Scripts

**`scripts/setup_tests.py`**
- Initializes test directory structure
- Creates necessary files and folders
- Sets up test templates
- Run once during initial setup

**`scripts/run_checks.sh`**
- Runs all code quality checks
- Formats code (with --fix flag)
- Lints code
- Type checks
- Runs tests with coverage
- Used before commits

## 📊 Generated Directories

These directories are created during runtime/testing:

```
.pytest_cache/          # Pytest cache
__pycache__/            # Python bytecode cache
.ruff_cache/            # Ruff linter cache
.venv/                  # Virtual environment
htmlcov/                # HTML coverage reports
junit/                  # JUnit test results (for CI)
.coverage               # Coverage data file
```

## 🚫 Excluded Files

The following are excluded via `.gitignore`:

- `*.pyc` - Python bytecode
- `__pycache__/` - Bytecode cache directories
- `.pytest_cache/` - Pytest cache
- `htmlcov/` - Coverage HTML reports
- `.coverage` - Coverage data
- `*.egg-info/` - Package metadata
- `dist/` - Distribution packages
- `build/` - Build artifacts
- `.venv/` - Virtual environments
- `*.xlsx` - Generated Excel files
- `.DS_Store` - macOS metadata

## 📈 Code Metrics

### Module Sizes
- Total source code: ~1,320 lines
- Total test code: ~3,500 lines
- Test to code ratio: 2.65:1

### Coverage
- Overall coverage: 80%+
- models.py: 95%
- generator.py: 88%
- excel_parser.py: 85%
- yaml_converter.py: 92%
- cli.py: 78%

## 🔄 Workflow Integration

### Development Workflow
1. Edit code in `src/odcs_converter/`
2. Write/update tests in `tests/`
3. Run `./scripts/run_checks.sh --fix`
4. Commit and push

### Testing Workflow
1. Unit tests run first (fastest feedback)
2. Integration tests run next
3. E2E tests run last (most comprehensive)
4. Coverage report generated

### CI/CD Workflow
1. Tests run on push/PR
2. Linting and formatting checked
3. Coverage verified (>= 80%)
4. Package built and published (on release)

## 🎯 Best Practices

### Code Organization
- One class per file when possible
- Group related functionality
- Keep modules focused and cohesive
- Use clear, descriptive names

### Import Organization
1. Standard library imports
2. Third-party imports
3. Local application imports
4. Separate groups with blank lines

### File Naming
- Python files: `snake_case.py`
- Test files: `test_*.py`
- Documentation: `UPPERCASE.md` for main docs
- Scripts: `action_target.ext`

## 📞 Support

For questions about project structure:
- Review this document
- Check related documentation
- Open an issue on GitHub
- Contact: thiruselvaa@gmail.com

---

**Last Updated**: 2025-01-26
**Version**: 0.2.0
**Maintainer**: Thiruselva