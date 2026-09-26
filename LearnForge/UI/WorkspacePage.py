import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from WorkspaceManager import (
    add_workspace,
    get_active_workspace,
    get_workspaces,
    set_active_workspace,
)


class WorkspacePage(ttk.Frame):
    def __init__(self, master, on_back=None, on_workspace_changed=None):
        super().__init__(master, padding=24)
        self.on_back = on_back
        self.on_workspace_changed = on_workspace_changed
        self._build()
        self.refresh()

    def _build(self):
        header = ttk.Frame(self)
        header.pack(fill=tk.X, pady=(0, 24))
        if self.on_back:
            ttk.Button(
                header,
                text="← Back",
                style="Back.TButton",
                command=self.on_back,
            ).pack(side=tk.LEFT)

        ttk.Label(self, text="Workspace", style="Title.TLabel").pack(pady=(12, 6))
        ttk.Label(
            self,
            text="Create and switch between knowledge-base workspaces.",
            style="Subtitle.TLabel",
        ).pack(pady=(0, 28))

        form = ttk.Frame(self)
        form.pack(fill=tk.X)

        ttk.Label(form, text="Active workspace", style="Heading.TLabel").pack(anchor="w")
        self.active_label = ttk.Label(form, text="", style="Subtitle.TLabel")
        self.active_label.pack(anchor="w", pady=(4, 24))

        ttk.Label(form, text="Switch workspace", style="Heading.TLabel").pack(anchor="w")
        switch_row = ttk.Frame(form)
        switch_row.pack(fill=tk.X, pady=(8, 24))
        self.switch_var = tk.StringVar()
        self.switch_box = ttk.Combobox(
            switch_row,
            textvariable=self.switch_var,
            state="readonly",
            width=32,
        )
        self.switch_box.pack(side=tk.LEFT, padx=(0, 12))
        ttk.Button(
            switch_row,
            text="Submit",
            command=self.on_switch_workspace,
        ).pack(side=tk.LEFT)

        ttk.Label(form, text="Create new workspace", style="Heading.TLabel").pack(anchor="w")
        create_row = ttk.Frame(form)
        create_row.pack(fill=tk.X, pady=(8, 16))
        self.create_var = tk.StringVar()
        ttk.Entry(
            create_row,
            textvariable=self.create_var,
            width=34,
        ).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Button(
            create_row,
            text="Submit",
            command=self.on_create_workspace,
        ).pack(side=tk.LEFT)

        self.status_label = ttk.Label(form, text="", style="Muted.TLabel")
        self.status_label.pack(anchor="w", pady=(8, 0))

    def refresh(self):
        workspaces = get_workspaces()
        names = [workspace["name"] for workspace in workspaces]
        active = get_active_workspace()
        active_name = active.get("name", "")
        self.active_label.config(text=f"{active_name}  ({active.get('path', '')})")
        self.switch_box["values"] = names
        if active_name:
            self.switch_var.set(active_name)

    def on_switch_workspace(self):
        name = self.switch_var.get().strip()
        if not name:
            self.status_label.config(text="Select a workspace to switch.")
            return
        try:
            workspace = set_active_workspace(name)
        except Exception as error:
            self.status_label.config(text=str(error))
            return
        self.refresh()
        self.status_label.config(text=f"Switched to '{workspace['name']}'.")
        if self.on_workspace_changed:
            self.on_workspace_changed()

    def on_create_workspace(self):
        name = self.create_var.get().strip()
        if not name:
            self.status_label.config(text="Enter a workspace name.")
            return
        try:
            workspace = add_workspace(name)
        except Exception as error:
            self.status_label.config(text=str(error))
            return
        self.create_var.set("")
        self.refresh()
        self.status_label.config(text=f"Created workspace '{workspace['name']}'.")
        if self.on_workspace_changed:
            self.on_workspace_changed()
