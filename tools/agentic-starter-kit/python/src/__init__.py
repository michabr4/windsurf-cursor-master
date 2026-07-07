"""Starter Python API clients for the template repo."""

from .graph_client import GraphClient
from .graph_calendar import GraphCalendar, CALENDAR_SCOPES
from .graph_teams import GraphTeams, TEAMS_SCOPES
from .graph_files import GraphFiles, FILES_SCOPES

__all__ = [
    "GraphClient",
    "GraphCalendar",
    "CALENDAR_SCOPES",
    "GraphTeams",
    "TEAMS_SCOPES",
    "GraphFiles",
    "FILES_SCOPES",
]