# 📄 Spec‑Driven Design Document (SDD)

---

## 1. Project Overview
A lightweight, production‑style ELT pipeline that extracts **product**, **user**, and **cart** data from the **DummyJSON** REST API, lands the raw JSON in a local S3‑style bucket, transforms it with **dbt Core** (using CTEs, Jinja templating, and tests), and loads the curated tables into **DuckDB** (or Redshift). The stack is limited to free, open‑source tools and is beginner‑friendly.

---

## 2. Business Problem
E‑commerce analysts need timely, reliable metrics (revenue, churn, cohort analysis). Manual CSV dumps are error‑prone, not versioned, and do not scale. A reproducible ELT pipeline solves these pain points.

---

## 3. Objectives
| # | Objective |
|---|-----------|
| 1 | Pull raw data (products, users, carts) via a Python client. |
| 2 | Store raw JSON in `data/raw/` with date‑partitioned folders. |
| 3 | Load raw JSON into DuckDB staging tables. |
| 4 | Model dimensional tables and business metrics with dbt. |
| 5 | Provide automated data‑quality tests. |
| 6 | Keep the stack confined to Python, dbt, DuckDB, S3‑style storage, Git/GitHub. |

---

## 4. Architecture Diagram (ASCII)
```
+-------------------+   +-------------------+   +--------------------+
|  DummyJSON API    |→ |  Python Extractor |→ | data/raw/ (S3‑like) |
+-------------------+   +-------------------+   +--------------------+
                                                       |
                                                       v
                                              +--------------------+
                                              | DuckDB (raw layer) |
                                              +--------------------+
                                                       |
                                                       v
                                              +--------------------+
                                              | dbt Core (models) |
                                              +--------------------+
                                                       |
                                                       v
                                              +--------------------+
                                              | DuckDB (analytics) |
                                              +--------------------+
                                                       |
                                                       v
                                              +--------------------+
                                              | Business Metrics  |
                                              +--------------------+
```
---

## 5. Data Flow Diagram
1. **Extract** – Python script calls `/products`, `/users`, `/carts` → writes timestamped JSON files to `data/raw/<entity>/YYYY/MM/DD/`.
2. **Load (raw)** – DuckDB `READ_JSON_AUTO` loads files into staging tables (`stg_products`, `stg_users`, `stg_carts`).
3. **Transform** – dbt models (`dim_product`, `dim_customer`, `fact_order`, `mtd_revenue`, `customer_churn`).
4. **Validate** – dbt tests (unique, not null, relationships, custom SQL).
5. **Publish** – Final tables stored in `data/warehouse/warehouse.duckdb` for downstream analytics.
---

## 6. Folder Structure
```
ecommerce-elt-data-warehouse/
│
├─ data/
│   ├─ raw/           # Date‑partitioned raw JSON
│   ├─ processed/     # Optional cleaned CSV/Parquet
│   └─ warehouse/     # DuckDB analytics DB
│
├─ extraction/        # API client & config
├─ transformations/   # dbt project (models, macros, tests)
├─ sql/               # Ad‑hoc queries
├─ tests/             # Pytest suite for Python code
├─ docs/              # Design docs, SDD, diagrams
├─ config/            # .env.example, dbt profiles
├─ logs/              # JSON‑line logs for extraction & pipeline
└─ notebooks/         # Exploratory Jupyter notebooks
```
---

## 7. Tech Stack (with rationale)
| Layer | Tool | Reason |
|-------|------|--------|
| Extraction | Python 3.x + `requests` | Simple HTTP client, no external services |
| Storage (raw) | Local folder mimicking S3 | No cloud dependency, easy to version |
| Processing | DuckDB | Zero‑config, fast analytical engine, works on Windows |
| Transformation | dbt Core + dbt‑duckdb adapter | Declarative SQL, testing, documentation |
| Version Control | Git + GitHub | Standard collaborative workflow |
| Logging | Python `logging` (JSON lines) | Structured logs for observability |
| Configuration | `.env` + `config.py` | Centralised, environment‑agnostic |
---

## 8. Project Workflow
1. **Setup** – clone repo, create virtual env, `pip install -r requirements.txt`.
2. **Extract** – `python extraction/extractor.py` → raw JSON files.
3. **Load** – DuckDB automatically reads JSON when dbt runs.
4. **Transform** – `dbt run --profiles-dir config`.
5. **Test** – `dbt test` and `pytest tests/`.
6. **Explore** – Open `data/warehouse/warehouse.duckdb` with DuckDB CLI or a notebook.
---

## 9. Sprint Planning (Modules 0‑9)
| Sprint | Module | Core Deliverable |
|--------|--------|------------------|
| 0 | Planning & Concepts | SDD (this document) |
| 1 | Project Setup | Repo scaffold, `.gitignore`, `requirements.txt` |
| 2 | Data Extraction | `extraction/config.py`, `extraction/extractor.py`, logging |
| 3 | Raw Data Storage | Date‑partitioned `data/raw/` hierarchy |
| 4 | DuckDB Loading | Helper script (optional) – load raw JSON into staging tables |
| 5 | Data Modeling | dbt staging, dimension, fact models |
| 6 | dbt Transformations | CTE‑based models, Jinja macros, tests |
| 7 | Business Analytics | Analytic models (`mtd_revenue`, `customer_churn`) |
| 8 | Project Documentation | This SDD, README, architecture diagram |
| 9 | GitHub Finalization | PR template, CONTRIBUTING guide, CI‑free checks |
---

## 10. Module Breakdown
Below each module follows the required template.

### 📦 Module 0 – Planning & Concepts
| Item | Detail |
|------|--------|
| **Concept** | Establish shared terminology, coding standards, and the SDD (this document). |
| **Goal** | Align the team on scope, avoid over‑engineering, and document decisions up‑front. |
| **Files to create** | `docs/SDD.md` (this file), `docs/coding_standards.md`. |
| **Code** | N/A – documentation only. |
| **Run** | N/A |
| **Test** | Peer‑review of the document for completeness and correctness. |
| **Common Errors** | Missing sections, broken internal links. |
| **Interview Questions** | *Why is a spec‑driven approach valuable for data pipelines?* |
| **Definition of Done** | Document published, reviewed, and merged to `main`. |
| **Git Commit** | `docs: add spec‑driven design document`. |
| **Git Push** | Push branch, open PR, merge. |

---

### 📦 Module 1 – Project Setup
| Item | Detail |
|------|--------|
| **Concept** | Scaffold the repository with the required folders and base configuration. |
| **Goal** | Provide a reproducible environment for all contributors. |
| **Files to create** | `.gitignore`, `requirements.txt`, `README.md`, top‑level `docs/`, `config/` folder, empty `data/` hierarchy. |
| **Code** | No implementation code – only file creation. |
| **Run** | `git init`, create virtual env, install deps. |
| **Test** | `pip install -r requirements.txt` succeeds; `git status` shows a clean working tree. |
| **Common Errors** | Missing `.gitignore` entries causing large files to be tracked. |
| **Interview Questions** | *What should be excluded in `.gitignore` for a data‑warehouse project?* |
| **Definition of Done** | Repo scaffolded, initial commit pushed. |
| **Git Commit** | `chore: scaffold project layout & basic config`. |
| **Git Push** | Push to remote `origin/main`. |

---

### 📦 Module 2 – Data Extraction
| Item | Detail |
|------|--------|
| **Concept** | Pull raw JSON payloads from DummyJSON and persist them locally. |
| **Goal** | Populate `data/raw/` with timestamped, versioned files for downstream processing. |
| **Files to create** | `extraction/config.py` (API base URL & endpoints), `extraction/extractor.py` (client logic), `logs/extraction.log`. |
| **Code** | *High‑level description*: a Python script iterates over the endpoint map, performs `GET` requests with `requests`, writes the JSON response to `data/raw/<entity>/YYYY/MM/DD/<entity>_YYYYMMDD_HHMMSS.json`, and logs success/failure in JSON‑line format. |
| **Run** | `python extraction/extractor.py` from the repo root. |
| **Test** | Smoke test – after run, each entity folder contains at least one `.json` file; each file contains a top‑level key (`products`, `users`, `carts`). Log file contains three INFO entries. |
| **Common Errors** | Network connectivity issues, permission errors on the `data/raw/` directory, empty response due to API rate limits. |
| **Interview Questions** | *How would you make extraction idempotent if the API lacks timestamps?* |
| **Definition of Done** | Script runs without exception, files created with correct naming, logs emitted, documentation updated. |
| **Git Commit** | `feat(extraction): add API client, config, and structured logging`. |
| **Git Push** | Push branch, open PR, merge. |

---

### 📦 Module 3 – Raw Data Storage
| Item | Detail |
|------|--------|
| **Concept** | Organise raw files using a date‑partitioned hierarchy. |
| **Goal** | Enable easy re‑processing of a specific ingestion date and support data‑retention policies. |
| **Files to create** | Update `extraction/extractor.py` to write to `data/raw/<entity>/YYYY/MM/DD/`. Optional cleanup script (`scripts/cleanup_raw.py`). |
| **Code** | *Description*: the script builds the output path with `datetime.utcnow().strftime('%Y/%m/%d')` and creates missing folders with `mkdir(parents=True, exist_ok=True)`. |
| **Run** | Same as Module 2 – the extractor now respects the partitioned layout. |
| **Test** | Verify that generated files reside under the correct date folders; run cleanup script on a test folder and confirm files older than N days are removed. |
| **Common Errors** | Incorrect path separators on Windows; missing parent directories. |
| **Interview Questions** | *Why is partitioning beneficial for raw data lakes?* |
| **Definition of Done** | Files are correctly partitioned, cleanup script works, documentation reflects the layout. |
| **Git Commit** | `refactor(extraction): store raw files in date‑partitioned folders`. |
| **Git Push** | Push and merge. |

---

### 📦 Module 4 – DuckDB Loading
| Item | Detail |
|------|--------|
| **Concept** | Load raw JSON files into DuckDB staging tables automatically when dbt runs. |
| **Goal** | Provide a queryable layer for dbt models without a separate ETL step. |
| **Files to create** | Optional helper `transformations/load_raw.py` (pure‑Python) – not required for dbt‑duckdb but useful for debugging. |
| **Code** | *Description*: open a DuckDB connection to `data/warehouse/warehouse.duckdb`; use `CREATE OR REPLACE TABLE stg_<entity> AS SELECT * FROM read_json_auto('data/raw/<entity>/**/*.json')`. |
| **Run** | `dbt run` will invoke the above statements via dbt models in `models/staging/`. |
| **Test** | After dbt run, execute `SELECT COUNT(*) FROM stg_products;` (via DuckDB CLI or Python) – count > 0. |
| **Common Errors** | Schema mismatch, missing files, glob pattern errors. |
| **Interview Questions** | *How does DuckDB handle nested JSON structures?* |
| **Definition of Done** | Staging tables present with correct row counts, no errors in dbt run logs. |
| **Git Commit** | `feat(duckdb): add staging load logic via dbt`. |
| **Git Push** | Push branch, PR, merge. |

---

### 📦 Module 5 – Data Modeling
| Item | Detail |
|------|--------|
| **Concept** | Design a star schema (dimensions + fact) for ecommerce analytics. |
| **Goal** | Support business‑level metrics such as revenue, repeat purchase, churn. |
| **Files to create** | `models/staging/stg_*.sql`, `models/dim/dim_*.sql`, `models/fact/fact_*.sql`, `models/analytics/*.sql`. |
| **Code** | *Description*: each model is a single SELECT statement using CTEs; dimension models generate surrogate keys, fact model joins dimensions on those keys. |
| **Run** | `dbt run --models dim+ fact+`. |
| **Test** | dbt tests for primary key uniqueness, foreign‑key relationships, non‑null constraints. |
| **Common Errors** | Duplicate keys, mismatched data types, circular joins. |
| **Interview Questions** | *Explain the purpose of a surrogate key in a dimension table.* |
| **Definition of Done** | All models compile, tests pass, documentation generated (`dbt docs generate`). |
| **Git Commit** | `feat(models): create star‑schema staging, dimension, and fact models`. |
| **Git Push** | Push and merge. |

---

### 📦 Module 6 – dbt Transformations
| Item | Detail |
|------|--------|
| **Concept** | Implement business metrics using dbt CTEs, Jinja macros, and tests. |
| **Goal** | Provide reusable, versioned SQL for revenue, MTD revenue, churn, and cohort analysis. |
| **Files to create** | `macros/generate_surrogate_key.sql`, `models/analytics/mtd_revenue.sql`, `models/analytics/customer_churn.sql`, `tests/schema.yml` (dbt test configs). |
| **Code** | *Description*: macros generate deterministic hash‑based keys; analytic models build on the fact table with window functions and date truncation. |
| **Run** | `dbt run --models analytics+`. |
| **Test** | `dbt test` – all custom and generic tests succeed. |
| **Common Errors** | Macro naming collisions, incorrect Jinja syntax, test failures due to data quality issues. |
| **Interview Questions** | *How do Jinja macros improve maintainability of dbt models?* |
| **Definition of Done** | Analytic tables created, tests pass, docs updated (`dbt docs serve`). |
| **Git Commit** | `feat(analytics): add revenue & churn models with tests`. |
| **Git Push** | Push branch, PR, merge. |

---

### 📦 Module 7 – Business Analytics
| Item | Detail |
|------|--------|
| **Concept** | Provide end‑user queries and visualisations for key business KPIs. |
| **Goal** | Enable analysts to answer revenue, churn, and cohort questions directly against the DuckDB warehouse. |
| **Files to create** | `sql/reports/revenue_report.sql`, `sql/reports/churn_report.sql`, optional Jupyter notebook `notebooks/analytics_demo.ipynb`. |
| **Code** | *Description*: simple SELECT statements that reference the analytic models; notebook demonstrates plots using `pandas` + `matplotlib`. |
| **Run** | Execute SQL via DuckDB CLI or run the notebook. |
| **Test** | Verify that query results match expected aggregates for a known test dataset. |
| **Common Errors** | Off‑by‑one date boundaries, missing joins. |
| **Interview Questions** | *What is the difference between MTD revenue and cumulative revenue?* |
| **Definition of Done** | Reports produce correct numbers, notebook renders charts without error. |
| **Git Commit** | `doc(analytics): add sample revenue & churn queries`. |
| **Git Push** | Push and merge. |

---

### 📦 Module 8 – Project Documentation
| Item | Detail |
|------|--------|
| **Concept** | Keep all design decisions, architecture, and usage instructions up‑to‑date. |
| **Goal** | Provide a single source of truth for new contributors and future maintainers. |
| **Files to create** | `README.md` (overview), `docs/architecture.md` (diagrams), `docs/coding_standards.md`, `docs/CHANGELOG.md`. |
| **Code** | N/A – markdown only. |
| **Run** | N/A |
| **Test** | Rendered markdown displays correctly on GitHub; internal links resolve. |
| **Common Errors** | Broken image links, outdated diagrams. |
| **Interview Questions** | *Why is continuous documentation important for data pipelines?* |
| **Definition of Done** | All markdown files reviewed, merged, and linked from the main README. |
| **Git Commit** | `docs: update project documentation and architecture diagram`. |
| **Git Push** | Push and merge. |

---

### 📦 Module 9 – GitHub Finalization
| Item | Detail |
|------|--------|
| **Concept** | Prepare the repo for public consumption and future contributions. |
| **Goal** | Provide clear contribution guidelines, issue templates, and a release process. |
| **Files to create** | `.github/ISSUE_TEMPLATE/bug_report.md`, `pull_request_template.md`, `CONTRIBUTING.md`, optional GitHub Actions lint workflow (CI‑free). |
| **Code** | Minimal YAML for linting (`yaml-lint`) – optional, not required for CI. |
| **Run** | N/A |
| **Test** | Open a draft PR to verify that templates appear correctly. |
| **Common Errors** | Mis‑named template directories, syntax errors in YAML. |
| **Interview Questions** | *What elements belong in a good CONTRIBUTING guide?* |
| **Definition of Done** | Templates live in `.github/`, CONTRIBUTING guide merged, repo tagged with `v1.0.0`. |
| **Git Commit** | `docs(github): add issue & PR templates, CONTRIBUTING guide`. |
| **Git Push** | Push and merge. |

---

## 11. Coding Standards & Conventions
- **Style** – PEP 8 for Python, dbt model files use lowercase snake_case.
- **Naming** – Files: `snake_case.py`; DB objects: `snake_case`; Jinja macros: `snake_case`. 
- **Docstrings** – Triple‑quoted, include purpose, args, returns.
- **Commit Messages** – Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`). 

## 12. Git Workflow
1. Create a feature branch `git checkout -b <feature>/<ticket-id>`.
2. Write code / docs.
3. Run local tests.
4. Commit with Conventional Commits.
5. Push and open a PR to `main`.
6. PR requires at least one approving review and CI (optional lint) to pass.
7. Merge with `--no-ff` to retain history.

## 13. Error‑Handling Strategy
- **Extraction** – Retry up to 3 times with exponential back‑off; log failures as `ERROR`.
- **Database** – Wrap DuckDB operations in `try/except`; on fatal error, abort dbt run and surface the exception.
- **Testing** – Fail fast; use pytest fixtures to clean up temporary files.

## 14. Logging Strategy
- JSON‑line format (`timestamp level message`), written to `logs/`.
- Separate logger per component (`extraction`, `dbt`, `pipeline`).
- INFO for successful steps, WARNING for recoverable issues, ERROR for unrecoverable failures.

## 15. Configuration Strategy
- Central `config/.env.example` with placeholders (`API_BASE_URL`, `DUCKDB_PATH`).
- Runtime loads via `python-dotenv`; values accessed through `config.py` constants.
- Sensitive values never committed (git‑ignore `.env`).

## 16. Future Improvements (optional)
- Add incremental loads with checkpointing.
- Introduce a lightweight scheduler (e.g., `cron` on Windows Task Scheduler) for daily runs.
- plug‑in for Redshift target via dbt‑redshift adapter.
- Data quality dashboard using Great Expectations (open‑source).

---

*End of Spec‑Driven Design Document.*
