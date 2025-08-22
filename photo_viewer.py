#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
照片查看器 - 查看下载的学生照片
"""

import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import glob

class PhotoViewer:
    def __init__(self, photo_dir="student_photos"):
        self.photo_dir = photo_dir
        self.photos = []
        self.current_index = 0
        
        self.load_photos()
        self.setup_gui()
    
    def load_photos(self):
        """加载所有照片"""
        if not os.path.exists(self.photo_dir):
            print(f"目录 {self.photo_dir} 不存在")
            return
        
        # 支持的图片格式
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']
        for ext in extensions:
            pattern = os.path.join(self.photo_dir, ext)
            self.photos.extend(glob.glob(pattern))
        
        self.photos.sort()
        print(f"找到 {len(self.photos)} 张照片")
    
    def setup_gui(self):
        """设置GUI界面"""
        self.root = tk.Tk()
        self.root.title("学生照片抽认卡")
        self.root.geometry("800x600")
        
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 照片显示区域
        self.photo_label = ttk.Label(main_frame)
        self.photo_label.pack(fill=tk.BOTH, expand=True)
        
        # 信息标签
        self.info_label = ttk.Label(main_frame, text="", font=("Arial", 12))
        self.info_label.pack(pady=10)
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="上一张", command=self.prev_photo).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="下一张", command=self.next_photo).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="随机", command=self.random_photo).pack(side=tk.LEFT, padx=5)
        
        # 键盘绑定
        self.root.bind('<Left>', lambda e: self.prev_photo())
        self.root.bind('<Right>', lambda e: self.next_photo())
        self.root.bind('<space>', lambda e: self.random_photo())
        
        # 显示第一张照片
        if self.photos:
            self.show_photo(0)
        else:
            self.info_label.config(text="未找到照片，请先运行抓取脚本")
    
    def show_photo(self, index):
        """显示指定索引的照片"""
        if not self.photos or index < 0 or index >= len(self.photos):
            return
        
        try:
            photo_path = self.photos[index]
            
            # 打开并调整图片大小
            image = Image.open(photo_path)
            
            # 获取窗口大小
            window_width = self.root.winfo_width() - 40
            window_height = self.root.winfo_height() - 150
            
            if window_width > 1 and window_height > 1:
                # 计算缩放比例
                image.thumbnail((window_width, window_height), Image.Resampling.LANCZOS)
            
            # 转换为Tkinter格式
            photo = ImageTk.PhotoImage(image)
            
            # 更新标签
            self.photo_label.config(image=photo)
            self.photo_label.image = photo  # 防止垃圾回收
            
            # 更新信息
            filename = os.path.basename(photo_path)
            name = os.path.splitext(filename)[0]
            self.info_label.config(text=f"{index + 1}/{len(self.photos)} - {name}")
            
            self.current_index = index
            
        except Exception as e:
            print(f"显示照片失败: {e}")
            self.info_label.config(text=f"无法加载照片: {os.path.basename(self.photos[index])}")
    
    def next_photo(self):
        """下一张照片"""
        if self.photos:
            next_index = (self.current_index + 1) % len(self.photos)
            self.show_photo(next_index)
    
    def prev_photo(self):
        """上一张照片"""
        if self.photos:
            prev_index = (self.current_index - 1) % len(self.photos)
            self.show_photo(prev_index)
    
    def random_photo(self):
        """随机显示照片"""
        if self.photos:
            import random
            random_index = random.randint(0, len(self.photos) - 1)
            self.show_photo(random_index)
    
    def run(self):
        """运行查看器"""
        if not self.photos:
            print("请先运行照片抓取脚本下载照片")
            return
        
        print("照片查看器已启动")
        print("使用说明：")
        print("- 左右箭头键：切换照片")
        print("- 空格键：随机显示")
        print("- 窗口按钮：导航控制")
        
        self.root.mainloop()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="学生照片查看器")
    parser.add_argument("--dir", default="student_photos", help="照片目录")
    
    args = parser.parse_args()
    
    try:
        viewer = PhotoViewer(args.dir)
        viewer.run()
    except ImportError as e:
        print(f"需要安装Pillow库：pip install Pillow")
        print("或使用命令行查看：")
        print("ls student_photos/")

if __name__ == "__main__":
    main()