"""Local server for Asana task review UI + JSON API.

Serves web/asana_review.html and proxies Asana with ASANA_ACCESS_TOKEN from .env.
Bind: 127.0.0.1 only. Set ASANA_REVIEW_PORT (default 8845).

Webhook (optional): POST /api/asana/webhook with header X-Asana-Review-Secret
matching ASANA_REVIEW_WEBHOOK_SECRET. Body: {"task":"GID or URL"} or Asana events[].

Run: python python/examples/asana_review_server.py
"""

from __future__ import annotations

import json
import os
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse


PYTHON_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PYTHON_ROOT.parent
OUT_DIR = REPO_ROOT / "out" / "asana-reviews"

if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from src.asana_client import AsanaClient, normalize_task_gid  # noqa: E402
from src.asana_oauth import (  # noqa: E402
    exchange_code,
    is_authenticated,
    login_start_url,
    oauth_configured,
    redirect_uri,
)
from src.asana_review_service import outcome_to_api_dict, review_task  # noqa: E402


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def _json_bytes(obj: object) -> bytes:
    return json.dumps(obj).encode("utf-8")


def _origin_ok(origin: str | None) -> bool:
    if not origin:
        return True
    if origin == "null":
        return True
    return origin.startswith("http://127.0.0.1:") or origin.startswith("http://localhost:")


def _parse_json_body(raw: bytes, max_len: int) -> dict[str, object] | None:
    if len(raw) > max_len:
        return None
    try:
        out = json.loads(raw.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return None
    return out if isinstance(out, dict) else None


def _body_bool(body: Dict[str, object], key: str) -> Optional[bool]:
    if key not in body:
        return None
    v = body[key]
    if v is True:
        return True
    if v is False:
        return False
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ("1", "true", "yes", "on"):
            return True
        if s in ("0", "false", "no", "off"):
            return False
    return None


def _webhook_secret_configured() -> bool:
    return bool(os.getenv("ASANA_REVIEW_WEBHOOK_SECRET", "").strip())


def _webhook_secret_ok(headers: Any) -> bool:
    expected = os.getenv("ASANA_REVIEW_WEBHOOK_SECRET", "").strip()
    if not expected:
        return False
    got = headers.get("X-Asana-Review-Secret", "")
    return got == expected


def _extract_task_ref(body: Dict[str, object]) -> Optional[str]:
    task_raw = body.get("task")
    if isinstance(task_raw, str) and task_raw.strip():
        return task_raw.strip()
    events = body.get("events")
    if isinstance(events, list):
        for ev in events:
            if not isinstance(ev, dict):
                continue
            res = ev.get("resource")
            if not isinstance(res, dict):
                continue
            if res.get("resource_type") != "task":
                continue
            gid = res.get("gid")
            if isinstance(gid, (str, int)):
                return str(gid)
    return None


class AsanaReviewHandler(BaseHTTPRequestHandler):
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

    def _redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.FOUND)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def _html_page(self, title: str, body: str) -> None:
        page = f"""<!doctype html><html><head><meta charset="utf-8"><title>{title}</title></head>
<body style="font-family:system-ui;max-width:40rem;margin:2rem auto;padding:0 1rem;">
<h1>{title}</h1>{body}<p><a href="/">Back to task review</a></p></body></html>"""
        self._send(HTTPStatus.OK, page.encode("utf-8"), "text/html; charset=utf-8")

    def log_error(self, format: str, *args: object) -> None:
        sys.stderr.write("ERROR %s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format % args))

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", self.headers.get("Origin", "*"))
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type, Accept, X-Asana-Review-Secret",
        )
        self.send_header("Access-Control-Max-Age", "600")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path or "/"

        if path == "/":
            html_path = REPO_ROOT / "web" / "asana_review.html"
            if not html_path.is_file():
                self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "asana_review.html missing"})
                return
            self._send(HTTPStatus.OK, _read_bytes(html_path), "text/html; charset=utf-8")
            return

        if path == "/styles.css":
            css_path = REPO_ROOT / "web" / "styles.css"
            if not css_path.is_file():
                self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "styles.css missing"})
                return
            self._send(HTTPStatus.OK, _read_bytes(css_path), "text/css; charset=utf-8")
            return

        if path in ("/oauth/start", "/api/asana/oauth/start"):
            try:
                self._redirect(login_start_url())
            except ValueError as exc:
                self._html_page("Asana login", f"<p>{exc}</p>")
            return

        if path == "/oauth/callback":
            qs = parse_qs(parsed.query or "")
            err = qs.get("error", [""])[0]
            if err:
                self._html_page("Asana login failed", f"<p>Asana returned: <code>{err}</code></p>")
                return
            code = qs.get("code", [""])[0]
            state = qs.get("state", [""])[0]
            if not code or not state:
                self._html_page("Asana login", "<p>Missing code or state in callback.</p>")
                return
            try:
                exchange_code(code, state)
            except (ValueError, RuntimeError) as exc:
                self._html_page("Asana login failed", f"<p>{exc}</p>")
                return
            self._html_page(
                "Asana connected",
                "<p>You are signed in. Tokens were saved to <code>.env</code> on this machine.</p>",
            )
            return

        if path == "/api/asana/auth-status":
            port = os.getenv("ASANA_REVIEW_PORT", "8845")
            self._json(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "oauth_configured": oauth_configured(),
                    "authenticated": is_authenticated(),
                    "login_url": f"http://127.0.0.1:{port}/oauth/start",
                    "redirect_uri": redirect_uri(),
                },
            )
            return

        self._json(
            HTTPStatus.NOT_FOUND,
            {
                "ok": False,
                "error": "Not found",
                "hint": "Restart asana_review_server.py after updates. OAuth login: GET /oauth/start",
                "paths": ["/", "/oauth/start", "/oauth/callback", "/api/asana/auth-status"],
            },
        )

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path or "/"
        origin = self.headers.get("Origin")

        if path == "/api/asana/webhook":
            if not _webhook_secret_configured():
                self._json(
                    HTTPStatus.SERVICE_UNAVAILABLE,
                    {"ok": False, "error": "Set ASANA_REVIEW_WEBHOOK_SECRET in .env to enable webhooks"},
                )
                return
            if not _webhook_secret_ok(self.headers):
                self._json(HTTPStatus.UNAUTHORIZED, {"ok": False, "error": "Invalid webhook secret"})
                return
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length) if length else b"{}"
            body = _parse_json_body(raw, 65_536)
            if body is None:
                self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "Invalid JSON or body too large"})
                return
            task_ref = _extract_task_ref(body)
            if not task_ref:
                self._json(
                    HTTPStatus.BAD_REQUEST,
                    {"ok": False, "error": 'Provide "task" or an Asana events[] payload with a task resource'},
                )
                return
            use_llm = _body_bool(body, "use_llm")
            post = _body_bool(body, "post") is True
            try:
                gid = normalize_task_gid(task_ref)
                outcome = review_task(gid, out_dir=OUT_DIR, use_llm=use_llm)
            except ValueError as exc:
                self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                return
            except RuntimeError as exc:
                self._json(HTTPStatus.BAD_GATEWAY, {"ok": False, "error": str(exc)})
                return

            payload = outcome_to_api_dict(outcome)
            if post:
                story = AsanaClient().add_comment_story(gid, outcome.suggested_comment)
                payload["posted"] = True
                payload["story_gid"] = story.get("gid", "")
            else:
                payload["posted"] = False
            self._json(HTTPStatus.OK, payload)
            return

        if path == "/api/asana/review":
            if not _origin_ok(origin):
                self._json(HTTPStatus.FORBIDDEN, {"ok": False, "error": "Origin not allowed"})
                return
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length) if length else b"{}"
            body = _parse_json_body(raw, 4096)
            if body is None:
                self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "Invalid JSON or body too large"})
                return
            task_raw = body.get("task")
            if not isinstance(task_raw, str) or not task_raw.strip():
                self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "task must be a non-empty string"})
                return
            use_llm = _body_bool(body, "use_llm")

            try:
                gid = normalize_task_gid(task_raw.strip())
                outcome = review_task(gid, out_dir=OUT_DIR, use_llm=use_llm)
            except ValueError as exc:
                self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                return
            except RuntimeError as exc:
                self._json(HTTPStatus.BAD_GATEWAY, {"ok": False, "error": str(exc)})
                return

            self._json(HTTPStatus.OK, outcome_to_api_dict(outcome))
            return

        if path == "/api/asana/post-comment":
            if not _origin_ok(origin):
                self._json(HTTPStatus.FORBIDDEN, {"ok": False, "error": "Origin not allowed"})
                return
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length) if length else b"{}"
            body = _parse_json_body(raw, 32_768)
            if body is None:
                self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "Invalid JSON or body too large"})
                return
            gid_raw = body.get("task_gid")
            text_raw = body.get("text")
            if not isinstance(gid_raw, str) or not isinstance(text_raw, str):
                self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "task_gid and text must be strings"})
                return
            text = text_raw.strip()
            if len(text) < 1 or len(text) > 8000:
                self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "text length must be 1..8000"})
                return
            try:
                gid = normalize_task_gid(gid_raw.strip())
                story = AsanaClient().add_comment_story(gid, text)
            except ValueError as exc:
                self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                return
            except RuntimeError as exc:
                self._json(HTTPStatus.BAD_GATEWAY, {"ok": False, "error": str(exc)})
                return

            sid = story.get("gid", "")
            self._json(HTTPStatus.OK, {"ok": True, "story_gid": sid})
            return

        self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "Not found"})

    def log_message(self, format: str, *args: object) -> None:
        sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format % args))


def main() -> None:
    port = int(os.getenv("ASANA_REVIEW_PORT", "8845"))
    server = ThreadingHTTPServer(("127.0.0.1", port), AsanaReviewHandler)
    print(f"Asana review UI: http://127.0.0.1:{port}/")
    if oauth_configured():
        print(f"Asana OAuth login: http://127.0.0.1:{port}/oauth/start")
        print(f"Redirect URI (register in Asana app): {redirect_uri()}")
    if _webhook_secret_configured():
        print(f"Webhook: POST http://127.0.0.1:{port}/api/asana/webhook (X-Asana-Review-Secret)")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
