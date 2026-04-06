"""CLI interface for infa-xml-analyzer."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console

from . import __version__
from .formatter import export_csv, export_json, print_lineage, print_mappings, print_summary
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
    help="Output directory for exported files.",
)
@click.option(
    "--format", "-f",
    "fmt",
    type=click.Choice(["csv", "json"], case_sensitive=False),
    default="csv",
    help="Export format: csv (multiple files) or json (single file).",
)
def export(file: Path, output: Path, fmt: str) -> None:
    """Export analysis results to CSV or JSON files."""
    try:
        result = parse_xml(file)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    if not result.folders:
        console.print("[yellow]No Informatica metadata found.[/yellow]")
        return

    if fmt == "json":
        json_file = export_json(result, output)
        console.print(f"\n[green]Exported JSON to {json_file}[/green]\n")
    else:
        files = export_csv(result, output)
        console.print(f"\n[green]Exported {len(files)} CSV files to {output}/[/green]")
        for f in files:
            console.print(f"  - {f}")
        console.print()


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
def validate(file: Path) -> None:
    """Validate an Informatica XML file without full analysis.

    Checks if the file is well-formed XML and contains expected
    Informatica PowerCenter elements (POWERMART, REPOSITORY, FOLDER).
    """
    from lxml import etree

    try:
        tree = etree.parse(str(file))
    except etree.XMLSyntaxError as e:
        console.print(f"[red]INVALID[/red] - XML syntax error: {e}")
        raise SystemExit(1)

    root = tree.getroot()
    tag = root.tag if root is not None else None

    if tag != "POWERMART":
        console.print(
            f"[yellow]WARNING[/yellow] - Root element is <{tag}>, "
            f"expected <POWERMART>. This may not be an Informatica export."
        )
        raise SystemExit(1)

    repo_count = len(root.findall(".//REPOSITORY"))
    folder_count = len(root.findall(".//FOLDER"))
    mapping_count = len(root.findall(".//MAPPING"))
    mapplet_count = len(root.findall(".//MAPPLET"))

    console.print(f"[green]VALID[/green] - {file.name}")
    console.print(f"  Repositories: {repo_count}")
    console.print(f"  Folders:      {folder_count}")
    console.print(f"  Mappings:     {mapping_count}")
    console.print(f"  Mapplets:     {mapplet_count}")


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
def stats(file: Path) -> None:
    """Show quick statistics for an Informatica XML file."""
    try:
        result = parse_xml(file)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    total_sources = sum(len(m.sources) for m in result.mappings)
    total_targets = sum(len(m.targets) for m in result.mappings)
    total_transforms = sum(len(m.transformations) for m in result.mappings)
    total_transforms += sum(len(m.transformations) for m in result.mapplets)

    console.print(f"\n[bold]Quick Stats: {file.name}[/bold]")
    console.print(f"  Folders:         {len(result.folders)}")
    console.print(f"  Mappings:        {len(result.mappings)}")
    console.print(f"  Mapplets:        {len(result.mapplets)}")
    console.print(f"  Sources:         {total_sources}")
    console.print(f"  Targets:         {total_targets}")
    console.print(f"  Transformations: {total_transforms}")
    console.print(f"  Lineage paths:   {len(result.lineage)}")
    console.print()


def main() -> None:
    """Entry point."""
    cli()


if __name__ == "__main__":
    main()
