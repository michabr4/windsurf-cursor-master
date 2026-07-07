"""CLI: fetch an Asana task, run checks, write reports under out/asana-reviews/.

Dry-run by default. Use --confirm to post the suggested comment as a task story.

Usage:
  python python/examples/asana_review_cli.py 1234567890123456
  python python/examples/asana_review_cli.py "https://app.asana.com/0/111/222" --confirm
  python python/examples/asana_review_cli.py 123 --llm   # polish with local Ollama
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PYTHON_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PYTHON_ROOT.parent
OUT_DIR = REPO_ROOT / "out" / "asana-reviews"

if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from src.asana_client import normalize_task_gid  # noqa: E402
from src.asana_review_service import review_task  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Review an Asana task (local, secrets in .env).")
    parser.add_argument(
        "task",
        help="Numeric task GID or Asana task URL",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="After review, post the suggested comment to Asana (otherwise dry-run only).",
    )
    parser.add_argument(
        "--llm",
        action="store_true",
        help="Polish the comment with local Ollama (requires Ollama running; see ASANA_REVIEW_USE_LLM).",
    )
    args = parser.parse_args()

    gid = normalize_task_gid(args.task)
    outcome = review_task(gid, out_dir=OUT_DIR, use_llm=args.llm)

    print("Review complete.")
    print(f"  Markdown: {outcome.markdown_path}")
    print(f"  JSON:     {outcome.json_path}")
    if outcome.llm_error:
        print(f"  LLM:      {outcome.llm_error}")
    elif outcome.llm_applied:
        print("  LLM:      applied")
    print()
    print("Suggested comment:")
    print("---")
    print(outcome.suggested_comment)
    print("---")

    if args.confirm:
        from src.asana_client import AsanaClient  # noqa: E402

        AsanaClient().add_comment_story(gid, outcome.suggested_comment)
        print("Posted comment to Asana.")
    else:
        print("Dry-run only. Re-run with --confirm to post the comment above.")


if __name__ == "__main__":
    main()
