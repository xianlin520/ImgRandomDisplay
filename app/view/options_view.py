import tkinter as tk

from app.controller.options_controller import OptionsController
from app.init_var import InitVar


class OptionsView:
    def __init__(self, view):
        self.view = view
        self.root = view.root

        self.controller = OptionsController(self)
        # 添加选择框
        options_list = InitVar.OPTIONS_LIST
        self.display_option_var = tk.StringVar(value=InitVar.options)  # 初始值设置为"随机展示"
        self.display_option_menu = tk.OptionMenu(
            self.view.top_frame,
            self.display_option_var,
            *options_list,
            command=self.controller.update_display_option,
        )
        self.display_option_menu.config(
            # 移出白边
            indicatoron=False,
            bg="#135D8E",
            fg="white",
            activebackground="#555555",
            activeforeground="white",
            width=15,
            height=1
        )
        self.display_option_menu.pack(side=tk.LEFT, padx=10)
