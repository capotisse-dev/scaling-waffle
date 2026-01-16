from __future__ import annotations

from typing import Dict, List, Optional

from .common import Actor, audit, require_permission
from .validation import validate_machine_history_entry
from ..db import (
    create_machine_document,
    add_machine_document_revision,
    get_next_machine_document_revision_number,
    list_machine_document_revisions,
    list_machine_documents,
    set_machine_document_active,
)


PERMISSION_KEY = "manage_documents"


def list_documents(line: str, machine: str, doc_type: Optional[str] = None, search: str = "") -> List[Dict]:
    return list_machine_documents(line, machine, doc_type=doc_type, search=search)


def list_revisions(document_id: int) -> List[Dict]:
    return list_machine_document_revisions(document_id)


def create_document(
    line: str,
    machine: str,
    doc_type: str,
    doc_name: str,
    *,
    actor_user: Actor | Dict[str, str] | None,
) -> int:
    actor = require_permission(actor_user, PERMISSION_KEY, "create_document", "Machine History")
    validate_machine_history_entry({
        "line": line,
        "machine": machine,
        "doc_type": doc_type,
        "doc_name": doc_name,
    })
    try:
        document_id = create_machine_document(line, machine, doc_type, doc_name, actor.username)
        audit(
            "machine_document.create",
            actor.username,
            {"doc_name": doc_name, "doc_type": doc_type},
            success=True,
        )
        return document_id
    except Exception as exc:
        audit(
            "machine_document.create",
            actor.username,
            {"doc_name": doc_name, "doc_type": doc_type, "error": str(exc)},
            success=False,
        )
        raise


def add_revision(
    document_id: int,
    stored_path: str,
    original_filename: str,
    file_hash: str,
    notes: str | None,
    *,
    actor_user: Actor | Dict[str, str] | None,
) -> int:
    actor = require_permission(actor_user, PERMISSION_KEY, "add_revision", "Machine History")
    try:
        revision_number = get_next_machine_document_revision_number(document_id)
        add_machine_document_revision(
            document_id=document_id,
            revision_number=revision_number,
            stored_path=stored_path,
            original_filename=original_filename,
            file_hash=file_hash,
            created_by=actor.username,
            notes=notes,
        )
        audit(
            "machine_document.revision.add",
            actor.username,
            {"document_id": document_id, "revision": revision_number},
            success=True,
        )
        return revision_number
    except Exception as exc:
        audit(
            "machine_document.revision.add",
            actor.username,
            {"document_id": document_id, "error": str(exc)},
            success=False,
        )
        raise


def update_document_active(document_id: int, is_active: bool, *, actor_user: Actor | Dict[str, str] | None) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "update_document_active", "Machine History")
    try:
        set_machine_document_active(document_id, is_active)
        audit(
            "machine_document.update",
            actor.username,
            {"document_id": document_id, "active": int(is_active)},
            success=True,
        )
    except Exception as exc:
        audit(
            "machine_document.update",
            actor.username,
            {"document_id": document_id, "active": int(is_active), "error": str(exc)},
            success=False,
        )
        raise


def get_document(document_id: int) -> Optional[Dict]:
    revisions = list_machine_document_revisions(document_id)
    return revisions[0] if revisions else None
