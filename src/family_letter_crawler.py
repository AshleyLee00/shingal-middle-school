#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
학교 홈페이지 가정통신문 크롤러
HTML 페이지를 직접 크롤링하여 가정통신문을 수집하는 모듈입니다.
"""

import json
import logging
import os
import re
import requests
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# 로그 파일 경로 설정
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'family_letter_crawler.log')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_file,
    filemode='w',
    encoding='utf-8'
)

def crawl_school_letters(url, site_name=None):
    """
    학교 홈페이지 가정통신문을 HTML 페이지에서 직접 크롤링합니다.
    
    Args:
        url (str): 가정통신문 페이지 URL
        site_name (str, optional): 사이트 이름, 없으면 URL에서 추출
        
    Returns:
        dict: 크롤링된 가정통신문 정보
    """
    if not site_name:
        # URL에서 도메인 추출하여 사이트 이름으로 사용
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if match:
            site_name = match.group(1)
        else:
            site_name = "unknown_site"
    
    logging.info(f"{site_name} 가정통신문 HTML 크롤러 시작...")
    
    # 웹 페이지 요청
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'  # 한글 인코딩 설정
    except requests.RequestException as e:
        logging.error(f"요청 중 오류 발생: {e}")
        return {
            "letters": [],
            "meta": {
                "total_count": 0,
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "source": site_name,
                "url": url,
                "error": str(e)
            }
        }
    
    # HTML 파싱
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 가정통신문 테이블 찾기
        # 테이블 내의 tr 요소들을 찾습니다 (헤더 제외)
        table = soup.find('table')
        if not table:
            logging.error("가정통신문 테이블을 찾을 수 없습니다.")
            return {
                "letters": [],
                "meta": {
                    "total_count": 0,
                    "last_updated": datetime.now().strftime("%Y-%m-%d"),
                    "source": site_name,
                    "url": url,
                    "error": "가정통신문 테이블을 찾을 수 없습니다."
                }
            }
        
        # 테이블의 모든 행(tr)을 찾습니다
        rows = table.find_all('tr')
        letters = []
        
        for row in rows:
            # 헤더 행은 건너뜁니다
            if row.find('th'):
                continue
                
            # td 요소들을 찾습니다
            cells = row.find_all('td')
            if len(cells) >= 5:  # 번호, 제목, 첨부, 이름, 날짜, 조회 컬럼이 있어야 함
                try:
                    # 번호 추출
                    number_cell = cells[0]
                    number = number_cell.get_text(strip=True)
                    
                    # 공지사항은 건너뜁니다
                    if number == "공지":
                        continue
                    
                    # 제목과 링크 추출
                    title_cell = cells[1]
                    title_link = title_cell.find('a')
                    if title_link:
                        title = title_link.get_text(strip=True)
                        link = title_link.get('href')
                        if link and not link.startswith('http'):
                            link = urljoin(url, link)
                    else:
                        title = title_cell.get_text(strip=True)
                        link = ""
                    
                    # 첨부파일 여부 확인
                    attachment_cell = cells[2]
                    has_attachment = bool(attachment_cell.find('img'))
                    
                    # 작성자 추출
                    author_cell = cells[3]
                    author = author_cell.get_text(strip=True)
                    
                    # 날짜 추출
                    date_cell = cells[4]
                    date_text = date_cell.get_text(strip=True)
                    
                    # 조회수 추출 (있는 경우)
                    views = "0"
                    if len(cells) > 5:
                        views_cell = cells[5]
                        views = views_cell.get_text(strip=True)
                    
                    # 날짜 형식 정리 (YY.MM.DD 형식을 YYYY-MM-DD로 변환)
                    try:
                        if re.match(r'\d{2}\.\d{2}\.\d{2}', date_text):
                            # 25.07.03 형식을 2025-07-03으로 변환
                            year, month, day = date_text.split('.')
                            year = f"20{year}"  # 25 -> 2025
                            formatted_date = f"{year}-{month}-{day}"
                        else:
                            formatted_date = date_text
                    except:
                        formatted_date = date_text
                    
                    letter_data = {
                        "number": number,
                        "title": title,
                        "author": author,
                        "date": formatted_date,
                        "views": views,
                        "url": link,
                        "has_attachment": has_attachment
                    }
                    
                    letters.append(letter_data)
                    
                except Exception as e:
                    logging.error(f"행 파싱 중 오류 발생: {e}")
                    continue
        
        logging.info(f"가정통신문 HTML 크롤링 완료: {len(letters)}개")
        
    except Exception as e:
        logging.error(f"HTML 파싱 오류: {e}")
        return {
            "letters": [],
            "meta": {
                "total_count": 0,
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "source": site_name,
                "url": url,
                "error": f"HTML 파싱 오류: {str(e)}"
            }
        }
    
    # 메타 정보 추가
    result = {
        "letters": letters,
        "meta": {
            "total_count": len(letters),
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "source": site_name,
            "url": url
        }
    }
    
    return result

if __name__ == "__main__":
    # 남성중학교 가정통신문 페이지 URL
    test_url = "https://school.jbedu.kr/jb-namsung/M010601/"
    result = crawl_school_letters(test_url, "남성중학교")
    
    # 모든 가정통신문 출력
    print("\n가정통신문 목록:")
    for i, letter in enumerate(result["letters"], 1):
        print(f"{i}. {letter.get('title')} ({letter.get('date')}) - {letter.get('author')}")
        if letter.get('has_attachment'):
            print("   [첨부파일 있음]") 