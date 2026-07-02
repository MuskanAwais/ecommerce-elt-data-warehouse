# E-Commerce ELT Data Warehouse

End-to-end **ELT pipeline** for e-commerce analytics: extract from DummyJSON, store in AWS S3, load into DuckDB, transform with dbt, and generate business KPIs.

## Tech Stack

Python · DuckDB · dbt · AWS S3 · DummyJSON API

## Project Structure

```
├── src/                      # Source code (extraction, dbt, scripts)
├── Data/                     # Raw JSON + DuckDB warehouse (local, gitignored)
├── results/                  # Pipeline logs and dbt artifacts (gitignored)
├── tests/                    # pytest suite
├── .planning/                # SDD, specs, master plan, revision guide
├── orchestration_pipeline.py # Run the full pipeline with one command
├── config/profiles.yml       # dbt DuckDB connection
└── run_dbt.ps1               # dbt helper script
```

## Quick Start

```powershell
git clone https://github.com/MuskanAwais/ecommerce-elt-data-warehouse.git
cd ecommerce-elt-data-warehouse

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file at the repo root with your AWS credentials (see [.planning/revision.md](.planning/revision.md#environment-variables)).

### Run the full pipeline

```powershell
python orchestration_pipeline.py
```

This executes: **API extract → S3 upload → DuckDB load → dbt transform → dbt test → analytics report**.

### Run tests

```powershell
pytest
.\run_dbt.ps1 test
```

## Documentation

| Document | Description |
|---|---|
| [.planning/revision.md](.planning/revision.md) | Full guide: concepts, architecture, workflow, testing, expected output |
| [.planning/master_plan.md](.planning/master_plan.md) | Module roadmap and completion tracker |
| [.planning/SDD.md](.planning/SDD.md) | Spec-driven design document (modules 0–9) |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Development workflow and coding standards |

## License

MIT License
