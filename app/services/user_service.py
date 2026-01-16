from __future__ import annotations

from typing import Any, Dict, List, Optional

from .common import Actor, audit, require_permission
from ..db import (
    delete_screen_permission,
    get_user,
    list_screen_permissions,
    list_users,
    set_screen_permission,
    upsert_user,
    update_user_fields,
)


PERMISSION_KEY = "manage_users"


def create_user(
    *,
    username: str,
    password: str,
    role: str,
    name: str,
    line: str,
    actor_user: Actor | Dict[str, str] | None,
) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "create_user", "Admin")
    try:
        upsert_user(
            username=username,
            password=password,
            role=role,
            name=name,
            line=line,
            is_active=1,
            created_by=actor.username,
            updated_by=actor.username,
        )
        audit(
            "user.create",
            actor.username,
            {"username": username, "role": role},
            success=True,
        )
    except Exception as exc:
        audit(
            "user.create",
            actor.username,
            {"username": username, "role": role, "error": str(exc)},
            success=False,
        )
        raise


def update_user(
    username: str,
    fields: Dict[str, Any],
    *,
    actor_user: Actor | Dict[str, str] | None,
) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "update_user", "Admin")
    fields = dict(fields)
    fields["updated_by"] = actor.username
    try:
        update_user_fields(username, fields)
        audit(
            "user.update",
            actor.username,
            {"username": username},
            success=True,
        )
    except Exception as exc:
        audit(
            "user.update",
            actor.username,
            {"username": username, "error": str(exc)},
            success=False,
        )
        raise


def list_user_accounts() -> List[Dict[str, Any]]:
    return list_users()


def get_user_account(username: str) -> Optional[Dict[str, Any]]:
    return get_user(username)


def list_permissions(username: Optional[str] = None) -> List[Dict[str, Any]]:
    return list_screen_permissions(username)


def set_permission(
    username: str,
    screen: str,
    level: str,
    *,
    actor_user: Actor | Dict[str, str] | None,
) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "set_permission", "Admin")
    try:
        set_screen_permission(username, screen, level)
        audit(
            "permission.set",
            actor.username,
            {"username": username, "screen": screen, "level": level},
            success=True,
        )
    except Exception as exc:
        audit(
            "permission.set",
            actor.username,
            {"username": username, "screen": screen, "level": level, "error": str(exc)},
            success=False,
        )
        raise


def delete_permission(
    username: str,
    screen: str,
    *,
    actor_user: Actor | Dict[str, str] | None,
) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "delete_permission", "Admin")
    try:
        delete_screen_permission(username, screen)
        audit(
            "permission.delete",
            actor.username,
            {"username": username, "screen": screen},
            success=True,
        )
    except Exception as exc:
        audit(
            "permission.delete",
            actor.username,
            {"username": username, "screen": screen, "error": str(exc)},
            success=False,
        )
        raise
