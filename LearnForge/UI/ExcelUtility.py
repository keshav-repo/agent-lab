import tkinter as tk
from tkinter import ttk


class ExcelUtility(ttk.Frame):
    def __init__(self, master, on_back=None):
        super().__init__(master, padding=24)
        self.on_back = on_back
        self._build()

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

        ttk.Label(self, text="Excel Utility", style="Title.TLabel").pack(pady=(12, 6))
        ttk.Label(
            self,
            text="Choose an Excel action.",
            style="Subtitle.TLabel",
        ).pack(pady=(0, 28))

        actions = ttk.Frame(self)
        actions.pack()

        ttk.Button(
            actions,
            text="Download Learning Entity",
            command=self.download_learning_entity,
        ).pack(fill=tk.X, pady=8, ipadx=48)

        ttk.Button(
            actions,
            text="Update Metadata",
            style="Secondary.TButton",
            command=self.update_metadata,
        ).pack(fill=tk.X, pady=8, ipadx=48)

        self.status_label = ttk.Label(self, text="", style="Muted.TLabel")
        self.status_label.pack(pady=(28, 0))

    def download_learning_entity(self):
        self.status_label.config(text="Download Learning Entity — coming soon")

    def update_metadata(self):
        self.status_label.config(text="Update Metadata — coming soon")
