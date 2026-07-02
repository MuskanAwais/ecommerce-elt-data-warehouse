# Spec-Driven Design Document (SDD)
## E-Commerce ELT Data Warehouse

**Stack:** Python, dbt, S3, DuckDB/Redshift, PostgreSQL
**Document Type:** Spec-Driven Design (SDD)
**Version:** 1.0

---

## How to Read This Document

This project is broken into **modules**. Each module is a self-contained unit of work with a clear goal, the exact files it produces, how to run it, how to test it, and a **Definition of Done**. When a module is finished, it becomes one Git commit — so the commit history itself acts as a visual progress tracker of the whole project.

Every module follows the same table structure, so an evaluator (or you, six months from now) can scan any module and immediately understand: what it does, why it exists, how to verify it works, and when it's considered complete.

---

## Module 0 — Planning & Concepts

| Item | Detail |
|---|---|
| **Concept** | Establish shared terminology, coding standards, and this SDD itself. |
| **Goal** | Align scope before writing code, avoid over-engineering, and document key decisions up front. |
| **Files Created** | `docs/SDD.md` (this file), `docs/coding_standards.md` |
| **Code** | None — documentation only. |
| **Run** | N/A |
| **Test** | Review the document for completeness and correctness. |
| **Common Errors** | Missing sections, broken internal links. |
| **Interview Question** | Why is a spec-driven approach valuable for data pipelines? |
| **Definition of Done** | Document written, reviewed, and merged to `main`. |

**✅ Milestone 0 Commit**
```
git commit -m "docs: add spec-driven design document"
```

---

## Module 1 — Project Setup

| Item | Detail |
|---|---|
| **Concept** | Scaffold the repository with required folders and base configuration. |
| **Goal** | Give the project a clean, reproducible environment from day one. |
| **Files Created** | `.gitignore`, `requirements.txt`, `README.md`, `docs/`, `config/`, empty `data/` folder structure |
| **Code** | File/folder creation only — no logic yet. |
| **Run** | `git init`, create virtual environment, `pip install -r requirements.txt` |
| **Test** | Install succeeds with no errors; `git status` shows a clean working tree. |
| **Common Errors** | Missing `.gitignore` entries causing large data/log files to get tracked by Git. |
| **Interview Question** | What should be excluded in `.gitignore` for a data warehouse project? |
| **Definition of Done** | Repo scaffolded and pushed. |

**✅ Milestone 1 Commit**
```
git commit -m "chore: scaffold project layout & basic config"
```

---

## Module 2 — Data Extraction

| Item | Detail |
|---|---|
| **Concept** | Pull raw JSON data from the DummyJSON API and save it locally. |
| **Goal** | Populate the `s3://<bucket-name>/raw/` layer with timestamped files for downstream processing. |
| **Files Created** | `extraction/config.py` (API base URL, endpoints & AWS config), `extraction/extractor.py` (client logic & S3 upload), `logs/extraction.log` |
| **Code** | A Python script loops over each endpoint, sends a GET request via `requests`, and uploads the JSON response to `s3://<bucket-name>/raw/<entity>/YYYY/MM/DD/<entity>_<timestamp>.json` using `boto3`. Success/failure is logged in JSON-line format. |
| **Run** | `python extraction/extractor.py` from the repo root. |
| **Test** | After running: check S3 bucket to verify each entity folder contains at least one `.json` file; log file shows successful entries for all calls. |
| **Common Errors** | Network issues, AWS IAM permission errors for S3 upload, empty responses due to rate limits. |
| **Interview Question** | How would you make extraction idempotent if the API had no timestamps? |
| **Definition of Done** | Script runs without errors, S3 files are named/structured correctly, logs are produced. |

**✅ Milestone 2 Commit**
```
git commit -m "feat(extraction): add API client, config, structured logging, and S3 upload"
```

---

## Module 3 — Raw Data Storage

| Item | Detail |
|---|---|
| **Concept** | Organize raw files in the S3 bucket using a date-partitioned prefix hierarchy. |
| **Goal** | Make it easy to reprocess data from a specific date and support future S3 lifecycle policies for data retention. |
| **Files Created** | Update to `extraction/extractor.py`; optional `scripts/cleanup_raw.py` |
| **Code** | S3 object key is built using `raw/<entity>/<YYYY>/<MM>/<DD>/`. Boto3 uploads the JSON content directly to this partitioned key. |
| **Run** | Same as Module 2 — the extractor now writes into the S3 partitioned layout. |
| **Test** | Confirm files land in the correct date paths in S3; run the cleanup script and confirm old objects are deleted. |
| **Common Errors** | Incorrect S3 path construction; missing AWS credentials. |
| **Interview Question** | Why is date-partitioning useful for cloud object storage like S3? |
| **Definition of Done** | Files are correctly partitioned in S3, cleanup script works, docs updated. |

**✅ Milestone 3 Commit**
```
git commit -m "refactor(extraction): store raw files in date-partitioned S3 paths"
```

---

## Module 4 — Data Loading (DuckDB / Redshift)

| Item | Detail |
|---|---|
| **Concept** | Load raw JSON files from S3 into DuckDB (local dev) or Redshift (production) staging tables automatically via dbt. |
| **Goal** | Provide a queryable layer for dbt models directly from the S3 data lake, without needing a separate manual ETL step. |
| **Files Created** | `profiles.yml` (dbt connection for DuckDB/Redshift), optional debugging helper `transformations/load_raw.py` |
| **Code** | For DuckDB: run `CREATE OR REPLACE TABLE stg_<entity> AS SELECT * FROM read_json_auto('s3://<bucket-name>/raw/<entity>/**/*.json')` (using the `httpfs` extension). For Redshift: `COPY stg_<entity> FROM 's3://<bucket-name>/raw/<entity>/' IAM_ROLE '...' FORMAT AS JSON 'auto'`. |
| **Run** | Triggered automatically via dbt models in `models/staging/` when `dbt run` executes. |
| **Test** | After `dbt run`, query `SELECT COUNT(*) FROM stg_products;` — should return a count greater than 0. |
| **Common Errors** | AWS IAM/credential issues in DuckDB `httpfs` or Redshift, schema mismatches, missing S3 files. |
| **Interview Question** | How do external tables or `read_json_auto` over S3 differ from standard database tables? |
| **Definition of Done** | Staging tables exist with correct row counts, AWS connection works, no errors in dbt run logs. |

**✅ Milestone 4 Commit**
```
git commit -m "feat(warehouse): add staging load logic from S3 via dbt (DuckDB/Redshift)"
```

---

## Module 5 — Data Modeling

| Item | Detail |
|---|---|
| **Concept** | Design a star schema (dimensions + fact table) for e-commerce analytics. |
| **Goal** | Support business-level metrics like revenue, repeat purchases, and churn. |
| **Files Created** | `models/staging/stg_*.sql`, `models/dim/dim_*.sql`, `models/fact/fact_*.sql`, `models/analytics/*.sql` |
| **Code** | Each model is a single `SELECT` built from CTEs. Dimension models generate surrogate keys; the fact model joins to dimensions using those keys. |
| **Run** | `dbt run --models dim+ fact+` |
| **Test** | dbt tests for primary key uniqueness, foreign key relationships, and non-null constraints. |
| **Common Errors** | Duplicate keys, mismatched data types, circular joins. |
| **Interview Question** | What is the purpose of a surrogate key in a dimension table? |
| **Definition of Done** | All models compile, tests pass, `dbt docs generate` runs cleanly. |

**✅ Milestone 5 Commit**
```
git commit -m "feat(models): create star-schema staging, dimension, and fact models"
```

---

## Module 6 — dbt Transformations (Business Metrics)

| Item | Detail |
|---|---|
| **Concept** | Implement business metrics using dbt CTEs, Jinja macros, and tests. |
| **Goal** | Provide reusable, versioned SQL logic for revenue, MTD revenue, churn, and cohort analysis. |
| **Files Created** | `macros/generate_surrogate_key.sql`, `models/analytics/mtd_revenue.sql`, `models/analytics/customer_churn.sql`, `tests/schema.yml` |
| **Code** | Macros generate deterministic hash-based surrogate keys. Analytic models build on the fact table using window functions and date truncation. |
| **Run** | `dbt run --models analytics+` |
| **Test** | `dbt test` — all generic and custom tests must pass. |
| **Common Errors** | Macro naming collisions, Jinja syntax errors, test failures from data quality issues. |
| **Interview Question** | How do Jinja macros improve maintainability of dbt models? |
| **Definition of Done** | Analytics tables created, all tests pass, docs updated via `dbt docs serve`. |

**✅ Milestone 6 Commit**
```
git commit -m "feat(analytics): add revenue & churn models with tests"
```

---

## Module 7 — Business Analytics (Reporting & Serving Layer)

| Item | Detail |
|---|---|
| **Concept** | Provide end-user queries for key KPIs and optionally serve final aggregates to PostgreSQL. |
| **Goal** | Let analysts answer revenue, churn, and cohort questions. PostgreSQL is used as a serving layer (Data Mart) to connect standard BI tools (Tableau, Metabase). |
| **Files Created** | `sql/reports/revenue_report.sql`, `sql/reports/churn_report.sql`, optional script to sync to PostgreSQL (`scripts/sync_to_postgres.py`) |
| **Code** | Simple `SELECT` queries referencing the analytics models in DuckDB/Redshift. The sync script connects to DuckDB/Redshift, reads the aggregate tables, and writes them to a PostgreSQL database. |
| **Run** | Execute SQL via CLI, or run the sync script to push data to PostgreSQL. |
| **Test** | Confirm query results match expected aggregates. If syncing to Postgres, verify tables are populated in the Postgres database. |
| **Common Errors** | Off-by-one date boundaries, missing joins, PostgreSQL connection failures. |
| **Interview Question** | What's the difference between MTD revenue and cumulative revenue? |
| **Definition of Done** | Reports return correct numbers, PostgreSQL sync works successfully. |

**✅ Milestone 7 Commit**
```
git commit -m "feat(analytics): add sample reporting queries and Postgres serving sync"
```

---

## Module 8 — Project Documentation

| Item | Detail |
|---|---|
| **Concept** | Keep all design decisions, architecture, and usage instructions up to date. |
| **Goal** | Provide a single source of truth for new contributors and future maintainers. |
| **Files Created** | `README.md`, `docs/architecture.md`, `docs/coding_standards.md`, `docs/CHANGELOG.md` |
| **Code** | None — markdown only. |
| **Run** | N/A |
| **Test** | Markdown renders correctly on GitHub; all internal links resolve. |
| **Common Errors** | Broken image links, outdated diagrams. |
| **Interview Question** | Why is continuous documentation important for data pipelines? |
| **Definition of Done** | All docs reviewed, merged, and linked from the main README. |

**✅ Milestone 8 Commit**
```
git commit -m "docs: update project documentation and architecture diagram"
```

---

## Module 9 — GitHub Finalization

| Item | Detail |
|---|---|
| **Concept** | Prepare the repo for public consumption and future contributions. |
| **Goal** | Provide clear contribution guidelines, issue templates, and a release process. |
| **Files Created** | `.github/ISSUE_TEMPLATE/bug_report.md`, `.github/pull_request_template.md`, `CONTRIBUTING.md`, optional lint workflow |
| **Code** | Minimal YAML for linting (optional, no CI required). |
| **Run** | N/A |
| **Test** | Open a draft PR to confirm templates render correctly. |
| **Common Errors** | Mis-named template directories, YAML syntax errors. |
| **Interview Question** | What belongs in a good CONTRIBUTING guide? |
| **Definition of Done** | Templates live under `.github/`, CONTRIBUTING guide merged, repo tagged `v1.0.0`. |

**✅ Milestone 9 Commit**
```
git commit -m "docs(github): add issue & PR templates, CONTRIBUTING guide"
```

---

## Coding Standards & Conventions

- **Style** — PEP 8 for Python; dbt model files use lowercase `snake_case`.
- **Naming** — Files: `snake_case.py`; database objects: `snake_case`; Jinja macros: `snake_case`.
- **Docstrings** — Triple-quoted, include purpose, args, and returns.
- **Commit Messages** — Follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`.

---

## Git Workflow

1. Create a feature branch: `git checkout -b <feature>/<ticket-id>`
2. Write code or documentation for the module.
3. Run the module's tests locally.
4. Commit using the Conventional Commits format shown in that module's section.
5. Push the branch and open a Pull Request into `main`.
6. PR requires at least one approving review (and CI lint pass, if configured).
7. Merge using `--no-ff` to preserve history.

---

## Milestone Summary (Quick Reference)

| Milestone | Module | Commit Message |
|---|---|---|
| M0 | Planning & Concepts | `docs: add spec-driven design document` |
| M1 | Project Setup | `chore: scaffold project layout & basic config` |
| M2 | Data Extraction | `feat(extraction): add API client, config, structured logging, and S3 upload` |
| M3 | Raw Data Storage | `refactor(extraction): store raw files in date-partitioned S3 paths` |
| M4 | Data Loading | `feat(warehouse): add staging load logic from S3 via dbt (DuckDB/Redshift)` |
| M5 | Data Modeling | `feat(models): create star-schema staging, dimension, and fact models` |
| M6 | dbt Transformations | `feat(analytics): add revenue & churn models with tests` |
| M7 | Business Analytics | `feat(analytics): add sample reporting queries and Postgres serving sync` |
| M8 | Project Documentation | `docs: update project documentation and architecture diagram` |
| M9 | GitHub Finalization | `docs(github): add issue & PR templates, CONTRIBUTING guide` |

When every row in this table has a matching commit on GitHub, the project is complete and ready for evaluation.
