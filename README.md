# Befora POC

![CI Status](https://github.com/OWNER/befora-poc/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/OWNER/befora-poc/branch/main/graph/badge.svg)](https://codecov.io/gh/OWNER/befora-poc)

Phase 1 scaffolding for the Befora pre-appointment history taking PoC.

> **Note**: Replace `OWNER` in the badge URLs with your GitHub username or organization name.

## Structure

- `apps/web-client`: patient-facing React app (Vite + TS)
- `apps/doctor-dashboard`: doctor dashboard (Vite + TS)
- `server`: FastAPI backend
- `shared`: shared schemas/constants

## Frontend (web-client)

```bash
pnpm install
pnpm dev:web
```

## Frontend (doctor-dashboard)

```bash
pnpm install
pnpm dev:dashboard
```

## Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn server.main:app --reload
```

## Local Realtime (Phase 2)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[local-realtime]"
uvicorn server.main:app --reload --port 8000
```

```bash
VITE_REALTIME_PROVIDER=local pnpm -C apps/web-client dev
```

## Environment

Copy `.env.example` to `.env` and update values as needed.

## Codex Workflow (Automated PR Generation)

### Quick Start
```bash
# 1. Generate task file
/codex-task-generation

# 2. Codex generates code

# 3. Auto-generate PR
/auto-pr-from-task

# OR use script
./scripts/auto-pr.sh docs/tasks/codex-YYYYMMDD-{name}.md
```

### Workflow Options

| Method | Command | When to Use |
|--------|---------|-------------|
| **Claude Skill** | `/auto-pr-from-task` | Manual control, flexible |
| **GitHub Actions** | `git push origin codex/{name}` | Team collaboration, automated |
| **Shell Script** | `./scripts/auto-pr.sh` | Quick one-liner |

See [docs/CODEX_WORKFLOW.md](docs/CODEX_WORKFLOW.md) for detailed guide.
