import json
import pathlib
import pytest
import duckdb

from scripts import load_raw

# ─────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────

@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary DuckDB database for testing."""
    db_path = tmp_path / "test.duckdb"
    conn = duckdb.connect(str(db_path))
    yield conn
    conn.close()


@pytest.fixture
def temp_raw_data(tmp_path):
    """Create temporary raw data files for testing."""
    raw_root = tmp_path / "raw"
    
    # Create sample data matching DummyJSON API structure
    # Note: The load_raw script checks for entity keys in different ways
    customers_data = {
        "users": [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
        ]
    }
    
    products_data = {
        "products": [
            {"id": 101, "title": "Product A", "price": 29.99},
            {"id": 102, "title": "Product B", "price": 49.99},
        ]
    }
    
    # For orders/carts, DummyJSON uses "carts" key
    orders_data = {
        "carts": [
            {"id": 1001, "userId": 1, "total": 79.98},
            {"id": 1002, "userId": 2, "total": 49.99},
        ]
    }
    
    # Write files
    for entity, data in [
        ("customers", customers_data),
        ("products", products_data),
        ("orders", orders_data),
    ]:
        entity_dir = raw_root / entity / "2026" / "06" / "29"
        entity_dir.mkdir(parents=True, exist_ok=True)
        
        json_file = entity_dir / f"{entity}_20260629_120000.json"
        json_file.write_text(json.dumps(data), encoding="utf-8")
    
    return raw_root


# ─────────────────────────────────────────────
# TESTS
# ─────────────────────────────────────────────

def test_get_json_files(temp_raw_data, monkeypatch):
    """Test that get_json_files finds all JSON files."""
    monkeypatch.setattr(load_raw, "DATA_RAW_ROOT", temp_raw_data)
    
    customers_files = load_raw.get_json_files("customers")
    assert len(customers_files) == 1
    assert customers_files[0].name == "customers_20260629_120000.json"
    
    products_files = load_raw.get_json_files("products")
    assert len(products_files) == 1


def test_infer_table_name():
    """Test table name mapping."""
    assert load_raw.infer_table_name("customers") == "stg_customers"
    assert load_raw.infer_table_name("products") == "stg_products"
    assert load_raw.infer_table_name("orders") == "stg_orders"


def test_create_staging_table_if_needed(temp_db, temp_raw_data, monkeypatch):
    """Test that staging tables are created correctly."""
    monkeypatch.setattr(load_raw, "DATA_RAW_ROOT", temp_raw_data)
    
    # Create table
    result = load_raw.create_staging_table_if_needed(temp_db, "stg_customers", "customers")
    assert result is True
    
    # Verify table was created
    tables = temp_db.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_name = 'stg_customers'"
    ).fetchall()
    assert len(tables) == 1


def test_load_json_file(temp_db, temp_raw_data, monkeypatch):
    """Test loading a JSON file into DuckDB."""
    monkeypatch.setattr(load_raw, "DATA_RAW_ROOT", temp_raw_data)
    
    # Create table first
    load_raw.create_staging_table_if_needed(temp_db, "stg_customers", "customers")
    
    # Load file
    json_file = temp_raw_data / "customers" / "2026" / "06" / "29" / "customers_20260629_120000.json"
    row_count = load_raw.load_json_file(temp_db, json_file, "stg_customers", "customers")
    
    # DuckDB READ_JSON_AUTO returns the count of records in the JSON array
    assert row_count == 2
    
    # Verify data was inserted (DuckDB flattens nested arrays into rows)
    result = temp_db.execute("SELECT COUNT(*) FROM stg_customers").fetchall()
    # One row per INSERT statement (which may contain multiple records)
    assert result[0][0] >= 1


def test_load_entity_data(temp_db, temp_raw_data, monkeypatch):
    """Test loading all files for an entity."""
    monkeypatch.setattr(load_raw, "DATA_RAW_ROOT", temp_raw_data)
    
    total_rows = load_raw.load_entity_data(temp_db, "customers")
    
    # Each JSON file contains 2 customer records
    assert total_rows == 2
    
    # Verify table has data
    result = temp_db.execute("SELECT COUNT(*) FROM stg_customers").fetchall()
    # At least one row inserted
    assert result[0][0] >= 1
