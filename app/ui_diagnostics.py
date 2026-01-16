from __future__ import annotations

from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from .config import APP_INFO, BACKUPS_DIR
from .db import get_meta


def _latest_backup_info() -> str:
    backup_dir = Path(BACKUPS_DIR)
    if not backup_dir.exists():
        return "None"
    backups = list(backup_dir.glob("backup_*.db"))
    if not backups:
        return "None"
    latest = max(backups, key=lambda p: p.stat().st_mtime)
    timestamp = datetime.fromtimestamp(latest.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    return f"{latest.name} ({timestamp})"


def _diagnostics_text() -> str:
    schema_version = get_meta("schema_version") or "unknown"
    last_backup = _latest_backup_info()
    lines = [
        f"App Version: {APP_INFO.version}",
        f"Data Directory: {APP_INFO.data_dir}",
        f"Database Path: {APP_INFO.db_path}",
        f"Logs Directory: {APP_INFO.logs_dir}",
        f"DB Schema Version: {schema_version}",
        f"Last Backup: {last_backup}",
    ]
    return "\n".join(lines)


def show_diagnostics(parent, controller) -> None:
    dialog = tk.Toplevel(parent)
    dialog.title("Diagnostics")
    dialog.geometry("520x320")
    dialog.configure(bg=controller.colors["bg"])

    header = tk.Label(
        dialog,
        text="Diagnostics",
        bg=controller.colors["bg"],
        fg=controller.colors["fg"],
        font=("Arial", 14, "bold"),
    )
    header.pack(anchor="w", padx=12, pady=(12, 6))

    text_frame = tk.Frame(dialog, bg=controller.colors["bg"])
    text_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    text = tk.Text(text_frame, height=10, wrap="word")
    text.insert("1.0", _diagnostics_text())
    text.configure(state="disabled")
    text.pack(fill="both", expand=True)

    button_frame = tk.Frame(dialog, bg=controller.colors["bg"])
    button_frame.pack(fill="x", padx=12, pady=(0, 12))

    def copy_to_clipboard():
        try:
            dialog.clipboard_clear()
            dialog.clipboard_append(_diagnostics_text())
            dialog.update()
            messagebox.showinfo("Copied", "Diagnostics copied to clipboard.")
        except Exception as exc:
            messagebox.showerror("Copy Failed", f"Unable to copy diagnostics.\n{exc}")

    ttk.Button(button_frame, text="Copy to Clipboard", command=copy_to_clipboard).pack(side="right")

    dialog.transient(parent)
    dialog.grab_set()
