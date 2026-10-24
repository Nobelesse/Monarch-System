# v0.4.3 — Cinematic App-wide UI

This update is a **working React interface upgrade**, not a screenshot placed over the app. All existing screens remain functional and the Django API / PostgreSQL models are unchanged.

## Included
- Full-width, layered animated Dark Abyss scene with the actual live Overview text, button and progress/health data.
- Matching sidebar, header, path cards, Account/Login, Onboarding, Workout, Roadmap and System Status treatments.
- Workout hero artwork, glass card system and a shaded procedural movement-model canvas in place of the former neon skeleton styling.
- A contextual pose photograph for **Seated knee raise** only, because that specific pose is represented by the supplied artwork.
- Motion effects stop under `prefers-reduced-motion: reduce`, and all buttons/inputs retain keyboard focus indicators.
- Real statuses, not invented workout totals, streaks, technique accuracy, or XP.

## Limitations
- Source artwork is derived from the **user-provided visual reference**, not genuinely 4K moving footage. Atmosphere uses CSS motion, particle drift and zoom/pan; it is **not** cinematic video.
- The procedural 3D exercise movement is a general movement-family orientation. A realistic, independently verified animated demonstration for every catalog exercise would require separately sourced/licensed, validated motion assets and is **not included**.
- No new package, external API, database migration or paid service.

## Windows upgrade
1. Back up project directory and database using existing scripts.
2. Extract the integrated ZIP into `E:\Projects\Monarch-System` using `Expand-Archive -Force`.
3. Run `scripts\test.ps1`, then `scripts\backend.ps1`, `scripts\frontend.ps1`, and `scripts\chrome.ps1` in separate terminals.
4. Browser-check login/registration, onboarding completion, saved paths, workout plan editing, exercise guide controls and navigation.

## Release verification
Full Django + Vite tests need execution on the user’s Windows dependencies. This container has no access to the project's pinned frontend dependency packages. No tests have been represented as passing unless actually executed.
