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
