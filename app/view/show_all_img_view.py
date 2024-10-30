import threading
import tkinter as tk

from app.controller.show_img_controller import ShowImgController


class ShowAllImgView:
    def __init__(self, view):
        self.view = view
        self.root = view.root

        # 表示为全部
        self.is_all = True
        # 处理视图逻辑
        self.controller = ShowImgController(self)


        # 创建“随机显示图片”按钮
        self.button = tk.Button(
            self.view.top_frame,
            text="随机显示图片",
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
        self.is_long_pressed = False  # 记录是否长按
        self.is_btn = False # 防止多次点击, 记录是否在执行中
        # 加载图片
        self.controller.load_images()
        # 显示一次图片
        self.controller.display_images()

    def on_button_press(self, event):
        """鼠标按下事件"""
        self.is_long_pressed = False
        self.view.now_view = self
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
        if self.is_btn:
            return
        self.is_btn = True
        thr = threading.Thread(target= self.controller.load_images())
        thr.start()
        # start完成后执行赋值
        thr.join()
        self.is_btn = False


    def click_action(self):
        """点击动作, 点击展现下一组"""
        # 新建线程执行
        if self.is_btn:
            return
        self.is_btn = True
        threading.Thread(target=self.controller.display_images).start()
        # self.controller.display_images()


