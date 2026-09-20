from tkinter import ttk

THEMES = {
    "light": {
        "bg": "#f8fafc",
        "card": "#ffffff",
        "accent": "#0284c7",
        "accent_hover": "#0369a1",
        "text": "#0f172a",
        "muted": "#64748b",
        "row_odd": "#f1f5f9",
        "row_even": "#ffffff",
        "header": "#e2e8f0",
        "button_fg": "#ffffff",
        "secondary": "#e2e8f0",
        "secondary_hover": "#cbd5e1",
        "selected_fg": "#ffffff",
    },
    "dark": {
        "bg": "#0f172a",
        "card": "#1e293b",
        "accent": "#0ea5e9",
        "accent_hover": "#0284c7",
        "text": "#f8fafc",
        "muted": "#94a3b8",
        "row_odd": "#1f2937",
        "row_even": "#111827",
        "header": "#334155",
        "button_fg": "#ffffff",
        "secondary": "#334155",
        "secondary_hover": "#475569",
        "selected_fg": "#ffffff",
    },
}

current_mode = "light"


def colors():
    return THEMES[current_mode]


def apply_theme(root, mode=None):
    global current_mode
    if mode is not None:
        current_mode = mode
    c = colors()
    root.configure(bg=c["bg"])
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", background=c["bg"], foreground=c["text"], fieldbackground=c["card"])
    style.configure("TFrame", background=c["bg"])
    style.configure("Card.TFrame", background=c["card"])
    style.configure("TLabel", background=c["bg"], foreground=c["text"])
    style.configure("Muted.TLabel", background=c["bg"], foreground=c["muted"])
    style.configure("Card.TLabel", background=c["card"], foreground=c["text"])
    style.configure(
        "Title.TLabel",
        background=c["bg"],
        foreground=c["text"],
        font=("Helvetica", 24, "bold"),
    )
    style.configure(
        "Subtitle.TLabel",
        background=c["bg"],
        foreground=c["muted"],
        font=("Helvetica", 13),
    )
    style.configure(
        "Heading.TLabel",
        background=c["bg"],
        foreground=c["text"],
        font=("Helvetica", 16, "bold"),
    )

    style.configure(
        "TButton",
        background=c["accent"],
        foreground=c["button_fg"],
        font=("Helvetica", 12, "bold"),
        padding=(16, 10),
        borderwidth=0,
    )
    style.map("TButton", background=[("active", c["accent_hover"]), ("pressed", c["accent_hover"])])

    style.configure(
        "Secondary.TButton",
        background=c["secondary"],
        foreground=c["text"],
        font=("Helvetica", 12),
        padding=(16, 10),
        borderwidth=0,
    )
    style.map("Secondary.TButton", background=[("active", c["secondary_hover"])])

    style.configure(
        "Back.TButton",
        background=c["secondary"],
        foreground=c["text"],
        font=("Helvetica", 11, "bold"),
        padding=(12, 6),
        borderwidth=0,
    )
    style.map("Back.TButton", background=[("active", c["secondary_hover"])])

    style.configure(
        "TEntry",
        fieldbackground=c["card"],
        foreground=c["text"],
        insertcolor=c["text"],
        padding=6,
    )
    style.configure(
        "TCombobox",
        fieldbackground=c["card"],
        background=c["card"],
        foreground=c["text"],
        arrowcolor=c["text"],
        padding=4,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", c["card"])],
        foreground=[("readonly", c["text"])],
    )

    style.configure(
        "Treeview",
        background=c["row_even"],
        fieldbackground=c["row_even"],
        foreground=c["text"],
        rowheight=28,
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=c["header"],
        foreground=c["text"],
        font=("Helvetica", 11, "bold"),
        relief="flat",
    )
    style.map(
        "Treeview",
        background=[("selected", c["accent"]), ("!selected", c["row_even"])],
        foreground=[("selected", c["selected_fg"]), ("!selected", c["text"])],
    )
    style.map(
        "Treeview",
        foreground=[
            elm
            for elm in style.map("Treeview", query_opt="foreground")
            if elm[:2] != ("!disabled", "!selected")
        ],
        background=[
            elm
            for elm in style.map("Treeview", query_opt="background")
            if elm[:2] != ("!disabled", "!selected")
        ],
    )
    style.configure(
        "TScrollbar",
        background=c["card"],
        troughcolor=c["bg"],
        borderwidth=0,
        arrowcolor=c["text"],
    )
    return current_mode


def toggle_theme(root):
    return apply_theme(root, "dark" if current_mode == "light" else "light")


def toggle_label():
    return "Light mode" if current_mode == "dark" else "Night mode"
