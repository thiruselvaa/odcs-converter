"""
Warnings configuration for ODCS Converter.

This module configures Python warnings to provide a cleaner user experience
while maintaining important warning visibility during development.
"""

import warnings
import sys
import os
from typing import Optional


def configure_warnings(debug_mode: Optional[bool] = None) -> None:
    """
    Configure warning filters for the application.

    Args:
        debug_mode: If True, show all warnings. If False, suppress harmless warnings.
                   If None, determine from environment.
    """
    if debug_mode is None:
        debug_mode = os.getenv("ODCS_DEBUG", "").lower() in ("true", "1", "yes", "on")
        debug_mode = debug_mode or os.getenv("DEBUG", "").lower() in (
            "true",
            "1",
            "yes",
            "on",
        )

    if debug_mode:
        # In debug mode, show all warnings
        warnings.resetwarnings()
        warnings.simplefilter("always")
    else:
        # In production mode, suppress specific harmless warnings

        # Suppress Pydantic V2 migration warnings that don't affect functionality
        warnings.filterwarnings(
            "ignore",
            category=DeprecationWarning,
            message=".*Support for class-based `config` is deprecated.*",
        )

        # Suppress field shadowing warnings that we've handled with aliases
        warnings.filterwarnings(
            "ignore",
            category=UserWarning,
            message='.*Field name "schema" in .* shadows an attribute in parent.*',
        )

        # Suppress runpy warnings when running as module
        warnings.filterwarnings(
            "ignore",
            category=RuntimeWarning,
            message=".*found in sys.modules after import of package.*",
        )

        # Suppress pandas future warnings if any
        warnings.filterwarnings("ignore", category=FutureWarning, module="pandas.*")

        # Suppress openpyxl warnings about styles
        warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl.*")


def setup_import_warnings() -> None:
    """
    Set up warnings configuration at import time.
    This should be called early in the application lifecycle.
    """
    # Check if we're in a test environment
    is_testing = "pytest" in sys.modules or "unittest" in sys.modules

    # Check if we're in development mode
    is_development = os.getenv("ODCS_ENV", "").lower() in (
        "local",
        "dev",
        "development",
    )

    # Configure based on context
    if is_testing:
        # During tests, we might want to see deprecation warnings
        warnings.filterwarnings(
            "ignore",
            category=UserWarning,
            message='.*Field name "schema" in .* shadows an attribute in parent.*',
        )
        warnings.filterwarnings(
            "ignore",
            category=RuntimeWarning,
            message=".*found in sys.modules after import of package.*",
        )
    elif is_development:
        # In development, show most warnings but suppress the annoying ones
        configure_warnings(debug_mode=False)
    else:
        # In production, suppress non-critical warnings
        configure_warnings(debug_mode=False)


def suppress_warning_context():
    """
    Context manager to temporarily suppress all warnings.

    Usage:
        with suppress_warning_context():
            # Code that might generate warnings
            pass
    """

    class SuppressWarnings:
        def __enter__(self):
            self.old_filters = warnings.filters[:]
            warnings.resetwarnings()
            warnings.simplefilter("ignore")
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            warnings.resetwarnings()
            warnings.filters[:] = self.old_filters
            return False

    return SuppressWarnings()


# Automatically configure warnings when this module is imported
setup_import_warnings()
