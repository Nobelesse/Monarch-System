# Human-first Exercise Form Studio — v0.4.4

## Why the old demo was replaced

The old canvas model was a generic joint/capsule mannequin. In some exercises (e.g., countertop push-up) it did not actually depict the named move. For a beginner trying to imitate it, that is misleading. This release **removes the generic animated mannequin entirely**.

The new human-first viewer opens beside an exercise in the **Workout schedule** and **Exercise Library**. It supports:

- Matching per-exercise human `.mp4` / `.webm` instructional video clips played in-page with native controls, loop and speed adjustment.
- Matching per-exercise `.glb` rigged human animations with orbit rotation using an *optional* Google `<model-viewer>` web component, loaded only when a `.glb` clip is configured. The current component loader needs internet access; video player and the rest of Monarch-System work locally/offline. **A GLB must contain the correct animation; an idle mesh is not a demonstration.**
- A quick local video preview for learners who possess a clip. The video stays in their browser and isn't sent to the backend; the preview is not persisted.
- An exact-name YouTube search for external instructor footage; **search results are not verified** by Monarch-System.
- Exercise-specific text from the existing Django catalog, with general movement-family caution cues.
- A static human pose reference for **Seated knee raise only**, correctly labeled as a still—not animated instruction.

**v0.4.5 ships no copied video files, but does provide six in-app YouTube embeds of real instructors for exact exercises (online access required).** This is the infrastructure for high-quality human demonstrations, not a claim that 63 verified demonstrations now exist. For an exercise without a curated web embed or a locally supplied video/rig, the interface clearly says a demonstration is not installed. We do not show inaccurate 3D motions to fill a gap.

## Add a professionally recorded / appropriately licensed exercise demo

1. Obtain an authentic `.mp4`, `.webm` or **animated** `.glb` for exactly the exercise you intend to demonstrate, with redistribution rights (or footage you made yourself).
2. Identify its slug from the Workout exercise data (e.g. `counter-pushup`, the slug of **Countertop push-up**).
3. From the VS Code project directory, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\add_human_demo.ps1 -Slug "counter-pushup" -File "C:\Videos\counter-pushup.mp4" -Credit "Original demonstration; filmed by me" -IHaveRights
```

4. Restart/refresh the Vite app. Open Workout → the exact exercise → `HUMAN FORM GUIDE`. The correct media plays automatically. No Django migration needed.
5. Exercise files live in `frontend/public/human-demos/media/` and the exact-match manifest is `frontend/public/human-demos/manifest.json`.
6. Only distribute the demos via GitHub if the license allows it. Copyrighted third-party videos must not be committed without permission. Avoid sharing minors, private training footage, or identifying personal information.

The manifest schema is `{ "version": 1, "demos": [{ "slug": "counter-pushup", "filename": "counter-pushup.mp4", "kind": "video", "credit": "Creator", "checked": false }] }`.

## Quality requirements before shipping a demo to beginners

- Exercise name and equipment exactly match the recording.
- Subject is clearly human with an unobstructed front and/or side view.
- Full starting position, controlled repetition, and finishing position are visible.
- A qualified trainer has reviewed technique, range of motion, and the applicability of variations.
- If animation is rigged, inspect skeleton and foot/hand contacts through its full loop, not just its appearance.
- Verified training clips should be explicitly reviewed and only then change `checked` to true. A developer must not silently mark them as reviewed.

## Future assets

Suitable sources for creating original/CC0 rigged 3D humans include Mesh2Motion (CC0 motion assets) and OpenGym3D (human movement retargeting workflow), but **their external files are not bundled**. Verify each downloaded asset's license and exercise-specific match before use.

## Smoke checks

- All 81 Django tests from the previous version still need to pass.
- TypeScript/Vite build.
- Reopening Workout library and plan displays no generic mannequin or stick-figure motion anywhere.
- Exercise without footage shows honest “exact demonstration not installed” UI with its original instructions.
- Seated knee raise still shows the actual human pose reference, correctly labeled as a still.
- File picker previews MP4/WEBM locally; clearing it reverts to installed media or placeholder.
- Adding a licensed exact-matched clip using `add_human_demo.ps1` makes it available for that exercise only.
- Malformed manifest entries do not load arbitrary remote URLs or incorrectly match a different exercise.
