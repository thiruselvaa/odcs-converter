# Scripts Directory

This directory contains utility scripts for development, testing, and maintenance of the ODCS Converter project.

## 📋 Available Scripts

### setup_tests.py

**Purpose**: Initialize and set up the test directory structure

**Usage**:
```bash
python scripts/setup_tests.py
```

**Description**:
Creates the complete test directory structure with proper organization for unit tests, integration tests, and end-to-end tests. This script:
- Creates all necessary test directories
- Generates `__init__.py` files for proper Python package structure
- Creates `.gitkeep` files to track empty directories
- Generates README files for test documentation
- Creates sample test files as templates
- Verifies the setup was successful

**When to use**:
- Initial project setup
- After cloning the repository
- When restructuring test directories
- To regenerate test structure after cleanup

---

### run_checks.sh

**Purpose**: Run all code quality checks before committing

**Usage**:
```bash
# Run all checks in read-only mode
./scripts/run_checks.sh

# Run checks and auto-fix issues where possible
./scripts/run_checks.sh --fix
```

**Description**:
Comprehensive script that runs all code quality checks including:
1. Python version verification (>= 3.8)
2. Dependency installation/update
3. Code formatting with Black
4. Linting with Ruff
5. Type checking with MyPy
6. Security scanning with Bandit
7. Full test suite execution
8. Code coverage analysis (>= 80%)
9. TODO/FIXME comment detection
10. Documentation completeness check

**Exit Codes**:
- `0` - All checks passed
- `1` - One or more checks failed

**When to use**:
- Before committing code
- After making significant changes
- As part of pre-commit hooks
- In CI/CD pipelines

---

## 🚀 Quick Start

### First Time Setup

```bash
# 1. Set up test structure
python scripts/setup_tests.py

# 2. Run all checks to verify setup
./scripts/run_checks.sh
```

### Daily Development Workflow

```bash
# 1. Make your changes to code

# 2. Run checks before committing
./scripts/run_checks.sh --fix

# 3. If all checks pass, commit
git add .
git commit -m "Your commit message"
git push
```

## 📝 Adding New Scripts

When adding new scripts to this directory:

1. **Use descriptive names**: `action_target.ext` (e.g., `generate_docs.py`, `deploy_prod.sh`)

2. **Add shebang line**: For executable scripts
   ```bash
   #!/bin/bash
   # or
   #!/usr/bin/env python3
   ```

3. **Make executable**: 
   ```bash
   chmod +x scripts/your_script.sh
   ```

4. **Add documentation**: Update this README with:
   - Script name and purpose
   - Usage examples
   - Description of what it does
   - When to use it

5. **Include help text**: Scripts should support `--help` flag

6. **Error handling**: Use proper exit codes and error messages

7. **Test the script**: Ensure it works in different environments

## 🔧 Script Development Guidelines

### Python Scripts

```python
#!/usr/bin/env python3
"""
Brief description of what the script does.

Usage:
    python script_name.py [OPTIONS]

Examples:
    python script_name.py --option value
"""

import sys
from pathlib import Path


def main():
    """Main function."""
    # Script logic here
    pass


if __name__ == "__main__":
    main()
```

### Shell Scripts

```bash
#!/bin/bash
#
# Brief description of what the script does
#
# Usage: ./script_name.sh [OPTIONS]
#

set -e  # Exit on error

# Script logic here
```

## 🎯 Common Tasks

### Running Tests Only

```bash
# Instead of full checks, run tests directly
uv run pytest

# Or use make commands
make test
make test-unit
make test-integration
make test-e2e
```

### Formatting Code Only

```bash
# Check formatting
uv run black --check src/ tests/

# Auto-format
uv run black src/ tests/
```

### Linting Only

```bash
# Check linting
uv run ruff check src/ tests/

# Auto-fix linting issues
uv run ruff check --fix src/ tests/
```

### Coverage Report Only

```bash
# Generate coverage report
uv run pytest --cov=src/odcs_converter --cov-report=html

# Open coverage report
open htmlcov/index.html
```

## 🐛 Troubleshooting

### Script Permission Denied

```bash
# Solution: Make script executable
chmod +x scripts/script_name.sh
```

### Script Not Found

```bash
# Solution: Run from project root
cd /path/to/odcs-converter
./scripts/script_name.sh
```

### Python Module Not Found

```bash
# Solution: Install dependencies
uv sync --all-extras
# or
pip install -e ".[dev,test]"
```

### uv Command Not Found

```bash
# Solution: Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# or use pip
pip install uv
```

## 📦 Dependencies

Scripts in this directory may require:

- **Python 3.8+**: Core language requirement
- **uv**: Package manager (recommended)
- **pip**: Alternative package manager
- **bash**: For shell scripts
- **git**: Version control

### Optional Dependencies

- **black**: Code formatting
- **ruff**: Linting
- **mypy**: Type checking
- **bandit**: Security scanning
- **pytest**: Testing framework

## 🔗 Related Documentation

- [Development Setup](../docs/development/SETUP.md)
- [Contributing Guide](../docs/development/CONTRIBUTING.md)
- [Testing Guide](../docs/testing/TESTING.md)
- [Main README](../README.md)

## 💡 Tips

1. **Use virtual environments**: Always work in a virtual environment
2. **Run checks frequently**: Catch issues early
3. **Fix mode is safe**: The `--fix` flag only fixes auto-fixable issues
4. **Check before pushing**: Run checks before pushing to GitHub
5. **CI mirrors local**: CI runs the same checks as `run_checks.sh`

## 📞 Support

If you encounter issues with scripts:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the script's help: `script_name.sh --help`
3. Open an issue on GitHub
4. Contact: thiruselvaa@gmail.com

---

**Last Updated**: 2025-01-26
**Maintainer**: Thiruselva
**Project**: ODCS Converter