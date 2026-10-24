# Monarch-System v0.4.5 — Real Human Instructor Videos

## Problem addressed
v0.4.4 removed the mannequin but shipped an **empty human-demos/manifest.json**. Consequently, the user's Countertop push-up screenshot showed **EXACT DEMONSTRATION NOT INSTALLED**. The app required the user to supply a video, which did not meet the request.

## Solution
When an exercise has no local clip configured, the app now automatically embeds the publisher's official YouTube video for a curated list of exact exercises. **Countertop push-up** (`counter-pushup`) defaults to a real human doing Counter Push-Ups from KUTV — visible in the embedded guide, no manual download or video picker necessary. Online access is required. If the embed is unavailable or blocked in a user's browser/network, **Watch on YouTube** always links to the original page. We do not mirror, download, or redistribute anyone's YouTube footage.

| Monarch catalog slug | Original video | Publisher | URL |
|---|---|---|---|
| counter-pushup | Counter Push-Ups | KUTV 2 News Salt Lake City | https://www.youtube.com/watch?v=u883qxjOffE |
| wall-pushup | Wall Push Up Exercise | Margaret Martin, Physical Therapist | https://www.youtube.com/watch?v=lIRpibTFB9I |
| floor-pushup | Muscle Strengthening at Home — Push-ups | CDC | https://www.youtube.com/watch?v=pONDDchJjOI |
| bird-dog | How to Do the Bird Dog Exercise | Hinge Health | https://www.youtube.com/watch?v=xEDnlOxeJH4 |
| glute-bridge | How to Do a Glute Bridge Exercise | Hinge Health | https://www.youtube.com/watch?v=PhTDzR0TpZs |
| chair-sit-to-stand | Chair Standing Techniques | Front Row with Ed and Elizabeth | https://www.youtube.com/watch?v=1wAKXdS0Ark |

Exact slug mapping resides in `frontend/src/curated-human-videos.ts`. The guard script `scripts/verify_curated_videos.py` checks all IDs, validates YouTube ID syntax, and confirms every mapped exercise exists in the actual Django catalog migrations. Those static checks do not establish that YouTube permits embedding or that a video is clinically reviewed. **In the Windows Chrome acceptance check, click the video to verify actual motion and match with the written exercise title.** Videos can be unavailable due to the user's network restrictions or publisher embedding settings. The direct original video links provide the workaround.

### For all remaining exercises
The exercise names, movement notes and local video player still work. We do not auto-assign a generic motion clip to another named exercise. New demos require researching the exact exercise and confirming licensing/embedding and appropriate form. Users can preview and install video footage they have rights to using `scripts/add_human_demo.ps1`.

### Limitations
This release offers **real 2D human instructional videos**, not 3D anatomical motion-capture for every one of 63 exercises. Accuracy of form should still be checked with a knowledgeable trainer; videos are for general education, not a substitute for individualized instruction.

### Windows upgrade and acceptance
1. Back up the existing project, verify PostgreSQL archive if not recently done, and extract the integrated v0.4.5 ZIP over the project directory.
2. Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1` (81 Django tests, 1 static media-index check, Vite build).
3. Restart backend/frontend dev servers; in Chrome log in -> Workout -> Countertop push-up -> **View human guide**.
4. Verify a human demonstrator is visible and moves when playing, not the “not installed” placeholder.
5. Test the Watch on YouTube button, and confirm that no video or local credentials are published to GitHub.
6. Do not publish the release tag until the tests and manual browser checks pass.
