import tkinter as tk
from tkinter import ttk

from LLMSetting import LLMSetting

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

		ttk.Label(self, text="Settings", style="Title.TLabel").pack(pady=(12, 6))
		ttk.Label(
			self,
			text="Choose a setting to configure.",
			style="Subtitle.TLabel",
		).pack(pady=(0, 28))

		ttk.Button(
			self,
			text="LLM Setting",
			command=self.open_llm_settings,
		).pack(pady=8, ipadx=48)

	def open_llm_settings(self):
		if hasattr(self, "llm_settings_window") and self.llm_settings_window.winfo_exists():
			self.llm_settings_window.lift()
			self.llm_settings_window.focus_force()
			return
		self.llm_settings_window = LLMSetting(self)

