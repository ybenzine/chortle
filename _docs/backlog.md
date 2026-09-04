# Household Chores Tracker — Backlog

Small, sequential tasks for building the tool described in `plan.md` on Django, using Django models and the ORM for persistence (SQLite), with server-rendered views. No accounts/login — the app is used from one shared household device, consistent with `plan.md`.

## Milestone 1 — Data model

- [x] **1.1** `Member` model: name.
- [x] **1.2** `Chore` model: name, assignment type (`fixed` / `rotating` / `claimable`), recurrence rule (e.g. interval-in-days + optional weekday, enough to express "every 3 days" and "every other Monday"), last-done date, next-due date.
- [x] **1.3** Assignment fields/relations on `Chore`: fixed assignee (FK to `Member`, nullable), rotation order (ordered list/M2M of `Member` for rotating chores), current claim (FK to `Member`, nullable, for claimable chores).
- [x] **1.4** `Completion` model: FK to `Chore`, FK to `Member`, timestamp — the append-only log of who did what and when.
- [x] **1.5** Migrations for all of the above; register models in `core/admin.py` for inspection during development.

## Milestone 2 — Members & Chores CRUD

- [ ] **2.1** Views + templates + URLs to list/add/edit/remove `Member`s.
- [ ] **2.2** Views + templates + URLs to list/add/edit/remove `Chore`s, including setting assignment type and recurrence rule.
- [ ] **2.3** Form validation: a chore's assignment fields match its type (e.g. rotating chores need a rotation order with at least one member).
- [ ] **2.4** Pure function (with unit tests) to compute the next due date from a recurrence rule + last-done date.

## Milestone 3 — Assignment logic

- [ ] **3.1** Fixed assignment: chore detail/list always displays its fixed assignee.
- [ ] **3.2** Rotating assignment: on completion, advance a stored pointer/index so the next occurrence is assigned to the next member in rotation order.
- [ ] **3.3** Claimable assignment: "claim" action sets the current claimant; chore shows as unclaimed/in the shared pool until claimed.

## Milestone 4 — Completion & tracking

- [ ] **4.1** "Mark done" view: creates a `Completion` record (chore, member, now), updates the chore's `last_done`/`next_due`, and (for rotating chores) advances rotation.
- [ ] **4.2** History view: paginated, reverse-chronological list of `Completion` records, read-only.

## Milestone 5 — Due/overdue view

- [ ] **5.1** "Today" view: query chores due today, grouped by assignee.
- [ ] **5.2** Overdue view/section: query chores past due, ordered by days overdue.
- [ ] **5.3** Empty/all-caught-up state when nothing is due or overdue.

## Milestone 6 — Polish & resilience

- [ ] **6.1** First-run/empty state when no members or chores exist yet, with a simple setup prompt.
- [ ] **6.2** Basic responsive styling suitable for a fridge-mounted tablet (large tap targets, readable at a glance).
- [ ] **6.3** Seed/fixture data or a management command for quickly populating a demo household during development and grading.

## Explicitly deferred (out of scope per plan.md)

Accounts/login, multi-device sync beyond the single shared device/DB, verification/proof of completion, gamification, fairness balancing, push/email notifications.
