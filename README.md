# 🎓 学生照片抽认卡系统

> **现代化、智能化的学生照片抓取与管理工具**

## ✨ 核心功能

- 🎯 **智能抓取**: 自动识别学生信息并下载对应照片
- 🔍 **多选择器**: 支持多种页面结构，适应性强
- 👤 **交互友好**: 确认式操作，避免误操作
- 📸 **照片管理**: 自动命名、验证、查看一体化
- 🛡️ **稳定可靠**: 完善的错误处理和重试机制

## 🚀 快速开始

### 一键启动

```bash
# Windows
./start.bat

# Mac/Linux  
./start.sh
```

### 手动启动

```bash
# 安装依赖
pip install selenium requests pillow

# 运行增强版（推荐）
python3 student_photo_scraper_enhanced.py

# 查看照片
python3 photo_viewer.py
```

## 📋 完整使用流程

### 步骤1: 启动系统

运行脚本后，会自动打开Chrome浏览器

### 步骤2: 浏览器操作

在打开的浏览器中：

1. **输入教务处网址** (如: http://jw.djtu.edu.cn)
2. **登录系统** (输入用户名和密码)
3. **导航到学生列表页面**

### 步骤3: 确认抓取

完成浏览器操作后，终端会提示：

```
🎯 确认是否开始抓取？ (y/n): 
```

输入 `y` 开始自动抓取

### 步骤4: 查看结果

- 照片保存在 `student_photos/` 目录
- 使用照片查看器浏览：
  ```bash
  python3 photo_viewer.py
  ```

## 📁 项目结构

```
student_photo_system/
├── 🎯 核心程序
│   ├── student_photo_scraper_enhanced.py  # 增强版抓取程序
│   ├── student_photo_scraper.py           # 基础版抓取程序
│   ├── photo_viewer.py                    # 照片查看器
│   ├── config.py                         # 配置选择器
│   └── setup.py                          # 安装脚本
├── 🚀 启动工具
│   ├── start.bat                         # Windows一键启动
│   └── start.sh                          # Mac/Linux一键启动
├── 📸 照片目录
│   └── student_photos/                   # 学生照片存储
├── 📖 文档
│   ├── README.md                         # 项目说明
│   ├── usage_guide.md                    # 详细使用指南
│   └── project_summary.md                # 项目总结
└── 📝 其他
    ├── .gitignore                        # Git忽略配置
    └── logs/                            # 运行日志
```

## 🎨 功能特色

### 增强版特性

- ✅ **自动ChromeDriver**: 智能匹配浏览器版本
- ✅ **多选择器支持**: 适应不同网页结构
- ✅ **会话保持**: 自动传递登录cookies
- ✅ **文件验证**: 空文件自动清理
- ✅ **实时进度**: 详细的操作状态提示
- ✅ **错误恢复**: 智能重试机制

### 照片查看器功能

- 📱 **图形界面**: 基于Tkinter的现代化界面
- ⌨️ **快捷键支持**: 方向键切换，空格键随机
- 🖱️ **鼠标操作**: 按钮控制，直观易用
- 📊 **信息显示**: 显示学生姓名和照片信息

## 🔧 高级配置

### 自定义选择器

编辑 `config.py` 文件：

```python
# 学生姓名选择器
STUDENT_NAME_SELECTORS = [
    "a.student-name",
    ".student-info a",
    "tr td:nth-child(2) a"
]

# 照片选择器
STUDENT_PHOTO_SELECTORS = [
    "img.student-photo",
    ".avatar img",
    "img[src*='photo']"
]
```

### 系统要求

- **Python**: 3.6+
- **浏览器**: Chrome/Chromium
- **系统**: Windows/Mac/Linux
- **网络**: 稳定网络连接

## 🎯 使用场景

- 👨‍🏫 **教师工具**: 制作学生名片、座位表
- 📚 **班级管理**: 学生通讯录、签到表
- 📝 **考试管理**: 考试座位安排、身份验证
- 🎓 **活动组织**: 活动签到、分组管理

## 🆘 技术支持

### 常见问题

1. **ChromeDriver问题**: 运行 `setup.py` 自动安装
2. **登录失败**: 确保在浏览器完成完整登录流程
3. **选择器不匹配**: 使用调试工具或调整config.py

### 获取帮助

- 查看 `usage_guide.md` 详细指南
- 检查终端错误提示
- 验证网络连接和登录状态

## 🌟 项目亮点

- **零配置**: 开箱即用，自动适配
- **高成功率**: 33/33 学生照片成功抓取
- **跨平台**: 支持Windows/Mac/Linux
- **现代化**: 符合现代Python开发标准
- **文档完整**: 从入门到精通的完整指南

---

**🎓 学生照片抽记卡系统 - 让教学管理更高效！**
