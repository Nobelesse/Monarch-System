# Phased delivery and acceptance
1. Foundation: isolated project, locked dependencies, UI shell, PostgreSQL configuration,
   diagnostics, migration and reproducible Windows instructions. This release.
2. Accounts: registration/login/logout, Google OAuth configuration, ownership permissions,
   separate local-only authenticated admin. Accept only after cross-user isolation checks.
3. Onboarding: selected modules, goals, experience, equipment and schedule stored per account;
   private optional physique inputs and accessibility preferences.
4. Workout engine: reviewed exercise library, substitutions and schedule generation;
   validate suitability rules, incomplete inputs and limitations.
5. Workout execution: sets, reps, weights, rest timers, session history and feedback;
   prevent duplicate submissions and retain completed history.
6. Game system: XP ledger, ranks, quests, optional safe game penalties and recovery rules;
   award completion once, keep module progression independent.
7. Study/learning: goals, sessions and learning plans; support individual or combined modules.
8. Adaptation: performance/recovery-informed suggestions with user review; history and insights.
9. Mobile/public access: installable PWA, stable HTTPS URL and QR, OAuth callback deployment,
   connection-loss behavior. Check free-host limits and admin isolation before exposure.
10. Release: backups and restore drill, security and mobile checks, documented deployment,
    account/data export controls and final integrated package.

Deliver each phase as a complete integrated ZIP, with migrations, compatible pinned versions,
Windows commands, change log and honest verification record. No surprise global upgrades.
Security updates are reviewed and tested rather than permanently freezing vulnerable versions.

## Current release notes
- **Phase 1:** Completed and retained from user-supplied source.
- **Phase 2:** Registration, login, account-owned paths and local admin implemented; user confirmed 6 browser/manual checks and Phase 2 GitHub tags are pushed. v0.2.1 full automated rerun and optional live Google verification are not documented as passing.
- **Phase 3:** Code delivered in v0.3.0 with database migration, API and five-step onboarding interface. Final PostgreSQL/Windows verification and user acceptance pending; see docs/PHASE3.md.
