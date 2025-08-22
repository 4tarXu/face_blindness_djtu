#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装脚本 - 自动安装学生照片抓取工具所需的依赖
"""

import subprocess
import sys
import os

def install_package(package):
    """安装单个包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ 成功安装 {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ 安装 {package} 失败")
        return False

def check_chrome_installation():
    """检查Chrome浏览器安装"""
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✓ 找到Chrome浏览器: {path}")
            return True
    
    print("✗ 未找到Chrome浏览器")
    print("请从 https://www.google.com/chrome/ 下载并安装Chrome浏览器")
    return False

def check_chromedriver():
    """检查ChromeDriver安装"""
    try:
        result = subprocess.run(["chromedriver", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ ChromeDriver已安装: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("✗ 未找到ChromeDriver")
    print("请从 https://chromedriver.chromium.org/ 下载对应版本的ChromeDriver")
    print("下载后请将chromedriver添加到系统PATH中")
    return False

def install_requirements():
    """安装所有必需的Python包"""
    packages = [
        "selenium>=4.0.0",
        "requests>=2.25.0",
        "webdriver-manager>=3.8.0"  # 自动管理webdriver
    ]
    
    print("正在安装Python依赖包...")
    all_success = True
    
    for package in packages:
        if not install_package(package):
            all_success = False
    
    return all_success

def create_directories():
    """创建必要的目录"""
    directories = ["student_photos", "logs"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ 创建目录: {directory}")

def main():
    """主安装流程"""
    print("=== 学生照片抓取工具安装程序 ===\n")
    
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("✗ 需要Python 3.6或更高版本")
        return
    print(f"✓ Python版本: {sys.version}")
    
    # 检查Chrome
    chrome_ok = check_chrome_installation()
    
    # 检查ChromeDriver
    chromedriver_ok = check_chromedriver()
    
    # 安装Python包
    packages_ok = install_requirements()
    
    # 创建目录
    create_directories()
    
    print("\n=== 安装结果 ===")
    if chrome_ok and packages_ok:
        print("✓ 基本安装完成！")
        print("\n下一步：")
        print("1. 如果ChromeDriver未安装，请手动下载并配置")
        print("2. 运行: python student_photo_scraper.py")
    else:
        print("✗ 安装未完成，请解决上述问题")
        
    if not chromedriver_ok:
        print("\nChromeDriver安装建议：")
        print("方法1: 使用webdriver-manager（推荐）")
        print("   已安装webdriver-manager，脚本会自动下载匹配的ChromeDriver")
        print("方法2: 手动安装")
        print("   访问: https://chromedriver.chromium.org/")
        print("   下载与Chrome版本匹配的ChromeDriver")
        print("   将chromedriver文件放在:/usr/local/bin/ 或其他PATH目录")

if __name__ == "__main__":
    main()