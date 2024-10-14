# 导入必要的库
import os
import random
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import sys
import subprocess
import time

"""
此版本描述:
1. 窗口化全屏（最大化窗口）
2. 选择图片目录
3. 随机显示图片
4. 显示图片的大小
5. 保存到指定目录
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

        # 窗口化全屏（最大化窗口）
        self.set_maximized_window()

        # 设置全局字体为微软雅黑
        self.default_font = ("微软雅黑", 12)
        self.root.option_add("*Font", self.default_font)

        # 初始化变量
        self.image_dir = ""               # 图片目录
        self.all_image_files = []         # 所有图片文件列表
        self.remaining_images = []        # 剩余未展示的图片列表
        self.total_size = 0               # 总大小（字节）
        self.image_size_mb = {}           # 每张图片的大小（MB）
        self.photo_images = []            # Tkinter显示的图片对象

        # 创建随机按钮
        self.random_button = tk.Button(
            self.root,
            text="随机显示图片",
            command=self.display_random_images,
            font=self.default_font,
            bg="#333333",    # 按钮背景颜色
            fg="white",      # 按钮文字颜色
            activebackground="#555555",  # 按钮按下时的背景颜色
            activeforeground="white"     # 按钮按下时的文字颜色
        )
        self.random_button.pack(pady=20)

        # 创建图片展示框架，居中显示图片
        self.images_frame = tk.Frame(self.root, bg="black")
        self.images_frame.pack(expand=True)

        # 选择图片目录并读取文件
        self.select_directory()

        # 启动时自动执行一次随机显示图片
        self.display_random_images()

        # 绑定按键事件，按下Esc键退出程序
        self.root.bind("<Escape>", self.exit_program)

    def set_maximized_window(self):
        """
        设置窗口为最大化状态（窗口化全屏）
        支持Windows、macOS和Linux
        """
        if sys.platform.startswith('win'):
            self.root.state('zoomed')  # Windows
        elif sys.platform.startswith('darwin'):
            # macOS没有直接的最大化方法，但可以通过稍微调整窗口大小来模拟
            try:
                self.root.attributes('-zoomed', True)
            except:
                pass  # 某些macOS版本可能不支持'-zoomed'属性
        else:
            # 对于Linux，可以尝试使用 'zoomed' 状态
            self.root.state('zoomed')

    def exit_program(self, event=None):
        """
        退出程序
        """
        self.root.quit()

    def select_directory(self):
        """
        弹出对话框让用户选择图片目录，并读取目录下的图片文件
        """
        self.image_dir = filedialog.askdirectory(title="请选择图片所在的文件夹")
        if not self.image_dir:
            messagebox.showerror("错误", "未选择任何文件夹，程序将退出。")
            self.root.quit()
            return

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
        self.root.title(f"随机图片查看器 - 已读取 {file_count} 张 - {total_size_gb} GB")

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

    def open_image(self, path):
        """
        打开指定路径的图片
        支持Windows、macOS和Linux
        """
        try:
            if sys.platform.startswith('darwin'):
                subprocess.call(('open', path))
            elif os.name == 'nt':  # Windows
                os.startfile(path)
            elif os.name == 'posix':  # Linux
                subprocess.call(['xdg-open', path])
            else:
                messagebox.showinfo("提示", "无法在此操作系统上打开图片。")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开图片: {e}")

    def show_context_menu(self, event, path):
        """
        显示右键菜单，包含“另存为”选项
        """
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="另存为", command=lambda: self.save_as(path))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def save_as(self, path):
        """
        将选定的图片另存为到指定目录，默认文件名为 '另存图片-分秒'
        """
        try:
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

# 主程序运行
if __name__ == "__main__":
    root = tk.Tk()
    app = RandomImageViewer(root)
    root.mainloop()
