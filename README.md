# Monarch System — Phase 3 (v0.3.0)

Local-first gamified personal development app for **Workout, Study and Learning**, continuing the original Phase 1/2 project. Python Django + PostgreSQL backend and React/TypeScript/Vite frontend. No mandatory paid APIs.

**Owner:** Nobelesse | **Windows folder:** `E:\Projects\Monarch-System` | **GitHub:** https://github.com/Nobelesse/Monarch-System

## Phase 3 functionality

- Existing Phase 2 registration, login, session auth, Google identity option and protected path choices retained.
- **Onboarding** sidebar page: five-step guided setup of display name/timezone/language/accessibility, per-path goal/experience/equipment or topics, weekly availability, optional private height/weight, and review/completion.
- Workouts, Study and Learning are configured independently or together; draft state survives refresh, sign-out and sign-in after saving.
- Django account-owned data and additive database migration `0003_onboarding` with security and validation checks.
- This release does **not** implement plan generation, XP or actual training recommendations. Full UI translation beyond the onboarding preference field is also not available yet.

**Release instructions and checklist:** [docs/PHASE3.md](docs/PHASE3.md)
**Earlier phase authentication and OAuth details:** [docs/PHASE2.md](docs/PHASE2.md)

## Prerequisites

- Python 3.12.x, Node.js 22.12–22.x, npm 10, PostgreSQL 17.
- Existing local `monarch_system` database, `monarch_app` user, ignored `backend/config.local.json`.
- Visual Studio Code and Google Chrome.

## Upgrade existing Phase 2 project (Windows PowerShell)

Stop running backend, frontend and admin PowerShell terminals (`Ctrl+C`), back up both your database and project folder, and download the full integrated Phase 3 ZIP to Downloads.

```powershell
Set-Location 'E:\Projects\Monarch-System'
Expand-Archive -LiteralPath "$env:USERPROFILE\Downloads\Monarch-System-Phase3-v0.3.0.zip" -DestinationPath 'E:\Projects\Monarch-System' -Force
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\upgrade_phase3.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

`upgrade_phase3.ps1` checks existing credentials and applies additive migrations without reinstalling your packages. If this is a first-time installation, use `scripts/setup.ps1` instead (see Phase 2 docs).

**VS Code terminal 1 — Backend**

```powershell
Set-Location 'E:\Projects\Monarch-System'
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\backend.ps1
```

**VS Code terminal 2 — Frontend**

```powershell
Set-Location 'E:\Projects\Monarch-System'
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\frontend.ps1
```

**VS Code terminal 3 — Chrome**

```powershell
Set-Location 'E:\Projects\Monarch-System'
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\chrome.ps1
```

App: `http://127.0.0.1:5173/` → **Login → Onboarding**.

Automated tests use in-memory SQLite and don't mutate your development PostgreSQL data. Real PostgreSQL migrations and the Chrome manual checklist still must be verified on your PC. Do not expose the local admin publicly or upload `backend/config.local.json`.

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
