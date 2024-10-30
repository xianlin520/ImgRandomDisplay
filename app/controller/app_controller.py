import sys


class AppController:
    def __init__(self, view):
        self.view = view

    def exit_program(self, event=None):
        """
        退出程序
        """
        print('ESC退出程序')
        sys.exit(0)

    def on_button_press(self, event):
        # 执行当前视图按钮按下
        self.view.now_view.on_button_press(event=event)
    def on_button_release(self,event):
        # 执行当前视图按钮释放
        self.view.now_view.on_button_release(event=event)
