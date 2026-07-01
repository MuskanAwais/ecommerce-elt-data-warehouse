"""
Configuration for API endpoints and AWS S3 settings.

All values here are plain constants — no real AWS credentials are needed
during development. Tests use Moto to mock the S3 service transparently.
Real credentials will be wired in during the deployment phase.
"""

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
# The bucket name used by both the extractor and the Moto tests.
# Change this to your real bucket name during the deployment phase.
S3_BUCKET_NAME: str = "ecommerce-elt-raw-data-bucket-123"
AWS_REGION: str = "us-east-1"
