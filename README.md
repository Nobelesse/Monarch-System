> Current package version: **v0.4.7**

# Monarch-System — v0.4.6 Offline Workout Prototype

**Monarch-System** is a local-first gamified Workout / Study / Learning application, with a Django + PostgreSQL backend and React / TypeScript / Vite frontend. GitHub: https://github.com/Nobelesse/Monarch-System. Project folder on Windows: `E:\Projects\Monarch-System`.

## v0.4.6: What is new

- Removes the previously embedded YouTube/online exercise viewer from the active workout pages.
- Adds **offline illustrated 3D motion for all 63 catalog exercise names**, each mapped to one of 39 named movement templates. Camera orbit, pause, speed and scrubbing are available without an internet connection. The body is procedural/stylized: **it is not photorealistic, 4K motion capture, or an anatomically verified exercise demonstration**. The request for a lifelike exercise trainer is still outstanding; details in [docs/PHASE4_6_OFFLINE.md](docs/PHASE4_6_OFFLINE.md).
- Adds a **Set & Recovery Coach** to the generated workout plan showing the *actual prescribed* sets, repetitions/hold times, rest between sets, selectable 30–120 second between-exercise break and countdowns. Tap **Complete set** manually; the software does not detect repetitions, record real training completion, or add XP.
- Retains the existing 63-exercise catalog, onboarding, login, account privacy, workout preferences, plan editing/substitutions, cinematic Overview, and PostgreSQL data.
- No new Python or npm dependencies; no database schema migration.

**Safety:** Models are visual study aids, not validated form. Consult a qualified coach for correct lifting mechanics, particularly with free weights. Stop if you experience pain or alarming symptoms.

## Full Windows upgrade from existing v0.4.5

Stop the Django/React servers first. Back up the current directory and database **before extraction**:

```powershell
cd "E:\Projects"
$backup = "E:\Projects\Monarch-System-Pre-v0.4.6-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Copy-Item "E:\Projects\Monarch-System" -Destination $backup -Recurse
cd "E:\Projects\Monarch-System"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\backup_postgres.ps1
```

Continue only after backup verification. Download `Monarch-System-v0.4.6-Offline-Workout-Prototype.zip` into Windows Downloads:

```powershell
cd "E:\Projects\Monarch-System"
$zip = Get-ChildItem "$env:USERPROFILE\Downloads" -Filter "Monarch-System-v0.4.6-Offline-Workout-Prototype*.zip" -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $zip) { throw 'v0.4.6 ZIP not found. Check Chrome downloads and copy it into Downloads.' }
Expand-Archive -LiteralPath $zip.FullName -DestinationPath "E:\Projects\Monarch-System" -Force
Get-Content VERSION
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\upgrade_offline_motion.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

`test.ps1` runs 63-slug/offline coverage, rendered-motion smoke checks, Django system/migration tests and the existing 81 backend tests, followed by TypeScript/Vite production build. **Results must be confirmed locally on Windows**, not assumed from this ZIP.

**Start backend (VS Code Terminal 1):**

```powershell
cd "E:\Projects\Monarch-System"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\backend.ps1
```

**Start frontend (Terminal 2):**

```powershell
cd "E:\Projects\Monarch-System"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\frontend.ps1
```

**Open Google Chrome (Terminal 3):**

```powershell
cd "E:\Projects\Monarch-System"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\chrome.ps1
```

Visit `http://127.0.0.1:5173/` → Sign in → Workout → choose a training day → **Offline 3D human demo**. For the detailed set/rest timer, find **Set & Recovery Coach** under the exercise.

## Existing features and documentation

Phase 1: app foundation. Phase 2: registration, CSRF, account access, optional Google OAuth and local-only admin at `127.0.0.1:8001/admin/`. Phase 3: private five-step personalized onboarding. Phase 4: exercise catalogue, deterministic plans, recovery scheduling, edit/reorder/substitute, cinematic Dark Abyss design. See [docs/PHASE2.md](docs/PHASE2.md), [docs/PHASE3.md](docs/PHASE3.md), [docs/PHASE4.md](docs/PHASE4.md), [docs/PHASE4_REFINEMENTS.md](docs/PHASE4_REFINEMENTS.md) and [docs/ROADMAP.md](docs/ROADMAP.md).

### Tests and configuration

Python 3.12.x, Node.js 22.12–22.x, npm 10 and PostgreSQL 17, plus an existing initialized app, are required. Keep `backend/config.local.json`, private user data, database backups, `.venv`, and `frontend/node_modules` out of Git. The default development test script uses its own SQLite in-memory test database; it does not overwrite the running PostgreSQL records. For final acceptance verify PostgreSQL backup and actual UI behavior separately.
