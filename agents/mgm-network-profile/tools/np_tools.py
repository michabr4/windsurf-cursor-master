"""Tool functions for MGM Resorts Network Profile agent.

Thin wrappers around the extractor and recommender suitable for
use as discrete, composable tool calls by an LLM orchestrator.
"""

from __future__ import annotations

import logging
from typing import Any

from config import get_settings
from extractor import NPExtractor
from models import NPSnapshot, Recommendation
from recommender import NPRecommender

logger = logging.getLogger(__name__)


def fetch_snapshot(cpy_key: int | None = None) -> NPSnapshot:
    """Pull a full network snapshot for the configured company.

    Args:
        cpy_key: Optional override for the company key (default: NP_CPY_KEY env var).

    Returns:
        NPSnapshot populated with groups, devices, collectors, and CLI outputs.
    """
    settings = get_settings()
    if cpy_key is not None:
        settings = settings.model_copy(update={"np_cpy_key": cpy_key})
    extractor = NPExtractor(settings)
    logger.info("fetch_snapshot: starting extraction cpy_key=%s", settings.np_cpy_key)
    return extractor.run()


def generate_recommendations(snapshot: NPSnapshot) -> list[Recommendation]:
    """Analyse a snapshot and return prioritised recommendations.

    Args:
        snapshot: A populated NPSnapshot (from fetch_snapshot).

    Returns:
        List of Recommendation objects sorted by priority.
    """
    recommender = NPRecommender()
    recs = recommender.analyse(snapshot)
    logger.info("generate_recommendations: %d findings produced", len(recs))
    return recs


def snapshot_summary(snapshot: NPSnapshot) -> dict[str, Any]:
    """Return a lightweight summary dict for the snapshot (safe to serialize).

    Returns:
        dict with keys: cpy_key, fetched_at, groups, devices, collectors, findings.
    """
    return {
        "cpy_key": snapshot.cpy_key,
        "fetched_at": snapshot.fetched_at.isoformat(),
        "groups": len(snapshot.groups),
        "devices": snapshot.device_count,
        "collectors": snapshot.collector_count,
        "findings": len(snapshot.recommendations),
    }


def top_findings(snapshot: NPSnapshot, n: int = 10) -> list[dict[str, Any]]:
    """Return the top-N findings as serialisable dicts.

    Args:
        snapshot: Snapshot that already has recommendations populated.
        n:        Maximum number of findings to return.
    """
    recs = snapshot.recommendations[:n] if snapshot.recommendations else []
    return [
        {
            "priority": r.priority,
            "category": r.category,
            "title": r.title,
            "device": r.device_name,
            "detail": r.detail,
        }
        for r in recs
    ]
