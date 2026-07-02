# analytics_report.py – Professional Rich terminal dashboard
"""Analytics dashboard using existing dbt models.

This script:
1. Connects to the DuckDB database used by the dbt project.
2. Discovers analytic models via the dbt ``manifest.json`` (no hard‑coded names).
3. Verifies which tables actually exist in DuckDB.
4. Renders a clean, colour‑rich dashboard with sections:
   • **Sales Summary**
   • **Product Analytics**
   • **Customer Analytics**
   • **Revenue Analytics**
   KPI values are shown as cards (Rich ``Panel``), numbers are formatted
   with commas and two decimal places, and ranking tables are limited to the
   top 5 rows.
5. Falls back to a simple text dashboard when the ``rich`` library is not
   available, ensuring the script always runs.
"""

from orchestrator import console
import time
import pathlib
import json
import logging
from typing import Dict, List
import duckdb

from paths import RESULTS_DBT, WAREHOUSE_DB

# ---------------------------------------------------------------------------
# Optional Rich import – graceful fallback if not installed
# ---------------------------------------------------------------------------
try:
    from rich.console import Console, Group
    from rich.table import Table
    from rich.panel import Panel
    from rich.align import Align
    from rich.layout import Layout
    from rich.text import Text
except ImportError:  # pragma: no cover
    Console = None  # type: ignore
    Group = None  # type: ignore
    Table = None  # type: ignore
    Panel = None  # type: ignore
    Align = None  # type: ignore
    Layout = None  # type: ignore
    Text = None  # type: ignore

# ---------------------------------------------------------------------------
# Logging – debug only
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)-8s %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _load_manifest() -> Dict:
    """Load dbt ``manifest.json`` from the results directory.
    Returns an empty dict on failure.
    """
    manifest_path = RESULTS_DBT / "manifest.json"
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load manifest: {e}")
        return {}


def _discover_analytics_models() -> Dict[str, str]:
    """Map model *alias* → DuckDB table name for all analytics models.
    A model is considered analytics if its path contains ``/analytics/`` or
    it carries an ``analytics`` tag.
    """
    manifest = _load_manifest()
    nodes = manifest.get("nodes", {})
    alias_to_table: Dict[str, str] = {}
    for node in nodes.values():
        if node.get("resource_type") != "model":
            continue
        path = node.get("path", "")
        tags = node.get("tags", [])
        if "analytics" not in path and "analytics" not in tags:
            continue
        alias = node.get("alias") or node.get("name")
        relation = node.get("relation_name", "")
        table_name = relation.split(".")[-1].strip('"')
        alias_to_table[alias] = table_name
    return alias_to_table


def _existing_tables(conn: duckdb.DuckDBPyConnection, tables: List[str]) -> List[str]:
    """Return the subset of ``tables`` that exist in the ``main`` schema."""
    if not tables:
        return []
    placeholders = ", ".join([f"'{t}'" for t in tables])
    sql = (
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema='main' AND table_name IN (" + placeholders + ")"
    )
    rows = conn.execute(sql).fetchall()
    return [r[0] for r in rows]


def _column_names(conn: duckdb.DuckDBPyConnection, table: str) -> List[str]:
    """Return a list of column names for ``table`` using DuckDB pragma."""
    try:
        rows = conn.execute(f"PRAGMA table_info('{table}')").fetchall()
        return [r[1] for r in rows]
    except Exception:
        return []


def _fmt_currency(value) -> str:
    """Format a numeric value as currency with commas and two decimals.
    Returns ``-`` on failure.
    """
    try:
        return f"${float(value):,.2f}"
    except Exception:
        return "-"

# ---------------------------------------------------------------------------
# Rich‑based rendering helpers (no‑op when Rich is missing)
# ---------------------------------------------------------------------------

def _kpi_panel(title: str, value: str, subtitle: str = "") -> Panel:
    txt = Text(value, style="bold green", justify="center")
    if subtitle:
        txt.append("\n" + subtitle, style="dim")
    return Panel(
        Align.center(txt, vertical="middle"),
        title=title,
        border_style="bright_blue",
        padding=(1, 2),
        width=30,
    )

def _section_panel(title: str, renderable) -> Panel:
    return Panel(renderable, title=title, border_style="magenta", padding=(1, 2))

# ---------------------------------------------------------------------------
# Dashboard construction (Rich)
# ---------------------------------------------------------------------------

def _build_rich_dashboard(conn: duckdb.DuckDBPyConnection, alias_to_table: Dict[str, str]):
    """Create a Rich ``Layout`` containing all sections.
    Returns the layout and a dict of *present* tables (alias → table).
    """
    present = _present_tables(alias_to_table, conn)

    # ---------- Sales Summary ----------
    sales_kpis: List[Panel] = []
    if "mtd_revenue" in present.values():
        cols = _column_names(conn, "mtd_revenue")
        if "net_revenue" in cols:
            val = conn.execute("SELECT SUM(net_revenue) FROM mtd_revenue").fetchdf()["sum(net_revenue)"][0]
            sales_kpis.append(_kpi_panel("MTD Net Revenue", _fmt_currency(val)))
        if "gross_revenue" in cols:
            val = conn.execute("SELECT SUM(gross_revenue) FROM mtd_revenue").fetchdf()["sum(gross_revenue)"][0]
            sales_kpis.append(_kpi_panel("MTD Gross Revenue", _fmt_currency(val)))
        if "total_orders" in cols:
            val = conn.execute("SELECT SUM(total_orders) FROM mtd_revenue").fetchdf()["sum(total_orders)"][0]
            sales_kpis.append(_kpi_panel("Orders MTD", f"{int(val):,}"))
        if "unique_customers" in cols:
            val = conn.execute("SELECT SUM(unique_customers) FROM mtd_revenue").fetchdf()["sum(unique_customers)"][0]
            sales_kpis.append(_kpi_panel("Customers MTD", f"{int(val):,}"))

    # ---------- Product Analytics ----------
    product_table = None
    if "fact_orders" in present.values():
        cols = _column_names(conn, "fact_orders")
        if {"product_id", "quantity"}.issubset(set(cols)):
            df = conn.execute(
                "SELECT product_id, SUM(quantity) AS qty FROM fact_orders GROUP BY product_id ORDER BY qty DESC LIMIT 5"
            ).fetchdf()
            table = Table(show_header=True, header_style="bold blue")
            table.add_column("Product ID")
            table.add_column("Qty Sold", justify="right")
            for _, row in df.iterrows():
                table.add_row(str(row["product_id"]), f"{int(row["qty"]):,}")
            product_table = table

    # ---------- Customer Analytics ----------
    customer_kpis: List[Panel] = []
    if "customer_churn" in present.values():
        cols = _column_names(conn, "customer_churn")
        if "last_order_date" in cols:
            # Customers with no order in the last 90 days are considered churned
            val = conn.execute(
                "SELECT ROUND(100.0 * SUM(CASE WHEN (current_date - last_order_date) > 90 THEN 1 ELSE 0 END) / COUNT(*), 2) FROM customer_churn"
            ).fetchdf()[0][0]
            customer_kpis.append(_kpi_panel("Churn Rate (calc)", f"{val}%"))
        elif "customer_status" in cols:
            # Fallback to status‑based churn if the date column is missing
            val = conn.execute(
                "SELECT ROUND(100.0 * SUM(CASE WHEN customer_status = 'Churned' THEN 1 ELSE 0 END) / COUNT(*), 2) FROM customer_churn"
            ).fetchdf()[0][0]
            customer_kpis.append(_kpi_panel("Churn Rate (calc)", f"{val}%"))
    if "analytics_customer_metrics" in present.values():
        cols = _column_names(conn, "analytics_customer_metrics")
        if "lifetime_value" in cols:
            val = conn.execute("SELECT AVG(lifetime_value) FROM analytics_customer_metrics").fetchdf()["avg(lifetime_value)"][0]
            customer_kpis.append(_kpi_panel("Avg LTV", _fmt_currency(val)))

    # ---------- Revenue Analytics ----------
    revenue_kpis: List[Panel] = []
    if "analytics_revenue_daily" in present.values():
        cols = _column_names(conn, "analytics_revenue_daily")
        if "daily_revenue" in cols:
            total = conn.execute("SELECT SUM(daily_revenue) FROM analytics_revenue_daily").fetchdf()["sum(daily_revenue)"][0]
            revenue_kpis.append(_kpi_panel("Total Revenue", _fmt_currency(total)))
            latest = conn.execute(
                "SELECT report_date, daily_revenue FROM analytics_revenue_daily ORDER BY report_date DESC LIMIT 1"
            ).fetchdf()
            date = latest["report_date"][0]
            amount = _fmt_currency(latest["daily_revenue"][0])
            revenue_kpis.append(_kpi_panel("Latest Daily Rev", f"{date}\n{amount}"))

    # ---------- Assemble layout ----------
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body", ratio=1),
        Layout(name="footer", size=3),
    )
    layout["header"].update(Align.center(Text("📊 E‑Commerce Analytics Dashboard", style="bold white on dark_green"), vertical="middle"))

    body = Layout()
    body.split_row(Layout(name="left"), Layout(name="right"))

    left_items = []
    if sales_kpis:
        left_items.append(_section_panel("Sales Summary", Group(*sales_kpis)))
    if revenue_kpis:
        left_items.append(_section_panel("Revenue Analytics", Group(*revenue_kpis)))
    if left_items:
        body["left"].update(Align.center(Panel(Group(*left_items), padding=1)))
    else:
        body["left"].update(Align.center(Text("No Sales/Revenue data", style="dim")))

    right_items = []
    if product_table:
        right_items.append(_section_panel("Product Analytics", product_table))
    if customer_kpis:
        right_items.append(_section_panel("Customer Analytics", Group(*customer_kpis)))
    if right_items:
        body["right"].update(Align.center(Panel(Group(*right_items), padding=1)))
    else:
        body["right"].update(Align.center(Text("No Product/Customer data", style="dim")))

    layout["body"].update(body)
    layout["footer"].update(Align.center(Text("Dashboard rendered", style="green")))
    return layout, present

# ---------------------------------------------------------------------------
# Fallback plain‑text dashboard
# ---------------------------------------------------------------------------

def _fallback_dashboard(conn: duckdb.DuckDBPyConnection, present: Dict[str, str]) -> None:
    print("\n=== E-Commerce Analytics Dashboard (fallback) ===\n")
    # Sales Summary
    if "mtd_revenue" in present.values():
        print("-- Sales Summary --")
        cols = _column_names(conn, "mtd_revenue")
        if "net_revenue" in cols:
            val = conn.execute("SELECT SUM(net_revenue) FROM mtd_revenue").fetchone()[0]
            print(f"MTD Net Revenue: {_fmt_currency(val)}")
        if "gross_revenue" in cols:
            val = conn.execute("SELECT SUM(gross_revenue) FROM mtd_revenue").fetchone()[0]
            print(f"MTD Gross Revenue: {_fmt_currency(val)}")
        if "total_orders" in cols:
            val = conn.execute("SELECT SUM(total_orders) FROM mtd_revenue").fetchone()[0]
            print(f"Orders MTD: {int(val):,}")
        if "unique_customers" in cols:
            val = conn.execute("SELECT SUM(unique_customers) FROM mtd_revenue").fetchone()[0]
            print(f"Customers MTD: {int(val):,}")
        print()
    # Product Analytics
    if "fact_orders" in present.values():
        cols = _column_names(conn, "fact_orders")
        if {"product_id", "quantity"}.issubset(set(cols)):
            print("-- Top 5 Products by Qty Sold --")
            rows = conn.execute(
                "SELECT product_id, SUM(quantity) AS qty FROM fact_orders GROUP BY product_id ORDER BY qty DESC LIMIT 5"
            ).fetchall()
            for pid, qty in rows:
                print(f"Product {pid}: {int(qty):,} sold")
            print()
    # Customer Analytics
    if "customer_churn" in present.values():
        cols = _column_names(conn, "customer_churn")
        print("-- Customer Analytics --")
        if "churn_rate" in cols:
            val = conn.execute("SELECT churn_rate FROM customer_churn LIMIT 1").fetchone()[0]
            print(f"Churn Rate: {float(val)*100:.2f}%")
        elif "customer_status" in cols:
            val = conn.execute(
                "SELECT ROUND(100.0 * SUM(CASE WHEN customer_status = 'Churned' THEN 1 ELSE 0 END) / COUNT(*), 2) FROM customer_churn"
            ).fetchone()[0]
            print(f"Churn Rate (calc): {val}%")
        if "analytics_customer_metrics" in present.values():
            if "lifetime_value" in _column_names(conn, "analytics_customer_metrics"):
                val = conn.execute("SELECT AVG(lifetime_value) FROM analytics_customer_metrics").fetchone()[0]
                print(f"Avg LTV: {_fmt_currency(val)}")
        print()
    # Revenue Analytics
    if "analytics_revenue_daily" in present.values():
        cols = _column_names(conn, "analytics_revenue_daily")
        if "daily_revenue" in cols:
            total = conn.execute("SELECT SUM(daily_revenue) FROM analytics_revenue_daily").fetchone()[0]
            latest = conn.execute(
                "SELECT report_date, daily_revenue FROM analytics_revenue_daily ORDER BY report_date DESC LIMIT 1"
            ).fetchone()
            print("-- Revenue Analytics --")
            print(f"Total Revenue: {_fmt_currency(total)}")
            print(f"Latest ({latest[0]}): {_fmt_currency(latest[1])}")
            print()
    # Summary
    print(f"Reports executed: {len(present)}")

# ---------------------------------------------------------------------------
# Helper to compute which models are present in DuckDB
# ---------------------------------------------------------------------------

def _present_tables(alias_to_table: Dict[str, str], conn: duckdb.DuckDBPyConnection) -> Dict[str, str]:
    all_tables = list(alias_to_table.values())
    existing = _existing_tables(conn, all_tables)
    return {alias: tbl for alias, tbl in alias_to_table.items() if tbl in existing}

# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    start = time.time()
    conn = duckdb.connect(str(WAREHOUSE_DB))

    alias_to_table = _discover_analytics_models()
    if not alias_to_table:
        msg = "No analytics models found in manifest."
        if Console:
            console.print(Panel(msg, style="red"))
        else:
            print(msg)
        return

    present = _present_tables(alias_to_table, conn)

    if Console:
        layout, _ = _build_rich_dashboard(conn, alias_to_table)
        console.print(layout)
    else:
        _fallback_dashboard(conn, present)

    conn.close()
    elapsed = time.time() - start
    # Final summary
    summary_msg = f"Total reports executed: {len(present)}\nExecution time: {elapsed:.2f}s"
    if Console:
        console.print(Panel(summary_msg, title="Report Status", border_style="bright_yellow"))
    else:
        print(summary_msg)

if __name__ == "__main__":
    main()
