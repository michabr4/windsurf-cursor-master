"""
ServiceFlow SDM data source connectivity tester.

Reads environment variables (and optional .env file), probes configured data sources,
and writes a non-sensitive status report to source_status.json for platform rendering.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import socket
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


DEFAULT_OUT = "source_status.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_dotenv(path: Optional[Path]) -> None:
    if not path or not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        item = line.strip()
        if not item or item.startswith("#") or "=" not in item:
            continue
        key, val = item.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def env_present(keys: List[str]) -> Dict[str, bool]:
    return {k: bool(os.getenv(k)) for k in keys}


def sanitize_env_status(status: Dict[str, bool]) -> Dict[str, str]:
    return {k: ("set" if v else "missing") for k, v in status.items()}


def http_probe(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    data: Optional[bytes] = None,
    timeout: int = 8,
) -> Tuple[str, Optional[int], Optional[str], Optional[float]]:
    req = urllib.request.Request(url=url, method=method, headers=headers or {}, data=data)
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            latency = (time.perf_counter() - start) * 1000
            return "reachable", int(response.status), None, round(latency, 1)
    except urllib.error.HTTPError as ex:
        latency = (time.perf_counter() - start) * 1000
        # 4xx/5xx still confirms network reachability; auth may simply be invalid or absent.
        return "reachable_http_error", int(ex.code), f"HTTP {ex.code}", round(latency, 1)
    except Exception as ex:  # pylint: disable=broad-except
        return "unreachable", None, str(ex), None


def tcp_probe(host: str, port: int, timeout: int = 6) -> Tuple[str, Optional[str], Optional[float]]:
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            latency = (time.perf_counter() - start) * 1000
            return "reachable", None, round(latency, 1)
    except Exception as ex:  # pylint: disable=broad-except
        return "unreachable", str(ex), None


@dataclass
class SourceStatus:
    source_id: str
    source_name: str
    required_env: Dict[str, str]
    configured: bool
    connectivity_status: str
    http_status: Optional[int]
    latency_ms: Optional[float]
    detail: str
    next_steps: List[str]


def check_tac() -> SourceStatus:
    required = ["TAC_API_KEY", "TAC_API_SECRET", "TAC_BASE_URL"]
    envs = env_present(required)
    configured = all(envs.values())
    base_url = os.getenv("TAC_BASE_URL", "https://tools.cisco.com/tac/api/v2")

    headers = {}
    if os.getenv("TAC_API_KEY"):
        headers["X-API-KEY"] = os.getenv("TAC_API_KEY", "")

    status, code, err, latency = http_probe(base_url, headers=headers)
    detail = err or "Probe completed"
    if not configured:
        detail = "Missing one or more TAC env vars. " + detail

    steps = []
    if not envs["TAC_API_KEY"] or not envs["TAC_API_SECRET"]:
        steps.append("Set TAC_API_KEY and TAC_API_SECRET in your local environment.")
    if not envs["TAC_BASE_URL"]:
        steps.append("Set TAC_BASE_URL (default is tools.cisco.com/tac/api/v2).")
    if code in (401, 403):
        steps.append("Credentials likely not authorized or contract entitlement missing.")

    return SourceStatus(
        source_id="tac",
        source_name="Cisco TAC Service Request API",
        required_env=sanitize_env_status(envs),
        configured=configured,
        connectivity_status=status,
        http_status=code,
        latency_ms=latency,
        detail=detail,
        next_steps=steps,
    )


def check_dna_center() -> SourceStatus:
    required = ["DNA_CENTER_HOST", "DNA_CENTER_PORT", "DNA_CENTER_USERNAME", "DNA_CENTER_PASSWORD"]
    envs = env_present(required)
    configured = all(envs.values())
    host = os.getenv("DNA_CENTER_HOST", "")
    port = int(os.getenv("DNA_CENTER_PORT", "443"))

    if host:
        status, err, latency = tcp_probe(host, port)
        code = None
        detail = err or "TCP probe completed"
    else:
        status, code, detail, latency = "unreachable", None, "DNA_CENTER_HOST is not configured.", None

    steps = []
    if not configured:
        steps.append("Set DNA_CENTER_HOST, DNA_CENTER_PORT, DNA_CENTER_USERNAME, DNA_CENTER_PASSWORD.")
    if status != "reachable":
        steps.append("Confirm VPN/network route and firewall path to DNA Center.")

    return SourceStatus(
        source_id="dna_center",
        source_name="Cisco DNA Center / Catalyst Center",
        required_env=sanitize_env_status(envs),
        configured=configured,
        connectivity_status=status,
        http_status=code,
        latency_ms=latency,
        detail=detail,
        next_steps=steps,
    )


def check_smart_licensing() -> SourceStatus:
    required = [
        "SMART_LICENSING_CLIENT_ID",
        "SMART_LICENSING_CLIENT_SECRET",
        "SMART_LICENSING_TOKEN_URL",
        "SMART_LICENSING_API_URL",
    ]
    envs = env_present(required)
    configured = all(envs.values())
    token_url = os.getenv("SMART_LICENSING_TOKEN_URL", "https://cloudsso.cisco.com/as/token.oauth2")

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    cid = os.getenv("SMART_LICENSING_CLIENT_ID")
    csec = os.getenv("SMART_LICENSING_CLIENT_SECRET")
    if cid and csec:
        basic = base64.b64encode(f"{cid}:{csec}".encode("utf-8")).decode("utf-8")
        headers["Authorization"] = f"Basic {basic}"
    payload = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode("utf-8")

    status, code, err, latency = http_probe(token_url, method="POST", headers=headers, data=payload)
    detail = err or "Token endpoint probe completed"
    if not configured:
        detail = "Missing one or more Smart Licensing env vars. " + detail

    steps = []
    if not configured:
        steps.append("Set Smart Licensing client ID/secret and URLs.")
    if code in (400, 401, 403):
        steps.append("Validate Smart Account app registration and client credentials.")

    return SourceStatus(
        source_id="smart_licensing",
        source_name="Cisco Smart Software Manager API",
        required_env=sanitize_env_status(envs),
        configured=configured,
        connectivity_status=status,
        http_status=code,
        latency_ms=latency,
        detail=detail,
        next_steps=steps,
    )


def check_webex() -> SourceStatus:
    required = ["WEBEX_BOT_TOKEN"]
    envs = env_present(required)
    configured = all(envs.values())
    token = os.getenv("WEBEX_BOT_TOKEN", "")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    status, code, err, latency = http_probe("https://webexapis.com/v1/people/me", headers=headers)
    detail = err or "WebEx API probe completed"
    if not configured:
        detail = "WEBEX_BOT_TOKEN missing. " + detail

    steps = []
    if not configured:
        steps.append("Set WEBEX_BOT_TOKEN in environment.")
    if code in (401, 403):
        steps.append("Verify WebEx bot token validity and app scopes.")

    return SourceStatus(
        source_id="webex",
        source_name="Cisco WebEx REST API",
        required_env=sanitize_env_status(envs),
        configured=configured,
        connectivity_status=status,
        http_status=code,
        latency_ms=latency,
        detail=detail,
        next_steps=steps,
    )


def check_support_enrichment() -> SourceStatus:
    required = ["CISCO_SUPPORT_API_KEY", "CISCO_SUPPORT_API_SECRET"]
    envs = env_present(required)
    configured = all(envs.values())
    headers = {}
    if os.getenv("CISCO_SUPPORT_API_KEY"):
        headers["X-API-KEY"] = os.getenv("CISCO_SUPPORT_API_KEY", "")

    # Probe a known support API base path.
    url = "https://api.cisco.com"
    status, code, err, latency = http_probe(url, headers=headers)
    detail = err or "Support API base probe completed"
    if not configured:
        detail = "Support enrichment credentials not configured. " + detail

    steps = []
    if not configured:
        steps.append("Set CISCO_SUPPORT_API_KEY and CISCO_SUPPORT_API_SECRET for EoX/Contract/Bug enrichment.")
    steps.append("After credentials, wire EoX, warranty, contract, and bug adapters into sync jobs.")

    return SourceStatus(
        source_id="support_enrichment",
        source_name="Cisco Support APIs (Contract / EoX / Bug)",
        required_env=sanitize_env_status(envs),
        configured=configured,
        connectivity_status=status,
        http_status=code,
        latency_ms=latency,
        detail=detail,
        next_steps=steps,
    )


def build_report() -> Dict:
    checks = [
        check_tac(),
        check_dna_center(),
        check_smart_licensing(),
        check_webex(),
        check_support_enrichment(),
    ]

    sources = [asdict(item) for item in checks]
    configured_count = sum(1 for x in checks if x.configured)
    reachable_count = sum(1 for x in checks if x.connectivity_status.startswith("reachable"))

    return {
        "generated_at": utc_now(),
        "summary": {
            "total_sources": len(checks),
            "configured_sources": configured_count,
            "reachable_sources": reachable_count,
        },
        "sources": sources,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe ServiceFlow SDM data source connectivity.")
    parser.add_argument("--env-file", default=None, help="Optional .env file path")
    parser.add_argument("--output", default=DEFAULT_OUT, help="Output JSON file path")
    args = parser.parse_args()

    env_file = Path(args.env_file).resolve() if args.env_file else None
    load_dotenv(env_file)

    report = build_report()
    out_path = Path(args.output).resolve()
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Wrote source connectivity report: {out_path}")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
