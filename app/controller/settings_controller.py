import configparser
import json
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

from app.init_var import InitVar


class SettingsController:
    def __init__(self, view):
        self._view = view
        self.root = view.root

        # 读取配置文件
        self.config = None
        self.config_file = InitVar.CONFIG_FILE
        self.default_read_dir = ''
        self.default_save_dir = ''
        self.read_config()

        # 设置最爱配置文件
        self.favorite_config = None
        self.favorite_config_file = InitVar.LIKE_CONFIG_FILE
        self.favorites = []
        self.read_favorite_config()

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
            bg="#333333",
            fg="white",
            activebackground="#555555",
            activeforeground="white",
            width=10,
            height=2
        )
        reset_button.pack(side=tk.LEFT, padx=10)

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

        # 如果配置文件中有默认读取目录，则使用，否则弹出选择目录
        if not (InitVar.image_dir and os.path.isdir(InitVar.image_dir)):
            InitVar.image_dir = filedialog.askdirectory(title="请选择图片所在的文件夹")
            if not InitVar.image_dir:
                messagebox.showerror("错误", "未选择任何文件夹")
                # 关闭程序
                sys.exit(0)
            return
        else:
            InitVar.image_dir = self.default_read_dir
            InitVar.default_read_dir = self.default_read_dir
            InitVar.default_save_dir = self.default_save_dir

    def write_config(self):
        """
        将配置写入配置文件
        """
        InitVar.default_read_dir = self.default_read_dir
        InitVar.default_save_dir = self.default_save_dir
        self.config['Settings'] = {
            'read_dir': self.default_read_dir,
            'save_dir': self.default_save_dir,
        }
        with open(self.config_file, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)

    def read_favorite_config(self):
        """
        读取配置文件，如果存在，则加载默认读取目录和保存目录
        """
        self.favorite_config_file = os.path.join(InitVar.image_dir, InitVar.LIKE_CONFIG_FILE)
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
        InitVar.favorites = self.favorites

    def write_favorite_config(self):
        """
        将配置写入配置文件
        """
        self.favorite_config['Settings'] = {
            'favorites': json.dumps(self.favorites)
        }
        with open(self.favorite_config_file, 'w', encoding='utf-8') as f:
            self.favorite_config.write(f)

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

    def browse_directory(self, entry_widget):
        """
        打开目录选择对话框，并将选择的目录路径写入指定的Entry组件
        """
        directory = filedialog.askdirectory()
        if directory:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, directory)
