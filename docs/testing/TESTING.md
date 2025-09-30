# Testing Guide - ODCS Converter

This comprehensive guide covers all aspects of testing in the ODCS Converter project.

## 📋 Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Types](#test-types)
- [Test Utilities](#test-utilities)
- [Best Practices](#best-practices)
- [Code Quality](#code-quality)
- [Continuous Integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)

## Overview

The ODCS Converter uses **pytest** as its testing framework. The test suite is organized into three main categories:

- **Unit Tests** - Fast, isolated tests for individual components
- **Integration Tests** - Tests for component interactions and workflows
- **End-to-End Tests** - Complete workflow tests including CLI

### Current Test Status

- **Total Tests**: 237 passing (47 CLI + 190 core)
- **Test Coverage**: 100% CLI coverage, 80%+ overall
- **Execution Time**: ~3 seconds for full suite
- **Lint Status**: ✅ All checks passing
- **CLI Framework**: Typer + Rich + Click integration
- **Last Updated**: 2025-01-27

### Related Documentation

- [Test Fixes Summary](./TEST_FIXES_SUMMARY.md) - History of test failure resolutions
- [Lint Fixes Summary](./LINT_FIXES_SUMMARY.md) - Lint issue resolutions and best practices

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── __init__.py                 # Package initialization
│
├── unit/                       # Unit tests (fast, isolated)
│   ├── __init__.py
│   ├── utils.py               # Unit test utilities
│   ├── test_models.py         # Model validation tests
│   ├── test_cli.py            # CLI unit tests (33 tests)
│   ├── test_example_unit.py   # Example unit tests
│   └── test_yaml_converter.py # YAML converter tests
│
├── integration/                # Integration tests (component interaction)
│   ├── __init__.py
│   ├── utils.py               # Integration test utilities
│   ├── test_generator.py      # Generator integration tests
│   ├── test_excel_parser.py   # Parser integration tests
│   ├── test_excel_generation.py
│   ├── test_excel_parsing.py
│   ├── test_cli_integration.py # CLI integration tests
│   └── test_cli_real_conversion.py # Real conversion tests (14 tests)
│
└── end_to_end/                 # E2E tests (complete workflows)
    ├── __init__.py
    ├── utils.py               # E2E test utilities
    └── test_example_e2e.py    # E2E workflow tests
```

## Running Tests

### Prerequisites

```bash
# Install dependencies
uv sync --all-extras

# Or with pip
pip install -e ".[test]"
```

### Basic Test Commands

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=src/odcs_converter

# Run specific test file
uv run pytest tests/unit/test_models.py

# Run specific test class
uv run pytest tests/unit/test_models.py::TestODCSDataContract

# Run specific test method
uv run pytest tests/unit/test_models.py::TestODCSDataContract::test_valid_minimal_contract

# Run tests by marker
uv run pytest -m unit        # Only unit tests
uv run pytest -m integration # Only integration tests
uv run pytest -m e2e         # Only end-to-end tests

# Run CLI tests specifically
uv run pytest tests/unit/test_cli.py -v                    # CLI unit tests
uv run pytest tests/integration/test_cli_*.py -v           # CLI integration tests
```

### Using Makefile Commands

```bash
# Run all tests
make test

# Run specific test suites
make test-unit
make test-integration
make test-e2e

# CLI-specific test commands
make test-cli         # All CLI tests (if defined)

# Run with coverage report
make test-cov

# Run and generate HTML coverage report
make test-html
```

### Advanced Test Options

```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Stop on first failure
pytest -x

# Show local variables in tracebacks
pytest -l

# Run only failed tests from last run
pytest --lf

# Run failed tests first, then others
pytest --ff

# Disable warnings
pytest --disable-warnings

# Capture output (show print statements)
pytest -s

# Run with specific log level
pytest --log-cli-level=DEBUG
```

## Writing Tests

### Test File Naming

- Test files must start with `test_` or end with `_test.py`
- Test classes must start with `Test`
- Test methods must start with `test_`

### Basic Test Structure

```python
"""Module docstring describing the test suite."""

import pytest
from odcs_converter.models import ODCSDataContract


class TestODCSDataContract:
    """Test ODCSDataContract model."""

    def test_valid_contract(self):
        """Test creating a valid contract."""
        # Arrange
        data = {
            "version": "1.0.0",
            "kind": "DataContract",
            "apiVersion": "v3.0.2",
            "id": "test-contract",
            "status": "active"
        }

        # Act
        contract = ODCSDataContract(**data)

        # Assert
        assert contract.version == "1.0.0"
        assert contract.id == "test-contract"

    def test_invalid_contract(self):
        """Test validation of invalid contract."""
        # Arrange
        data = {"version": "1.0.0"}  # Missing required fields

        # Act & Assert
        with pytest.raises(ValidationError):
            ODCSDataContract(**data)
```

### Using Fixtures

```python
import pytest
from pathlib import Path


@pytest.fixture
def sample_contract():
    """Provide a sample contract for testing."""
    return {
        "version": "1.0.0",
        "kind": "DataContract",
        "apiVersion": "v3.0.2",
        "id": "test-contract",
        "status": "active"
    }


@pytest.fixture
def temp_output_dir(tmp_path):
    """Provide a temporary output directory."""
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    return output_dir


def test_with_fixtures(sample_contract, temp_output_dir):
    """Test using fixtures."""
    output_file = temp_output_dir / "test.xlsx"
    # Use sample_contract and output_file in test
    assert sample_contract["version"] == "1.0.0"
    assert temp_output_dir.exists()
```

### Parametrized Tests

```python
import pytest


@pytest.mark.parametrize("version,is_valid", [
    ("v3.0.0", True),
    ("v3.0.1", True),
    ("v3.1.0", True),
    ("v2.0.0", False),
    ("invalid", False),
])
def test_api_version(version, is_valid):
    """Test API version validation."""
    if is_valid:
        contract = ODCSDataContract(
            version="1.0.0",
            kind="DataContract",
            apiVersion=version,
            id="test",
            status="active"
        )
        assert contract.apiVersion == version
    else:
        with pytest.raises(Exception):
            ODCSDataContract(
                version="1.0.0",
                kind="DataContract",
                apiVersion=version,
                id="test",
                status="active"
            )
```

## Test Types

### Unit Tests

**Purpose**: Test individual components in isolation

**Characteristics**:
- Fast execution (< 1 second per test)
- No external dependencies
- Use mocks for dependencies
- High coverage of edge cases

**Example**:

```python
from tests.unit.utils import unit_test, UnitTestHelper


class TestModelValidation:
    """Unit tests for model validation."""

    @unit_test
    def test_field_validation(self, unit_test_helper):
        """Test field validation logic."""
        data = unit_test_helper.create_minimal_odcs_dict()
        contract = ODCSDataContract(**data)
        assert contract.version is not None
```

### Integration Tests

**Purpose**: Test component interactions

**Characteristics**:
- Medium execution time (1-10 seconds)
- Real file I/O when appropriate
- Test conversion workflows
- Focus on component integration

**Example**:

```python
from tests.integration.utils import integration_test


class TestConversionWorkflow:
    """Integration tests for conversion workflows."""

    @integration_test
    def test_odcs_to_excel_conversion(self, temp_dir):
        """Test ODCS to Excel conversion workflow."""
        from odcs_converter.generator import ODCSToExcelConverter

        converter = ODCSToExcelConverter()
        output_path = temp_dir / "output.xlsx"

        # Test conversion
        converter.generate_from_dict(sample_data, output_path)

        assert output_path.exists()
        assert output_path.stat().st_size > 0
```

### End-to-End Tests

**Purpose**: Test complete user workflows

**Characteristics**:
- Slower execution (10+ seconds)
- Test CLI interactions
- Real-world scenarios
- Complete workflow validation

**Example**:

```python
from tests.end_to_end.utils import e2e_test, EndToEndTestHelper


class TestCompleteWorkflow:
    """E2E tests for complete workflows."""

    @e2e_test
    def test_data_engineer_workflow(self, temp_dir, scenario_test_helper):
        """Test complete data engineer workflow."""
        success, results, errors = scenario_test_helper.simulate_data_engineer_workflow(temp_dir)

        assert success
        assert "Created ODCS JSON contract" in results["steps_completed"]
        assert len(errors) == 0
```

## Test Utilities

### Unit Test Utilities

Located in `tests/unit/utils.py`:

```python
from tests.unit.utils import (
    UnitTestHelper,
    MockFactory,
    ValidationHelper,
    unit_test
)

# Create test data
helper = UnitTestHelper()
minimal_odcs = helper.create_minimal_odcs_dict()

# Create mocks
mock_factory = MockFactory()
mock_file = mock_factory.create_mock_file_response("content")

# Validate data
validator = ValidationHelper()
validator.assert_odcs_contract_valid(data)
```

### Integration Test Utilities

Located in `tests/integration/utils.py`:

```python
from tests.integration.utils import (
    IntegrationTestHelper,
    integration_test
)

# Create complete test data
helper = IntegrationTestHelper()
complete_odcs = helper.create_complete_odcs_dict()
```

### E2E Test Utilities

Located in `tests/end_to_end/utils.py`:

```python
from tests.end_to_end.utils import (
    EndToEndTestHelper,
    CLITestHelper,
    PerformanceTestHelper,
    e2e_test
)

# Create production-like data
helper = EndToEndTestHelper()
prod_data = helper.create_production_like_odcs()

# Test CLI
cli_helper = CLITestHelper()
success, output = cli_helper.test_cli_help()

# Measure performance
perf_helper = PerformanceTestHelper()
elapsed, result = perf_helper.measure_conversion_time(func, *args)
```

## Best Practices

### 1. Follow AAA Pattern

```python
def test_example():
    """Test following Arrange-Act-Assert pattern."""
    # Arrange - Set up test data and conditions
    data = {"key": "value"}

    # Act - Execute the code under test
    result = process_data(data)

    # Assert - Verify the results
    assert result is not None
```

### 2. Use Descriptive Names

```python
# Good
def test_convert_valid_odcs_to_excel_creates_file():
    """Test that valid ODCS data converts to Excel file."""
    pass

# Avoid
def test_convert():
    """Test convert."""
    pass
```

### 3. Test One Thing Per Test

```python
# Good - Each test has a single focus
def test_contract_requires_version():
    """Test that contract requires version field."""
    pass

def test_contract_requires_id():
    """Test that contract requires id field."""
    pass

# Avoid - Testing multiple things
def test_contract_validation():
    """Test contract validation."""
    # Tests version, id, status, etc. all in one test
    pass
```

### 4. Use Fixtures for Shared Setup

```python
@pytest.fixture
def sample_excel_file(tmp_path):
    """Create a sample Excel file for testing."""
    file_path = tmp_path / "test.xlsx"
    # Create file
    return file_path

def test_parse_excel(sample_excel_file):
    """Test parsing Excel file."""
    parser = ExcelToODCSParser()
    result = parser.parse_from_file(sample_excel_file)
    assert result is not None
```

### 5. Mock External Dependencies

```python
from unittest.mock import patch, MagicMock

@patch('requests.get')
def test_fetch_from_url(mock_get):
    """Test fetching ODCS from URL."""
    # Arrange
    mock_response = MagicMock()
    mock_response.json.return_value = {"version": "1.0.0"}
    mock_get.return_value = mock_response

    # Act
    result = fetch_odcs_from_url("https://example.com/contract.json")

    # Assert
    assert result["version"] == "1.0.0"
    mock_get.assert_called_once()
```

### 6. Test Error Cases

```python
def test_invalid_input_raises_error():
    """Test that invalid input raises appropriate error."""
    with pytest.raises(ValueError) as exc_info:
        process_invalid_data(None)

    assert "data cannot be None" in str(exc_info.value)
```

### 7. Use Test Markers

```python
@pytest.mark.unit
def test_unit_functionality():
    """Unit test example."""
    pass

@pytest.mark.slow
def test_large_dataset():
    """Test that may take longer."""
    pass

@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature():
    """Test for future feature."""
    pass
```

## Code Quality

The project maintains high code quality standards through automated linting and formatting tools.

### Linting with Ruff

Run lint checks to ensure code follows style guidelines:

```bash
# Run all lint checks
make lint

# Auto-fix issues where possible
make format
```

**Current Status:** ✅ All lint checks passing

See [Lint Fixes Summary](./LINT_FIXES_SUMMARY.md) for details on resolved issues.

### Formatting with Black

Black is used for consistent code formatting:

```bash
# Format all code
make format

# Check formatting without changes
uv run black --check src/ tests/
```

### Type Checking with MyPy

Type hints are checked using MyPy (note: some issues with external library stubs remain):

```bash
# Run type checking
make type-check
```

**Note:** Type checking currently has known issues with missing type stubs for external libraries (yaml, requests, openpyxl, pandas). These are tracked separately from lint issues.

### Quality Target

Run all quality checks at once:

```bash
# Run lint, format, and type-check
make quality
```

### Best Practices for Code Quality

1. **Run lint before committing**: Ensure `make lint` passes
2. **Format automatically**: Use `make format` to apply Black formatting
3. **Fix lint issues promptly**: Address Ruff warnings as they appear
4. **Use `__all__` for re-exports**: Explicitly declare public module interfaces
5. **Follow type comparison rules**: Use `is`/`is not` for type comparisons

### Common Lint Rules

- **F401**: Unused imports - Remove or re-export with `__all__`
- **E721**: Type comparisons - Use `is`/`is not` instead of `==`/`!=`
- **F841**: Unused variables - Remove or prefix with underscore
- **E501**: Line too long - Keep lines under 100 characters (Black handles this)

## Continuous Integration

### GitHub Actions

Tests run automatically on:
- Push to main branch
- Pull requests
- Manual workflow dispatch

Configuration: `.github/workflows/test.yml`

### Running CI Tests Locally

```bash
# Run the same checks as CI
make ci-test

# Or manually
pytest --cov=src/odcs_converter --cov-report=xml --junitxml=junit/test-results.xml
```

### Coverage Requirements

- Minimum coverage: **80%**
- Coverage report generated in `htmlcov/`
- XML report for CI: `coverage.xml`

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Solution: Install in development mode
pip install -e .
# Or with uv
uv sync
```

#### 2. Fixture Not Found

```bash
# Solution: Check if fixture is defined in conftest.py or imported
# Make sure fixture is in scope
```

#### 3. Tests Pass Locally but Fail in CI

```bash
# Solution: Check for environment-specific issues
# - File path differences
# - Missing dependencies
# - Timezone issues
# - Random data generation
```

#### 4. Slow Tests

```bash
# Solution: Use pytest-xdist for parallel execution
pip install pytest-xdist
pytest -n auto
```

#### 5. Failed Assertions with Unclear Messages

```python
# Use custom assertion messages
assert result == expected, f"Expected {expected}, got {result}"

# Or use pytest's assert rewriting (automatic)
assert result == expected  # pytest shows both values
```

### Debug Tests

```bash
# Run with debugger
pytest --pdb

# Drop into debugger on failure
pytest --pdb --maxfail=1

# Print captured output
pytest -s

# Verbose output
pytest -vv
```

## Test Metrics

### Current Coverage by Module

- `models.py`: 95%
- `generator.py`: 88%
- `excel_parser.py`: 85%
- `yaml_converter.py`: 92%
- `cli.py`: 78%

### Test Execution Time

- Unit tests: ~0.5 seconds
- Integration tests: ~0.8 seconds
- E2E tests: ~0.7 seconds
- **Total**: ~2 seconds

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Python Testing Guide](https://realpython.com/python-testing/)
- [Test Fixtures Summary](testing/TEST_FIXES_SUMMARY.md)

## Contributing to Tests

When adding new features:

1. Write tests first (TDD approach)
2. Ensure tests cover edge cases
3. Add integration tests for workflows
4. Update this guide if adding new patterns
5. Run full test suite before committing
6. Maintain 80%+ coverage

## Questions?

- Check [Test Fixes Summary](TEST_FIXES_SUMMARY.md) for recent changes
- Open an issue on GitHub
- Contact: thiruselvaa@gmail.com

---

**Last Updated**: 2025-01-26
**Test Coverage**: 80%+
**Tests Passing**: 198/200