# orchestrator.py – Production‑style ELT orchestration
"""Top‑level entry point that orchestrates the full E‑Commerce ELT pipeline.

It re‑uses the existing modules:
* ``extraction.extractor`` – fetches data from the API, saves locally and uploads to S3.
* ``scripts.load_raw``      – loads raw JSON files into DuckDB staging tables.
* ``run_dbt.ps1``          – PowerShell wrapper that forces dbt to use the project‑local
  ``config/profiles.yml`` profile.

The script follows the eight steps described in the task specification and
provides rich, timestamped logging with clear emojis for progress indication.
"""

import sys
import subprocess
import logging
import datetime
from pathlib import Path
from typing import List

SRC_ROOT = Path(__file__).resolve().parent
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from paths import REPO_ROOT, WAREHOUSE_DB

# Optional – colourised output via `rich`
try:
    from rich.console import Console
    console = Console()
except ImportError:  # pragma: no cover
    console = None

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _emoji(icon: str) -> str:
    """Wrap an emoji for console output when Rich is available."""
    return f"{icon} " if console else f"{icon} "

# ---------------------------------------------------------------------------
# STEP 1 – Extraction (fetch, save locally, upload to S3)
# ---------------------------------------------------------------------------

def extract_data() -> None:
    """Run the extraction pipeline defined in ``extraction.extractor``.

    The function logs start/end markers and propagates any exception so the
    orchestrator can abort on failure.
    """
    logger.info(_emoji("▶") + "[STEP 1/8] Extracting data from API …")
    from extraction import extractor
    extractor.main()
    logger.info(_emoji("✓") + "[STEP 1/8] Extraction completed")

# ---------------------------------------------------------------------------
# STEP 4 – Validate S3 upload
# ---------------------------------------------------------------------------

def validate_upload() -> List[str]:
    """Validate that objects uploaded by the extraction step exist in S3.

    Returns a list of the S3 keys that were found – this list is later used for
    the final summary.
    """
    logger.info(_emoji("▶") + "[STEP 4/8] Validating S3 upload …")
    from extraction.config import (
        AWS_REGION,
        AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY,
        S3_BUCKET_NAME,
    )
    import boto3
    s3 = boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID or None,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY or None,
    )
    paginator = s3.get_paginator("list_objects_v2")
    found_keys: List[str] = []
    for page in paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix="raw/"):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            s3.head_object(Bucket=S3_BUCKET_NAME, Key=key)
            found_keys.append(key)
            logger.info(_emoji("✓") + f"Validated s3://{S3_BUCKET_NAME}/{key}")
    if not found_keys:
        raise RuntimeError("No objects found under the 'raw/' prefix in the bucket")
    logger.info(
        _emoji("✓") + f"[STEP 4/8] Validation completed – {len(found_keys)} objects verified"
    )
    return found_keys

# ---------------------------------------------------------------------------
# STEP 5 – Load raw JSON into DuckDB staging tables
# ---------------------------------------------------------------------------

def load_into_duckdb() -> None:
    """Execute ``scripts.load_raw`` which populates DuckDB staging tables."""
    logger.info(_emoji("▶") + "[STEP 5/8] Loading raw JSON into DuckDB …")
    result = subprocess.run(
        [sys.executable, "-m", "scripts.load_raw"],
        cwd=str(SRC_ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.error(_emoji("✗") + "load_raw failed")
        logger.error(result.stderr)
        raise RuntimeError("load_raw script exited with non‑zero status")
    logger.info(_emoji("✓") + "[STEP 5/8] DuckDB staging tables populated")

# ---------------------------------------------------------------------------
# STEP 6 – Run dbt models
# ---------------------------------------------------------------------------

def run_dbt_models() -> None:
    """Run ``dbt deps``, ``dbt seed`` and ``dbt run`` via the PowerShell wrapper."""
    logger.info(_emoji("▶") + "[STEP 6/8] Running dbt models …")
    commands = ["deps", "seed", "run"]
    for cmd in commands:
        logger.info(_emoji("⏳") + f"dbt {cmd}")
        result = subprocess.run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(SRC_ROOT / "run_dbt.ps1"),
                cmd,
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            logger.error(_emoji("✗") + f"dbt {cmd} failed")
            logger.error(result.stderr)
            raise RuntimeError(f"dbt {cmd} exited with non‑zero status")
        logger.info(_emoji("✓") + f"dbt {cmd} succeeded")

# ---------------------------------------------------------------------------
# STEP 7 – Run dbt tests
# ---------------------------------------------------------------------------

def run_dbt_tests() -> None:
    logger.info(_emoji("▶") + "[STEP 7/8] Executing dbt tests …")
    result = subprocess.run(
        [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SRC_ROOT / "run_dbt.ps1"),
            "test",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.error(_emoji("✗") + "dbt test failed")
        logger.error(result.stderr)
        raise RuntimeError("dbt test exited with non‑zero status")
    logger.info(_emoji("✓") + "All dbt tests passed")

# ---------------------------------------------------------------------------
# STEP 8 – Summary
# ---------------------------------------------------------------------------

def print_summary(start_time: datetime.datetime, uploaded_keys: List[str]) -> None:
    elapsed = datetime.datetime.now() - start_time
    logger.info("=" * 60)
    logger.info(_emoji("✅") + "PIPELINE SUMMARY")
    logger.info(f"Status          : SUCCESS")
    logger.info(f"Execution time  : {elapsed.total_seconds():.2f} seconds")
    logger.info(f"Files uploaded  : {len(uploaded_keys)}")
    bucket_name = uploaded_keys[0].split("/")[0] if uploaded_keys else "N/A"
    logger.info(f"S3 bucket       : {bucket_name}")
    logger.info(f"DuckDB file     : {WAREHOUSE_DB.relative_to(REPO_ROOT).as_posix()}")
    logger.info("=" * 60)

# ---------------------------------------------------------------------------
# Main orchestration function
# ---------------------------------------------------------------------------

def main() -> None:
    start = datetime.datetime.now()
    try:
        # 1‑3 – extraction (includes upload to S3)
        extract_data()
        # 4 – validate upload
        uploaded = validate_upload()
        # 5 – load raw JSON into DuckDB staging tables
        load_into_duckdb()
        # 6 – run dbt models
        run_dbt_models()
        # 7 – run dbt tests
        run_dbt_tests()
        # 8 – final summary
        print_summary(start, uploaded)
    except Exception as exc:  # pragma: no cover
        logger.error(_emoji("✗") + "Pipeline aborted due to an error")
        logger.error(str(exc))
        sys.exit(1)

if __name__ == "__main__":
    main()
