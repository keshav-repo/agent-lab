import os
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from dotenv import dotenv_values, set_key


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"


class OllamaSetting(tk.Toplevel):
	def __init__(self, master):
		super().__init__(master)
		self.title("Ollama Setting")
		self.resizable(False, False)
		self.transient(master.winfo_toplevel())
		self.grab_set()

		env_values = dotenv_values(ENV_PATH) if ENV_PATH.exists() else {}
		container = ttk.Frame(self, padding=20)
		container.pack(fill=tk.BOTH, expand=True)

		self.model_var = tk.StringVar(
			value=os.getenv("OLLAMA_MODEL")
			or env_values.get("OLLAMA_MODEL")
			or "llama3.2"
		)
		self.base_url_var = tk.StringVar(
			value=os.getenv("OLLAMA_BASE_URL")
			or env_values.get("OLLAMA_BASE_URL")
			or "http://localhost:11434/v1"
		)

		ttk.Label(container, text="OLLAMA_MODEL", style="Heading.TLabel").pack(anchor="w")
		ttk.Entry(container, textvariable=self.model_var, width=40).pack(
			fill=tk.X, pady=(4, 12)
		)
		ttk.Label(container, text="OLLAMA_BASE_URL", style="Heading.TLabel").pack(anchor="w")
		ttk.Entry(container, textvariable=self.base_url_var, width=40).pack(
			fill=tk.X, pady=(4, 12)
		)
		ttk.Label(
			container,
			text="Changes apply after restarting LearnForge.",
		).pack(anchor="w", pady=(0, 16))

		buttons = ttk.Frame(container)
		buttons.pack(fill=tk.X)
		ttk.Button(buttons, text="Cancel", style="Back.TButton", command=self.destroy).pack(
			side=tk.RIGHT, padx=(8, 0)
		)
		ttk.Button(buttons, text="Save", command=self.save).pack(side=tk.RIGHT)

	def save(self):
		model = self.model_var.get().strip()
		base_url = self.base_url_var.get().strip()
		if not model or not base_url:
			messagebox.showerror(
				"Missing settings",
				"Enter both an Ollama model and base URL.",
				parent=self,
			)
			return

		try:
			ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
			if not ENV_PATH.exists():
				ENV_PATH.touch()
			set_key(str(ENV_PATH), "LLM_PROVIDER", "ollama")
			set_key(str(ENV_PATH), "OLLAMA_MODEL", model)
			set_key(str(ENV_PATH), "OLLAMA_BASE_URL", base_url)
		except OSError as error:
			messagebox.showerror(
				"Could not save settings",
				str(error),
				parent=self,
			)
			return

		messagebox.showinfo(
			"Ollama Setting",
			"Ollama settings saved. Restart LearnForge to apply them.",
			parent=self,
		)
		self.destroy()

