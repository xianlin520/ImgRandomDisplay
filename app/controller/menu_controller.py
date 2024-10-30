# 导入必要的库
import configparser
import io
import json
import os
import shutil
import subprocess
import time
from tkinter import filedialog, messagebox

import win32clipboard
from PIL import Image

from app.init_var import InitVar


def open_image(path):
    """
    打开指定路径的图片
    仅适配Windows系统
    """
    try:
        if os.name == 'nt':  # Windows
            os.startfile(path)
        else:
            messagebox.showinfo("提示", "当前操作系统不支持此功能。")
    except Exception as e:
        messagebox.showerror("错误", f"无法打开图片: {e}")


def save_as(path):
    """
    将选定的图片另存为到指定目录，默认文件名为 '另存图片-HHMMSS'
    """
    try:
        # 如果配置文件中有默认保存目录，则使用，否则弹出选择目录
        if InitVar.default_save_dir and os.path.isdir(InitVar.default_save_dir):
            save_dir = InitVar.default_save_dir
        else:
            save_dir = filedialog.askdirectory(title="选择保存目录")
            if not save_dir:
                return

        timestamp = time.strftime("%H%M%S")
        filename = f"另存图片-{timestamp}{os.path.splitext(path)[1]}"
        destination = os.path.join(save_dir, filename)
        shutil.copy2(path, destination)
        messagebox.showinfo("成功", f"图片已保存为 {filename}")
    except Exception as e:
        messagebox.showerror("错误", f"无法保存图片: {e}")


def copy_image(path):
    """
    将选中的图片路径复制到剪贴板
    """
    try:
        if not path:
            messagebox.showwarning("警告", "未选中任何图片。")
            return
        image = Image.open(path)

        output = io.BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]  # BMP 文件头前14字节
        output.close()

        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        finally:
            win32clipboard.CloseClipboard()
    except Exception as e:
        messagebox.showerror("错误", f"无法复制图片路径: {e}")


def open_file_location(path):
    """
    打开指定文件所在的文件夹，并选中该文件
    仅适配Windows系统
    """
    try:
        if os.name == 'nt':  # Windows
            # 将 '/select,' 和路径合并为一个参数
            explorer_argument = f'/select,{os.path.normpath(path)}'
            subprocess.run(['explorer', explorer_argument])
        else:
            messagebox.showinfo("提示", "当前操作系统不支持此功能。")
    except Exception as e:
        messagebox.showerror("错误1", f"无法打开文件所在位置: {e}")


def remove_image(path):
    """
    将选中的图片移出到 Remove 子目录下，如果不存在则创建
    """
    # 添加确认按钮
    if not messagebox.askokcancel("移出图片", "确定要移出图片吗？"):
        return

    # 判断是否在最爱中
    if path in InitVar.favorites:
        cancel_favorite(path)
    try:
        # 定义 Remove 子目录路径
        remove_dir = os.path.join(InitVar.image_dir, "Remove")

        # 如果 Remove 子目录不存在，则创建
        if not os.path.exists(remove_dir):
            os.makedirs(remove_dir)

        # 目标路径
        destination = os.path.join(remove_dir, os.path.basename(path))

        # 移动文件到 Remove 子目录
        shutil.move(path, destination)

        # 提示用户
        messagebox.showinfo("成功", f"图片已移出到 {remove_dir}")

    except Exception as e:
        messagebox.showerror("错误", f"无法移出图片: {e}")


def set_as_favorite(path):
    """
    将选中的图片添加到收藏列表
    """
    # 把path转成相对路径
    path = os.path.relpath(path, InitVar.image_dir)
    try:
        if path in InitVar.favorites:
            messagebox.showinfo("提示", "该图片已在收藏列表中。")
            return
        InitVar.favorites.append(path)
        write_favorite_config()
        messagebox.showinfo("成功", "图片已添加到收藏列表。")
    except Exception as e:
        messagebox.showerror("错误", f"无法将图片设为最爱: {e}")


def cancel_favorite(path):
    """
    将选中的图片从收藏列表中移除
    """
    # 把path转成相对路径
    path = os.path.relpath(path, InitVar.image_dir)
    try:
        if path not in InitVar.favorites:
            messagebox.showinfo("提示", "该图片不在收藏列表中。")
            return
        InitVar.favorites.remove(path)
        write_favorite_config()
        messagebox.showinfo("成功", "图片已从收藏列表中移除。")
    except Exception as e:
        messagebox.showerror("错误", f"无法取消最爱: {e}")


favorite_config = configparser.ConfigParser()


def write_favorite_config():
    """
    将配置写入配置文件
    """
    favorite_config['Settings'] = {
        'favorites': json.dumps(InitVar.favorites)
    }
    favorite_config_file = os.path.join(InitVar.image_dir, InitVar.LIKE_CONFIG_FILE)
    with open(favorite_config_file, 'w', encoding='utf-8') as f:
        favorite_config.write(f)
