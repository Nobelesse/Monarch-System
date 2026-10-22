# Phase 3 — Player Onboarding & Personalization (v0.3.0)

**Status:** Code integrated; user must run Windows/PostgreSQL migrations, backend test suite, frontend build, and Chrome manual checklist before the phase is accepted.

## Scope implemented

- Five-step authenticated React onboarding: (1) identity/accessibility, (2) goals and level for each selected path, (3) per-path weekday availability, (4) optional private height/weight fields for workout, (5) review and complete.
- Resumable drafts: each `Save draft` or `Save & continue` sends an atomic database update; reload loads the last saved step. Unsaved edits are not synced until saved.
- Works with Workout, Study, Learning individually or together, reusing Phase 2's server-owned `PlayerPaths` selection.
- Edits after completion reopen onboarding until completed again. Adding/removing selected paths invalidates previous completion; unselected preferences are retained for possible later selection, and unselected weekly schedule entries are discarded on the next save.
- Backend models: `PlayerProfile`, `ModulePreference`, `WeeklyAvailability`, `PrivatePhysique`. Migration `0003_onboarding` is additive; existing accounts and selections stay intact.
- Validation: supported IANA timezone, 48-character display name, two language preferences (English and Hindi), validated module goals, starting experience, equipment list, topics list, per-day availability of 15–240 minutes in 15-minute increments, optional physique range and privacy boundaries.
- Hindi is recorded only as a preferred language; this version's interface has not been fully translated. Reduced motion / higher contrast preferences are applied to the onboarding interface, not yet the full application.
- No simulated training, health diagnoses, photos, XP, punishment or generated study plans.

## JSON API

`GET /api/onboarding/` (session required): returns `{modules:[...],onboarding:{...}}` with this signed-in user's saved draft and optional private physique. GET may initialize the signed-in user's empty `PlayerProfile` record.

`PUT /api/onboarding/` (session + CSRF required): fully replaces the signed-in user's draft state. Unknown fields (including a user/owner ID) are rejected. Writes are atomic. Requires exactly these fields:

```json
{
  "display_name":"My Player",
  "timezone":"Asia/Kolkata",
  "language":"en",
  "reduced_motion":false,
  "high_contrast":false,
  "current_step":3,
  "completed":false,
  "preferences":{
    "workout":{"goal":"Build consistent strength","experience":"beginner","equipment":["bodyweight"],"topics":[]}
  },
  "schedule":[{"module":"workout","weekday":0,"minutes":45}],
  "physique":{"height_cm":null,"weight_kg":null}
}
```

Only selected paths may occur in `preferences` or `schedule`. Completion additionally requires each selected path to have a goal and at least one scheduled weekday. Day integers run Monday=0 to Sunday=6. The `physique` fields are optional, limited to the workout path and not exposed in `/api/auth/me/` or `/api/system/`.

## Upgrade Windows project, without overwriting your local configuration

1. **Backup** `E:\Projects\Monarch-System` and the PostgreSQL database before migrating.
2. Stop backend, frontend and admin servers (`Ctrl+C` in their terminals).
3. Download the full integrated `Monarch-System-Phase3-v0.3.0.zip` into Downloads and extract the files directly into `E:\Projects\Monarch-System` using `Expand-Archive -Force`. Keep `.venv`, `frontend/node_modules` and the ignored `backend/config.local.json` unchanged.
4. From a VS Code PowerShell terminal in the root:

```powershell
Set-Location 'E:\Projects\Monarch-System'
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\upgrade_phase3.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

5. Start `scripts/backend.ps1` and `scripts/frontend.ps1` in **separate terminals**, then `scripts/chrome.ps1`. Login and open **Onboarding** in the left navigation at `http://127.0.0.1:5173/`.
6. If TypeScript/Vite binaries are missing, **stop any running Node/Vite servers first**, then run `cd frontend; npm.cmd ci; npm.cmd run build`. No dependency versions were changed for this phase.
7. If migrations fail, stop and read the first error; do not delete or reset production/local PostgreSQL data. Your backup is your rollback path. Do not reverse data migrations without checking affected user records.

## Acceptance checklist — mark only after real local verification

- [ ] PostgreSQL backup exists, `upgrade_phase3.ps1` successfully applied `core.0003_onboarding`.
- [ ] `scripts/test.ps1`: Django checks pass, no model/migration drift, **all tests pass**, frontend TypeScript/Vite build passes.
- [ ] Existing Phase 2 registration/login/logout and selected paths still work.
- [ ] Player profile, timezone and language save and return after refresh/re-login.
- [ ] Workout goals, experience and equipment save; Study and Learning goals/topics save, individually and in combination.
- [ ] Weekly availability validates durations, avoids duplicates, persists after refresh.
- [ ] Incomplete draft can be resumed; completed profile can be edited/recompleted.
- [ ] Private optional physique fields can be omitted, saved and cleared; no leakage to basic account API.
- [ ] Another registered user cannot see or edit the first user's onboarding data.
- [ ] Public `/admin/` remains unavailable; local admin remains loopback-only.
- [ ] GitHub updated with reviewed Phase 3 commit and version tag `v0.3.0` **only after local tests pass**.

## Verification honesty

At package creation, Python AST parsing and TypeScript TSX transpilation were successfully executed, and the ZIP archive was checked. Django and Vite end-to-end test commands could **not** run in the packaging environment because the pinned npm and pip dependencies could not be downloaded. The developer must run `scripts/test.ps1` on Windows and report output. Browser, PostgreSQL and live Google OAuth tests have not been executed here. Never represent a test file's presence as proof the test passed.

## Limitations and later phases

- Hindi preference does not yet translate all pages; accessibility settings only affect onboarding.
- No scheduling reminders, plan generation, workout recommendations or health-risk analysis.
- Private measurements are stored as database columns without application-level encryption at rest; local database access, backups, Windows permissions and future public deployment protections must be managed carefully.
- Admin is intentionally separate on localhost port 8001. No public hosting approved.
- Google ID sign-in is optional Phase 2 functionality and needs its own live credentials/test.
