# Repository Guidelines

## Project Structure & Module Organization
- `app_v2.py` is the main Streamlit entry point.
- `src/services/` holds core logic (AI generation, chat handling, data processing).
- `src/utils/` contains shared helpers and small utilities.
- `tests/` mirrors `src/` with pytest suites.
- `docs/` stores specs and design notes; `prompts.py` contains system prompts.

## Build, Test, and Development Commands
- `python3 -m venv .venv` and `source .venv/bin/activate`: create and activate a venv.
- `pip install -r requirements.txt`: install dependencies.
- `streamlit run app_v2.py`: run the local app.
- `python check_env.py`: quick import/sanity check.
- `pytest`: run tests under `tests/`.
- `ruff check .` / `ruff format .`: lint and format (also run by pre-commit).
- `pre-commit run --all-files`: run hooks locally (ruff + pytest).

## Coding Style & Naming Conventions
- Python 3.10, 4-space indentation, max line length 100.
- Use `ruff` for linting/formatting (double quotes, isort rules enabled).
- Modules and functions use `snake_case`; classes use `CamelCase`.
- Keep service logic in `src/services/` and avoid mixing UI and data logic in `app_v2.py`.

## Testing Guidelines
- Framework: `pytest`.
- Naming: files `test_*.py`, functions `test_*`, classes `Test*`.
- Coverage config targets `src/`; use `coverage run -m pytest` if you need reports.

## Commit & Pull Request Guidelines
- Commit messages are short, imperative summaries (e.g., "Fix linting issues").
- PRs should include: what changed, how to run/test, and screenshots/GIFs for UI changes.
- Link related issues and note any new environment variables or API key requirements.

## Security & Configuration Tips
- Copy `.env.example` to `.env` for local API keys; never commit secrets.
- Treat generated dashboards/HTML as artifacts; review before sharing.
