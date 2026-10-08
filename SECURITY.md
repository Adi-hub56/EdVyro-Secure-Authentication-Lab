# Security Notes

## Password security

Passwords are processed with Flask-Bcrypt before storage. The database stores the password hash, not the supplied plaintext password.

## Input validation

Usernames are restricted to 3-30 characters using letters, numbers, underscores, periods, and hyphens. Passwords must be 8-128 characters.

## Login protection

The login endpoint is limited to 5 requests per minute per client IP. Failed authentication uses the generic message "Invalid username or password" to reduce account enumeration.

## Session security

A random session token is generated with Python's secrets module. Only its SHA-256 hash is stored server-side. Sessions expire after 15 minutes.

The authentication cookie uses HttpOnly and SameSite=Lax. Logout deletes the server-side session record, so replaying the old cookie after logout returns HTTP 401.

## Database safety

Database operations use parameterized SQL queries.

## Verification evidence

Manual testing produced:

- Login: HTTP 200
- Authenticated profile: HTTP 200
- Logout: HTTP 200
- Replayed old session after logout: HTTP 401
- Failed login attempts 1-5: HTTP 401
- Failed login attempt 6: HTTP 429

## Production considerations

This lab intentionally uses HTTP localhost, so the Secure cookie attribute is disabled. Production should use HTTPS, Secure cookies, a production WSGI server, protected database infrastructure, appropriate CSRF defenses for cookie-authenticated browser forms, centralized rate-limit storage, monitoring, and secure secret management.
