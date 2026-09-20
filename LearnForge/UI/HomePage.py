import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from EntityPage import EntityPage
from theme import BG, apply_theme


class HomePage(tk.Tk):
    def __init__(self):
        super().__init__()
        apply_theme(self)
        self.title("Learning")
        self.minsize(720, 480)
        self.geometry("780x520")
        self.entity_page = None
        self._build_home()
        self.show_home()

    def _build_home(self):
        self.home_frame = ttk.Frame(self, padding=48)

        ttk.Label(self.home_frame, text="LearnForge", style="Title.TLabel").pack(
            pady=(40, 6)
        )
        ttk.Label(
            self.home_frame,
            text="Welcome. Browse your learning knowledge base.",
            style="Subtitle.TLabel",
        ).pack(pady=(0, 36))

        actions = ttk.Frame(self.home_frame)
        actions.pack()

        ttk.Button(
            actions,
            text="Learning Entity",
            command=self.show_entities,
        ).pack(fill=tk.X, pady=8, ipadx=48)

        ttk.Button(
            actions,
            text="Download Excel",
            style="Secondary.TButton",
            command=self.download_excel,
        ).pack(fill=tk.X, pady=8, ipadx=48)

        self.todo_label = ttk.Label(self.home_frame, text="", style="Muted.TLabel")
        self.todo_label.pack(pady=(28, 0))

    def show_home(self):
        if self.entity_page is not None:
            self.entity_page.pack_forget()
        self.geometry("780x520")
        self.title("LearnForge")
        self.configure(bg=BG)
        self.home_frame.pack(fill=tk.BOTH, expand=True)

    def show_entities(self):
        self.home_frame.pack_forget()
        self.geometry("1180x640")
        self.title("Learning Entities")
        if self.entity_page is None:
            self.entity_page = EntityPage(self, on_back=self.show_home)
        self.entity_page.pack(fill=tk.BOTH, expand=True)
        self.entity_page.refresh()

    def download_excel(self):
        self.todo_label.config(text="Download Excel — coming soon")


if __name__ == "__main__":
    HomePage().mainloop()
