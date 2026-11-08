# Capstone Verification Status

**Updated:** 2026-11-08  
**Repository:** EdVyro Secure Authentication Lab  
**Status:** Code and test assets committed; runtime verification pending.

## Work completed in the repository

- Added CSRF token generation and validation for logout.
- Added defensive response headers and no-store caching.
- Added safe handling for non-object JSON request bodies.
- Added SQLite foreign-key enforcement and a session-table migration.
- Expanded regression tests for CSRF, session revocation, malformed JSON, and headers.
- Added GitHub Actions CI to run pytest on pushes and pull requests.
- Added `workflow_dispatch` so the workflow can also be started manually.
- Configured the workflow to publish a JUnit XML test-result artifact.

## Verification attempts from the assistant environment

| Check | Result | Notes |
|---|---|---|
| Clone repository to run pytest | Blocked | Environment could not resolve `github.com` (DNS/network unavailable). |
| Check Python dependencies | Blocked | `flask`, `flask_bcrypt`, and `flask_limiter` are not installed in this environment. |
| Inspect GitHub Actions run for the workflow commit | No run returned | No workflow run was available to verify at the time of this update. |
| Source and test files on GitHub | Confirmed present | Files were fetched from the repository after commit. |

**No test pass is claimed here.** A test suite being committed is not evidence that it passed.

## How to complete the runtime verification

1. Open the repository's **Actions** tab.
2. Select **Security lab tests**.
3. Choose **Run workflow** on the `main` branch.
4. Wait for the run to complete.
5. Confirm the `pytest` job is green.
6. Download the `pytest-results` artifact and retain it as evidence.
7. If the run fails, open the job logs, fix the issue, push a correction, and rerun.

## Local alternative

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q --junitxml=test-results.xml
```

Use only synthetic credentials and the local application. Redact session cookies, CSRF tokens, passwords, and any personal data from screenshots or logs.

## Submission note

The public repository contains the assessment report, remediation log, retest plan, source changes, regression tests, and CI workflow. The only outstanding evidence item is a successful actual test run and sanitized runtime retest output.
