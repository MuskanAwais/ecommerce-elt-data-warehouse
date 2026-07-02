# Contributing Guide

Thank you for contributing to the E-Commerce ELT Data Warehouse project.

## Getting Started

1. Fork the repository and clone your fork.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   pip install -r requirements.txt
   ```
3. Copy environment variables if needed (AWS credentials for S3 upload):
   ```bash
   cp .env.example .env          # if provided
   ```

## Project Layout

| Folder | Purpose |
|---|---|
| `src/` | All Python source, dbt project, and SQL reports |
| `Data/` | Raw JSON and DuckDB warehouse (not committed) |
| `results/` | Pipeline logs and dbt artifacts (not committed) |
| `tests/` | Pytest unit tests |
| `.planning/` | SDD, specs, master plan, and revision guide |
| `config/` | dbt profiles |

## Development Workflow

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feat/my-feature
   ```
2. Make your changes in the appropriate folder under `src/`.
3. Run tests before committing:
   ```bash
   pytest
   .\src\run_dbt.ps1 test
   ```
4. Commit using [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   feat(extraction): add retry logic for API timeouts
   fix(analytics): correct order_date in fact_orders
   docs: update architecture diagram
   chore: update dependencies
   ```
5. Push and open a Pull Request against `main`.

## Coding Standards

- **Python**: Follow PEP 8; use type hints where helpful; add docstrings for public functions.
- **dbt models**: Lowercase `snake_case` filenames; one model per file; use `ref()` and `source()`.
- **Paths**: Import from `src/paths.py` — do not hard-code legacy `data/` or root-level module paths.
- **Tests**: Add pytest tests for new Python logic; add dbt tests in `schema.yml` for new models.

## Pull Request Checklist

- [ ] Code follows project conventions
- [ ] `pytest` passes
- [ ] `.\src\run_dbt.ps1 test` passes (if dbt models changed)
- [ ] Documentation updated if paths or behavior changed
- [ ] No secrets or large data files committed

## Reporting Issues

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) when filing issues. Include steps to reproduce, expected vs. actual behavior, and relevant log output from `results/logs/`.
