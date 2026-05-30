"""Main agent class for MGM Resorts Network Profile.

Implements the AI Factory Agent standard:
  - trust_tier property
  - run(), validate_inputs(), handle_error()
  - KPI metrics printed at end of run()
"""

from __future__ import annotations

import logging
import time
from typing import Optional

from config import get_settings, Settings
from extractor import NPExtractor
from models import NPSnapshot
from recommender import NPRecommender

logger = logging.getLogger(__name__)


class MGMNetworkProfileAgent:
    """AI Factory T3 agent — human-triggered network profile analysis for MGM Resorts."""

    trust_tier: str = "T3"

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._settings = settings or get_settings()
        self._extractor = NPExtractor(self._settings)
        self._recommender = NPRecommender()

    def validate_inputs(self) -> None:
        """Raise ValueError if required configuration is missing."""
        if not self._settings.mimir_url:
            raise ValueError("MIMIR_URL is not configured.")
        if not self._settings.np_cpy_key:
            raise ValueError("NP_CPY_KEY is not configured.")
        logger.info(
            "validate_inputs passed: url=%s cpy_key=%s",
            self._settings.mimir_url,
            self._settings.np_cpy_key,
        )

    def handle_error(self, exc: Exception) -> None:
        """Log the exception before re-raising."""
        logger.error("MGMNetworkProfileAgent run failed: %s: %s", type(exc).__name__, exc)
        raise exc

    def run(self) -> NPSnapshot:
        """Extract data, generate recommendations, print KPI metrics, and return snapshot."""
        start = time.monotonic()
        errors = 0
        records = 0

        try:
            self.validate_inputs()

            logger.info("Starting extraction for cpyKey=%s", self._settings.np_cpy_key)
            snapshot = self._extractor.run()
            records = snapshot.device_count

            logger.info("Starting recommendation analysis")
            snapshot.recommendations = self._recommender.analyse(snapshot)

            duration = time.monotonic() - start
            print(
                f"[METRICS] Records processed: {records}, "
                f"errors: {errors}, "
                f"findings: {len(snapshot.recommendations)}, "
                f"duration: {duration:.1f}s"
            )
            return snapshot

        except Exception as exc:
            errors += 1
            duration = time.monotonic() - start
            print(
                f"[METRICS] Records processed: {records}, "
                f"errors: {errors}, "
                f"duration: {duration:.1f}s"
            )
            self.handle_error(exc)
