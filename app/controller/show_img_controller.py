# 导入必要的库
import os
import random
import threading
import time
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk

from app.controller import menu_controller
from app.init_var import InitVar


class ShowImgController:
    def __init__(self, view):
        self.view = view
        self.root = view.root

        # 初始化变量
        self.options = InitVar.options  # 配置文件中的选项
        self.all_image_files = []  # 所有图片文件列表
        self.remaining_images = []  # 剩余未展示的图片列表
        self.show_list = []  # 自适应适配完成后的图片列表
        self.photo_images = []  # Tkinter显示的图片对象
        self.total_size = 0  # 总大小（字节）
        self.image_size_mb = {}  # 每张图片的大小（MB）

        # 设置图片目录到成员变量
        self.image_dir = InitVar.image_dir

    def display_images(self):
        """
            选择8张未展示过的图片并显示在界面上，排列为4列2行
            如果所有图片都已展示，则提示用户并重置展示列表
        """
        # 禁用按钮
        self.view.button.config(state=tk.DISABLED)

        # 检查是否还有剩余的图片可以展示
        if not self.remaining_images:
            messagebox.showinfo("提示", "所有图片都已展示完毕，即将重置展示列表。")
            self.remaining_images = self.all_image_files.copy()

        # 选择图片
        self.count_img_list()
        # 获取展示图片
        selected = self.show_list

        # 获取屏幕分辨率, 以适应不同图片大小
        screen_width = self.root.winfo_width()
        screen_height = self.root.winfo_height()
        screen_width = screen_width // 4
        screen_height = screen_height // 3

        # 清空之前的图片
        for widget in self.view.view.images_frame.winfo_children():
            widget.destroy()
        for widget in self.view.view.images_frame1.winfo_children():
            widget.destroy()

        for file in selected:
            file_path = os.path.join(self.image_dir, file[0])
            try:
                # 打开图片并调整大小
                img = Image.open(file_path)
                # 获取分辨率
                width, height = img.size
                # 设置图片最大尺寸
                max_size = (screen_width * file[2], screen_height)
                img.thumbnail(max_size, resample=Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.photo_images.append(photo)  # 保持引用，防止图片被垃圾回收

                row = file[1][0]
                column = file[1][1]

                if row == 0:
                    # 创建图片和大小标签的容器
                    container = tk.Frame(self.view.view.images_frame, bg="black")
                    container.grid(row=0, column=column, padx=0, pady=0)
                else:
                    # 创建图片和大小标签的容器
                    container = tk.Frame(self.view.view.images_frame1, bg="black")
                    container.grid(row=0, column=column, padx=0, pady=0)

                # 创建图片标签
                img_label = tk.Label(container, image=photo, bg="black", cursor="hand2")
                img_label.pack()

                # 显示图片大小
                size_label = tk.Label(
                    container,
                    text=f"{self.image_size_mb[file[0]]} MB - {width} x {height}",
                    fg="white",
                    bg="black",
                    font=("微软雅黑", 10)
                )
                if self.options == InitVar.OPTIONS_LIST[0]:  # 随机排序
                    # 读取文件名, 并且限制在16位以内, 如果超出, 则省略中间部分为...
                    file_name = file[0]
                    if len(file_name) > 16:
                        file_name = file_name[:8] + "..." + file_name[-8:]
                    # 显示图片的文件名
                    size_label.config(text=f'{file_name}')

                elif self.options == InitVar.OPTIONS_LIST[1] or self.options == InitVar.OPTIONS_LIST[2]:  # 新 -> 旧
                    # 显示图片的日期信息
                    getmtime = os.path.getmtime(os.path.join(self.image_dir, file[0]))
                    size_label.config(text=f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(getmtime))}')

                size_label.pack(pady=1)

                # 绑定左键点击事件打开图片
                img_label.bind("<Button-1>", lambda e, path=file_path: menu_controller.open_image(path))

                # 绑定右键点击事件显示菜单
                img_label.bind("<Button-3>", lambda e, path=file_path: self.show_context_menu(e, path))

            except Exception as e:
                print(f"无法打开图片 {file}: {e}")
        # 更新按钮文本
        self.view.button.config(text=f"下一组 - 剩{len(self.remaining_images)}张")

        # 完成后启用按钮
        def open_btn():
            self.view.button.config(state=tk.NORMAL)
            self.view.is_btn = False

        # 新建线程, 延迟执行
        threading.Timer(0.1, open_btn).start()

    def show_context_menu(self, event, path):
        """
        显示右键菜单，包含“另存为”和“打开文件所在位置”选项
        """
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="另存为", command=lambda: menu_controller.save_as(path))
        menu.add_command(label="复制图片", command=lambda: menu_controller.copy_image(path))
        menu.add_command(label="打开文件所在位置", command=lambda: menu_controller.open_file_location(path))
        menu.add_command(label="移出图片", command=lambda: menu_controller.remove_image(path))  # 新增“移出图片”选项
        # 添加空行
        menu.add_separator()
        if os.path.relpath(path, self.image_dir) in InitVar.favorites:
            menu.add_command(label="取消最爱", command=lambda: menu_controller.cancel_favorite(path))
        else:
            menu.add_command(label="设为最爱", command=lambda: menu_controller.set_as_favorite(path))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def count_img_list(self):
        # 确定本次要展示的图片数
        num_images_to_display = min(8, len(self.remaining_images))

        # 顺序选择未展示的图片
        selected = self.remaining_images[:num_images_to_display]

        self.photo_images.clear()

        # 计算出所有图片宽高的比值, 比值最高的在前
        raty_sort_list = []
        for index, file in enumerate(selected):
            file_path = os.path.join(self.image_dir, file)
            try:
                with Image.open(file_path) as img:
                    img.verify()
                # img = Image.open(file_path)
                img_width, img_height = img.size
                ratio = img_width / img_height
                # print(f'图片分辨率比值: {ratio}')
                raty_sort_list.append((file, ratio))
            except Exception as e:
                # 移出错误图片
                self.remaining_images.remove(file)
                print(f"Error opening image {file_path}: {e}")
                continue

        raty_sort_list.sort(key=lambda x: x[1], reverse=True)

        # print(raty_sort_list)
        index_list = [(0, 1), (1, 1), (0, 3), (1, 3), (0, 2), (1, 2), (0, 4), (1, 4)]
        self.show_list = []
        matrix_list = []
        no1 = 0
        no2 = 0
        for index in range(len(raty_sort_list)):
            matrix_list.append([raty_sort_list[index][0], index_list[index], raty_sort_list[index][1]])

        # 判断每行比值总和是否超过上限, 超过则跳过
        for i in matrix_list:
            if i[1][0] == 0:
                no1 += i[2]
                # print(f'比值1总和{no1}')
                if no1 > 5:
                    continue
            else:
                no2 += i[2]
                # print(f'比值2总和{no2}')
                if no2 > 5:
                    continue
            self.show_list.append(i)
        # 从剩余图片列表中移除已展示的图片
        for file in self.show_list:
            self.remaining_images.remove(file[0])
        # print(f"展示列表:{self.show_list}")

    def load_images(self):
        """
        读取指定目录下的所有图片文件，并计算总大小
        """
        # 清空之前的图片列表
        self.all_image_files.clear()
        print('开始读取图片列表')

        # 判断调用对象是否有is_like属性
        if hasattr(self.view, 'is_like') and self.view.is_like: # 如果喜欢模式, 则直接载入喜欢的图片
            self.all_image_files = InitVar.favorites.copy()
        else: # 否则载入所有图片
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

        # 计算总大小和每张图片的大小
        self.total_size = 0
        self.image_size_mb = {}
        for file in self.all_image_files:
            file_path = os.path.join(self.image_dir, file)
            size = os.path.getsize(file_path)
            self.total_size += size
            size_mb = round(size / (1024 * 1024), 2)
            self.image_size_mb[file] = size_mb

        # 根据选项排序所有图片
        self.options = InitVar.options
        if self.options == InitVar.OPTIONS_LIST[0]:  # 随机排序
            random.shuffle(self.all_image_files)
        elif self.options == InitVar.OPTIONS_LIST[1]:  # 新 -> 旧
            # 读取所有图片的时间, 新的在前
            self.all_image_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.image_dir, x)), reverse=True)
        elif self.options == InitVar.OPTIONS_LIST[2]:  # 旧 -> 新
            # 读取所有图片的时间, 旧的在前
            self.all_image_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.image_dir, x)))
        elif self.options == InitVar.OPTIONS_LIST[3]:  # 大 -> 小
            # 读取所有图片的大小, 大的在前
            self.all_image_files.sort(key=lambda x: self.image_size_mb[x])
        elif self.options == InitVar.OPTIONS_LIST[4]:  # 小 -> 大
            # 读取所有图片的大小, 小的在前
            self.all_image_files.sort(key=lambda x: self.image_size_mb[x], reverse=True)

        # 初始化剩余图片列表为所有图片
        self.remaining_images = self.all_image_files.copy()

        # 更新按钮文本
        if hasattr(self.view, 'is_like') and self.view.is_like:
            self.view.button.config(text=f"展示最爱 - 共{len(self.all_image_files)}张")
        else:
            self.view.button.config(text=f"展示全部 - 共{len(self.all_image_files)}张")
        # 更新窗口标题
        total_size_gb = round(self.total_size / (1024 ** 3), 2)  # 转换为GB
        file_count = len(self.all_image_files)
        self.root.title(f"{InitVar.WINDOW_TITLE} - 已读取 {file_count} 张 - {total_size_gb} GB -- By 羡林i")
