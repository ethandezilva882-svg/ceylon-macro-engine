"""
Backend/scheduler.py

Standalone daily scheduler for t1-10. Runs the three scrapers as separate
subprocesses once a day, the same way they are already run manually
(python -m Scrapers.cbsl_scraper etc). Subprocess isolation means if one
scraper crashes, it does not take the other two or the scheduler down with it.

Run with: python -m Backend.scheduler (from project root, venv active)

When Phase 2 FastAPI app exists, import run_all_scrapers and start this
scheduler from a startup event instead of running this file directly.
"""

import subprocess
import sys
import logging

from apscheduler.schedulers.blocking import BlockingScheduler

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


def run_scraper(module_name):
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


def run_all_scrapers():
    logger.info("=== Daily scraper run starting ===")
    for module in SCRAPER_MODULES:
        run_scraper(module)
    logger.info("=== Daily scraper run finished ===")


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(run_all_scrapers, "cron", hour=6, minute=0)
    logger.info("Scheduler started, daily run scheduled for 06:00. Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
