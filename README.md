# Monarch System — Phase 2 (v0.2.1)

Gamified, local-first **Workout + Study + Learning** companion. Built on top of the genuine Phase 1 project, retaining React/TypeScript/Vite, Django, PostgreSQL and the original visual design.

**Owner:** Nobelesse | **Windows project:** `E:\Projects\Monarch-System`

## Features ready in Phase 2

- Phase 1 dark dashboard, paths, roadmap and system diagnostics.
- New **Account** screen with register, sign in, sign out and personal account information.
- Server-side password hashing, session cookies, CSRF protection and ownership-enforced account path selections.
- Optional Google Identity Services sign-in and account linking (requires your own free Google OAuth web client ID).
- Isolated loopback-only Django admin service, **not** exposed on the public backend port.
- Automated tests for basic security, cross-user isolation, account flows and mocked Google verification.

Not ready: workout plan generation, XP, quests, study session logging, installable PWA, public/phone access or production deployment. There is **no fake progress**. Phase 3 is richer onboarding.

## Requirements

- **Python 3.12.x**; `py -3.12` (existing Windows setup uses Python 3.12.10).
- **Node.js 22.12+**, within major version 22; npm 10.
- Local **PostgreSQL 17**, existing database `monarch_system` and user `monarch_app`.
- VS Code and Google Chrome.

## Upgrade from your tested Phase 1 folder

1. Back up the current project and make a PostgreSQL database backup before any schema migration. Avoid sharing private backups or `backend/config.local.json`.
2. Download this complete `Monarch-System-Phase2-v0.2.1.zip`.
3. Extract its **contents directly into** `E:\Projects\Monarch-System` (no nested folder). All versioned source code is updated. No `.venv`, `node_modules`, local config or database is included in the ZIP.
4. In VS Code, open **two PowerShell terminals** and run:

```powershell
Set-Location "E:\Projects\Monarch-System"
# If ZIP is in Downloads, after taking backups:
Expand-Archive -LiteralPath "$env:USERPROFILE\Downloads\Monarch-System-Phase2-v0.2.1.zip" -DestinationPath "E:\Projects\Monarch-System" -Force
code .
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

The setup script reuses your existing `.venv` and `backend/config.local.json`, installs pinned dependencies, runs Django migrations **without dropping your database**, performs a production Vite build, and never prompts for an existing config password.

**Terminal 1 — Django backend**:

```powershell
Set-Location "E:\Projects\Monarch-System"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\backend.ps1
```

**Terminal 2 — Vite frontend**:

```powershell
Set-Location "E:\Projects\Monarch-System"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\frontend.ps1
```

**Open in Chrome**: http://127.0.0.1:5173/

For convenience, in a third PowerShell prompt run `Start-Process chrome 'http://127.0.0.1:5173'` if `chrome` is on your PATH. Otherwise paste the address into Chrome manually. The VS Code terminal is only used to host the app, not as a browser.

## Optional local admin (third terminal)

```powershell
Set-Location "E:\Projects\Monarch-System"
.\.venv\Scripts\python.exe backend/manage.py createsuperuser --settings=config.admin_settings
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\admin.ps1
```

Open **http://127.0.0.1:8001/admin/** in Chrome. The admin site runs on a distinct Django URL configuration, session cookie and loopback-only listener. `http://127.0.0.1:8000/admin/` must still return **404**. Do not expose admin port 8001 to the network or a tunnel.

## Run all local checks

```powershell
Set-Location "E:\Projects\Monarch-System"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

The test command runs with `MONARCH_TEST_MODE=1`, and uses **SQLite memory for tests, not your PostgreSQL live development data**. Run it after setup and review actual output. Extra checks on PostgreSQL are still needed for release acceptance.

## Google sign-in (optional)

See [docs/PHASE2.md](docs/PHASE2.md) for configuration instructions. Use a **Web application** OAuth client ID and authorize origin `http://127.0.0.1:5173`. Add `"google_client_id": "..."` inside your ignored `backend/config.local.json` (or use `MONARCH_GOOGLE_CLIENT_ID` environment variable), then restart the backend. Do not send credentials in chat. No paid AI API is required.

## API and security

See [docs/PHASE2.md](docs/PHASE2.md) for route list, security decisions, migration limitations and Google sign-in behavior. Existing guest path selections remain local; after signing in, **account paths come from the database** and are never determined from user IDs supplied by clients.

## Troubleshooting

- `Python 3.12` missing: install 3.12 and run `py -0p` to verify.
- `npm` or `vite` missing: run `scripts/setup.ps1`, which performs `npm ci` from the included lockfile. Do not run `npm run dev` before installing the dependencies.
- Backend fails to connect: check PostgreSQL 17 service and your local ignored config, **do not paste credentials**.
- Registration/login error: start the Django backend first, then the Vite frontend. Open `http://127.0.0.1:5173/`; v0.2.1 accepts only the local frontend origins listed in Django `CSRF_TRUSTED_ORIGINS`. Hard-refresh after installing the hotfix.
- Google sign-in button missing: check optional client ID and consent-screen configuration; email/password login still works.
- Admin shows unstyled content: use the **local** `scripts/admin.ps1` (includes development-only static file serving), not the public Django server.
- 5173 in use: stop the old Vite process with Ctrl+C.
- Configuration `backend/config.local.json` already exists: setup intentionally preserves it.

## Changelog

See [CHANGELOG.md](CHANGELOG.md). Phase 3 onboarding is the next milestone.

### One-command Chrome launcher

Once the backend and frontend terminals are running, you can also open Chrome with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\chrome.ps1
```

This searches standard Windows Chrome install locations and opens the web app directly in Chrome; it is not an embedded VS Code browser.
