import requests
import re
import os
import time
from urllib.parse import urljoin
from pathlib import Path

# 配置信息
BASE_URL = "https://www.comicbox.xyz"
BOOK_ID = "4638"
BOOK_URL = f"{BASE_URL}/book/{BOOK_ID}"
DOWNLOAD_DIR = Path("downloads")
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': BASE_URL
}

def get_chapters():
    """获取所有章节链接"""
    print(f"正在获取书籍 {BOOK_ID} 的章节列表...")
    try:
        response = requests.get(BOOK_URL, headers=HEADERS)
        response.raise_for_status()
        
        # 提取章节链接
        # 格式: <li><a href="/chapter/21913" target="_blank" title="第1話">
        chapters = re.findall(r'<li><a href="(/chapter/\d+)" target="_blank"\s+title="(.*?)">', response.text)
        
        if not chapters:
            # 尝试另一种匹配方式
            chapters = re.findall(r'<a href="(/chapter/\d+)"[^>]*title="(.*?)"', response.text)
            
        # 按章节编号排序（从第1话到最后）
        # 提取标题中的数字进行排序，例如 "第1話" -> 1
        def sort_key(item):
            title = item[1]
            nums = re.findall(r'\d+', title)
            return int(nums[0]) if nums else 0
            
        chapters.sort(key=sort_key)
            
        print(f"共找到 {len(chapters)} 个章节。")
        return [(urljoin(BASE_URL, c[0]), c[1].strip()) for c in chapters]
    except Exception as e:
        print(f"获取章节列表失败: {e}")
        return []

def download_chapter(chapter_url, chapter_title):
    """下载指定章节的所有图片"""
    # 清理文件名中的非法字符
    safe_title = re.sub(r'[\\/:*?"<>|]', '_', chapter_title)
    chapter_dir = DOWNLOAD_DIR / f"{safe_title}"
    
    if not chapter_dir.exists():
        chapter_dir.mkdir(parents=True)
    else:
        # 如果目录已存在，检查是否已经下载过（简单检查，可以更复杂）
        if list(chapter_dir.glob("*.jpg")):
            print(f"章节 '{chapter_title}' 似乎已下载，跳过。")
            return

    print(f"正在下载章节: {chapter_title} ({chapter_url})")
    
    try:
        response = requests.get(chapter_url, headers=HEADERS)
        response.raise_for_status()
        
        # 提取图片链接
        # 格式: data-src="https://bmigmi-global-wuwu.ccavbox.com/break_2/static/upload/book/4638/21916/652180.jpg"
        # 注意: 某些页面可能使用单引号或不规范的空格，使用更宽容的正则
        image_urls = re.findall(r'data-src\s*=\s*["\'](https?://[^"\']+)["\']', response.text)
        
        if not image_urls:
            print(f"章节 '{chapter_title}' 未找到图片链接。")
            return

        print(f"找到 {len(image_urls)} 张图片。")

        for i, img_url in enumerate(image_urls):
            # 过滤掉封面等非漫画图片（通常包含 cover 或 static/images）
            if "cover" in img_url.lower() or "static/images" in img_url:
                continue
                
            file_path = chapter_dir / f"{i+1:03d}.jpg"
            
            # 下载图片
            try:
                img_res = requests.get(img_url, headers=HEADERS, timeout=30)
                img_res.raise_for_status()
                with open(file_path, 'wb') as f:
                    f.write(img_res.content)
                print(f"  [{i+1}/{len(image_urls)}] 已下载: {file_path.name}")
                # 适当延迟，避免请求过快
                time.sleep(0.5)
            except Exception as e:
                print(f"  下载图片失败 {img_url}: {e}")

    except Exception as e:
        print(f"下载章节失败 {chapter_title}: {e}")

def main():
    if not DOWNLOAD_DIR.exists():
        DOWNLOAD_DIR.mkdir()
        
    chapters = get_chapters()
    
    # 为了演示，我们只下载最新的一个章节，或者您可以循环下载所有
    # 章节列表已经按顺序排列
    for url, title in chapters: # 从第1话开始按顺序下载
        download_chapter(url, title)
        # break # 演示时只下载第一章

if __name__ == '__main__':
    main()
