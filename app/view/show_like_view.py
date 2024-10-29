import tkinter as tk

from app.controller.show_like_controller import ShowLikeController


class ShowLikeView:
    def __init__(self, view):
        self.view = view
        self.root = view.root

        # 处理视图逻辑
        self.controller = ShowLikeController(self)

        # 创建“随机最爱”按钮
        self.button = tk.Button(
            self.view.top_frame,
            text="查看最爱图片",
            bg="#333333",  # 按钮背景颜色
            fg="white",  # 按钮文字颜色
            activebackground="#555555",  # 按钮按下时的背景颜色
            activeforeground="white",  # 按钮按下时的文字颜色
            width=15,
            height=2
        )
        self.button.pack(side=tk.LEFT, padx=10)
        # 绑定鼠标按下和松开事件
        self.button.bind("<ButtonPress-1>", self.on_button_press)
        self.button.bind("<ButtonRelease-1>", self.on_button_release)
        self.press_start_time = None
        self.is_long_pressed = False  # 新增状态标志
        # 加载图片
        self.controller.load_images()

    def on_button_press(self, event):
        """鼠标按下事件"""
        self.is_long_pressed = False
        self.press_start_time = self.root.after(1000, self.long_press_action)  # 1秒后调用长按动作

    def on_button_release(self, event):
        """鼠标松开事件"""
        if self.press_start_time is not None:  # 只有在长按开始后才取消
            self.root.after_cancel(self.press_start_time)  # 取消长按动作
            self.press_start_time = None  # 重置开始时间
            if not self.is_long_pressed:
                # 执行点击操作
                self.click_action()

    def long_press_action(self):
        """长按动作, 长按重新载图"""
        self.is_long_pressed = True
        self.controller.load_images()

    def click_action(self):
        """点击动作, 点击展现下一组"""
        self.controller.display_images()
