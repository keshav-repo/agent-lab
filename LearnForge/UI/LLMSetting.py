import os
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from dotenv import set_key


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"
PROVIDERS = ("openrouter", "ollama")


class LLMSetting(tk.Toplevel):
	def __init__(self, master):
		super().__init__(master)
		self.title("LLM Setting")
		self.resizable(False, False)
		self.transient(master.winfo_toplevel())
		self.grab_set()

		current_provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
		if ENV_PATH.exists():
			for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
				key, separator, value = line.partition("=")
				if separator and key.strip() == "LLM_PROVIDER":
					current_provider = value.strip().strip("\"'").lower()
					break
		if current_provider not in PROVIDERS:
			current_provider = "ollama"

		container = ttk.Frame(self, padding=20)
		container.pack(fill=tk.BOTH, expand=True)

		ttk.Label(container, text="LLM_PROVIDER", style="Heading.TLabel").pack(
			anchor="w", pady=(0, 10)
		)
		self.provider_var = tk.StringVar(value=current_provider)
		self.provider_box = ttk.Combobox(
			container,
			textvariable=self.provider_var,
			values=PROVIDERS,
			state="readonly",
			width=24,
		)
		self.provider_box.pack(fill=tk.X, pady=(0, 16))

		ttk.Label(
			container,
			text="Changes apply after restarting LearnForge.",
			style="Muted.TLabel",
		).pack(anchor="w", pady=(0, 16))

		buttons = ttk.Frame(container)
		buttons.pack(fill=tk.X)
		ttk.Button(buttons, text="Cancel", style="Back.TButton", command=self.destroy).pack(
			side=tk.RIGHT, padx=(8, 0)
		)
		ttk.Button(buttons, text="Save", command=self.save).pack(side=tk.RIGHT)

	def save(self):
		provider = self.provider_var.get().strip().lower()
		if provider not in PROVIDERS:
			messagebox.showerror(
				"Invalid provider",
				"Select OpenRouter or Ollama.",
				parent=self,
			)
			return

		try:
			ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
			if not ENV_PATH.exists():
				ENV_PATH.touch()
			set_key(str(ENV_PATH), "LLM_PROVIDER", provider)
		except OSError as error:
			messagebox.showerror(
				"Could not save setting",
				str(error),
				parent=self,
			)
			return

		messagebox.showinfo(
			"LLM Setting",
			f"LLM_PROVIDER saved as '{provider}'. Restart LearnForge to apply it.",
			parent=self,
		)
		self.destroy()

