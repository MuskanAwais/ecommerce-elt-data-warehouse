# Module 5: dbt Data Modeling and Analytics

## Overview

This module implements the dbt-based data modeling layer for the ecommerce ELT warehouse. It builds a simple star schema from raw staging tables loaded into DuckDB in Module 4.

## What was delivered

- `transformations/models/staging/`
  - `stg_products.sql`
  - `stg_orders.sql`
  - `stg_customers.sql`
- `transformations/models/dim/`
  - `dim_product.sql`
  - `dim_customer.sql`
- `transformations/models/fact/`
  - `fact_orders.sql`
- `transformations/models/analytics/`
  - `mtd_revenue.sql`
  - `customer_churn.sql`
- `transformations/macros/generate_surrogate_key.sql`
- `transformations/models/schema.yml`
- `transformations/models/sources.yml`
- `transformations/dbt_project.yml`
- `config/profiles.yml`

## Architecture

- Raw JSON data is loaded into DuckDB staging tables by Module 4: `stg_products`, `stg_orders`, `stg_customers`
- Staging dbt models unnest the raw JSON arrays into clean row sets
- Dimension models create business entities with surrogate keys
- Fact model joins order data to customer dimension keys
- Analytics models produce business metrics and customer churn analysis

## Key implementation details

- Source definitions use DuckDB schema `main` so dbt can resolve raw tables loaded in Module 4
- Staging models use `{{ source('raw', ...) }}` to avoid recursive self-references
- `generate_surrogate_key` macro creates deterministic surrogate keys based on business keys
- Analytics models use `date_trunc('month', current_date)` for month aggregation and customer lifecycle categorization

## Validation

The following commands were run successfully:

```bash
cd transformations
dbt run --profiles-dir ../config
dbt test --profiles-dir ../config
```

- `dbt run`: 8 of 8 models built successfully
- `dbt test`: 31 of 31 tests passed successfully

## GitHub status

- Committed in this workspace as: `Add dbt star schema models for module 5`
- Pushed to remote branch `main`

## Notes

- `transformations/dbt_project.yml` currently includes warnings for unused config paths (`models.ecommerce_elt.marts` and `seeds.ecommerce_elt`) but these do not block dbt execution.
- The raw DuckDB warehouse file is at `data/warehouse/warehouse.duckdb`.
