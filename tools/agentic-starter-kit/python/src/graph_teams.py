"""Microsoft Graph API — Microsoft Teams module.

Read and send Teams chat messages and channel posts for the signed-in user.

Required Azure app permissions (delegated):
    Chat.Read           — read 1:1 and group chat messages
    Chat.ReadWrite      — also send messages to chats
    Team.ReadBasic.All  — list teams the user belongs to
    Channel.ReadBasic.All — list channels in a team
    User.Read           — resolve the signed-in user

Note on ChannelMessage.Read.All: This permission requires admin consent in
most organisations. The methods here use Chat.Read for DM/group chats (which
does NOT require admin consent) and fall back gracefully for channels.

Usage:
    from src.graph_teams import GraphTeams

    teams = GraphTeams()
    chats = teams.list_chats()
    for chat in chats[:3]:
        print(chat["topic"], chat["chat_type"])

    msgs = teams.get_chat_messages(chats[0]["id"])
    for m in msgs:
        print(m["sender"], ":", m["body_preview"])
"""

from __future__ import annotations

from typing import Any

from .graph_client import GraphClient

TEAMS_SCOPES = [
    "Chat.Read",
    "Chat.ReadWrite",
    "Team.ReadBasic.All",
    "Channel.ReadBasic.All",
    "User.Read",
]


class GraphTeams:
    """Read and write Microsoft Teams messages via Microsoft Graph.

    Args:
        client: Optional pre-built GraphClient. One is created automatically
                with TEAMS_SCOPES if not provided.
    """

    def __init__(self, client: GraphClient | None = None) -> None:
        self._client = client or GraphClient(scopes=TEAMS_SCOPES)

    def list_chats(self, max_results: int = 50) -> list[dict[str, Any]]:
        """List all chats (1:1, group, meeting) for the signed-in user.

        Returns:
            List of chat dicts with keys: id, topic, chat_type,
            web_url, last_updated.
        """
        params = {
            "$top": max_results,
            "$select": "id,topic,chatType,webUrl,lastUpdatedDateTime",
            "$orderby": "lastUpdatedDateTime desc",
        }
        raw = self._client.get_paged("/me/chats", params=params)
        return [self._normalize_chat(c) for c in raw]

    def get_chat_messages(
        self,
        chat_id: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Fetch recent messages from a specific chat.

        Args:
            chat_id:  The chat ID (from list_chats).
            limit:    Maximum number of messages to return.

        Returns:
            List of message dicts with keys: id, sender, sender_email,
            sent_at, body_preview, body_content, message_type, importance.
        """
        params = {
            "$top": limit,
            "$select": "id,from,createdDateTime,body,messageType,importance,webUrl",
        }
        raw = self._client.get_paged(f"/me/chats/{chat_id}/messages", params=params)
        return [self._normalize_message(m) for m in raw]

    def send_chat_message(
        self,
        chat_id: str,
        content: str,
        content_type: str = "text",
    ) -> dict[str, Any]:
        """Send a message to a chat.

        Args:
            chat_id:       The chat ID (from list_chats).
            content:       Message body. Plain text by default.
            content_type:  "text" or "html".

        Returns:
            The sent message object.
        """
        payload = {
            "body": {
                "contentType": content_type,
                "content": content,
            }
        }
        raw = self._client.post(f"/me/chats/{chat_id}/messages", json=payload)
        return self._normalize_message(raw)

    def list_teams(self) -> list[dict[str, Any]]:
        """List all Teams the signed-in user is a member of.

        Returns:
            List of team dicts with keys: id, display_name, description,
            visibility, web_url.
        """
        params = {
            "$select": "id,displayName,description,visibility,webUrl",
        }
        raw = self._client.get_paged("/me/joinedTeams", params=params)
        return [
            {
                "id": t.get("id", ""),
                "display_name": t.get("displayName", ""),
                "description": t.get("description", ""),
                "visibility": t.get("visibility", ""),
                "web_url": t.get("webUrl", ""),
            }
            for t in raw
        ]

    def list_channels(self, team_id: str) -> list[dict[str, Any]]:
        """List all channels in a team.

        Args:
            team_id: The team ID (from list_teams).

        Returns:
            List of channel dicts with keys: id, display_name, description,
            membership_type, web_url.
        """
        params = {
            "$select": "id,displayName,description,membershipType,webUrl",
        }
        raw = self._client.get_paged(f"/teams/{team_id}/channels", params=params)
        return [
            {
                "id": c.get("id", ""),
                "display_name": c.get("displayName", ""),
                "description": c.get("description", ""),
                "membership_type": c.get("membershipType", ""),
                "web_url": c.get("webUrl", ""),
            }
            for c in raw
        ]

    def get_channel_messages(
        self,
        team_id: str,
        channel_id: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Fetch recent messages from a channel.

        Note: Requires ChannelMessage.Read.All (admin consent in most tenants).
        An empty list is returned with a warning if access is denied.

        Args:
            team_id:    The team ID.
            channel_id: The channel ID (from list_channels).
            limit:      Maximum number of messages to return.
        """
        try:
            params = {
                "$top": limit,
                "$select": "id,from,createdDateTime,body,messageType,importance,webUrl",
            }
            raw = self._client.get_paged(
                f"/teams/{team_id}/channels/{channel_id}/messages",
                params=params,
            )
            return [self._normalize_message(m) for m in raw]
        except Exception as exc:
            print(
                f"[graph_teams] Could not read channel messages: {exc}\n"
                "ChannelMessage.Read.All permission may require admin consent."
            )
            return []

    def send_channel_message(
        self,
        team_id: str,
        channel_id: str,
        content: str,
        content_type: str = "text",
    ) -> dict[str, Any]:
        """Post a message to a Teams channel.

        Args:
            team_id:       The team ID.
            channel_id:    The channel ID.
            content:       Message body.
            content_type:  "text" or "html".
        """
        payload = {
            "body": {
                "contentType": content_type,
                "content": content,
            }
        }
        raw = self._client.post(
            f"/teams/{team_id}/channels/{channel_id}/messages",
            json=payload,
        )
        return self._normalize_message(raw)

    @staticmethod
    def _normalize_chat(raw: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": raw.get("id", ""),
            "topic": raw.get("topic") or "(no topic)",
            "chat_type": raw.get("chatType", ""),
            "web_url": raw.get("webUrl", ""),
            "last_updated": raw.get("lastUpdatedDateTime", ""),
        }

    @staticmethod
    def _normalize_message(raw: dict[str, Any]) -> dict[str, Any]:
        sender_block = raw.get("from") or {}
        user_block = sender_block.get("user") or {}
        body = raw.get("body") or {}
        content = body.get("content", "")
        preview = content[:200].replace("\n", " ").strip() if content else ""

        return {
            "id": raw.get("id", ""),
            "sender": user_block.get("displayName", ""),
            "sender_email": user_block.get("email", ""),
            "sent_at": raw.get("createdDateTime", ""),
            "body_preview": preview,
            "body_content": content,
            "body_type": body.get("contentType", "text"),
            "message_type": raw.get("messageType", "message"),
            "importance": raw.get("importance", "normal"),
            "web_url": raw.get("webUrl", ""),
        }
