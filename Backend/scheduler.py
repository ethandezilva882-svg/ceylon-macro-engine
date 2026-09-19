"""
Backend/scheduler.py

AsyncIOScheduler wired into FastAPI startup (t2-7). Runs all three
scrapers as subprocesses once daily at 01:00 Sri Lanka time.

Replaces the standalone BlockingScheduler version from t1-10. The
scraper subprocess calls are still blocking (subprocess.run), so the
daily job is wrapped with asyncio.to_thread to keep it off the FastAPI
event loop, the whole point of using AsyncIOScheduler over
BlockingScheduler is that it must not block request handling.

Run standalone for manual testing/debugging with:
    python -m Backend.scheduler
"""

import asyncio
import logging
import subprocess
import sys
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("scheduler")

SCRAPER_MODULES = [
    "Scrapers.cbsl_scraper",
    "Scrapers.inflation_scraper",
    "Scrapers.lkr_usd_scraper",
]

SRI_LANKA_TZ = ZoneInfo("Asia/Colombo")

scheduler = AsyncIOScheduler(timezone=SRI_LANKA_TZ)


def run_scraper(module_name: str) -> None:
    logger.info(f"Starting {module_name}")
    result = subprocess.run(
        [sys.executable, "-m", module_name],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        logger.info(f"{module_name} finished OK")
        if result.stdout.strip():
            logger.info(result.stdout.strip())
    else:
        logger.error(f"{module_name} FAILED (exit code {result.returncode})")
        if result.stderr.strip():
            logger.error(result.stderr.strip())


def run_all_scrapers_sync() -> None:
    logger.info("=== Daily scraper run starting ===")
    for module in SCRAPER_MODULES:
        run_scraper(module)
    logger.info("=== Daily scraper run finished ===")


async def run_all_scrapers_async() -> None:
    """
    Runs the blocking scraper batch in a worker thread so the FastAPI
    event loop stays free to handle requests while scraping runs.
    """
    await asyncio.to_thread(run_all_scrapers_sync)


def start_scheduler() -> None:
    scheduler.add_job(
        run_all_scrapers_async,
        "cron",
        hour=1,
        minute=0,
        id="daily_scraper_run",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("AsyncIOScheduler started, daily run scheduled for 01:00 Asia/Colombo")


def shutdown_scheduler() -> None:
    scheduler.shutdown(wait=False)
    logger.info("Scheduler shut down")


if __name__ == "__main__":
    logger.info("Running scrapers once, standalone mode (manual test)")
    asyncio.run(run_all_scrapers_async())
