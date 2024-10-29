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



"""
版本描述:
v1.4.0
- 添加图片顺序查看功能, 与随机查看同级
- 添加图片排序功能, 按时间, 大小等排序
"""

# 定义主应用类
class RandomImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("随机图片查看器")  # 初始窗口标题
        self.root.configure(bg='black')     # 设置背景颜色为黑色，提升对比度

        # 设置初始窗口大小
        initial_width = 1200
        initial_height = 800
        self.root.geometry(f"{initial_width}x{initial_height}")  # 设置窗口大小为宽1200高800
        # 设置程序ICO
        self.root.iconbitmap("ChatZenLogo_64x64.ico")  # 设置程序ICO
        # 设置运行程序ICO

        # 窗口化全屏（最大化窗口）
        self.root.state('zoomed')  # 最大化窗口

        # 设置全局字体为微软雅黑
        self.default_font = ("微软雅黑", 12)
        self.root.option_add("*Font", self.default_font)

        # 初始化变量
        self.all_image_files = []         # 所有图片文件列表
        self.remaining_images = []        # 剩余未展示的图片列表
        self.total_size = 0               # 总大小（字节）
        self.image_size_mb = {}           # 每张图片的大小（MB）
        self.photo_images = []            # Tkinter显示的图片对象
        self.favorites = []  # 收藏的图片路径列表

        # 读取配置文件
        self.config_file = "../config.ini"
        self.read_config()

        # 设置最爱配置文件
        self.favorite_config_file = "favorites.ini"
        # self.read_favorite_config()

        # 创建顶部按钮框架
        self.top_frame = tk.Frame(self.root, bg='black')
        self.top_frame.pack(pady=10)

        # 创建“随机最爱”按钮
        self.random_favorite_button = tk.Button(
            self.top_frame,
            text="查看最爱图片",
            command=self.display_random_favorite_image,
            font=self.default_font,
            bg="#333333",  # 按钮背景颜色
            fg="white",  # 按钮文字颜色
            activebackground="#555555",  # 按钮按下时的背景颜色
            activeforeground="white",  # 按钮按下时的文字颜色
            width=15,
            height=2
        )
        self.random_favorite_button.pack(side=tk.LEFT, padx=10)

        # 添加选择框
        options = ["随机展示", "按时间排序", "按大小排序"]
        self.display_option_var = tk.StringVar(value=options[0])  # 初始值设置为"随机展示"
        self.display_option_menu = tk.OptionMenu(
            self.top_frame,
            self.display_option_var,
            *options,
            command=self.update_display_option,
        )
        self.display_option_menu.config(
            # 移出白边
            indicatoron=False,
            font=self.default_font,
            bg="#135D8E",
            fg="white",
            activebackground="#555555",
            activeforeground="white",
            width=15,
            height=1
        )
        self.display_option_menu.pack(side=tk.LEFT, padx=10)

        # 创建“随机显示图片”按钮
        self.random_button = tk.Button(
            self.top_frame,
            text="查看全部图片",
            command=self.display_random_images,
            font=self.default_font,
            bg="#333333",    # 按钮背景颜色
            fg="white",      # 按钮文字颜色
            activebackground="#555555",  # 按钮按下时的背景颜色
            activeforeground="white",     # 按钮按下时的文字颜色
            width=15,
            height=2
        )
        self.random_button.pack(side=tk.LEFT, padx=10)

        # 创建“设置”按钮
        self.settings_button = tk.Button(
            self.top_frame,
            text="设置",
            command=self.open_settings,
            font=self.default_font,
            bg="#333333",
            fg="white",
            activebackground="#555555",
            activeforeground="white",
            width=10,
            height=2
        )
        self.settings_button.pack(side=tk.LEFT, padx=10)

        # 创建图片展示框架，居中显示图片
        self.images_frame = tk.Frame(self.root, bg="black")
        self.images_frame.pack(expand=True)

        # 读取图片目录并加载图片
        self.load_images()

        # 启动时自动执行一次随机显示图片
        self.display_random_images()

        # 绑定按键事件，按下Esc键退出程序
        self.root.bind("<Escape>", self.exit_program)


    def exit_program(self, event=None):
        """
        退出程序
        """
        self.root.quit()

    def update_display_option(self, value):
        """
        更新展示图片的选项并重新显示图片
        """
        if value == "随机展示":
            self.display_random_images()
        elif value == "按时间排序":
            self.display_images_sorted_by_time()
        elif value == "按大小排序":
            self.display_images_sorted_by_size()

    def display_random_favorite_image(self):
        """
        随机显示收藏列表中的一张或多张图片，排列为4列2行
        """
        try:
            if not self.favorites:
                messagebox.showinfo("提示", "收藏列表为空，请先设定一些最爱图片。")
                return

            # 清空之前的图片
            for widget in self.images_frame.winfo_children():
                widget.destroy()
            self.photo_images.clear()

            # 确定本次要展示的图片数
            num_images_to_display = min(8, len(self.favorites))

            # 随机选择收藏的图片
            selected = random.sample(self.favorites, num_images_to_display)

            # 设置网格布局参数
            columns = 4  # 每行4列
            rows = 2  # 共2行

            for index, file in enumerate(selected):
                try:
                    # 将相对路径转成绝对路径
                    file = os.path.abspath(os.path.join(self.image_dir, file))
                    # 打开图片并调整大小
                    img = Image.open(file)
                    max_size = (250, 250)  # 设置图片最大尺寸
                    if hasattr(Image, 'Resampling'):
                        resample_mode = Image.Resampling.LANCZOS
                    else:
                        resample_mode = Image.ANTIALIAS  # 兼容旧版本
                    img.thumbnail(max_size, resample=resample_mode)
                    photo = ImageTk.PhotoImage(img)
                    self.photo_images.append(photo)  # 保持引用，防止图片被垃圾回收

                    # 计算行列
                    row = index // columns
                    column = index % columns

                    # 创建图片和大小标签的容器
                    container = tk.Frame(self.images_frame, bg="black")
                    container.grid(row=row, column=column, padx=20, pady=20)

                    # 创建图片标签
                    img_label = tk.Label(container, image=photo, bg="black", cursor="hand2")
                    img_label.pack()

                    # 显示图片大小
                    size_mb = round(os.path.getsize(file) / (1024 * 1024), 2)
                    size_label = tk.Label(
                        container,
                        text=f"{size_mb} MB",
                        fg="white",
                        bg="black",
                        font=("微软雅黑", 10)
                    )
                    size_label.pack(pady=5)

                    # 绑定左键点击事件打开图片
                    img_label.bind("<Button-1>", lambda e, path=file: self.open_image(path))

                    # 绑定右键点击事件显示菜单
                    img_label.bind("<Button-3>", lambda e, path=file: self.show_context_menu(e, path))

                except Exception as e:
                    print(f"无法打开图片 {file}: {e}")

        except Exception as e:
            messagebox.showerror("错误", f"无法显示随机收藏图片: {e}")

    def read_favorite_config(self):
        """
        读取配置文件，如果存在，则加载默认读取目录和保存目录
        """
        self.favorite_config = configparser.ConfigParser()
        if os.path.exists(self.favorite_config_file):
            # 加载收藏列表
            self.favorite_config.read(self.favorite_config_file, encoding='utf-8')
            favorites_str = self.favorite_config.get('Settings', 'favorites', fallback='')
            if favorites_str:
                self.favorites = json.loads(favorites_str)
            else:
                self.favorites = []
        else:
            self.favorites = []

    def read_config(self):
        """
        读取配置文件，如果存在，则加载默认读取目录和保存目录
        """
        self.config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
            self.default_read_dir = self.config.get('Settings', 'read_dir', fallback='')
            self.default_save_dir = self.config.get('Settings', 'save_dir', fallback='')
        else:
            self.default_read_dir = ''
            self.default_save_dir = ''

    def write_favorite_config(self):
        """
        将配置写入配置文件
        """
        self.favorite_config['Settings'] = {
            'favorites': json.dumps(self.favorites)
        }
        with open(self.favorite_config_file, 'w', encoding='utf-8') as f:
            self.favorite_config.write(f)

    def write_config(self):
        """
        将配置写入配置文件
        """
        self.config['Settings'] = {
            'read_dir': self.default_read_dir,
            'save_dir': self.default_save_dir,
        }
        with open(self.config_file, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)

    def open_settings(self):
        """
        打开设置窗口，允许用户配置默认读取目录和默认保存目录
        """
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("550x300")  # 设置窗口大小为550x300
        settings_window.configure(bg='black')

        # 设置窗口在父窗口居中
        settings_window.transient(self.root)
        settings_window.grab_set()

        # 读取目录标签和按钮
        read_dir_label = tk.Label(settings_window, text="默认读取目录:", fg="white", bg="black", font=("微软雅黑", 12))
        read_dir_label.pack(pady=10)
        read_dir_frame = tk.Frame(settings_window, bg='black')
        read_dir_frame.pack(pady=5)
        self.read_dir_entry = tk.Entry(read_dir_frame, width=50, font=("微软雅黑", 12))
        self.read_dir_entry.pack(side=tk.LEFT, padx=5)
        self.read_dir_entry.insert(0, self.default_read_dir)
        read_dir_browse = tk.Button(
            read_dir_frame,
            text="浏览",
            command=lambda: self.browse_directory(self.read_dir_entry),
            font=self.default_font,
            bg="#333333",
            fg="white",
            activebackground="#555555",
            activeforeground="white"
        )
        read_dir_browse.pack(side=tk.LEFT, padx=5)

        # 保存目录标签和按钮
        save_dir_label = tk.Label(settings_window, text="默认保存目录:", fg="white", bg="black", font=("微软雅黑", 12))
        save_dir_label.pack(pady=10)
        save_dir_frame = tk.Frame(settings_window, bg='black')
        save_dir_frame.pack(pady=5)
        self.save_dir_entry = tk.Entry(save_dir_frame, width=50, font=("微软雅黑", 12))
        self.save_dir_entry.pack(side=tk.LEFT, padx=5)
        self.save_dir_entry.insert(0, self.default_save_dir)
        save_dir_browse = tk.Button(
            save_dir_frame,
            text="浏览",
            command=lambda: self.browse_directory(self.save_dir_entry),
            font=self.default_font,
            bg="#333333",
            fg="white",
            activebackground="#555555",
            activeforeground="white"
        )
        save_dir_browse.pack(side=tk.LEFT, padx=5)

        # 创建按钮框架，包括保存和重置按钮
        buttons_frame = tk.Frame(settings_window, bg='black')
        buttons_frame.pack(pady=20)

        # 保存按钮
        save_button = tk.Button(
            buttons_frame,
            text="保存",
            command=lambda: self.save_settings(settings_window),
            font=self.default_font,
            bg="#333333",
            fg="white",
            activebackground="#555555",
            activeforeground="white",
            width=10,
            height=2
        )
        save_button.pack(side=tk.LEFT, padx=10)

        # 重置按钮
        reset_button = tk.Button(
            buttons_frame,
            text="重置",
            command=lambda: self.reset_settings(settings_window),
            font=self.default_font,
            bg="#333333",
            fg="white",
            activebackground="#555555",
            activeforeground="white",
            width=10,
            height=2
        )
        reset_button.pack(side=tk.LEFT, padx=10)

    def browse_directory(self, entry_widget):
        """
        打开目录选择对话框，并将选择的目录路径写入指定的Entry组件
        """
        directory = filedialog.askdirectory()
        if directory:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, directory)

    def save_settings(self, window):
        """
        保存用户在设置窗口中选择的目录，并更新配置文件
        """
        read_dir = self.read_dir_entry.get().strip()
        save_dir = self.save_dir_entry.get().strip()

        # 检查读取目录是否存在（如果填写）
        if read_dir and not os.path.isdir(read_dir):
            messagebox.showerror("错误", "默认读取目录无效，请重新选择。")
            return

        # 检查保存目录是否存在（如果填写）
        if save_dir and not os.path.isdir(save_dir):
            messagebox.showerror("错误", "默认保存目录无效，请重新选择。")
            return

        self.default_read_dir = read_dir
        self.default_save_dir = save_dir
        self.write_config()
        messagebox.showinfo("成功", "设置已保存。")
        window.destroy()
        # 重载图片，以应用新的读取目录
        self.load_images()
        # 自动显示一次随机图片
        self.display_random_images()

    def reset_settings(self, window):
        """
        重置设置，将默认读取目录和默认保存目录清空
        """
        self.default_read_dir = ''
        self.default_save_dir = ''
        self.write_config()
        # 清空Entry组件内容
        self.read_dir_entry.delete(0, tk.END)
        self.save_dir_entry.delete(0, tk.END)
        messagebox.showinfo("成功", "设置已重置。")
        window.destroy()
        # 重载图片，以应用重置后的读取目录
        self.load_images()
        # 自动显示一次随机图片
        self.display_random_images()

    def load_images(self):
        """
        读取指定目录下的所有图片文件，并计算总大小
        """
        # 如果配置文件中有默认读取目录，则使用，否则弹出选择目录
        if self.default_read_dir and os.path.isdir(self.default_read_dir):
            self.image_dir = self.default_read_dir
        else:
            self.image_dir = filedialog.askdirectory(title="请选择图片所在的文件夹")
            if not self.image_dir:
                messagebox.showerror("错误", "未选择任何文件夹，程序将退出。")
                self.root.quit()
                return

        # 设置配置文件路径为图片目录的根目录下
        self.favorite_config_file = os.path.join(self.image_dir, "favorites.ini")

        # 读取配置文件
        self.read_favorite_config()

        # 清空之前的图片列表
        self.all_image_files.clear()

        # 读取目录下的所有文件（不包括子文件夹）
        for file in os.listdir(self.image_dir):
            file_path = os.path.join(self.image_dir, file)
            if os.path.isfile(file_path):
                # 检查文件是否是图片格式
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
                    self.all_image_files.append(file)

        if not self.all_image_files:
            messagebox.showerror("错误", "所选目录下没有图片文件，程序将退出。")
            self.root.quit()
            return

        # 初始化剩余图片列表为所有图片
        self.remaining_images = self.all_image_files.copy()

        # 计算总大小和每张图片的大小
        self.total_size = 0
        self.image_size_mb = {}
        for file in self.all_image_files:
            file_path = os.path.join(self.image_dir, file)
            size = os.path.getsize(file_path)
            self.total_size += size
            size_mb = round(size / (1024 * 1024), 2)
            self.image_size_mb[file] = size_mb

        # 更新窗口标题
        total_size_gb = round(self.total_size / (1024 ** 3), 2)  # 转换为GB
        file_count = len(self.all_image_files)
        self.root.title(f"随机图片查看器 - 已读取 {file_count} 张 - {total_size_gb} GB -- By 羡林i")

    def display_random_images(self):
        """
        随机选择8张未展示过的图片并显示在界面上，排列为4列2行
        如果所有图片都已展示，则提示用户并重置展示列表
        """
        # 检查是否还有剩余的图片可以展示
        if not self.remaining_images:
            messagebox.showinfo("提示", "所有图片都已展示完毕，即将重置展示列表。")
            self.remaining_images = self.all_image_files.copy()

        # 确定本次要展示的图片数
        num_images_to_display = min(8, len(self.remaining_images))

        # 随机选择未展示的图片
        selected = random.sample(self.remaining_images, num_images_to_display)

        # 从剩余图片列表中移除已选择的图片
        for file in selected:
            self.remaining_images.remove(file)

        # 清空之前的图片
        for widget in self.images_frame.winfo_children():
            widget.destroy()
        self.photo_images.clear()

        # 设置网格布局参数
        columns = 4  # 每行4列
        rows = 2     # 共2行

        for index, file in enumerate(selected):
            file_path = os.path.join(self.image_dir, file)
            try:
                # 打开图片并调整大小
                img = Image.open(file_path)
                max_size = (250, 250)  # 设置图片最大尺寸
                if hasattr(Image, 'Resampling'):
                    resample_mode = Image.Resampling.LANCZOS
                else:
                    resample_mode = Image.ANTIALIAS  # 兼容旧版本
                img.thumbnail(max_size, resample=resample_mode)
                photo = ImageTk.PhotoImage(img)
                self.photo_images.append(photo)  # 保持引用，防止图片被垃圾回收

                # 计算行列
                row = index // columns
                column = index % columns

                # 创建图片和大小标签的容器
                container = tk.Frame(self.images_frame, bg="black")
                container.grid(row=row, column=column, padx=20, pady=20)

                # 创建图片标签
                img_label = tk.Label(container, image=photo, bg="black", cursor="hand2")
                img_label.pack()

                # 显示图片大小
                size_label = tk.Label(
                    container,
                    text=f"{self.image_size_mb[file]} MB",
                    fg="white",
                    bg="black",
                    font=("微软雅黑", 10)
                )
                size_label.pack(pady=5)

                # 绑定左键点击事件打开图片
                img_label.bind("<Button-1>", lambda e, path=file_path: self.open_image(path))

                # 绑定右键点击事件显示菜单
                img_label.bind("<Button-3>", lambda e, path=file_path: self.show_context_menu(e, path))

            except Exception as e:
                print(f"无法打开图片 {file}: {e}")

    def display_images_sorted_by_time(self):
        """
        按时间排序展示图片
        """
        sorted_images = sorted(self.all_image_files, key=lambda f: os.path.getmtime(os.path.join(self.image_dir, f)))
        self.display_images(sorted_images)

    def display_images_sorted_by_size(self):
        """
        按大小排序展示图片
        """
        sorted_images = sorted(self.all_image_files, key=lambda f: os.path.getsize(os.path.join(self.image_dir, f)))
        self.display_images(sorted_images)

    def display_images(self, image_list):
        """
        根据提供的图片列表展示图片
        """
        # 检查是否还有剩余的图片可以展示
        if not self.remaining_images:
            messagebox.showinfo("提示", "所有图片都已展示完毕，即将重置展示列表。")
            self.remaining_images = image_list.copy()

        # 确定本次展示的图片数
        num_images_to_display = min(8, len(self.remaining_images))
        # 选择未展示的图片前八张
        selected = image_list[:num_images_to_display]

        # 从剩余图片列表中移除已选择的图片
        for file in selected:
            self.remaining_images.remove(file)

        # 清空之前的图片
        for widget in self.images_frame.winfo_children():
            widget.destroy()
        self.photo_images.clear()

        # 设置网格布局参数
        columns = 4  # 每行4列
        rows = 2     # 共2行

        for index, file in enumerate(selected):
            file_path = os.path.join(self.image_dir, file)
            try:
                # 打开图片并调整大小
                img = Image.open(file_path)
                max_size = (250, 250)  # 设置图片最大尺寸
                if hasattr(Image, 'Resampling'):
                    resample_mode = Image.Resampling.LANCZOS
                else:
                    resample_mode = Image.ANTIALIAS  # 兼容旧版本
                img.thumbnail(max_size, resample=resample_mode)
                photo = ImageTk.PhotoImage(img)
                self.photo_images.append(photo)  # 保持引用，防止图片被垃圾回收

                # 计算行列
                row = index // columns
                column = index % columns

                # 创建图片和大小标签的容器
                container = tk.Frame(self.images_frame, bg="black")
                container.grid(row=row, column=column, padx=20, pady=20)

                # 创建图片标签
                img_label = tk.Label(container, image=photo, bg="black", cursor="hand2")
                img_label.pack()

                # 显示图片大小
                size_label = tk.Label(
                    container,
                    text=f"{self.image_size_mb[file]} MB",
                    fg="white",
                    bg="black",
                    font=("微软雅黑", 10)
                )
                size_label.pack(pady=5)

                # 绑定左键点击事件打开图片
                img_label.bind("<Button-1>", lambda e, path=file_path: self.open_image(path))

                # 绑定右键点击事件显示菜单
                img_label.bind("<Button-3>", lambda e, path=file_path: self.show_context_menu(e, path))

            except Exception as e:
                print(f"无法打开图片 {file}: {e}")

    def open_image(self, path):
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

    def show_context_menu(self, event, path):
        """
        显示右键菜单，包含“另存为”和“打开文件所在位置”选项
        """
        menu = Menu(self.root, tearoff=0)
        menu.add_command(label="另存为", command=lambda: self.save_as(path))
        menu.add_command(label="复制图片", command=lambda: self.copy_image(path))
        menu.add_command(label="打开文件所在位置", command=lambda: self.open_file_location(path))
        menu.add_command(label="移出图片", command=lambda: self.remove_image(path))  # 新增“移出图片”选项
        # 添加空行
        menu.add_separator()
        if os.path.relpath(path, self.image_dir) in self.favorites:
            menu.add_command(label="取消最爱", command=lambda: self.cancel_favorite(path))
        else:
            menu.add_command(label="设为最爱", command=lambda: self.set_as_favorite(path))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def save_as(self, path):
        """
        将选定的图片另存为到指定目录，默认文件名为 '另存图片-HHMMSS'
        """
        try:
            # 如果配置文件中有默认保存目录，则使用，否则弹出选择目录
            if self.default_save_dir and os.path.isdir(self.default_save_dir):
                save_dir = self.default_save_dir
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

    def copy_image(self, path):
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

    def open_file_location(self, path):
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

    def remove_image(self, path):
        """
        将选中的图片移出到 Remove 子目录下，如果不存在则创建
        """
        # 添加确认按钮
        if not messagebox.askokcancel("移出图片", "确定要移出图片吗？"):
            return

        # 判断是否在最爱中
        if path in self.favorites:
            self.cancel_favorite(path)
        try:
            # 定义 Remove 子目录路径
            remove_dir = os.path.join(self.image_dir, "Remove")

            # 如果 Remove 子目录不存在，则创建
            if not os.path.exists(remove_dir):
                os.makedirs(remove_dir)

            # 目标路径
            destination = os.path.join(remove_dir, os.path.basename(path))

            # 移动文件到 Remove 子目录
            shutil.move(path, destination)

            # 提示用户
            messagebox.showinfo("成功", f"图片已移出到 {remove_dir}")

            # 重新加载图片列表
            self.load_images()

            # 重新显示随机图片
            self.display_random_images()
        except Exception as e:
            messagebox.showerror("错误", f"无法移出图片: {e}")

    def set_as_favorite(self, path):
        """
        将选中的图片添加到收藏列表
        """
        # 把path转成相对路径
        path = os.path.relpath(path, self.image_dir)
        try:
            if path in self.favorites:
                messagebox.showinfo("提示", "该图片已在收藏列表中。")
                return
            self.favorites.append(path)
            self.write_favorite_config()
            messagebox.showinfo("成功", "图片已添加到收藏列表。")
        except Exception as e:
            messagebox.showerror("错误", f"无法将图片设为最爱: {e}")

    def cancel_favorite(self, path):
        """
        将选中的图片从收藏列表中移除
        """
        # 把path转成相对路径
        path = os.path.relpath(path, self.image_dir)
        try:
            if path not in self.favorites:
                messagebox.showinfo("提示", "该图片不在收藏列表中。")
                return
            self.favorites.remove(path)
            self.write_favorite_config()
            messagebox.showinfo("成功", "图片已从收藏列表中移除。")
        except Exception as e:
            messagebox.showerror("错误", f"无法取消最爱: {e}")


# 主程序运行
if __name__ == "__main__":
    if os.name != 'nt':
        messagebox.showerror("错误", "当前程序仅支持Windows系统。")
        sys.exit()
    # 设置设置当前进程显式应用程序用户模型ID
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("RandomImageViewer")
    root = tk.Tk()
    app = RandomImageViewer(root)
    root.mainloop()
