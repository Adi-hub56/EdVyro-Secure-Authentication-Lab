# Remediation Log

This log records the code changes made for the Defensive Security Assessment Capstone.

| Finding | Change | Verification artifact |
|---|---|---|
| F-01 CSRF on logout | Per-session random CSRF token; required custom header; constant-time comparison | `tests/test_auth.py::test_logout_rejects_missing_or_invalid_csrf_token`, `test_logout_revokes_session` |
| F-02 Missing response headers | Added conservative headers for a JSON-only API and disabled caching | `tests/test_auth.py::test_security_headers_are_present` |
| F-03 Non-object JSON handling | Validate parsed JSON is a dictionary before reading fields | `tests/test_auth.py::test_malformed_json_shapes_are_rejected_safely` |
| F-04 Cookie Secure deployment setting | `COOKIE_SECURE` environment switch; local HTTP remains false | Documented configuration in README and application |

## Additional hardening

- Enabled SQLite foreign-key enforcement on each connection.
- Added a migration for the new CSRF-token column.
- Revoked legacy sessions that cannot satisfy the new CSRF validation.
- Set authenticated profile responses to `Cache-Control: no-store`.

## Commit record

- `348fd3f` — fix: add CSRF protection and security headers
- `f68e304` — test: cover CSRF, malformed input, and security headers

These are repository commits. They do not, by themselves, prove that the tests have been executed successfully.
