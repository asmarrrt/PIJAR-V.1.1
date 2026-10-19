# PIJAR Implementation Status

Status: IMPLEMENTED / STATICALLY REVIEWED. Runtime verification is BLOCKED in the current environment because Flask and the required Flask extensions are not installed. pytest is available but the application test suite cannot import until dependencies are installed.

## Completed in source
- Application factory, configuration, extensions, role model.
- Teacher registration/login/logout and role guards.
- Teacher dashboard, exam creation, publication/closure, private question bank.
- Four question types and question snapshots for historical exam integrity.
- Student join flow, attempt creation, server-side timer, autosave endpoint, submission and server-side scoring.
- Manual essay grading and result views.
- Superadmin dashboard and teacher activation/deactivation.
- Responsive UI and CSRF-enabled forms.
- requirements.txt, .env.example, README.

## Pending runtime verification
- Install requirements and run pytest.
- Exercise browser flows against a running Flask/PostgreSQL environment.
- Migration files are included; run `flask --app run.py db upgrade` after dependencies are installed.

## Important implementation note
Production should use PostgreSQL. SQLite is configured as the default local development database only.
