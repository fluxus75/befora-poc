# Befora POC

Phase 1 scaffolding for the Befora pre-appointment history taking PoC.

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

## Environment

Copy `.env.example` to `.env` and update values as needed.
