import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlLiteDB import get_all_learning_entities

COLUMNS = ("id", "text", "category", "subcategory", "topic", "subtopic", "concept", "tags")
FILTER_FIELDS = ("category", "subcategory", "topic", "subtopic")
ALL = "All"


def _entity_values(entity):
    return (
        entity.id,
        entity.text,
        entity.category,
        entity.subcategory or "",
        entity.topic or "",
        entity.subtopic or "",
        entity.concept or "",
        ", ".join(entity.tags),
    )


def _search_blob(entity):
    return " ".join(str(value) for value in _entity_values(entity)).lower()


class EntityPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Learning Entities")
        self.geometry("1100x560")
        self.entities = []
        self.filter_vars = {}
        self.filter_boxes = {}
        self._updating_filters = False
        self._build()
        self.refresh()

    def _build(self):
        frame = ttk.Frame(self, padding=8)
        frame.pack(fill=tk.BOTH, expand=True)

        toolbar = ttk.Frame(frame)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        ttk.Label(toolbar, text="Search").pack(side=tk.LEFT, padx=(0, 8))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_var.trace_add("write", lambda *_args: self.apply_filter())

        ttk.Button(toolbar, text="Clear", command=self.clear_filters).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        ttk.Button(toolbar, text="Refresh", command=self.refresh).pack(
            side=tk.LEFT, padx=(8, 0)
        )

        filters = ttk.Frame(frame)
        filters.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        for field in FILTER_FIELDS:
            ttk.Label(filters, text=field.title()).pack(side=tk.LEFT, padx=(0, 4))
            var = tk.StringVar(value=ALL)
            box = ttk.Combobox(filters, textvariable=var, state="readonly", width=22)
            box.pack(side=tk.LEFT, padx=(0, 12))
            var.trace_add("write", lambda *_args, current=field: self._on_filter_change(current))
            self.filter_vars[field] = var
            self.filter_boxes[field] = box

        self.tree = ttk.Treeview(frame, columns=COLUMNS, show="headings")
        for col in COLUMNS:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=120, stretch=True)
        self.tree.column("id", width=50, stretch=False)
        self.tree.column("text", width=320)

        yscroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        xscroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        self.tree.grid(row=2, column=0, sticky="nsew")
        yscroll.grid(row=2, column=1, sticky="ns")
        xscroll.grid(row=3, column=0, sticky="ew")
        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(0, weight=1)

    def clear_filters(self):
        self._updating_filters = True
        self.search_var.set("")
        for var in self.filter_vars.values():
            var.set(ALL)
        self._updating_filters = False
        self._sync_filter_options()
        self.apply_filter()

    def refresh(self):
        self.entities = get_all_learning_entities()
        self._sync_filter_options()
        self.apply_filter()

    def _selected_filters(self, until=None):
        selected = {}
        for field in FILTER_FIELDS:
            if field == until:
                break
            value = self.filter_vars[field].get()
            if value and value != ALL:
                selected[field] = value
        return selected

    def _matching_entities(self, until=None):
        selected = self._selected_filters(until=until)
        return [
            entity
            for entity in self.entities
            if all(getattr(entity, field) == value for field, value in selected.items())
        ]

    def _sync_filter_options(self):
        self._updating_filters = True
        for field in FILTER_FIELDS:
            values = sorted(
                {
                    getattr(entity, field)
                    for entity in self._matching_entities(until=field)
                    if getattr(entity, field)
                }
            )
            self.filter_boxes[field]["values"] = (ALL, *values)
            if self.filter_vars[field].get() not in (ALL, *values):
                self.filter_vars[field].set(ALL)
        self._updating_filters = False

    def _on_filter_change(self, _field):
        if self._updating_filters:
            return
        self._sync_filter_options()
        self.apply_filter()

    def apply_filter(self):
        query = self.search_var.get().strip().lower()
        selected = self._selected_filters()
        self.tree.delete(*self.tree.get_children())
        for entity in self.entities:
            if any(getattr(entity, field) != value for field, value in selected.items()):
                continue
            if query and query not in _search_blob(entity):
                continue
            self.tree.insert("", tk.END, values=_entity_values(entity))


if __name__ == "__main__":
    EntityPage().mainloop()
