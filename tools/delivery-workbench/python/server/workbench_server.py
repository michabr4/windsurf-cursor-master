"""Local Delivery Workbench server — 127.0.0.1 only, no secrets in responses."""

from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = REPO_ROOT / "web"
PLAYBOOKS = REPO_ROOT / "playbooks"


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def _json_bytes(obj: object) -> bytes:
    return json.dumps(obj).encode("utf-8")


class WorkbenchHandler(BaseHTTPRequestHandler):
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

    def _serve_file(self, path: Path, content_type: str) -> None:
        if not path.is_file():
            self._json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return
        self._send(HTTPStatus.OK, _read_bytes(path), content_type)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        route = parsed.path or "/"

        if route == "/":
            self._serve_file(WEB_ROOT / "index.html", "text/html; charset=utf-8")
            return

        if route == "/styles.css":
            self._serve_file(WEB_ROOT / "styles.css", "text/css; charset=utf-8")
            return

        if route == "/api/playbooks":
            items = []
            if PLAYBOOKS.is_dir():
                for md in sorted(PLAYBOOKS.glob("*.md")):
                    items.append(
                        {
                            "id": md.stem,
                            "title": md.stem.replace("-", " ").title(),
                            "path": f"playbooks/{md.name}",
                        }
                    )
            self._json(HTTPStatus.OK, {"playbooks": items})
            return

        if route == "/api/health":
            self._json(HTTPStatus.OK, {"ok": True, "service": "delivery-workbench"})
            return

        self._json(HTTPStatus.NOT_FOUND, {"error": "Not found"})

    def log_message(self, format: str, *args: object) -> None:
        # Avoid logging request paths that might contain sensitive query strings.
        if args and isinstance(args[0], str) and "?" in args[0]:
            return
        super().log_message(format, *args)


def main() -> None:
    port = int(os.getenv("WORKBENCH_PORT", "8840"))
    server = ThreadingHTTPServer(("127.0.0.1", port), WorkbenchHandler)
    print(f"Delivery Workbench: http://127.0.0.1:{port}/")
    print("Bound to localhost only. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
