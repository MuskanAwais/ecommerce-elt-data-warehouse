# Module 6: dbt Transformations (Spec 6)

## 1. Concept & Goal
**Concept:** Build the Business Analytics layer on top of the Dimensional Model using advanced SQL logic.
**Goal:** Provide pre-calculated, reusable, and version-controlled SQL logic for key business metrics like Total Revenue, Month-to-Date (MTD) Revenue, and Customer Churn.

## 2. Workflow
1. dbt reads from the `fct_orders` and dimension tables.
2. Advanced SQL (Window functions, CTEs) computes business aggregations.
3. The results are materialized as tables or views in the Data Warehouse.

## 3. Architecture
- **Layer:** Semantic / Analytics Layer (Data Marts)
- **Compute:** DuckDB / Redshift via dbt SQL.

## 4. Database Design
- `analytics_revenue_daily`: Aggregates total sales per day.
- `analytics_customer_metrics`: Lifetime value (LTV), total orders per customer, and churn status (e.g., no orders in >90 days).

## 5. Implementation Plan
- Create `models/analytics/` directory.
- Write `revenue_metrics.sql`:
  ```sql
  SELECT 
      DATE_TRUNC('day', order_date) as report_date,
      SUM(total_amount) as daily_revenue
  FROM {{ ref('fct_orders') }}
  GROUP BY 1
  ```
- Write `customer_churn.sql` utilizing window functions to determine the days since the customer's last order.
- Define custom Jinja macros (e.g., `macros/cents_to_dollars.sql`) if currency conversions are necessary.
- Add robust tests for these analytics tables in `schema.yml`.

## 6. Deployment Plan
- **Execution:** Run `dbt run --models analytics+`.

## 7. Git Commit Instructions
```bash
git add dbt_project/models/analytics/ dbt_project/macros/
git commit -m "feat(analytics): add revenue & churn models with tests"
```
