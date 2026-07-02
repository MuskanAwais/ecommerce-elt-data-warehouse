# Project Context: Ecommerce ELT Data Warehouse

## Overview
This repository implements an **Extract‑Load‑Transform (ELT)** data pipeline for an ecommerce platform.  The pipeline ingests raw JSON event data, loads it into a DuckDB data warehouse, and builds a dimensional model with staging, dimension, fact, and analytics layers using **dbt**.

## Repository Layout
```
.
├─ .planning/                # Project specifications and master plan
│   ├─ master_plan.md        # High‑level roadmap (Modules 1‑7)
│   ├─ spec_6.md            # Module 6 – analytics layer spec
│   └─ spec_7.md            # Module 7 – BI/reporting spec
├─ extraction/               # Python code that extracts raw data
│   └─ config.py            # Extraction configuration (API keys, paths)
├─ transformations/          # dbt project
│   ├─ dbt_project.yml       # dbt project config
│   ├─ macros/               # Jinja macros (e.g., cents_to_dollars)
│   ├─ models/               # dbt models
│   │   ├─ staging/          # Staging views (stg_*)
│   │   ├─ dim/              # Dimension tables (dim_*)
│   │   ├─ fact/             # Fact tables (fact_*)
│   │   └─ analytics/        # Analytics / data‑mart models (Module 6)
│   │       ├─ analytics_revenue_daily.sql   # Daily revenue aggregation
│   │       ├─ analytics_customer_metrics.sql # LTV & churn metrics
│   │       ├─ revenue_metrics.sql           # Legacy model (currently disabled)
│   │       └─ customer_churn.sql             # Legacy churn model (currently disabled)
│   └─ tests/               # dbt tests for data quality
├─ config/                   # dbt profile (DuckDB connection settings)
└─ README.md                 # High‑level README (not shown here)
```

## Modules Implemented
| Module | Description | Status |
|--------|-------------|--------|
| 1‑5   | Extraction, staging, dimension, fact layers – fully functional and passing all dbt tests. |
| 6      | **Analytics layer** – adds `analytics_revenue_daily` and `analytics_customer_metrics` models, macro `cents_to_dollars`, and associated tests. |
| 7      | Planned BI/reporting layer (spec_7.md) – not yet implemented. |

## Key dbt Details
- **Adapter:** DuckDB (local, file‑based `warehouse/warehouse.duckdb`).
- **Materialisations:** All analytics models are materialised as **tables**.
- **Macros:** `cents_to_dollars.sql` converts integer cents to a decimal dollar amount and is used in the LTV calculation.
- **Tests:** Added `not_null`, `unique`, and `accepted_values` tests for the new analytics tables (see `models/schema.yml`).
- **Run Commands (run from `transformations` directory):**
  ```bash
  dbt compile --profiles-dir ../config --select analytics+
  dbt test    --profiles-dir ../config --select analytics+
  dbt run     --profiles-dir ../config --select analytics+
  ```

## Specification Documents
- **master_plan.md** – outlines the end‑to‑end roadmap from raw extraction to BI.
- **spec_6.md** – defines the analytics layer requirements (daily revenue, customer LTV, churn > 90 days, macro for currency conversion).
- **spec_7.md** – future BI/reporting specifications.

## How to Get Started
1. Install dependencies (`pip install -r extraction/requirements.txt`).
2. Run the extraction scripts to populate `raw/` data.
3. From the `transformations` folder, execute the dbt commands above.
4. Verify the analytics tables exist in DuckDB (`SELECT * FROM analytics_revenue_daily LIMIT 5;`).

---
*This file provides a quick reference for anyone onboarding to the project or needing an overview of its structure and current state.*
