# Module 3: Raw Data Storage (Spec 3)

## 1. Concept & Goal
**Concept:** Organize the raw JSON files in the S3 bucket using a logical, date-partitioned folder hierarchy.
**Goal:** Ensure the data lake remains organized over time, making it easy to query specific days, re-process historical data, and apply lifecycle policies (like deleting data older than 90 days).

## 2. Workflow
1. During the extraction phase, capture the current UTC timestamp.
2. Format the timestamp into a date hierarchy: `YYYY/MM/DD`.
3. Construct the exact S3 Key (filepath) using this date structure.
4. Upload the file to that specific key in S3.

## 3. Architecture
- **Storage Strategy:** Date-Partitioned Data Lake (S3).
- **Partition Format:** `s3://<bucket_name>/raw/<entity_name>/YYYY/MM/DD/<entity>_timestamp.json`

## 4. Database Design
*Not applicable. This concerns object storage hierarchy, not relational tables.*

## 5. Implementation Plan
- **In `extraction/extractor.py`**:
  - Utilize Python's `datetime` module to capture `datetime.datetime.now(datetime.UTC)`.
  - Extract the year, month, and day strings.
  - Dynamically build the `s3_key`: `f"raw/{entity}/{YYYY}/{MM}/{DD}/{entity}_{timestamp}.json"`.
  - Pass this formatted key to the `boto3` upload function.
- *(Optional)* Create a `scripts/cleanup_raw.py` utility that connects to S3 and deletes objects older than a specific date threshold to manage storage costs.

## 6. Deployment Plan
- This is inherently deployed as part of the execution of the `extractor.py` script. The structure is enforced programmatically on every run.

## 7. Git Commit Instructions
```bash
git add extraction/extractor.py
git commit -m "refactor(extraction): store raw files in date-partitioned S3 paths"
```
