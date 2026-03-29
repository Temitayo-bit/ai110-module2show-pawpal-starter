# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

## Smarter Scheduling

The scheduler now includes a few practical upgrades for day-to-day pet planning:

- Time sorting: tasks can be sorted by HH:MM values for predictable order.
- Task filtering: tasks can be filtered by completion status and by pet name.
- Recurring tasks: when a daily or weekly recurring task is completed, a new next-occurrence task is auto-created.
- Conflict warnings: overlapping scheduled tasks are detected and returned as warning messages instead of stopping execution.

These features make the planner more useful in real routines while keeping behavior easy to explain and test.

## Testing PawPal+

Run the full test suite from the project root with:

```bash
python -m pytest
```

Current tests cover core scheduler behavior, including:

- Happy paths for task sorting, filtering, and schedule generation by priority.
- Recurrence logic when completing daily and weekly recurring tasks.
- Conflict detection for overlapping and duplicate scheduled times.
- Edge cases like pets with no tasks, case-insensitive pet filtering, unsupported recurrence values, and tasks outside the owner day window.

Confidence Level: 4/5 stars based on passing test results across these critical scheduling scenarios.

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
