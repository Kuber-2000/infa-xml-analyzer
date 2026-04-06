# infa-xml-analyzer

A Python CLI tool that parses **Informatica PowerCenter XML exports** and extracts mappings, mapplets, folder relations, and data lineage.

## Problem

Informatica PowerCenter stores metadata in complex XML exports. Understanding what lives where -- which folders hold which mappings, what sources feed what targets, and how data flows through transformations -- typically means manually reading thousands of lines of XML or using expensive commercial tools.

**infa-xml-analyzer** gives you instant visibility into your Informatica metadata from the command line.

## Features

- Parse single XML files or scan entire directories
- Extract folders, mappings, mapplets, sources, targets, and transformations
- Count unique folder-to-mapping and folder-to-mapplet relationships
- Trace data lineage (source -> transformation path -> target)
- Rich terminal tables for quick analysis
- CSV export for further processing in Excel, pandas, or BI tools
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
python -m infa_xml_analyzer.cli analyze examples/sample_export.xml
```

With detailed mapping info and lineage:

```bash
python -m infa_xml_analyzer.cli analyze examples/sample_export.xml --detail --lineage
```

### Scan a directory

```bash
python -m infa_xml_analyzer.cli scan /path/to/xml/exports/
```

### Export to CSV

```bash
python -m infa_xml_analyzer.cli export examples/sample_export.xml -o ./output
```

This creates four CSV files in the output directory:
- `summary.csv` - Folder-level counts
- `mappings.csv` - All mappings with sources, targets, transformation counts
- `mapplets.csv` - All mapplets with transformation counts  
- `lineage.csv` - Full source-to-target lineage with transformation paths

If installed as a package, you can also use:

```bash
infa-xml-analyzer analyze examples/sample_export.xml
infa-xml-analyzer scan /path/to/exports/
infa-xml-analyzer export examples/sample_export.xml -o ./output
```

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

## Running Tests

```bash
pytest tests/ -v
```

## License

MIT
