# 导入必要的库
import io
import os
import random
import shutil
import struct
import tkinter as tk
from tkinter import filedialog, messagebox, Menu

import win32clipboard
import win32con
from PIL import Image, ImageTk
import sys
import subprocess
import time
import configparser
import json
import ctypes

from app.controller.app_controller import AppController
from app.view.app_view import AppView

if __name__ == "__main__":
    if os.name != 'nt':
        messagebox.showerror("错误", "当前程序仅支持Windows系统。")
        sys.exit()
    # 设置设置当前进程显式应用程序用户模型ID
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("RandomImageViewer")
    root = tk.Tk()
    # 初始窗口标题
    root.title("随机图片查看器")
    # 设置程序ICO
    root.iconbitmap("ChatZenLogo_64x64.ico")  # 设置程序ICO
    # 设置全局字体为微软雅黑
    default_font = ("微软雅黑", 12)
    root.option_add("*Font", default_font)
    # 将窗体对象传入主视图
    app_view = AppView(root)
    root.mainloop()