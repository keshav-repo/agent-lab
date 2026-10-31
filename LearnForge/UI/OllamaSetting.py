import os
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from dotenv import dotenv_values, set_key


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

		env_values = dotenv_values(ENV_PATH) if ENV_PATH.exists() else {}
		current_provider = (
			os.getenv("LLM_PROVIDER") or env_values.get("LLM_PROVIDER") or "ollama"
		).strip().lower()
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
		self.provider_box.bind("<<ComboboxSelected>>", self.on_provider_changed)

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

		ttk.Label(self.openrouter_frame, text="OPENROUTER_MODEL").pack(anchor="w")
		ttk.Entry(self.openrouter_frame, textvariable=self.model_var, width=36).pack(
			fill=tk.X, pady=(4, 12)
		)
		ttk.Label(
			self.openrouter_frame,
			text="OPENROUTER_API_KEY (leave blank to keep the saved key)",
		).pack(anchor="w")
		ttk.Entry(
			self.openrouter_frame,
			textvariable=self.api_key_var,
			show="•",
			width=36,
		).pack(fill=tk.X, pady=(4, 12))
		if current_provider == "openrouter":
			self.openrouter_frame.pack(fill=tk.X, pady=(0, 8))

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

	def on_provider_changed(self, _event=None):
		if self.provider_var.get().strip().lower() == "openrouter":
			self.openrouter_frame.pack(fill=tk.X, pady=(0, 8))
		else:
			self.openrouter_frame.pack_forget()

	def save(self):
		provider = self.provider_var.get().strip().lower()
		if provider not in PROVIDERS:
			messagebox.showerror(
				"Invalid provider",
				"Select OpenRouter or Ollama.",
				parent=self,
			)
			return

		model = self.model_var.get().strip()
		api_key = self.api_key_var.get().strip()
		if provider == "openrouter":
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
			set_key(str(ENV_PATH), "LLM_PROVIDER", provider)
			if provider == "openrouter":
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
			f"LLM_PROVIDER saved as '{provider}'. Restart LearnForge to apply it.",
			parent=self,
		)
		self.destroy()

