from pathlib import Path
import sys


# Add the Python starter folder so this example can import the local src
# package even when someone runs the file directly from the examples folder.
PYTHON_ROOT = Path(__file__).resolve().parents[1]
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from src.circuit_api_client import CircuitApiClient  # noqa: E402


def main() -> None:
    client = CircuitApiClient()

    try:
        bridge_token = client.get_bridge_access_token()
        print("Bridge access token acquired:", "yes" if bridge_token else "no")
    except Exception as exc:
        print("Bridge token request failed:", exc)

    try:
        # Keep chat separate from token retrieval so partial configuration still
        # lets users learn from the first half of the example.
        response_json = client.send_chat_prompt("Translate to French: Hello, how are you?")
        print("Chat response:")
        print(client.extract_first_message(response_json))
    except Exception as exc:
        print("Chat request failed:", exc)
        print(
            "This is expected if chat is not configured: set USE_OLLAMA=1 (default model qwen2.5-coder:7b via OLLAMA_MODEL), "
            "or set the Cisco chat variables in .env."
        )


if __name__ == "__main__":
    main()
