# Validation — Phase 1

Completed in the author environment:
- Python 3.12.14 Linux: six Django tests passed using an isolated in-memory SQLite database.
- Tests cover health success, sanitized database failure, absent admin route, read-only endpoints,
  explicit capability flags and password hashing.
- Django system check passed; no missing migrations (`makemigrations --check --dry-run`).
- pip dependency consistency check passed.
- All pinned Python requirements resolved as binary/universal wheels for CPython 3.12 Windows x64,
  including psycopg-binary. No C compiler is required for those wheels.
- Frontend TypeScript check and Vite production build passed under Node 22.23.2 (Linux).
- Clean npm lockfile install passed in the runner (npm 11.9.0); lock format is npm v3.
- Desktop browser visual inspection passed: dashboard, navigation and paths render correctly.
- Browser interaction checks passed: path selection, save, persistence after refresh, minimum
  one selected module, and explicit backend-unavailable diagnostics.

Not verified here:
- Execution of PowerShell scripts on Windows; no Windows runtime is available in this runner.
- Live PostgreSQL 17 migrations/health against the user's database. The user's earlier psql
  check established connectivity; installing this package must verify its own migration run.
- Python 3.12.10 runtime itself (same minor version; author runtime is 3.12.14).
- Physical-phone layout, touch interaction or mobile install. Responsive styles are included;
  actual device acceptance and PWA/public networking are later milestones.
- Public exposure, load capacity, account security or Google OAuth (not implemented).

Run README's acceptance checklist locally before starting Phase 2. Report exact error text
without credentials. Never interpret a successful SQLite test as a PostgreSQL integration test.
