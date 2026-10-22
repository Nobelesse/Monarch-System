# Monarch System changelog

## v0.2.1 — Phase 2 Registration Hotfix (22 October 2026)
- Trust only local Vite frontend origins (`127.0.0.1:5173`, `localhost:5173`) for Django CSRF-protected requests proxied to port 8000.
- Handle unexpected HTML and HTTP errors in the React API client without raw JSON parsing exceptions.
- Verify the CSRF cookie-fetch step; add browser-origin, untrusted-origin, and local admin-isolation tests.
- No dependency changes, no new migrations, and no database resets required.

## v0.2.0 — Phase 2 Accounts & Access (20 October 2026)
- Added username/email registration, password validation, session login/logout, CSRF endpoint and current-account endpoint.
- Added account-owned path preferences, migration, tests and strict per-request user scoping.
- Added optional Google ID-token verification, passwordless Google accounts, and explicit Google linking.
- Added isolated Django admin config, local-only middleware, separate cookie names and Windows admin script.
- Updated React UI for accounts and personal paths; preserved Phase 1 theme and browser workflow.
- Added tests and Phase 2 docs. See `docs/VALIDATION.md` for verification limitations.

## v0.1.0 — Phase 1 foundation
- Original responsive React shell, Django backend, PostgreSQL configuration, initial User model and diagnostics.
