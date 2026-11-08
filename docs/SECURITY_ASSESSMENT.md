# Defensive Security Assessment Report

**Project:** EdVyro Secure Authentication Lab  
**Assessment type:** Authorized source-code review and remediation  
**Target:** Local Flask authentication API in this repository  
**Assessment date:** 2026-11-08  
**Assessor:** Project owner / student  
**Data handling:** Synthetic test account only; no real credentials or personal data

## 1. Executive summary

The review focused on the authentication and session lifecycle implemented in `app/auth.py`. The original implementation already used bcrypt, parameterized SQL, random session identifiers, server-side expiry, logout revocation, generic login errors, and a login rate limit. The review identified gaps around CSRF protection for logout, defensive HTTP headers, and handling JSON values that are valid JSON but not objects. The remediation adds controls for these cases and improves SQLite foreign-key enforcement.

This is a code-level assessment of a local educational application. It is not a penetration test of a production deployment. No claim is made that the updated code has been independently tested in a running environment as part of this report.

## 2. Scope and rules of engagement

### In scope
- `POST /register`
- `POST /login`
- `GET /profile`
- `POST /logout`
- Session creation, token storage, expiry, and revocation
- Request parsing and response headers

### Authorization and safety
- Only the owner-controlled source code and local application are in scope.
- Use loopback only (`127.0.0.1`).
- Use synthetic credentials and disposable local data.
- No external scanning, exploitation of third-party services, destructive testing, denial-of-service testing, or collection of real user data.

## 3. Methodology

1. Reviewed route handlers, database queries, session lifecycle, cookie settings, and rate-limit configuration.
2. Mapped observed behavior to common web application risk categories (input handling, CSRF, session management, and security configuration).
3. Prioritized issues by practical impact in this small local application.
4. Applied targeted code changes.
5. Added regression tests and a repeatable manual retest plan.

## 4. Findings

### F-01 — Authenticated logout lacked CSRF validation

**Initial severity:** Medium  
**Area:** Session management / CSRF  
**Evidence:** The original `POST /logout` handler revoked the session based only on the ambient session cookie. It did not require an anti-CSRF token. A cross-site request could therefore attempt to trigger logout in a browser that automatically attached the cookie, depending on browser cookie behavior and request context.

**Impact:** Forced logout / session disruption. This is not account takeover, but it is an integrity and availability issue for the user's authenticated session.

**Remediation:** Generate a cryptographically random CSRF token per session, return it only from the authenticated profile response, and require it in the `X-CSRF-Token` header for logout. Compare tokens using `secrets.compare_digest`.

**Retest:** Missing or incorrect token must return 403; correct token must return 200; replaying the revoked session must return 401.

### F-02 — Missing baseline security response headers

**Initial severity:** Low  
**Area:** Security configuration  
**Evidence:** The reviewed application did not consistently set headers such as `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, or a restrictive Content Security Policy.

**Impact:** Browser-side defense-in-depth was weaker than necessary. The API currently returns JSON and does not serve an interactive UI, so the practical impact is limited.

**Remediation:** Add `nosniff`, `DENY`, `no-referrer`, a restrictive `default-src 'none'` CSP with `frame-ancestors 'none'`, and `Cache-Control: no-store`.

**Retest:** Assert the headers on representative responses.

### F-03 — Valid non-object JSON could cause an unhandled route error

**Initial severity:** Low  
**Area:** Input validation / availability  
**Evidence:** The original handlers used `request.get_json(silent=True) or {}` and then called `.get()`. A JSON array or string is truthy but does not provide the expected mapping interface, which can cause an unhandled exception.

**Impact:** Malformed client input could produce a server error rather than a controlled validation response.

**Remediation:** Verify that parsed JSON is a dictionary before reading fields. Invalid registration data returns 400; malformed login data returns the same generic 401 used for invalid credentials.

**Retest:** Submit JSON arrays to registration and login and verify controlled status codes with no traceback.

### F-04 — Secure cookie flag is disabled for local HTTP

**Initial severity:** Informational / deployment limitation  
**Area:** Session cookie configuration  
**Evidence:** The original cookie configuration set `Secure=False`. This is required for the documented plain-HTTP localhost lab, but not appropriate for production HTTPS deployment.

**Impact:** If deployed over an untrusted network without HTTPS, session cookies could be exposed in transit.

**Remediation:** Make the flag configurable through `COOKIE_SECURE`; production must set it to true and use HTTPS. The local default remains false so the documented localhost lab works.

**Retest:** Inspect the cookie with the environment flag enabled in an HTTPS-capable deployment. Do not infer production readiness from localhost tests.

## 5. Existing controls observed

- Bcrypt password hashing.
- Parameterized SQL statements for user and session lookups.
- Generic invalid-credential response.
- Random session token generation and SHA-256 token-hash storage.
- 15-minute server-side session expiry.
- Session revocation on logout.
- HttpOnly and SameSite=Lax cookie attributes.
- Login throttling configured at five attempts per minute per IP.

## 6. Residual risks

- In-memory rate-limit storage is not shared across multiple workers and resets on process restart. Use a shared backend such as Redis in production.
- IP-only throttling is not a complete credential-stuffing defense.
- The app is a learning sample; it lacks a full production account lifecycle, MFA, password reset, security monitoring, and operational controls.
- Local HTTP testing does not validate TLS, reverse-proxy, or production cookie behavior.

## 7. Conclusion

The code changes address the four identified issues within the stated local-lab scope. The automated tests and manual retest plan are included as reproducible verification artifacts. Final pass/fail status must be based on running those tests and capturing the actual results in the intended environment.
