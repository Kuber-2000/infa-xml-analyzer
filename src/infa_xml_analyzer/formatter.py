"""Output formatters for terminal tables, CSV, and JSON export."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.table import Table

from .parser import ParseResult


console = Console()


def _mappings_to_df(result: ParseResult) -> pd.DataFrame:
    """Convert mappings to a DataFrame."""
    rows = []
    for m in result.mappings:
        rows.append({
            "Folder": m.folder,
            "Mapping": m.name,
            "Description": m.description,
            "Sources": ", ".join(m.sources),
            "Targets": ", ".join(m.targets),
            "Transformations": len(m.transformations),
        })
    return pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["Folder", "Mapping", "Description", "Sources", "Targets", "Transformations"]
    )


def _mapplets_to_df(result: ParseResult) -> pd.DataFrame:
    """Convert mapplets to a DataFrame."""
    rows = []
    for m in result.mapplets:
        rows.append({
            "Folder": m.folder,
            "Mapplet": m.name,
            "Description": m.description,
            "Transformations": len(m.transformations),
        })
    return pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["Folder", "Mapplet", "Description", "Transformations"]
    )


def _lineage_to_df(result: ParseResult) -> pd.DataFrame:
    """Convert lineage entries to a DataFrame."""
    rows = []
    for entry in result.lineage:
        rows.append({
            "Folder": entry.folder,
            "Mapping": entry.mapping,
            "Source": entry.source,
            "Target": entry.target,
            "Transformation Path": " -> ".join(entry.transformation_path),
        })
    return pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["Folder", "Mapping", "Source", "Target", "Transformation Path"]
    )


def _summary_to_df(result: ParseResult) -> pd.DataFrame:
    """Build a folder summary DataFrame."""
    folder_map = result.folder_to_mapping_count
    folder_mlt = result.folder_to_mapplet_count
    all_folders = sorted(set(list(folder_map.keys()) + list(folder_mlt.keys())))
    rows = []
    for f in all_folders:
        rows.append({
            "Folder": f,
            "Mappings": folder_map.get(f, 0),
            "Mapplets": folder_mlt.get(f, 0),
        })
    return pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["Folder", "Mappings", "Mapplets"]
    )


def print_summary(result: ParseResult) -> None:
    """Print a summary table to the terminal."""
    table = Table(title="Informatica XML Analysis Summary")
    table.add_column("Folder", style="cyan", no_wrap=True)
    table.add_column("Mappings", style="green", justify="right")
    table.add_column("Mapplets", style="yellow", justify="right")

    folder_map = result.folder_to_mapping_count
    folder_mlt = result.folder_to_mapplet_count
    all_folders = sorted(set(list(folder_map.keys()) + list(folder_mlt.keys())))

    for f in all_folders:
        table.add_row(f, str(folder_map.get(f, 0)), str(folder_mlt.get(f, 0)))

    table.add_section()
    table.add_row(
        "TOTAL",
        str(len(result.mappings)),
        str(len(result.mapplets)),
        style="bold",
    )

    console.print()
    console.print(table)
    console.print()


def print_mappings(result: ParseResult) -> None:
    """Print mappings detail table."""
    table = Table(title="Mappings")
    table.add_column("Folder", style="cyan")
    table.add_column("Mapping", style="green")
    table.add_column("Sources", style="blue")
    table.add_column("Targets", style="magenta")
    table.add_column("Transformations", justify="right")

    for m in result.mappings:
        table.add_row(
            m.folder,
            m.name,
            ", ".join(m.sources),
            ", ".join(m.targets),
            str(len(m.transformations)),
        )

    console.print()
    console.print(table)
    console.print()


def print_lineage(result: ParseResult) -> None:
    """Print lineage table."""
    table = Table(title="Data Lineage")
    table.add_column("Folder", style="cyan")
    table.add_column("Mapping", style="green")
    table.add_column("Source", style="blue")
    table.add_column("Target", style="magenta")
    table.add_column("Path", style="dim")

    for entry in result.lineage:
        table.add_row(
            entry.folder,
            entry.mapping,
            entry.source,
            entry.target,
            " -> ".join(entry.transformation_path) if entry.transformation_path else "-",
        )

    console.print()
    console.print(table)
    console.print()


def export_csv(result: ParseResult, output_dir: str | Path) -> list[str]:
    """Export all data to CSV files.

    Returns list of created file paths.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    files_created = []

    summary_path = out / "summary.csv"
    _summary_to_df(result).to_csv(summary_path, index=False)
    files_created.append(str(summary_path))

    mappings_path = out / "mappings.csv"
    _mappings_to_df(result).to_csv(mappings_path, index=False)
    files_created.append(str(mappings_path))

    mapplets_path = out / "mapplets.csv"
    _mapplets_to_df(result).to_csv(mapplets_path, index=False)
    files_created.append(str(mapplets_path))

    lineage_path = out / "lineage.csv"
    _lineage_to_df(result).to_csv(lineage_path, index=False)
    files_created.append(str(lineage_path))

    return files_created


def _result_to_dict(result: ParseResult) -> dict:
    """Convert ParseResult to a JSON-serializable dictionary."""
    return {
        "summary": {
            "total_folders": len(result.folders),
            "total_mappings": len(result.mappings),
            "total_mapplets": len(result.mapplets),
            "total_lineage_paths": len(result.lineage),
            "folder_counts": [
                {
                    "folder": f.name,
                    "mappings": len(f.mappings),
                    "mapplets": len(f.mapplets),
                }
                for f in result.folders
            ],
        },
        "mappings": [
            {
                "folder": m.folder,
                "name": m.name,
                "description": m.description,
                "sources": m.sources,
                "targets": m.targets,
                "transformations": m.transformations,
            }
            for m in result.mappings
        ],
        "mapplets": [
            {
                "folder": m.folder,
                "name": m.name,
                "description": m.description,
                "transformations": m.transformations,
            }
            for m in result.mapplets
        ],
        "lineage": [
            {
                "folder": e.folder,
                "mapping": e.mapping,
                "source": e.source,
                "target": e.target,
                "transformation_path": e.transformation_path,
            }
            for e in result.lineage
        ],
    }


def export_json(result: ParseResult, output_dir: str | Path) -> str:
    """Export all data to a single JSON file.

    Returns the path of the created file.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    json_path = out / "analysis.json"
    data = _result_to_dict(result)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return str(json_path)
