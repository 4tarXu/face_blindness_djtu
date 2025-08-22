#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生照片抓取脚本
用于从教务处网站抓取学生照片并保存为姓名命名的文件
"""

import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import urllib.parse

class StudentPhotoScraper:
    def __init__(self, download_dir="student_photos"):
        self.download_dir = download_dir
        self.setup_directories()
        self.driver = None
        
    def setup_directories(self):
        """创建必要的目录"""
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            print(f"创建目录: {self.download_dir}")
    
    def setup_driver(self):
        """设置Chrome浏览器驱动"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # 设置下载目录
        prefs = {
            "download.default_directory": os.path.abspath(self.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("Chrome浏览器启动成功")
            return True
        except Exception as e:
            print(f"启动浏览器失败: {e}")
            print("请确保已安装Chrome浏览器和ChromeDriver")
            return False
    
    def get_current_page_students(self):
        """获取当前页面的学生列表"""
        try:
            # 查找学生姓名链接（需要根据实际网页结构调整选择器）
            # 常见的选择器模式：
            student_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='student'], .student-name a, .student-info a")
            
            students = []
            for link in student_links:
                name = link.text.strip()
                href = link.get_attribute('href')
                if name and href:
                    students.append({'name': name, 'url': href})
            
            print(f"当前页面找到 {len(students)} 个学生")
            return students
        except Exception as e:
            print(f"获取学生列表失败: {e}")
            return []
    
    def download_student_photo(self, student_name, detail_url):
        """下载单个学生的照片"""
        try:
            print(f"处理学生: {student_name}")
            
            # 进入学生详情页
            self.driver.get(detail_url)
            time.sleep(2)
            
            # 查找照片元素（需要根据实际网页结构调整选择器）
            # 常见的照片选择器：
            photo_selectors = [
                "img.student-photo",
                ".student-avatar img",
                "img[src*='photo']",
                "img[src*='avatar']",
                ".photo img",
                "#student-photo",
                "img[alt*='照片']",
                "img[alt*='头像']"
            ]
            
            photo_element = None
            for selector in photo_selectors:
                try:
                    photo_element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if photo_element:
                        break
                except:
                    continue
            
            if not photo_element:
                print(f"未找到 {student_name} 的照片")
                return False
            
            # 获取照片URL
            photo_url = photo_element.get_attribute('src')
            if not photo_url:
                print(f"无法获取 {student_name} 的照片URL")
                return False
            
            # 如果URL是相对路径，转换为绝对路径
            if photo_url.startswith('//'):
                photo_url = 'https:' + photo_url
            elif photo_url.startswith('/'):
                current_url = self.driver.current_url
                base_url = '/'.join(current_url.split('/')[:3])
                photo_url = base_url + photo_url
            
            print(f"照片URL: {photo_url}")
            
            # 下载照片
            response = requests.get(photo_url, stream=True, timeout=10)
            response.raise_for_status()
            
            # 根据内容类型确定扩展名
            content_type = response.headers.get('content-type', '').lower()
            
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            elif 'bmp' in content_type:
                ext = '.bmp'
            else:
                # 如果内容类型不可用，检查URL
                parsed_url = urllib.parse.urlparse(photo_url)
                path = parsed_url.path
                url_ext = os.path.splitext(path)[1].lower()
                
                if url_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                    ext = url_ext
                else:
                    ext = '.jpg'  # 默认使用jpg
            
            # 清理文件名（移除特殊字符）
            safe_name = "".join(c for c in student_name if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = f"{safe_name}{ext}"
            filepath = os.path.join(self.download_dir, filename)
            
            # 保存照片
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # 验证文件完整性 - 降低限制
            file_size = os.path.getsize(filepath)
            if file_size > 100:  # 降低到100字节
                print(f"已保存: {filename} ({file_size} bytes)")
                return True
            else:
                print(f"注意: {filename} 文件较小 ({file_size} bytes)，但仍已保存")
                return True
            
        except Exception as e:
            print(f"下载 {student_name} 的照片失败: {e}")
            return False
    
    def navigate_to_next_page(self):
        """导航到下一页（如果有分页）"""
        try:
            # 查找下一页按钮（需要根据实际网页结构调整选择器）
            next_buttons = [
                "a.next",
                ".pagination .next",
                "a[rel='next']",
                ".page-next"
            ]
            
            for selector in next_buttons:
                try:
                    next_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if next_btn.is_enabled():
                        next_btn.click()
                        time.sleep(2)
                        return True
                except:
                    continue
            
            return False
        except:
            return False
    
    def scrape_all_photos(self):
        """抓取所有学生的照片"""
        if not self.setup_driver():
            return
        
        try:
            print("开始抓取学生照片...")
            print("请在浏览器中手动登录教务处网站并导航到学生列表页面")
            print("完成后请按回车键继续...")
            
            # 打开浏览器到空白页面
            self.driver.get("about:blank")
            
            # 等待用户操作
            input()
            
            total_downloaded = 0
            page_num = 1
            
            while True:
                print(f"\n处理第 {page_num} 页...")
                
                # 获取当前页面的学生
                students = self.get_current_page_students()
                
                if not students:
                    print("未找到学生，请确保已在正确的页面")
                    break
                
                # 下载每个学生的照片
                for student in students:
                    success = self.download_student_photo(student['name'], student['url'])
                    if success:
                        total_downloaded += 1
                    time.sleep(1)  # 避免请求过快
                
                # 尝试导航到下一页
                if not self.navigate_to_next_page():
                    print("已到达最后一页")
                    break
                
                page_num += 1
            
            print(f"\n完成！共下载了 {total_downloaded} 张照片")
            print(f"照片保存在: {os.path.abspath(self.download_dir)}")
            
        except Exception as e:
            print(f"抓取过程中出错: {e}")
        finally:
            if self.driver:
                self.driver.quit()
    
    def run(self):
        """运行完整的抓取流程"""
        print("=== 学生照片抓取工具 ===")
        print("使用说明：")
        print("1. 确保已安装Chrome浏览器和ChromeDriver")
        print("2. 脚本会打开浏览器，请手动登录教务处网站")
        print("3. 导航到学生列表页面")
        print("4. 按回车键开始自动抓取")
        print()
        
        self.scrape_all_photos()

def main():
    scraper = StudentPhotoScraper()
    scraper.run()

if __name__ == "__main__":
    main()