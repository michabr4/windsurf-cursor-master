"""Microsoft Graph API — shared authenticated base client.

Handles MSAL device-code auth (no client secret required) with in-memory
token caching and automatic refresh. All Graph service modules (calendar,
teams, files) extend or compose this client.

Environment variables (same names used across the starter kit):
    MS_TENANT_ID   — Azure AD tenant ID or "organizations" for multi-tenant
    MS_CLIENT_ID   — App registration client ID (portal.azure.com)

Usage:
    from src.graph_client import GraphClient

    client = GraphClient(scopes=["Mail.Read", "Calendars.Read", "User.Read"])
    me = client.get("/me")
    print(me["displayName"])
"""

from __future__ import annotations

import os
from typing import Any

import msal
import requests
from dotenv import load_dotenv

load_dotenv()

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

_DEFAULT_SCOPES = ["User.Read"]


class GraphClient:
    """Authenticated Microsoft Graph API client using MSAL device-code flow.

    Args:
        scopes: List of Graph permission scopes to request. Defaults to
                ["User.Read"]. Pass the full set your application needs
                so a single interactive login grants all permissions.
        tenant_id: Azure AD tenant ID. Falls back to MS_TENANT_ID env var.
        client_id: App registration client ID. Falls back to MS_CLIENT_ID env var.
    """

    def __init__(
        self,
        scopes: list[str] | None = None,
        tenant_id: str | None = None,
        client_id: str | None = None,
    ) -> None:
        self._tenant_id = (
            tenant_id
            or os.getenv("MS_TENANT_ID")
            or os.getenv("AZURE_TENANT_ID")
            or "organizations"
        )
        self._client_id = client_id or os.getenv("MS_CLIENT_ID") or os.getenv("AZURE_CLIENT_ID") or ""
        if not self._client_id:
            raise ValueError(
                "MS_CLIENT_ID (or AZURE_CLIENT_ID) must be set. "
                "Register an app at https://portal.azure.com."
            )
        self._scopes = list(scopes) if scopes else list(_DEFAULT_SCOPES)
        self._access_token: str | None = None
        self._msal_app = msal.PublicClientApplication(
            client_id=self._client_id,
            authority=f"https://login.microsoftonline.com/{self._tenant_id}",
        )

    def _authenticate(self) -> str:
        """Return a valid access token, refreshing silently or via device code."""
        if self._access_token:
            return self._access_token

        accounts = self._msal_app.get_accounts()
        result: dict[str, Any] = {}

        if accounts:
            result = self._msal_app.acquire_token_silent(self._scopes, account=accounts[0]) or {}

        if "access_token" not in result:
            flow = self._msal_app.initiate_device_flow(scopes=self._scopes)
            if "user_code" not in flow:
                raise RuntimeError(
                    f"Device-code flow failed: {flow.get('error_description', 'unknown error')}"
                )

            print("\n┌────────────────────────────────────────────────┐")
            print("│  Microsoft Graph — sign-in required             │")
            print("│                                                  │")
            print(f"│  Open:  {flow['verification_uri']:<41}│")
            print(f"│  Code:  {flow['user_code']:<41}│")
            print("│                                                  │")
            print("│  Waiting for sign-in...                          │")
            print("└────────────────────────────────────────────────┘\n")

            result = self._msal_app.acquire_token_by_device_flow(flow)

        if "access_token" not in result:
            raise RuntimeError(
                f"Authentication failed: {result.get('error_description', 'unknown error')}"
            )

        self._access_token = result["access_token"]
        return self._access_token

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._authenticate()}",
            "Content-Type": "application/json",
        }

    def _url(self, path: str) -> str:
        return f"{GRAPH_BASE_URL}{path}" if path.startswith("/") else path

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """HTTP GET — returns parsed JSON."""
        resp = requests.get(self._url(path), headers=self._headers(), params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        """HTTP POST — returns parsed JSON (or empty dict for 204 No Content)."""
        resp = requests.post(self._url(path), headers=self._headers(), json=json, timeout=30)
        resp.raise_for_status()
        return resp.json() if resp.content else {}

    def patch(self, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        """HTTP PATCH — returns parsed JSON."""
        resp = requests.patch(self._url(path), headers=self._headers(), json=json, timeout=30)
        resp.raise_for_status()
        return resp.json() if resp.content else {}

    def delete(self, path: str) -> None:
        """HTTP DELETE — raises on error, returns nothing."""
        resp = requests.delete(self._url(path), headers=self._headers(), timeout=30)
        resp.raise_for_status()

    def get_bytes(self, path: str) -> bytes:
        """HTTP GET that returns raw bytes (for file downloads)."""
        resp = requests.get(self._url(path), headers=self._headers(), timeout=60)
        resp.raise_for_status()
        return resp.content

    def put_bytes(self, url: str, data: bytes, content_type: str = "application/octet-stream") -> dict[str, Any]:
        """HTTP PUT with raw bytes body — used for upload sessions."""
        headers = {
            "Authorization": f"Bearer {self._authenticate()}",
            "Content-Type": content_type,
            "Content-Length": str(len(data)),
        }
        resp = requests.put(url, headers=headers, data=data, timeout=120)
        resp.raise_for_status()
        return resp.json() if resp.content else {}

    def get_paged(self, path: str, params: dict[str, Any] | None = None, max_pages: int = 10) -> list[dict[str, Any]]:
        """Fetch all pages from a paged Graph endpoint.

        Follows ``@odata.nextLink`` automatically up to ``max_pages`` pages.

        Returns:
            Flat list of all items from the ``value`` array across all pages.
        """
        items: list[dict[str, Any]] = []
        url: str | None = self._url(path)
        page = 0

        while url and page < max_pages:
            resp = requests.get(url, headers=self._headers(), params=params if page == 0 else None, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            items.extend(data.get("value", []))
            url = data.get("@odata.nextLink")
            page += 1

        return items

    def whoami(self) -> dict[str, Any]:
        """Return the signed-in user's profile."""
        return self.get("/me?$select=displayName,mail,userPrincipalName,id")
