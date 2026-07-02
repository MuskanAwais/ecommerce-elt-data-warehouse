"""
Configuration for API endpoints and AWS S3 settings.

Values are loaded from the local .env file when present and can also be
overridden by environment variables at runtime.
"""

import os

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

from paths import REPO_ROOT

# ─────────────────────────────────────────────
# API SETTINGS
# ─────────────────────────────────────────────
BASE_URL = "https://dummyjson.com"

API_ENDPOINTS: dict[str, str] = {
    "products":  f"{BASE_URL}/products",
    "customers": f"{BASE_URL}/users",
    "orders":    f"{BASE_URL}/carts",
}

# ─────────────────────────────────────────────
# AWS S3 SETTINGS
# ─────────────────────────────────────────────
ENV_PATH = REPO_ROOT / ".env"

for encoding in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"):
    try:
        load_dotenv(ENV_PATH, override=False, encoding=encoding)
        break
    except UnicodeError:
        continue

S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "ecommerce-elt-raw-data-bucket")
AWS_REGION: str = os.getenv("AWS_REGION", "eu-north-1")
AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
