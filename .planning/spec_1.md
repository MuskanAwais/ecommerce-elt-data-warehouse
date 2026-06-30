# Module 1: Project Setup (Spec 1)

## 1. Concept & Goal
**Concept:** Scaffold the repository with the required folders, environments, and base configurations.
**Goal:** Give the project a clean, reproducible environment from day one, allowing any data engineer to clone the repository and start developing immediately.

## 2. Workflow
1. Initialize the Git repository.
2. Define Python dependencies to ensure consistent environments.
3. Establish the base directory structure for raw data, logs, transformations, and tests.
4. Add placeholder files (`.gitkeep`) so Git tracks empty directories.

## 3. Architecture
- **Environment:** Local Python Virtual Environment (`.venv`).
- **Structure:** Standard ELT data engineering repository layout (separation of extraction scripts, dbt transformations, and data storage).

## 4. Database Design
*Not applicable for this module. No databases are created yet.*

## 5. Implementation Plan
- Create the virtual environment using `python -m venv .venv`.
- Create a `requirements.txt` containing base dependencies (like `requests`, `boto3`, `pytest`).
- Create standard directories:
  - `config/` (for credentials)
  - `data/` (with subdirectories `processed/`, `warehouse/`)
  - `extraction/` (for Python EL scripts)
  - `logs/` (for application logs)
  - `notebooks/` (for EDA)
  - `tests/` (for unit testing)
- Place `.gitkeep` inside empty directories.
- Create a comprehensive `.gitignore` to avoid pushing secrets, large data files, or local virtual environments to the remote server.

## 6. Deployment Plan
- **Execution:** Developers run `pip install -r requirements.txt` locally to set up their machine. No remote deployment required for this stage.

## 7. Git Commit Instructions
```bash
git add .gitignore requirements.txt README.md config/ data/ logs/ notebooks/ extraction/ tests/
git commit -m "chore: scaffold project layout & basic config"
```
