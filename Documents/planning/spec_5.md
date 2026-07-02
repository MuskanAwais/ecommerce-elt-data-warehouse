# Module 5: Data Modeling (Spec 5)

## 1. Concept & Goal
**Concept:** Transform the raw staging tables into a structured Dimensional Model (Star Schema).
**Goal:** Create clean, highly optimized tables (Facts and Dimensions) that support complex business analytics, ensuring data integrity through primary/foreign key relationships.

## 2. Workflow
1. dbt reads the staging tables (`stg_*`).
2. Dimension models apply data cleaning, renaming, and type casting, generating unique surrogate keys.
3. Fact models aggregate transactional data and join to the dimensions using the surrogate keys.
4. dbt tests are run to guarantee uniqueness and non-null constraints.

## 3. Architecture
- **Framework:** dbt (Data Build Tool)
- **Architecture Pattern:** Kimball Dimensional Modeling (Star Schema)

## 4. Database Design
- **Dimensions:**
  - `dim_customers`: customer_id, name, email, demographic data.
  - `dim_products`: product_id, title, category, price.
- **Facts:**
  - `fct_orders`: order_id, customer_id (FK), product_id (FK), quantity, total_amount, order_date.

## 5. Implementation Plan
- Create `models/dim/dim_customers.sql` and `models/dim/dim_products.sql`. Use SQL to standardize column names.
- Create `models/fact/fct_orders.sql`. Unnest the JSON arrays from the raw carts payload to flatten the line items into individual fact rows.
- Use the `dbt_utils.generate_surrogate_key()` macro to create consistent ID hashes.
- Create `schema.yml` inside the models folder to define tests: `unique`, `not_null`, and `relationships`.

## 6. Deployment Plan
- **Execution:** Run `dbt run --models dim+ fact+` followed by `dbt test`.

## 7. Git Commit Instructions
```bash
git add dbt_project/models/dim/ dbt_project/models/fact/
git commit -m "feat(models): create star-schema staging, dimension, and fact models"
```
