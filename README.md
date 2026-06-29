# ecommerce-elt-data-warehouse

> **A modern, Python‑based ETL data‑warehouse for ecommerce analytics**

## Overview

This repository contains a lightweight, extensible data‑pipeline that extracts raw ecommerce data, transforms it, and loads it into a DuckDB‑backed data‑warehouse.  The pipeline is orchestrated with **dbt‑duckdb**, making it easy to version‑control transformations and generate analytical models.

## Directory Structure

```
ecommerce-elt-data-warehouse/
│
├─ data/
│   ├─ raw/           # Original extracts (CSV, JSON, etc.)
│   ├─ processed/     # Cleaned/intermediate files
│   └─ warehouse/     # Final parquet / DuckDB files
│
├─ extraction/        # Scripts that pull data from source APIs
├─ transformations/   # dbt models & SQL scripts
├─ sql/               # Ad‑hoc queries & helper SQL files
├─ tests/             # Pytest suite for the pipeline
├─ docs/              # Project documentation & design notes
├─ config/            # Configuration files (e.g., .env.example)
├─ logs/              # Runtime logs
└─ notebooks/         # Exploration notebooks
```

## Quick Start

1. **Clone the repo**
   ```bash
   git clone <repo‑url>
   cd ecommerce-elt-data-warehouse
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate   # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp config/.env.example .env
   # Edit .env with your API keys / DB paths
   ```

5. **Run the pipeline**
   ```bash
   # Example: extract raw data
   python extraction/run_extraction.py

   # Transform with dbt
   dbt run --profiles-dir config
   ```

6. **Explore the warehouse**
   ```bash
   duckdb data/warehouse/warehouse.duckdb
   ```

## Testing

Run the test suite to ensure the pipeline behaves as expected:
```bash
pytest tests/
```

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a feature branch (`git checkout -b my-feature`).
3. Commit your changes with clear messages.
4. Open a Pull Request targeting `main`.

## License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---
