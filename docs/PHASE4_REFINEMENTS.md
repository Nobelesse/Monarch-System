# Monarch-System Phase 4 refinements — v0.4.1

**Status:** Integrated code complete. Awaiting Django/PostgreSQL tests, TypeScript/Vite production build and user browser verification on Windows. No Phase 5 execution or XP features included.

## Features

- 63 curated exercise entries (28 retained, 35 newly seeded) grouped into squat, hinge, push, pull, core and mobility. Equipment and experience filters continue to apply.
- Explicit training focus: **balanced**, **strength**, **endurance**, or **mobility**. These are user selections; the saved free-text goal is shown but **not** automatically interpreted for clinical/training suitability.
- Training pace: **easy** caps drafted strength sessions at 40 minutes, gentle movement at 20 minutes and limits suggested strength sets to two; **standard** uses the existing caps (60/75/90 minutes by experience, 30 minutes for gentle movement).
- Nonadjacent strength scheduling continues to apply, up to three weekly strength days (two for endurance/mobility focus). One strength day uses full-body; two use upper/lower; three use upper/lower/full-body. Insufficient equipment or movement restrictions may reduce the available movements, not silently violate those restrictions.
- Bounded server-side prescription editor: 1–4 sets (max 2 for recovery), curated repetition presets, 30–120 sec rest. Users can move an exercise up/down **within its existing day**, or replace it only with another exercise from the same movement group that satisfies the existing filters.
- Changes are account-owned and server-stored. Missing/invalid payload fields are rejected; CSRF applies to every edit; another account cannot access plan items. Changed onboarding flags old drafts stale; editing is blocked until regeneration.
- Modern dashboard: focus cards, timeline-day switcher, prescription editor, exercise swapper, library search/filter, stat cards, responsive motion and reduced-motion accessibility option.

## Additive migration

`core.0005_workout_refinements` adds `WorkoutPlan.focus_mode`, `WorkoutPlan.pace`, `WorkoutSession.theme` and 35 new catalog records. Existing plans remain; because the catalog version changes, old drafts may display **stale** until regenerated. Regeneration intentionally replaces the *draft*; actual completed workout history starts in Phase 5.

## Windows upgrade — full integrated ZIP

Before upgrading, create/verify the PostgreSQL archive and backup your project folder. Do not reset PostgreSQL, commit local config, or delete your virtual environment.

```powershell
cd "E:\Projects\Monarch-System"
Expand-Archive -LiteralPath "$env:USERPROFILE\Downloads\Monarch-System-Phase4-v0.4.1-Refined.zip" -DestinationPath "E:\Projects\Monarch-System" -Force
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\backup_postgres.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\upgrade_phase4_refinements.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

The upgrade script applies any missing 0004 and 0005 migrations and checks the new exercise count. If upgrading from Phase 3, both migrations apply; if from Phase 4, only 0005 should apply. `scripts/test.ps1` must report **78 tests passed** and a successful Vite build before GitHub release.

Start in separate VS Code terminals:

```powershell
cd "E:\Projects\Monarch-System"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\backend.ps1
# Terminal 2:
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\frontend.ps1
# Terminal 3:
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\chrome.ps1
```

Open `http://127.0.0.1:5173/`, sign in, finish onboarding if needed, select **Workout**. Existing users with v0.4.0 plans should regenerate their stale draft after reviewing new training focus/pace settings.

## Manual release checklist

- [ ] Verified pre-upgrade readable database backup and dated source folder backup.
- [ ] Migration `0005_workout_refinements` applied; active catalog count at least 63.
- [ ] 78 backend tests pass, Django system and migration checks pass, Vite build passes.
- [ ] Phase 1–3 registration, login/logout, profile, saved preferences and account separation remain working.
- [ ] Focus modes and easy/standard pace generate expected sessions and persist through refresh.
- [ ] Upper/lower/full-body split aligns with Workout onboarding days and avoids adjacent strength days.
- [ ] Equipment requirements, experience levels and movement exclusions are respected.
- [ ] In-line sets/reps/rest changes persist; invalid values show errors.
- [ ] Exercise swap and up/down reordering persist, and cannot access another user's items.
- [ ] Library search, movement/equipment filters and responsive mobile/reduced-motion behavior work.
- [ ] Revisit onboarding → draft stale → regenerate; no completed workouts or XP falsely shown.
- [ ] GitHub main commit/tag `v0.4.1` pushed only after checks pass; no secrets staged.

## Limitations & honest validation

This is a general physical activity planning tool, not medical screening or individually certified programming. Stop for discomfort and seek qualified advice for health-related restrictions. Workout execution, feedback, sets actually completed, weights and history are not in scope until Phase 5.

**Verification performed in the build environment:** Python AST/bytecode compilation, TypeScript TSX syntactic transpilation, helper logic checks, package-content and CRC checks. **Not verified here:** complete Django suite, PostgreSQL migration on the user's machine, full Vite production build or live browser behavior; pinned dependencies cannot be downloaded here.
