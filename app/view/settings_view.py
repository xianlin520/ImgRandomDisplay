import tkinter as tk

from app.controller.settings_controller import SettingsController


class SettingsView:
    def __init__(self, view):
        self._view = view
        self.root = view.root

        self.controller = SettingsController(self)

        # 创建“设置”按钮
        self.settings_button = tk.Button(
            self._view.top_frame,
            text="设置",
            command=self.controller.open_settings,
            bg="#333333",
            fg="white",
            activebackground="#555555",
            activeforeground="white",
            width=10,
            height=2
        )
        self.settings_button.pack(side=tk.RIGHT, padx=10)
