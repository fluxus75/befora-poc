from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server import __version__
from server.api.auth import router as auth_router
from server.api.local_realtime import router as local_realtime_router
from server.api.reports import router as reports_router
from server.api.realtime import router as realtime_router
from server.api.routes import router as api_router
from server.api.sessions import router as sessions_router
from server.db.database import initialize_db
from server.services.auth_store import ensure_default_users

app = FastAPI(
    title="Befora Voice AI Agent",
    description="Voice AI Agent for patient intake",
    version=__version__,
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(auth_router)
app.include_router(sessions_router)
app.include_router(reports_router)
app.include_router(realtime_router)
app.include_router(local_realtime_router)


@app.on_event("startup")
def startup() -> None:
    initialize_db()
    ensure_default_users()
