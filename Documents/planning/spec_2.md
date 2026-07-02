# Module 2: Data Extraction (Spec 2)

## 1. Concept & Goal
**Concept:** Pull raw JSON data from a source (DummyJSON API) and save it to a raw data lake (AWS S3).
**Goal:** Successfully connect to external data sources, extract payloads for Products, Customers (Users), and Orders (Carts), and safely persist them for downstream processing.

## 2. Workflow
1. Read the API endpoints and AWS configurations from `config.py`.
2. Python script iterates through each endpoint.
3. Performs an HTTP GET request to extract the data.
4. Serializes the data into a JSON string.
5. Uses `boto3` to upload the JSON payload to the designated AWS S3 bucket.
6. Logs the success or failure of each extraction.

## 3. Architecture
- **Data Source:** DummyJSON REST API.
- **Compute:** Local Python process (or AWS Lambda/Airflow in production).
- **Storage Target:** AWS S3 Bucket (Raw Layer).

## 4. Database Design
*Not applicable. Data is stored as unstructured/semi-structured JSON documents.*

## 5. Implementation Plan
- **`extraction/config.py`**: Define `API_ENDPOINTS` mapping and the `S3_BUCKET_NAME`.
- **`extraction/extractor.py`**:
  - `_fetch()` function: Takes an endpoint URL, executes `requests.get()`, and returns a dictionary. Includes timeout and error handling.
  - `_store()` function: Takes the JSON dictionary, converts it to a string using `json.dumps`, and uploads it using `boto3.client('s3').put_object()`.
  - `main()` function: Orchestrates the fetch and store loop.
- **`tests/test_extraction.py`**: Use the `moto` library (`@mock_aws`) to simulate an S3 bucket so unit tests can run locally without real AWS credentials.

## 6. Deployment Plan
- **Local Dev:** Run manually via `python -m extraction.extractor`.
- **Production (Future):** This Python script can be containerized using Docker and run on a schedule using Apache Airflow or an AWS EventBridge + Lambda trigger.

## 7. Testing Instructions
- Ensure your virtual environment is active.
- Run `pip install -r requirements.txt` to install the `boto3` and `moto` dependencies.
- Run `pytest tests/` in the root of your project to execute the mocked AWS tests.

## 8. Git Commit Instructions
Once the tests pass successfully, run these commands to checkpoint your code:
```bash
git add extraction/ tests/ requirements.txt pytest.ini
git commit -m "feat(extraction): add API client, config, structured logging, and S3 upload"
git push
```
