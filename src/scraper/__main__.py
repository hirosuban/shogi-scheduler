"""Entry point for the scraper.

Usage:
    uv run python -m src.scraper          # run once
    uv run python -m src.scraper --daemon # run on a schedule
"""

import argparse
import logging
import sys

from .config import CONFIG
from .scheduler import start
from .service import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Shogi tournament scraper")
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run continuously on a schedule instead of once",
    )
    args = parser.parse_args()

    if args.daemon:
        start(CONFIG)
    else:
        try:
            run_pipeline(CONFIG)
        except Exception:
            sys.exit(1)


if __name__ == "__main__":
    main()
