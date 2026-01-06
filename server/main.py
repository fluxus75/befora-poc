from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server import __version__
from server.api.realtime import router as realtime_router
from server.api.routes import router as api_router

app = FastAPI(
    title="Befora Voice AI Agent",
    description="Voice AI Agent for patient intake",
    version=__version__,
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(realtime_router)
