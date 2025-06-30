#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
학교 홈페이지 공지사항 RSS 크롤러
RSS 피드를 통해 공지사항을 크롤링하는 모듈입니다.
"""

import json
import logging
import os
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urljoin

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='crawler.log',
    filemode='a'
)

def crawl_school_notices(url, site_name=None):
    """
    학교 홈페이지 공지사항을 RSS 피드로 크롤링합니다.
    
    Args:
        url (str): 공지사항 RSS 피드 URL
        site_name (str, optional): 사이트 이름, 없으면 URL에서 추출
        
    Returns:
        dict: 크롤링된 공지사항 정보
    """
    if not site_name:
        # URL에서 도메인 추출하여 사이트 이름으로 사용
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if match:
            site_name = match.group(1)
        else:
            site_name = "unknown_site"
    
    logging.info(f"{site_name} 공지사항 RSS 크롤러 시작...")
    
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
            "notices": [],
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
        
        # RSS 네임스페이스 처리
        namespaces = {'rss': 'http://purl.org/rss/1.0/'}
        
        # item 요소들 찾기
        items = root.findall('.//item')
        if not items:
            # 네임스페이스 없이 시도
            items = root.findall('.//item')
        
        notices = []
        
        for item in items:
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
                    # RSS 날짜 형식 (예: Mon, 24 Jun 2025 10:30:00 +0900)
                    date_obj = datetime.strptime(date_text, "%a, %d %b %Y %H:%M:%S %z")
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    try:
                        # 다른 형식 시도
                        date_obj = datetime.strptime(date_text, "%Y-%m-%d %H:%M:%S")
                        formatted_date = date_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        # 시간 정보가 포함된 다른 형식들 처리
                        if 'T' in date_text:
                            # ISO 형식 (예: 2025-06-24T16:03:22)
                            date_part = date_text.split('T')[0]
                            formatted_date = date_part
                        else:
                            formatted_date = date_text
                
                notice_data = {
                    "number": str(len(notices) + 1),
                    "title": title,
                    "author": "",
                    "date": formatted_date,
                    "views": "0",
                    "url": link
                }
                
                notices.append(notice_data)
                
            except Exception as e:
                logging.error(f"RSS 항목 파싱 중 오류 발생: {e}")
                continue
        
        logging.info(f"공지사항 RSS 크롤링 완료: {len(notices)}개")
        
    except ET.ParseError as e:
        logging.error(f"RSS XML 파싱 오류: {e}")
        return {
            "notices": [],
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
        "notices": notices,
        "meta": {
            "total_count": len(notices),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": site_name,
            "url": url
        }
    }
    
    logging.info(f"크롤링 완료: {len(notices)}개 공지사항")
    return result

if __name__ == "__main__":
    # 예제 URL
    test_url = "https://anyang-e.goeay.kr/anyang-e/na/ntt/selectRssFeed.do?mi=4492&bbsId=1821"
    result = crawl_school_notices(test_url, "안양초등학교")
    
    # 모든 공지사항 출력
    print("\n공지사항 목록:")
    for i, notice in enumerate(result["notices"], 1):
        print(f"{i}. {notice.get('title')} ({notice.get('date')})") 