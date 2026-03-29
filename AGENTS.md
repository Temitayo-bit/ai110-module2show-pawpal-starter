# Repository Guidelines

## Project Structure & Module Organization
This repository is a lightweight starter for **PawPal+**, a Streamlit-based pet care planner. `app.py` contains the UI shell and should stay focused on input/output and display logic. Keep project requirements in `requirements.txt`, assignment context in `README.md`, and design notes or retrospectives in `reflection.md`. As you add backend logic, place domain models and scheduling code in dedicated Python modules at the repository root (for example, `pawpal_system.py` or `scheduler.py`) and add tests under `tests/`.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` — create and activate the local virtual environment.
- `pip install -r requirements.txt` — install Streamlit and pytest.
- `streamlit run app.py` — launch the local app for manual testing.
- `pytest` — run the test suite.

If you add modules, keep commands runnable from the repository root.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indentation. Use `snake_case` for variables, functions, and filenames; use `PascalCase` for classes such as `Pet`, `Owner`, or `Task`. Prefer small, single-purpose functions and keep scheduling logic out of Streamlit callbacks when possible. No formatter or linter is configured yet, so match the style already used in `app.py`: clear names, short blocks, and minimal inline comments.

## Testing Guidelines
Use `pytest` for all tests. Put tests in `tests/` and name files `test_*.py`; name test functions `test_<behavior>()`, such as `test_high_priority_tasks_scheduled_first`. Focus coverage on scheduling behavior, task ordering, duration handling, and edge cases like empty task lists or limited available time.

## Commit & Pull Request Guidelines
Recent commits use short, imperative summaries such as `add starter app` and `Update README, app structure, and project files`. Follow that pattern: start with a verb, keep the subject concise, and scope each commit to one logical change. Pull requests should include a brief summary, list of tested commands, linked assignment or issue context, and screenshots or screen recordings when the Streamlit UI changes.

## Security & Configuration Tips
Do not commit `.venv/`, `__pycache__/`, or local caches; these are already ignored in `.gitignore`. Keep secrets out of source files and prefer environment variables or Streamlit secrets if the project later integrates external services.
