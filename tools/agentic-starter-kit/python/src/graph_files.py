"""Microsoft Graph API — OneDrive and SharePoint files module.

List, download, and upload files in the signed-in user's OneDrive and in
SharePoint document libraries.

Required Azure app permissions (delegated):
    Files.Read          — read items in the user's OneDrive
    Files.ReadWrite     — also create/upload files to OneDrive
    Sites.Read.All      — read items in any SharePoint site the user can access
    User.Read           — resolve the signed-in user

Usage:
    from src.graph_files import GraphFiles

    files = GraphFiles()

    # List root of personal OneDrive
    items = files.list_drive_items()
    for item in items:
        print(item["name"], item["size"], item["item_type"])

    # Download a file by item ID
    content = files.download_file(items[0]["id"])
    with open(items[0]["name"], "wb") as f:
        f.write(content)

    # Upload a file
    result = files.upload_file("/Documents", "report.txt", b"Hello world")
    print("Uploaded:", result["web_url"])
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any

import requests

from .graph_client import GraphClient

FILES_SCOPES = [
    "Files.Read",
    "Files.ReadWrite",
    "Sites.Read.All",
    "User.Read",
]

_UPLOAD_SESSION_THRESHOLD = 4 * 1024 * 1024


class GraphFiles:
    """Read and write OneDrive and SharePoint files via Microsoft Graph.

    Args:
        client: Optional pre-built GraphClient. One is created automatically
                with FILES_SCOPES if not provided.
    """

    def __init__(self, client: GraphClient | None = None) -> None:
        self._client = client or GraphClient(scopes=FILES_SCOPES)

    def list_drive_items(
        self,
        folder_path: str = "/",
        max_results: int = 100,
    ) -> list[dict[str, Any]]:
        """List items in the user's OneDrive at the given folder path.

        Args:
            folder_path: POSIX-style path relative to drive root, e.g.
                         "/Documents/Reports". Use "/" for the root.
            max_results: Max items to return (across all pages).

        Returns:
            List of item dicts with keys: id, name, size, item_type
            (file|folder), mime_type, created_at, modified_at, web_url,
            download_url.
        """
        if folder_path in ("/", ""):
            path = "/me/drive/root/children"
        else:
            clean = folder_path.strip("/")
            path = f"/me/drive/root:/{clean}:/children"

        params = {
            "$top": min(max_results, 200),
            "$select": (
                "id,name,size,file,folder,createdDateTime,"
                "lastModifiedDateTime,webUrl,@microsoft.graph.downloadUrl"
            ),
        }
        raw = self._client.get_paged(path, params=params, max_pages=5)
        return [self._normalize_item(i) for i in raw]

    def get_item_by_path(self, item_path: str) -> dict[str, Any]:
        """Resolve a single drive item by its path.

        Args:
            item_path: Full path from drive root, e.g. "/Documents/report.txt".
        """
        clean = item_path.strip("/")
        raw = self._client.get(f"/me/drive/root:/{clean}")
        return self._normalize_item(raw)

    def download_file(self, item_id: str) -> bytes:
        """Download a file's raw bytes by its drive item ID.

        Args:
            item_id: The file's drive item ID (from list_drive_items).
        """
        return self._client.get_bytes(f"/me/drive/items/{item_id}/content")

    def download_file_by_path(self, item_path: str) -> bytes:
        """Download a file by its path in the drive.

        Args:
            item_path: Full path from drive root, e.g. "/Documents/report.txt".
        """
        clean = item_path.strip("/")
        return self._client.get_bytes(f"/me/drive/root:/{clean}:/content")

    def upload_file(
        self,
        folder_path: str,
        filename: str,
        content: bytes,
        conflict_behavior: str = "rename",
    ) -> dict[str, Any]:
        """Upload a file to the user's OneDrive.

        For files ≤ 4 MB, uses simple PUT upload.
        For files > 4 MB, uses resumable upload session.

        Args:
            folder_path:        Destination folder path (e.g. "/Documents").
            filename:           Destination filename (no path separators).
            content:            Raw file bytes.
            conflict_behavior:  "rename" | "replace" | "fail" on name conflict.

        Returns:
            Uploaded item dict with web_url and download_url.
        """
        if "/" in filename or "\\" in filename:
            raise ValueError("filename must not contain path separators")

        folder_path = folder_path.strip("/")
        dest = f"{folder_path}/{filename}" if folder_path else filename

        if len(content) <= _UPLOAD_SESSION_THRESHOLD:
            raw = self._client.put_bytes(
                f"https://graph.microsoft.com/v1.0/me/drive/root:/{dest}:/content"
                f"?@microsoft.graph.conflictBehavior={conflict_behavior}",
                data=content,
            )
        else:
            raw = self._upload_large_file(dest, content, conflict_behavior)

        return self._normalize_item(raw)

    def _upload_large_file(
        self,
        dest_path: str,
        content: bytes,
        conflict_behavior: str,
    ) -> dict[str, Any]:
        """Use a resumable upload session for files > 4 MB."""
        session_payload = {
            "item": {
                "@microsoft.graph.conflictBehavior": conflict_behavior,
            }
        }
        session = self._client.post(
            f"/me/drive/root:/{dest_path}:/createUploadSession",
            json=session_payload,
        )
        upload_url = session.get("uploadUrl", "")
        if not upload_url:
            raise RuntimeError("Failed to create upload session")

        chunk_size = 3 * 1024 * 1024
        total = len(content)
        result: dict[str, Any] = {}

        for offset in range(0, total, chunk_size):
            chunk = content[offset: offset + chunk_size]
            end = offset + len(chunk) - 1
            headers = {
                "Content-Range": f"bytes {offset}-{end}/{total}",
                "Content-Length": str(len(chunk)),
            }
            resp = requests.put(upload_url, headers=headers, data=chunk, timeout=120)
            resp.raise_for_status()
            if resp.content:
                result = resp.json()

        return result

    def create_folder(self, parent_path: str, folder_name: str) -> dict[str, Any]:
        """Create a new folder in OneDrive.

        Args:
            parent_path:  Path of the parent folder (e.g. "/Documents").
            folder_name:  Name of the new folder.
        """
        if parent_path in ("/", ""):
            path = "/me/drive/root/children"
        else:
            clean = parent_path.strip("/")
            path = f"/me/drive/root:/{clean}:/children"

        payload = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename",
        }
        raw = self._client.post(path, json=payload)
        return self._normalize_item(raw)

    def list_sharepoint_sites(self, search: str = "") -> list[dict[str, Any]]:
        """Search for SharePoint sites the user can access.

        Args:
            search: Optional keyword to filter sites by display name.
                    Omit to return the most popular sites.

        Returns:
            List of site dicts with keys: id, display_name, web_url.
        """
        if search:
            raw = self._client.get_paged(
                f"/sites?search={search}",
                params={"$select": "id,displayName,webUrl"},
            )
        else:
            raw = self._client.get_paged(
                "/sites?search=*",
                params={"$select": "id,displayName,webUrl", "$top": 20},
            )

        return [
            {
                "id": s.get("id", ""),
                "display_name": s.get("displayName", ""),
                "web_url": s.get("webUrl", ""),
            }
            for s in raw
        ]

    def list_site_drive_items(
        self,
        site_id: str,
        folder_path: str = "/",
        max_results: int = 100,
    ) -> list[dict[str, Any]]:
        """List items in a SharePoint site's default document library.

        Args:
            site_id:      The site ID (from list_sharepoint_sites).
            folder_path:  Path within the document library, or "/" for root.
            max_results:  Max items to return.
        """
        if folder_path in ("/", ""):
            path = f"/sites/{site_id}/drive/root/children"
        else:
            clean = folder_path.strip("/")
            path = f"/sites/{site_id}/drive/root:/{clean}:/children"

        params = {
            "$top": min(max_results, 200),
            "$select": (
                "id,name,size,file,folder,createdDateTime,"
                "lastModifiedDateTime,webUrl,@microsoft.graph.downloadUrl"
            ),
        }
        raw = self._client.get_paged(path, params=params, max_pages=5)
        return [self._normalize_item(i) for i in raw]

    def download_site_file(self, site_id: str, item_id: str) -> bytes:
        """Download a file from a SharePoint site by item ID."""
        return self._client.get_bytes(f"/sites/{site_id}/drive/items/{item_id}/content")

    @staticmethod
    def _normalize_item(raw: dict[str, Any]) -> dict[str, Any]:
        is_folder = "folder" in raw
        is_file = "file" in raw
        file_block = raw.get("file") or {}

        return {
            "id": raw.get("id", ""),
            "name": raw.get("name", ""),
            "size": raw.get("size", 0),
            "item_type": "folder" if is_folder else ("file" if is_file else "unknown"),
            "mime_type": file_block.get("mimeType", ""),
            "created_at": raw.get("createdDateTime", ""),
            "modified_at": raw.get("lastModifiedDateTime", ""),
            "web_url": raw.get("webUrl", ""),
            "download_url": raw.get("@microsoft.graph.downloadUrl", ""),
            "child_count": raw.get("folder", {}).get("childCount", 0) if is_folder else 0,
        }
