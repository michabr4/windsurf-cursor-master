"""Local Delivery Workbench server — 127.0.0.1 only, no secrets in responses."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = REPO_ROOT / "web"
PLAYBOOKS = REPO_ROOT / "playbooks"
PROJECTS = REPO_ROOT / "projects"
DATA = REPO_ROOT / "data"
SCRIPTS = REPO_ROOT / "scripts"
TEMPLATES = REPO_ROOT / "templates"

_SLUG_RE = re.compile(r"^[a-z0-9_][a-z0-9_\-]{0,63}$")
_TEMPLATE_MAP: dict[str, str] = {
    "status-report": "status-report.md",
    "meeting-notes": "meeting-notes.md",
    "raid-entry": "raid-entry.md",
}


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def _json_bytes(obj: object) -> bytes:
    return json.dumps(obj).encode("utf-8")


def _create_project(slug: str) -> dict:
    if not _SLUG_RE.match(slug):
        return {"ok": False, "error": "Invalid slug — use lowercase letters, digits, hyphens, underscores"}
    dest = PROJECTS / slug
    if dest.exists():
        return {"ok": False, "error": f"Project '{slug}' already exists"}
    src = PROJECTS / "_example"
    if src.is_dir():
        shutil.copytree(src, dest)
    else:
        dest.mkdir(parents=True)
    data_dir = DATA / slug
    data_dir.mkdir(parents=True, exist_ok=True)
    return {"ok": True, "slug": slug}


def _create_draft(slug: str, draft_type: str) -> dict:
    valid_types = list(_TEMPLATE_MAP)
    if not _SLUG_RE.match(slug):
        return {"ok": False, "error": "Invalid slug"}
    if draft_type not in _TEMPLATE_MAP:
        return {"ok": False, "error": f"Unknown type '{draft_type}'. Valid: {valid_types}"}
    proj = PROJECTS / slug
    if not proj.is_dir():
        return {"ok": False, "error": f"Project not found: {slug}"}
    src = TEMPLATES / _TEMPLATE_MAP[draft_type]
    if not src.is_file():
        return {"ok": False, "error": f"Template missing: {_TEMPLATE_MAP[draft_type]}"}
    out_dir = DATA / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    dest = out_dir / f"{today}-{draft_type}.md"
    n = 2
    while dest.exists():
        dest = out_dir / f"{today}-{draft_type}-{n}.md"
        n += 1
    shutil.copy2(src, dest)
    return {"ok": True, "name": dest.name, "path": str(dest.relative_to(REPO_ROOT))}


def _list_projects() -> dict:
    items = []
    if PROJECTS.is_dir():
        for p in sorted(PROJECTS.iterdir()):
            if p.is_dir() and not p.name.startswith("_"):
                draft_dir = DATA / p.name
                drafts = len(list(draft_dir.glob("*.md"))) if draft_dir.is_dir() else 0
                items.append({"slug": p.name, "drafts": drafts})
    return {"projects": items}


def _list_drafts(slug: str) -> dict:
    if not _SLUG_RE.match(slug):
        return {"drafts": []}
    draft_dir = DATA / slug
    items = []
    if draft_dir.is_dir():
        for f in sorted(draft_dir.glob("*.md"), reverse=True)[:20]:
            items.append({"name": f.name})
    return {"drafts": items}


def _list_briefings() -> dict:
    briefing_dir = DATA / "runs" / "morning-briefing"
    items = []
    if briefing_dir.is_dir():
        for f in sorted(briefing_dir.glob("*.md"), reverse=True)[:10]:
            items.append({"date": f.stem, "name": f.name})
    return {"runs": items}


class WorkbenchHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj: object) -> None:
        self._send(code, _json_bytes(obj), "application/json; charset=utf-8")

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(min(length, 65536))
        try:
            return json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}

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

        if route == "/api/projects":
            self._json(HTTPStatus.OK, _list_projects())
            return

        m = re.match(r"^/api/projects/([a-z0-9_][a-z0-9_\-]{0,63})/drafts$", route)
        if m:
            self._json(HTTPStatus.OK, _list_drafts(m.group(1)))
            return

        if route == "/api/briefings":
            self._json(HTTPStatus.OK, _list_briefings())
            return

        if route == "/api/health":
            self._json(HTTPStatus.OK, {"ok": True, "service": "delivery-workbench"})
            return

        self._json(HTTPStatus.NOT_FOUND, {"error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        route = parsed.path

        if route == "/api/briefings/run":
            script = SCRIPTS / "morning-briefing.py"
            try:
                result = subprocess.run(
                    [sys.executable, str(script), "--dry-run"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(REPO_ROOT),
                )
                if result.returncode == 0:
                    self._json(HTTPStatus.OK, {"ok": True, "output": result.stdout.strip()})
                else:
                    self._json(
                        HTTPStatus.INTERNAL_SERVER_ERROR,
                        {"ok": False, "error": result.stderr.strip() or result.stdout.strip()},
                    )
            except subprocess.TimeoutExpired:
                self._json(HTTPStatus.GATEWAY_TIMEOUT, {"ok": False, "error": "Briefing timed out (60 s)"})
            except Exception as exc:  # noqa: BLE001
                self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error": str(exc)})
            return

        if route == "/api/projects":
            body = self._read_json_body()
            slug = str(body.get("slug", "")).strip().lower()
            if not slug:
                self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "slug is required"})
                return
            res = _create_project(slug)
            if res["ok"]:
                self._json(HTTPStatus.CREATED, res)
            elif "already exists" in res.get("error", ""):
                self._json(HTTPStatus.CONFLICT, res)
            else:
                self._json(HTTPStatus.BAD_REQUEST, res)
            return

        m = re.match(r"^/api/projects/([a-z0-9_][a-z0-9_\-]{0,63})/drafts$", route)
        if m:
            body = self._read_json_body()
            slug = m.group(1)
            draft_type = str(body.get("type", "")).strip()
            if not draft_type:
                self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "type is required"})
                return
            res = _create_draft(slug, draft_type)
            if res["ok"]:
                self._json(HTTPStatus.CREATED, res)
            else:
                self._json(HTTPStatus.BAD_REQUEST, res)
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
