import os
import sys
from pathlib import Path

import duckdb
import psycopg2
from psycopg2.extras import execute_values

SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from paths import WAREHOUSE_DB

# Configuration – replace with your connection details
POSTGRES_DSN = os.getenv("POSTGRES_DSN", "dbname=warehouse user=postgres password=secret host=localhost port=5432")
DUCKDB_PATH = os.getenv("DUCKDB_PATH", str(WAREHOUSE_DB))

# Tables you want to sync (list of dbt model names)
TABLES = ["fact_sales", "dim_customer", "dim_product", "fact_churn"]

def sync_table(conn_duckdb, conn_pg, table_name: str):
    df = conn_duckdb.execute(f"SELECT * FROM {table_name}").fetchdf()
    if df.empty:
        print(f"[WARN] Table {table_name} is empty – skipping")
        return
    # Build insert query
    columns = ", ".join(df.columns)
    values = [tuple(row) for row in df.itertuples(index=False, name=None)]
    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES %s"
    with conn_pg.cursor() as cur:
        execute_values(cur, insert_sql, values)
    conn_pg.commit()
    print(f"[INFO] Synced {len(values)} rows to {table_name}")

def main():
    # Connect to DuckDB (or Redshift – you would need a different driver)
    duck_con = duckdb.connect(database=DUCKDB_PATH, read_only=False)
    # Connect to PostgreSQL
    pg_con = psycopg2.connect(POSTGRES_DSN)

    for tbl in TABLES:
        sync_table(duck_con, pg_con, tbl)

    duck_con.close()
    pg_con.close()

if __name__ == "__main__":
    main()
