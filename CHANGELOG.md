## v0.4.2 — Dark Abyss and Exercise Guidance

- Fresh-start sign-in: clear prior Django session at every app load and expire browser cookies on browser close.
- Completed onboarding routes to Overview and opens a saved-profile summary, while incomplete drafts resume.
- Local interactive 3D movement-family animations beside exercise names and in Codex.
- Overview replaces floating crown with original generated dark-abyss throne/portal art.
- No new database migration or paid external services.
- Regression tests for persistent completion and session-cookie behavior.

## 0.4.1 — Phase 4 refinement release (2026-10-22)

- Redesigned Workout UI: responsive command center, animated crest, focus and pace cards, weekly day tabs, per-item controls, filterable/searchable exercise codex, reduced-motion behavior.
- Expanded the curated, manually written exercise catalog from 28 to 63 entries (additive migration 0005).
- Added explicit balanced/strength/endurance/mobility focus and easy/standard pacing; upper/lower/full-body splits and conservative session limits.
- Added bounded set/repetition/rest editing and same-session exercise ordering; persisted to the owner's workout draft.
- Preserved session auth, CSRF, per-account data and existing Phases 1–3 features.
- Added 12 backend regression tests; complete suite contains 78 tests awaiting Windows execution.
- No workout completion, history, XP, medical diagnosis or claims of clinical suitability.

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

## 0.3.0 — Player onboarding
- Add five-step private, resumable onboarding for selected paths.
- Add four per-account models and additive PostgreSQL migration core.0003_onboarding.
- Add authenticated `/api/onboarding/` GET/PUT with CSRF, type validation and atomic writes.
- Add per-path goals, experience, equipment/topics and weekly availability.
- Add optional private height/weight, clearing and separate storage.
- Add onboarding regression/security tests and phase-specific Windows upgrade helper.
- No dependency upgrades. Full Windows/PostgreSQL and frontend build verification pending.

## v0.4.0 — Phase 4 Workout Engine (22 October 2026)
- 28-entry manually curated starter exercise library with descriptions and broad caution tags.
- Django models, additive migration and exercise seed; owner-scoped current workout drafts and day/prescription records.
- Deterministic, conservative draft generation informed by onboarding experience, equipment and weekly availability; broad exclusions, rest/mobility days and duration caps.
- Account-safe same-movement substitutions, CSRF protection, stale detection and idempotent reuse.
- React Workout interface, Windows backup/upgrade scripts and 20 new automated test cases.
- Phase 5 remains responsible for actual workout execution/history; Phase 6 for XP/ranks.
