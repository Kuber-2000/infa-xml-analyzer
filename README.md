# infa-xml-analyzer

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-23%20passed-brightgreen)

A Python CLI tool that parses **Informatica PowerCenter XML exports** and extracts mappings, mapplets, folder relations, and data lineage.

## Problem

Informatica PowerCenter stores metadata in complex XML exports. Understanding what lives where -- which folders hold which mappings, what sources feed what targets, and how data flows through transformations -- typically means manually reading thousands of lines of XML or using expensive commercial tools.

**infa-xml-analyzer** gives you instant visibility into your Informatica metadata from the command line.

## Features

- Parse single XML files or scan entire directories
- Extract folders, mappings, mapplets, sources, targets, and transformations
- Count unique folder-to-mapping and folder-to-mapplet relationships
- Trace data lineage (source -> transformation path -> target)
- Validate XML structure before analysis
- Quick stats for scripting and CI pipelines
- Rich terminal tables for quick analysis
- Export to CSV (multiple files) or JSON (single structured file)
- Handles malformed XML gracefully with warnings

## Installation

```bash
git clone https://github.com/Kuber-2000/infa-xml-analyzer.git
cd infa-xml-analyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Or install as a package:

```bash
pip install -e .
```

## Usage

### Analyze a single file

```bash
infa-xml-analyzer analyze examples/sample_export.xml
```

With detailed mapping info and lineage:

```bash
infa-xml-analyzer analyze examples/sample_export.xml --detail --lineage
```

### Scan a directory

```bash
infa-xml-analyzer scan /path/to/xml/exports/
```

### Validate an XML file

Check if a file is well-formed XML with valid Informatica structure:

```bash
infa-xml-analyzer validate examples/sample_export.xml
```

Output:
```
VALID - sample_export.xml
  Repositories: 1
  Folders:      3
  Mappings:     4
  Mapplets:     3
```

### Quick stats

Get numeric counts without full table rendering:

```bash
infa-xml-analyzer stats examples/sample_export.xml
```

Output:
```
Quick Stats: sample_export.xml
  Folders:         3
  Mappings:        4
  Mapplets:        3
  Sources:         4
  Targets:         5
  Transformations: 25
  Lineage paths:   5
```

### Export to CSV

```bash
infa-xml-analyzer export examples/sample_export.xml -o ./output
```

This creates four CSV files in the output directory:
- `summary.csv` - Folder-level counts
- `mappings.csv` - All mappings with sources, targets, transformation counts
- `mapplets.csv` - All mapplets with transformation counts
- `lineage.csv` - Full source-to-target lineage with transformation paths

### Export to JSON

```bash
infa-xml-analyzer export examples/sample_export.xml -o ./output -f json
```

Creates a single `analysis.json` with all data in a structured format.

## Example Output

```
  Informatica XML Analysis Summary
┏━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┓
┃ Folder      ┃ Mappings ┃ Mapplets ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━┩
│ ETL_Finance │        2 │        1 │
│ ETL_HR      │        1 │        0 │
│ ETL_Sales   │        1 │        2 │
├─────────────┼──────────┼──────────┤
│ TOTAL       │        4 │        3 │
└─────────────┴──────────┴──────────┘
```

## All Commands

| Command    | Description                                      |
|------------|--------------------------------------------------|
| `analyze`  | Parse and display tables for a single XML file   |
| `scan`     | Scan a directory for XML files and analyze all    |
| `export`   | Export results to CSV or JSON                     |
| `validate` | Check XML syntax and Informatica structure        |
| `stats`    | Show quick numeric summary                        |

## Running Tests

```bash
pytest tests/ -v
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT
