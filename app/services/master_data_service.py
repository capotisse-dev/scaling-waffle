from __future__ import annotations

import shutil
from typing import Any, Dict, List

from .common import Actor, audit, require_permission
from ..config import DB_PATH
from ..db import (
    add_line,
    add_machine_to_line,
    deactivate_downtime_code,
    deactivate_part,
    deactivate_tool,
    delete_machine_from_line,
    get_scrap_costs_simple,
    get_tool_lines,
    get_tool_parts,
    list_cells_for_line,
    list_downtime_codes,
    list_lines,
    list_machines_for_line,
    list_parts_for_line,
    list_parts_with_lines,
    list_production_goals,
    list_tool_inserts,
    list_tools_for_line,
    list_tools_simple,
    replace_tool_inserts,
    set_scrap_cost,
    set_tool_lines,
    set_tool_parts,
    upsert_downtime_code,
    upsert_part,
    upsert_production_goal,
    upsert_tool_inventory,
)


PERMISSION_KEY = "manage_tools"
EXPORT_PERMISSION_KEY = "export"


def list_tools_simple_service() -> List[Dict[str, Any]]:
    return list_tools_simple()


def list_tools_for_line_service(line: str, include_unassigned: bool = True) -> List[str]:
    return list_tools_for_line(line, include_unassigned=include_unassigned)


def list_lines_service() -> List[str]:
    return list_lines()


def get_tool_lines_service(tool_num: str) -> List[str]:
    return get_tool_lines(tool_num)


def set_tool_lines_service(tool_num: str, lines: List[str], *, actor_user: Actor | Dict[str, str] | None) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "set_tool_lines", "Master Data")
    try:
        set_tool_lines(tool_num, lines)
        audit(
            "tool.lines.set",
            actor.username,
            {"tool_num": tool_num, "lines": ",".join(lines)},
            success=True,
        )
    except Exception as exc:
        audit(
            "tool.lines.set",
            actor.username,
            {"tool_num": tool_num, "error": str(exc)},
            success=False,
        )
        raise


def list_tool_inserts_service(tool_num: str) -> List[Dict[str, Any]]:
    return list_tool_inserts(tool_num)


def replace_tool_inserts_service(
    tool_num: str,
    inserts: List[Dict[str, Any]],
    *,
    actor_user: Actor | Dict[str, str] | None,
) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "replace_tool_inserts", "Master Data")
    try:
        replace_tool_inserts(tool_num, inserts)
        audit(
            "tool.inserts.replace",
            actor.username,
            {"tool_num": tool_num, "insert_count": len(inserts)},
            success=True,
        )
    except Exception as exc:
        audit(
            "tool.inserts.replace",
            actor.username,
            {"tool_num": tool_num, "error": str(exc)},
            success=False,
        )
        raise


def get_tool_parts_service(tool_num: str) -> List[str]:
    return get_tool_parts(tool_num)


def set_tool_parts_service(tool_num: str, parts: List[str], *, actor_user: Actor | Dict[str, str] | None) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "set_tool_parts", "Master Data")
    try:
        set_tool_parts(tool_num, parts)
        audit(
            "tool.parts.set",
            actor.username,
            {"tool_num": tool_num, "parts": ",".join(parts)},
            success=True,
        )
    except Exception as exc:
        audit(
            "tool.parts.set",
            actor.username,
            {"tool_num": tool_num, "error": str(exc)},
            success=False,
        )
        raise


def list_parts_with_lines_service() -> List[Dict[str, Any]]:
    return list_parts_with_lines()


def upsert_part_service(
    part_number: str,
    *,
    name: str,
    lines: List[str],
    actor_user: Actor | Dict[str, str] | None,
) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "upsert_part", "Master Data")
    try:
        upsert_part(part_number, name=name, lines=lines)
        audit(
            "part.upsert",
            actor.username,
            {"part_number": part_number, "lines": ",".join(lines)},
            success=True,
        )
    except Exception as exc:
        audit(
            "part.upsert",
            actor.username,
            {"part_number": part_number, "error": str(exc)},
            success=False,
        )
        raise


def deactivate_part_service(part_number: str, *, deleted_by: str, actor_user: Actor | Dict[str, str] | None) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "deactivate_part", "Master Data")
    try:
        deactivate_part(part_number, deleted_by=deleted_by)
        audit(
            "part.deactivate",
            actor.username,
            {"part_number": part_number},
            success=True,
        )
    except Exception as exc:
        audit(
            "part.deactivate",
            actor.username,
            {"part_number": part_number, "error": str(exc)},
            success=False,
        )
        raise


def set_scrap_cost_service(part_number: str, cost: float, *, actor_user: Actor | Dict[str, str] | None) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "set_scrap_cost", "Master Data")
    try:
        set_scrap_cost(part_number, cost)
        audit(
            "scrap_cost.set",
            actor.username,
            {"part_number": part_number, "cost": cost},
            success=True,
        )
    except Exception as exc:
        audit(
            "scrap_cost.set",
            actor.username,
            {"part_number": part_number, "error": str(exc)},
            success=False,
        )
        raise


def get_scrap_costs_simple_service() -> Dict[str, float]:
    return get_scrap_costs_simple()


def list_downtime_codes_service(active_only: bool = True) -> List[Dict[str, Any]]:
    return list_downtime_codes(active_only=active_only)


def upsert_downtime_code_service(
    code: str,
    description: str,
    *,
    actor_user: Actor | Dict[str, str] | None,
) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "upsert_downtime_code", "Master Data")
    try:
        upsert_downtime_code(code, description)
        audit(
            "downtime_code.upsert",
            actor.username,
            {"code": code},
            success=True,
        )
    except Exception as exc:
        audit(
            "downtime_code.upsert",
            actor.username,
            {"code": code, "error": str(exc)},
            success=False,
        )
        raise


def deactivate_downtime_code_service(code: str, *, deleted_by: str, actor_user: Actor | Dict[str, str] | None) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "deactivate_downtime_code", "Master Data")
    try:
        deactivate_downtime_code(code, deleted_by=deleted_by)
        audit(
            "downtime_code.deactivate",
            actor.username,
            {"code": code},
            success=True,
        )
    except Exception as exc:
        audit(
            "downtime_code.deactivate",
            actor.username,
            {"code": code, "error": str(exc)},
            success=False,
        )
        raise


def list_production_goals_service() -> List[Dict[str, Any]]:
    return list_production_goals()


def upsert_production_goal_service(
    *,
    line: str,
    cell: str,
    machine: str,
    part_number: str,
    target: float,
    actor_user: Actor | Dict[str, str] | None,
) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "upsert_production_goal", "Master Data")
    try:
        upsert_production_goal(line, cell, machine, part_number, target)
        audit(
            "production_goal.upsert",
            actor.username,
            {"line": line, "cell": cell, "machine": machine, "part_number": part_number},
            success=True,
        )
    except Exception as exc:
        audit(
            "production_goal.upsert",
            actor.username,
            {"line": line, "cell": cell, "machine": machine, "part_number": part_number, "error": str(exc)},
            success=False,
        )
        raise


def list_cells_for_line_service(line: str) -> List[str]:
    return list_cells_for_line(line)


def list_machines_for_line_service(line: str) -> List[str]:
    return list_machines_for_line(line)


def list_parts_for_line_service(line: str) -> List[str]:
    return list_parts_for_line(line)


def add_line_service(line: str, *, actor_user: Actor | Dict[str, str] | None) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "add_line", "Master Data")
    try:
        add_line(line)
        audit(
            "line.add",
            actor.username,
            {"line": line},
            success=True,
        )
    except Exception as exc:
        audit(
            "line.add",
            actor.username,
            {"line": line, "error": str(exc)},
            success=False,
        )
        raise


def add_machine_to_line_service(
    line: str,
    machine: str,
    *,
    actor_user: Actor | Dict[str, str] | None,
) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "add_machine_to_line", "Master Data")
    try:
        add_machine_to_line(line, machine)
        audit(
            "machine.add",
            actor.username,
            {"line": line, "machine": machine},
            success=True,
        )
    except Exception as exc:
        audit(
            "machine.add",
            actor.username,
            {"line": line, "machine": machine, "error": str(exc)},
            success=False,
        )
        raise


def delete_machine_from_line_service(
    line: str,
    machine: str,
    *,
    deleted_by: str,
    actor_user: Actor | Dict[str, str] | None,
) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "delete_machine_from_line", "Master Data")
    try:
        delete_machine_from_line(line, machine, deleted_by=deleted_by)
        audit(
            "machine.delete",
            actor.username,
            {"line": line, "machine": machine},
            success=True,
        )
    except Exception as exc:
        audit(
            "machine.delete",
            actor.username,
            {"line": line, "machine": machine, "error": str(exc)},
            success=False,
        )
        raise


def upsert_tool_inventory_service(
    *,
    tool_num: str,
    name: str,
    unit_cost: float,
    stock_qty: int,
    inserts_per_tool: int,
    actor_user: Actor | Dict[str, str] | None,
) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "upsert_tool_inventory", "Master Data")
    try:
        upsert_tool_inventory(
            tool_num=tool_num,
            name=name,
            unit_cost=unit_cost,
            stock_qty=stock_qty,
            inserts_per_tool=inserts_per_tool,
        )
        audit(
            "tool.upsert",
            actor.username,
            {"tool_num": tool_num},
            success=True,
        )
    except Exception as exc:
        audit(
            "tool.upsert",
            actor.username,
            {"tool_num": tool_num, "error": str(exc)},
            success=False,
        )
        raise


def deactivate_tool_service(tool_num: str, *, deleted_by: str, actor_user: Actor | Dict[str, str] | None) -> None:
    actor = require_permission(actor_user, PERMISSION_KEY, "deactivate_tool", "Master Data")
    try:
        deactivate_tool(tool_num, deleted_by=deleted_by)
        audit(
            "tool.deactivate",
            actor.username,
            {"tool_num": tool_num},
            success=True,
        )
    except Exception as exc:
        audit(
            "tool.deactivate",
            actor.username,
            {"tool_num": tool_num, "error": str(exc)},
            success=False,
        )
        raise


def export_database(path: str, *, actor_user: Actor | Dict[str, str] | None) -> None:
    actor = require_permission(actor_user, EXPORT_PERMISSION_KEY, "export_database", "Master Data")
    try:
        shutil.copyfile(DB_PATH, path)
        audit(
            "database.export",
            actor.username,
            {"path": path},
            success=True,
        )
    except Exception as exc:
        audit(
            "database.export",
            actor.username,
            {"path": path, "error": str(exc)},
            success=False,
        )
        raise


def import_database(path: str, *, actor_user: Actor | Dict[str, str] | None) -> None:
    actor = require_permission(actor_user, EXPORT_PERMISSION_KEY, "import_database", "Master Data")
    try:
        shutil.copyfile(path, DB_PATH)
        audit(
            "database.import",
            actor.username,
            {"path": path},
            success=True,
        )
    except Exception as exc:
        audit(
            "database.import",
            actor.username,
            {"path": path, "error": str(exc)},
            success=False,
        )
        raise
