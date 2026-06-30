"""
Configuration file for API endpoints and AWS settings.
"""

BASE_URL = "https://dummyjson.com"

API_ENDPOINTS = {
    "products": f"{BASE_URL}/products",
    "customers": f"{BASE_URL}/users",
    "orders": f"{BASE_URL}/carts"
}

# ---------------- AWS S3 CONFIG ---------------- #
# The name of your S3 Bucket (you can change this later to your real bucket)
S3_BUCKET_NAME = "ecommerce-elt-raw-data-bucket-123" 
