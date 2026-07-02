"""
Module 4: Load raw JSON files into DuckDB staging tables.

Workflow:
  1. Scan Data/raw/<entity>/YYYY/MM/DD/*.json recursively.
  2. Use DuckDB's READ_JSON_AUTO to infer schema from each JSON file.
  3. Create staging tables (stg_customers, stg_products, stg_orders).
  4. Append data from all JSON files into the corresponding staging table.
  5. Log row counts and data quality metrics.

Run:
    python -m scripts.load_raw          (from src/)
    python src/scripts/load_raw.py
"""

import json
import logging
import pathlib
import sys
from typing import Optional

import duckdb

from paths import DATA_RAW, DATA_WAREHOUSE, RESULTS_LOGS, WAREHOUSE_DB

# ─────────────────────────────────────────────
# PATHS & SETUP
# ─────────────────────────────────────────────
DATA_RAW_ROOT = DATA_RAW
DATA_WAREHOUSE_ROOT = DATA_WAREHOUSE
LOG_PATH = RESULTS_LOGS / "load_raw.log"

# Create necessary directories
DATA_WAREHOUSE_ROOT.mkdir(parents=True, exist_ok=True)
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# DATABASE CONNECTION
# ─────────────────────────────────────────────
DB_PATH = WAREHOUSE_DB


def get_db_connection() -> duckdb.DuckDBPyConnection:
    """
    Create or connect to the DuckDB warehouse database.
    
    Returns:
        A DuckDB connection object.
    """
    logger.info("[DB] Connecting to DuckDB at %s", DB_PATH)
    conn = duckdb.connect(str(DB_PATH), read_only=False)
    logger.info("[DB] Connection established")
    return conn


def get_json_files(entity: str) -> list[pathlib.Path]:
    """
    Recursively find all JSON files for a given entity.
    
    Args:
        entity: Entity name (customers / products / orders).
    
    Returns:
        List of pathlib.Path objects for each JSON file found.
    """
    entity_root = DATA_RAW_ROOT / entity
    
    if not entity_root.exists():
        logger.warning("[SCAN] Entity folder does not exist: %s", entity_root)
        return []
    
    json_files = sorted(entity_root.glob("**/*.json"))
    logger.info("[SCAN] Found %d JSON files for %s", len(json_files), entity)
    
    return json_files


def infer_table_name(entity: str) -> str:
    """Map entity name to staging table name."""
    mapping = {
        "customers": "stg_customers",
        "products":  "stg_products",
        "orders":    "stg_orders",
    }
    return mapping.get(entity, f"stg_{entity}")


def load_json_file(
    conn: duckdb.DuckDBPyConnection,
    json_path: pathlib.Path,
    table_name: str,
    entity: str,
) -> Optional[int]:
    """
    Load a single JSON file into the staging table.
    
    DuckDB's READ_JSON_AUTO automatically infers the schema.
    If the table does not exist, it is created on first insert.
    
    Args:
        conn:       DuckDB connection.
        json_path:  Path to the JSON file.
        table_name: Target staging table name.
        entity:     Entity name (for logging).
    
    Returns:
        Number of rows inserted, or None if an error occurred.
    """
    try:
        # Read JSON file and check row count first
        with open(json_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        
        # Extract the entity array (handle DummyJSON API structure)
        # DummyJSON returns:
        # - /products → {"products": [...]}
        # - /users → {"users": [...]}
        # - /carts → {"carts": [...]}
        if isinstance(raw_data, dict):
            # Map entity names to their JSON keys
            key_mapping = {
                "customers": "users",
                "products": "products",
                "orders": "carts",
            }
            json_key = key_mapping.get(entity, entity)
            records = raw_data.get(json_key, [])
            if not isinstance(records, list):
                records = [records]
        elif isinstance(raw_data, list):
            records = raw_data
        else:
            logger.warning("[LOAD] Unexpected JSON structure in %s", json_path)
            return None
        
        if not records:
            logger.info("[LOAD] No records in %s", json_path.name)
            return 0
        
        # Insert into DuckDB
        conn.execute(
            f"""
            INSERT INTO {table_name} 
            SELECT * FROM read_json_auto(?)
            """,
            [str(json_path)],
        )
        
        row_count = len(records)
        logger.info(
            "[LOAD] ✓ %s → %s (%d rows)",
            json_path.name,
            table_name,
            row_count,
        )
        return row_count
    
    except Exception as exc:
        logger.error("[LOAD] Failed to load %s: %s", json_path, exc)
        return None


def create_staging_table_if_needed(
    conn: duckdb.DuckDBPyConnection,
    table_name: str,
    entity: str,
) -> bool:
    """
    Check if a staging table exists; if not, create an empty table
    with an inferred schema from the first JSON file.
    
    Args:
        conn:       DuckDB connection.
        table_name: Staging table name.
        entity:     Entity name (customers / products / orders).
    
    Returns:
        True if table was created or already exists; False if no JSON files found.
    """
    # Check if table exists
    result = conn.execute(
        f"SELECT table_name FROM information_schema.tables WHERE table_name = '{table_name}'"
    ).fetchall()
    
    if result:
        logger.info("[TABLE] Table %s already exists", table_name)
        return True
    
    # Find first JSON file to infer schema
    json_files = get_json_files(entity)
    if not json_files:
        logger.warning("[TABLE] No JSON files found for %s; skipping table creation", entity)
        return False
    
    # Use first JSON file to infer schema and create table
    first_json = json_files[0]
    logger.info("[TABLE] Creating %s using schema from %s", table_name, first_json.name)
    
    try:
        conn.execute(
            f"""
            CREATE TABLE {table_name} AS
            SELECT * FROM read_json_auto(?) LIMIT 0
            """,
            [str(first_json)],
        )
        logger.info("[TABLE] ✓ Table %s created", table_name)
        return True
    except Exception as exc:
        logger.error("[TABLE] Failed to create %s: %s", table_name, exc)
        return False


def load_entity_data(
    conn: duckdb.DuckDBPyConnection,
    entity: str,
) -> int:
    """
    Load all JSON files for a given entity into its staging table.
    
    Args:
        conn:   DuckDB connection.
        entity: Entity name (customers / products / orders).
    
    Returns:
        Total number of rows loaded.
    """
    table_name = infer_table_name(entity)
    json_files = get_json_files(entity)
    
    if not json_files:
        logger.warning("[ENTITY] No JSON files found for %s", entity)
        return 0
    
    # Create table if needed
    if not create_staging_table_if_needed(conn, table_name, entity):
        return 0
    
    # Load each JSON file
    total_rows = 0
    for json_path in json_files:
        row_count = load_json_file(conn, json_path, table_name, entity)
        if row_count is not None:
            total_rows += row_count
    
    return total_rows


def validate_data_quality(conn: duckdb.DuckDBPyConnection) -> None:
    """
    Run basic data quality checks on all staging tables.
    
    Args:
        conn: DuckDB connection.
    """
    logger.info("=" * 60)
    logger.info("DATA QUALITY CHECKS")
    logger.info("=" * 60)
    
    tables = ["stg_customers", "stg_products", "stg_orders"]
    
    for table_name in tables:
        try:
            # Check if table exists
            result = conn.execute(
                f"SELECT COUNT(*) as row_count FROM {table_name}"
            ).fetchall()
            
            if result:
                row_count = result[0][0]
                logger.info("[DQ] %s: %d rows", table_name, row_count)
            else:
                logger.warning("[DQ] %s: Table not found", table_name)
        except Exception as exc:
            logger.warning("[DQ] %s: %s", table_name, exc)
    
    logger.info("=" * 60)


def main() -> None:
    """
    Main pipeline: load all raw JSON files into DuckDB staging tables.
    """
    logger.info("=" * 60)
    logger.info("Module 4: Raw Data Loading → DuckDB")
    logger.info("=" * 60)
    
    try:
        conn = get_db_connection()
        
        # Load each entity
        entities = ["customers", "products", "orders"]
        total_loaded = 0
        
        for entity in entities:
            logger.info("")
            logger.info("[ENTITY] Loading %s...", entity)
            rows = load_entity_data(conn, entity)
            total_loaded += rows
            logger.info("[ENTITY] Total for %s: %d rows", entity, rows)
        
        # Validate data quality
        logger.info("")
        validate_data_quality(conn)
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("✓ Pipeline complete — Total rows loaded: %d", total_loaded)
        logger.info("=" * 60)
        
        conn.close()
    
    except Exception as exc:
        logger.error("=" * 60)
        logger.error("✗ Pipeline failed: %s", exc)
        logger.error("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
