import os
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from dotenv import dotenv_values, set_key

from theme import colors


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"

class OpenRouterSetting(tk.Toplevel):
	def __init__(self, master):
		super().__init__(master)
		self.title("OpenRouter Setting")
		self.resizable(False, False)
		self.configure(bg=colors()["bg"])
		self.transient(master.winfo_toplevel())
		self.grab_set()

		env_values = dotenv_values(ENV_PATH) if ENV_PATH.exists() else {}

		container = ttk.Frame(self, padding=28)
		container.pack(fill=tk.BOTH, expand=True)

		self.openrouter_frame = ttk.Frame(container)
		self.model_var = tk.StringVar(
			value=os.getenv("OPENROUTER_MODEL")
			or env_values.get("OPENROUTER_MODEL")
			or ""
		)
		self.api_key_var = tk.StringVar()
		self.saved_api_key = (
			os.getenv("OPENROUTER_API_KEY")
			or env_values.get("OPENROUTER_API_KEY")
			or ""
		)

		ttk.Label(container, text="OpenRouter", style="Title.TLabel").pack(anchor="w", pady=(0, 20))

		ttk.Label(self.openrouter_frame, text="OPENROUTER_MODEL", style="Heading.TLabel").pack(anchor="w")
		ttk.Entry(self.openrouter_frame, textvariable=self.model_var, width=44).pack(
			fill=tk.X, pady=(6, 18)
		)
		ttk.Label(
			self.openrouter_frame,
			text="OPENROUTER_API_KEY",
			style="Heading.TLabel",
		).pack(anchor="w")
		ttk.Entry(
			self.openrouter_frame,
			textvariable=self.api_key_var,
			show="•",
			width=44,
		).pack(fill=tk.X, pady=(6, 4))
		ttk.Label(
			self.openrouter_frame,
			text="Leave blank to keep the saved key.",
			style="Muted.TLabel",
		).pack(anchor="w")
		self.openrouter_frame.pack(fill=tk.X, pady=(0, 16))

		ttk.Label(
			container,
			text="Changes apply after restarting LearnForge.",
			style="Muted.TLabel",
		).pack(anchor="w", pady=(0, 20))

		buttons = ttk.Frame(container)
		buttons.pack(fill=tk.X)
		ttk.Button(buttons, text="Cancel", style="Back.TButton", command=self.destroy).pack(
			side=tk.RIGHT, padx=(8, 0)
		)
		ttk.Button(buttons, text="Save", command=self.save).pack(side=tk.RIGHT)

	def save(self):
		model = self.model_var.get().strip()
		api_key = self.api_key_var.get().strip()
		if not model:
			messagebox.showerror(
				"Missing model",
				"Enter an OpenRouter model name.",
				parent=self,
			)
			return
		if not api_key and not self.saved_api_key:
			messagebox.showerror(
				"Missing API key",
				"Enter an OpenRouter API key to use this provider.",
				parent=self,
			)
			return

		try:
			ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
			if not ENV_PATH.exists():
				ENV_PATH.touch()
			set_key(str(ENV_PATH), "LLM_PROVIDER", "openrouter")
			set_key(str(ENV_PATH), "OPENROUTER_MODEL", model)
			if api_key:
				set_key(str(ENV_PATH), "OPENROUTER_API_KEY", api_key)
		except OSError as error:
			messagebox.showerror(
				"Could not save setting",
				str(error),
				parent=self,
			)
			return

		messagebox.showinfo(
			"LLM Setting",
			"OpenRouter settings saved. Restart LearnForge to apply them.",
			parent=self,
		)
		self.destroy()


