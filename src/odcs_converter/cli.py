"""Command-line interface for ODCS Converter - Bidirectional conversion between ODCS and Excel."""

# Configure warnings early
from .warnings_config import configure_warnings

configure_warnings()

import json
import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from enum import Enum

import typer
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box

from .generator import ODCSToExcelConverter
from .excel_parser import ExcelToODCSParser
from .yaml_converter import YAMLConverter
from .template_generator import TemplateGenerator, TemplateType
from .logging_config import (
    setup_logging,
    get_logger,
    LogContext,
    log_operation_start,
    log_operation_end,
)
from .logging_utils import PerformanceTracker
from . import __version__


# Configure rich console with enhanced features
console = Console(stderr=True, force_terminal=True)

# Initialize logging (will be properly configured when CLI commands are run)
logger = get_logger(__name__)

# Initialize performance tracker
performance_tracker = PerformanceTracker()

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


def _configure_logging(
    verbose: bool = False, quiet: bool = False, environment: str = None
) -> None:
    """Configure comprehensive logging with loguru."""
    # Determine log level based on verbosity
    if quiet:
        level_override = "ERROR"
    elif verbose:
        level_override = "DEBUG"
    else:
        level_override = None

    # Get environment from CLI option or environment variable
    env = environment or os.getenv("ODCS_ENV", "local")

    # Override log level if specified
    if level_override:
        os.environ["ODCS_LOG_LEVEL"] = level_override

    # Setup logging with environment-specific configuration
    setup_logging(environment=env)

    # Update global logger
    global logger
    logger = get_logger(__name__)


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
@performance_tracker.track_performance("cli.convert")
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
    environment: Optional[str] = typer.Option(
        None,
        "--env",
        "--environment",
        help="🌍 Logging environment (local, dev, test, stage, prod)",
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
    _configure_logging(verbose, quiet, environment)

    # Start operation tracking
    operation_id = log_operation_start(
        "convert",
        input_source=input_source,
        output_file=output_file,
        format=format.value if format else "auto",
    )

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
        with LogContext(operation_id, operation="convert"):
            # Determine conversion direction
            input_path = Path(input_source)
            output_path = Path(output_file)

            logger.info(
                "Starting conversion",
                input_source=input_source,
                output_file=output_file,
                correlation_id=operation_id,
            )

            if _validate_url(input_source) or input_path.suffix.lower() in [
                ".json",
                ".yaml",
                ".yml",
            ]:
                # ODCS to Excel conversion
                logger.info(
                    "Detected ODCS → Excel conversion",
                    input_type="ODCS",
                    output_type="Excel",
                )
                _odcs_to_excel(input_source, str(output_path), config, verbose, quiet)
                conversion_type = "ODCS → Excel"
            elif input_path.suffix.lower() in [".xlsx", ".xls"]:
                # Excel to ODCS conversion
                logger.info(
                    "Detected Excel → ODCS conversion",
                    input_type="Excel",
                    output_type="ODCS",
                )
                _excel_to_odcs(
                    str(input_path), str(output_path), format, validate, verbose, quiet
                )
                conversion_type = "Excel → ODCS"
            else:
                error_msg = f"Unsupported input file type: {input_source}"
                logger.error(
                    "Conversion failed", error=error_msg, input_source=input_source
                )
                console.print(f"[red]❌ Error: {error_msg}[/red]")
                raise typer.Exit(1)

            duration = time.time() - start_time

            logger.info(
                "Conversion completed successfully",
                conversion_type=conversion_type,
                duration_seconds=round(duration, 2),
                input_source=input_source,
                output_file=output_file,
            )

            if not quiet:
                _show_conversion_summary(
                    input_source, output_file, conversion_type, duration
                )

            log_operation_end(
                "convert",
                operation_id,
                success=True,
                conversion_type=conversion_type,
                duration_seconds=duration,
            )

    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            "Conversion failed",
            error=str(e),
            input_source=input_source,
            output_file=output_file,
            duration_seconds=round(duration, 2),
            exception_type=type(e).__name__,
        )

        log_operation_end(
            "convert",
            operation_id,
            success=False,
            error=str(e),
            duration_seconds=duration,
        )

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
@performance_tracker.track_performance("cli.odcs_to_excel")
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
        False, "--quiet", "-q", help="🔇 Suppress all output except errors"
    ),
    environment: Optional[str] = typer.Option(
        None,
        "--env",
        "--environment",
        help="🌍 Logging environment (local, dev, test, stage, prod)",
    ),
) -> None:
    """📊 Convert ODCS contract to Excel workbook with 15 comprehensive worksheets.

    Creates a complete Excel representation of the ODCS contract with dedicated
    worksheets for all contract components including datasets, quality rules,
    logical types, and transform documentation.
    """
    _configure_logging(verbose, quiet, environment)

    # Start operation tracking
    operation_id = log_operation_start(
        "odcs_to_excel",
        input_file=str(input_file),
        output_file=str(output_file),
    )

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
@performance_tracker.track_performance("cli.excel_to_odcs")
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
        False, "--quiet", "-q", help="🔇 Suppress all output except errors"
    ),
    environment: Optional[str] = typer.Option(
        None,
        "--env",
        "--environment",
        help="🌍 Logging environment (local, dev, test, stage, prod)",
    ),
) -> None:
    """📄 Convert Excel workbook back to ODCS contract format.

    Reconstructs a complete ODCS contract from Excel workbook data,
    preserving all contract components and metadata with optional
    schema validation.
    """
    _configure_logging(verbose, quiet, environment)

    # Start operation tracking
    operation_id = log_operation_start(
        "excel_to_odcs",
        input_file=str(input_file),
        output_file=str(output_file),
        format=format.value if format else "auto",
    )

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
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="🔇 Suppress all output except errors"
    ),
    environment: Optional[str] = typer.Option(
        None,
        "--env",
        "--environment",
        help="🌍 Logging environment (local, dev, test, stage, prod)",
    ),
) -> None:
    """📋 Show version and system information."""
    _configure_logging(verbose, quiet, environment)

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
def help(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="🔍 Show detailed help information"
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="🔇 Suppress all output except errors"
    ),
    environment: Optional[str] = typer.Option(
        None,
        "--env",
        "--environment",
        help="🌍 Logging environment (local, dev, test, stage, prod)",
    ),
) -> None:
    """📚 Show comprehensive help information."""
    _configure_logging(verbose, quiet, environment)
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
def show_formats(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="🔍 Show detailed format information"
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="🔇 Suppress all output except errors"
    ),
    environment: Optional[str] = typer.Option(
        None,
        "--env",
        "--environment",
        help="🌍 Logging environment (local, dev, test, stage, prod)",
    ),
) -> None:
    """📋 Show supported file formats and their descriptions."""
    _configure_logging(verbose, quiet, environment)
    _show_supported_formats()


@app.command("generate-template")
def generate_template(
    output: Path = typer.Argument(
        ...,
        help="📁 Output path for the Excel template file",
        exists=False,
    ),
    template_type: str = typer.Option(
        "full",
        "--type",
        "-t",
        help="📝 Template type: minimal (essential fields only), required (all required fields), full (all fields)",
    ),
    no_examples: bool = typer.Option(
        False,
        "--no-examples",
        help="🚫 Don't include example values in the template",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="🔍 Show detailed information"
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="🔇 Suppress all output except errors"
    ),
    environment: Optional[str] = typer.Option(
        None,
        "--env",
        "--environment",
        help="🌍 Logging environment (local, dev, test, stage, prod)",
    ),
) -> None:
    """📋 Generate sample Excel template for creating ODCS data contracts.

    This command creates pre-formatted Excel templates with:
    - Color-coded headers (RED = required, BLUE = optional)
    - Example values and helpful descriptions
    - Cell comments with field explanations
    - Multiple worksheets for different contract sections

    Template Types:

    • minimal: Only the most essential required fields
      - Basic Information (5 fields)
      - Schema (2 fields)
      - Schema Properties (3 fields)
      Perfect for quick proof-of-concept contracts

    • required: All required fields plus common optional fields
      - Basic Information (7 fields)
      - Servers (3 fields)
      - Schema (4 fields)
      - Schema Properties (5 fields)
      Good for standard production contracts

    • full: All available fields (required + optional)
      - All 15 worksheet types
      - Complete field coverage
      - Maximum flexibility and detail
      Best for comprehensive data contracts

    Examples:

      # Generate a minimal template
      odcs-converter generate-template minimal_template.xlsx --type minimal

      # Generate a full template with examples
      odcs-converter generate-template full_template.xlsx --type full

      # Generate required fields template without examples
      odcs-converter generate-template template.xlsx --type required --no-examples
    """
    _configure_logging(verbose, quiet, environment)

    with LogContext(operation="generate_template", template_type=template_type):
        try:
            # Validate template type
            template_type_lower = template_type.lower()
            if template_type_lower not in ["minimal", "required", "full"]:
                console.print(
                    f"[bold red]❌ Invalid template type: {template_type}[/bold red]"
                )
                console.print("[yellow]Valid types: minimal, required, full[/yellow]")
                raise typer.Exit(1)

            # Map string to enum
            type_mapping = {
                "minimal": TemplateType.MINIMAL,
                "required": TemplateType.REQUIRED,
                "full": TemplateType.FULL,
            }
            template_enum = type_mapping[template_type_lower]

            # Show generation info
            if not quiet:
                console.print(
                    f"\n[bold cyan]📋 Generating {template_type_lower} Excel template...[/bold cyan]\n"
                )

                info_table = Table(show_header=False, box=box.ROUNDED)
                info_table.add_column("Field", style="cyan")
                info_table.add_column("Value", style="white")

                info_table.add_row("Template Type", template_type_lower.upper())
                info_table.add_row(
                    "Include Examples", "Yes" if not no_examples else "No"
                )
                info_table.add_row("Output File", str(output))

                console.print(info_table)
                console.print()

            # Create template generator
            generator = TemplateGenerator()

            # Generate template with progress indicator
            with console.status("[bold green]Creating template..."):
                generator.generate_template(
                    output_path=output,
                    template_type=template_enum,
                    include_examples=not no_examples,
                )

            if not quiet:
                console.print(
                    f"\n[bold green]✅ Template generated successfully![/bold green]"
                )
                console.print(f"[dim]📄 File: {output}[/dim]\n")

                # Show next steps
                next_steps = Panel(
                    "[bold white]Next Steps:[/bold white]\n\n"
                    f"1. Open the template: [cyan]{output}[/cyan]\n"
                    "2. Read the [cyan]📖 Instructions[/cyan] sheet\n"
                    "3. Fill in your data (replace example rows)\n"
                    "4. [bold]RED headers[/bold] = REQUIRED fields\n"
                    "5. [bold blue]BLUE headers[/bold blue] = OPTIONAL fields\n"
                    f"6. Convert to ODCS: [cyan]odcs-converter excel-to-odcs {output}[/cyan]\n",
                    title="🎯 How to Use This Template",
                    border_style="green",
                )
                console.print(next_steps)

            logger.info(
                f"Template generated successfully",
                template_type=template_type_lower,
                output=str(output),
                include_examples=not no_examples,
            )

        except Exception as e:
            logger.error(f"Failed to generate template: {e}")
            console.print(f"\n[bold red]❌ Error: {e}[/bold red]\n")
            raise typer.Exit(1)


def main() -> None:
    """Main entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
