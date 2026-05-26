"""AGT-001 demo: generate a daily inbox digest (delivery workbench).

Run from repo root:

    python3 scripts/integrations/agt001_daily_digest_demo.py

Prerequisites: `.env` with `MS_CLIENT_ID` and `MS_TENANT_ID` (see docs/email/OUTLOOK_AGT001_SETUP.md).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INTEGRATIONS = REPO_ROOT / "python" / "integrations"
if str(INTEGRATIONS) not in sys.path:
    sys.path.insert(0, str(INTEGRATIONS.parent))

from integrations.agt001 import EmailChiefOfStaff  # noqa: E402


def main() -> None:
    agent = EmailChiefOfStaff()

    print("AGT-001 Email Chief-of-Staff — Daily Digest")
    print("=" * 50)
    print()

    try:
        digest = agent.generate_daily_digest()
    except Exception as exc:
        print(f"Failed to generate digest: {exc}")
        print()
        print("Troubleshooting:")
        print("  1. Confirm MS_CLIENT_ID and MS_TENANT_ID are set in .env")
        print("  2. See docs/email/OUTLOOK_AGT001_SETUP.md")
        return

    print(digest.to_text_summary())
    print()

    output_dir = REPO_ROOT / "data" / "runs" / "agt001"
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "agt001_daily_digest.json"
    json_path.write_text(digest.to_json(), encoding="utf-8")
    print(f"Saved JSON digest: {json_path}")

    text_path = output_dir / "agt001_daily_digest.txt"
    text_path.write_text(digest.to_text_summary(), encoding="utf-8")
    print(f"Saved text digest: {text_path}")

    print()
    print("Chain output demo (CHAIN-001, step 1):")
    chain_output = agent.summarize_for_chain(chain_id="CHAIN-001", step_number=1)
    print(f"  Status: {chain_output.status}")
    print(f"  Emails scanned: {chain_output.data.get('total_emails_scanned', 'N/A')}")
    print(f"  Handle first: {len(chain_output.data.get('handle_first', []))}")
    print(f"  Decisions needed: {len(chain_output.data.get('decisions_needed', []))}")
    print(f"  Actions required: {len(chain_output.data.get('action_required', []))}")


if __name__ == "__main__":
    main()
