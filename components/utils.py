"""
Utility functions for the Webtoon Downloader
"""
import os
import re
from urllib.parse import urljoin


def safe_filename(filename):
    """
    Make filename safe for all operating systems
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Safe filename
    """
    # Replace specific characters that cause issues
    filename = filename.replace(':', ' -')
    filename = filename.replace('/', '-')
    filename = filename.replace('\\', '-')
    
    # Replace other invalid characters
    invalid_chars = '<>"|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    
    # Replace multiple spaces with single space
    filename = ' '.join(filename.split())
    
    # Remove dots and spaces from the end
    filename = filename.rstrip('. ')
    
    # Truncate if too long
    max_length = 200
    if len(filename) > max_length:
        filename = filename[:max_length]
    
    return filename


def get_webtoon_headers(referer=None):
    """
    Get headers for webtoon requests
    
    Args:
        referer (str, optional): Referer URL
        
    Returns:
        dict: Request headers
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }
    if referer:
        headers['Referer'] = referer
    return headers


def cleanup_directory(directory):
    """
    Recursively delete a directory and all its contents
    
    Args:
        directory (str): Directory path to clean up
    """
    try:
        for root, dirs, files in os.walk(directory, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except:
                    pass
            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                except:
                    pass
        try:
            os.rmdir(directory)
        except:
            pass
    except Exception:
        pass


def ensure_directory(directory):
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory (str): Directory path
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
