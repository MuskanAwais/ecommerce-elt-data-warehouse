# Module 4: Data Loading (Spec 4)

## 1. Concept & Goal
**Concept:** Load the raw JSON files from the S3 data lake into a queryable data warehouse (DuckDB for local development, Redshift for production).
**Goal:** Transition the data from unstructured JSON in cloud storage into relational database tables (the "Staging Layer") automatically via dbt, eliminating the need for manual loading scripts.

## 2. Workflow
1. Initialize the dbt project.
2. Configure dbt to connect to the target database (DuckDB).
3. DuckDB utilizes the `httpfs` extension to read JSON files directly from S3.
4. dbt executes SQL to `CREATE TABLE ... AS SELECT ...` from the S3 paths.

## 3. Architecture
- **Source:** AWS S3 (`s3://.../*.json`)
- **Compute/Transform Engine:** dbt (Data Build Tool)
- **Data Warehouse Target:** DuckDB (stored locally as `data/warehouse/warehouse.duckdb`)

## 4. Database Design
This module creates the **Staging Layer**.
- `stg_products`: 1:1 mapped to raw product JSON.
- `stg_customers`: 1:1 mapped to raw user JSON.
- `stg_orders`: 1:1 mapped to raw cart JSON.

## 5. Implementation Plan
- Run `dbt init dbt_project` to scaffold the dbt environment.
- Update `profiles.yml` to set up the DuckDB connection pointing to `data/warehouse/warehouse.duckdb`.
- Install DuckDB's `httpfs` and `aws` extensions if required.
- Write `models/staging/stg_products.sql` containing:
  ```sql
  SELECT * FROM read_json_auto('s3://<bucket-name>/raw/products/**/*.json')
  ```
- Repeat for customers and orders.

## 6. Deployment Plan
- **Execution:** Run `dbt run --models staging` via terminal. 
- In a production environment, this dbt command would be triggered by an orchestrator right after the extraction script completes.

## 7. Git Commit Instructions
```bash
git add dbt_project/
git commit -m "feat(warehouse): add staging load logic from S3 via dbt (DuckDB/Redshift)"
```
