# E-Commerce ELT Project Documentation

## Project overview

This project is a simple E-Commerce ELT pipeline built with Python, DuckDB, and dbt. It extracts ecommerce data from the DummyJSON API, saves the raw data locally, and transforms it into analytics-friendly tables.

The goal is to create a clean, easy-to-follow pipeline that starts with raw JSON data and ends with a DuckDB data warehouse that analysts can query.

## Data source

- The project uses the **DummyJSON API** as the data source.
- DummyJSON provides sample ecommerce data for:
  - `products`
  - `users` (customers)
  - `carts` (orders)
- This is a mock API service, so it is safe to use for learning and development.

## Module-wise breakdown

### Module 1: Project setup

- Set up the repository structure and required files.
- Installed Python dependencies and prepared the environment.
- Created a clean folder layout for raw data, warehouse files, scripts, transformations, and tests.

### Module 2: Data extraction

- Built the extractor to call DummyJSON endpoints.
- Saved raw JSON responses into local folders under `data/raw/`.
- The extractor also uploads the same raw files to S3-style storage.
- This module creates a reproducible raw data layer.

### Module 3: Raw data storage

- Stored the extracted JSON in a date-partitioned layout:
  - `data/raw/<entity>/YYYY/MM/DD/<file>.json`
- This makes it easier to see when the data was collected and to load specific dates.
- The raw layer is the source of truth before any transformation.

### Module 4: DuckDB raw data loading

- Loaded raw JSON files into a DuckDB database.
- Created staging tables inside DuckDB:
  - `stg_products`
  - `stg_orders`
  - `stg_customers`
- Used DuckDB’s JSON reader so the raw files could be converted into table form automatically.
- The DuckDB database file is stored at:
  - `data/warehouse/warehouse.duckdb`

### Module 5: Data modeling with dbt

- Built dbt models to transform the raw staging tables into a star schema.
- Created:
  - staging models to clean and flatten raw data
  - dimension models for products and customers
  - a fact model for orders
  - analytics models for revenue and churn
- Added dbt tests for data quality and model correctness.
- Verified the full pipeline with `dbt run` and `dbt test`.

## Data flow (step-by-step)

1. **Extract**
   - Python code calls DummyJSON API endpoints.
   - Raw JSON data is saved to `data/raw/`.

2. **Load raw files**
   - DuckDB reads the saved JSON files.
   - Data is loaded into staging tables inside `data/warehouse/warehouse.duckdb`.

3. **Transform**
   - dbt reads the staging tables and applies SQL transformations.
   - The project builds dimension and fact tables.

4. **Analyze**
   - The final models are ready for queries and analytics.
   - You can explore the warehouse with DuckDB or use dbt to run reports.

## Where data is stored

- **Raw data** is stored locally in `data/raw/`.
- **Warehouse data** is stored in DuckDB at `data/warehouse/warehouse.duckdb`.
- The test setup also uses S3-style storage with `boto3` and `moto` so the project can mimic uploading to S3 safely.
- In practice, this means:
  - raw files are kept locally for development
  - the warehouse is also local, making it easy to run on any machine

## What DuckDB does

DuckDB is the local data warehouse engine in this project.

- It reads raw JSON files and turns them into tables.
- It stores transformed data in a single file: `warehouse.duckdb`.
- DuckDB makes it easy to run SQL queries quickly without needing a separate database server.
- It is used together with dbt to build and test the final models.

## Simple explanation for beginners

- Think of this project as a kitchen for data.
- First, the project collects raw ingredients from DummyJSON.
- Then it stores those ingredients in a simple shelf (`data/raw/`).
- Next, DuckDB cooks the ingredients into basic dishes (`staging tables`).
- Finally, dbt assembles the dishes into a full meal (`analytics models`).

This makes it easy to keep raw data separate from cleaned data and to check that everything is working at each step.

## How to use the project

1. Install dependencies.
   - `pip install -r requirements.txt`

2. Run the extractor to get data from DummyJSON.
   - Example: `python extraction/extractor.py`
   - This saves raw JSON files into `data/raw/`.

3. Load the raw JSON into DuckDB.
   - Example: `python scripts/load_raw.py`
   - This builds or updates `data/warehouse/warehouse.duckdb` with staging tables.

4. Run dbt to transform the data.
   - From the project root:
     - `cd transformations`
     - `dbt run --profiles-dir ../config`
   - Then run tests:
     - `dbt test --profiles-dir ../config`

5. Use DuckDB or dbt to query the final tables.
   - Open the warehouse file from `data/warehouse/warehouse.duckdb`.
   - Or use dbt with `dbt docs generate` and `dbt docs serve` if documentation is configured.

That’s the full E-Commerce ELT flow in a beginner-friendly way.