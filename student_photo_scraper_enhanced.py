#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版学生照片抓取脚本
支持自动管理ChromeDriver，更智能的元素选择
"""

import os
import time
import requests
import json
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
from urllib.parse import urljoin, urlparse

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
        
        # 处理弹出窗口
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])
        
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
    
    def switch_to_new_window(self, original_window: str) -> bool:
        """切换到最新弹出的窗口"""
        try:
            # 等待新窗口打开
            WebDriverWait(self.driver, 15).until(
                lambda driver: len(driver.window_handles) > 1
            )
            
            # 获取所有窗口句柄
            windows = self.driver.window_handles
            
            # 切换到最新的窗口（最后一个）
            if len(windows) > 1:
                latest_window = windows[-1]  # 获取最新的窗口
                if latest_window != original_window:
                    self.driver.switch_to.window(latest_window)
                    print(f"✓ 已切换到最新窗口 (窗口 {len(windows)})")
                    
                    # 等待新窗口页面完全加载
                    WebDriverWait(self.driver, 10).until(
                        lambda driver: driver.execute_script("return document.readyState") == "complete"
                    )
                    time.sleep(2)  # 额外等待确保内容加载
                    return True
            
            return False
        except Exception as e:
            print(f"⚠ 切换窗口失败: {e}")
            return False
    
    def switch_to_latest_window(self) -> str:
        """切换到最新窗口并返回其句柄"""
        try:
            windows = self.driver.window_handles
            if len(windows) > 0:
                latest_window = windows[-1]
                self.driver.switch_to.window(latest_window)
                return latest_window
            return self.driver.current_window_handle
        except:
            return self.driver.current_window_handle
    
    def close_extra_windows(self, original_window: str):
        """关闭多余的窗口，回到原始窗口"""
        try:
            for window in self.driver.window_handles:
                if window != original_window:
                    self.driver.switch_to.window(window)
                    self.driver.close()
            self.driver.switch_to.window(original_window)
        except Exception as e:
            print(f"⚠ 关闭窗口时出错: {e}")
    
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
        
        # 获取当前窗口句柄，用于后续处理
        original_window = self.driver.current_window_handle
        
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
                    
                    # 检查是否是JavaScript链接
                    if href.startswith('javascript:'):
                        # 尝试点击元素打开新窗口
                        try:
                            element.click()
                            time.sleep(2)
                            if len(self.driver.window_handles) > 1:
                                self.switch_to_new_window(original_window)
                                # 获取新窗口的URL
                                new_url = self.driver.current_url
                                students.append({'name': name, 'url': new_url})
                                # 关闭新窗口，回到原始窗口
                                self.close_extra_windows(original_window)
                            else:
                                # 如果没有新窗口，使用原始href
                                students.append({'name': name, 'url': href})
                        except:
                            students.append({'name': name, 'url': href})
                    else:
                        students.append({'name': name, 'url': href})
            except Exception as e:
                continue
        
        print(f"✓ 当前页面找到 {len(students)} 个学生")
        return students
    
    def wait_for_page_load(self, timeout: int = 10):
        """等待页面完全加载"""
        print("⏳ 等待页面加载...")
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            print("✅ 页面加载完成")
            time.sleep(1)  # 减少额外等待
        except:
            print("⚠ 页面加载超时，继续尝试...")
            time.sleep(2)  # 兜底等待
    
    def find_photo_element(self) -> Optional[str]:
        """查找并返回照片URL"""
        print("🔍 开始查找学生照片...")
        
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
            "img[src*='head']",
            "img[src*='face']",
            ".avatar-img",
            "img.avatar",
        ]
        
        # 等待页面加载
        self.wait_for_page_load()
        
        # 调试：打印当前页面信息
        try:
            current_url = self.driver.current_url
            print(f"📍 当前页面URL: {current_url}")
            
            # 检查页面标题
            title = self.driver.title
            print(f"📄 页面标题: {title}")
            
        except Exception as e:
            print(f"⚠ 获取页面信息失败: {e}")
        
        found_imgs = []
        
        # 尝试多个选择器
        print("🔍 尝试标准选择器...")
        for selector in selectors:
            try:
                img_elements = WebDriverWait(self.driver, 3).until(  # 减少等待时间
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                )
                
                for img_element in img_elements:
                    src = img_element.get_attribute('src')
                    if src and not src.startswith('data:'):  # 排除base64图片
                        width = img_element.size.get('width', 0)
                        height = img_element.size.get('height', 0)
                        if width > 50 and height > 50:
                            print(f"✅ 找到照片 (选择器: {selector}): {src}")
                            return src
                        else:
                            found_imgs.append(f"小图片: {src} ({width}x{height})")
            except:
                continue
        
        print("🔍 标准选择器未找到，尝试通用查找...")
        
        # 如果没找到特定选择器，尝试查找页面中所有图片
        try:
            all_imgs = self.driver.find_elements(By.TAG_NAME, "img")
            print(f"📊 页面中找到 {len(all_imgs)} 个图片")
            
            candidate_imgs = []
            for i, img in enumerate(all_imgs):
                try:
                    src = img.get_attribute('src')
                    if src and not src.startswith('data:'):
                        width = img.size.get('width', 0)
                        height = img.size.get('height', 0)
                        is_displayed = img.is_displayed()
                        
                        print(f"   图片{i+1}: {src[:80]}... ({width}x{height}) 显示: {is_displayed}")
                        
                        # 过滤条件
                        if width >= 100 and height >= 100 and is_displayed:
                            # 检查URL是否包含照片相关关键词
                            src_lower = src.lower()
                            if any(keyword in src_lower for keyword in ['photo', 'avatar', 'pic', 'img', 'head', 'face', 'student']):
                                candidate_imgs.append(src)
                                if len(candidate_imgs) == 1:  # 返回第一个匹配的
                                    print(f"✅ 找到候选照片: {src}")
                                    return src
                except Exception as e:
                    print(f"   图片{i+1} 检查失败: {e}")
                    continue
                    
            if candidate_imgs:
                print(f"✅ 使用候选照片: {candidate_imgs[0]}")
                return candidate_imgs[0]
                
        except Exception as e:
            print(f"⚠ 通用查找失败: {e}")
        
        # 最后尝试查找所有可见的图片
        print("🔍 最后尝试查找可见图片...")
        try:
            visible_imgs = []
            all_imgs = self.driver.find_elements(By.TAG_NAME, "img")
            
            for img in all_imgs:
                try:
                    if img.is_displayed():
                        width = img.size.get('width', 0)
                        if width >= 100:
                            src = img.get_attribute('src')
                            if src and not src.startswith('data:'):
                                visible_imgs.append(src)
                                
                except Exception as e:
                    continue
            
            if visible_imgs:
                print(f"✅ 使用可见图片: {visible_imgs[0]}")
                return visible_imgs[0]
            else:
                print("❌ 未找到任何符合条件的图片")
                
        except Exception as e:
            print(f"⚠ 最终查找失败: {e}")
        
        print("⚠ 未找到学生照片")
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
    
    def wait_for_new_window_or_navigation(self, original_window: str, original_url: str, timeout: int = 8) -> bool:
        """等待新窗口或页面导航完成"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # 检查是否有新窗口
                current_windows = self.driver.window_handles
                if len(current_windows) > 1 and current_windows[-1] != original_window:
                    self.driver.switch_to.window(current_windows[-1])
                    print("🔄 已切换到新窗口")
                    return True
                    
                # 检查URL是否改变
                current_url = self.driver.current_url
                if current_url != original_url and not current_url.startswith('about:'):
                    print("🔄 检测到页面导航")
                    return True
                    
                time.sleep(0.5)
            except:
                time.sleep(0.5)
        
        print("⚠ 未检测到窗口变化或页面导航")
        return False

    def process_student(self, student: Dict[str, str]) -> bool:
        """处理单个学生"""
        try:
            original_window = self.driver.current_window_handle
            original_url = self.driver.current_url
            
            print(f"\n📋 处理学生: {student['name']}")
            print(f"🌐 目标URL: {student['url']}")

            # 记录初始状态
            initial_windows = len(self.driver.window_handles)
            print(f"🔗 初始窗口数: {initial_windows}")

            # 根据URL类型选择处理方式
            if student['url'].startswith('javascript:'):
                print("⚡ 执行JavaScript链接...")
                self.driver.execute_script(student['url'])
                
            elif student['url'].startswith('http'):
                # 尝试多种方式处理HTTP链接
                processed = False
                
                # 方法1: 尝试在当前页面查找并点击对应链接
                if not processed:
                    try:
                        # 构建精确和模糊选择器
                        selectors = [
                            f"a[href='{student['url']}']",
                            f"a[href*='{student['url'].split('/')[-1]}']",
                            f"a[title*='{student['name']}']",
                            f"a:contains('{student['name']}')",
                            "a.student-link",
                            "a.detail-link",
                            "a[href*='student']",
                            "a[href*='detail']",
                            "a[target='_blank']",
                            "td a",
                            ".name a"
                        ]
                        
                        for selector in selectors:
                            try:
                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                for element in elements:
                                    if element.is_displayed() and element.is_enabled():
                                        # 验证链接相关性
                                        text = element.text.strip()
                                        href = element.get_attribute('href') or ''
                                        
                                        # 优先匹配姓名
                                        if student['name'] in text:
                                            print(f"🎯 通过姓名匹配点击: {text}")
                                            element.click()
                                            processed = True
                                            break
                                        elif student['url'] in href or href in student['url']:
                                            print(f"🔗 通过URL匹配点击: {selector}")
                                            element.click()
                                            processed = True
                                            break
                                            
                                if processed:
                                    break
                                    
                            except Exception as e:
                                continue
                                
                    except Exception as e:
                        print(f"❌ 方法1失败: {e}")
                
                # 方法2: 直接访问URL（如果方法1失败）
                if not processed:
                    try:
                        print("🔄 直接访问URL...")
                        self.driver.get(student['url'])
                        processed = True
                    except Exception as e:
                        print(f"❌ 直接访问失败: {e}")
                        return False
            
            else:
                # 相对路径或其他情况
                try:
                    full_url = urllib.parse.urljoin(original_url, student['url'])
                    print(f"🔗 处理相对路径: {student['url']} -> {full_url}")
                    self.driver.get(full_url)
                except Exception as e:
                    print(f"❌ 相对路径处理失败: {e}")
                    return False

            # 等待页面变化
            if not self.wait_for_new_window_or_navigation(original_window, original_url):
                print("⚠ 等待超时，继续尝试...")
                time.sleep(2)

            # 确保页面完全加载
            self.wait_for_page_load()
            print(f"📍 当前页面: {self.driver.current_url}")

            # 查找并下载照片
            photo_url = self.find_photo_element()
            download_success = False
            
            if photo_url:
                print(f"📸 找到照片: {photo_url}")
                
                # 检查文件大小
                try:
                    response = requests.head(photo_url, timeout=5)
                    size = response.headers.get('content-length')
                    if size:
                        print(f"📏 文件大小: {int(size)} bytes")
                except:
                    pass
                
                download_success = self.download_photo(student['name'], photo_url)
                if download_success:
                    print(f"✅ 学生 {student['name']} 照片下载完成")
                else:
                    print(f"❌ 学生 {student['name']} 照片下载失败")
            else:
                print("⚠ 未找到学生照片")
                # 提供调试信息
                try:
                    imgs = [img for img in self.driver.find_elements(By.TAG_NAME, "img") 
                           if img.size.get('width', 0) > 50]
                    print(f"📊 找到 {len(imgs)} 个可能的照片")
                    for i, img in enumerate(imgs[:3]):
                        src = img.get_attribute('src') or '无src'
                        alt = img.get_attribute('alt') or '无alt'
                        size = f"{img.size.get('width')}x{img.size.get('height')}"
                        print(f"   图片{i+1}: {src[:60]}... ({size}) alt: {alt}")
                except Exception as e:
                    print(f"❌ 调试信息获取失败: {e}")
                
                print(f"⚠ 学生 {student['name']} 无照片可下载")
                download_success = False

            # 清理并返回原始窗口
            self.close_extra_windows(original_window)
            
            # 明确显示完成状态
            print(f"🏁 学生 {student['name']} 处理完成")
            return download_success

        except Exception as e:
            print(f"❌ 处理学生失败: {student['name']}")
            print(f"   错误: {str(e)}")
            
            # 清理窗口
            try:
                self.close_extra_windows(original_window)
            except:
                pass
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
                
                print(f"📊 本页共找到 {len(students)} 个学生")
                
                # 处理每个学生
                page_downloaded = 0
                for i, student in enumerate(students, 1):
                    print(f"\n📋 正在处理第 {i}/{len(students)} 个学生: {student['name']}")
                    
                    success = self.process_student(student)
                    if success:
                        total_downloaded += 1
                        page_downloaded += 1
                        print(f"✅ 进度: {i}/{len(students)} 完成 (已下载)")
                    else:
                        print(f"⚠ 进度: {i}/{len(students)} 跳过 (无照片)")
                    
                    total_processed += 1
                    
                    # 显示总体进度
                    progress = (i / len(students)) * 100
                    print(f"📊 本页进度: {progress:.1f}% ({page_downloaded}/{len(students)} 本页, {total_downloaded}/{total_processed} 总计)")
                    
                    # 避免请求过快
                    time.sleep(1.5)
                
                print(f"\n✅ 第 {page_num} 页处理完成！")
                print(f"   本页学生: {len(students)} 个")
                print(f"   本页下载: {page_downloaded} 张照片")
                print(f"   总计下载: {total_downloaded}/{total_processed}")
                
                # 检查下一页
                if not self.has_next_page():
                    print("✓ 已到达最后一页")
                    break
                
                page_num += 1
                print(f"\n🔄 准备处理第 {page_num} 页...")
            
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