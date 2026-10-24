# Monarch-System 0.4.6 — Offline Exercise Engine Prototype

## What this release actually implements

- Offline, browser-canvas 3D-position-based animation engine **without remote media, CDN scripts, videos or exercise files**.
- Explicitly keyed **63 catalog exercise IDs**, mapped into **39 illustrated movement presets**. These are simplified 3D-position animations rather than rigged photorealistic human assets or motion capture. Several movements share an archetype (e.g. equipment variants). Not a medically validated demonstration of exact form.
- Animated figure with basic skin, clothing, face, a few props and an adjustable orbit camera. It is **not yet the lifelike trainer requested**. Do not misrepresent it as 4K motion-capture content.
- Per-exercise written steps and caution cues from the existing manually authored catalog.
- A local Set & Recovery Coach in the saved workout plan: actual prescribed sets/reps, rest between sets, configurable post-exercise transition (30–120 s), visible timer with pause/resume/skip/reset and manual set completion. The coach does not detect repetitions, store workout history or award XP.
- **No backend API or database migration change.** Account ownership, registration, onboarding, exercise plan and catalog are retained from 0.4.5.

## Explicit scope still outstanding

The requested **photorealistic, anatomical, 4K-HD, exercise-accurate rigged 3D trainer for each of the 63 movements** is NOT delivered. A true solution requires (1) permission-cleared, realistic rigged human model(s), (2) 63 specific and correctly retargeted motion clips incl. equipment, (3) safety/biomechanical review by an instructor, (4) a bundled, offline-capable Three.js/WebGL player, and (5) detailed QA for every movement and device. A procedural position-driven illustration does not substitute for these steps.

Potential open-source R&D starting point: OpenGym3D (MIT project code; individual motion assets have **separate license rules**, and drafts without motion assets are not public demonstrations). Its asset pipeline verifies actual GLBs and motion quality. Do not silently redistribute unverified animation data.

## Local checks

Run from `E:\Projects\Monarch-System` after extracting:

```powershell
.\.venv\Scripts\python.exe scripts/verify_offline_demos.py
node scripts/verify_offline_renderer.cjs
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\upgrade_offline_motion.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

Run the app in Chrome with the existing `backend.ps1`, `frontend.ps1`, `chrome.ps1` scripts. Test both the Training planner and Exercise codex, turn **Wi-Fi off** during a demo, and manually check the set/break countdown. These tests remain pending until run on the user's Windows machine.

## Quality and safety

Motion is illustrative, not a substitute for a qualified instructor. Do not assume the avatar demonstrates safe anatomical technique, especially with injuries or equipment. Stop for pain, dizziness, or concerning symptoms. Start with manageable loads and consider professional assessment where needed.
