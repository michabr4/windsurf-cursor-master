"""AGT-001 Demo: Generate a daily inbox digest.

Run:
    cd python
    python examples/agt001_daily_digest_demo.py

Prerequisites:
    1. Copy .env.example to .env
    2. Set MS_CLIENT_ID and MS_TENANT_ID (see docs/OUTLOOK_API_ACCESS_GUIDE.md)
    3. pip install -r requirements.txt
"""

from pathlib import Path
import json
import sys

PYTHON_ROOT = Path(__file__).resolve().parents[1]
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from src.agt001_email_chief_of_staff import EmailChiefOfStaff  # noqa: E402


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
        print("  2. Run the basic test first: python examples/outlook_action_items_demo.py")
        print("  3. See docs/OUTLOOK_API_ACCESS_GUIDE.md for setup steps")
        return

    # Print human-readable summary
    print(digest.to_text_summary())
    print()

    # Save structured JSON output
    output_dir = PYTHON_ROOT / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "agt001_daily_digest.json"
    json_path.write_text(digest.to_json(), encoding="utf-8")
    print(f"Saved JSON digest: {json_path}")

    text_path = output_dir / "agt001_daily_digest.txt"
    text_path.write_text(digest.to_text_summary(), encoding="utf-8")
    print(f"Saved text digest: {text_path}")

    # Demo: chain-compatible output
    print()
    print("Chain output demo (CHAIN-001, step 1):")
    chain_output = agent.summarize_for_chain(chain_id="CHAIN-001", step_number=1)
    print(f"  Status: {chain_output.status}")
    print(f"  Emails scanned: {chain_output.data.get('total_emails_scanned', 'N/A')}")
    handle_first_count = len(chain_output.data.get("handle_first", []))
    decisions_count = len(chain_output.data.get("decisions_needed", []))
    actions_count = len(chain_output.data.get("action_required", []))
    print(f"  Handle first: {handle_first_count}")
    print(f"  Decisions needed: {decisions_count}")
    print(f"  Actions required: {actions_count}")


if __name__ == "__main__":
    main()
