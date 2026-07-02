# ecommerce-elt-data-warehouse

Python ELT pipeline for ecommerce analytics: API extraction, DuckDB warehouse, and dbt transformations.

## Project layout

```
ecommerce-elt-data-warehouse/
├── src/              # Application source code (Python, dbt, SQL)
├── Data/             # Raw, processed, and warehouse data files
├── results/          # Pipeline outputs (dbt artifacts, logs)
├── tests/            # Pytest suite
├── Documents/        # Project documentation (.md, specs, guides)
├── config/           # dbt profiles and environment config
├── requirements.txt
└── pytest.ini
```

Full setup instructions and architecture notes are in [Documents/README.md](Documents/README.md) and [Documents/architecture.md](Documents/architecture.md).

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow and coding standards.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run the complete ELT pipeline (one command)
python orchestration_pipeline.py

# Extract raw data (manual)
cd src && python -m extraction.extractor
cd src && python -m scripts.load_raw

# Run dbt models (works from repo root — cwd is restored after each run)
.\run_dbt.ps1 run

# Run tests
.\run_dbt.ps1 test
pytest
```

## License

MIT License — see [Documents/README.md](Documents/README.md) for details.
