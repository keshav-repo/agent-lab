import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlLiteDB import get_all_learning_entities

COLUMNS = ("id", "text", "category", "subcategory", "topic", "subtopic", "concept", "tags")


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
        self.geometry("1100x500")
        self.entities = []
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

        ttk.Button(toolbar, text="Clear", command=self.clear_search).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        ttk.Button(toolbar, text="Refresh", command=self.refresh).pack(
            side=tk.LEFT, padx=(8, 0)
        )

        self.tree = ttk.Treeview(frame, columns=COLUMNS, show="headings")
        for col in COLUMNS:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=120, stretch=True)
        self.tree.column("id", width=50, stretch=False)
        self.tree.column("text", width=320)

        yscroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        xscroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        self.tree.grid(row=1, column=0, sticky="nsew")
        yscroll.grid(row=1, column=1, sticky="ns")
        xscroll.grid(row=2, column=0, sticky="ew")
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

    def clear_search(self):
        self.search_var.set("")

    def refresh(self):
        self.entities = get_all_learning_entities()
        self.apply_filter()

    def apply_filter(self):
        query = self.search_var.get().strip().lower()
        self.tree.delete(*self.tree.get_children())
        for entity in self.entities:
            if query and query not in _search_blob(entity):
                continue
            self.tree.insert("", tk.END, values=_entity_values(entity))


if __name__ == "__main__":
    EntityPage().mainloop()
