#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
학교 홈페이지 앨범 크롤러
RSS 피드를 통해 앨범 게시물을 크롤링하고, 각 게시물의 상세 페이지에서 사진과 내용을 추출하는 모듈입니다.
"""

import json
import logging
import os
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time

# 로그 파일 경로 설정
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'album_crawler.log')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_file,
    filemode='w',
    encoding='utf-8'
)

def crawl_album_posts(url, site_name=None, max_posts=5):
    """
    학교 홈페이지 앨범을 RSS 피드로 크롤링하고, 각 게시물의 상세 정보를 가져옵니다.
    
    Args:
        url (str): 앨범 RSS 피드 URL
        site_name (str, optional): 사이트 이름, 없으면 URL에서 추출
        max_posts (int): 최대 크롤링할 게시물 수
        
    Returns:
        dict: 크롤링된 앨범 정보
    """
    if not site_name:
        # URL에서 도메인 추출하여 사이트 이름으로 사용
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if match:
            site_name = match.group(1)
        else:
            site_name = "unknown_site"
    
    logging.info(f"{site_name} 앨범 RSS 크롤러 시작...")
    
    # 웹 페이지 요청
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"요청 중 오류 발생: {e}")
        return {
            "albums": [],
            "meta": {
                "total_count": 0,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": site_name,
                "url": url,
                "error": str(e)
            }
        }
    
    # RSS XML 파싱
    try:
        root = ET.fromstring(response.text)
        
        # item 요소들 찾기 (여러 방법 시도)
        items = root.findall('.//item')
        if not items:
            # 다른 태그명으로 시도
            items = root.findall('.//entry')  # Atom 형식
        if not items:
            # 네임스페이스와 함께 시도
            namespaces = {'rss': 'http://purl.org/rss/1.0/'}
            items = root.findall('.//rss:item', namespaces)
        
        albums = []
        
        for i, item in enumerate(items[:max_posts]):
            try:
                # 제목 추출
                title_elem = item.find('title')
                title = title_elem.text if title_elem is not None else ""
                
                # 링크 추출
                link_elem = item.find('link')
                link = link_elem.text if link_elem is not None else ""
                
                # 날짜 추출
                date_elem = item.find('pubDate')
                date_text = date_elem.text if date_elem is not None else ""
                
                # 날짜 형식 변환
                try:
                    # RSS 날짜 형식 (예: Wed, 02 Jul 2025 23:17:42 GMT)
                    if 'GMT' in date_text:
                        date_obj = datetime.strptime(date_text, "%a, %d %b %Y %H:%M:%S GMT")
                    else:
                        # RSS 날짜 형식 (예: Mon, 24 Jun 2025 10:30:00 +0900)
                        date_obj = datetime.strptime(date_text, "%a, %d %b %Y %H:%M:%S %z")
                    
                    formatted_date = date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    try:
                        # 다른 형식 시도
                        date_obj = datetime.strptime(date_text, "%Y-%m-%d %H:%M:%S")
                        formatted_date = date_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        # 시간 정보가 포함된 다른 형식들 처리
                        if 'T' in date_text:
                            # ISO 형식 (예: 2025-06-24T16:03:22)
                            date_part = date_text.split('T')[0]
                            formatted_date = date_part
                        else:
                            formatted_date = date_text
                
                # 상세 페이지에서 사진과 내용 크롤링
                detail_info = crawl_post_detail(link, headers)
                
                album_data = {
                    "number": str(len(albums) + 1),
                    "title": title,
                    "date": formatted_date,
                    "url": link,
                    "images": detail_info.get('images', []),
                    "content": detail_info.get('content', ''),
                    "author": detail_info.get('author', '')
                }
                
                albums.append(album_data)
                
                # 요청 간격을 두어 서버 부하 방지
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"RSS 항목 파싱 중 오류 발생: {e}")
                continue
        
        logging.info(f"앨범 RSS 크롤링 완료: {len(albums)}개")
        
    except ET.ParseError as e:
        logging.error(f"RSS XML 파싱 오류: {e}")
        return {
            "albums": [],
            "meta": {
                "total_count": 0,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": site_name,
                "url": url,
                "error": f"RSS XML 파싱 오류: {str(e)}"
            }
        }
    
    # 메타 정보 추가
    result = {
        "albums": albums,
        "meta": {
            "total_count": len(albums),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": site_name,
            "url": url
        }
    }
    
    logging.info(f"크롤링 완료: {len(albums)}개 앨범")
    return result

def crawl_post_detail(url, headers):
    """
    게시물 상세 페이지에서 사진과 내용을 크롤링합니다.
    
    Args:
        url (str): 게시물 상세 페이지 URL
        headers (dict): HTTP 헤더
        
    Returns:
        dict: 사진 URL 목록과 내용
    """
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 사진 URL 추출
        images = []
        
        # img 태그에서 사진 찾기
        img_tags = soup.find_all('img')
        for img in img_tags:
            src = img.get('src')
            if src:
                # 상대 URL을 절대 URL로 변환
                if src.startswith('/'):
                    parsed_url = urlparse(url)
                    src = f"{parsed_url.scheme}://{parsed_url.netloc}{src}"
                elif not src.startswith('http'):
                    src = urljoin(url, src)
                
                # 실제 이미지 파일인지 확인 (일반적인 이미지 확장자)
                if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']):
                    # 썸네일이나 작은 이미지 제외 (일반적으로 큰 이미지가 메인)
                    if not any(keyword in src.lower() for keyword in ['thumb', 'small', 'icon', 'logo']):
                        images.append(src)
        
        # 내용 추출
        content = ""
        
        # 본문 내용 찾기 (여러 가능한 선택자 시도)
        content_selectors = [
            '.board_view_content',
            '.content',
            '.post-content',
            '.article-content',
            '.board_content',
            '#content',
            '.view_content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # HTML 태그 제거하고 텍스트만 추출
                content = content_elem.get_text(strip=True)
                break
        
        # 작성자 추출
        author = ""
        author_selectors = [
            '.writer',
            '.author',
            '.user_name',
            '.post_author'
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                author = author_elem.get_text(strip=True)
                break
        
        return {
            'images': images,
            'content': content,
            'author': author
        }
        
    except Exception as e:
        logging.error(f"상세 페이지 크롤링 오류: {e}")
        return {
            'images': [],
            'content': '',
            'author': ''
        }

def main():
    # 학교 정보
    school_info = {
        "name": "신갈중학교",
        "album_url": "http://shingal-m.goeyi.kr/shingal-m/na/ntt/selectRssFeed.do?mi=14354&bbsId=8201"
    }
    
    # 앨범 크롤링
    print(f"{school_info['name']} 앨범 크롤링 시작...")
    albums_result = crawl_album_posts(
        school_info["album_url"],
        school_info["name"],
        max_posts=5  # 최대 5개 게시물
    )
    print(f"앨범 크롤링 완료: {len(albums_result.get('albums', []))}개")
    
    # 결과 출력
    for i, album in enumerate(albums_result.get('albums', []), 1):
        print(f"{i}. {album['title']} ({album['date']})")
        print(f"   이미지: {len(album['images'])}개")
        print(f"   내용: {album['content'][:100]}...")

if __name__ == "__main__":
    main() 