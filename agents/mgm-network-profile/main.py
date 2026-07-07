"""MGM Resorts Network Profile — entry point.

Usage:
    python3.10 main.py                    # uses .env defaults (cpyKey=172361)
    python3.10 main.py --cpy-key 99999    # override company
    python3.10 main.py --json             # dump JSON snapshot to output/
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from config import get_settings
from extractor import NPExtractor
from recommender import NPRecommender


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NetProfile Insight baseline runner")
    parser.add_argument("--cpy-key", type=int, help="Override NP_CPY_KEY")
    parser.add_argument("--json", action="store_true", help="Write JSON snapshot to output/")
    parser.add_argument("--dry-run", action="store_true", help="Print config and exit without fetching")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    settings = get_settings()

    if args.cpy_key:
        settings.np_cpy_key = args.cpy_key

    _setup_logging(settings.log_level)
    logger = logging.getLogger("main")

    if args.dry_run:
        logger.info("Dry-run mode — config:")
        logger.info("  cpyKey      = %s", settings.np_cpy_key)
        logger.info("  mimir_url   = %s", settings.mimir_url)
        logger.info("  cookie_file = %s", settings.mimir_cookie_file)
        logger.info("  cache_dir   = %s", settings.mimir_cache_dir)
        logger.info("  cli_commands= %s", settings.np_cli_commands)
        return 0

    # ── Extract ────────────────────────────────────────────────────────────────
    extractor = NPExtractor(settings)
    snapshot = extractor.run()

    # ── Recommend ─────────────────────────────────────────────────────────────
    recommender = NPRecommender()
    snapshot.recommendations = recommender.analyse(snapshot)

    # ── Print summary ──────────────────────────────────────────────────────────
    company_name = snapshot.company.cpy_name if snapshot.company else "Unknown"
    print(f"\n{'='*60}")
    print(f"  MGM Resorts Network Profile — {company_name} (cpyKey={snapshot.cpy_key})")
    print(f"  Fetched: {snapshot.fetched_at.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")
    print(f"  Groups    : {len(snapshot.groups)}")
    print(f"  Devices   : {snapshot.device_count}")
    print(f"  Collectors: {snapshot.collector_count}")
    print(f"  Findings  : {len(snapshot.recommendations)}")
    print()

    for rec in snapshot.recommendations:
        device_label = f" [{rec.device_name}]" if rec.device_name else ""
        print(f"  [{rec.severity.upper():8s}] {rec.category}{device_label}")
        print(f"           {rec.title}")
        print(f"           {rec.detail[:120]}{'...' if len(rec.detail) > 120 else ''}")
        print()

    # ── JSON output ────────────────────────────────────────────────────────────
    if args.json:
        out_dir = Path(settings.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out_path = out_dir / f"np_snapshot_{snapshot.cpy_key}_{ts}.json"
        payload = {
            "cpy_key": snapshot.cpy_key,
            "company": snapshot.company.cpy_name if snapshot.company else None,
            "fetched_at": snapshot.fetched_at.isoformat(),
            "groups": [g.group_name for g in snapshot.groups],
            "device_count": snapshot.device_count,
            "collector_count": snapshot.collector_count,
            "recommendations": [r.to_dict() for r in snapshot.recommendations],
        }
        out_path.write_text(json.dumps(payload, indent=2))
        logger.info("Snapshot written to %s", out_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
