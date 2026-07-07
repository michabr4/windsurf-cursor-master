"""Microsoft Graph API — Calendar module.

Reads and creates calendar events using the signed-in user's calendar.

Required Azure app permissions (delegated):
    Calendars.Read          — list and read events
    Calendars.ReadWrite     — also create / update / delete events
    User.Read               — resolve the signed-in user

Usage:
    from src.graph_calendar import GraphCalendar

    cal = GraphCalendar()
    agenda = cal.get_today_agenda()
    for event in agenda:
        print(event["start"], event["subject"])
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from .graph_client import GraphClient

CALENDAR_SCOPES = ["Calendars.Read", "Calendars.ReadWrite", "User.Read"]


class GraphCalendar:
    """Read and write calendar events via Microsoft Graph.

    Args:
        client: Optional pre-built GraphClient. One is created automatically
                with CALENDAR_SCOPES if not provided.
    """

    def __init__(self, client: GraphClient | None = None) -> None:
        self._client = client or GraphClient(scopes=CALENDAR_SCOPES)

    def list_events(
        self,
        days_ahead: int = 7,
        days_behind: int = 0,
        max_results: int = 50,
        calendar_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """List calendar events within a time window.

        Args:
            days_ahead:   Include events up to this many days in the future.
            days_behind:  Include events starting this many days in the past.
            max_results:  Maximum number of events to return.
            calendar_id:  Specific calendar ID, or None for the default calendar.

        Returns:
            List of event dicts with keys: id, subject, start, end,
            location, organizer, is_all_day, web_link, body_preview.
        """
        now = datetime.now(timezone.utc)
        start_dt = (now - timedelta(days=days_behind)).strftime("%Y-%m-%dT%H:%M:%SZ")
        end_dt = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%dT%H:%M:%SZ")

        base = f"/me/calendars/{calendar_id}/calendarView" if calendar_id else "/me/calendarView"
        params = {
            "startDateTime": start_dt,
            "endDateTime": end_dt,
            "$top": max_results,
            "$orderby": "start/dateTime asc",
            "$select": (
                "id,subject,start,end,location,organizer,"
                "isAllDay,webLink,bodyPreview,importance,showAs"
            ),
        }

        raw = self._client.get_paged(base, params=params)
        return [self._normalize_event(e) for e in raw]

    def get_today_agenda(self) -> list[dict[str, Any]]:
        """Return all events happening today (midnight-to-midnight local UTC)."""
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        params = {
            "startDateTime": start_of_day.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "endDateTime": end_of_day.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "$top": 50,
            "$orderby": "start/dateTime asc",
            "$select": "id,subject,start,end,location,organizer,isAllDay,webLink,showAs,importance",
        }
        raw = self._client.get_paged("/me/calendarView", params=params)
        return [self._normalize_event(e) for e in raw]

    def get_upcoming(self, hours: int = 24) -> list[dict[str, Any]]:
        """Return events starting within the next N hours."""
        return self.list_events(days_ahead=hours // 24 + 1, days_behind=0, max_results=20)

    def list_calendars(self) -> list[dict[str, Any]]:
        """Return all calendars for the signed-in user."""
        raw = self._client.get_paged(
            "/me/calendars",
            params={"$select": "id,name,color,isDefaultCalendar,canEdit"},
        )
        return raw

    def create_event(
        self,
        subject: str,
        start: datetime,
        end: datetime,
        body: str = "",
        location: str = "",
        attendees: list[str] | None = None,
        is_online_meeting: bool = False,
        calendar_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a new calendar event.

        Args:
            subject:           Event title.
            start:             Start datetime (timezone-aware recommended).
            end:               End datetime.
            body:              Optional HTML or plain-text description.
            location:          Optional location string.
            attendees:         Optional list of email addresses to invite.
            is_online_meeting: If True, auto-generate a Teams meeting link.
            calendar_id:       Target calendar ID, or None for default.

        Returns:
            Created event as returned by the Graph API.
        """

        def _dt_str(dt: datetime) -> str:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%S")

        payload: dict[str, Any] = {
            "subject": subject,
            "start": {"dateTime": _dt_str(start), "timeZone": "UTC"},
            "end": {"dateTime": _dt_str(end), "timeZone": "UTC"},
            "isOnlineMeeting": is_online_meeting,
            "onlineMeetingProvider": "teamsForBusiness" if is_online_meeting else "unknown",
        }

        if body:
            payload["body"] = {"contentType": "HTML", "content": body}

        if location:
            payload["location"] = {"displayName": location}

        if attendees:
            payload["attendees"] = [
                {"emailAddress": {"address": addr}, "type": "required"}
                for addr in attendees
            ]

        path = f"/me/calendars/{calendar_id}/events" if calendar_id else "/me/events"
        raw = self._client.post(path, json=payload)
        return self._normalize_event(raw)

    def delete_event(self, event_id: str) -> None:
        """Delete a calendar event by its ID."""
        self._client.delete(f"/me/events/{event_id}")

    @staticmethod
    def _normalize_event(raw: dict[str, Any]) -> dict[str, Any]:
        """Flatten a Graph event object into a simpler dict."""
        start_raw = raw.get("start", {})
        end_raw = raw.get("end", {})

        organizer = (
            raw.get("organizer", {})
            .get("emailAddress", {})
        )

        return {
            "id": raw.get("id", ""),
            "subject": raw.get("subject", "(no subject)"),
            "start": start_raw.get("dateTime", ""),
            "start_timezone": start_raw.get("timeZone", "UTC"),
            "end": end_raw.get("dateTime", ""),
            "end_timezone": end_raw.get("timeZone", "UTC"),
            "is_all_day": raw.get("isAllDay", False),
            "location": raw.get("location", {}).get("displayName", ""),
            "organizer_name": organizer.get("name", ""),
            "organizer_email": organizer.get("address", ""),
            "importance": raw.get("importance", "normal"),
            "show_as": raw.get("showAs", "busy"),
            "body_preview": raw.get("bodyPreview", ""),
            "web_link": raw.get("webLink", ""),
            "online_meeting_url": raw.get("onlineMeeting", {}).get("joinUrl", ""),
        }
