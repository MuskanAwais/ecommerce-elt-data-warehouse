# Module 7: Business Analytics Serving (Spec 7)

## 1. Concept & Goal
**Concept:** Export or serve the final analytics metrics to end-users, BI platforms, or a traditional relational database like PostgreSQL.
**Goal:** Allow non-technical business users and BI tools (Tableau, Metabase, PowerBI) to query the finalized KPIs easily, bridging the gap between the Data Warehouse and business reporting.

## 2. Workflow
1. Business users query the data using standard SQL scripts.
2. (Optional Workflow) A Python sync script extracts the aggregated tables from DuckDB/Redshift and pushes them to a PostgreSQL instance.
3. BI tools connect to PostgreSQL to read the data.

## 3. Architecture
- **Query Engine:** DuckDB CLI or Jupyter Notebooks.
- **Serving Layer Database:** PostgreSQL (Optional Data Mart target).

## 4. Database Design
- The PostgreSQL schema will exactly mirror the tables generated in Module 6 (e.g., `analytics_revenue_daily`, `analytics_customer_metrics`).

## 5. Implementation Plan
- Create `sql/reports/revenue_report.sql` and `churn_report.sql` demonstrating how an analyst would write standard SQL against the warehouse.
- (If deploying Postgres sync): Create `scripts/sync_to_postgres.py`.
  - Connect to DuckDB.
  - Read `analytics_*` tables into Pandas DataFrames or use raw SQL.
  - Connect to PostgreSQL using `SQLAlchemy` or `psycopg2`.
  - Write the DataFrames to Postgres using `df.to_sql()`.

## 6. Deployment Plan
- **Execution:** Analysts can run the SQL scripts directly in DuckDB IDEs (like DBeaver). The Python sync script can be scheduled via Airflow or Cron to run daily after the dbt pipeline finishes.

## 7. Git Commit Instructions
```bash
git add sql/ scripts/
git commit -m "feat(analytics): add sample reporting queries and Postgres serving sync"
```
