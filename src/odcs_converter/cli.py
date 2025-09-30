"""Command-line interface for ODCS Converter - Bidirectional conversion between ODCS and Excel."""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
from enum import Enum

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    MofNCompleteColumn,
)
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.prompt import Confirm
from rich.tree import Tree
from rich import box

from .generator import ODCSToExcelConverter
from .excel_parser import ExcelToODCSParser
from .yaml_converter import YAMLConverter
from . import __version__


# Configure rich console with enhanced features
console = Console(stderr=True, force_terminal=True)

# Configure logging with rich handler
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True, markup=True)],
)

logger = logging.getLogger(__name__)

# Create the main Typer app
app = typer.Typer(
    name="odcs-converter",
    help="🔄 ODCS Converter - Complete ODCS v3.0.2 ↔ Excel conversion toolkit",
    rich_markup_mode="rich",
    add_completion=False,
)


class OutputFormat(str, Enum):
    """Supported output formats."""

    json = "json"
    yaml = "yaml"
    excel = "excel"


def _configure_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Configure logging level based on verbosity settings."""
    if quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)


def _show_banner() -> None:
    """Display the application banner with version info."""
    banner = Panel.fit(
        f"[bold blue]ODCS Converter[/bold blue] [green]v{__version__}[/green]\n"
        f"[dim]Complete ODCS v3.0.2 Implementation[/dim]",
        box=box.DOUBLE,
        style="blue",
    )
    console.print(banner)


def _show_file_info(file_path: Path, file_type: str) -> None:
    """Display file information in a formatted table."""
    if file_path.exists():
        file_size = _format_file_size(file_path.stat().st_size)
        table = Table(box=box.SIMPLE)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="yellow")

        table.add_row("File", str(file_path))
        table.add_row("Type", file_type)
        table.add_row("Size", file_size)

        console.print(table)


def _format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def _validate_url(url: str) -> bool:
    """Validate if string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def _show_conversion_summary(
    input_source: str, output_file: str, conversion_type: str, duration: float
) -> None:
    """Display conversion summary with timing information."""
    summary_table = Table(title="Conversion Summary", box=box.ROUNDED)
    summary_table.add_column("Property", style="bold cyan")
    summary_table.add_column("Value", style="yellow")

    summary_table.add_row("Input", input_source)
    summary_table.add_row("Output", output_file)
    summary_table.add_row("Type", conversion_type)
    summary_table.add_row("Duration", f"{duration:.2f}s")
    summary_table.add_row("Status", "[green]✅ Success[/green]")

    console.print(summary_table)


def _detect_file_type(file_path: Path) -> str:
    """Detect file type based on extension."""
    suffix = file_path.suffix.lower()
    if suffix in [".json"]:
        return "ODCS JSON"
    elif suffix in [".yaml", ".yml"]:
        return "ODCS YAML"
    elif suffix in [".xlsx", ".xls"]:
        return "Excel Workbook"
    else:
        return "Unknown"


def _show_supported_formats() -> None:
    """Display supported file formats."""
    formats_table = Table(title="Supported File Formats", box=box.ROUNDED)
    formats_table.add_column("Format", style="bold cyan")
    formats_table.add_column("Extensions", style="yellow")
    formats_table.add_column("Description", style="white")

    formats_table.add_row("ODCS JSON", ".json", "JSON format ODCS contracts")
    formats_table.add_row("ODCS YAML", ".yaml, .yml", "YAML format ODCS contracts")
    formats_table.add_row("Excel", ".xlsx, .xls", "Excel workbooks with 15 worksheets")
    formats_table.add_row("Remote URL", "http://, https://", "Remote ODCS contracts")

    console.print(formats_table)


@app.command()
def convert(
    input_source: str = typer.Argument(..., help="📁 Input file path or URL"),
    output_file: str = typer.Argument(..., help="📄 Output file path"),
    format: Optional[OutputFormat] = typer.Option(
        None,
        "--format",
        "-f",
        help="🎯 Output format (auto-detected from file extension if not specified)",
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-c", help="⚙️ Path to configuration file", exists=True
    ),
    validate: bool = typer.Option(
        False,
        "--validate",
        "--check",
        help="✅ Validate against ODCS v3.0.2 schema (for JSON/YAML output)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="🔍 Enable verbose logging with detailed progress",
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="🔇 Suppress all output except errors"
    ),
    no_banner: bool = typer.Option(
        False, "--no-banner", help="🚫 Skip showing the application banner"
    ),
    show_formats: bool = typer.Option(
        False, "--show-formats", help="📋 Show supported file formats and exit"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="🧪 Show what would be done without actually converting",
    ),
) -> None:
    """🔄 Bidirectional converter between ODCS and Excel with 100% v3.0.2 coverage.

    🎯 CONVERSION DIRECTIONS:
    • ODCS (JSON/YAML) → Excel: Creates 15 comprehensive worksheets
    • Excel → ODCS (JSON/YAML): Reconstructs complete ODCS structure
    • URL → Excel: Fetch remote ODCS and convert to Excel

    📁 INPUT SOURCES:
    • Local ODCS files (.json, .yaml, .yml)
    • Local Excel files (.xlsx, .xls)
    • Remote URLs (http/https) for ODCS data

    📊 OUTPUT FORMATS:
    • Excel (.xlsx) - 15 worksheets with complete ODCS v3.0.2 data
    • JSON (.json) - Structured ODCS contract
    • YAML (.yaml/.yml) - Human-readable ODCS contract

    ✨ FEATURES:
    • 100% ODCS v3.0.2 specification coverage
    • Advanced quality rules with all operators
    • Logical type options and constraints
    • Transform documentation and data lineage
    • Element-level authoritative definitions
    • Rich progress indicators and error reporting
    """
    _configure_logging(verbose, quiet)

    if show_formats:
        _show_supported_formats()
        raise typer.Exit()

    if not no_banner and not quiet:
        _show_banner()

    if dry_run:
        _show_dry_run_info(input_source, output_file, format)
        return

    start_time = time.time()

    try:
        # Determine conversion direction
        input_path = Path(input_source)
        output_path = Path(output_file)

        if _validate_url(input_source) or input_path.suffix.lower() in [
            ".json",
            ".yaml",
            ".yml",
        ]:
            # ODCS to Excel conversion
            _odcs_to_excel(input_source, str(output_path), config, verbose, quiet)
            conversion_type = "ODCS → Excel"
        elif input_path.suffix.lower() in [".xlsx", ".xls"]:
            # Excel to ODCS conversion
            _excel_to_odcs(
                str(input_path), str(output_path), format, validate, verbose, quiet
            )
            conversion_type = "Excel → ODCS"
        else:
            console.print(
                f"[red]❌ Error: Unsupported input file type: {input_source}[/red]"
            )
            raise typer.Exit(1)

        duration = time.time() - start_time

        if not quiet:
            _show_conversion_summary(
                input_source, output_file, conversion_type, duration
            )

    except Exception as e:
        console.print(f"[red]❌ Conversion failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


def _show_dry_run_info(
    input_source: str, output_file: str, format: Optional[OutputFormat]
) -> None:
    """Show what would be done in dry run mode."""
    console.print("[yellow]🧪 DRY RUN MODE - No files will be modified[/yellow]")

    dry_run_table = Table(title="Planned Conversion", box=box.ROUNDED)
    dry_run_table.add_column("Step", style="cyan")
    dry_run_table.add_column("Action", style="yellow")

    input_path = Path(input_source)
    output_path = Path(output_file)

    if _validate_url(input_source):
        dry_run_table.add_row("1. Input", f"Fetch from URL: {input_source}")
        dry_run_table.add_row("2. Detection", "Remote ODCS contract")
        dry_run_table.add_row("3. Conversion", "ODCS → Excel (15 worksheets)")
        dry_run_table.add_row("4. Output", f"Create: {output_file}")
    elif input_path.suffix.lower() in [".json", ".yaml", ".yml"]:
        dry_run_table.add_row("1. Input", f"Read: {input_source}")
        dry_run_table.add_row("2. Detection", f"ODCS {input_path.suffix.upper()}")
        dry_run_table.add_row("3. Conversion", "ODCS → Excel (15 worksheets)")
        dry_run_table.add_row("4. Output", f"Create: {output_file}")
    elif input_path.suffix.lower() in [".xlsx", ".xls"]:
        output_format = format or OutputFormat(output_path.suffix[1:])
        dry_run_table.add_row("1. Input", f"Read: {input_source}")
        dry_run_table.add_row("2. Detection", "Excel workbook")
        dry_run_table.add_row("3. Conversion", f"Excel → ODCS {output_format.upper()}")
        dry_run_table.add_row("4. Output", f"Create: {output_file}")

    console.print(dry_run_table)


def _odcs_to_excel(
    input_source: str,
    output_file: str,
    config: Optional[Path],
    verbose: bool,
    quiet: bool,
) -> None:
    """Convert ODCS to Excel format."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
            disable=quiet,
        ) as progress:
            # Load ODCS data
            load_task = progress.add_task("📥 Loading ODCS data...", total=100)

            if _validate_url(input_source):
                import requests

                response = requests.get(input_source, timeout=30)
                response.raise_for_status()

                if input_source.endswith((".yaml", ".yml")):
                    odcs_data = YAMLConverter.yaml_string_to_dict(response.text)
                else:
                    odcs_data = response.json()
            else:
                input_path = Path(input_source)
                if not input_path.exists():
                    raise FileNotFoundError(f"Input file not found: {input_source}")

                if input_path.suffix.lower() in [".yaml", ".yml"]:
                    odcs_data = YAMLConverter.yaml_to_dict(str(input_path))
                else:
                    with open(input_path, "r", encoding="utf-8") as f:
                        odcs_data = json.load(f)

            progress.update(load_task, completed=50)

            # Convert to Excel
            convert_task = progress.add_task("🔄 Converting to Excel...", total=100)

            # Load configuration if provided
            style_config = None
            if config:
                with open(config, "r", encoding="utf-8") as f:
                    style_config = json.load(f)

            converter = ODCSToExcelConverter(style_config=style_config)

            progress.update(load_task, completed=100)
            progress.update(convert_task, completed=30)

            # Generate Excel file
            converter.generate_from_dict(odcs_data, output_file)
            progress.update(convert_task, completed=100)

            if not quiet:
                console.print(
                    f"[green]✅ Successfully converted to Excel: {output_file}[/green]"
                )

    except Exception as e:
        raise Exception(f"ODCS to Excel conversion failed: {str(e)}")


def _excel_to_odcs(
    input_file: str,
    output_file: str,
    format: Optional[OutputFormat],
    validate: bool,
    verbose: bool,
    quiet: bool,
) -> None:
    """Convert Excel to ODCS format."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
            disable=quiet,
        ) as progress:
            # Parse Excel file
            parse_task = progress.add_task("📊 Parsing Excel file...", total=100)

            parser = ExcelToODCSParser()
            odcs_data = parser.parse_from_file(input_file)

            progress.update(parse_task, completed=100)

            # Determine output format
            output_path = Path(output_file)
            if format:
                output_format = format.value
            else:
                output_format = output_path.suffix[1:].lower()
                if output_format not in ["json", "yaml", "yml"]:
                    output_format = "json"

            # Convert and save
            save_task = progress.add_task(
                f"💾 Saving as {output_format.upper()}...", total=100
            )

            if output_format in ["yaml", "yml"]:
                YAMLConverter.dict_to_yaml(odcs_data, output_file)
            else:
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(odcs_data, f, indent=2, ensure_ascii=False)

            progress.update(save_task, completed=100)

            # Validate if requested
            if validate:
                validate_task = progress.add_task(
                    "✅ Validating ODCS schema...", total=100
                )
                try:
                    is_valid = parser.validate_odcs_data(odcs_data)
                    progress.update(validate_task, completed=100)

                    if is_valid:
                        if not quiet:
                            console.print(
                                "[green]✅ ODCS schema validation passed[/green]"
                            )
                    else:
                        if not quiet:
                            console.print(
                                "[yellow]⚠️ ODCS schema validation found issues[/yellow]"
                            )
                except Exception as e:
                    progress.update(validate_task, completed=100)
                    if not quiet:
                        console.print(f"[yellow]⚠️ Validation error: {str(e)}[/yellow]")

            if not quiet:
                console.print(
                    f"[green]✅ Successfully converted to {output_format.upper()}: {output_file}[/green]"
                )
                _show_parsing_results(odcs_data)

    except Exception as e:
        raise Exception(f"Excel to ODCS conversion failed: {str(e)}")


def _show_parsing_results(odcs_data: Dict[str, Any]) -> None:
    """Display parsing results summary."""
    results_table = Table(title="Parsing Results", box=box.SIMPLE)
    results_table.add_column("Component", style="cyan")
    results_table.add_column("Count", style="yellow")

    # Count various components
    dataset_count = len(odcs_data.get("dataset", {}).get("columns", []))
    quality_count = len(odcs_data.get("quality", []))

    results_table.add_row(
        "Datasets",
        str(len([odcs_data.get("dataset")] if odcs_data.get("dataset") else [])),
    )
    results_table.add_row("Columns", str(dataset_count))
    results_table.add_row("Quality Rules", str(quality_count))

    console.print(results_table)


@app.command("to-excel")
def odcs_to_excel(
    input_file: Path = typer.Argument(
        ..., help="📁 ODCS input file (JSON/YAML)", exists=True
    ),
    output_file: Path = typer.Argument(..., help="📄 Excel output file"),
    config: Optional[Path] = typer.Option(
        None, "--config", "-c", help="⚙️ Configuration file", exists=True
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="🔍 Verbose output with detailed progress"
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="🔇 Suppress output except errors"
    ),
) -> None:
    """📊 Convert ODCS contract to Excel workbook with 15 comprehensive worksheets.

    Creates a complete Excel representation of the ODCS contract with dedicated
    worksheets for all contract components including datasets, quality rules,
    logical types, and transform documentation.
    """
    _configure_logging(verbose, quiet)

    if not quiet:
        _show_banner()
        console.print("[bold cyan]🔄 ODCS → Excel Conversion[/bold cyan]")

    try:
        _odcs_to_excel(str(input_file), str(output_file), config, verbose, quiet)
    except Exception as e:
        console.print(f"[red]❌ Conversion failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


@app.command("to-odcs")
def excel_to_odcs(
    input_file: Path = typer.Argument(..., help="📊 Excel input file", exists=True),
    output_file: Path = typer.Argument(..., help="📄 ODCS output file"),
    format: Optional[OutputFormat] = typer.Option(
        None,
        "--format",
        "-f",
        help="🎯 Output format (auto-detected from extension if not specified)",
    ),
    validate: bool = typer.Option(
        False, "--validate", "--check", help="✅ Validate against ODCS v3.0.2 schema"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="🔍 Verbose output with parsing details"
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="🔇 Suppress output except errors"
    ),
) -> None:
    """📄 Convert Excel workbook back to ODCS contract format.

    Reconstructs a complete ODCS contract from Excel workbook data,
    preserving all contract components and metadata with optional
    schema validation.
    """
    _configure_logging(verbose, quiet)

    if not quiet:
        _show_banner()
        console.print("[bold cyan]🔄 Excel → ODCS Conversion[/bold cyan]")

    try:
        # Filter format to only allow json/yaml for this command
        if format == OutputFormat.excel:
            console.print(
                "[red]❌ Error: Excel format not supported for ODCS output[/red]"
            )
            raise typer.Exit(1)

        _excel_to_odcs(
            str(input_file), str(output_file), format, validate, verbose, quiet
        )
    except Exception as e:
        console.print(f"[red]❌ Conversion failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def version(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="🔍 Show detailed version information"
    ),
) -> None:
    """📋 Show version and system information."""

    # Basic version info
    version_panel = Panel.fit(
        f"[bold blue]ODCS Converter[/bold blue] [green]v{__version__}[/green]\n"
        f"[dim]Complete ODCS v3.0.2 Implementation[/dim]",
        box=box.ROUNDED,
        style="blue",
    )
    console.print(version_panel)

    if verbose:
        # System information
        import platform

        system_table = Table(title="System Information", box=box.SIMPLE)
        system_table.add_column("Component", style="cyan")
        system_table.add_column("Version", style="yellow")

        system_table.add_row("Python", f"{sys.version.split()[0]}")
        system_table.add_row("Platform", platform.platform())
        system_table.add_row("Architecture", platform.machine())

        console.print(system_table)

        # Features summary
        features = [
            "✅ 100% ODCS v3.0.2 specification coverage",
            "📊 15 comprehensive Excel worksheets",
            "🔄 Full bidirectional conversion",
            "🎯 Advanced quality rules and operators",
            "🔧 Logical type options and constraints",
            "📈 Transform documentation and lineage",
            "🛡️  Enterprise-grade validation",
        ]

        features_panel = Panel(
            "\n".join(features),
            title="[bold green]Features[/bold green]",
            box=box.ROUNDED,
            style="green",
        )
        console.print(features_panel)


@app.command()
def help() -> None:
    """📚 Show comprehensive help information."""
    help_content = """
# ODCS Converter Help

## Overview
ODCS Converter is a complete implementation of the ODCS v3.0.2 specification
with bidirectional conversion capabilities between ODCS contracts and Excel workbooks.

## Key Features
- **100% ODCS v3.0.2 Coverage**: Every field, every feature
- **15 Excel Worksheets**: Comprehensive data organization
- **Advanced Quality Rules**: All operators, SQL queries, custom engines
- **Logical Type Options**: String patterns, number ranges, array constraints
- **Transform Documentation**: Complete data lineage and logic
- **Rich CLI Interface**: Progress bars, validation, error reporting

## Commands

### Main Conversion (Auto-detection)
```bash
odcs-converter convert INPUT OUTPUT [OPTIONS]
```

### Specific Direction Commands
```bash
odcs-converter to-excel contract.json output.xlsx
odcs-converter to-odcs data.xlsx contract.yaml --validate
```

### Information Commands
```bash
odcs-converter version --verbose
odcs-converter help
```

## Common Options
- `--verbose, -v`: Detailed progress and debugging information
- `--quiet, -q`: Suppress all output except errors
- `--validate`: Validate ODCS schema compliance
- `--dry-run`: Preview conversion without executing
- `--help`: Show command-specific help

## Examples

### ODCS to Excel
```bash
# Local files
odcs-converter to-excel contract.json output.xlsx
odcs-converter to-excel contract.yaml output.xlsx --verbose

# With configuration
odcs-converter to-excel contract.json output.xlsx --config style.yaml
```

### Excel to ODCS
```bash
# With validation
odcs-converter to-odcs data.xlsx contract.json --validate

# Specific format
odcs-converter to-odcs data.xlsx contract.yaml --format yaml --verbose

# Auto-detection
odcs-converter convert data.xlsx contract.json
```

## Support
- Documentation: https://github.com/thiruselvaa/odcs-converter/docs
- Issues: https://github.com/thiruselvaa/odcs-converter/issues
- ODCS Specification: https://bitol-io.github.io/open-data-contract-standard/v3.0.2/
"""

    console.print(Markdown(help_content))


@app.command("formats")
def show_formats() -> None:
    """📋 Show all supported file formats and their descriptions."""
    _show_supported_formats()


def main() -> None:
    """Main entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
