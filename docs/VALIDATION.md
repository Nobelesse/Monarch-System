# Phase 2 validation record

The Phase 2 ZIP was created from the user-uploaded Phase 1 source archive on 20 October 2026.

**Checks performed during packaging:**
- `python -m compileall` for modified backend Python files: passed (syntax only).
- ZIP structural checks: see packaging notes / archive validation.

**Unable to execute here:**
- Django unit/integration tests. Django and Google auth dependencies were not installed in the packaging environment; outbound package repository resolution was unavailable.
- Frontend TypeScript and Vite production build. `npm ci` could not complete from the locked dependency registry in this offline environment. No passing frontend build is claimed.
- Windows PowerShell scripts and migrations against the owner's live PostgreSQL database.
- Real Google OAuth sign-in: needs the owner's configured OAuth client and real browser environment.

Run `scripts/test.ps1` locally after `scripts/setup.ps1`, report actual results, and fix regressions before treating Phase 2 as accepted. Maintain the original Phase 1 test evidence as historical evidence, not new verification.

## v0.2.1 — 22 October 2026
The owner reported all **26/26 backend tests passed** and a successful Vite production build for v0.2.0, but registration in Chrome displayed `Unexpected token '<', '<!DOCTYPE ... is not valid JSON` and did not create an account.

Root cause identified in source: Vite proxies browser POST requests between different port origins; Django `CSRF_TRUSTED_ORIGINS` was not configured for the Vite page origin. The previous Django tests did not supply the browser `Origin` header.

This hotfix adds three CSRF regression/security tests and validates/handles non-JSON responses in the frontend. These new tests **still require execution on the owner's Windows environment**; their passing status is not yet reported. The v0.2.0 26-test pass does not establish a v0.2.1 29-test pass.


## v0.3.0 validation state
Static Python AST parsing and TypeScript TSX transpilation were executed during packaging. Full Django tests and Vite production build were NOT executed in this environment (dependency downloads blocked). Run `scripts/test.ps1` and the manual checklist in `docs/PHASE3.md` on Windows before tagging the release.

## Phase 4 (v0.4.0)
66 test functions defined in core/test suite (46 from earlier phases + 20 workout tests). The Phase 4 authoring environment verified Python syntax and TypeScript TSX parsing, but Django and Vite production testing require the user's local dependency environment. See docs/PHASE4.md.

## v0.4.3 visual overhaul
Python backend `compileall`: checked in packaging environment. TypeScript/TSX syntax transpilation: checked using local TypeScript installation. Image references and ZIP integrity: checked. Full Django tests, real-browser interaction and pinned-dependency Vite build require the user's existing Windows installation; do not assume they passed.
