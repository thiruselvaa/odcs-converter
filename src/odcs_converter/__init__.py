"""ODCS Converter - Bidirectional conversion between ODCS and Excel formats."""

# Configure warnings before any other imports
from .warnings_config import configure_warnings

configure_warnings()

__version__ = "0.2.0"
__author__ = "Thiruselva"
__email__ = "thiruselvaa@gmail.com"

from .generator import ODCSToExcelConverter
from .excel_parser import ExcelToODCSParser
from .yaml_converter import YAMLConverter
from .models import ODCSDataContract
from .cli import main, odcs_to_excel, excel_to_odcs

__all__ = [
    "ODCSToExcelConverter",
    "ExcelToODCSParser",
    "YAMLConverter",
    "ODCSDataContract",
    "main",
    "odcs_to_excel",
    "excel_to_odcs",
]
