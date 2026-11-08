# Capstone Verification Status

**Updated:** 2026-11-08  
**Repository:** EdVyro Secure Authentication Lab  
**Status:** Automated CI regression workflow passed; manual runtime evidence remains outstanding.

## Work completed

- Added CSRF token generation and validation for logout.
- Added defensive response headers and no-store caching.
- Added safe handling for non-object JSON request bodies.
- Added SQLite foreign-key enforcement and a session-table migration.
- Expanded regression tests for CSRF, session revocation, malformed JSON, and headers.
- Added GitHub Actions CI to run pytest on pushes and pull requests.
- Added `workflow_dispatch` for manual runs.
- Configured JUnit XML test-result artifact upload.

## GitHub Actions verification

The repository owner's GitHub Actions screenshot captured on 2026-11-08 shows:

| Workflow run | Commit | Status | Interpretation |
|---|---|---|---|
| Security lab tests #1 | `dda379b` | Success (green check) | Initial pytest workflow completed successfully |
| Security lab tests #2 | `fefba7d` | Success (green check) | Updated workflow with JUnit artifact configuration completed successfully |
| Security lab tests #3 | `3e80721` | In progress at screenshot time | Documentation-only verification-status update; final result not yet observed |

The green workflow results establish that the automated CI jobs completed successfully for the code present in those runs. The latest documentation-only run was still running when the screenshot was taken; its final status should be checked separately.

## What is not yet independently evidenced

- A separate manual HTTP/API retest with sanitized request and response captures.
- A downloaded and retained JUnit XML artifact from run #2.
- Final completion status for run #3.

Do not represent manual testing as completed unless it is actually performed and captured.

## Manual evidence checklist

- [ ] Capture sanitized successful login and authenticated profile responses.
- [ ] Capture logout without CSRF header returning 403.
- [ ] Capture logout with valid CSRF header returning 200.
- [ ] Capture replay of the revoked session returning 401.
- [ ] Capture the rate-limit sequence (five 401 responses followed by 429).
- [ ] Remove all passwords, cookies, CSRF tokens, and personal data from evidence.

## Local retest command

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q --junitxml=test-results.xml
```

## Submission note

The repository contains the assessment report, remediation log, retest plan, source changes, regression tests, and CI workflow. Automated GitHub Actions verification has passed in runs #1 and #2. Manual runtime evidence remains a separate optional strengthening of the capstone submission.
