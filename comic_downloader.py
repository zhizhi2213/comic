
import requests
import re
import os
from urllib.parse import urljoin

def download_comic(url):
    """
    下载指定URL的漫画。

    :param url: 漫画章节的URL。
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果请求失败，则抛出HTTPError
    except requests.exceptions.RequestException as e:
        print(f"请求页面失败: {e}")
        return

    # 提取漫画标题
    title_match = re.search(r'<title>(.*?)</title>', response.text)
    title = title_match.group(1).strip() if title_match else "comic"
    
    # 创建保存图片的目录
    if not os.path.exists(title):
        os.makedirs(title)

    # 查找包含图片数据的脚本
    script_match = re.search(r'var img_data = "(.*?)";', response.text)
    if not script_match:
        print("未找到图片数据。")
        return

    img_data = script_match.group(1)
    
    # 简单的解码（根据网站的JS逻辑）
    # 这里只是一个示例，实际的解码方式可能更复杂
    # 在这个网站的例子中，它只是简单的字符串替换
    img_data = img_data.replace('\\\\/', '/')

    # 提取图片链接
    image_urls = re.findall(r'(\w+:\\/\\/[^"]+)', img_data)
    
    if not image_urls:
        # 如果上面的正则找不到，尝试另一种
        image_urls = re.findall(r'(https?://[^"]+)', img_data)


    print(f"找到 {len(image_urls)} 张图片。")

    for i, img_url in enumerate(image_urls):
        img_url = img_url.replace('\\\\/', '/') # 再次清理URL
        try:
            img_response = requests.get(img_url, headers=headers)
            img_response.raise_for_status()
            
            # 保存图片
            file_extension = os.path.splitext(img_url)[1]
            # 如果没有扩展名，默认为.jpg
            if not file_extension:
                file_extension = '.jpg'

            file_name = f"{i+1:03d}{file_extension}"
            file_path = os.path.join(title, file_name)
            
            with open(file_path, 'wb') as f:
                f.write(img_response.content)
            
            print(f"已下载: {file_path}")

        except requests.exceptions.RequestException as e:
            print(f"下载图片失败: {img_url}, 错误: {e}")

if __name__ == '__main__':
    # 示例URL，您可以替换成任何您想下载的漫画章节页面
    start_url = 'https://www.comicbox.xyz/book/4638?id=4638&page=4'
    download_comic(start_url)
