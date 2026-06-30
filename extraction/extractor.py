"""
Data extraction module for DummyJSON API.
"""

import json
import logging
import pathlib
import os
import datetime
import requests
import boto3

from extraction.config import API_ENDPOINTS

# ---------------- CONFIG ---------------- #
DATA_ROOT = pathlib.Path(
    os.getenv("DATA_ROOT", pathlib.Path(__file__).parents[1] / "data")
)

# ---------------- LOGGING ---------------- #
LOG_PATH = pathlib.Path(__file__).parents[1] / "logs" / "extraction.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8")],
)

logger = logging.getLogger(__name__)


# ---------------- FETCH ---------------- #
def _fetch(entity: str, url: str) -> dict:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        logger.error("Fetch failed for %s: %s", entity, exc)
        raise




# ---------------- STORE ---------------- #
def _store(entity: str, payload: dict) -> str:
    """
    Upload JSON response to S3:
    s3://<bucket>/raw/<entity>/YYYY/MM/DD/<entity>_timestamp.json
    """
    from extraction.config import S3_BUCKET_NAME
    
    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
    date_path = datetime.datetime.now(datetime.UTC).strftime("%Y/%m/%d")

    # The exact path (key) inside the S3 bucket
    s3_key = f"raw/{entity}/{date_path}/{entity}_{timestamp}.json"

    # Initialize the S3 client
    s3_client = boto3.client("s3")

    # Convert the Python dictionary payload to a JSON string
    json_string = json.dumps(payload, ensure_ascii=False, indent=2)

    # Upload to S3
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=s3_key,
        Body=json_string,
        ContentType="application/json"
    )

    # Count the records for logging
    count = len(payload.get(entity, [])) if isinstance(payload, dict) else 0
    logger.info("Uploaded %s → s3://%s/%s (records=%s)", entity, S3_BUCKET_NAME, s3_key, count)

    return s3_key



# ---------------- MAIN PIPELINE ---------------- #
def main() -> None:
    for entity, url in API_ENDPOINTS.items():
        data = _fetch(entity, url)
        _store(entity, data)


if __name__ == "__main__":
    main()