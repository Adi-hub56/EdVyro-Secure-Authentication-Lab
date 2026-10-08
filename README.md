# EdVyro Secure Authentication Lab

A small local Flask authentication service demonstrating defensive authentication controls.

## Controls implemented

- Bcrypt password hashing
- Server-side input validation
- Generic authentication errors
- Login rate limiting: 5 requests/minute/IP
- Cryptographically random server-side session tokens
- SHA-256 session-token storage
- 15-minute session expiry
- HttpOnly and SameSite=Lax cookies
- Server-side session revocation on logout
- Parameterized SQL queries

## Run locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m app.auth
```

The lab runs at http://127.0.0.1:5000.

## Automated tests

```bash
pytest -q
```

The tests cover registration, password hashing, cookie attributes, authentication failures, protected routes, logout/session revocation, and rate limiting.

## Manual verification

The local implementation was manually verified:

- Login: HTTP 200
- Authenticated profile: HTTP 200
- Logout: HTTP 200
- Replayed old session after logout: HTTP 401
- Failed login attempts 1-5: HTTP 401
- Failed login attempt 6: HTTP 429

## Lab limitation

The Secure cookie flag is disabled because this educational lab runs over HTTP on localhost. Production deployments must use HTTPS and Secure cookies. This project is not presented as production-ready.
