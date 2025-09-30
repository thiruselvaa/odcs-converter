#!/usr/bin/env python3
"""
Setup script to initialize the test directory structure for ODCS Converter.

This script creates the complete test directory structure with proper organization
for unit tests, integration tests, and end-to-end tests, along with all necessary
subdirectories for test data management.
"""

import os
import sys
from pathlib import Path
from typing import List


def create_directory(path: Path) -> None:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created directory: {path}")


def create_file(path: Path, content: str = "") -> None:
    """Create file with optional content if it doesn't exist."""
    if not path.exists():
        path.write_text(content)
        print(f"✓ Created file: {path}")
    else:
        print(f"- File already exists: {path}")


def setup_test_directories() -> None:
    """Set up the complete test directory structure."""
    print("🏗️  Setting up test directory structure...")

    # Base test directory
    tests_dir = Path("tests")

    # Main test directories
    directories = [
        # Root test directories
        tests_dir,
        tests_dir / "logs",
        tests_dir / "reports",
        tests_dir / "fixtures",
        tests_dir / "outputs",

        # Centralized test data
        tests_dir / "test_data",
        tests_dir / "test_data" / "inputs",
        tests_dir / "test_data" / "inputs" / "json",
        tests_dir / "test_data" / "inputs" / "yaml",
        tests_dir / "test_data" / "inputs" / "excel",
        tests_dir / "test_data" / "expected_outputs",
        tests_dir / "test_data" / "expected_outputs" / "json",
        tests_dir / "test_data" / "expected_outputs" / "yaml",
        tests_dir / "test_data" / "expected_outputs" / "excel",

        # Unit tests
        tests_dir / "unit",
        tests_dir / "unit" / "fixtures",
        tests_dir / "unit" / "test_data",
        tests_dir / "unit" / "outputs",

        # Integration tests
        tests_dir / "integration",
        tests_dir / "integration" / "fixtures",
        tests_dir / "integration" / "test_data",
        tests_dir / "integration" / "outputs",

        # End-to-end tests
        tests_dir / "end_to_end",
        tests_dir / "end_to_end" / "fixtures",
        tests_dir / "end_to_end" / "test_data",
        tests_dir / "end_to_end" / "outputs",

        # Additional directories
        Path("junit"),  # For CI/CD test results
        Path("htmlcov"), # For coverage reports (will be generated)
    ]

    for directory in directories:
        create_directory(directory)


def create_init_files() -> None:
    """Create __init__.py files for proper Python package structure."""
    print("\n📦 Creating __init__.py files...")

    init_files = [
        Path("tests") / "__init__.py",
        Path("tests") / "unit" / "__init__.py",
        Path("tests") / "integration" / "__init__.py",
        Path("tests") / "end_to_end" / "__init__.py",
    ]

    init_content = '"""Test package initialization."""\n'

    for init_file in init_files:
        create_file(init_file, init_content)


def create_gitkeep_files() -> None:
    """Create .gitkeep files in empty directories to ensure they're tracked by git."""
    print("\n📁 Creating .gitkeep files for empty directories...")

    gitkeep_dirs = [
        Path("tests") / "logs",
        Path("tests") / "reports",
        Path("tests") / "fixtures",
        Path("tests") / "test_data" / "inputs" / "excel",
        Path("tests") / "unit" / "fixtures",
        Path("tests") / "unit" / "test_data",
        Path("tests") / "integration" / "fixtures",
        Path("tests") / "integration" / "test_data",
        Path("tests") / "end_to_end" / "fixtures",
        Path("tests") / "end_to_end" / "test_data",
        Path("junit"),
    ]

    for directory in gitkeep_dirs:
        gitkeep_file = directory / ".gitkeep"
        create_file(gitkeep_file, "# This file ensures the directory is tracked by git\n")


def create_readme_files() -> None:
    """Create README files for documentation."""
    print("\n📚 Creating README files...")

    # Unit tests README
    unit_readme = Path("tests") / "unit" / "README.md"
    unit_content = """# Unit Tests

This directory contains unit tests for individual components.

## Guidelines
- Test isolated functionality
- Use mocks for external dependencies
- Keep tests fast (< 1 second each)
- Aim for high code coverage

## Structure
- `test_*.py` - Test files
- `utils.py` - Unit test utilities and helpers
- `fixtures/` - Unit test specific fixtures
- `test_data/` - Unit test specific data
- `outputs/` - Generated test outputs (gitignored)

## Running
```bash
make test-unit
# or
pytest tests/unit/ -m unit
```
"""

    # Integration tests README
    integration_readme = Path("tests") / "integration" / "README.md"
    integration_content = """# Integration Tests

This directory contains integration tests for component interactions.

## Guidelines
- Test component interactions
- Use real file I/O when appropriate
- Test conversion workflows
- Medium execution time (1-10 seconds)

## Structure
- `test_*.py` - Test files
- `utils.py` - Integration test utilities and helpers
- `fixtures/` - Integration test specific fixtures
- `test_data/` - Integration test specific data
- `outputs/` - Generated test outputs (gitignored)

## Running
```bash
make test-integration
# or
pytest tests/integration/ -m integration
```
"""

    # E2E tests README
    e2e_readme = Path("tests") / "end_to_end" / "README.md"
    e2e_content = """# End-to-End Tests

This directory contains end-to-end tests for complete workflows.

## Guidelines
- Test complete user journeys
- Include CLI testing
- Test real-world scenarios
- May be slower (10+ seconds)

## Structure
- `test_*.py` - Test files
- `utils.py` - E2E test utilities and helpers
- `fixtures/` - E2E test specific fixtures
- `test_data/` - E2E test specific data
- `outputs/` - Generated test outputs (gitignored)

## Running
```bash
make test-e2e
# or
pytest tests/end_to_end/ -m e2e
```
"""

    create_file(unit_readme, unit_content)
    create_file(integration_readme, integration_content)
    create_file(e2e_readme, e2e_content)


def create_sample_test_files() -> None:
    """Create sample test files to demonstrate the structure."""
    print("\n🧪 Creating sample test files...")

    # Sample unit test
    unit_test_content = '''"""Sample unit test demonstrating the structure."""

import pytest
from tests.unit.utils import unit_test, UnitTestHelper

class TestSampleUnit:
    """Sample unit test class."""

    @unit_test
    def test_sample_functionality(self, unit_test_helper):
        """Sample test method."""
        # Arrange
        test_data = unit_test_helper.create_minimal_odcs_dict()

        # Act & Assert
        assert test_data["version"] == "1.0.0"
        assert test_data["kind"] == "DataContract"

    def test_basic_assertion(self):
        """Basic assertion example."""
        assert True  # Replace with actual test
'''

    # Sample integration test
    integration_test_content = '''"""Sample integration test demonstrating the structure."""

import pytest
from tests.integration.utils import integration_test, IntegrationTestHelper

class TestSampleIntegration:
    """Sample integration test class."""

    @integration_test
    def test_sample_integration(self, integration_test_helper):
        """Sample integration test method."""
        # Arrange
        test_data = integration_test_helper.create_complete_odcs_dict()

        # Act & Assert
        assert test_data["id"] == "integration-test-complete"
        assert len(test_data["schema"]) > 0

    def test_basic_integration(self):
        """Basic integration example."""
        assert True  # Replace with actual test
'''

    # Sample E2E test
    e2e_test_content = '''"""Sample end-to-end test demonstrating the structure."""

import pytest
from tests.end_to_end.utils import e2e_test, EndToEndTestHelper

class TestSampleE2E:
    """Sample E2E test class."""

    @e2e_test
    def test_sample_e2e_workflow(self, e2e_test_helper):
        """Sample E2E workflow test."""
        # Arrange
        test_data = e2e_test_helper.create_production_like_odcs()

        # Act & Assert
        assert test_data["id"] == "e2e-production-contract"
        assert "production" in test_data["tags"]

    def test_basic_e2e(self):
        """Basic E2E example."""
        assert True  # Replace with actual test
'''

    create_file(Path("tests") / "unit" / "test_sample_unit.py", unit_test_content)
    create_file(Path("tests") / "integration" / "test_sample_integration.py", integration_test_content)
    create_file(Path("tests") / "end_to_end" / "test_sample_e2e.py", e2e_test_content)


def verify_setup() -> bool:
    """Verify that the setup was successful."""
    print("\n🔍 Verifying setup...")

    required_files = [
        Path("tests") / "__init__.py",
        Path("tests") / "conftest.py",
        Path("tests") / "unit" / "utils.py",
        Path("tests") / "integration" / "utils.py",
        Path("tests") / "end_to_end" / "utils.py",
        Path("tests") / "README.md",
    ]

    required_dirs = [
        Path("tests") / "unit",
        Path("tests") / "integration",
        Path("tests") / "end_to_end",
        Path("tests") / "test_data" / "inputs",
        Path("tests") / "test_data" / "expected_outputs",
    ]

    missing_files = []
    missing_dirs = []

    for file_path in required_files:
        if not file_path.exists():
            missing_files.append(file_path)

    for dir_path in required_dirs:
        if not dir_path.exists():
            missing_dirs.append(dir_path)

    if missing_files or missing_dirs:
        print("❌ Setup verification failed!")
        if missing_files:
            print(f"Missing files: {missing_files}")
        if missing_dirs:
            print(f"Missing directories: {missing_dirs}")
        return False

    print("✅ Setup verification passed!")
    return True


def main() -> None:
    """Main setup function."""
    print("🚀 ODCS Converter Test Setup")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("src").exists() or not Path("pyproject.toml").exists():
        print("❌ Error: This script should be run from the project root directory.")
        print("   Make sure you're in the odcs-converter directory.")
        sys.exit(1)

    try:
        # Create directory structure
        setup_test_directories()

        # Create Python package files
        create_init_files()

        # Create .gitkeep files
        create_gitkeep_files()

        # Create documentation
        create_readme_files()

        # Create sample test files
        create_sample_test_files()

        # Verify setup
        if verify_setup():
            print("\n🎉 Test structure setup completed successfully!")
            print("\nNext steps:")
            print("1. Review the test structure in tests/README.md")
            print("2. Run 'make test' to verify everything works")
            print("3. Start writing tests using the provided utilities")
            print("4. Check the sample test files for examples")
        else:
            print("\n❌ Setup completed with some issues. Please check the output above.")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
