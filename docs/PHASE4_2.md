# Monarch-System v0.4.2 — Fresh Login, Onboarding, Exercise Guides, Abyss Overview

This is an **integrated update to v0.4.1**. Prior phases and exercise drafts are preserved. No new database migrations.

## Change 1 — New opening must sign in

- App starts on **Account → Sign in / Register**, not the last player's Overview.
- An existing Django session is signed out via the **CSRF-protected** `/api/auth/logout/` endpoint on each full application load, even after browser restore.
- The sign-in button stays disabled until the startup session cleanup completes.
- React StrictMode shares the startup logout promise to avoid a second late logout interrupting a new login.
- Django sessions also expire on browser close; tokens are never placed in localStorage.
- **Trade-off:** A full browser refresh intentionally signs the user out. Sign back in; profile, workout plans and onboarding stay saved. Opening another app tab signs out sessions sharing that browser cookie.
- Google sign-in is also subject to this fresh-start behavior.

## Change 2 — Completed onboarding is remembered

- After successful login/Google login, the app fetches the authenticated `/api/onboarding/` state. If `completed=true`, it navigates to **Overview**, otherwise to the saved onboarding draft.
- Opening Onboarding as a completed player displays a **Completed & Saved** profile summary first, not Step 05.
- **Review / edit profile** explicitly opens the wizard. Valid edits maintain completion. Changing selected paths still reopens onboarding because new path goals/schedule may be required.
- The existing Django DB-backed `PlayerProfile.completed_at` remains the authority; no new localStorage flag.

## Change 3 — Interactive 3D movement-family previews

- In the **Workout schedule**, each exercise has a prominent **▶ 3D DEMO** button beside its name.
- In the **Exercise Codex**, each entry offers a 3D motion guide.
- All library entries use a locally rendered 3D joint model (XYZ skeleton; perspective and camera orbit), dynamically posing for **squat, hinge, push, pull, core, mobility** movement families.
- Users may **Play / Pause**, rotate the model, and change speed. `prefers-reduced-motion` is honored with a paused initial state.
- Beside the visual: movement cue, beginner caution and exercise-specific instructions from the existing library.
- **Important limitation:** The previews are representative **movement-family guides**, not medically validated, precise exercise-by-exercise biomechanical animations or certified tutorials. Exact technique can differ by exercise; do not treat them as a substitute for appropriate coaching.
- This is entirely local and adds no paid services or third-party visualization dependencies.

## Change 4 — Dark Abyss Overview

- Replaces the floating crown emblem with a generated original **abyss throne/portal illustration**.
- Animated neon portal halo, dark-violet game-inspired hero, improved emphasis and mobile behavior.
- Honors reduced-motion preference.

## Windows upgrade from v0.4.1

1. Back up `E:\Projects\Monarch-System` and run `scripts\backup_postgres.ps1` to create a verified readable database archive.
2. Stop all Monarch backend and frontend dev servers.
3. Extract `Monarch-System-v0.4.2-Dark-Abyss-Fixes.zip` **into your existing** `E:\Projects\Monarch-System` using `Expand-Archive -Force`.
4. `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\upgrade_phase4_2.ps1`
5. `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1`
6. Start `scripts\backend.ps1` and `scripts\frontend.ps1` in separate VS Code terminals and open Chrome at http://127.0.0.1:5173/.

Do not overwrite/delete `backend/config.local.json`, your database, `.venv`, or `frontend/node_modules`.

## Acceptance checklist

- [ ] Verified PostgreSQL backup before upgrade.
- [ ] Django checks and migrations succeed; no new migrations required.
- [ ] All old and new backend tests pass; frontend TypeScript/Vite build succeeds.
- [ ] Launching Chrome and reloading opens Account sign-in, not an auto-restored user.
- [ ] Register/login work; after completed onboarding, login goes to Overview.
- [ ] Incomplete onboarding resumes where last saved, without losing data.
- [ ] Onboarding completed summary appears; editing and saving does not require repeating completion.
- [ ] Existing workout plan, substitutions and logged-in ownership still work.
- [ ] Exercise demo appears beside name and in Codex; Play, Pause, Rotate and speed respond.
- [ ] Motion guides are clearly described as representative, not exact exercise-specific coaching.
- [ ] Overview shows dark abyss illustration instead of crown; mobile and reduced motion behave safely.
- [ ] After manual checks, commit and push v0.4.2 and the matching version tag.
