"""Small Webex API client used by the starter examples.

The methods intentionally stay simple so beginners can follow the request flow
without needing a framework or SDK.
"""

import os
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv


load_dotenv()


class WebexClient:
    def __init__(self) -> None:
        self.access_token = os.getenv("WEBEX_ACCESS_TOKEN")
        self.base_url = os.getenv("WEBEX_API_BASE_URL", "https://webexapis.com/v1").rstrip("/")
        self.max_page_size = int(os.getenv("WEBEX_MAX_PAGE_SIZE", "50"))

    def _require_token(self) -> str:
        if not self.access_token:
            raise ValueError("Missing required environment variable: WEBEX_ACCESS_TOKEN")
        return self.access_token

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._require_token()}",
            "Content-Type": "application/json",
        }

    def _get_all_pages(self, path: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        next_url = f"{self.base_url}{path}"
        request_params = dict(params or {})
        request_params.setdefault("max", self.max_page_size)
        items: List[Dict[str, Any]] = []

        while next_url:
            response = requests.get(next_url, headers=self._headers(), params=request_params, timeout=60)
            response.raise_for_status()
            payload = response.json()
            items.extend(payload.get("items", []))
            next_url = response.links.get("next", {}).get("url")
            # Follow-up pages already contain the query string in the next link.
            request_params = {}

        return items

    def list_spaces(self) -> List[Dict[str, Any]]:
        # The Webex API path is /rooms even though users usually say "spaces".
        return self._get_all_pages("/rooms")

    def list_messages(self, room_id: str) -> List[Dict[str, Any]]:
        return self._get_all_pages("/messages", {"roomId": room_id})

    def list_recordings(self) -> List[Dict[str, Any]]:
        return self._get_all_pages("/recordings")

    def list_transcripts(self) -> List[Dict[str, Any]]:
        return self._get_all_pages("/meeting/transcripts")

    def get_transcript_details(self, transcript_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/meeting/transcripts/{transcript_id}",
            headers=self._headers(),
            timeout=60,
        )
        response.raise_for_status()
        return response.json()
