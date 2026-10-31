import os
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from dotenv import dotenv_values

from OpenRouterSetting import OpenRouterSetting
from OllamaSetting import OllamaSetting
from SettingService import setLLMProvider

LLM_PROVIDERS = ("openrouter", "ollama")
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"

class SettingPage(ttk.Frame):
	def __init__(self, master, on_back=None):
		super().__init__(master, padding=24)
		self.on_back = on_back
		self._build()

	def _build(self):
		header = ttk.Frame(self)
		header.pack(fill=tk.X, pady=(0, 24))

		if self.on_back:
			ttk.Button(
				header,
				text="← Back",
				style="Back.TButton",
				command=self.on_back,
			).pack(side=tk.LEFT)

		env_values = dotenv_values(ENV_PATH) if ENV_PATH.exists() else {}
		provider = (
			env_values.get("LLM_PROVIDER") or os.getenv("LLM_PROVIDER") or "ollama"
		).strip().lower()
		if provider not in LLM_PROVIDERS:
			provider = "ollama"
		self.provider_var = tk.StringVar(value=provider)

		ttk.Label(self, text="LLM Provider", style="Heading.TLabel").pack(anchor="w")
		ttk.Label(
			self,
			text="Choose which provider LearnForge uses for duplicate detection.",
			style="Muted.TLabel",
		).pack(anchor="w", pady=(2, 10))

		provider_row = ttk.Frame(self)
		provider_row.pack(fill=tk.X, pady=(0, 28))
		self.provider_box = ttk.Combobox(
			provider_row,
			textvariable=self.provider_var,
			values=LLM_PROVIDERS,
			state="readonly",
			font=("Helvetica", 12),
		)
		self.provider_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12), ipady=4)
		ttk.Button(
			provider_row,
			text="Submit",
			command=self.submit_provider,
		).pack(side=tk.RIGHT)

		ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 24))

		ttk.Label(self, text="Provider Configuration", style="Heading.TLabel").pack(anchor="w")
		ttk.Label(
			self,
			text="Set the model and connection details for each provider.",
			style="Muted.TLabel",
		).pack(anchor="w", pady=(2, 10))

		actions = ttk.Frame(self)
		actions.pack(fill=tk.X)
		actions.columnconfigure((0, 1), weight=1, uniform="settings")
		ttk.Button(
			actions,
			text="OpenRouter Setting",
			style="Secondary.TButton",
			command=self.open_llm_settings,
		).grid(row=0, column=0, sticky="ew", padx=(0, 8))
		ttk.Button(
			actions,
			text="Ollama Setting",
			style="Secondary.TButton",
			command=self.open_ollama_settings,
		).grid(row=0, column=1, sticky="ew", padx=(8, 0))

	def submit_provider(self):
		provider = self.provider_var.get().strip().lower()
		if provider not in LLM_PROVIDERS:
			messagebox.showerror(
				"Invalid provider",
				"Select OpenRouter or Ollama.",
				parent=self,
			)
			return
		try:
			setLLMProvider(provider)
		except Exception as error:
			messagebox.showerror("Could not save provider", str(error), parent=self)
			return
		messagebox.showinfo(
			"Provider saved",
			f"LLM_PROVIDER saved as '{provider}'. Restart LearnForge to apply it.",
			parent=self,
		)

	def open_llm_settings(self):
		if hasattr(self, "llm_settings_window") and self.llm_settings_window.winfo_exists():
			self.llm_settings_window.lift()
			self.llm_settings_window.focus_force()
			return
		self.llm_settings_window = OpenRouterSetting(self)

	def open_ollama_settings(self):
		if hasattr(self, "ollama_settings_window") and self.ollama_settings_window.winfo_exists():
			self.ollama_settings_window.lift()
			self.ollama_settings_window.focus_force()
			return
		self.ollama_settings_window = OllamaSetting(self)

