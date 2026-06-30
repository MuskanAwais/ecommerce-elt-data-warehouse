# Module 9: GitHub Finalization (Spec 9)

## 1. Concept & Goal
**Concept:** Prepare the Git repository for open-source visibility, collaboration, and continuous integration.
**Goal:** Implement quality control measures so that any future code changes are automatically tested, and contributors have templates to follow when submitting bugs or features.

## 2. Workflow
1. A developer opens a Pull Request.
2. GitHub Actions intercepts the PR and spins up a cloud runner.
3. The runner executes `pytest` and `dbt test`.
4. If tests pass, the PR is allowed to merge.

## 3. Architecture
- **Platform:** GitHub
- **CI/CD Pipeline:** GitHub Actions

## 4. Database Design
*Not applicable.*

## 5. Implementation Plan
- **Templates:** 
  - Create `.github/ISSUE_TEMPLATE/bug_report.md` and `feature_request.md`.
  - Create `.github/pull_request_template.md`.
- **Guidelines:**
  - Create `CONTRIBUTING.md` outlining the branch strategies (e.g., `feat/`, `fix/`) and coding standards.
- **CI Pipeline:**
  - Create `.github/workflows/ci.yml`.
  - Write YAML steps to: checkout code, setup python, install requirements, run `pytest tests/`, and run `dbt test`.

## 6. Deployment Plan
- **Execution:** Pushing to GitHub automatically triggers the CI/CD pipeline. No local deployment is needed.

## 7. Git Commit Instructions
```bash
git add .github/ CONTRIBUTING.md
git commit -m "docs(github): add issue & PR templates, CI workflow, and CONTRIBUTING guide"
```
