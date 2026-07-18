"""
Backend/main.py

FastAPI application entrypoint (t2-1). Skeleton only: app instance, CORS,
health check, and router wiring. Real endpoints (rates, inflation, exchange,
correlation, auth, basket) get added as routers in Backend/routers/ in
later tickets (t2-3 onward), then included below.

Run with: uvicorn Backend.main:app --reload (from project root, venv active)
"""

import os

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from Backend.database import get_db

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

app = FastAPI(
    title="Ceylon Cost of Living Engine API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    """
    Confirms the API is up AND can actually reach the database,
    not just that the process is running.
    """
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}


# Routers get included here as they're built:
# from Backend.routers import rates
# app.include_router(rates.router, prefix="/api")
