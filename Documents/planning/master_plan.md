# Master Plan: E-Commerce ELT Data Warehouse

## 1. Project Overview
The E-Commerce ELT Data Warehouse is an end-to-end data pipeline designed to extract raw e-commerce data (orders, products, and customers), load it into a central repository, and transform it for business intelligence and analytics. This project demonstrates core data engineering principles using an Extract, Load, Transform (ELT) architecture, serving as a comprehensive, beginner-friendly portfolio piece.

## 2. Project Goals
**Technical Goals:**
- Build a robust ELT pipeline pulling data from a mock REST API.
- Implement reliable data ingestion into cloud storage or a local data lake (S3/Raw Layer).
- Use dbt for modular, tested, and version-controlled data transformations.
- Create a dimensional data model suitable for reporting.

**Learning Goals:**
- Master the ELT paradigm (Extract, Load, Transform vs. ETL).
- Gain hands-on experience with modern data stack tools like DuckDB and dbt.
- Understand how to structure, test, and document data models for business users.

## 3. Technology Stack
- **Python**: Extraction scripts, DuckDB loading, orchestration, and pytest suite.
- **S3 / Local File System**: Raw data lake (S3 in production; `Data/raw/` locally).
- **DuckDB**: In-process analytical database (`Data/warehouse/warehouse.duckdb`).
- **dbt (data build tool)**: SQL transformations, Jinja macros, and data-quality tests.
- **PostgreSQL (Optional)**: Serving layer for BI tools via `src/scripts/sync_to_postgres.py`.

## 4. Project Architecture
The data flows through a modern ELT architecture:

**Mock API → Raw Layer → DuckDB → dbt Transformations → Analytics Tables → Reports**

| Layer | Location | Purpose |
|---|---|---|
| Mock API | DummyJSON (`/products`, `/users`, `/carts`) | Source system |
| Raw Layer | `Data/raw/<entity>/YYYY/MM/DD/` + S3 `raw/` prefix | Landing zone (immutable JSON) |
| Warehouse | `Data/warehouse/warehouse.duckdb` | Query engine and transformed tables |
| dbt Project | `src/transformations/` | Staging → dim/fact → analytics models |
| Results | `results/logs/`, `results/dbt/` | Pipeline logs and dbt artifacts |
| Reports | `src/sql/reports/` | Analyst-facing SQL queries |

## 5. Project Structure (Current — Required Layout)
```text
ecommerce-elt-data-warehouse/
├── src/                          # All application source code
│   ├── extraction/               # API client (config.py, extractor.py)
│   ├── scripts/                  # load_raw.py, sync_to_postgres.py
│   ├── transformations/          # dbt project (models, macros, tests)
│   ├── sql/reports/              # revenue_report.sql, churn_report.sql
│   ├── paths.py                  # Shared path constants
│   ├── orchestrator.py           # End-to-end pipeline runner
│   ├── analytics_report.py       # Terminal analytics dashboard
│   ├── verify_warehouse.py       # DuckDB verification helper
│   └── run_dbt.ps1               # dbt wrapper script
├── Data/                         # All data files (not committed except .gitkeep)
│   ├── raw/                      # Extracted JSON from API
│   ├── processed/                # Intermediate files (reserved)
│   └── warehouse/                # DuckDB database file
├── results/                      # Pipeline outputs (not committed)
│   ├── logs/                     # extraction.log, load_raw.log, dbt.log
│   └── dbt/                      # manifest.json, run_results.json, compiled SQL
├── tests/                        # Pytest unit tests
├── Documents/                    # All documentation (.md, .docx, .pdf)
│   └── planning/                 # master_plan.md, SDD, spec_1–spec_9
├── config/                       # dbt profiles.yml, local user config
├── .github/                      # Issue templates
├── README.md                     # Quick-start entry point
├── requirements.txt
└── pytest.ini
```

## 6. Database Design
The warehouse follows a dimensional modeling approach (Star Schema):

- **Source Tables**: Raw JSON landed from the API.
- **Staging Tables (`stg_`)**: Cleaned, typed views/tables.
  - `stg_customers`, `stg_products`, `stg_orders`
- **Dimension Tables (`dim_`)**: Descriptive context.
  - `dim_customer`, `dim_product`
- **Fact Table (`fact_`)**: Measurable transactions.
  - `fact_orders` — order amounts, dates, foreign keys to dimensions
- **Analytics Tables**: Business KPIs.
  - `analytics_revenue_daily`, `analytics_customer_metrics`, `mtd_revenue`, `customer_churn`

## 7. Module Completion Tracker

Each module maps to the SDD in `Documents/planning/SDD_ECommerce_ELT.md`. Status is based on the current codebase as of the latest restructure.

| Module | Name | Status | Completion |
|---|---|---|---|
| **0** | Planning & Concepts | ✅ Complete | 100% |
| **1** | Project Setup | ✅ Complete | 100% |
| **2** | Data Extraction | ✅ Complete | 100% |
| **3** | Raw Data Storage | ✅ Complete* | 95% |
| **4** | Data Loading (DuckDB) | ✅ Complete | 100% |
| **5** | Data Modeling | ✅ Complete | 100% |
| **6** | dbt Transformations (Analytics) | ✅ Complete | 100% |
| **7** | Business Analytics (Reporting) | ✅ Complete | 95% |
| **8** | Project Documentation | ✅ Complete | 95% |
| **9** | GitHub Finalization | ✅ Complete | 90% |

\* Module 3 optional `cleanup_raw.py` was not implemented (not required for core pipeline).

### Module 0 — Planning & Concepts ✅
| Item | Detail |
|---|---|
| **Goal** | Align scope, terminology, and architecture before coding. |
| **Deliverables** | `Documents/planning/SDD_ECommerce_ELT.md`, `Documents/planning/master_plan.md`, `spec_1.md`–`spec_9.md` |
| **Expected Output** | Written SDD with module definitions, Definition of Done per module, and Git commit conventions. |
| **Verify** | Open `Documents/planning/SDD_ECommerce_ELT.md` — all 10 modules documented. |
| **Status** | ✅ Complete |

### Module 1 — Project Setup ✅
| Item | Detail |
|---|---|
| **Goal** | Reproducible repo scaffold with required folder layout. |
| **Deliverables** | `.gitignore`, `requirements.txt`, `README.md`, `config/`, `Data/` hierarchy, `tests/`, `pytest.ini` |
| **Expected Output** | `pip install -r requirements.txt` succeeds; folders match Section 5 structure above. |
| **Verify** | `pytest --collect-only` discovers tests; `git status` excludes `.venv`, `Data/raw/`, `results/`. |
| **Status** | ✅ Complete — restructured to `src/`, `Data/`, `results/`, `Documents/`. |

### Module 2 — Data Extraction ✅
| Item | Detail |
|---|---|
| **Goal** | Pull JSON from DummyJSON API and upload to S3. |
| **Deliverables** | `src/extraction/config.py`, `src/extraction/extractor.py`, `results/logs/extraction.log` |
| **Expected Output** | Three JSON payloads fetched (products, customers, orders); S3 keys under `raw/<entity>/YYYY/MM/DD/<entity>_<timestamp>.json`; local copies in `Data/raw/`. |
| **Verify** | `cd src && python -m extraction.extractor` — log shows ✓ for all entities; `pytest tests/test_extraction.py` passes (7/7 tests). |
| **Status** | ✅ Complete |

### Module 3 — Raw Data Storage ✅
| Item | Detail |
|---|---|
| **Goal** | Date-partitioned raw layer for reprocessing and retention policies. |
| **Deliverables** | Updated `src/extraction/extractor.py` (local + S3 partitioned paths) |
| **Expected Output** | Files land at `Data/raw/<entity>/YYYY/MM/DD/` and `s3://<bucket>/raw/<entity>/YYYY/MM/DD/`. |
| **Verify** | List `Data/raw/products/` — date subfolders present; S3 list shows matching prefix structure. |
| **Gap** | Optional `src/scripts/cleanup_raw.py` not built (S3 lifecycle cleanup). |
| **Status** | ✅ Complete (core); optional cleanup pending |

### Module 4 — Data Loading (DuckDB) ✅
| Item | Detail |
|---|---|
| **Goal** | Load raw JSON into DuckDB staging tables. |
| **Deliverables** | `config/profiles.yml`, `src/scripts/load_raw.py`, dbt staging models in `src/transformations/models/staging/` |
| **Expected Output** | `Data/warehouse/warehouse.duckdb` created with `stg_customers`, `stg_products`, `stg_orders` populated (row count > 0). Log at `results/logs/load_raw.log`. |
| **Verify** | `cd src && python -m scripts.load_raw` then `python verify_warehouse.py` — staging tables listed with rows. |
| **Status** | ✅ Complete — re-run load after restructure if `warehouse.duckdb` is missing. |

### Module 5 — Data Modeling ✅
| Item | Detail |
|---|---|
| **Goal** | Star-schema dimensions and fact table via dbt. |
| **Deliverables** | `stg_*.sql`, `dim_customer.sql`, `dim_product.sql`, `fact_orders.sql`, `schema.yml` |
| **Expected Output** | dbt builds `dim_customer`, `dim_product`, `fact_orders` with surrogate keys and FK relationships; all generic tests pass. |
| **Verify** | `.\src\run_dbt.ps1 run --select staging+ dim+ fact+` then `.\src\run_dbt.ps1 test --select staging+ dim+ fact+`. |
| **Status** | ✅ Complete |

### Module 6 — dbt Transformations (Analytics) ✅
| Item | Detail |
|---|---|
| **Goal** | Business metrics: revenue, MTD, churn, LTV with macros and tests. |
| **Deliverables** | `macros/cents_to_dollars.sql`, `macros/generate_surrogate_key.sql`, `analytics_*.sql`, `mtd_revenue.sql`, `customer_churn.sql`, tests in `schema.yml` |
| **Expected Output** | Tables `analytics_revenue_daily`, `analytics_customer_metrics`, `mtd_revenue`, `customer_churn`, `revenue_metrics` materialized; `dbt test --select analytics+` all green. |
| **Verify** | `.\src\run_dbt.ps1 run --select analytics+` → 11/11 PASS; `.\src\run_dbt.ps1 test` → 35/35 PASS. |
| **Status** | ✅ Complete — fixed `order_date` in fact table, macro/SQL syntax, trailing semicolons. |

### Module 7 — Business Analytics (Reporting) ✅
| Item | Detail |
|---|---|
| **Goal** | Analyst SQL reports and optional PostgreSQL serving layer. |
| **Deliverables** | `src/sql/reports/revenue_report.sql`, `src/sql/reports/churn_report.sql`, `src/scripts/sync_to_postgres.py`, `src/analytics_report.py`, `src/orchestrator.py` |
| **Expected Output** | Report queries return revenue and churn KPIs from analytics tables; orchestrator runs extract → load → dbt → test end-to-end. |
| **Verify** | Run report SQL against DuckDB; `cd src && python analytics_report.py` renders dashboard. |
| **Gap** | PostgreSQL sync requires live `POSTGRES_DSN` — not verified in CI. |
| **Status** | ✅ Complete (core); Postgres sync optional |

### Module 8 — Project Documentation ✅
| Item | Detail |
|---|---|
| **Goal** | Single source of truth for contributors and evaluators. |
| **Deliverables** | `README.md`, `Documents/revision.md`, `Documents/planning/master_plan.md`, `CONTRIBUTING.md` |
| **Expected Output** | GitHub README renders; revision guide covers architecture, workflow, and expected pipeline output. |
| **Verify** | Review `README.md` and `Documents/revision.md`. |
| **Status** | ✅ Complete |

### Module 9 — GitHub Finalization ✅
| Item | Detail |
|---|---|
| **Goal** | Repo ready for public portfolio and contributions. |
| **Deliverables** | `.github/ISSUE_TEMPLATE/bug_report.md`, `.github/pull_request_template.md`, `CONTRIBUTING.md` |
| **Expected Output** | New issues use templates; PR template guides reviewers; CONTRIBUTING linked from README. |
| **Verify** | Open GitHub → Issues → New issue shows bug template; CONTRIBUTING.md exists at repo root. |
| **Gap** | Optional: GitHub Actions CI workflow and release tag `v1.0.0`. |
| **Status** | ✅ Complete (core); CI/tag optional |

---

## 8. Development Roadmap (Phases → Expected Outputs)

### Phase 1: Planning and Setup ✅
- **Objective**: Establish project foundation and architecture.
- **Tasks**: Master plan, Git repo, folder structure, mock API endpoints.
- **Expected Output**: Structured repo (`src/`, `Data/`, `results/`, `tests/`, `Documents/`) with documented plan.

### Phase 2: Data Extraction (Extract & Load) ✅
- **Objective**: Ingest data from DummyJSON API.
- **Tasks**: Python extraction modules, S3 upload, local raw save.
- **Expected Output**: JSON files in `Data/raw/<entity>/YYYY/MM/DD/` and S3 `raw/` prefix; 7 pytest tests passing.

### Phase 3: Data Warehousing (Load to DB) ✅
- **Objective**: Move raw data into DuckDB.
- **Tasks**: `load_raw.py`, DuckDB staging tables.
- **Expected Output**: `Data/warehouse/warehouse.duckdb` with `stg_*` tables (row count > 0).

### Phase 4: Data Transformation (dbt) ✅
- **Objective**: Build dimensional model and analytics layer.
- **Tasks**: dbt staging, dim, fact, and analytics models with tests.
- **Expected Output**: Star schema tables built; dbt tests pass for staging/dim/fact; analytics models mostly built (see Module 6 gap).

### Phase 5: Testing and Documentation ✅
- **Objective**: Ensure data quality and pipeline reliability.
- **Tasks**: dbt tests, pytest, dbt docs, README updates.
- **Expected Output**: Full test suite green; compiled data dictionary in `results/dbt/`; documentation aligned with current structure.
- **Status**: ✅ Complete — 7 pytest + 35 dbt tests passing; architecture doc added.

---

## 9. Business Metrics
The analytics layer supports these KPIs:

| KPI | Source Model | Expected Query Result |
|---|---|---|
| **Total Revenue** | `fact_orders` / `analytics_revenue_daily` | Sum of order totals by day |
| **Average Order Value (AOV)** | `mtd_revenue` | `net_revenue / total_orders` |
| **Active / Churned Customers** | `analytics_customer_metrics`, `customer_churn` | Status: Active, At Risk, Churned, Never Purchased |
| **Revenue by Category** | `fact_orders` ⋈ `dim_product` | Aggregated revenue grouped by product category |
| **Customer LTV** | `analytics_customer_metrics` | Lifetime value in dollars (via `cents_to_dollars` macro) |

---

## 10. Testing Strategy
| Type | Tool | Location | Expected Output |
|---|---|---|---|
| Python unit tests | pytest | `tests/` | 7 tests pass (`test_extraction`, `test_load_raw`) |
| dbt generic tests | dbt test | `src/transformations/models/schema.yml` | not_null, unique, relationships, accepted_values all pass |
| End-to-end | orchestrator | `src/orchestrator.py` | Extract → S3 validate → load → dbt run → dbt test completes without error |

**Run tests:**
```bash
pytest                                    # Python tests
.\src\run_dbt.ps1 test                    # dbt tests
cd src && python orchestrator.py          # full pipeline (requires AWS creds)
```

---

## 11. Deployment Strategy
- **Local Execution**: `cd src && python -m extraction.extractor` → `python -m scripts.load_raw` → `.\src\run_dbt.ps1 run`
- **Containerization (Docker)**: Future — package pipeline into a reproducible image.
- **Automation (GitHub Actions)**: Future — CI on push for pytest + dbt test.

---

## 12. Final Deliverables Checklist

| # | Deliverable | Path | Status |
|---|---|---|---|
| 1 | Extraction codebase | `src/extraction/` | ✅ |
| 2 | dbt project (staging, dim, fact, analytics) | `src/transformations/` | ✅ |
| 3 | Populated DuckDB warehouse | `Data/warehouse/warehouse.duckdb` | ✅ |
| 4 | pytest + dbt test suites | `tests/`, `schema.yml` | ✅ (7 pytest + 35 dbt) |
| 5 | Architecture + revision guide | `Documents/revision.md` | ✅ |
| 6 | README + setup guide | `README.md` | ✅ |
| 7 | SQL report queries | `src/sql/reports/` | ✅ |
| 8 | Pipeline orchestrator | `src/orchestrator.py` | ✅ |
| 9 | GitHub templates + CONTRIBUTING | `.github/`, `CONTRIBUTING.md` | ✅ |

---

## 13. Remaining Work (Optional Enhancements)
1. **GitHub Actions CI** — run `pytest` + `dbt test` on every push.
2. **Release tag** — tag `v1.0.0` on GitHub when ready for portfolio.
3. **PostgreSQL sync verification** — test `sync_to_postgres.py` with live database.
4. **Optional** — `cleanup_raw.py`, Docker containerization, incremental dbt models.

---

## 14. Coding Standards & Conventions
- **Style** — PEP 8 for Python; dbt model files use lowercase `snake_case`.
- **Naming** — Files: `snake_case.py`; database objects: `snake_case`; Jinja macros: `snake_case`.
- **Docstrings** — Triple-quoted, include purpose, args, and returns.
- **Commit Messages** — Follow Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`.
- **Paths** — Use `src/paths.py` constants; never hard-code legacy `data/` or root-level module paths.

---

## 15. Milestone Summary (Quick Reference)

| Milestone | Module | Commit Message | Status |
|---|---|---|---|
| M0 | Planning & Concepts | `docs: add spec-driven design document` | ✅ |
| M1 | Project Setup | `chore: scaffold project layout & basic config` | ✅ |
| M2 | Data Extraction | `feat(extraction): add API client, config, structured logging, and S3 upload` | ✅ |
| M3 | Raw Data Storage | `refactor(extraction): store raw files in date-partitioned S3 paths` | ✅ |
| M4 | Data Loading | `feat(warehouse): add staging load logic from S3 via dbt (DuckDB/Redshift)` | ✅ |
| M5 | Data Modeling | `feat(models): create star-schema staging, dimension, and fact models` | ✅ |
| M6 | dbt Transformations | `feat(analytics): add revenue & churn models with tests` | ✅ |
| M7 | Business Analytics | `feat(analytics): add sample reporting queries and Postgres serving sync` | ✅ |
| M8 | Project Documentation | `docs: update project documentation and architecture diagram` | ✅ |
| M9 | GitHub Finalization | `docs(github): add issue & PR templates, CONTRIBUTING guide` | ✅ |

**Overall project completion: ~98%** — all core modules complete; optional CI/tag/Postgres sync remain.

When every row shows ✅ and `dbt test` passes for all models, the project is complete and ready for evaluation.
