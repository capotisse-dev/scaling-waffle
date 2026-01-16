from __future__ import annotations

from typing import Any, Dict, List, Optional

from .common import Actor, audit, require_permission
from ..db import fetch_tool_entries, upsert_tool_entry


PERMISSION_KEY = "manage_quality"


def list_quality_entries() -> List[Dict[str, Any]]:
    return fetch_tool_entries()


def get_quality_entry(entry_id: str) -> Optional[Dict[str, Any]]:
    for row in fetch_tool_entries():
        if row.get("id") == entry_id:
            return row
    return None


def update_quality_entry(
    entry: Dict[str, Any],
    *,
    actor_user: Actor | Dict[str, str] | None,
) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "update_quality_entry", "Quality")
    try:
        upsert_tool_entry(entry)
        audit(
            "quality.update",
            actor.username,
            {"entry_id": entry.get("ID")},
            success=True,
        )
    except Exception as exc:
        audit(
            "quality.update",
            actor.username,
            {"entry_id": entry.get("ID"), "error": str(exc)},
            success=False,
        )
        raise


def create_quality_entry(
    entry: Dict[str, Any],
    *,
    actor_user: Actor | Dict[str, str] | None,
) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "create_quality_entry", "Quality")
    try:
        upsert_tool_entry(entry)
        audit(
            "quality.create",
            actor.username,
            {"entry_id": entry.get("ID")},
            success=True,
        )
    except Exception as exc:
        audit(
            "quality.create",
            actor.username,
            {"entry_id": entry.get("ID"), "error": str(exc)},
            success=False,
        )
        raise
