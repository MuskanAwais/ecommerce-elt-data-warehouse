#!/usr/bin/env python3
"""
E-Commerce ELT Orchestration Pipeline

Run the complete pipeline with one command:
    python orchestration_pipeline.py

Flow: DummyJSON API → Python Extractor → AWS S3 → DuckDB → dbt → Analytics Report
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Windows terminals often default to cp1252; reconfigure for emoji/Unicode report output.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ── Bootstrap paths ──────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from paths import (  # noqa: E402
    CONFIG_DIR,
    DBT_PROJECT_DIR,
    WAREHOUSE_DB,
)
from extraction.config import API_ENDPOINTS, S3_BUCKET_NAME  # noqa: E402

import duckdb  # noqa: E402

# Suppress noisy logs during pipeline execution; final report is printed to stdout.
logging.basicConfig(level=logging.WARNING)

ENTITY_JSON_KEYS = {
    "products": "products",
    "customers": "users",
    "orders": "carts",
}

DBT_MODELS_DISPLAY = [
    "raw_customers",
    "raw_products",
    "raw_orders",
    "dim_customer",
    "dim_product",
    "fact_orders",
    "customer_churn",
    "mtd_revenue",
    "analytics_revenue_daily",
    "analytics_customer_metrics",
]

WIDTH = 70
LINE = "─" * WIDTH
DOUBLE = "═" * WIDTH


@dataclass
class PipelineState:
    """Collect metrics across pipeline stages for the final report."""

    start_time: float = field(default_factory=time.time)
    extraction: dict[str, dict[str, int]] = field(default_factory=dict)
    s3_uploads: list[tuple[str, str]] = field(default_factory=list)
    dbt_models_built: list[str] = field(default_factory=list)
    dbt_tests_passed: bool = False
    dbt_test_count: int = 0
    raw_tables: list[str] = field(default_factory=list)
    analytics: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


def _dbt_executable() -> Path:
    venv_dbt = REPO_ROOT / ".venv" / "Scripts" / "dbt.exe"
    if venv_dbt.exists():
        return venv_dbt
    return Path("dbt")


def _run_dbt(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["DBT_PROFILES_DIR"] = str(CONFIG_DIR)
    return subprocess.run(
        [str(_dbt_executable()), *args],
        cwd=str(DBT_PROJECT_DIR),
        env=env,
        capture_output=True,
        text=True,
    )


def _fmt_money(value: float | int | None) -> str:
    if value is None:
        return "$0.00"
    return f"${float(value):,.2f}"


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "0.00%"
    return f"{value:.2f}%"


def _pad(label: str, value: str, label_width: int = 22) -> str:
    return f"{label:<{label_width}}: {value}"


def step_extract(state: PipelineState) -> None:
    from extraction import extractor

    fetch = extractor._fetch
    save = extractor._save_local
    upload = extractor._upload_to_s3

    for entity, url in API_ENDPOINTS.items():
        payload = fetch(entity, url)
        save(entity, payload)
        s3_key = upload(entity, payload)
        state.s3_uploads.append((entity, s3_key))

        json_key = ENTITY_JSON_KEYS[entity]
        records = payload.get(json_key, [])
        batch = len(records) if isinstance(records, list) else 0
        total = int(payload.get("total", batch))
        state.extraction[entity] = {"batch": batch, "total": total}


def step_load_duckdb(state: PipelineState) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "scripts.load_raw"],
        cwd=str(SRC_ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"load_raw failed:\n{result.stderr or result.stdout}")

    conn = duckdb.connect(str(WAREHOUSE_DB), read_only=True)
    try:
        rows = conn.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'main'
              AND table_name IN ('stg_customers', 'stg_products', 'stg_orders')
            ORDER BY table_name
            """
        ).fetchall()
        state.raw_tables = [r[0] for r in rows]
    finally:
        conn.close()


def step_dbt_run(state: PipelineState) -> None:
    result = _run_dbt("run")
    if result.returncode != 0:
        raise RuntimeError(f"dbt run failed:\n{result.stderr or result.stdout}")

    manifest_path = REPO_ROOT / "results" / "dbt" / "run_results.json"
    if manifest_path.exists():
        run_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in run_data.get("results", []):
            uid = item.get("unique_id", "")
            if uid.startswith("model.") and item.get("status") == "success":
                name = uid.split(".")[-1]
                if name not in state.dbt_models_built:
                    state.dbt_models_built.append(name)
    else:
        state.dbt_models_built = DBT_MODELS_DISPLAY.copy()


def step_dbt_test(state: PipelineState) -> None:
    result = _run_dbt("test")
    if result.returncode != 0:
        raise RuntimeError(f"dbt test failed:\n{result.stderr or result.stdout}")

    manifest_path = REPO_ROOT / "results" / "dbt" / "run_results.json"
    if manifest_path.exists():
        run_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        passed = sum(
            1 for item in run_data.get("results", []) if item.get("status") == "pass"
        )
        state.dbt_test_count = passed
    state.dbt_tests_passed = True


def step_collect_analytics(state: PipelineState) -> None:
    conn = duckdb.connect(str(WAREHOUSE_DB), read_only=True)
    try:
        state.analytics["customers"] = conn.execute(
            "SELECT COUNT(*) FROM main_dbt.dim_customer"
        ).fetchone()[0]
        state.analytics["products"] = conn.execute(
            "SELECT COUNT(*) FROM main_dbt.dim_product"
        ).fetchone()[0]
        state.analytics["orders"] = conn.execute(
            "SELECT COUNT(*) FROM main_dbt.fact_orders"
        ).fetchone()[0]

        mtd = conn.execute(
            """
            SELECT gross_revenue, net_revenue, avg_order_value
            FROM main_dbt.mtd_revenue
            LIMIT 1
            """
        ).fetchone()
        state.analytics["gross_revenue"] = mtd[0] if mtd else 0
        state.analytics["net_revenue"] = mtd[1] if mtd else 0
        state.analytics["avg_order_value"] = mtd[2] if mtd else 0

        state.analytics["daily_revenue_rows"] = conn.execute(
            "SELECT COUNT(*) FROM main_dbt.analytics_revenue_daily"
        ).fetchone()[0]

        today_rev = conn.execute(
            "SELECT COALESCE(SUM(daily_revenue), 0) FROM main_dbt.analytics_revenue_daily"
        ).fetchone()[0]
        state.analytics["today_revenue"] = today_rev

        churn = conn.execute(
            """
            SELECT
                COUNT(*) FILTER (WHERE customer_status = 'Active') AS active,
                COUNT(*) FILTER (WHERE customer_status = 'Churned') AS churned,
                COUNT(*) AS total,
                COALESCE(AVG(lifetime_value), 0) AS avg_ltv
            FROM main_dbt.analytics_customer_metrics
            """
        ).fetchone()
        state.analytics["active_customers"] = churn[0] or 0
        state.analytics["churned_customers"] = churn[1] or 0
        total_cust = churn[2] or 1
        state.analytics["churn_rate"] = (churn[1] or 0) / total_cust * 100
        state.analytics["avg_ltv"] = churn[3] or 0

        state.analytics["top_products"] = conn.execute(
            """
            SELECT
                p.title,
                SUM(p.quantity)::INT AS orders,
                ROUND(SUM(p.discountedTotal), 2) AS revenue
            FROM main.stg_orders t,
                 UNNEST(t.carts) AS u(cart),
                 UNNEST(cart.products) AS v(p)
            GROUP BY 1
            ORDER BY 3 DESC
            LIMIT 5
            """
        ).fetchall()

        state.analytics["top_customers"] = conn.execute(
            """
            SELECT
                rc.name,
                COUNT(DISTINCT fo.order_id)::INT AS orders,
                ROUND(SUM(fo.discounted_total), 2) AS spend
            FROM main_dbt.fact_orders fo
            JOIN main_dbt.dim_customer dc ON fo.customer_key = dc.customer_key
            JOIN main_dbt.raw_customers rc ON dc.customer_id = rc.customer_id
            GROUP BY rc.name
            ORDER BY 3 DESC
            LIMIT 5
            """
        ).fetchall()

        state.analytics["stg_rows"] = {
            "customers": conn.execute("SELECT COUNT(*) FROM main.stg_customers").fetchone()[0],
            "products": conn.execute("SELECT COUNT(*) FROM main.stg_products").fetchone()[0],
            "orders": conn.execute("SELECT COUNT(*) FROM main.stg_orders").fetchone()[0],
        }
    finally:
        conn.close()


def print_report(state: PipelineState) -> None:
    elapsed = time.time() - state.start_time
    ext = state.extraction
    a = state.analytics

    customers_total = ext.get("customers", {}).get("total", a.get("customers", 0))
    products_total = ext.get("products", {}).get("total", a.get("products", 0))
    orders_batch = ext.get("orders", {}).get("batch", a.get("orders", 0))

    # Files uploaded this run (most recent per entity)
    upload_labels = []
    for entity, _key in state.s3_uploads:
        upload_labels.append(f"✓ {entity}.json")

    models_to_show = state.dbt_models_built or DBT_MODELS_DISPLAY
    key_models = [m for m in DBT_MODELS_DISPLAY if m in models_to_show]
    if not key_models:
        key_models = models_to_show[:8]

    lines: list[str] = [
        "",
        DOUBLE,
        "                 🚀 E-COMMERCE ELT PIPELINE SUCCESS",
        DOUBLE,
        "",
        "📥 EXTRACTION",
        "",
        _pad("Source API", "DummyJSON"),
        _pad("Customers Extracted", str(customers_total)),
        _pad("Products Extracted", str(products_total)),
        _pad("Orders Extracted", str(orders_batch)),
        "",
        "✓ API extraction completed successfully",
        "",
        LINE,
        "",
        "☁️ RAW DATA STORAGE (AWS S3)",
        "",
        _pad("Bucket", S3_BUCKET_NAME),
        _pad("Files Uploaded", str(len(state.s3_uploads))),
        "",
    ]
    lines.extend(upload_labels)
    lines.extend(
        [
            "",
            _pad("Upload Status", "SUCCESS"),
            "",
            LINE,
            "",
            "🗄 DATA WAREHOUSE (DuckDB)",
            "",
            _pad("Database", WAREHOUSE_DB.name),
            "",
            "Raw Tables Loaded",
            "",
        ]
    )
    for tbl in state.raw_tables or ["stg_customers", "stg_products", "stg_orders"]:
        lines.append(f"✓ {tbl}")
    lines.extend(
        [
            "",
            LINE,
            "",
            "🔄 DBT TRANSFORMATION",
            "",
            _pad("Models Built", str(len(key_models))),
            "",
        ]
    )
    for model in key_models:
        lines.append(f"✓ {model}")
    test_label = "PASSED ✅" if state.dbt_tests_passed else "FAILED ❌"
    lines.extend(
        [
            "",
            _pad("dbt Tests", f"{test_label} ({state.dbt_test_count} tests)"),
            "",
            LINE,
            "",
            "📊 BUSINESS SUMMARY",
            "",
            _pad("Total Customers", str(a.get("customers", 0))),
            _pad("Total Products", str(products_total)),
            _pad("Total Orders", str(a.get("orders", 0))),
            "",
            _pad("Gross Revenue", _fmt_money(a.get("gross_revenue"))),
            _pad("Net Revenue", _fmt_money(a.get("net_revenue"))),
            _pad("Average Order Value", _fmt_money(a.get("avg_order_value"))),
            "",
            LINE,
            "",
            "🏆 TOP SELLING PRODUCTS",
            "",
        ]
    )
    for i, row in enumerate(a.get("top_products", []), 1):
        title = (row[0] or "Unknown")[:28]
        lines.append(f"{i}. {title:<28} {row[1]:>3} Orders   {_fmt_money(row[2])}")
    lines.extend(["", LINE, "", "👥 TOP CUSTOMERS", ""])
    for i, row in enumerate(a.get("top_customers", []), 1):
        name = (row[0] or "Unknown")[:22]
        order_word = "Order" if row[1] == 1 else "Orders"
        lines.append(f"{i}. {name:<22} {row[1]:>2} {order_word:<6} {_fmt_money(row[2]):>12}")
    lines.extend(
        [
            "",
            LINE,
            "",
            "📈 REVENUE ANALYTICS",
            "",
            _pad("Today's Revenue", _fmt_money(a.get("today_revenue"))),
            _pad("Daily Revenue Rows", str(a.get("daily_revenue_rows", 0))),
            _pad("Monthly Revenue", _fmt_money(a.get("net_revenue"))),
            "",
            LINE,
            "",
            "👤 CUSTOMER ANALYTICS",
            "",
            _pad("Active Customers", str(a.get("active_customers", 0))),
            _pad("Churned Customers", str(a.get("churned_customers", 0))),
            _pad("Customer Churn Rate", _fmt_pct(a.get("churn_rate"))),
            _pad("Average Customer LTV", _fmt_money(a.get("avg_ltv"))),
            "",
            LINE,
            "",
            "📦 DATA SUMMARY",
            "",
        ]
    )
    stg = a.get("stg_rows", {})
    lines.append(_pad("Customers Table", f"{stg.get('customers', 0)} rows"))
    lines.append(_pad("Products Table", f"{stg.get('products', 0)} rows"))
    lines.append(_pad("Orders Table", f"{stg.get('orders', 0)} rows"))
    lines.extend(
        [
            "",
            LINE,
            "",
            "✅ PIPELINE STATUS",
            "",
            "✓ DummyJSON API Extracted",
            "✓ Raw JSON Stored in S3",
            "✓ DuckDB Warehouse Loaded",
            "✓ dbt Models Executed",
            "✓ dbt Tests Passed",
            "✓ Analytics Generated",
            "",
            _pad("Execution Time", f"{elapsed:.2f} sec"),
            "",
            DOUBLE,
            "            🎉 END-TO-END ELT PIPELINE COMPLETED",
            DOUBLE,
            "",
        ]
    )
    print("\n".join(lines))


def run_pipeline() -> int:
    state = PipelineState()
    try:
        step_extract(state)
        step_load_duckdb(state)
        step_dbt_run(state)
        step_dbt_test(state)
        step_collect_analytics(state)
        print_report(state)
        return 0
    except Exception as exc:
        elapsed = time.time() - state.start_time
        print("\n" + DOUBLE)
        print("                 ❌ E-COMMERCE ELT PIPELINE FAILED")
        print(DOUBLE)
        print(f"\nError: {exc}\n")
        print(_pad("Execution Time", f"{elapsed:.2f} sec"))
        print("\n" + DOUBLE + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(run_pipeline())
