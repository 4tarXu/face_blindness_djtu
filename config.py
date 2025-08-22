#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件 - 根据实际网页结构调整选择器
"""

class Config:
    # 学生姓名链接的选择器
    STUDENT_NAME_SELECTORS = [
        "a[href*='student']",           # 包含student的链接
        ".student-name a",              # class为student-name下的链接
        ".student-info a",              # class为student-info下的链接
        "a.student-link",               # class为student-link的链接
        "table tr td a",                # 表格中的链接
        ".list-item a",                 # 列表项中的链接
    ]
    
    # 学生照片的选择器
    STUDENT_PHOTO_SELECTORS = [
        "img.student-photo",            # class为student-photo的图片
        ".student-avatar img",          # class为student-avatar下的图片
        "img[src*='photo']",           # src包含photo的图片
        "img[src*='avatar']",          # src包含avatar的图片
        ".photo img",                   # class为photo下的图片
        "#student-photo",               # id为student-photo的图片
        "img[alt*='照片']",              # alt包含照片的图片
        "img[alt*='头像']",              # alt包含头像的图片
        ".profile-image img",           # class为profile-image下的图片
        "img.profile-photo",            # class为profile-photo的图片
    ]
    
    # 下一页按钮的选择器
    NEXT_PAGE_SELECTORS = [
        "a.next",                       # class为next的链接
        ".pagination .next",            # class为pagination下的next
        "a[rel='next']",               # rel属性为next的链接
        ".page-next",                  # class为page-next的元素
        "a:contains('下一页')",          # 文字包含下一页的链接
        ".pagination a:last-child",     # 分页中最后一个链接
    ]
    
    # 等待时间设置（秒）
    WAIT_TIME = {
        'page_load': 2,                 # 页面加载等待时间
        'photo_load': 3,                # 照片加载等待时间
        'between_requests': 1,          # 请求间隔时间
    }
    
    # 文件设置
    FILE_SETTINGS = {
        'download_dir': 'student_photos',  # 下载目录
        'default_format': 'jpg',            # 默认图片格式
        'max_filename_length': 50,          # 文件名最大长度
    }
    
    # 浏览器设置
    BROWSER_SETTINGS = {
        'window_size': '1920,1080',         # 浏览器窗口大小
        'headless': False,                  # 是否无头模式运行
        'timeout': 10,                      # 页面加载超时时间
    }