#!/usr/bin/env python3
"""
Main entry point for the ODCS Converter CLI when running as a module.

This file allows the package to be run with `python -m odcs_converter`
without triggering runpy warnings.
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main() or 0)
