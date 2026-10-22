# Phase 2 — Accounts & Access

## What was implemented

- Standard Django session authentication: registered username/email + password; password strength checks; sign in/out; a current-user endpoint.
- CSRF protection on registration, sign in/out, Google sign-in and all account mutations, including anonymous calls.
- Case-insensitive unique username/email constraints, server-authoritative account-owned paths, no API owner-ID parameter.
- Lightweight IP+identifier sign-in throttle for the local single-process development server. **Not sufficient for public multi-process deployment.**
- Google Identity Services browser button and backend validation of Google-signed ID tokens, issuer, audience, expiry and verified email. **Live Google credentials have not been tested in this build.**
- Google-first accounts receive unusable passwords and an identity linked by Google's immutable subject. Existing password accounts with matching email are **not** automatically linked (prevents silent account takeover). They must sign in with the password and explicitly link the same verified Google email.
- Public Django listener has no admin route. A separate admin-only URL configuration on `127.0.0.1:8001` checks `REMOTE_ADDR` and requires staff authentication; uses distinct admin session/CSRF cookie names.
- The guest preview still works with browser-only path choices, but authenticated path choices are persisted in PostgreSQL. Full onboarding begins in Phase 3.

## Google sign-in configuration (optional)

1. In the **Google Cloud Console**, configure the OAuth consent screen / Google Auth Platform and create a **Web application** OAuth client ID.
2. Add `http://127.0.0.1:5173` under **Authorized JavaScript origins**. Use exactly this origin when opening the app (don't switch to `localhost`). This uses the Google Identity Services JavaScript callback flow; this phase does not implement a server redirect callback or require a Google client secret.
3. Edit your existing ignored `backend/config.local.json` file *on your own computer* (never upload/share it). Add a `google_client_id` string alongside the existing `secret_key` and `database_password`. Keep JSON syntax valid:
   `"google_client_id": "YOUR_WEB_APPLICATION_CLIENT_ID.apps.googleusercontent.com"`
4. Restart both servers. The app's Account page will render the Google sign-in button if Google Identity Services loads.
5. Validate in Chrome with a testing Google account added to the consent screen if the app is still in testing. For an existing Monarch password account, first sign in normally, then visit Account → Link Google.

**Never send your password, Django secret key, Google ID tokens, or backend/config.local.json in chat.** The Google Web client ID is not a secret, but the rest of the local configuration is sensitive.

## API

| Method | Route | Access | Purpose |
|---|---|---|---|
| GET | `/api/health/` | Public | Database health |
| GET | `/api/system/` | Public | Feature flags / configured Google client ID |
| GET | `/api/auth/csrf/` | Public | Establish CSRF cookie |
| POST | `/api/auth/register/` | Public + CSRF | Create player + default path selection |
| POST | `/api/auth/login/` | Public + CSRF | Start session |
| POST | `/api/auth/logout/` | Signed in + CSRF | Destroy session |
| GET | `/api/auth/me/` | Signed in | Profile and selected paths |
| POST | `/api/auth/google/` | Public + CSRF | Verify Google ID token, sign in/create |
| POST | `/api/auth/google/link/` | Signed in + CSRF | Link same verified Google email |
| GET | `/api/paths/` | Signed in | Current player's selected paths |
| PUT | `/api/paths/` | Signed in + CSRF | Save current player's selected paths |

## Security boundaries and remaining work

- Both Django and Vite development listeners bind to `127.0.0.1` only. Never forward/tunnel port 8001. Remote-address middleware is defense-in-depth, not a guarantee if networking is reconfigured.
- Both listeners use localhost HTTP; cookies are HTTP-only sessions but not HTTPS Secure cookies. Public hosting needs HTTPS, secure cookies, trusted hosts/origins, reverse proxy configuration and shared distributed throttling.
- End-to-end OAuth flow, real PostgreSQL upgrades and Windows PowerShell execution require local verification by the project owner.
- There is **no email verification/password reset** in Phase 2. An email address is recorded, not independently verified for password accounts. Public-facing deployment must introduce email ownership verification and recovery before launch.
- To deploy a live service later, do a dedicated security assessment and add production ASGI/WSGI serving, persistent caching, event logs, monitoring and abuse controls.

## Verification

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1` runs Django checks, migration-drift detection, account/security tests with an in-memory SQLite test database, and Vite TypeScript/build checks. It does **not** run against existing PostgreSQL data. The owner should run and report results; do not equate the validation script existing with tests having passed.

## v0.2.1 browser CSRF hotfix

When browsing the application at `http://127.0.0.1:5173`, Chrome POST requests include the Vite origin (`http://127.0.0.1:5173`), while the Vite proxy forwards the request to Django (`http://127.0.0.1:8000`). Django must explicitly trust that **local** frontend origin for CSRF checks. Without it, the registration POST yields Django's HTML 403 page, which the old React client tried to parse as JSON.

The new `CSRF_TRUSTED_ORIGINS` allows only local Vite dev origins. This does not disable CSRF checks, and a new regression test confirms an untrusted origin is still rejected. Do not copy these development origins as a production configuration; use your deployed frontend origin and HTTPS security settings after a full deployment review.

No new dependencies or migrations are required. Apply the v0.2.1 ZIP after stopping both running development servers, then run `scripts/test.ps1` and restart backend/frontend. The tests include a browser-origin request; manually try registration again in Chrome.

Admin isolation: `config.admin_settings` explicitly does **not** trust the public Vite frontend origin.
