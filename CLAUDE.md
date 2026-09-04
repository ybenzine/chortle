chortle - Household Chores Tracker

Documents
- `_docs/process.md` - how work is organized
- `_docs/plan.md` - scope/decisions 
- `_docs/backlog.md` - implementation backlog.

Rules
- Dependencies are added in `pyproject.toml`. Do not add one without asking.
- Use `uv` for all dependency and environment management.
- Configuration comes from the environment. A new setting means a new env var and line in `.env.example`, never a hardcoded value or a checked-in secret.
- Every behavior change must be covered by tests
- Run `uv run pytest` before considering a change complete. All tests must pass.
- Tests live alongside the code they cover (e.g. `core/tests.py`, or a `core/tests/` package if it grows). Use `pytest-django` style (`@pytest.mark.django_db`) rather than `django.test.TestCase` unless there's a specific reason to prefer the latter.
- GitHub issue titles do not repeat the issue number. GitHub already shows it.

Commands
- Run the dev server: `uv run python manage.py runserver`
- Run tests: `uv run pytest`
- Run migrations: `uv run python manage.py migrate`
