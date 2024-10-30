import tkinter as tk

from app.controller.app_controller import AppController
from app.init_var import InitVar
from app.view.options_view import OptionsView
from app.view.settings_view import SettingsView
from app.view.show_all_img_view import ShowAllImgView
from app.view.show_like_view import ShowLikeView


class AppView:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg='black')  # 设置背景颜色为黑色，提升对比度

        # 设置初始窗口大小
        initial_width = InitVar.WINDOW_SIZE[0]
        initial_height = InitVar.WINDOW_SIZE[1]
        self.root.geometry(f"{initial_width}x{initial_height}")  # 设置窗口大小为宽1200高800
        # 窗口化全屏（最大化窗口）
        self.root.state('zoomed')  # 最大化窗口

        # 创建顶部按钮框架
        self.top_frame = tk.Frame(self.root, bg='black')
        self.top_frame.pack(pady=10)

        # 创建图片展示框架，居中显示图片
        self.images_frame = tk.Frame(self.root, bg="black")
        self.images_frame.pack(pady=(50, 0))
        self.images_frame1 = tk.Frame(self.root, bg="black")
        self.images_frame1.pack(pady=0)

        # 处理主视图控制逻辑
        controller = AppController(self)

        # 绑定退出事件
        self.root.bind("<Escape>", controller.exit_program)

        # 显示提示
        size_label = tk.Label(
            self.top_frame,
            text=f"Ps:长按展示按钮重载图片",
            fg="white",
            bg="#1E1F22",
            font=("微软雅黑", 10),
            height=2,
        )
        size_label.pack(side=tk.LEFT, padx=10)

        # 绑定功能视图
        # 设置界面, 优先加载设置, 读取配置文件
        SettingsView(self)
        # 查看最爱图片
        ShowLikeView(self)
        # 选项框
        OptionsView(self)
        # 查看全部图片
        ShowAllImgView(self)


