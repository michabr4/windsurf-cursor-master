from pathlib import Path
import sys


# Add the Python starter folder so this example can import the local src
# package even when someone runs the file directly from the examples folder.
PYTHON_ROOT = Path(__file__).resolve().parents[1]
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from src.webex_client import WebexClient  # noqa: E402


def main() -> None:
    client = WebexClient()

    spaces = client.list_spaces()
    print(f"Spaces found: {len(spaces)}")
    for space in spaces[:5]:
        print("-", space.get("title") or space.get("id"))

    if spaces:
        # Use the first available space to keep the starter flow short.
        first_space_id = spaces[0].get("id", "")
        messages = client.list_messages(first_space_id)
        print(f"Messages in first space: {len(messages)}")
        for message in messages[:5]:
            print("-", (message.get("text") or "").strip()[:80] or "<no text>")

    try:
        recordings = client.list_recordings()
        print(f"Recordings found: {len(recordings)}")
    except Exception as exc:
        print("Recording list failed:", exc)
        print("This can happen if the PAT owner does not have meeting recording access.")

    try:
        transcripts = client.list_transcripts()
        print(f"Transcripts found: {len(transcripts)}")
        if transcripts:
            details = client.get_transcript_details(transcripts[0]["id"])
            print("First transcript id:", details.get("id"))
    except Exception as exc:
        # Transcript access is often empty or restricted even when spaces work.
        print("Transcript access failed:", exc)
        print("This can happen if the PAT owner does not have transcript access or none are available.")


if __name__ == "__main__":
    main()
