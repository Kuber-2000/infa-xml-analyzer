"""CLI interface for infa-xml-analyzer."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console

from . import __version__
from .formatter import export_csv, print_lineage, print_mappings, print_summary
from .parser import parse_xml, scan_directory

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="infa-xml-analyzer")
def cli() -> None:
    """Informatica XML Analyzer - Parse and analyze Informatica PowerCenter XML exports."""


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--detail", is_flag=True, help="Show detailed mapping information.")
@click.option("--lineage", is_flag=True, help="Show data lineage paths.")
def analyze(file: Path, detail: bool, lineage: bool) -> None:
    """Analyze a single Informatica XML export file."""
    try:
        result = parse_xml(file)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    if not result.folders:
        console.print("[yellow]No Informatica metadata found in this file.[/yellow]")
        return

    print_summary(result)

    if detail:
        print_mappings(result)

    if lineage:
        print_lineage(result)


@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--no-recursive", is_flag=True, help="Do not scan subdirectories.")
@click.option("--detail", is_flag=True, help="Show detailed mapping information.")
@click.option("--lineage", is_flag=True, help="Show data lineage paths.")
def scan(directory: Path, no_recursive: bool, detail: bool, lineage: bool) -> None:
    """Scan a directory for Informatica XML files and analyze them."""
    try:
        result = scan_directory(directory, recursive=not no_recursive)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    if not result.folders:
        console.print("[yellow]No Informatica metadata found.[/yellow]")
        return

    print_summary(result)

    if detail:
        print_mappings(result)

    if lineage:
        print_lineage(result)


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    default=Path("output"),
    help="Output directory for CSV files.",
)
def export(file: Path, output: Path) -> None:
    """Export analysis results to CSV files."""
    try:
        result = parse_xml(file)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    if not result.folders:
        console.print("[yellow]No Informatica metadata found.[/yellow]")
        return

    files = export_csv(result, output)
    console.print(f"\n[green]Exported {len(files)} CSV files to {output}/[/green]")
    for f in files:
        console.print(f"  - {f}")
    console.print()


def main() -> None:
    """Entry point."""
    cli()


if __name__ == "__main__":
    main()
