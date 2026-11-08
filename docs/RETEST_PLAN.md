# Retest Plan and Evidence Checklist

Run only against the local owner-controlled application using synthetic data.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Start the app in a separate terminal:

```bash
python3 -m app.auth
```

## Automated regression tests

| Test | Expected result |
|---|---|
| Registration with valid synthetic input | 201 |
| Registration with non-object JSON | 400 |
| Login with non-object JSON | 401 |
| Password storage inspection | Bcrypt hash, not plaintext |
| Valid login | 200; HttpOnly, SameSite=Lax, 900-second cookie |
| Unauthenticated profile | 401 |
| Authenticated profile | 200 and CSRF token |
| Logout without CSRF header | 403 |
| Logout with incorrect CSRF header | 403 |
| Logout with correct CSRF header | 200 |
| Reuse revoked session | 401 |
| Security response headers | All expected headers present |
| Six invalid logins in one minute from same test client IP | First five 401, sixth 429 |

## Manual API retest

Use an API client or curl. Do not place credentials in shell history on a shared machine.

1. Register a disposable user.
2. Login and store the returned cookie in a local-only cookie jar.
3. Request `/profile` and note the CSRF token.
4. Attempt logout without the token; expect 403.
5. Attempt logout with the token; expect 200.
6. Replay the old cookie against `/profile`; expect 401.
7. Verify the login rate-limit behavior with controlled requests.

## Evidence to capture before submission

- [ ] Terminal output showing the complete `pytest -q` result and exit code.
- [ ] Sanitized request/response evidence for successful login and authenticated profile.
- [ ] Logout without CSRF token returning 403.
- [ ] Logout with valid CSRF token returning 200.
- [ ] Replayed revoked session returning 401.
- [ ] Rate-limit sequence showing 401 x5 then 429.
- [ ] GitHub commit history showing remediation and test commits.

Remove cookie values, passwords, tokens, local database files, and personal data from screenshots. Never publish live session cookies or CSRF tokens.

## Result status

**Pending execution in the student's local environment.** The repository includes automated tests and this repeatable plan, but no fabricated test output or runtime evidence is included.
