import threading
import tkinter as tk
from tkinter import filedialog, ttk

from KnowledgeService import UploadLearningItems
from fs_utils import UploadFiles


class JsonUtility(ttk.Frame):
    def __init__(self, master, on_back=None):
        super().__init__(master, padding=24)
        self.on_back = on_back
        self._processing_thread = None
        self._processing_error = None
        self._build()

    def _build(self):
        header = ttk.Frame(self)
        header.pack(fill=tk.X, pady=(0, 24))
        if self.on_back:
            self.back_button = ttk.Button(
                header,
                text="← Back",
                style="Back.TButton",
                command=self.on_back,
            )
            self.back_button.pack(side=tk.LEFT)
        else:
            self.back_button = None

        ttk.Label(self, text="JSON Utility", style="Title.TLabel").pack(pady=(12, 6))
        ttk.Label(
            self,
            text="Choose a JSON action.",
            style="Subtitle.TLabel",
        ).pack(pady=(0, 28))

        actions = ttk.Frame(self)
        actions.pack()

        self.single_upload_button = ttk.Button(
            actions,
            text="Single Json Upload",
            command=self.single_json_upload,
        )
        self.single_upload_button.pack(fill=tk.X, pady=8, ipadx=48)

        self.process_button = ttk.Button(
            actions,
            text="process File",
            style="Secondary.TButton",
            command=self.process_file,
        )
        self.process_button.pack(fill=tk.X, pady=8, ipadx=48)

        self.loader = ttk.Progressbar(self, mode="indeterminate", length=260)

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

    def process_file(self):
        if self._processing_thread and self._processing_thread.is_alive():
            return

        self._set_processing_state(True)
        self.status_label.config(text="Processing files...")
        self._processing_error = None
        self._processing_thread = threading.Thread(
            target=self._run_upload_learning_items,
            daemon=True,
        )
        self._processing_thread.start()
        self.after(100, self._poll_processing)

    def _run_upload_learning_items(self):
        try:
            UploadLearningItems()
        except Exception as exc:
            self._processing_error = exc

    def _poll_processing(self):
        if self._processing_thread and self._processing_thread.is_alive():
            self.after(100, self._poll_processing)
            return

        self._set_processing_state(False)
        if self._processing_error is not None:
            self.status_label.config(text=f"Processing failed: {self._processing_error}")
            return

        self.status_label.config(text="Files processed successfully.")

    def _set_processing_state(self, is_processing: bool):
        button_state = tk.DISABLED if is_processing else tk.NORMAL
        self.single_upload_button.config(state=button_state)
        self.process_button.config(state=button_state)
        if self.back_button is not None:
            self.back_button.config(state=button_state)

        if is_processing:
            self.loader.pack(pady=(16, 0))
            self.loader.start(10)
        else:
            self.loader.stop()
            self.loader.pack_forget()
