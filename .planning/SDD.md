# Spec-Driven Design Document (SDD)
## E-Commerce ELT Data Warehouse

**Stack:** Python, dbt, AWS S3, DuckDB, PostgreSQL (optional)  
**Document Type:** Spec-Driven Design (SDD)  
**Version:** 2.0  
**Location:** `.planning/SDD.md`

---

## 1. Project Overview

A production-style **ELT pipeline** that extracts product, customer, and order data from the **DummyJSON** REST API, lands raw JSON in a date-partitioned data lake (local `Data/raw/` + AWS S3), loads into **DuckDB**, transforms with **dbt Core**, and produces analytics KPIs via `orchestration_pipeline.py`.

All planning documents live in `.planning/`:

| File | Purpose |
|---|---|
| `SDD.md` | This document — module specs and milestones |
| `master_plan.md` | Roadmap, completion tracker, deliverables |
| `revision.md` | Full workflow, architecture, testing, expected output |
| `spec_1.md` – `spec_9.md` | Per-module detailed specifications |

---

## 2. Business Problem

E-commerce analysts need timely, reliable metrics (revenue, churn, cohort analysis). Manual CSV dumps are error-prone, not versioned, and do not scale. A reproducible ELT pipeline solves these pain points.

---

## 3. Objectives

| # | Objective |
|---|---|
| 1 | Pull raw data (products, customers, orders) via a Python client |
| 2 | Store raw JSON in `Data/raw/` with date-partitioned folders + S3 upload |
| 3 | Load raw JSON into DuckDB staging tables |
| 4 | Model dimensional tables and business metrics with dbt |
| 5 | Provide automated data-quality tests (pytest + dbt) |
| 6 | Run the full pipeline with one command and a formatted analytics report |

---

## 4. Architecture

```
DummyJSON API
      │
      ▼
src/extraction/  ──►  Data/raw/  +  s3://bucket/raw/
      │
      ▼
src/scripts/load_raw.py  ──►  DuckDB (main.stg_*)
      │
      ▼
src/transformations/ (dbt)  ──►  dim / fact / analytics tables
      │
      ▼
orchestration_pipeline.py  ──►  Terminal analytics report
```

---

## 5. Project Structure

```
ecommerce-elt-data-warehouse/
├── .planning/              # SDD, specs, master plan, revision guide
├── src/                    # All source code
├── Data/                   # Raw JSON + DuckDB warehouse (gitignored)
├── results/                # Logs + dbt artifacts (gitignored)
├── tests/                  # pytest suite
├── orchestration_pipeline.py
├── config/profiles.yml
└── README.md
```

---

## 6. Tech Stack

| Layer | Tool | Reason |
|---|---|---|
| Extraction | Python + `requests` + `boto3` | Simple HTTP client and S3 upload |
| Raw storage | Local `Data/raw/` + AWS S3 | Data lake with date partitioning |
| Warehouse | DuckDB | Fast local analytics engine |
| Transform | dbt Core + dbt-duckdb | Versioned SQL, tests, lineage |
| Orchestration | `orchestration_pipeline.py` | One-command end-to-end run |
| Testing | pytest + dbt tests | Python and SQL data quality |
| Version control | Git + GitHub | Module-based commit history |

---

## 7. How to Read This Document

This project is broken into **modules** (0–9). Each module has a clear goal, files it produces, how to run it, how to test it, and a **Definition of Done**. When a module is finished, it becomes one Git commit — the commit history acts as a visual progress tracker.

For detailed per-module specs see `spec_1.md` through `spec_9.md`. For the full operational guide see `revision.md`.

---

## Module 0 — Planning & Concepts

| Item | Detail |
|---|---|
| **Concept** | Establish shared terminology, coding standards, and this SDD. |
| **Goal** | Align scope before writing code and document key decisions up front. |
| **Files Created** | `.planning/SDD.md`, `.planning/master_plan.md`, `.planning/revision.md`, `spec_1.md`–`spec_9.md` |
| **Run** | N/A |
| **Test** | Review documents for completeness and correct paths. |
| **Definition of Done** | All planning docs in `.planning/`, reviewed and merged. |

**Milestone commit:** `docs: add spec-driven design document`

---

## Module 1 — Project Setup

| Item | Detail |
|---|---|
| **Concept** | Scaffold the repository with required folders and base configuration. |
| **Goal** | Reproducible environment from day one. |
| **Files Created** | `.gitignore`, `requirements.txt`, `README.md`, `config/`, `Data/` hierarchy, `tests/`, `pytest.ini` |
| **Run** | `pip install -r requirements.txt` |
| **Test** | Install succeeds; `git status` excludes `.env`, `Data/raw/`, `results/`. |
| **Definition of Done** | Repo scaffolded with `src/`, `Data/`, `results/`, `.planning/` layout. |

**Milestone commit:** `chore: scaffold project layout & basic config`

---

## Module 2 — Data Extraction

| Item | Detail |
|---|---|
| **Concept** | Pull raw JSON from DummyJSON API and upload to S3. |
| **Goal** | Populate raw layer with timestamped files. |
| **Files Created** | `src/extraction/config.py`, `src/extraction/extractor.py`, `results/logs/extraction.log` |
| **Run** | `cd src && python -m extraction.extractor` |
| **Test** | S3 contains files under `raw/` prefix; `pytest tests/test_extraction.py` passes. |
| **Definition of Done** | Script runs without errors, S3 paths correct, logs produced. |

**Milestone commit:** `feat(extraction): add API client, config, structured logging, and S3 upload`

---

## Module 3 — Raw Data Storage

| Item | Detail |
|---|---|
| **Concept** | Date-partitioned raw layer for reprocessing and retention. |
| **Goal** | Files at `Data/raw/<entity>/YYYY/MM/DD/` and `s3://bucket/raw/<entity>/YYYY/MM/DD/`. |
| **Files Created** | Updated `src/extraction/extractor.py` |
| **Run** | Same as Module 2. |
| **Test** | Confirm date paths in local storage and S3. |
| **Definition of Done** | Files correctly partitioned locally and in S3. |

**Milestone commit:** `refactor(extraction): store raw files in date-partitioned S3 paths`

---

## Module 4 — Data Loading (DuckDB)

| Item | Detail |
|---|---|
| **Concept** | Load raw JSON into DuckDB staging tables. |
| **Goal** | Queryable `stg_*` tables in `Data/warehouse/warehouse.duckdb`. |
| **Files Created** | `config/profiles.yml`, `src/scripts/load_raw.py` |
| **Run** | `cd src && python -m scripts.load_raw` |
| **Test** | `SELECT COUNT(*) FROM stg_products` > 0; `pytest tests/test_load_raw.py` passes. |
| **Definition of Done** | Staging tables populated with correct row counts. |

**Milestone commit:** `feat(warehouse): add DuckDB load_raw under src/scripts`

---

## Module 5 — Data Modeling

| Item | Detail |
|---|---|
| **Concept** | Star schema (dimensions + fact table). |
| **Goal** | Support revenue, repeat purchases, and churn metrics. |
| **Files Created** | `src/transformations/models/staging/`, `dim/`, `fact/`, `macros/generate_surrogate_key.sql` |
| **Run** | `.\run_dbt.ps1 run --select staging+ dim+ fact+` |
| **Test** | dbt tests for PK uniqueness, FK relationships, not_null. |
| **Definition of Done** | All models compile and tests pass. |

**Milestone commit:** `feat(models): create star-schema staging, dimension, and fact models`

---

## Module 6 — dbt Transformations (Analytics)

| Item | Detail |
|---|---|
| **Concept** | Business metrics via dbt CTEs, Jinja macros, and tests. |
| **Goal** | Revenue, MTD, churn, LTV analytics tables. |
| **Files Created** | `models/analytics/*.sql`, `macros/cents_to_dollars.sql`, `schema.yml` |
| **Run** | `.\run_dbt.ps1 run --select analytics+` |
| **Test** | `.\run_dbt.ps1 test` — 35 tests pass. |
| **Definition of Done** | Analytics tables built, all dbt tests green. |

**Milestone commit:** `feat(analytics): add revenue & churn models with tests`

---

## Module 7 — Business Analytics & Orchestration

| Item | Detail |
|---|---|
| **Concept** | KPI reports and single-command pipeline orchestration. |
| **Goal** | Analyst SQL queries + end-to-end automated run with formatted output. |
| **Files Created** | `src/sql/reports/`, `orchestration_pipeline.py`, `src/scripts/sync_to_postgres.py` |
| **Run** | `python orchestration_pipeline.py` |
| **Test** | Pipeline report shows extraction, S3, DuckDB, dbt, and analytics sections. |
| **Definition of Done** | One-command pipeline completes with analytics report. |

**Milestone commit:** `feat(orchestration): add single-command end-to-end ELT pipeline runner`

---

## Module 8 — Project Documentation

| Item | Detail |
|---|---|
| **Concept** | Keep design decisions and usage instructions up to date. |
| **Goal** | Single source of truth for contributors. |
| **Files Created** | `README.md`, `.planning/revision.md`, `.planning/master_plan.md` |
| **Test** | Markdown renders on GitHub; internal links resolve. |
| **Definition of Done** | Docs reviewed and linked from README. |

**Milestone commit:** `docs: consolidate documentation into revision.md and clean up README`

---

## Module 9 — GitHub Finalization

| Item | Detail |
|---|---|
| **Concept** | Repo ready for public portfolio and contributions. |
| **Goal** | Issue/PR templates and contribution guide. |
| **Files Created** | `.github/ISSUE_TEMPLATE/`, `.github/pull_request_template.md`, `CONTRIBUTING.md` |
| **Test** | New issue/PR templates render correctly on GitHub. |
| **Definition of Done** | Templates merged; `.env` and secrets excluded from git. |

**Milestone commit:** `docs(github): add CONTRIBUTING guide and issue/PR templates`

---

## Coding Standards & Conventions

- **Style** — PEP 8 for Python; dbt models use lowercase `snake_case`.
- **Naming** — Files: `snake_case.py`; database objects: `snake_case`.
- **Docstrings** — Triple-quoted; include purpose, args, and returns.
- **Commits** — [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `chore:`.

---

## Milestone Summary

| Milestone | Module | Commit Message |
|---|---|---|
| M0 | Planning & Concepts | `docs: add spec-driven design document` |
| M1 | Project Setup | `chore: scaffold project layout & basic config` |
| M2 | Data Extraction | `feat(extraction): add API client, config, structured logging, and S3 upload` |
| M3 | Raw Data Storage | `refactor(extraction): store raw files in date-partitioned S3 paths` |
| M4 | Data Loading | `feat(warehouse): add DuckDB load_raw under src/scripts` |
| M5 | Data Modeling | `feat(models): create star-schema staging, dimension, and fact models` |
| M6 | dbt Transformations | `feat(analytics): add revenue & churn models with tests` |
| M7 | Orchestration | `feat(orchestration): add single-command end-to-end ELT pipeline runner` |
| M8 | Documentation | `docs: consolidate documentation into revision.md and clean up README` |
| M9 | GitHub Finalization | `docs(github): add CONTRIBUTING guide and issue/PR templates` |

When every row has a matching commit on GitHub, the project is complete and ready for evaluation.
