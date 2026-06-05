"""Optional capabilities ported from consolidated email projects."""

from __future__ import annotations

__all__ = ["offline_mail_digest"]

try:
    from . import offline_mail_digest
except ImportError:
    offline_mail_digest = None  # type: ignore[misc, assignment]
