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

		provider_row = ttk.Frame(self)
		provider_row.pack(fill=tk.X, pady=(12, 20))
		ttk.Label(provider_row, text="LLM_PROVIDER", style="Heading.TLabel").pack(
			side=tk.LEFT, padx=(0, 12)
		)
		self.provider_box = ttk.Combobox(
			provider_row,
			textvariable=self.provider_var,
			values=LLM_PROVIDERS,
			state="readonly",
		)
		self.provider_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
		ttk.Button(
			provider_row,
			text="Submit",
			command=self.submit_provider,
		).pack(side=tk.RIGHT)

		ttk.Button(
			self,
			text="Open RouterSetting",
			command=self.open_llm_settings,
		).pack(pady=8, ipadx=48)
		tk.Button(
			self,
			text="Ollama Setting",
			command=self.open_ollama_settings,
		).pack(pady=8, ipadx=48)

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

