# Monarch System — Real Human Demos (v0.4.5)

Local-first gamified personal development app for **Workout, Study and Learning**, continuing the original Phase 1/2 project. Python Django + PostgreSQL backend and React/TypeScript/Vite frontend. No mandatory paid APIs.

**Owner:** Nobelesse | **Windows folder:** `E:\Projects\Monarch-System` | **GitHub:** https://github.com/Nobelesse/Monarch-System

**Preserved v0.4.2 fixes:** Fresh sign-in on every full browser load, login routing by persisted onboarding completion, a completed-profile summary/edit flow, 3D movement-family exercise previews (not exact biomechanical demonstrations), and new neon dark-abyss Overview illustration. No database schema changes. See [v0.4.2 details](docs/PHASE4_2.md).

## v0.4.5 — Built-in real instructor demos (fix for empty player)

**Countertop push-up now shows an actual matching human instructor video in the app without a file upload.** Six exercise IDs have carefully selected third-party YouTube demonstrations (countertop push-up, wall push-up, floor push-up, chair sit-to-stand, glute bridge, bird dog). These are **live embeds**, not copied or downloaded assets, and require an internet connection. Every guide has a direct Watch on YouTube link if embedding is blocked. Exercises without an exact sourced demonstration keep their written instructions and clearly labeled no-clip fallback — we will not supply fake exercises. Locally installed licensed video or animated GLB files take priority over web embeds. See [docs/PHASE4_5.md](docs/PHASE4_5.md).

**This is real human video, not interactive motion-capture 3D**, because accurate human models and the corresponding movements cannot be conjured without actual licensed/created motion assets. Free videos are embedded with publisher attribution and remain on their original hosting service. No paid APIs, backend changes, or migrations.

## v0.4.4 — Human-first Exercise Form Studio

**The mannequin has been removed.** The workout guide now only plays exercise-specific human MP4/WEBM recordings or locally supplied rigged human GLB animations, and shows a clear **no exact demo installed** state instead of simulating potentially incorrect motions. Seated knee raise retains a labeled, static human pose reference. Users can preview local videos in their browser or find human exercise tutorials by exact name. See [docs/HUMAN_FORM_DEMOS.md](docs/HUMAN_FORM_DEMOS.md) for asset installation, clip review, licensing and limitations. **Human movement videos and 3D GLBs are not included with the release; adding a verified asset is necessary for a moving human demonstration.** No backend or database changes and no new npm dependencies.

## v0.4.3 — Whole-app cinematic UI

All actual React pages share the **user-reference-inspired Dark Abyss cinematic interface**. This is an integrated frontend implementation, not a flattened concept screenshot. It includes a full-width animated hero, real live Overview state, atmospheric sidebar/header, Account, Onboarding, Paths, Workout, Roadmap and System Status styling. The exercise module has a shaded procedural motion guide and a contextual still-image pose reference for Seated knee raise. See [docs/PHASE4_3.md](docs/PHASE4_3.md) for exact limitations and verification.

For existing installations, back up your local project/database, extract `Monarch-System-v0.4.3-Cinematic-UI.zip` to `E:\Projects\Monarch-System` with `Expand-Archive -Force`, then run:

```powershell
cd "E:\Projects\Monarch-System"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\upgrade_cinematic.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

**No new database migration, npm dependency, or external service.** Previous authentication, onboarding, workout-plan, edit/swap, exercise library and admin implementations are retained. No invented streaks or workout counts. The moving atmosphere is CSS animation using reference-derived artwork, **not rendered 4K footage**; the exercise rig is an illustrative movement-family model, **not a validated 3D demo for each exercise**.

## Phase 4 functionality

- Existing Phase 2 registration, login, session auth, Google identity option and protected path choices retained.
- **Onboarding** sidebar page: five-step guided setup of display name/timezone/language/accessibility, per-path goal/experience/equipment or topics, weekly availability, optional private height/weight, and review/completion.
- Workouts, Study and Learning are configured independently or together; draft state survives refresh, sign-out and sign-in after saving.
- Django account-owned data and additive database migration `0003_onboarding` with security and validation checks.
- **Workout** sidebar provides 63 curated exercises, explicit balanced/strength/endurance/mobility focus, easy/standard pacing, weekday-based upper/lower/full-body training splits, broad movement exclusions, same-pattern substitutions, bounded sets/reps/rest editing, and exercise reordering. All drafts remain account-owned and persist to PostgreSQL. This release does **not** record completed workouts, produce XP or provide medical advice. Full UI translation beyond the onboarding preference field is also not available yet.

**Previous refinement release:** [docs/PHASE4_REFINEMENTS.md](docs/PHASE4_REFINEMENTS.md)
**Original Phase 4 baseline:** [docs/PHASE4.md](docs/PHASE4.md)
**Phase 3 onboarding details:** [docs/PHASE3.md](docs/PHASE3.md)
**Earlier phase authentication and OAuth details:** [docs/PHASE2.md](docs/PHASE2.md)

## Prerequisites

- Python 3.12.x, Node.js 22.12–22.x, npm 10, PostgreSQL 17.
- Existing local `monarch_system` database, `monarch_app` user, ignored `backend/config.local.json`.
- Visual Studio Code and Google Chrome.

## Upgrade your existing v0.4.4 project to v0.4.5 (Windows PowerShell)

Stop running backend, frontend and admin servers with Ctrl+C. You do not need to recreate your virtual environment or database.

First **back up the working source folder and verify a PostgreSQL archive**:

```powershell
cd "E:\Projects"
$backup = "E:\Projects\Monarch-System-Pre-v0.4.5-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Copy-Item -LiteralPath "E:\Projects\Monarch-System" -Destination $backup -Recurse
cd "E:\Projects\Monarch-System"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\backup_postgres.ps1
```

Continue only after you see a verified readable backup. Download **Monarch-System-v0.4.5-Complete.zip** into Downloads and then run:

```powershell
cd "E:\Projects\Monarch-System"
$zip = Get-ChildItem "$env:USERPROFILE\Downloads" -Filter "Monarch-System-v0.4.5-Complete*.zip" -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $zip) { throw 'Full v0.4.5 ZIP not in Downloads. Check Chrome Downloads (Ctrl+J) and copy it there.' }
Expand-Archive -LiteralPath $zip.FullName -DestinationPath "E:\Projects\Monarch-System" -Force
Get-Content .\VERSION
.\.venv\Scripts\python.exe backend/manage.py migrate --noinput
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

No new database migrations or npm dependencies are required for the v0.4.5 update if v0.4.4 was working. The test script first audits the 6 exact-exercise curated video links in source, then runs Django system checks, 81 backend tests and the TypeScript/Vite production build. The index audit **does not establish current online YouTube availability**; test Countertop push-up in Chrome. Tests use an in-memory SQLite database and do not reset your PostgreSQL development data.

**VS Code terminal 1 — Backend**

```powershell
cd "E:\Projects\Monarch-System"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\backend.ps1
```

**VS Code terminal 2 — Frontend**

```powershell
cd "E:\Projects\Monarch-System"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\frontend.ps1
```

**VS Code terminal 3 — Chrome**

```powershell
cd "E:\Projects\Monarch-System"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\chrome.ps1
```

Open `http://127.0.0.1:5173/` → Sign in → Workout → **Countertop push-up** → Human Form Guide. The internet and embedding permission from the publisher are required; a Watch on YouTube fallback is provided. This is human instructor video, **not photorealistic rotatable 3D motion**, and just six of 63 exercises have curated embeds.

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

See [CHANGELOG.md](CHANGELOG.md). Phase 4 workout drafts are the current milestone; workout execution comes in Phase 5.

### One-command Chrome launcher

Once the backend and frontend terminals are running, you can also open Chrome with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\chrome.ps1
```

This searches standard Windows Chrome install locations and opens the web app directly in Chrome; it is not an embedded VS Code browser.
