"""Command-line interface for ODCS Excel Generator."""

import logging
import sys
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn

from .generator import ODCSExcelGenerator


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


@click.command()
@click.argument("input_source", type=str)
@click.argument("output_file", type=click.Path())
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Path to configuration file"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output except errors")
def main(
    input_source: str,
    output_file: str,
    config: Optional[str] = None,
    verbose: bool = False,
    quiet: bool = False,
) -> None:
    """Generate Excel files from ODCS (Open Data Contract Standard) JSON schema.

    INPUT_SOURCE can be either a local JSON file path or a URL to JSON data.
    OUTPUT_FILE is the path where the Excel file will be saved.

    Examples:

        odcs-excel contract.json output.xlsx

        odcs-excel https://example.com/contract.json output.xlsx

        odcs-excel contract.json output.xlsx --config config.yaml
    """
    # Configure logging level
    if quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Load configuration if provided
        style_config = None
        if config:
            logger.info(f"Loading configuration from: {config}")
            # TODO: Implement configuration loading
            # style_config = load_config(config)

        # Initialize generator
        generator = ODCSExcelGenerator(style_config=style_config)

        # Determine input type (file or URL)
        is_url = input_source.startswith(("http://", "https://"))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:

            if is_url:
                task = progress.add_task("Fetching data from URL...", total=None)
                generator.generate_from_url(input_source, output_file)
            else:
                task = progress.add_task("Processing local file...", total=None)
                generator.generate_from_file(input_source, output_file)

            progress.update(task, description="Generating Excel file...")

        console.print(
            f"✅ Excel file generated successfully: [bold green]{output_file}[/bold green]"
        )

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


@click.command()
def version() -> None:
    """Show version information."""
    from . import __version__

    console.print(
        f"ODCS Excel Generator version: [bold green]{__version__}[/bold green]"
    )


@click.group()
def cli() -> None:
    """ODCS Excel Generator CLI."""
    pass


# Add commands to group
cli.add_command(main, name="generate")
cli.add_command(version)


if __name__ == "__main__":
    main()
