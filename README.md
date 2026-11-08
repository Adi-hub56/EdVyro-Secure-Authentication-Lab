# EdVyro Defensive Security Assessment Capstone

A defensive security assessment and remediation of the local Flask authentication service. This repository is an educational lab, not a production identity provider.

## Capstone scope

- Target: this repository's Flask authentication API, run locally on `127.0.0.1:5000`.
- Authorization: owner-controlled local application only.
- In scope: registration, login, authenticated profile, logout, session storage, request validation, and HTTP response configuration.
- Out of scope: third-party systems, public targets, denial-of-service testing, real credentials, and personal data.
- Test data: synthetic username and password only.

## Security controls

- Bcrypt password hashing and parameterized SQLite queries.
- Username/password length and format validation.
- Generic login errors to reduce account enumeration.
- Login rate limit of 5 attempts per minute per client IP (Flask-Limiter's configured storage backend).
- Cryptographically random session and CSRF tokens.
- SHA-256 hashes of session identifiers stored server-side.
- 15-minute server-side session expiry and logout revocation.
- HttpOnly and SameSite=Lax session cookie.
- CSRF token required for authenticated logout.
- Defensive response headers and no-store caching.
- Foreign-key enforcement on SQLite connections.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m app.auth
```

The service listens on `http://127.0.0.1:5000`. Initialize the database by starting the module once. The service is deliberately bound to loopback.

To enable the Secure cookie flag behind HTTPS, set `COOKIE_SECURE=true` before starting the app. Do not enable it for plain HTTP localhost testing or the browser will not send the cookie.

## Automated tests

```bash
pytest -q
```

Tests cover registration, password hashing, malformed JSON structures, login failures, cookie attributes, protected profile access, CSRF rejection and acceptance, logout revocation, response headers, and login rate limiting.

## Manual verification workflow

1. Register a synthetic user with `POST /register`.
2. Log in with `POST /login`; retain the session cookie.
3. Request `GET /profile`; obtain the CSRF token from the authenticated response.
4. Send `POST /logout` without the `X-CSRF-Token` header and confirm HTTP 403.
5. Send the same request with the returned token and confirm HTTP 200.
6. Replay the old cookie against `GET /profile` and confirm HTTP 401.
7. Send six failed login attempts in a one-minute window from the same client IP; expect five HTTP 401 responses followed by HTTP 429.

**Evidence integrity:** the repository contains a reproducible procedure and automated tests. Do not describe the manual workflow or test suite as executed unless you run it and capture the actual output in your environment.

## Security report

See [`docs/SECURITY_ASSESSMENT.md`](docs/SECURITY_ASSESSMENT.md), [`docs/REMEDIATION.md`](docs/REMEDIATION.md), and [`docs/RETEST_PLAN.md`](docs/RETEST_PLAN.md).

## Known limitations and production recommendations

- The default `COOKIE_SECURE=false` is solely for local HTTP testing. Production must use HTTPS and set it to true.
- Flask-Limiter's default in-memory storage is not shared across workers and is not durable. Configure Redis or another shared backend for production.
- SQLite is suitable for this small local exercise, not a high-availability identity service.
- Add account lifecycle controls, password reset, MFA, audit logging, secret management, monitoring, and deployment-specific threat modeling before real use.
- The CSRF token is returned by the authenticated profile endpoint for this API-only exercise. A browser UI should keep it out of URLs and send it in a custom header.
- Rate limiting by IP alone can affect users behind shared NAT and can be bypassed by distributed sources; production controls should combine IP and account-aware throttles.
