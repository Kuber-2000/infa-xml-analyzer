# Contributing to infa-xml-analyzer

Thanks for your interest in contributing! This guide will help you get started.

## Development Setup

```bash
git clone https://github.com/Kuber-2000/infa-xml-analyzer.git
cd infa-xml-analyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pytest
```

## Running Tests

```bash
pytest tests/ -v
```

All tests must pass before submitting a pull request.

## Project Structure

```
src/infa_xml_analyzer/
  __init__.py       # Package version
  parser.py         # Core XML parsing logic
  formatter.py      # Terminal tables, CSV, and JSON output
  cli.py            # Click CLI commands
tests/
  test_parser.py    # Parser unit tests
  test_cli.py       # CLI integration tests
examples/
  sample_export.xml # Sample Informatica XML for testing
```

## How to Contribute

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run the tests: `pytest tests/ -v`
5. Commit with a clear message: `feat: add your feature description`
6. Push and open a pull request

## Commit Message Format

Use conventional commits:

- `feat:` new feature
- `fix:` bug fix
- `test:` adding or updating tests
- `docs:` documentation changes
- `refactor:` code refactoring

## What to Contribute

- Support for additional Informatica object types (sessions, workflows, tasks)
- New export formats
- Performance improvements for large XML files
- Better error messages
- Documentation improvements

## Code Style

- Use type hints
- Keep functions focused and small
- Follow existing patterns in the codebase
