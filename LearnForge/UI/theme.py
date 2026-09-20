from tkinter import ttk

BG = "#0f172a"
CARD = "#1e293b"
ACCENT = "#0ea5e9"
ACCENT_HOVER = "#0284c7"
TEXT = "#f8fafc"
MUTED = "#94a3b8"
ROW_ODD = "#1e293b"
ROW_EVEN = "#162032"
HEADER = "#334155"


def apply_theme(root):
    root.configure(bg=BG)
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", background=BG, foreground=TEXT, fieldbackground=CARD)
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=CARD)
    style.configure("TLabel", background=BG, foreground=TEXT)
    style.configure("Muted.TLabel", background=BG, foreground=MUTED)
    style.configure("Card.TLabel", background=CARD, foreground=TEXT)
    style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Helvetica", 24, "bold"))
    style.configure("Subtitle.TLabel", background=BG, foreground=MUTED, font=("Helvetica", 13))
    style.configure("Heading.TLabel", background=BG, foreground=TEXT, font=("Helvetica", 16, "bold"))

    style.configure(
        "TButton",
        background=ACCENT,
        foreground="#ffffff",
        font=("Helvetica", 12, "bold"),
        padding=(16, 10),
        borderwidth=0,
    )
    style.map("TButton", background=[("active", ACCENT_HOVER), ("pressed", ACCENT_HOVER)])

    style.configure(
        "Secondary.TButton",
        background=HEADER,
        foreground=TEXT,
        font=("Helvetica", 12),
        padding=(16, 10),
        borderwidth=0,
    )
    style.map("Secondary.TButton", background=[("active", "#475569")])

    style.configure(
        "Back.TButton",
        background=HEADER,
        foreground=TEXT,
        font=("Helvetica", 11, "bold"),
        padding=(12, 6),
        borderwidth=0,
    )
    style.map("Back.TButton", background=[("active", "#475569")])

    style.configure("TEntry", fieldbackground=CARD, foreground=TEXT, insertcolor=TEXT, padding=6)
    style.configure(
        "TCombobox",
        fieldbackground=CARD,
        background=CARD,
        foreground=TEXT,
        arrowcolor=TEXT,
        padding=4,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", CARD)],
        foreground=[("readonly", TEXT)],
    )

    style.configure(
        "Treeview",
        background=CARD,
        fieldbackground=CARD,
        foreground=TEXT,
        rowheight=28,
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=HEADER,
        foreground=TEXT,
        font=("Helvetica", 11, "bold"),
        relief="flat",
    )
    style.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", "#ffffff")])
    style.configure("TScrollbar", background=CARD, troughcolor=BG, borderwidth=0, arrowcolor=TEXT)
