import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from EntityPage import EntityPage
from theme import apply_theme, toggle_label, toggle_theme


class HomePage(tk.Tk):
    def __init__(self):
        super().__init__()
        apply_theme(self, "light")
        self.title("LearnForge")
        self.minsize(720, 480)
        self.geometry("780x520")
        self.entity_page = None
        self._build_shell()
        self._build_home()
        self.show_home()

    def _build_shell(self):
        topbar = ttk.Frame(self, padding=(12, 8))
        topbar.pack(fill=tk.X, side=tk.TOP)
        self.theme_btn = ttk.Button(
            topbar,
            text=toggle_label(),
            style="Back.TButton",
            command=self.on_toggle_theme,
        )
        self.theme_btn.pack(side=tk.RIGHT)

        self.content = ttk.Frame(self)
        self.content.pack(fill=tk.BOTH, expand=True)

    def _build_home(self):
        self.home_frame = ttk.Frame(self.content, padding=48)

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

    def on_toggle_theme(self):
        toggle_theme(self)
        self.theme_btn.config(text=toggle_label())
        if self.entity_page is not None:
            self.entity_page.refresh_theme()

    def show_home(self):
        if self.entity_page is not None:
            self.entity_page.pack_forget()
        self.geometry("780x520")
        self.title("LearnForge")
        self.home_frame.pack(fill=tk.BOTH, expand=True)

    def show_entities(self):
        self.home_frame.pack_forget()
        self.geometry("1180x640")
        self.title("Learning Entities")
        if self.entity_page is None:
            self.entity_page = EntityPage(self.content, on_back=self.show_home)
        self.entity_page.pack(fill=tk.BOTH, expand=True)
        self.entity_page.refresh()

    def download_excel(self):
        self.todo_label.config(text="Download Excel — coming soon")


if __name__ == "__main__":
    HomePage().mainloop()
