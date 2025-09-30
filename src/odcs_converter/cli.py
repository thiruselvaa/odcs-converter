"""Command-line interface for ODCS Converter - Bidirectional conversion between ODCS and Excel."""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn

from .generator import ODCSToExcelConverter
from .excel_parser import ExcelToODCSParser
from .yaml_converter import YAMLConverter


# Configure rich console
console = Console()

# Configure logging with rich handler
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)

logger = logging.getLogger(__name__)


def _configure_logging(verbose: bool, quiet: bool) -> None:
    """Configure logging level based on verbosity flags."""
    if quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif verbose:
        logging.getLogger().setLevel(logging.DEBUG)


def _detect_file_type(file_path: str) -> str:
    """Detect file type from extension."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix in [".xlsx", ".xls"]:
        return "excel"
    elif suffix in [".yaml", ".yml"]:
        return "yaml"
    elif suffix == ".json":
        return "json"
    else:
        return "unknown"


@click.command()
@click.argument("input_source", type=str)
@click.argument("output_file", type=click.Path())
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "yaml", "excel"], case_sensitive=False),
    help="Output format (auto-detected from file extension if not specified)",
)
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Path to configuration file"
)
@click.option(
    "--validate",
    is_flag=True,
    help="Validate against ODCS schema (for JSON/YAML output)",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output except errors")
def main(
    input_source: str,
    output_file: str,
    format: Optional[str] = None,
    config: Optional[str] = None,
    validate: bool = False,
    verbose: bool = False,
    quiet: bool = False,
) -> None:
    """Bidirectional converter between ODCS (Open Data Contract Standard) and Excel formats.

    Automatically detects conversion direction based on input and output file extensions:
    - ODCS (JSON/YAML) → Excel: Creates separate worksheets for each top-level field
    - Excel → ODCS (JSON/YAML): Parses worksheets back to ODCS format

    INPUT_SOURCE can be:
    - Local ODCS JSON/YAML file or Excel file
    - URL to ODCS JSON data (for ODCS→Excel conversion)

    OUTPUT_FILE extension determines the output format:
    - .xlsx/.xls for Excel output
    - .json for JSON output
    - .yaml/.yml for YAML output

    Examples:

        # ODCS to Excel
        odcs-converter contract.json output.xlsx
        odcs-converter contract.yaml output.xlsx
        odcs-converter https://example.com/contract.json output.xlsx

        # Excel to ODCS
        odcs-converter data.xlsx contract.json
        odcs-converter data.xlsx contract.yaml

        # With validation
        odcs-converter data.xlsx contract.json --validate
    """
    _configure_logging(verbose, quiet)

    try:
        # Detect input and output types
        is_url = input_source.startswith(("http://", "https://"))
        input_type = "url" if is_url else _detect_file_type(input_source)

        # Determine output format
        if format:
            output_format = format.lower()
        else:
            output_format = _detect_file_type(output_file)

        if output_format == "unknown":
            console.print(
                "❌ [bold red]Error:[/bold red] Cannot determine output format. Use --format option."
            )
            sys.exit(1)

        # Determine conversion direction
        if input_type in ["json", "yaml", "url"] and output_format == "excel":
            # ODCS to Excel conversion
            _odcs_to_excel(input_source, output_file, config, is_url)
        elif input_type == "excel" and output_format in ["json", "yaml"]:
            # Excel to ODCS conversion
            _excel_to_odcs(input_source, output_file, output_format, validate)
        else:
            console.print(
                f"❌ [bold red]Error:[/bold red] Unsupported conversion: {input_type} → {output_format}"
            )
            sys.exit(1)

    except FileNotFoundError as e:
        console.print(f"❌ [bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except ValueError as e:
        console.print(f"❌ [bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        console.print(f"❌ [bold red]Unexpected error:[/bold red] {e}")
        sys.exit(1)


def _odcs_to_excel(
    input_source: str, output_file: str, config: Optional[str], is_url: bool
) -> None:
    """Convert ODCS to Excel format."""
    # Load configuration if provided
    style_config = None
    if config:
        logger.info(f"Loading configuration from: {config}")
        # TODO: Implement configuration loading

    # Initialize converter
    converter = ODCSToExcelConverter(style_config=style_config)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:

        if is_url:
            task = progress.add_task("Fetching ODCS data from URL...", total=None)
            converter.generate_from_url(input_source, output_file)
        else:
            task = progress.add_task("Processing ODCS file...", total=None)
            if _detect_file_type(input_source) == "yaml":
                # Load YAML and convert to dict first
                yaml_data = YAMLConverter.yaml_to_dict(input_source)
                converter.generate_from_dict(yaml_data, output_file)
            else:
                converter.generate_from_file(input_source, output_file)

        progress.update(task, description="Generating Excel file...")

    console.print(
        f"✅ Excel file generated successfully: [bold green]{output_file}[/bold green]"
    )


def _excel_to_odcs(
    input_file: str, output_file: str, output_format: str, validate: bool
) -> None:
    """Convert Excel to ODCS format."""
    parser = ExcelToODCSParser()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:

        task = progress.add_task("Parsing Excel file...", total=None)
        odcs_data = parser.parse_from_file(input_file)

        progress.update(task, description=f"Converting to {output_format.upper()}...")

        # Validate if requested
        if validate:
            progress.update(task, description="Validating ODCS schema...")
            is_valid = parser.validate_odcs_data(odcs_data)
            if not is_valid:
                console.print(
                    "⚠️  [bold yellow]Warning:[/bold yellow] Generated ODCS data has validation issues"
                )

        # Write output file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_format == "yaml":
            YAMLConverter.dict_to_yaml(odcs_data, output_file)
        else:  # json
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(odcs_data, f, indent=2, ensure_ascii=False)

    console.print(
        f"✅ {output_format.upper()} file generated successfully: [bold green]{output_file}[/bold green]"
    )


@click.command("to-excel")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def odcs_to_excel(
    input_file: str,
    output_file: str,
    config: Optional[str] = None,
    verbose: bool = False,
) -> None:
    """Convert ODCS JSON/YAML to Excel format.

    Creates an Excel file with separate worksheets for each top-level ODCS field.
    """
    _configure_logging(verbose, False)

    try:
        _odcs_to_excel(input_file, output_file, config, False)
    except Exception as e:
        console.print(f"❌ [bold red]Error:[/bold red] {e}")
        sys.exit(1)


@click.command("to-odcs")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
    help="Output format (auto-detected from extension if not specified)",
)
@click.option("--validate", is_flag=True, help="Validate against ODCS schema")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def excel_to_odcs(
    input_file: str,
    output_file: str,
    format: Optional[str] = None,
    validate: bool = False,
    verbose: bool = False,
) -> None:
    """Convert Excel file to ODCS JSON/YAML format.

    Parses Excel worksheets and reconstructs ODCS data contract.
    """
    _configure_logging(verbose, False)

    try:
        # Determine output format
        if format:
            output_format = format.lower()
        else:
            output_format = _detect_file_type(output_file)
            if output_format not in ["json", "yaml"]:
                output_format = "json"  # default

        _excel_to_odcs(input_file, output_file, output_format, validate)
    except Exception as e:
        console.print(f"❌ [bold red]Error:[/bold red] {e}")
        sys.exit(1)


@click.command()
def version() -> None:
    """Show version information."""
    from . import __version__

    console.print(f"ODCS Converter version: [bold green]{__version__}[/bold green]")


@click.group()
def cli() -> None:
    """ODCS Converter - Bidirectional conversion between ODCS and Excel formats."""
    pass


# Add commands to group
cli.add_command(main, name="convert")
cli.add_command(odcs_to_excel)
cli.add_command(excel_to_odcs)
cli.add_command(version)


if __name__ == "__main__":
    cli()
