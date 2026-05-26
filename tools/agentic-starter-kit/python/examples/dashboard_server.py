"""Tiny local server: serves web/dashboard.html and JSON APIs backed by starter clients.

Secrets stay in .env and are never sent to the browser. For trusted local use only.
"""

from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
from urllib.parse import urlparse


PYTHON_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PYTHON_ROOT.parent
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from src.circuit_api_client import CircuitApiClient  # noqa: E402
from src.webex_client import WebexClient  # noqa: E402


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def _json_bytes(obj: object) -> bytes:
    return json.dumps(obj).encode("utf-8")


class DashboardHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj: object) -> None:
        self._send(code, _json_bytes(obj), "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path or "/"

        if path == "/":
            html_path = REPO_ROOT / "web" / "dashboard.html"
            if not html_path.is_file():
                self._json(HTTPStatus.NOT_FOUND, {"error": "dashboard.html missing"})
                return
            self._send(HTTPStatus.OK, _read_bytes(html_path), "text/html; charset=utf-8")
            return

        if path == "/styles.css":
            css_path = REPO_ROOT / "web" / "styles.css"
            if not css_path.is_file():
                self._json(HTTPStatus.NOT_FOUND, {"error": "styles.css missing"})
                return
            self._send(HTTPStatus.OK, _read_bytes(css_path), "text/css; charset=utf-8")
            return

        if path == "/api/webex/spaces":
            try:
                client = WebexClient()
                raw = client.list_spaces()
            except Exception as exc:
                self._json(HTTPStatus.OK, {"ok": False, "error": str(exc), "spaces": []})
                return
            spaces = []
            for item in raw[:25]:
                sid = item.get("id")
                title = item.get("title")
                if isinstance(sid, str) and sid:
                    spaces.append({"id": sid, "title": title if isinstance(title, str) else ""})
            self._json(HTTPStatus.OK, {"ok": True, "spaces": spaces})
            return

        if path == "/api/circuit/bridge":
            client = CircuitApiClient()
            try:
                token = client.get_bridge_access_token()
            except Exception as exc:
                self._json(HTTPStatus.OK, {"ok": False, "detail": str(exc)})
                return
            self._json(HTTPStatus.OK, {"ok": bool(token), "detail": ""})
            return

        self._json(HTTPStatus.NOT_FOUND, {"error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/api/circuit/chat":
            self._json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return

        length = int(self.headers.get("Content-Length", "0") or "0")
        if length > 16_384:
            self._json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "Body too large"})
            return

        raw_body = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw_body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json(HTTPStatus.BAD_REQUEST, {"error": "Invalid JSON"})
            return

        prompt = body.get("prompt", "Say hello in one sentence.")
        if not isinstance(prompt, str):
            self._json(HTTPStatus.BAD_REQUEST, {"error": "prompt must be a string"})
            return
        prompt = prompt.strip()
        if len(prompt) > 4_000:
            self._json(HTTPStatus.BAD_REQUEST, {"error": "prompt too long"})
            return
        if not prompt:
            prompt = "Say hello in one sentence."

        client = CircuitApiClient()
        try:
            response_json = client.send_chat_prompt(prompt)
            reply = client.extract_first_message(response_json)
        except Exception as exc:
            self._json(HTTPStatus.OK, {"ok": False, "error": str(exc), "reply": ""})
            return

        self._json(HTTPStatus.OK, {"ok": True, "reply": reply})

    def log_message(self, format: str, *args: object) -> None:
        sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format % args))


def main() -> None:
    port = int(os.getenv("APP_PORT", "8844"))
    server = ThreadingHTTPServer(("127.0.0.1", port), DashboardHandler)
    print(f"Dashboard: http://127.0.0.1:{port}/")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
