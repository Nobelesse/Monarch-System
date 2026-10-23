# Phase 4 — Workout Engine (v0.4.0)

**Status:** Implemented; requires the developer's Windows / PostgreSQL / browser validation before release sign-off.

## What Phase 4 adds

- Additive migration `core.0004_workout_engine`: versioned, seeded, manually authored 28-exercise catalog; one current account-owned workout draft; weekday sessions; item prescriptions and recorded substitutions.
- A logged-in player must select the Workout path and complete Phase 3 onboarding before generation.
- React **Workout** sidebar: exercise library, movement-exclusion checkboxes, explicit limitation acknowledgement, one-click generation/regeneration, persisted daily draft, alternatives picker. No third-party API or paid service.
- The Workout goal is displayed but **not** interpreted as a medical or AI diagnosis. The generator uses the saved experience, actual selected equipment (plus bodyweight), selected Workout weekdays/duration, and broad exclusion tags (knee, wrist, floor, overhead, impact).
- Deterministic conservative scheduling: maximum 3 nonadjacent strength days/week, remaining selected days used for gentle movement/recovery; beginner strength draft capped at 60 min, intermediate 75 min, advanced 90 min, recovery day capped at 30 min; short days receive fewer exercises.
- All generated prescriptions are **suggestions** (basic exercise repetitions/rest), not medically personalized. Each movement has plain-language instructions; stop for discomfort/pain, and consult a qualified professional about injuries or health risks.
- Substitutions use only the same movement family, permitted equipment and experience, and exclusions. Stored server-side against the account owner. No user IDs accepted from browsers.
- Idempotent when source preferences/exclusions are unchanged unless user explicitly requests regeneration. A subsequent onboarding edit marks the old plan stale until regenerated. Regeneration **replaces** the current draft; session history is not implemented until Phase 5.
- Django session authentication, CSRF, the `/admin/` isolation policy, and account permissions are preserved.

## API (same-origin, authenticated)

| Method | Endpoint | Behavior |
|---|---|---|
| GET | `/api/workout/library/` | Active reviewed catalog and supported caution tags |
| GET | `/api/workout/plan/` | Only this user's current draft, stale flag, or null |
| POST | `/api/workout/plan/generate/` | Generate/reuse/regenerate account-owned draft |
| GET | `/api/workout/items/<id>/alternatives/` | Same-pattern permitted alternatives for user's item |
| POST | `/api/workout/items/<id>/substitute/` | Replace only owner's item with an allowed slug |

Sample generate JSON: `{"avoid_tags":["floor","impact"],"acknowledged":true,"regenerate":false}`. A forced regeneration changes `regenerate` to `true`. Substitution JSON: `{"exercise_slug":"band-row"}`. Unknown JSON fields are rejected. CSRF required for POST. Nonmembers of Workout path receive HTTP 403; guests receive HTTP 401; other users' items return 404. Data is tied to the session, not caller-supplied IDs.

## Important limitations

- Broad movement-exclusion labels do **not** constitute medical screening and cannot capture every injury, discomfort, exercise contraindication, or disability.
- This is a curated *starter* library of 28 common movements with coaching cues, **not** expert-certified exercise prescriptions. No fabricated physiological outcomes, caloric burn, personal trainer endorsements or predictive modeling.
- Free-text goal is stored and shown but not semantically classified. Specific sports/rehabilitation targets, prenatal/rehabilitation plans, and advanced individualized programming are **not** supported.
- No set completion, weights, timers, history or adaptive recommendations yet (Phase 5/8). No XP or game penalties (Phase 6).
- No video instruction or offline installable PWA (Phase 9).

## Phase 3 → Phase 4 Windows upgrade

**Backup first.** A verified Phase 3 archive existed as `E:\Projects\Monarch-System-Phase3-20261022-220323.backup`, but take a new pre-Phase 4 backup too.

1. Stop backend/frontend/admin terminals using Ctrl+C. Optionally copy `E:\Projects\Monarch-System` to a dated backup folder.
2. Extract full `Monarch-System-Phase4-v0.4.0.zip` into `E:\Projects\Monarch-System` with `Expand-Archive -Force`.
3. Run the newly included `scripts\backup_postgres.ps1` **before** the upgrade script, and do not proceed unless it prints `Verified readable PostgreSQL archive`. It contains source code only; ignored `backend/config.local.json`, `.venv`, database and installed npm packages stay in place.
4. Run:

```powershell
cd "E:\Projects\Monarch-System"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\backup_postgres.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\upgrade_phase4.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

5. In two separate VS Code terminals, run `scripts\backend.ps1` and `scripts\frontend.ps1`, then use `scripts\chrome.ps1`. Browser URL: `http://127.0.0.1:5173/` → login → select Workout path → complete Onboarding → open **Workout**.
6. If npm install was interrupted and `tsc` isn't found, stop the frontend Node process, run `cd frontend; npm.cmd ci; npm.cmd run build`. Existing pins do not change.

## Manual Phase 4 acceptance checklist

- [ ] A new readable pre-migration PostgreSQL dump was created; upgrade script seeded 28 exercises.
- [ ] Django migration/model checks, **66 total tests** (46 retained + 20 new) and Vite production build pass on Windows.
- [ ] Existing register/login/logout, selected paths and Phase 3 onboarding are unchanged and working.
- [ ] Workout navigation is restricted appropriately; non-Workout and guest users are denied API access.
- [ ] Onboarding completion and scheduled Workout day(s) are required for generating a draft.
- [ ] Generated weekdays, displayed goal, experience, eligible equipment and availability match onboarding.
- [ ] A beginner's plan doesn't schedule more than three strength days in a week; no adjacent hard days are suggested; exercise duration is capped conservatively.
- [ ] Excluding a movement tag removes exercises bearing that tag (including alternatives), and validation blocks unsupported/excessive request fields.
- [ ] Reload/login persists the plan, and safe substitutions persist after refresh.
- [ ] Another account cannot read or edit the first player's plan; public `/admin/` remains 404.
- [ ] Editing Workout onboarding makes an existing plan stale; regeneration updates its contents without duplicating plans.
- [ ] Reviewed staged Git files contain no secrets, Phase 4 commit pushed, `v0.4.0` tag created **after** successful verification.

## Verification record

- At ZIP build: Python AST compile and TSX parse/transpile verified. Core scheduling algorithms were tested in isolated pure-Python checks and the archive's contents/CRC validated.
- **Unavailable here:** full Django test suite and Vite production compilation, due to unavailable pinned dependency downloads. Windows test outcome and real browser/PostgreSQL behavior still require evidence. Do not interpret tests being present as tests having passed.
