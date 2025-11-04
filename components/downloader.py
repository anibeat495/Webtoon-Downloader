"""
Webtoon Downloader Core Logic
"""
import requests
from bs4 import BeautifulSoup
import os
import img2pdf
from PIL import Image
import re
import json
import time
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import safe_filename, get_webtoon_headers, cleanup_directory


class WebtoonDownloader:
    """Main downloader class for webtoon series"""
    
    def __init__(self, log_callback=None):
        """
        Initialize downloader
        
        Args:
            log_callback (callable, optional): Callback function for logging
        """
        self.session = requests.Session()
        self.log_callback = log_callback
        self.is_cancelled = False
        
    def log(self, message, level="INFO"):
        """Log message if callback is set"""
        if self.log_callback:
            self.log_callback(message, level)
    
    def cancel(self):
        """Cancel ongoing download"""
        self.is_cancelled = True
    
    def get_series_info(self, series_url):
        """
        Get series information from URL
        
        Args:
            series_url (str): URL of the series
            
        Returns:
            str: Series title or None
        """
        try:
            response = self.session.get(series_url, headers=get_webtoon_headers(), timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            series_title = soup.select_one('h1.subj')
            if series_title:
                return safe_filename(series_title.text.strip())
            return "Unknown_Series"
        except Exception as e:
            self.log(f"Failed to get series info: {str(e)}", "ERROR")
            return None
    
    def get_all_chapters(self, series_url, progress_callback=None):
        """
        Get all chapters from series
        
        Args:
            series_url (str): URL of the series
            progress_callback (callable, optional): Callback for progress updates
            
        Returns:
            list: List of chapter dictionaries with 'url' and 'title'
        """
        chapters = []
        
        try:
            # Parse base URL
            base_url = series_url.split('&page=')[0]
            if '?' not in base_url:
                base_url += '?'
            if not base_url.endswith('?') and not base_url.endswith('&'):
                base_url += '&'
            
            # Find last page
            self.log("Finding total pages...", "INFO")
            last_page = 1
            
            try:
                response = self.session.get(
                    f"{base_url}page=999999",
                    headers=get_webtoon_headers(),
                    timeout=30
                )
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                paginate = soup.find('div', class_='paginate')
                if paginate:
                    page_numbers = [int(span.text) for span in paginate.find_all('span', class_='on')]
                    if page_numbers:
                        last_page = max(page_numbers)
            except Exception as e:
                self.log(f"Could not determine page count, using default: {str(e)}", "WARNING")
                last_page = 10
            
            self.log(f"Found {last_page} pages to scan", "INFO")
            
            # Get chapters from each page
            for page in range(1, last_page + 1):
                if self.is_cancelled:
                    break
                    
                try:
                    if progress_callback:
                        progress_callback(page, last_page)
                    
                    self.log(f"Scanning page {page}/{last_page}", "INFO")
                    
                    response = self.session.get(
                        f"{base_url}page={page}",
                        headers=get_webtoon_headers(),
                        timeout=30
                    )
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    chapter_list = soup.find('ul', id='_listUl')
                    if chapter_list:
                        for item in chapter_list.find_all('li'):
                            link = item.find('a', href=True)
                            title_elem = item.find('span', class_='subj')
                            
                            if link and title_elem:
                                chapter_url = link['href']
                                if not chapter_url.startswith('http'):
                                    chapter_url = urljoin('https://www.webtoons.com', chapter_url)
                                
                                title_text = title_elem.get_text(strip=True)
                                if title_text:
                                    chapters.append({
                                        'url': chapter_url,
                                        'title': title_text
                                    })
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    self.log(f"Error on page {page}: {str(e)}", "WARNING")
            
            # Reverse to get chronological order
            chapters.reverse()
            
            if not chapters:
                raise Exception("No chapters found")
            
            self.log(f"Found {len(chapters)} chapters", "SUCCESS")
            return chapters
            
        except Exception as e:
            self.log(f"Error fetching chapters: {str(e)}", "ERROR")
            return []
    
    def extract_image_urls(self, chapter_url):
        """
        Extract image URLs from chapter page
        
        Args:
            chapter_url (str): URL of the chapter
            
        Returns:
            list: List of image URLs
        """
        try:
            response = self.session.get(chapter_url, headers=get_webtoon_headers(), timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            image_urls = []
            
            # Method 1: Look for image list div
            image_list = soup.find('div', id='_imageList')
            if image_list:
                images = image_list.find_all('img', class_='_images')
                for img in images:
                    if 'data-url' in img.attrs:
                        image_urls.append(img['data-url'])
            
            # Method 2: Parse from JavaScript
            if not image_urls:
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and 'imageData' in script.string:
                        try:
                            match = re.search(r'var\s+imageData\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                            if match:
                                image_data = json.loads(match.group(1))
                                for item in image_data:
                                    if 'url' in item:
                                        image_urls.append(item['url'])
                                if image_urls:
                                    break
                        except:
                            continue
            
            # Method 3: Look for viewer images
            if not image_urls:
                viewer = soup.find('div', id='_viewerBox')
                if viewer:
                    for img in viewer.find_all('img'):
                        src = img.get('data-url') or img.get('data-src') or img.get('src')
                        if src and not any(x in src.lower() for x in ['advertisement', 'blank', 'loading']):
                            image_urls.append(src)
            
            return image_urls
            
        except Exception as e:
            self.log(f"Error extracting images: {str(e)}", "ERROR")
            return []
    
    def download_image(self, url, img_path, headers):
        """
        Download a single image
        
        Args:
            url (str): Image URL
            img_path (str): Path to save image
            headers (dict): Request headers
            
        Returns:
            str: Path to downloaded image or None
        """
        try:
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Verify content type
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                return None
            
            # Save image
            with open(img_path, 'wb') as f:
                f.write(response.content)
            
            # Verify image is valid
            with Image.open(img_path) as img:
                if img.size[0] < 100 or img.size[1] < 100:
                    os.remove(img_path)
                    return None
            
            return img_path
            
        except Exception:
            if os.path.exists(img_path):
                os.remove(img_path)
            return None
    
    def download_chapter(self, chapter_info, output_dir, progress_callback=None):
        """
        Download a single chapter
        
        Args:
            chapter_info (dict): Chapter info with 'url' and 'title'
            output_dir (str): Output directory
            progress_callback (callable, optional): Callback for progress updates (current, total)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.is_cancelled:
            return False
            
        chapter_dir = None
        
        try:
            chapter_title = chapter_info['title']
            safe_title = safe_filename(chapter_title)
            
            # Create temp directory
            chapter_dir = os.path.join(output_dir, f"temp_{safe_title}")
            os.makedirs(chapter_dir, exist_ok=True)
            
            # Extract image URLs
            image_urls = self.extract_image_urls(chapter_info['url'])
            if not image_urls:
                self.log("No images found in chapter", "WARNING")
                return False
            
            total_pages = len(image_urls)
            
            # Download images concurrently with real-time progress
            image_files = []
            headers = get_webtoon_headers(chapter_info['url'])
            downloaded = 0
            
            # Initial progress
            if progress_callback:
                progress_callback(0, total_pages)
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {}
                for i, url in enumerate(image_urls, 1):
                    if self.is_cancelled:
                        break
                    img_path = os.path.join(chapter_dir, f"{i:03d}.jpg")
                    future = executor.submit(self.download_image, url, img_path, headers)
                    futures[future] = i
                
                for future in as_completed(futures):
                    if self.is_cancelled:
                        break
                        
                    img_num = futures[future]
                    try:
                        img_path = future.result()
                        if img_path:
                            image_files.append(img_path)
                            downloaded += 1
                            
                            # Update progress for each downloaded page
                            if progress_callback:
                                progress_callback(downloaded, total_pages)
                                
                    except Exception as e:
                        self.log(f"Failed image {img_num}: {str(e)}", "WARNING")
            
            if self.is_cancelled:
                return False
                
            if not image_files:
                self.log("No valid images downloaded", "ERROR")
                return False
            
            # Sort and convert to PDF
            image_files.sort()
            pdf_path = os.path.join(output_dir, f"{safe_title}.pdf")
            
            # Final progress at 100%
            if progress_callback:
                progress_callback(total_pages, total_pages)
            
            with open(pdf_path, "wb") as f:
                f.write(img2pdf.convert(image_files))
            
            # Cleanup
            cleanup_directory(chapter_dir)
            
            return True
            
        except Exception as e:
            self.log(f"Error downloading chapter: {str(e)}", "ERROR")
            if chapter_dir and os.path.exists(chapter_dir):
                cleanup_directory(chapter_dir)
            return False
    
    def download_series(self, series_url, selected_chapters, output_dir, progress_callback=None):
        """
        Download selected chapters from a series
        
        Args:
            series_url (str): Series URL
            selected_chapters (list): List of chapter dicts
            output_dir (str): Output directory
            progress_callback (callable, optional): Callback for overall progress
            
        Returns:
            tuple: (success_count, total_count)
        """
        self.is_cancelled = False
        success_count = 0
        total = len(selected_chapters)
        
        for i, chapter in enumerate(selected_chapters, 1):
            if self.is_cancelled:
                self.log("Download cancelled by user", "WARNING")
                break
            
            if progress_callback:
                progress_callback(i, total, chapter['title'])
            
            if self.download_chapter(chapter, output_dir):
                success_count += 1
            
            # Small delay between chapters
            time.sleep(0.5)
        
        return success_count, total
