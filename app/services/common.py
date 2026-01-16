from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from ..audit import log_audit
from ..exceptions import PermissionDenied
from ..permissions import can


@dataclass(frozen=True)
class Actor:
    username: str
    role: str

    @classmethod
    def from_controller(cls, controller) -> "Actor":
        return cls(getattr(controller, "user", "") or "", getattr(controller, "role", "") or "")


def ensure_actor(actor_user: Actor | Dict[str, str] | None) -> Actor:
    if isinstance(actor_user, Actor):
        return actor_user
    if isinstance(actor_user, dict):
        return Actor(actor_user.get("username", ""), actor_user.get("role", ""))
    return Actor("", "")


def require_permission(
    actor_user: Actor | Dict[str, str] | None,
    permission_name: str,
    action: str | None = None,
    screen: str | None = None,
) -> Actor:
    actor = ensure_actor(actor_user)
    if can(actor.role, permission_name, at_least="edit"):
        return actor
    audit(
        "permission.denied",
        actor.username,
        {
            "permission": permission_name,
            "screen": screen or "",
            "action": action or "",
        },
        success=False,
    )
    raise PermissionDenied(f"{actor.username} lacks permission for {action or permission_name}")


def audit(
    action: str,
    user: str,
    details: Dict[str, Any] | str | None = None,
    *,
    success: bool = True,
) -> None:
    status = "SUCCESS" if success else "FAIL"
    details_str = ""
    if isinstance(details, dict):
        compact = ", ".join(f"{key}={value}" for key, value in details.items() if value is not None)
        details_str = f" | {compact}" if compact else ""
    elif isinstance(details, str) and details:
        details_str = f" | {details}"
    log_audit(user, f"{status} {action}{details_str}")
