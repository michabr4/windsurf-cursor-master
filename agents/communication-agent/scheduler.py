#!/usr/bin/env python3
"""Continuous/interval runtime scheduler for the Communication Intelligence Agent."""

import logging
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from agent import CommunicationAgent
from config import RuntimeMode, get_settings
from output_formatter import OutputFormatter


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def run_once(agent: CommunicationAgent, formatter: OutputFormatter, logger: logging.Logger) -> None:
    report = agent.run()
    paths = formatter.save_all_formats(report)
    logger.info(
        "Run complete | actions=%s high=%s overdue=%s | outputs=%s",
        len(report.action_items),
        report.high_priority_count,
        report.overdue_count,
        ", ".join(paths.values()),
    )


def main() -> None:
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)

    setup_logging()
    logger = logging.getLogger("scheduler")

    settings = get_settings()
    agent = CommunicationAgent(settings)
    formatter = OutputFormatter(settings)

    logger.info("Scheduler starting | mode=%s", settings.runtime_mode.value)

    if settings.runtime_mode == RuntimeMode.CONTINUOUS:
        logger.info(
            "Running in continuous mode with %s second backoff",
            settings.continuous_backoff_seconds,
        )
        while True:
            started = datetime.utcnow()
            try:
                run_once(agent, formatter, logger)
            except Exception as err:
                logger.exception("Run failed: %s", err)
            finally:
                logger.info(
                    "Sleeping %s seconds before next run",
                    settings.continuous_backoff_seconds,
                )
                time.sleep(max(1, settings.continuous_backoff_seconds))

    logger.info(
        "Running in interval mode: every %s minutes",
        settings.runtime_interval_minutes,
    )
    while True:
        started = datetime.utcnow()
        try:
            run_once(agent, formatter, logger)
        except Exception as err:
            logger.exception("Run failed: %s", err)

        elapsed = (datetime.utcnow() - started).total_seconds()
        sleep_seconds = max(1, settings.runtime_interval_minutes * 60 - int(elapsed))
        logger.info("Sleeping %s seconds before next run", sleep_seconds)
        time.sleep(sleep_seconds)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.getLogger("scheduler").info("Scheduler stopped by user")
        sys.exit(0)
