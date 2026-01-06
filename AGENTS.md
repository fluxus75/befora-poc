# Repository Guidelines

## Project Structure & Module Organization
- `apps/`: frontend apps (Vite). Expected apps: `web` (patient UI) and `dashboard` (doctor UI).
- `server/`: FastAPI backend, scenarios, and API endpoints.
- `shared/`: shared types/utilities used across apps.
- `SRD/` and `docs/`: product/spec docs and implementation plans.
- Top-level configs: `package.json`, `pnpm-workspace.yaml`, `eslint.config.js`, `pyproject.toml`.

## Build, Test, and Development Commands
Frontend (from repo root):
- `pnpm install`: install JS dependencies.
- `pnpm dev`: run all frontend apps.
- `pnpm dev:web`: run patient web client only.
- `pnpm dev:dashboard`: run doctor dashboard only.
- `pnpm build`: production build for all apps.
- `pnpm test`: run frontend tests.
- `pnpm lint`: run ESLint.

Backend (from `server/`):
- `uv venv && source .venv/bin/activate`: create/activate venv.
- `cd .. && uv pip install -e ".[dev]"`: install deps from root `pyproject.toml`.
- `uv run uvicorn main:app --reload --port 8000`: start API server.
- `uv run pytest`: run backend tests.

## Coding Style & Naming Conventions
- TypeScript: strict mode, 2-space indent, `PascalCase` components, `camelCase` functions, `SCREAMING_SNAKE_CASE` constants.
- Python: type hints required, 4-space indent, `PascalCase` classes, `snake_case` functions.
- Tools: ESLint/Prettier for TS; Black/isort/ruff for Python.

## Testing Guidelines
- Frontend: use `pnpm test` (see app-level configs for framework details).
- Backend: `pytest` via `uv run pytest`.
- Include tests for DSL scenario changes and API behavior; name tests to match modules (e.g., `test_scenarios.py`).

## Commit & Pull Request Guidelines
- Commit format: `type(scope): description`.
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `security`.
- Scopes: `web`, `dashboard`, `api`, `agent`, `auth`, `rtc`, `dsl`.
- PRs: include a clear description, testing evidence, and confirm no PII or secrets were added.

## Security & Configuration Tips
- Never commit secrets: `OPENAI_API_KEY`, `HEYGEN_API_KEY`, `TWILIO_*`, `DATABASE_URL`, `JWT_SECRET`, `DB_ENCRYPTION_KEY`.
- Audio must connect directly to OpenAI Realtime API; server issues ephemeral tokens only.

## Work Logging
- After completing code implementation tasks, write a brief result log under `SRD/dev_log/` (e.g., `0106_0208_codex.log`).
