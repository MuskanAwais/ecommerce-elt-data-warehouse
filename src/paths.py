"""Shared repository path constants."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"

DATA_DIR = REPO_ROOT / "Data"
DATA_RAW = DATA_DIR / "raw"
DATA_PROCESSED = DATA_DIR / "processed"
DATA_WAREHOUSE = DATA_DIR / "warehouse"
WAREHOUSE_DB = DATA_WAREHOUSE / "warehouse.duckdb"

RESULTS_DIR = REPO_ROOT / "results"
RESULTS_LOGS = RESULTS_DIR / "logs"
RESULTS_DBT = RESULTS_DIR / "dbt"

CONFIG_DIR = REPO_ROOT / "config"
DBT_PROJECT_DIR = SRC_ROOT / "transformations"
