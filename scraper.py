import requests
from bs4 import BeautifulSoup
import os
import time
import re
from pathlib import Path
import json
from datetime import datetime


class ComicboxScraper:
    def __init__(self, base_url="https://www.comicbox.xyz"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': base_url,
        })
        self.download_dir = Path("downloads")
        
    def get_page_content(self, url):
        """Fetch page content with error handling"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_image_urls(self, html):
        """Extract image URLs from page HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        images = []
        
        # Try to find images in common manga reader containers
        # Look for img tags with comic/manga related classes
        img_containers = soup.find_all('div', class_=re.compile(r'(chapter|content|reader|image|img)', re.I))
        
        if img_containers:
            for container in img_containers:
                imgs = container.find_all('img')
                for img in imgs:
                    src = img.get('data-src') or img.get('src')
                    if src and src.startswith('http'):
                        images.append(src)
                    elif src and src.startswith('/'):
                        images.append(self.base_url + src)
        
        # If no images found in containers, search all img tags
        if not images:
            all_imgs = soup.find_all('img')
            for img in all_imgs:
                src = img.get('data-src') or img.get('src')
                if src and src.startswith('http') and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    images.append(src)
        
        return images
    
    def get_chapter_list(self, book_url):
        """Get list of all chapters from the book page"""
        html = self.get_page_content(book_url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        chapters = []
        
        # Look for chapter links
        chapter_links = soup.find_all('a', href=re.compile(r'/chapter/|/book/\d+\?'))
        
        for link in chapter_links:
            href = link.get('href')
            title = link.get_text(strip=True)
            if href and title:
                if not href.startswith('http'):
                    href = self.base_url + href
                chapters.append({'title': title, 'url': href})
        
        # Remove duplicates while preserving order
        seen = set()
        unique_chapters = []
        for chapter in chapters:
            if chapter['url'] not in seen:
                seen.add(chapter['url'])
                unique_chapters.append(chapter)
        
        return unique_chapters
    
    def download_image(self, url, save_path):
        """Download a single image"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            return True
        except requests.RequestException as e:
            print(f"Error downloading {url}: {e}")
            return False
    
    def scrape_chapter(self, chapter_url, chapter_num=None):
        """Scrape all images from a chapter"""
        print(f"\nScraping chapter: {chapter_url}")
        
        html = self.get_page_content(chapter_url)
        if not html:
            return False
        
        images = self.extract_image_urls(html)
        
        if not images:
            print(f"No images found in chapter {chapter_url}")
            return False
        
        # Create chapter directory
        chapter_name = chapter_num or f"chapter_{int(time.time())}"
        chapter_dir = self.download_dir / chapter_name
        chapter_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Found {len(images)} images")
        
        # Download all images
        downloaded = 0
        for idx, img_url in enumerate(images, 1):
            filename = f"{idx:03d}.jpg"
            save_path = chapter_dir / filename
            
            if self.download_image(img_url, save_path):
                downloaded += 1
                print(f"Downloaded {idx}/{len(images)}: {filename}")
            
            # Be respectful - add small delay
            time.sleep(0.5)
        
        print(f"Downloaded {downloaded}/{len(images)} images successfully")
        return downloaded > 0
    
    def scrape_book(self, book_url, chapters=None):
        """Scrape entire book or specific chapters"""
        print(f"Starting to scrape book: {book_url}")
        
        # Ensure download directory exists
        self.download_dir.mkdir(exist_ok=True)
        
        # Get chapter list if not provided
        if not chapters:
            chapters = self.get_chapter_list(book_url)
            print(f"Found {len(chapters)} chapters")
        
        # Scrape each chapter
        for idx, chapter in enumerate(chapters, 1):
            print(f"\n{'='*50}")
            print(f"Chapter {idx}/{len(chapters)}: {chapter['title']}")
            print(f"{'='*50}")
            
            self.scrape_chapter(chapter['url'], f"chapter_{idx:03d}_{self.sanitize_filename(chapter['title'])}")
            
            # Add delay between chapters
            time.sleep(2)
    
    def sanitize_filename(self, filename):
        """Remove invalid characters from filename"""
        return re.sub(r'[<>:"/\\|?*]', '', filename)[:50]
    
    def save_progress(self, book_id, progress_data):
        """Save scraping progress to JSON file"""
        progress_file = self.download_dir / "progress.json"
        
        progress = {}
        if progress_file.exists():
            with open(progress_file, 'r') as f:
                progress = json.load(f)
        
        progress[book_id] = progress_data
        progress['last_updated'] = datetime.now().isoformat()
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    
    def load_progress(self, book_id):
        """Load previous scraping progress"""
        progress_file = self.download_dir / "progress.json"
        
        if not progress_file.exists():
            return None
        
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress = json.load(f)
        
        return progress.get(book_id)


def main():
    """Main function to run the scraper"""
    # Configuration
    BOOK_URL = "https://www.comicbox.xyz/book/4638?id=4638"
    BOOK_ID = "4638"
    
    scraper = ComicboxScraper()
    
    # Check if we should only download new chapters
    last_progress = scraper.load_progress(BOOK_ID)
    
    if last_progress:
        print(f"Last scraped on: {last_progress.get('last_scraped', 'Unknown')}")
        print(f"Last chapter: {last_progress.get('last_chapter', 'Unknown')}")
    
    # Scrape the book
    scraper.scrape_book(BOOK_URL)
    
    # Save progress
    scraper.save_progress(BOOK_ID, {
        'last_scraped': datetime.now().isoformat(),
        'last_chapter': 'All chapters',
        'book_url': BOOK_URL
    })
    
    print("\n" + "="*50)
    print("Scraping completed!")
    print(f"Downloads saved to: {scraper.download_dir.absolute()}")
    print("="*50)


if __name__ == "__main__":
    main()
