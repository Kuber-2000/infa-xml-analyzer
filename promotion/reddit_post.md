# Reddit Post (r/dataengineering)

---

**Title:** I built a Python CLI tool to parse Informatica PowerCenter XML exports and extract lineage

**Body:**

Hey r/dataengineering,

I've been working with Informatica PowerCenter and got tired of manually reading through XML exports to understand what's in each folder, which mappings exist, and how data flows from source to target.

So I built **infa-xml-analyzer** -- a simple Python CLI that:

- Parses Informatica PowerCenter XML export files
- Extracts all folders, mappings, mapplets, sources, targets, and transformations
- Shows folder-to-mapping and folder-to-mapplet counts
- Traces full data lineage paths (source -> transformation chain -> target)
- Outputs clean terminal tables (via Rich) or exports to CSV
- Can scan entire directories of XML files

**Quick usage:**

```bash
# Analyze a single file
infa-xml-analyzer analyze export.xml --detail --lineage

# Scan a directory
infa-xml-analyzer scan /path/to/exports/

# Export to CSV
infa-xml-analyzer export export.xml -o ./output
```

Stack: Python 3.10+, lxml, pandas, Click, Rich

It's open source (MIT): https://github.com/Kuber-2000/infa-xml-analyzer

Useful for ETL documentation, migration planning, or impact analysis. Would appreciate any feedback or feature requests.

---
