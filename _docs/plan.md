# Household Chores Tracker — Scope

A tool for managing shared household chores. This document defines the agreed scope before any building begins.

## Overview

A lightweight, trust-based chore tracker for a single, fixed household. It tracks who does what and when, shows what's due, and requires no accounts or internet. Everyone in the household uses it from one shared device.

## Decisions

**Users**
Built for one fixed, known household. Anyone can add or edit chores and members — no roles, no admin, no login.

**Assignment**
Mixed model:

- **Fixed** — some chores permanently belong to a specific person
- **Rotating** — some chores cycle automatically through people
- **Claimable** — some chores sit in a shared pool for anyone to pick up

**Recurrence**
Flexible recurrence, not just daily/weekly/monthly. Supports patterns like "every 3 days" or "every other Monday."

**Completion**
Self-report and trust-based. A person taps "done" — no verification, no dispute, no photo proof.

**Purpose**
Pure tracking: who did what, and when. No points, streaks, leaderboards, or fairness balancing.

**Reminders**
In-app only — a "due today / overdue" view. No push notifications and no email.

**Data**
Stored server-side in a Django-backed database (SQLite via the ORM), served to the single shared household device. No accounts, no multi-device sync — just one app instance the household accesses.

## Out of Scope

Deliberately excluded to keep the tool simple:

- User accounts or login
- Multi-device sync or a hosted/shared backend serving multiple independent households
- Verification, dispute, or proof of completion
- Gamification (points, streaks, leaderboards)
- Fairness balancing or workload flags
- Push or email notifications

## Note on the Usage Model

Even though data now lives in a server-side database rather than the browser, the tool is still built for one fixed household with no accounts — anyone can add or edit chores and members. In practice the household shares a single device or browser to run the tool — for example, a tablet mounted on the fridge or a shared family laptop. This is intentional and consistent with the choices above.
