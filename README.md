# 学生照片抽认卡系统 - 照片抓取工具

## 功能说明
这个工具可以帮助您从教务处网站自动抓取学生照片，并用学生姓名命名保存，用于制作照片抽认卡。

## 使用步骤

### 1. 环境准备
确保已安装以下软件：
- Python 3.6 或更高版本
- Chrome 浏览器
- ChromeDriver（与Chrome版本匹配）

### 2. 安装依赖
打开终端，运行以下命令：
```bash
pip install selenium requests
```

### 3. 运行脚本
```bash
python student_photo_scraper.py
```

### 4. 操作流程
1. 脚本会打开Chrome浏览器
2. **手动操作**：在浏览器中登录教务处网站
3. **手动操作**：导航到学生列表页面
4. 回到终端，按回车键开始自动抓取
5. 脚本会自动点击每个学生姓名，进入详情页下载照片
6. 照片将保存在 `student_photos/` 目录下

## 文件结构
```
student_photo_scraper.py  # 主抓取脚本
config.py                 # 配置文件（可调整选择器）
README.md                 # 使用说明
student_photos/           # 照片保存目录（自动创建）
```

## 自定义配置
如果网页结构与预期不同，请编辑 `config.py` 文件，调整选择器：
- `STUDENT_NAME_SELECTORS`: 学生姓名链接的选择器
- `STUDENT_PHOTO_SELECTORS`: 学生照片的选择器
- `NEXT_PAGE_SELECTORS`: 下一页按钮的选择器

## 常见问题

### Q: 找不到学生列表
A: 请检查是否已正确登录并导航到学生列表页面

### Q: 下载的照片不正确
A: 请检查 `config.py` 中的照片选择器是否正确匹配网页结构

### Q: 脚本运行缓慢
A: 可以在 `config.py` 中调整等待时间，或检查网络连接

### Q: 文件名乱码
A: 脚本会自动清理文件名中的特殊字符，确保兼容性

## 技术支持
如果遇到问题，可以：
1. 检查浏览器是否已正确安装ChromeDriver
2. 查看终端输出的错误信息
3. 根据实际情况调整 `config.py` 中的选择器