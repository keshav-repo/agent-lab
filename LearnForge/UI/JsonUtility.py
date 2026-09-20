import tkinter as tk
from tkinter import filedialog, ttk

from KnowledgeService import UploadFiles, UploadLearningItems


class JsonUtility(ttk.Frame):
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

        ttk.Label(self, text="JSON Utility", style="Title.TLabel").pack(pady=(12, 6))
        ttk.Label(
            self,
            text="Choose a JSON action.",
            style="Subtitle.TLabel",
        ).pack(pady=(0, 28))

        actions = ttk.Frame(self)
        actions.pack()

        ttk.Button(
            actions,
            text="Single Json Upload",
            command=self.single_json_upload,
        ).pack(fill=tk.X, pady=8, ipadx=48)

        ttk.Button(
            actions,
            text="Multiple Json Upload",
            style="Secondary.TButton",
            command=self.multiple_json_upload,
        ).pack(fill=tk.X, pady=8, ipadx=48)

        ttk.Button(
            actions,
            text="process File",
            style="Secondary.TButton",
            command=self.process_file,
        ).pack(fill=tk.X, pady=8, ipadx=48)

        self.status_label = ttk.Label(self, text="", style="Muted.TLabel")
        self.status_label.pack(pady=(28, 0))

    def single_json_upload(self):
        file_path = filedialog.askopenfilename(
            title="Select JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not file_path:
            self.status_label.config(text="No file selected.")
            return

        UploadFiles([file_path])
        self.status_label.config(text="File uploaded successfully.")

    def multiple_json_upload(self):
        self.status_label.config(text="Multiple Json Upload — coming soon")

    def process_file(self):
        UploadLearningItems()
        self.status_label.config(text="Files processed successfully.")
