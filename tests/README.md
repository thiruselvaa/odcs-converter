# Test Organization and Structure

This document describes the comprehensive test organization structure for the ODCS Converter project, designed for maintainability, clarity, and ease of development.

## 📁 Directory Structure

```
tests/
├── README.md                           # This file
├── conftest.py                         # Shared pytest configuration and fixtures
├── pytest.ini                         # Pytest configuration
├── logs/                               # Test execution logs
├── reports/                            # Test reports and coverage
├── test_data/                          # Centralized test data management
│   ├── inputs/                         # Input test data
│   │   ├── json/                       # JSON ODCS contracts
│   │   ├── yaml/                       # YAML ODCS contracts
│   │   └── excel/                      # Sample Excel files
│   └── expected_outputs/               # Expected output data for validation
│       ├── json/                       # Expected JSON outputs
│       ├── yaml/                       # Expected YAML outputs
│       └── excel/                      # Expected Excel outputs
├── fixtures/                           # Shared test fixtures
├── outputs/                            # Generated test outputs (gitignored)
├── unit/                               # Unit tests
│   ├── utils.py                        # Unit test utilities
│   ├── fixtures/                       # Unit-specific fixtures
│   ├── test_data/                      # Unit-specific test data
│   ├── outputs/                        # Unit test outputs
│   └── test_*.py                       # Unit test files
├── integration/                        # Integration tests
│   ├── utils.py                        # Integration test utilities
│   ├── fixtures/                       # Integration-specific fixtures
│   ├── test_data/                      # Integration-specific test data
│   ├── outputs/                        # Integration test outputs
│   └── test_*.py                       # Integration test files
└── end_to_end/                         # End-to-end tests
    ├── utils.py                        # E2E test utilities
    ├── fixtures/                       # E2E-specific fixtures
    ├── test_data/                      # E2E-specific test data
    ├── outputs/                        # E2E test outputs
    └── test_*.py                       # E2E test files
```

## 🧪 Test Categories

### Unit Tests (`tests/unit/`)

**Purpose**: Test individual components in isolation with no external dependencies.

**Characteristics**:
- Fast execution (< 1 second per test)
- No file I/O, network calls, or database access
- Heavy use of mocks and stubs
- Test single functions/methods/classes
- High test coverage for business logic

**Examples**:
- Model validation logic
- Data transformation functions
- Utility function behavior
- Error handling for invalid inputs
- Edge cases and boundary conditions

**Utilities**: `tests/unit/utils.py` provides:
- `UnitTestHelper`: Sample data creation for isolated testing
- `MockFactory`: Mock object creation for dependencies
- `ValidationHelper`: Assertion helpers for model validation
- `FileHelper`: Temporary file creation for testing
- `ParameterizedTestData`: Test data for parameterized tests

**Markers**: `@pytest.mark.unit`

### Integration Tests (`tests/integration/`)

**Purpose**: Test component interactions and data flow between modules.

**Characteristics**:
- Medium execution time (1-10 seconds per test)
- Tests multiple components working together
- Real file I/O operations
- Testing conversion workflows
- Validation of component interfaces

**Examples**:
- ODCS to Excel conversion end-to-end
- Excel to ODCS parsing with validation
- YAML converter integration
- File format validation
- Error propagation between components

**Utilities**: `tests/integration/utils.py` provides:
- `IntegrationTestHelper`: Complete ODCS data samples
- `ExcelTestHelper`: Excel file creation and validation
- `ConversionTestHelper`: Roundtrip conversion testing
- `ComponentTestHelper`: Component interaction testing
- `WorkflowTestHelper`: Multi-step workflow simulation

**Markers**: `@pytest.mark.integration`

### End-to-End Tests (`tests/end_to_end/`)

**Purpose**: Test complete user workflows and real-world scenarios.

**Characteristics**:
- Slower execution (10+ seconds per test)
- Test complete user journeys
- CLI testing with actual commands
- Performance and stress testing
- Real-world data scenarios
- Error handling in complete workflows

**Examples**:
- Complete data engineer workflow simulation
- CLI command testing with real files
- Large dataset performance testing
- Compliance review workflows
- Error recovery scenarios
- Multi-format conversion chains

**Utilities**: `tests/end_to_end/utils.py` provides:
- `EndToEndTestHelper`: Production-like ODCS data
- `CLITestHelper`: CLI command execution and validation
- `PerformanceTestHelper`: Performance measurement utilities
- `ScenarioTestHelper`: Real-world scenario simulation
- `ErrorScenarioTestHelper`: Comprehensive error testing

**Markers**: `@pytest.mark.e2e`, `@pytest.mark.slow`, `@pytest.mark.cli`, `@pytest.mark.performance`

## 🏃 Running Tests

### Basic Commands

```bash
# Run all tests
make test

# Run specific test categories
make test-unit           # Unit tests only
make test-integration    # Integration tests only  
make test-e2e           # End-to-end tests only

# Run fast vs slow tests
make test-fast          # Unit + Integration (quick feedback)
make test-slow          # E2E + Performance (comprehensive)

# Run tests by functionality
make test-cli           # CLI-specific tests
make test-excel         # Excel-specific tests
make test-yaml          # YAML-specific tests
make test-conversion    # Conversion-specific tests
```

### Advanced Test Execution

```bash
# Run with coverage
make test-coverage

# Run in parallel (faster)
make test-parallel

# Run with debugging
make test-debug

# Run specific test file
pytest tests/unit/test_models.py -v

# Run specific test method
pytest tests/unit/test_models.py::TestODCSDataContract::test_valid_minimal_contract -v

# Run tests matching pattern
pytest -k "test_validation" -v
```

### Test Markers

Use pytest markers to run specific subsets:

```bash
# Run by marker
pytest -m unit          # Unit tests
pytest -m integration   # Integration tests
pytest -m e2e          # End-to-end tests
pytest -m slow         # Slow tests
pytest -m smoke        # Smoke tests
pytest -m performance  # Performance tests

# Combine markers
pytest -m "unit or integration"  # Fast tests
pytest -m "e2e and not slow"    # E2E but not slow ones
```

## 📊 Test Data Management

### Input Test Data

Located in `tests/test_data/inputs/`:

- **JSON Files**: Complete ODCS contracts in various configurations
  - `minimal_contract.json`: Minimal valid contract
  - `complete_contract.json`: Full-featured contract
  - `multi_table_contract.json`: Contract with multiple schema objects

- **YAML Files**: ODCS contracts in YAML format
- **Excel Files**: Sample Excel files for parsing tests

### Expected Outputs

Located in `tests/test_data/expected_outputs/`:

- Reference outputs for validation
- Golden master files for regression testing
- Expected Excel structures and formats

### Test-Specific Data

Each test category has its own `test_data/` directory for category-specific test files.

### Generated Outputs

All test-generated files go to `outputs/` directories:
- Automatically cleaned up after tests
- Organized by test category
- Excluded from version control

## 🔧 Test Utilities and Helpers

### Shared Utilities (`conftest.py`)

- **Fixtures**: Shared test fixtures for common data and objects
- **File Management**: Utilities for creating and cleaning test files
- **Test Configuration**: Pytest configuration and markers

### Category-Specific Utilities

Each test category has its own `utils.py` with specialized helpers:

- **Unit**: Mock factories, validation helpers, parameterized data
- **Integration**: Conversion helpers, workflow testing, component interaction
- **E2E**: CLI testing, performance measurement, scenario simulation

## 📈 Coverage and Quality

### Coverage Requirements

- **Unit Tests**: Aim for 90%+ coverage of business logic
- **Integration Tests**: Cover all major component interactions
- **E2E Tests**: Cover all user-facing workflows

### Quality Gates

Tests must pass these quality gates:

1. **All tests pass** in CI/CD pipeline
2. **Coverage threshold** maintained (80% minimum)
3. **Performance benchmarks** not exceeded
4. **No test warnings** or deprecation notices
5. **Code quality checks** pass (linting, formatting)

## 🛠️ Development Guidelines

### Writing New Tests

1. **Choose the right category**:
   - Unit: Testing isolated logic
   - Integration: Testing component interaction
   - E2E: Testing complete workflows

2. **Use appropriate utilities**:
   - Import helpers from the category's `utils.py`
   - Use shared fixtures from `conftest.py`
   - Leverage parameterized test data

3. **Follow naming conventions**:
   - Test files: `test_*.py`
   - Test classes: `Test*`
   - Test methods: `test_*`
   - Use descriptive names that explain what is being tested

4. **Add appropriate markers**:
   ```python
   @pytest.mark.unit
   @pytest.mark.validation
   def test_model_validation():
       pass
   ```

### Test Data Guidelines

1. **Use existing sample data** when possible
2. **Create minimal test data** for specific scenarios
3. **Store reusable data** in `test_data/inputs/`
4. **Use factories and builders** for dynamic test data generation

### Best Practices

1. **Isolation**: Tests should not depend on each other
2. **Deterministic**: Tests should produce consistent results
3. **Fast**: Keep tests as fast as possible for their category
4. **Clear**: Test names and structure should be self-documenting
5. **Maintainable**: Use utilities and helpers to reduce duplication

## 🚀 Continuous Integration

### CI Pipeline Integration

The test structure integrates with CI/CD:

```yaml
# Example CI steps
- name: Run Fast Tests
  run: make test-fast

- name: Run Full Test Suite
  run: make test

- name: Generate Coverage Report
  run: make test-coverage

- name: Run Performance Tests
  run: make test-performance
  if: github.event_name == 'schedule'  # Only on scheduled runs
```

### Test Reporting

- **Coverage reports**: Generated in `htmlcov/`
- **JUnit XML**: For CI integration (`junit/test-results.xml`)
- **Performance metrics**: Tracked over time
- **Test logs**: Available in `tests/logs/`

## 📚 Examples and Templates

### Example Test Structure

```python
# tests/unit/test_example.py
import pytest
from tests.unit.utils import UnitTestHelper, unit_test

class TestExampleComponent:
    """Test the example component functionality."""
    
    @unit_test
    def test_basic_functionality(self, unit_test_helper):
        """Test basic component functionality."""
        # Arrange
        test_data = unit_test_helper.create_minimal_odcs_dict()
        
        # Act
        result = component_function(test_data)
        
        # Assert
        assert result.is_valid()
        
    @pytest.mark.parametrize("input_value,expected", [
        ("valid", True),
        ("invalid", False),
    ])
    def test_validation_scenarios(self, input_value, expected):
        """Test various validation scenarios."""
        result = validate_input(input_value)
        assert result == expected
```

## 🔍 Troubleshooting

### Common Issues

1. **Tests failing in CI but passing locally**:
   - Check for file path dependencies
   - Verify test isolation
   - Check for timing issues

2. **Slow test execution**:
   - Profile tests to find bottlenecks
   - Consider moving slow tests to E2E category
   - Use mocks instead of real operations

3. **Flaky tests**:
   - Check for race conditions
   - Ensure proper test cleanup
   - Verify test data consistency

### Debug Mode

Run tests in debug mode for detailed information:

```bash
make test-debug
# or
pytest -vv --tb=long --showlocals --maxfail=1
```

## 📝 Contributing

When adding new features:

1. **Add unit tests** for new business logic
2. **Add integration tests** for new component interactions  
3. **Add E2E tests** for new user-facing features
4. **Update test data** if new formats are supported
5. **Update documentation** for significant changes

For questions or suggestions about the test structure, please create an issue or reach out to the development team.