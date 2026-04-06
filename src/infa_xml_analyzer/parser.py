"""Core parser for Informatica PowerCenter XML export files."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from lxml import etree


@dataclass
class Mapping:
    """Represents an Informatica mapping."""

    name: str
    folder: str
    description: str = ""
    sources: list[str] = field(default_factory=list)
    targets: list[str] = field(default_factory=list)
    transformations: list[str] = field(default_factory=list)


@dataclass
class Mapplet:
    """Represents an Informatica mapplet."""

    name: str
    folder: str
    description: str = ""
    transformations: list[str] = field(default_factory=list)


@dataclass
class Folder:
    """Represents an Informatica folder."""

    name: str
    mappings: list[str] = field(default_factory=list)
    mapplets: list[str] = field(default_factory=list)


@dataclass
class LineageEntry:
    """Represents a source-to-target lineage path."""

    folder: str
    mapping: str
    source: str
    target: str
    transformation_path: list[str] = field(default_factory=list)


@dataclass
class ParseResult:
    """Aggregated result from parsing one or more XML files."""

    folders: list[Folder] = field(default_factory=list)
    mappings: list[Mapping] = field(default_factory=list)
    mapplets: list[Mapplet] = field(default_factory=list)
    lineage: list[LineageEntry] = field(default_factory=list)

    @property
    def folder_to_mapping_count(self) -> dict[str, int]:
        """Count unique mappings per folder."""
        counts: dict[str, int] = {}
        for m in self.mappings:
            counts[m.folder] = counts.get(m.folder, 0) + 1
        return counts

    @property
    def folder_to_mapplet_count(self) -> dict[str, int]:
        """Count unique mapplets per folder."""
        counts: dict[str, int] = {}
        for m in self.mapplets:
            counts[m.folder] = counts.get(m.folder, 0) + 1
        return counts

    def merge(self, other: ParseResult) -> None:
        """Merge another ParseResult into this one."""
        self.folders.extend(other.folders)
        self.mappings.extend(other.mappings)
        self.mapplets.extend(other.mapplets)
        self.lineage.extend(other.lineage)


def _get_attr(element: etree._Element, attr: str, default: str = "") -> str:
    """Safely get an XML attribute value."""
    return element.get(attr, default) or default


def parse_xml(filepath: str | Path) -> ParseResult:
    """Parse a single Informatica PowerCenter XML export file.

    Args:
        filepath: Path to the XML file.

    Returns:
        ParseResult with extracted folders, mappings, mapplets, and lineage.

    Raises:
        FileNotFoundError: If the file does not exist.
        etree.XMLSyntaxError: If the XML is malformed.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    tree = etree.parse(str(path))
    root = tree.getroot()

    result = ParseResult()

    # Process each FOLDER element
    for folder_elem in root.iter("FOLDER"):
        folder_name = _get_attr(folder_elem, "NAME")
        if not folder_name:
            continue

        folder = Folder(name=folder_name)

        # Extract MAPPINGS
        for mapping_elem in folder_elem.findall("MAPPING"):
            mapping_name = _get_attr(mapping_elem, "NAME")
            if not mapping_name:
                continue

            mapping = Mapping(
                name=mapping_name,
                folder=folder_name,
                description=_get_attr(mapping_elem, "DESCRIPTION"),
            )

            # Sources
            for src in mapping_elem.findall("SOURCE"):
                src_name = _get_attr(src, "NAME")
                if src_name:
                    mapping.sources.append(src_name)

            # Targets
            for tgt in mapping_elem.findall("TARGET"):
                tgt_name = _get_attr(tgt, "NAME")
                if tgt_name:
                    mapping.targets.append(tgt_name)

            # Transformations
            for tx in mapping_elem.findall("TRANSFORMATION"):
                tx_name = _get_attr(tx, "NAME")
                if tx_name:
                    mapping.transformations.append(tx_name)

            folder.mappings.append(mapping_name)
            result.mappings.append(mapping)

            # Build lineage entries (source -> target through transformations)
            for src_name in mapping.sources:
                for tgt_name in mapping.targets:
                    result.lineage.append(
                        LineageEntry(
                            folder=folder_name,
                            mapping=mapping_name,
                            source=src_name,
                            target=tgt_name,
                            transformation_path=list(mapping.transformations),
                        )
                    )

        # Extract MAPPLETS
        for mapplet_elem in folder_elem.findall("MAPPLET"):
            mapplet_name = _get_attr(mapplet_elem, "NAME")
            if not mapplet_name:
                continue

            mapplet = Mapplet(
                name=mapplet_name,
                folder=folder_name,
                description=_get_attr(mapplet_elem, "DESCRIPTION"),
            )

            for tx in mapplet_elem.findall("TRANSFORMATION"):
                tx_name = _get_attr(tx, "NAME")
                if tx_name:
                    mapplet.transformations.append(tx_name)

            folder.mapplets.append(mapplet_name)
            result.mapplets.append(mapplet)

        result.folders.append(folder)

    return result


def scan_directory(directory: str | Path, recursive: bool = True) -> ParseResult:
    """Scan a directory for Informatica XML files and parse them all.

    Args:
        directory: Path to the directory to scan.
        recursive: Whether to scan subdirectories.

    Returns:
        Merged ParseResult from all XML files found.

    Raises:
        FileNotFoundError: If the directory does not exist.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {dir_path}")

    pattern = "**/*.xml" if recursive else "*.xml"
    xml_files = sorted(dir_path.glob(pattern))

    if not xml_files:
        raise FileNotFoundError(f"No XML files found in: {dir_path}")

    combined = ParseResult()
    errors: list[str] = []

    for xml_file in xml_files:
        try:
            result = parse_xml(xml_file)
            combined.merge(result)
        except etree.XMLSyntaxError:
            errors.append(f"Skipping malformed XML: {xml_file}")
        except Exception as e:
            errors.append(f"Error parsing {xml_file}: {e}")

    if errors:
        for err in errors:
            print(f"  WARNING: {err}")

    return combined
