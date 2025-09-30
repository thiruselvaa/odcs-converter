# Contributing to ODCS Excel Generator

Thank you for your interest in contributing to ODCS Excel Generator! We welcome contributions from the community and are pleased to have you join us.

## 🚀 Quick Start

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Make your changes
5. Submit a pull request

## 📋 Prerequisites

- Python 3.8 or higher
- Git
- A GitHub account

## 🛠 Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR-USERNAME/odcs-excel-generator.git
cd odcs-excel-generator
```

### 2. Set Up Development Environment

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 3. Verify Setup

```bash
# Run tests
pytest

# Check code quality
black --check src/ tests/
ruff check src/ tests/
mypy src/

# Test the CLI
odcs-excel examples/example_contract.json test_output.xlsx
```

## 🔄 Development Workflow

### Branch Naming

Use descriptive branch names:
- `feature/add-new-worksheet-type`
- `fix/handle-missing-schema-fields`
- `docs/update-api-documentation`
- `refactor/improve-excel-styling`

### Making Changes

1. **Create a new branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write code following our style guide
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**:
   ```bash
   # Run the full test suite
   make test
   
   # Run specific tests
   pytest tests/test_generator.py::test_your_specific_test
   
   # Test with different Python versions (if available)
   tox
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "✨ Add new feature: descriptive message"
   ```

### Commit Message Convention

We use conventional commits with emojis:

- `✨ feat:` New features
- `🐛 fix:` Bug fixes
- `📚 docs:` Documentation changes
- `🎨 style:` Code style changes (formatting, etc.)
- `♻️ refactor:` Code refactoring
- `⚡ perf:` Performance improvements
- `✅ test:` Adding or updating tests
- `🔧 chore:` Maintenance tasks

Examples:
```
✨ feat: add support for nested schema objects
🐛 fix: handle empty tag arrays gracefully
📚 docs: update CLI usage examples
🔧 chore: update dependencies to latest versions
```

## 🧪 Testing Guidelines

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names: `test_generate_excel_with_empty_schema`
- Follow the AAA pattern: Arrange, Act, Assert
- Mock external dependencies (HTTP calls, file I/O when appropriate)

### Test Categories

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows

### Example Test

```python
def test_generate_excel_with_custom_styling():
    """Test Excel generation with custom styling configuration."""
    # Arrange
    style_config = {
        "header_font": Font(bold=True, color="FF0000"),
        "header_fill": PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    }
    generator = ODCSExcelGenerator(style_config=style_config)
    
    # Act
    generator.generate_from_file("examples/example_contract.json", "test_output.xlsx")
    
    # Assert
    assert Path("test_output.xlsx").exists()
    # Add more specific assertions
```

## 📋 Code Style Guidelines

We use automated tools to maintain consistent code style:

### Python Style

- **Formatter**: Black (line length: 88 characters)
- **Linter**: Ruff
- **Type Checker**: MyPy
- **Import Sorting**: Built into Ruff

### Key Principles

1. **Type Hints**: Use type hints for all function signatures
2. **Docstrings**: Use Google-style docstrings for public APIs
3. **Error Handling**: Handle errors gracefully with informative messages
4. **Logging**: Use structured logging with appropriate levels

### Example Code Style

```python
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

def process_schema_objects(
    schema_objects: List[Dict[str, Any]], 
    config: Optional[Dict[str, Any]] = None
) -> List[ProcessedSchema]:
    """Process ODCS schema objects into internal format.
    
    Args:
        schema_objects: List of raw schema object dictionaries
        config: Optional processing configuration
        
    Returns:
        List of processed schema objects
        
    Raises:
        ValidationError: If schema objects are invalid
    """
    if not schema_objects:
        logger.warning("No schema objects provided")
        return []
    
    processed = []
    for obj in schema_objects:
        try:
            processed_obj = ProcessedSchema.from_dict(obj)
            processed.append(processed_obj)
        except ValidationError as e:
            logger.error(f"Failed to process schema object {obj.get('name', 'unknown')}: {e}")
            raise
    
    return processed
```

## 🚦 Pull Request Process

### Before Submitting

1. **Update your branch**:
   ```bash
   git checkout main
   git pull origin main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run the full test suite**:
   ```bash
   make test-all
   ```

3. **Update documentation** if needed

### Pull Request Template

When submitting a PR, include:

- **Description**: Clear description of changes
- **Type**: Feature, bugfix, documentation, etc.
- **Testing**: How you tested the changes
- **Breaking Changes**: Any breaking changes
- **Related Issues**: Link to related issues

### Example PR Description

```markdown
## Description
Add support for generating separate worksheets for nested schema properties.

## Type of Change
- [x] New feature
- [ ] Bug fix
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- Added unit tests for nested schema processing
- Tested with example contract containing nested objects
- Verified Excel output contains expected nested worksheets

## Breaking Changes
None

## Related Issues
Closes #123
```

## 🐛 Reporting Issues

### Bug Reports

Include:
- Python version and OS
- Steps to reproduce
- Expected vs actual behavior
- Sample ODCS JSON (if applicable)
- Error messages and stack traces

### Feature Requests

Include:
- Use case description
- Proposed solution
- Example usage
- Alternative solutions considered

## 📚 Documentation

### Types of Documentation

1. **Code Documentation**: Docstrings and inline comments
2. **User Documentation**: README, examples, tutorials
3. **API Documentation**: Auto-generated from docstrings
4. **Developer Documentation**: This file and setup guides

### Documentation Standards

- Use clear, concise language
- Include code examples
- Keep examples up-to-date
- Link to related documentation

## 🏆 Recognition

Contributors are recognized in:
- GitHub contributor lists
- Release notes for significant contributions
- Special mention for first-time contributors

## ❓ Getting Help

- **Questions**: Open a GitHub Discussion
- **Real-time Chat**: Check if there's a Discord/Slack (if applicable)
- **Email**: Contact maintainers for sensitive issues

## 📄 License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

Thank you for contributing to ODCS Excel Generator! 🎉