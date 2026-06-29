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
- **Python**: Used for writing the extraction scripts that pull data from the API and load it into the raw layer.
- **S3 / Local File System**: Serves as the initial raw layer or data lake to store untransformed data.
- **DuckDB**: A fast, in-process analytical database used as the target data warehouse for simple, localized querying and processing.
- **dbt (data build tool)**: Handles the "Transform" step by converting raw data into business-ready tables using SQL, Jinja templating, and built-in testing.
- **PostgreSQL (Optional Target)**: Can be used as a traditional relational data warehouse alternative to DuckDB.

## 4. Project Architecture
The data flows through a modern ELT architecture:

**Mock API → Raw Layer → DuckDB → dbt Transformations → Analytics Tables**

- **Mock API**: The source system generating raw customer, product, and order records.
- **Raw Layer (S3/Local)**: Acts as the landing zone where data is stored exactly as it was extracted.
- **DuckDB**: Ingests the raw data to provide a query engine for the warehouse.
- **dbt Transformations**: Takes data from staging tables and builds clean fact and dimension tables using SQL.
- **Analytics Tables (Semantic Layer)**: The final, optimized tables ready to be connected to a BI tool for creating dashboards.

## 5. Project Structure
```text
ecommerce-elt-data-warehouse/
├── .planning/           # Project plans, roadmaps, and architectural documentation
├── config/              # Configuration files (API keys, database credentials)
├── data/
│   ├── raw/             # Extracted JSON/CSV files from the API
│   ├── processed/       # Intermediate data files
│   └── warehouse/       # DuckDB database files
├── dbt_project/         # dbt models, macros, and tests for data transformation
├── docs/                # Project documentation and setup instructions
├── extraction/          # Python scripts for API extraction and loading to raw layer
├── logs/                # Execution logs for the pipeline
├── notebooks/           # Jupyter notebooks for data exploration and prototyping
├── tests/               # Python unit tests for extraction scripts
└── README.md            # Main entry point explaining the project
```

## 6. Database Design
The warehouse follows a dimensional modeling approach (Star Schema):

- **Source Tables**: The raw, unstructured data landed straight from the API.
- **Staging Tables (stg_)**: Cleaned versions of the source tables (e.g., standardized column names, correct data types).
- **Dimension Tables (dim_)**: Descriptive data that provides context.
  - `dim_customers`: Customer details and demographics.
  - `dim_products`: Product catalog, categories, and pricing.
- **Fact Table (fct_)**: Measurable, quantitative data.
  - `fct_orders`: The core transaction table containing order amounts, dates, and foreign keys linking to customers and products.

## 7. Development Roadmap

### Phase 1: Planning and Setup
- **Objective**: Establish the project foundation and architecture.
- **Tasks**: Create this Master Plan, initialize the GitHub repository, set up the folder structure, and define the mock API endpoints.
- **Expected Output**: A structured repository ready for code, along with a documented plan.

### Phase 2: Data Extraction (Extract & Load)
- **Objective**: Ingest data from the source.
- **Tasks**: Write Python scripts to connect to the mock REST API, retrieve data, and save it as raw files in the `data/raw/` directory.
- **Expected Output**: Python modules in `extraction/` and raw data files successfully landed.

### Phase 3: Data Warehousing (Load to DB)
- **Objective**: Move raw data into the query engine.
- **Tasks**: Load the raw files into DuckDB tables (the base layer).
- **Expected Output**: A populated DuckDB database with raw source tables.

### Phase 4: Data Transformation (dbt)
- **Objective**: Build the business logic and dimensional model.
- **Tasks**: Initialize dbt, configure the DuckDB connection, write staging models, and build the final fact and dimension tables using SQL and CTEs.
- **Expected Output**: A compiled dbt project that successfully builds the `fct_orders`, `dim_customers`, and `dim_products` tables.

### Phase 5: Testing and Documentation
- **Objective**: Ensure data quality and pipeline reliability.
- **Tasks**: Add dbt tests (unique, not_null, accepted_values) to models, write Python unit tests for API scripts, and generate dbt documentation.
- **Expected Output**: A fully tested pipeline and a compiled data dictionary (dbt docs).

## 8. Business Metrics
The final analytics layer will empower the calculation of critical business KPIs:
- **Total Revenue**: Calculated from `fct_orders`. Useful for tracking business growth.
- **Average Order Value (AOV)**: Revenue divided by order count. Highlights customer purchasing behavior.
- **Active Customers**: Count of unique customers placing orders in a given timeframe.
- **Revenue by Category**: Joining `fct_orders` with `dim_products` to see which product lines are most profitable.

## 9. Testing Strategy
- **Python Testing**: Using `pytest` to test the API extraction logic (e.g., handling failed API calls, ensuring JSON parses correctly).
- **dbt Testing**: Using native dbt tests to enforce data integrity at the database level. We will check that primary keys are unique, amounts are never negative, and foreign keys match existing records.

## 10. Deployment Strategy
- **Local Execution**: The project will be executable locally using standard commands (e.g., `python extract.py` followed by `dbt run`).
- **Containerization (Docker)**: The pipeline can be packaged into a Docker container, ensuring it runs consistently on any machine without complex local environment setup.
- **Automation (GitHub Actions)**: In the future, a CI/CD pipeline could be implemented using GitHub Actions to automatically run Python tests and dbt models whenever new code is pushed.

## 11. Future Improvements
- **Data Visualization**: Connect a free BI tool (like Metabase or Preset) directly to DuckDB to build a visual dashboard.
- **Incremental Loading**: Upgrade dbt models from full-refresh to incremental builds to handle larger datasets efficiently.
- **Orchestration**: Introduce a lightweight orchestrator like Mage, Dagster, or Prefect to schedule the pipeline runs.

## 12. Final Deliverables
Upon completion, the project will include:
1. `extraction/` codebase for the API ingestion.
2. A functioning `dbt_project/` with staging, fact, and dimension models.
3. A populated DuckDB database containing the transformed analytics tables.
4. Comprehensive `pytest` and `dbt` test suites.
5. A clear Architecture Diagram (e.g., created via Draw.io or Excalidraw).
6. A detailed `README.md` explaining how to set up and run the project from scratch.

## 13. Coding Standards & Conventions
- **Style** — PEP 8 for Python; dbt model files use lowercase `snake_case`.
- **Naming** — Files: `snake_case.py`; database objects: `snake_case`; Jinja macros: `snake_case`.
- **Docstrings** — Triple-quoted, include purpose, args, and returns.
- **Commit Messages** — Follow Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`.
