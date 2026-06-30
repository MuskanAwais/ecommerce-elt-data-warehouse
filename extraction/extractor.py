"""
Data extraction module for DummyJSON API.
"""

import json
import logging
import pathlib
import os
import datetime
import requests

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
def _store(entity: str, payload: dict) -> pathlib.Path:
    """
    Save JSON response into:
    data/raw/<entity>/YYYY/MM/DD/<entity>_timestamp.json
    """

    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
    date_path = datetime.datetime.now(datetime.UTC).strftime("%Y/%m/%d")

    out_dir = DATA_ROOT / "raw" / entity / date_path
    out_dir.mkdir(parents=True, exist_ok=True)

    out_file = out_dir / f"{entity}_{timestamp}.json"

    # WRITE FILE (FIXED)
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # logging count safely
    count = len(payload.get(entity, [])) if isinstance(payload, dict) else 0

    logger.info("Saved %s → %s (records=%s)", entity, out_file, count)

    return out_file


# ---------------- MAIN PIPELINE ---------------- #
def main() -> None:
    for entity, url in API_ENDPOINTS.items():
        data = _fetch(entity, url)
        _store(entity, data)


if __name__ == "__main__":
    main()