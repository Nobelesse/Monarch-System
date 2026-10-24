## v0.4.2 — Dark Abyss fixes

- Fresh start sign-in, completed onboarding summary, local animated 3D movement-family guide, premium neon hero (see [PHASE4_2.md](PHASE4_2.md)).

# Release version record

Windows target: Python 3.12.10, Node 22.23.2, npm 10.9.8, PostgreSQL 17.11.
Author test runner: Python 3.12.14 on Linux. Node 22.23.2 used for the final production build.
Django 5.2 supports Python 3.12 and PostgreSQL 14+; PostgreSQL 17 is within that range.
Vite 7 requires Node 20.19+ or 22.12+; this project narrows the release target to Node 22.
Exact installed Python dependencies: ../backend/requirements.txt.
Exact frontend dependencies and transitive resolutions: ../frontend/package-lock.json.

- react: 19.3.1
- react-dom: 19.3.1
- @types/react: 19.3.0
- @types/react-dom: 19.3.0
- @vitejs/plugin-react: 5.2.0
- typescript: 5.9.3
- vite: 7.3.7

Sources:
https://docs.djangoproject.com/en/5.2/releases/5.2/
https://v7.vite.dev/guide/migration

Compatibility is not a claim of identical OS behavior. Windows first-run remains a required acceptance step.

## Phase 2 dependencies
- Django and djangorestframework stay pinned to the validated Phase 1 versions.
- Added `google-auth==2.41.1` for verified Google ID tokens and `requests==2.32.5` for Google certificate transport.
- React/Vite versions remain unchanged; frontend application release version advances to `0.2.0`.
- Check `scripts/check_versions.py` for the Python 3.12 / Node 22 policy, unchanged from Phase 1.

## v0.2.1 (hotfix)
- No dependency version changes. Fixes browser-origin CSRF handling and frontend API error messages.

## v0.3.0 — Phase 3
Integrated onboarding, model migration 0003, server-side validation, private optional physique data, draft/complete flows, frontend screens and tests. See docs/PHASE3.md. Tests on the developer Windows host remain pending.

## v0.4.0 — Phase 4
28 manually curated exercises, core.0004 migration, account-owned plan generation and substitutions, conservative rest-oriented scheduling, Workout UI and 20 additional test cases. Dependency versions retained from v0.3.0. Local Windows validation required. See docs/PHASE4.md.

- **v0.4.1** — Phase 4 refinement: curated catalog expansion, selectable focus/pace, smarter splits, editable account-owned workout drafts, refreshed interface. Local Django/React/PostgreSQL validation pending.

- `v0.4.3`: whole-app cinematic Dark Abyss React redesign, asset-backed hero, procedural anatomical motion previews, contextually matched pose reference; no API or migration changes.


- v0.4.7 adds contextual offline motion guidance improvements without schema changes.