# Monarch System — Phase 1 (v0.1.0)
A local-first foundation for a gamified workout, study and learning companion.
Owner: Nobelesse. Windows target: E:\Projects\Monarch-System.

## Included now
- Original dark responsive React/TypeScript interface, crown artwork and reduced-motion support.
- Overview, Your paths, Roadmap and System status screens.
- Choose one or more modules and save the choices in this browser's local storage.
- Django backend, PostgreSQL configuration and initial custom user migration.
- Read-only API health/capability endpoints, sanitized database failures, no admin URL.
- Version checks, dependency locks, password-prompt configuration and Windows setup/run scripts.
- Six backend tests and documented architecture/phase acceptance criteria.

## Not included yet
No registration, Google login, admin interface, exercise prescription, workout logging,
XP, penalties, public QR access or PWA installation. No fake progress records.
This is a development foundation, not a production/public service. Do not expose the
Django/Vite development servers through a tunnel. There is no user login screen in Phase 1.
The custom User table is schema preparation only; use of Django REST Framework is
reserved for account-backed APIs in Phase 2. Foundation endpoints use Django JSON views.

## Required local tools
- Python 3.12 (your installed 3.12.10 is the initial Windows target).
- Node 22.12+ within Node 22; build verified with Node 22.23.2.
- npm 10.9.8 on your PC; package lock format 3.
- PostgreSQL 17 (your installed 17.11), service running on 127.0.0.1:5432.
- Database monarch_system owned by monarch_app, already created by you.
- VS Code and Git. No Docker, paid API, local AI model or GPU workload required.

## Install on Windows
Download Monarch-System-Phase1-v0.1.0.zip to your Downloads folder. Its contents go
DIRECTLY into the project folder (there is no extra enclosing folder in the ZIP).
Keep your existing .venv. The ZIP does not include or overwrite it or local credentials.

```powershell
Set-Location "E:\Projects\Monarch-System"
Expand-Archive -LiteralPath "$env:USERPROFILE\Downloads\Monarch-System-Phase1-v0.1.0.zip" -DestinationPath "E:\Projects\Monarch-System" -Force
code .
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```
If downloaded elsewhere, change only the ZIP's source path. The execution-policy option
applies to that process only, not a permanent Windows policy change.
The setup checks tools, installs locked packages, asks privately for the monarch_app
password, generates a secret key, applies migrations and builds the frontend.
Use the application account password, NOT the postgres administrator password.
If configuration already exists, it is preserved. Dependencies require internet on first setup.

## Run — two VS Code PowerShell terminals
Terminal 1:
```powershell
Set-Location "E:\Projects\Monarch-System"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\backend.ps1
```
Terminal 2:
```powershell
Set-Location "E:\Projects\Monarch-System"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\frontend.ps1
```
Open http://127.0.0.1:5173 in your browser. Keep both terminals open.
Press Ctrl+C in each terminal to stop. Both services bind to loopback only.
Use the same browser address consistently: localhost and 127.0.0.1 have different browser storage.

## Verify Phase 1
1. Overview loads with the purple crown hero and three path cards.
2. Your paths: select modules, save, refresh; saved checkboxes remain checked.
3. At least one path must remain selected.
4. System status: API Online, PostgreSQL connected.
5. Roadmap shows Phase 1 as current and all later work as upcoming.
6. http://127.0.0.1:8000/admin/ returns 404 by design.
7. Resize the browser to a phone-sized window; check navigation and cards.

Automated checks (use isolated SQLite for tests; never modify your PostgreSQL data):
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```
See docs/VALIDATION.md for the exact checks completed by the author and their limits.

## Git — local milestone only
After setup and successful checks:
```powershell
git init -b main
git add .
git status --short
git commit -m "Phase 1: Monarch System foundation"
```
Inspect status before committing: config.local.json, .venv, node_modules and database
backups must not appear. GitHub repository creation/push is not performed by this package.
If Git asks for author information, configure your own name/email; do not invent an email.
After YOU create an empty repository named Monarch-System under Nobelesse:
```powershell
git remote add origin https://github.com/Nobelesse/Monarch-System.git
git push -u origin main
```
Do not run remote add a second time if a remote already exists. Check `git remote -v` first.

## Troubleshooting
- Backend unreachable: start backend.ps1; inspect that terminal. Check port 8000.
- Database unavailable/password authentication failed: check PostgreSQL service and
  backend/config.local.json locally. Never paste that file/password into chat or Git.
- Existing wrong password: edit ONLY database_password in config.local.json using valid JSON;
  preserve secret_key. Then restart backend and rerun setup.
- Address in use: stop the old instance with Ctrl+C. Vite deliberately will not silently switch ports.
- psql not recognized: use C:\Program Files\PostgreSQL\17\bin\psql.exe explicitly.
- Console code-page warning: does not mean database setup failed.
- Mobile cannot connect: expected in Phase 1. Loopback is intentionally PC-only.
- No .venv activation is necessary: scripts use its Python executable directly.
- No database reset/delete/drop command is required for this release.

## Data and updates
PostgreSQL stores the initial auth schema; browser path choices are not yet account data.
Before later schema updates, make a PostgreSQL backup and keep it outside the repository.
Future ZIPs must preserve config.local.json and .venv and use Django migrations.
See docs/ARCHITECTURE.md and docs/ROADMAP.md for the agreed design.
