# 导入必要的库
import base64
import ctypes
import os
import sys
import tkinter as tk
from tkinter import messagebox
import time
import threading

from app.init_var import InitVar
from app.view.app_view import AppView

if __name__ == "__main__":
    if os.name != 'nt':
        messagebox.showerror("错误", "当前程序仅支持Windows系统。")
        sys.exit()
    # 设置设置当前进程显式应用程序用户模型ID
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("RandomImageViewer")
    root = tk.Tk()

    # 初始窗口标题
    root.title(InitVar.WINDOW_TITLE)

    # 设置程序ICO
    # 读取Base64转成ICO文件
    icon_bytes = base64.b64decode(InitVar.ICO_)
    # 保存为临时 ICO 文件
    temp_icon_path = "temp_icon.ico"
    with open(temp_icon_path, "wb") as icon_file:
        icon_file.write(icon_bytes)
    root.iconbitmap(temp_icon_path)  # 设置程序ICO
    # 删除临时 ICO 文件
    os.remove(temp_icon_path)

    # 设置全局字体为微软雅黑
    default_font = ("微软雅黑", 12)
    root.option_add("*Font", default_font)

    # 将窗体对象传入主视图
    app_view = AppView(root)
    root.mainloop()


