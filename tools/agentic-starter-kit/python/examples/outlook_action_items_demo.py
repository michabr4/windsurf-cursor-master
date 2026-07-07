from pathlib import Path
import csv
import sys


# Add the Python starter folder so this example can import the local src
# package even when someone runs the file directly from the examples folder.
PYTHON_ROOT = Path(__file__).resolve().parents[1]
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from src.outlook_action_items import OutlookActionItemClient  # noqa: E402


def export_to_csv(items: list, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "rank",
                "priority_label",
                "priority_score",
                "subject",
                "sender",
                "due_date",
                "received_at",
                "reason",
                "web_link",
            ]
        )
        for idx, item in enumerate(items, start=1):
            writer.writerow(
                [
                    idx,
                    item.priority_label,
                    item.priority_score,
                    item.subject,
                    item.sender,
                    item.due_date or "",
                    item.received_at,
                    item.reason,
                    item.web_link,
                ]
            )


def print_startup_diagnostics(exc: Exception) -> None:
    error_text = str(exc)
    lowered = error_text.lower()
    print("Startup diagnostics:")

    if "proxyerror" in lowered or "unable to connect to proxy" in lowered:
        print("- Proxy connection failed while contacting Microsoft login.")
        print("- Check HTTPS proxy settings in your terminal (HTTP_PROXY / HTTPS_PROXY).")
        print("- Ask IT to allow login.microsoftonline.com and graph.microsoft.com.")
        return

    if "login.microsoftonline.com" in lowered and "403" in lowered:
        print("- Microsoft login endpoint is being blocked (HTTP 403).")
        print("- This is usually a corporate network policy restriction.")
        return

    if "missing required environment variable" in lowered:
        print("- .env is missing required Microsoft settings.")
        print("- Confirm MS_TENANT_ID and MS_CLIENT_ID are set.")
        return

    if "microsoft login failed" in lowered:
        print("- Sign-in started but token acquisition failed.")
        print("- Confirm the app registration allows delegated Mail.Read and User.Read.")
        print("- Confirm your account can grant/receive consent in this tenant.")
        return

    print("- Unknown startup issue. Check tenant/app settings and network access.")


def main() -> None:
    client = OutlookActionItemClient()
    try:
        items = client.build_action_list()
    except Exception as exc:
        print("Outlook action-item read failed:", exc)
        print_startup_diagnostics(exc)
        print("Check MS_TENANT_ID and MS_CLIENT_ID in .env.")
        print("MS_MAILBOX_USER is optional for delegated login (defaults to your own mailbox).")
        return

    if not items:
        print("No high-signal action items found in recent messages.")
        print("Try increasing MS_OUTLOOK_MAX_MESSAGES in .env if needed.")
        return

    print(f"Action items found: {len(items)}")
    print("Most critical work first:\n")
    for idx, item in enumerate(items, start=1):
        due_display = item.due_date or "no due date detected"
        print(f"{idx}. [{item.priority_label.upper()}] {item.subject}")
        print(f"   From: {item.sender}")
        print(f"   Due: {due_display}")
        print(f"   Score: {item.priority_score} ({item.reason})")
        if item.web_link:
            print(f"   Open in Outlook: {item.web_link}")
        print()

    output_path = PYTHON_ROOT / "output" / "outlook_action_items.csv"
    export_to_csv(items, output_path)
    print(f"Saved CSV: {output_path}")


if __name__ == "__main__":
    main()
