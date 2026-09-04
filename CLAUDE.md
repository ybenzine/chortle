# chortle

Household Chores Tracker. See `_docs/plan.md` for scope/decisions and `_docs/backlog.md` for the implementation backlog.

## Rules for agents working on this repo

- **Every behavior change must be covered by tests.** New models, views, forms, template logic, and pure functions (e.g. recurrence-date calculations) all need corresponding tests before the work is considered done — not just for milestones explicitly labeled "with unit tests" in the backlog.
- Run `uv run pytest` before considering a change complete. All tests must pass.
- Tests live alongside the code they cover (e.g. `core/tests.py`, or a `core/tests/` package if it grows). Use `pytest-django` style (`@pytest.mark.django_db`) rather than `django.test.TestCase` unless there's a specific reason to prefer the latter.
- Use `uv` for all dependency and environment management (`uv add`, `uv run ...`) — don't install packages into a bare venv or edit `requirements.txt` (removed in favor of `pyproject.toml` + `uv.lock`).

## Environment

- Run the dev server: `uv run python manage.py runserver`
- Run tests: `uv run pytest`
- Run migrations: `uv run python manage.py migrate`
