#!/bin/bash
#
# Run all code quality checks for ODCS Converter
# This script runs linting, formatting, type checking, and tests
#
# Usage: ./scripts/run_checks.sh [--fix]
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the project root
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: Must be run from project root directory${NC}"
    exit 1
fi

# Parse arguments
FIX_MODE=false
if [ "$1" == "--fix" ]; then
    FIX_MODE=true
fi

# Print section header
print_header() {
    echo ""
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

# Print success message
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Print error message
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Print warning message
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Track if any checks failed
CHECKS_FAILED=0

# 1. Check Python version
print_header "Checking Python Version"
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    print_success "Python version $PYTHON_VERSION (>= $REQUIRED_VERSION required)"
else
    print_error "Python version $PYTHON_VERSION is too old (>= $REQUIRED_VERSION required)"
    CHECKS_FAILED=1
fi

# 2. Install/Update dependencies
print_header "Installing Dependencies"
if command -v uv &> /dev/null; then
    print_success "Using uv for dependency management"
    uv sync --all-extras
else
    print_warning "uv not found, using pip"
    pip install -e ".[dev,test]"
fi

# 3. Code Formatting with Black
print_header "Code Formatting (Black)"
if [ "$FIX_MODE" = true ]; then
    print_warning "Running in fix mode - will format code"
    if uv run black src/ tests/ examples/ scripts/*.py; then
        print_success "Code formatted successfully"
    else
        print_error "Code formatting failed"
        CHECKS_FAILED=1
    fi
else
    if uv run black --check src/ tests/ examples/ scripts/*.py; then
        print_success "Code formatting check passed"
    else
        print_error "Code formatting check failed (run with --fix to auto-format)"
        CHECKS_FAILED=1
    fi
fi

# 4. Linting with Ruff
print_header "Linting (Ruff)"
if [ "$FIX_MODE" = true ]; then
    print_warning "Running in fix mode - will fix linting issues"
    if uv run ruff check --fix src/ tests/ examples/; then
        print_success "Linting issues fixed"
    else
        print_error "Some linting issues couldn't be fixed automatically"
        CHECKS_FAILED=1
    fi
else
    if uv run ruff check src/ tests/ examples/; then
        print_success "Linting check passed"
    else
        print_error "Linting check failed (run with --fix to auto-fix)"
        CHECKS_FAILED=1
    fi
fi

# 5. Type Checking with MyPy
print_header "Type Checking (MyPy)"
if uv run mypy src/ --ignore-missing-imports --no-strict-optional; then
    print_success "Type checking passed"
else
    print_warning "Type checking found issues (not failing build)"
    # Don't fail on mypy errors for now
fi

# 6. Security Check with Bandit
print_header "Security Check (Bandit)"
if command -v bandit &> /dev/null; then
    if uv run bandit -r src/ -ll; then
        print_success "Security check passed"
    else
        print_warning "Security check found issues (not failing build)"
    fi
else
    print_warning "Bandit not installed, skipping security check"
fi

# 7. Run Tests
print_header "Running Tests"
if uv run pytest tests/ -v --tb=short; then
    print_success "All tests passed"
else
    print_error "Tests failed"
    CHECKS_FAILED=1
fi

# 8. Test Coverage
print_header "Test Coverage"
if uv run pytest tests/ --cov=src/odcs_converter --cov-report=term-missing --cov-report=html --cov-fail-under=80; then
    print_success "Code coverage meets requirements (>= 80%)"
else
    print_error "Code coverage below 80%"
    CHECKS_FAILED=1
fi

# 9. Check for TODO/FIXME comments
print_header "Checking for TODOs/FIXMEs"
TODO_COUNT=$(grep -r "TODO\|FIXME" src/ tests/ --exclude-dir=__pycache__ | wc -l || echo "0")
if [ "$TODO_COUNT" -gt 0 ]; then
    print_warning "Found $TODO_COUNT TODO/FIXME comments"
    grep -rn "TODO\|FIXME" src/ tests/ --exclude-dir=__pycache__ || true
else
    print_success "No TODO/FIXME comments found"
fi

# 10. Check documentation
print_header "Documentation Check"
UNDOCUMENTED=$(grep -r "def \|class " src/ --include="*.py" | grep -v "\"\"\"" | wc -l || echo "0")
if [ "$UNDOCUMENTED" -gt 0 ]; then
    print_warning "Some functions/classes may lack documentation"
else
    print_success "Documentation check passed"
fi

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}          Check Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  - Review the output above"
    echo "  - Commit your changes"
    echo "  - Push to GitHub"
    exit 0
else
    echo -e "${RED}✗ Some checks failed${NC}"
    echo ""
    echo "To fix issues:"
    echo "  - Run with --fix flag: ./scripts/run_checks.sh --fix"
    echo "  - Review the errors above"
    echo "  - Fix manually if needed"
    exit 1
fi
