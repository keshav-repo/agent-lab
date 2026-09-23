import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from EntityPage import EntityPage
from ExcelUtility import ExcelUtility
from JsonUtility import JsonUtility
from theme import apply_theme, toggle_label, toggle_theme

class HomePage(tk.Tk):
    def __init__(self):
        super().__init__()
        apply_theme(self, "light")
        self.title("LearnForge")
        self.minsize(720, 480)
        self.geometry("780x520")
        self._set_icon()
        self.entity_page = None
        self.excel_page = None
        self.json_page = None
        self._build_shell()
        self._build_home()
        self.show_home()

    def _set_icon(self):
        icon_path = Path(__file__).resolve().parent / "app_icon_256.png"
        if not icon_path.exists():
            return
        self._icon_image = tk.PhotoImage(file=str(icon_path))
        self.iconphoto(True, self._icon_image)

    def _build_shell(self):
        self.content = ttk.Frame(self)
        self.content.pack(fill=tk.BOTH, expand=True)

        self.theme_btn = ttk.Button(
            self,
            text=toggle_label(),
            style="Back.TButton",
            command=self.on_toggle_theme,
        )
        self.theme_btn.place(relx=1.0, x=-12, y=10, anchor="ne")
        self.theme_btn.lift()

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
            text="Excel Utility",
            style="Secondary.TButton",
            command=self.show_excel,
        ).pack(fill=tk.X, pady=8, ipadx=48)

        ttk.Button(
            actions,
            text="Json Utility",
            style="Secondary.TButton",
            command=self.show_json,
        ).pack(fill=tk.X, pady=8, ipadx=48)

    def on_toggle_theme(self):
        toggle_theme(self)
        self.theme_btn.config(text=toggle_label())
        if self.entity_page is not None:
            self.entity_page.refresh_theme()

    def _hide_pages(self):
        self.home_frame.pack_forget()
        if self.entity_page is not None:
            self.entity_page.pack_forget()
        if self.excel_page is not None:
            self.excel_page.pack_forget()
        if self.json_page is not None:
            self.json_page.pack_forget()

    def show_home(self):
        self._hide_pages()
        self.geometry("780x520")
        self.title("LearnForge")
        self.home_frame.pack(fill=tk.BOTH, expand=True)
        self.theme_btn.lift()

    def show_entities(self):
        self._hide_pages()
        self.geometry("1180x640")
        self.title("Learning Entities")
        if self.entity_page is None:
            self.entity_page = EntityPage(self.content, on_back=self.show_home)
        self.entity_page.pack(fill=tk.BOTH, expand=True)
        self.entity_page.refresh()
        self.theme_btn.lift()

    def show_excel(self):
        self._hide_pages()
        self.geometry("780x520")
        self.title("Excel Utility")
        if self.excel_page is None:
            self.excel_page = ExcelUtility(self.content, on_back=self.show_home)
        self.excel_page.pack(fill=tk.BOTH, expand=True)
        self.theme_btn.lift()

    def show_json(self):
        self._hide_pages()
        self.geometry("780x520")
        self.title("JSON Utility")
        if self.json_page is None:
            self.json_page = JsonUtility(self.content, on_back=self.show_home)
        self.json_page.pack(fill=tk.BOTH, expand=True)
        self.theme_btn.lift()


if __name__ == "__main__":
    HomePage().mainloop()
