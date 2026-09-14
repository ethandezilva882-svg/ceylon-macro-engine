"""
Backend/main.py

FastAPI application entrypoint. App instance, CORS, health check,
router wiring, and scheduler lifecycle (t2-7). The AsyncIOScheduler
starts on app startup and shuts down cleanly on app shutdown via the
lifespan context manager.

Run with: uvicorn Backend.main:app --reload (from project root, venv active)
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.routers import rates, inflation, exchange, events, summary, correlation, auth, basket
from Backend.scheduler import start_scheduler, shutdown_scheduler

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(
    title="Ceylon Cost of Living Engine API",
    version="0.1.0",
    lifespan=lifespan,
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


app.include_router(rates.router, prefix="/api")
app.include_router(inflation.router, prefix="/api")
app.include_router(exchange.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(summary.router, prefix="/api")
app.include_router(correlation.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(basket.router, prefix="/api")
