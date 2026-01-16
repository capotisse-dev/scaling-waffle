from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .common import Actor, audit, require_permission
from .validation import validate_print_revision
from ..config import DATA_DIR
from ..db import (
    add_print_file,
    deactivate_print_revisions,
    get_active_print,
    list_print_revisions,
)


PERMISSION_KEY = "manage_documents"


def _safe_folder_name(value: str) -> str:
    return "".join([c if c.isalnum() or c in ("-", "_") else "_" for c in value.strip()]) or "document"


def _hash_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _store_file(source_path: str, scope: str, filename: str, revision: int) -> str:
    ext = Path(source_path).suffix
    target_dir = Path(DATA_DIR) / "storage" / "prints" / _safe_folder_name(scope) / _safe_folder_name(filename)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"rev_{revision}{ext}"
    target_path.write_bytes(Path(source_path).read_bytes())
    return str(target_path.relative_to(DATA_DIR))


def create_print_file(
    *,
    source_path: str,
    filename: str,
    scope_type: str,
    machine_id: Optional[int],
    actor_user: Actor | Dict[str, str] | None,
) -> Tuple[str, Optional[int]]:
    actor = require_permission(actor_user, PERMISSION_KEY, "add_print_file", "Machine History")
    validate_print_revision({"filename": filename, "scope_type": scope_type})

    try:
        file_hash = _hash_file(source_path)
        revisions = list_print_revisions(scope_type, filename, machine_id)
        for rev in revisions:
            if rev.get("file_hash") == file_hash:
                audit(
                    "print_file.create",
                    actor.username,
                    {"filename": filename, "scope": scope_type, "status": "DUPLICATE"},
                    success=True,
                )
                return "DUPLICATE", None

        next_revision = (revisions[0]["revision"] + 1) if revisions else 1
        deactivate_print_revisions(scope_type, filename, machine_id)
        stored_path = _store_file(source_path, scope_type, filename, next_revision)
        parent_id = revisions[0]["id"] if revisions else None
        new_id = add_print_file(
            scope_type=scope_type,
            machine_id=machine_id,
            filename=filename,
            file_path=stored_path,
            file_hash=file_hash,
            revision=next_revision,
            parent_id=parent_id,
            created_by=actor.username,
            is_active=1,
        )
        audit(
            "print_file.create",
            actor.username,
            {"filename": filename, "scope": scope_type, "revision": next_revision},
            success=True,
        )
        return "CREATED", new_id
    except Exception as exc:
        audit(
            "print_file.create",
            actor.username,
            {"filename": filename, "scope": scope_type, "error": str(exc)},
            success=False,
        )
        raise


def list_print_revisions_service(
    scope_type: str,
    filename: str,
    machine_id: Optional[int],
) -> List[Dict]:
    return list_print_revisions(scope_type, filename, machine_id)


def get_active_print_service(
    scope_type: str,
    filename: str,
    machine_id: Optional[int],
) -> Optional[Dict]:
    return get_active_print(scope_type, filename, machine_id)


def rollback_print_revision(
    *,
    scope_type: str,
    filename: str,
    machine_id: Optional[int],
    target_revision_id: int,
    actor_user: Actor | Dict[str, str] | None,
) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "rollback_print_revision", "Machine History")
    try:
        deactivate_print_revisions(scope_type, filename, machine_id)
        from ..db import activate_print_revision

        activate_print_revision(target_revision_id)
        audit(
            "print_file.rollback",
            actor.username,
            {"filename": filename, "target_revision_id": target_revision_id},
            success=True,
        )
    except Exception as exc:
        audit(
            "print_file.rollback",
            actor.username,
            {"filename": filename, "target_revision_id": target_revision_id, "error": str(exc)},
            success=False,
        )
        raise


def update_print_file(*args, **kwargs) -> None:
    return None


def get_print_file(*args, **kwargs) -> Optional[Dict]:
    return None
