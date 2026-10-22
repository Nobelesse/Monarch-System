# Architecture and decisions

## Phase 1 runtime
Browser -> Vite at 127.0.0.1:5173 -> /api proxy -> Django at 127.0.0.1:8000 -> PostgreSQL.
Vite forwards API requests and rewrites the host to the backend. No permissive CORS policy.
The React build is static assets; Vite is a development tool, not an additional Node API.
The release uses custom CSS to minimize dependencies; Tailwind is not needed for this shell.
No third-party fonts, image CDN, analytics, tracking or paid services are used.

## API contracts
GET /api/health/: 200 {status:ok, api:online, database:connected, version:0.1.0}.
Database failure: 503 {status:degraded, api:online, database:unavailable, version:0.1.0}.
No database exception text or password is returned.
GET /api/system/: name, phase, version, supported module names and false flags for
available authentication/public access. POST is rejected with 405 on both routes.

## Data design
Implemented: core.User extends AbstractUser in initial migration, plus Django's auth,
permissions, groups and session schema. This avoids changing user models after launch.
Planned (not migrated yet): PlayerProfile 1:1 User; ModulePreference per user;
Exercise; WorkoutPlan; WorkoutSession; ExerciseSet; Quest; QuestCompletion;
immutable XP ledger with a unique award key; StudySession; LearningGoal.
Later user-owned APIs must scope queries by authenticated user, not client-supplied owner IDs.
Health/profile/photos require private access. Photos will be optional, with no body scanning.
Store UTC timestamps and display the user's chosen timezone; initial default is Asia/Kolkata.

## Admin boundary
No admin interface is implemented in Phase 1. Phase 2 will use a distinct loopback-bound
listener and URL configuration with authentication. The public listener must have no admin
routes. Hiding navigation or trusting proxy-supplied IP headers is not sufficient.
Future tunnels may expose only the public listener, never admin or database ports.

## Configuration and security
Local credentials live in backend/config.local.json, generated through a masked terminal
prompt and excluded from Git/ZIPs. They are plaintext on disk: keep the Windows user profile
private and never share this file. No default credential is shipped.
Django DEBUG=False, restricted hosts, CSRF/session/security middleware and default-deny DRF
permissions are established. HTTPS cookies, throttling, account verification and production
serving will be finalized before public access; Phase 1 is not production approved.
A dedicated database owner account is used for local migrations; separate deployment and
runtime privileges should be reviewed before production.
The development-only terminal.local allowed host supports the author's preview environment;
it does not widen the loopback binding in the Windows startup scripts.

## Product constraints
Free-first; no mandatory paid AI/API. No promise of unlimited free hosting.
PC hosting means the app is unavailable when the PC sleeps, is off or loses internet.
A stable public URL is needed for a reusable QR and Google OAuth callbacks.
Body appearance is optional; training selection also requires age, experience, limitations,
availability and equipment. Fitness difficulty is independent of game levels.
Rest/recovery compliance earns credit. No punishment exercise, food restriction or sleep loss.
Early exercise content requires review before daily-use training recommendations.

## Open decisions for Phase 3
Age audience, fitness onboarding details, language options, initial user group, visual feedback,
and preferred optional game penalties. Do not infer the owner's health or body measurements.

## Phase 2 delta (v0.2.0)
- Public browser and JSON API remain same-origin through the existing Vite `/api` proxy.
- Auth uses Django's built-in server-side sessions and CSRF. The browser does **not** keep bearer access tokens in `localStorage`.
- Models: concrete custom `User` with case-insensitive username/email uniqueness; `PlayerPaths` (one account -> current modules); `SocialIdentity` (provider + immutable provider subject).
- Authorization: all personal reads/writes derive user from verified Django `request.user`; no caller-provided owner ID is accepted.
- Google: optional Google Identity Services `credential` -> verified ID token -> either social-subject lookup or new unlinked user. Same-email existing accounts must explicitly link while already signed in.
- Admin: `config.admin_settings` uses an independent `config.admin_urls`, loopback remote-address guard and admin-only cookies on port 8001. Main port 8000 has no `/admin/` route.
- Onboarding, detailed goals/equipment, sensitive physique data and game progression remain later phases; do not prematurely introduce them in Phase 2.
