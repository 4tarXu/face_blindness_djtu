#!/bin/bash
# 学生照片抓取工具启动脚本

echo "=== 学生照片抽认卡系统 ==="
echo "正在检查环境..."

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python 3.6或更高版本"
    echo "下载地址: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python3已安装"

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ 未找到pip3，请安装pip"
    exit 1
fi

echo "✅ pip3已安装"

# 安装依赖
echo "正在安装依赖包..."
pip3 install selenium requests webdriver-manager

# 创建目录
mkdir -p student_photos logs

echo ""
echo "🎉 环境准备完成！"
echo ""
echo "请选择运行方式："
echo "1) 增强版（推荐）- 自动管理ChromeDriver"
echo "2) 基础版 - 需要手动安装ChromeDriver"
echo ""

read -p "请选择 (1/2): " choice

case $choice in
    1)
        echo "启动增强版..."
        python3 student_photo_scraper_enhanced.py
        ;;
    2)
        echo "启动基础版..."
        python3 student_photo_scraper.py
        ;;
    *)
        echo "无效选择，启动增强版..."
        python3 student_photo_scraper_enhanced.py
        ;;
esac