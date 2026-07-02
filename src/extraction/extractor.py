"""
Data extraction module for the E-Commerce ELT pipeline.

Workflow (Modules 2, 3 & 4):
  1. Fetch raw JSON from each DummyJSON API endpoint.
  2. Save a local copy to Data/raw/<entity>/YYYY/MM/DD/ (used by load_raw.py).
  3. Upload the same JSON to S3 under a date-partitioned key:
       s3://<bucket>/raw/<entity>/YYYY/MM/DD/<entity>_<timestamp>.json

During local development the S3 upload is intercepted by Moto (in tests)
and requires no real AWS credentials. Real credentials are added during
the deployment phase only.

Run:
    python -m extraction.extractor      (from src/)
    python src/extraction/extractor.py
"""

import requests
import json
import logging
import datetime
import os
import pathlib
import sys

import boto3
import time
from botocore.exceptions import BotoCoreError, ClientError

SRC_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from paths import DATA_RAW, REPO_ROOT, RESULTS_LOGS
from extraction.config import (
    API_ENDPOINTS,
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    S3_BUCKET_NAME,
)

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
DATA_RAW_ROOT = DATA_RAW
LOG_PATH = RESULTS_LOGS / "extraction.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────
# LOGGING  (file + terminal)
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# FETCH
# ─────────────────────────────────────────────
def _fetch(entity: str, url: str) -> dict:
    """
    Send a GET request and return the parsed JSON response.

    Args:
        entity: Entity name used for logging (e.g. 'products').
        url:    Full API endpoint URL.

    Returns:
        Parsed JSON response as a Python dict.

    Raises:
        requests.HTTPError:        Non-2xx HTTP response.
        requests.Timeout:          Request exceeded 30 seconds.
        requests.RequestException: Any other network-level error.
    """
    logger.info("[FETCH] %s → %s", entity, url)
    max_retries = 3
    backoff = 5  # seconds
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            data = response.json()
            count = len(data.get(entity, [])) if isinstance(data, dict) else len(data)
            logger.info("[FETCH] ✓ %s — %d records received (attempt %d)", entity, count, attempt)
            return data
        except requests.Timeout:
            logger.warning("[FETCH] Timeout on attempt %d for %s", attempt, entity)
            if attempt == max_retries:
                logger.error("[FETCH] Timeout — %s", entity)
                raise
        except requests.HTTPError as exc:
            logger.error("[FETCH] HTTP %s — %s (attempt %d)", exc.response.status_code, entity, attempt)
            raise
        except requests.RequestException as exc:
            logger.warning("[FETCH] Network error on attempt %d for %s: %s", attempt, entity, exc)
            if attempt == max_retries:
                logger.error("[FETCH] Network error — %s: %s", entity, exc)
                raise
        time.sleep(backoff * attempt)


# ─────────────────────────────────────────────
# SAVE LOCAL  (Module 4 support)
# ─────────────────────────────────────────────
def _save_local(entity: str, payload: dict) -> pathlib.Path:
    """
    Write the JSON payload to a local date-partitioned file.

    Path format:
        Data/raw/<entity>/YYYY/MM/DD/<entity>_YYYYMMDD_HHMMSS.json

    This local copy is what load_raw.py reads to build DuckDB staging
    tables — no real AWS credentials required.

    Args:
        entity:  Entity name (products / customers / orders).
        payload: Raw API response dict.

    Returns:
        pathlib.Path to the saved file.
    """
    now_utc   = datetime.datetime.now(datetime.timezone.utc)
    timestamp = now_utc.strftime("%Y%m%d_%H%M%S")
    date_path = now_utc.strftime("%Y/%m/%d")

    out_dir  = DATA_RAW_ROOT / entity / date_path
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{entity}_{timestamp}.json"

    out_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("[LOCAL]  ✓ %s → %s", entity, out_file.relative_to(REPO_ROOT))
    return out_file


# ─────────────────────────────────────────────
# UPLOAD TO S3  (Modules 2 & 3)
# ─────────────────────────────────────────────
def _upload_to_s3(entity: str, payload: dict) -> str:
    """
    Upload the JSON payload to S3 under a date-partitioned key.

    S3 key format:
        raw/<entity>/YYYY/MM/DD/<entity>_YYYYMMDD_HHMMSS.json

    In tests, Moto intercepts boto3.client("s3") so no real AWS
    credentials or network access are needed.

    Args:
        entity:  Entity name (products / customers / orders).
        payload: Raw API response dict.

    Returns:
        The full S3 key string where the object was stored.

    Raises:
        ClientError:    AWS rejected the request (wrong bucket / permissions).
        BotoCoreError:  Low-level connection or credential error.
    """
    now_utc   = datetime.datetime.now(datetime.timezone.utc)
    timestamp = now_utc.strftime("%Y%m%d_%H%M%S")
    date_path = now_utc.strftime("%Y/%m/%d")

    s3_key    = f"raw/{entity}/{date_path}/{entity}_{timestamp}.json"
    json_body = json.dumps(payload, ensure_ascii=False, indent=2)

    s3_client = boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID or None,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY or None,
    )

    logger.info("[S3]     Uploading → s3://%s/%s", S3_BUCKET_NAME, s3_key)
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=json_body,
            ContentType="application/json",
        )
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        msg  = exc.response["Error"]["Message"]
        logger.error("[S3]     ClientError — %s | code=%s msg=%s", entity, code, msg)
        raise
    except BotoCoreError as exc:
        logger.error("[S3]     BotoCoreError — %s: %s", entity, exc)
        raise

    count = len(payload.get(entity, [])) if isinstance(payload, dict) else 0
    logger.info(
        "[S3]     ✓ %s — s3://%s/%s (%d records, %d bytes)",
        entity, S3_BUCKET_NAME, s3_key, count, len(json_body),
    )
    return s3_key


# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────
def main() -> None:
    """
    Run the full extraction pipeline for every configured API endpoint:
      1. Fetch JSON from DummyJSON.
      2. Save a local copy to Data/raw/ (for DuckDB loading).
      3. Upload to S3 (intercepted by Moto in tests).

    Failures are logged and the pipeline continues with the next entity.
    """
    logger.info("=" * 55)
    logger.info("Extraction pipeline started  bucket=s3://%s", S3_BUCKET_NAME)
    logger.info("=" * 55)

    results: dict[str, str] = {}

    for entity, url in API_ENDPOINTS.items():
        try:
            payload = _fetch(entity, url)
            _save_local(entity, payload)
            s3_key  = _upload_to_s3(entity, payload)
            results[entity] = f"s3://{S3_BUCKET_NAME}/{s3_key}"
        except Exception:
            results[entity] = "FAILED"
            logger.warning("[PIPELINE] Skipping %s — see error above.", entity)

    logger.info("=" * 55)
    logger.info("Pipeline complete — results:")
    for entity, outcome in results.items():
        icon = "✓" if outcome != "FAILED" else "✗"
        logger.info("  [%s] %-12s %s", icon, entity, outcome)
    logger.info("=" * 55)


if __name__ == "__main__":
    main()