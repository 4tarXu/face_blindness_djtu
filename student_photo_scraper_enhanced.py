#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版学生照片抓取脚本
支持自动管理ChromeDriver，更智能的元素选择
"""

import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import urllib.parse
import re
from typing import List, Dict, Optional

class EnhancedStudentPhotoScraper:
    def __init__(self, download_dir="student_photos"):
        self.download_dir = os.path.abspath(download_dir)
        self.setup_directories()
        self.driver = None
        self.session = requests.Session()
        
    def setup_directories(self):
        """创建必要的目录"""
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            print(f"✓ 创建目录: {self.download_dir}")
    
    def setup_driver(self):
        """设置Chrome浏览器驱动（自动管理ChromeDriver）"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 设置下载目录
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            # 使用webdriver-manager自动管理ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✓ Chrome浏览器启动成功")
            return True
        except Exception as e:
            print(f"✗ 启动浏览器失败: {e}")
            return False
    
    def find_elements_with_multiple_selectors(self, selectors: List[str], timeout: int = 10) -> List:
        """使用多个选择器查找元素"""
        for selector in selectors:
            try:
                elements = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                )
                if elements:
                    print(f"✓ 找到元素: {selector}")
                    return elements
            except:
                continue
        return []
    
    def get_students_from_page(self) -> List[Dict[str, str]]:
        """从当前页面获取学生列表"""
        selectors = [
            "a[href*='student']",
            ".student-name a",
            ".student-info a",
            "a.student-link",
            "table tbody tr td a",
            ".list-item a",
            ".name-link",
            "a[href*='detail']",
            "a[href*='info']",
        ]
        
        students = []
        elements = self.find_elements_with_multiple_selectors(selectors)
        
        for element in elements:
            try:
                name = element.text.strip()
                href = element.get_attribute('href')
                
                if name and href and len(name) >= 2:  # 过滤掉过短的姓名
                    # 确保URL是完整的
                    if href.startswith('//'):
                        href = 'https:' + href
                    elif href.startswith('/'):
                        current_url = self.driver.current_url
                        base_url = '/'.join(current_url.split('/')[:3])
                        href = base_url + href
                    
                    students.append({'name': name, 'url': href})
            except Exception as e:
                continue
        
        print(f"✓ 当前页面找到 {len(students)} 个学生")
        return students
    
    def find_photo_element(self) -> Optional[str]:
        """查找并返回照片URL"""
        selectors = [
            "img.student-photo",
            ".student-avatar img",
            "img[src*='photo']",
            "img[src*='avatar']",
            ".photo img",
            "#student-photo",
            "img[alt*='照片']",
            "img[alt*='头像']",
            ".profile-image img",
            "img.profile-photo",
            ".id-photo img",
            "img.id-card",
            ".student-card img",
        ]
        
        for selector in selectors:
            try:
                img_element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                if img_element:
                    src = img_element.get_attribute('src')
                    if src and not src.startswith('data:'):  # 排除base64图片
                        return src
            except:
                continue
        
        # 如果没找到特定选择器，尝试查找页面中所有图片
        try:
            all_imgs = self.driver.find_elements(By.TAG_NAME, 'img')
            for img in all_imgs:
                src = img.get_attribute('src')
                if src and any(keyword in src.lower() for keyword in ['photo', 'avatar', 'pic', 'img']):
                    return src
        except:
            pass
        
        return None
    
    def download_photo(self, name: str, photo_url: str) -> bool:
        """下载单张照片"""
        try:
            # 清理文件名
            safe_name = re.sub(r'[^\w\s-]', '', name).strip()
            safe_name = re.sub(r'[-\s]+', '-', safe_name)
            
            # 根据URL确定临时扩展名
            parsed_url = urllib.parse.urlparse(photo_url)
            path = parsed_url.path
            url_ext = os.path.splitext(path)[1].lower()
            if url_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                ext = url_ext
            else:
                ext = '.jpg'
            
            filename = f"{safe_name}{ext}"
            filepath = os.path.join(self.download_dir, filename)
            
            # 避免重复下载
            if os.path.exists(filepath):
                print(f"⚠ 文件已存在，跳过: {filename}")
                return False
            
            # 获取浏览器cookies用于会话保持
            cookies = self.driver.get_cookies()
            session = requests.Session()
            
            # 添加cookies到session
            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'])
            
            # 下载图片
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': self.driver.current_url,
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
            }
            
            print(f"📥 正在下载: {photo_url}")
            response = session.get(photo_url, headers=headers, timeout=15, stream=True)
            response.raise_for_status()
            
            # 验证内容类型
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type:
                print(f"⚠ 跳过非图片内容: {content_type}")
                return False
            
            # 根据实际内容类型重新确定扩展名
            content_type_lower = content_type.lower()
            if 'jpeg' in content_type_lower or 'jpg' in content_type_lower:
                ext = '.jpg'
            elif 'png' in content_type_lower:
                ext = '.png'
            elif 'gif' in content_type_lower:
                ext = '.gif'
            elif 'bmp' in content_type_lower:
                ext = '.bmp'
            
            # 更新文件名
            filename = f"{safe_name}{ext}"
            filepath = os.path.join(self.download_dir, filename)
            
            # 保存文件
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # 确保chunk不为空
                        f.write(chunk)
            
            # 验证文件完整性
            file_size = os.path.getsize(filepath)
            if file_size == 0:
                print(f"✗ 下载失败: 文件为空 ({filename})")
                os.remove(filepath)  # 删除空文件
                return False
            elif file_size < 100:
                print(f"⚠ 图片较小 ({file_size} bytes): {filename}")
                return True
            else:
                print(f"✓ 已保存: {filename} ({file_size} bytes)")
                return True
                
        except requests.exceptions.RequestException as e:
            print(f"✗ 网络错误 {name}: {e}")
            return False
        except Exception as e:
            print(f"✗ 下载失败 {name}: {e}")
            return False
    
    def process_student(self, student: Dict[str, str]) -> bool:
        """处理单个学生"""
        try:
            print(f"\n📋 处理学生: {student['name']}")
            
            # 进入详情页
            self.driver.get(student['url'])
            time.sleep(2)
            
            # 查找照片
            photo_url = self.find_photo_element()
            if not photo_url:
                print(f"⚠ 未找到照片: {student['name']}")
                return False
            
            print(f"📷 找到照片: {photo_url}")
            
            # 添加更多调试信息
            try:
                # 先获取文件大小信息
                response = requests.head(photo_url, timeout=10)
                content_length = response.headers.get('content-length')
                if content_length:
                    print(f"📏 文件大小: {int(content_length)} bytes")
                else:
                    print("📏 无法获取文件大小信息")
            except:
                pass
            
            # 下载照片
            return self.download_photo(student['name'], photo_url)
            
        except Exception as e:
            print(f"✗ 处理失败 {student['name']}: {e}")
            return False
    
    def has_next_page(self) -> bool:
        """检查是否有下一页"""
        selectors = [
            "a.next:not(.disabled)",
            ".pagination .next:not(.disabled)",
            "a[rel='next']:not(.disabled)",
            ".page-next:not(.disabled)",
            "a:contains('下一页'):not(.disabled)",
        ]
        
        for selector in selectors:
            try:
                next_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                if next_btn.is_enabled() and next_btn.is_displayed():
                    next_btn.click()
                    time.sleep(2)
                    return True
            except:
                continue
        
        return False
    
    def scrape_all_photos(self):
        """抓取所有照片"""
        if not self.setup_driver():
            return
        
        try:
            print("\n=== 学生照片抓取工具 ===")
            print("🚀 使用说明：")
            print("1. 脚本会自动下载匹配的ChromeDriver")
            print("2. 浏览器打开后，请：")
            print("   - 输入教务处网址")
            print("   - 登录系统")
            print("   - 导航到学生列表页面")
            print("3. 完成后返回终端确认是否开始")
            print()
            
            # 打开空白页面
            self.driver.get("about:blank")
            
            # 等待用户确认
            while True:
                ready = input("🎯 确认是否开始抓取？ (y/n): ").strip().lower()
                if ready in ['y', 'yes', '是']:
                    break
                elif ready in ['n', 'no', '否']:
                    print("已取消操作")
                    return
                else:
                    print("请输入 y 或 n")
            
            total_processed = 0
            total_downloaded = 0
            page_num = 1
            
            while True:
                print(f"\n📄 处理第 {page_num} 页...")
                
                # 获取当前页面学生
                students = self.get_students_from_page()
                if not students:
                    if page_num == 1:
                        print("⚠ 未找到学生，请确认已在正确页面")
                        break
                    else:
                        print("✓ 所有页面处理完成")
                        break
                
                # 处理每个学生
                for student in students:
                    success = self.process_student(student)
                    if success:
                        total_downloaded += 1
                    total_processed += 1
                    
                    # 避免请求过快
                    time.sleep(1.5)
                
                # 检查下一页
                if not self.has_next_page():
                    print("✓ 已到达最后一页")
                    break
                
                page_num += 1
            
            print(f"\n🎉 任务完成！")
            print(f"📊 总计处理: {total_processed} 个学生")
            print(f"📥 成功下载: {total_downloaded} 张照片")
            print(f"📁 保存目录: {self.download_dir}")
            
        except KeyboardInterrupt:
            print("\n⏹️ 用户中断操作")
        except Exception as e:
            print(f"❌ 运行错误: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                print("✓ 浏览器已关闭")

def main():
    scraper = EnhancedStudentPhotoScraper()
    scraper.scrape_all_photos()

if __name__ == "__main__":
    main()