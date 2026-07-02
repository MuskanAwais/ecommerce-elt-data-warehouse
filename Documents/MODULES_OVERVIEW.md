# Modules Overview

This document provides a concise reference for each **milestone/module** defined in the Spec‑Driven Design Document (SDD). For every module we list:

1. **Purpose** – what the module accomplishes.
2. **Key Files** – the source files created/modified by the module.
3. **Storage / Runtime Details** – where data lives (local, S3, DuckDB, Redshift, PostgreSQL) and how the code interacts with it.
4. **Execution Flow** – step‑by‑step order of operations when the module is run.
5. **Verification** – how to test that the module is successful.

---

## Module 0 – Planning & Concepts
**Purpose**: Establish terminology, coding standards, and the SDD itself.
**Key Files**:
- `docs/SDD.md` (this document)
- `docs/coding_standards.md`
**Storage**: Pure markdown stored in the repository.
**Flow**: No runtime code – just documentation creation and review.
**Verification**: Manual review of completeness; commit to `main`.

---

## Module 1 – Project Setup
**Purpose**: Scaffold a clean, reproducible repository.
**Key Files**:
- `.gitignore`
- `requirements.txt`
- `README.md`
- `docs/` (directory)
- `config/` (directory)
- `data/` (empty folder)
**Storage**: Files live in the Git repo; no external storage.
**Flow**:
1. `git init` the repo.
2. Create virtual environment.
3. Install dependencies with `pip install -r requirements.txt`.
**Verification**: `git status` shows a clean tree; `pip install -r requirements.txt` runs without errors.

---

## Module 2 – Data Extraction
**Purpose**: Pull raw JSON from the DummyJSON API and persist to S3.
**Key Files**:
- `extraction/config.py` – API base URL, endpoints, AWS config.
- `extraction/extractor.py` – client logic, looping over endpoints, uploading to S3.
- `logs/extraction.log` – JSON‑line log of successes/failures.
**Storage**:
- **Code**: Local Python package under `extraction/`.
- **Data**: `s3://<bucket-name>/raw/<entity>/YYYY/MM/DD/<entity>_<timestamp>.json`.
**Flow**:
1. Load config (API URLs, bucket name, credentials).
2. For each endpoint, `GET` JSON via `requests`.
3. Write response to a temporary file.
4. Upload file to S3 using `boto3` with the date‑partitioned key.
5. Log result (status, entity, timestamp) to `extraction.log`.
**Verification**: Inspect S3 bucket for correctly‑named JSON files; confirm log entries show `SUCCESS` for each call.

---

## Module 3 – Raw Data Storage
**Purpose**: Organise raw S3 objects using a date‑partitioned hierarchy and provide a cleanup utility.
**Key Files**:
- Updated `extraction/extractor.py` (adds partitioned key logic).
- Optional `scripts/cleanup_raw.py` – removes objects older than a retention period.
**Storage**: Same S3 bucket as Module 2 but structured as `raw/<entity>/YYYY/MM/DD/`.
**Flow**:
1. Extractor now builds the partitioned key before upload.
2. (Optional) Run `python scripts/cleanup_raw.py` to delete objects older than X days.
**Verification**: Verify objects appear under the correct date folders; run cleanup script and confirm old objects are removed.

---

## Module 4 – Data Loading (DuckDB / Redshift)
**Purpose**: Load raw JSON from S3 into staging tables for downstream dbt models.
**Key Files**:
- `profiles.yml` – dbt connection profiles for DuckDB (local) and Redshift (prod).
- Optional `transformations/load_raw.py` – helper script for manual loads.
**Storage / Runtime**:
- **DuckDB**: Local `.duckdb` file created in the repo root.
- **Redshift**: Managed cluster; data lands in schema `staging`.
**Flow**:
1. dbt `run` triggers models under `models/staging/`.
2. Each staging model issues a `CREATE OR REPLACE TABLE … AS SELECT * FROM read_json_auto('s3://…/*.json')` (DuckDB) or `COPY … FROM 's3://…/' IAM_ROLE …` (Redshift).
3. Resulting tables `stg_<entity>` are materialised.
**Verification**: After `dbt run`, run `SELECT COUNT(*) FROM stg_<entity>;` – count should be > 0.

---

## Module 5 – Data Modeling
**Purpose**: Build a star schema (dimensions + fact) for analytic workloads.
**Key Files**:
- `models/staging/stg_*.sql` – raw → staging transforms.
- `models/dim/dim_*.sql` – dimension tables (e.g., `dim_product.sql`).
- `models/fact/fact_*.sql` – fact tables (e.g., `fact_sales.sql`).
- `models/analytics/*.sql` – high‑level analytic models.
**Storage / Runtime**: dbt models compile to tables/views in DuckDB/Redshift.
**Flow**:
1. `dbt run --models dim+ fact+` builds dimensions first, then facts.
2. Surrogate keys generated via `macros/generate_surrogate_key.sql`.
3. Fact table joins to dimension surrogate keys.
**Verification**: dbt tests for primary‑key uniqueness, foreign‑key integrity, non‑null constraints all pass.

---

## Module 6 – dbt Transformations (Business Metrics)
**Purpose**: Implement reusable business metric calculations.
**Key Files**:
- `macros/generate_surrogate_key.sql`
- `models/analytics/mtd_revenue.sql`
- `models/analytics/customer_churn.sql`
- `tests/schema.yml` – custom dbt tests for the analytics models.
**Storage / Runtime**: Executed as dbt models; results stored as tables/views.
**Flow**:
1. `dbt run --models analytics+` builds analytic tables.
2. Macros generate deterministic surrogate keys where needed.
3. Window functions compute MTD, churn, cohort metrics.
**Verification**: `dbt test` – all generic and custom tests must succeed.

---

## Module 7 – Business Analytics (Reporting & Serving Layer)
**Purpose**: Provide end‑user SQL reports and optionally sync aggregates to a PostgreSQL data‑mart.
**Key Files**:
- `sql/reports/revenue_report.sql`
- `sql/reports/churn_report.sql`
- Optional `scripts/sync_to_postgres.py` – copies final tables to PostgreSQL.
**Storage / Runtime**:
- Reports run directly against DuckDB/Redshift.
- Sync script writes to a PostgreSQL instance (serving layer).
**Flow**:
1. Analyst runs the report SQL via CLI or BI tool.
2. (Optional) Execute `python scripts/sync_to_postgres.py` to push aggregates to PostgreSQL.
**Verification**: Query results match expected KPI values; PostgreSQL tables contain same data after sync.

---

## Module 8 – Project Documentation
**Purpose**: Keep design decisions, architecture diagrams, and usage instructions up‑to‑date.
**Key Files**:
- `README.md`
- `docs/architecture.md`
- `docs/coding_standards.md`
- `docs/CHANGELOG.md`
**Storage**: Markdown files in the repo; rendered on GitHub.
**Flow**: Documentation is edited manually; no runtime component.
**Verification**: Rendered markdown displays correctly on GitHub; internal links are valid.

---

## Module 9 – GitHub Finalization
**Purpose**: Prepare the repository for public consumption and future contributions.
**Key Files**:
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/pull_request_template.md`
- `CONTRIBUTING.md`
- Optional CI lint workflow (`.github/workflows/lint.yml`).
**Storage**: YAML/markdown under `.github/` and root.
**Flow**:
1. Add templates and contributing guide.
2. (Optional) Enable CI linting.
3. Open a draft PR to verify templates render.
**Verification**: Draft PR shows templates correctly; `CONTRIBUTING.md` merged; repo tagged `v1.0.0`.

---

## End‑to‑End Flow Summary
1. **Plan & Set Up** – Modules 0 & 1.
2. **Extract Raw JSON** – Module 2 stores data in S3.
3. **Organise Raw Data** – Module 3 adds date‑partitioning.
4. **Load into Staging** – Module 4 creates `stg_*` tables.
5. **Model Star Schema** – Module 5 builds dimensions & facts.
6. **Add Business Metrics** – Module 6 creates analytic tables.
7. **Expose Reports / Serve** – Module 7 provides SQL reports and optional PostgreSQL sync.
8. **Document Everything** – Module 8 keeps knowledge current.
9. **Finalize Repository** – Module 9 adds contribution scaffolding.

Each step builds on the previous one, ensuring data flows from raw ingestion in S3 all the way to consumable analytics and reporting layers, with automated testing and documentation throughout.

---

*Generated for the **ecommerce‑elt‑data‑warehouse** project on 2026‑07‑02.*
