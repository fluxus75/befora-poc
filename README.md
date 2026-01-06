# Befora POC

![CI Status](https://github.com/OWNER/befora-poc/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/OWNER/befora-poc/branch/main/graph/badge.svg)](https://codecov.io/gh/OWNER/befora-poc)

Phase 1 scaffolding for the Befora pre-appointment history taking PoC.

> **Note**: Replace `OWNER` in the badge URLs with your GitHub username or organization name.

## Structure

- `apps/web-client`: patient-facing React app (Vite + TS)
- `apps/doctor-dashboard`: placeholder for Phase 4
- `server`: FastAPI backend
- `shared`: shared schemas/constants

## Frontend (web-client)

```bash
cd apps/web-client
npm install
npm run dev
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
