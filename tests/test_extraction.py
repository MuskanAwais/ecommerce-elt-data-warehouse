import importlib
import json
import pytest
import boto3
from moto import mock_aws

from extraction import extractor
from extraction.config import S3_BUCKET_NAME


def test_config_reads_s3_settings_from_environment(monkeypatch):
    monkeypatch.setenv("S3_BUCKET_NAME", "env-bucket")
    monkeypatch.setenv("AWS_REGION", "eu-west-1")

    import extraction.config as config

    config = importlib.reload(config)

    assert config.S3_BUCKET_NAME == "env-bucket"
    assert config.AWS_REGION == "eu-west-1"

@mock_aws
def test_extraction_uploads_to_s3():
    # 1. Setup a fake S3 bucket in Moto
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=S3_BUCKET_NAME)

    # 2. Run the main extraction pipeline
    extractor.main()

    # 3. Verify the files exist in the fake S3 bucket
    response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix="raw/")
    
    assert "Contents" in response, "No objects were uploaded to S3"
    
    # Check that at least 3 files were uploaded (one for each entity)
    assert len(response["Contents"]) >= 3
    
    # Validate the data in one of the files
    for obj in response["Contents"]:
        key = obj["Key"]
        
        # Read the file back out of fake S3
        file_obj = s3.get_object(Bucket=S3_BUCKET_NAME, Key=key)
        payload = json.loads(file_obj["Body"].read().decode("utf-8"))
        
        # Make sure it's valid JSON from DummyJSON
        if "/products/" in key:
            assert "products" in payload
        elif "/customers/" in key:
            assert "users" in payload
        elif "/orders/" in key:
            assert "carts" in payload
