import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from .config import CONFIG, Config
from .service import run_pipeline

logger = logging.getLogger(__name__)


def _job(config: Config) -> None:
    logger.info("Scheduled run starting")
    try:
        run_pipeline(config)
    except Exception as exc:
        logger.error("Scheduled run failed: %s", exc)


def start(config: Config = CONFIG) -> None:
    """Start the blocking scheduler. Blocks until interrupted."""
    scheduler = BlockingScheduler()
    scheduler.add_job(
        _job,
        "interval",
        hours=config.schedule_interval_hours,
        args=[config],
        id="scraper",
        misfire_grace_time=3600,
    )
    logger.info(
        "Scheduler started (interval=%d h)", config.schedule_interval_hours
    )
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")
