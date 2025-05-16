#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
학교 홈페이지 가정통신문 범용 크롤러
URL을 입력받아 가정통신문을 크롤링하는 범용 모듈입니다.
"""

import json
import logging
import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

# 로그 파일 경로 설정
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'family_letter_crawler.log')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_file,
    filemode='a',
    encoding='utf-8'
)

def detect_table_structure(soup):
    """
    가정통신문 테이블 구조를 자동으로 감지합니다.
    """
    # 일반적인 테이블 선택자 패턴
    table_selectors = [
        "table.boardList", 
        "table.board_list",
        "table.list",
        "table.notice",
        ".board_list table", 
        ".notice_list table",
        ".board_body table",
        "#board_list table",
        ".board-list table",
        "table.tbl_list"
    ]
    
    # 테이블 찾기
    for selector in table_selectors:
        table = soup.select_one(selector)
        if table:
            return selector
    
    # 테이블을 찾지 못한 경우 일반 테이블 태그 찾기
    tables = soup.find_all('table')
    if tables:
        # 테이블 중 가장 행이 많은 테이블 선택 (가정통신문일 가능성이 높음)
        max_rows = 0
        best_table = None
        
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > max_rows:
                max_rows = len(rows)
                best_table = table
        
        if best_table:
            # 해당 테이블의 클래스나 ID 반환
            if best_table.get('class'):
                return f"table.{' '.join(best_table['class'])}"
            elif best_table.get('id'):
                return f"table#{best_table['id']}"
            else:
                return "table"
    
    return None

def crawl_school_letters(url, site_name=None):
    """
    학교 홈페이지 가정통신문을 크롤링합니다.
    
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
    
    logging.info(f"{site_name} 가정통신문 크롤러 시작...")
    
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
            "letters": [],
            "meta": {
                "total_count": 0,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": site_name,
                "url": url,
                "error": str(e)
            }
        }
    
    # HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 테이블 구조 감지
    table_selector = detect_table_structure(soup)
    
    if not table_selector:
        logging.error(f"가정통신문 테이블을 찾을 수 없습니다: {url}")
        return {
            "letters": [],
            "meta": {
                "total_count": 0,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": site_name,
                "url": url,
                "error": "가정통신문 테이블을 찾을 수 없습니다."
            }
        }
    
    # 가정통신문 목록 추출
    letters = []
    
    try:
        letter_rows = soup.select(f"{table_selector} > tbody > tr:not(.notice)")
        if not letter_rows:
            letter_rows = soup.select(f"{table_selector} > tbody > tr")
        
        if not letter_rows:
            logging.error(f"가정통신문 행을 찾을 수 없습니다: {url}")
            return {
                "letters": [],
                "meta": {
                    "total_count": 0,
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source": site_name,
                    "url": url,
                    "error": "가정통신문 행을 찾을 수 없습니다."
                }
            }
        
        for row in letter_rows:
            try:
                # 각 컬럼 데이터 추출
                columns = row.select("td")
                
                if len(columns) >= 3:  # 최소 3개 컬럼(번호, 제목, 날짜)이 있는지 확인
                    # 기본값 설정
                    letter_data = {
                        "number": "",
                        "title": "",
                        "author": "",
                        "date": "",
                        "views": "",
                        "url": ""
                    }
                    
                    # 번호 (첫번째 컬럼)
                    letter_data["number"] = columns[0].get_text(strip=True)
                    
                    # 제목 및 URL (두번째 컬럼)
                    title_element = columns[1].select_one("a")
                    if title_element:
                        letter_data["title"] = title_element.get_text(strip=True)
                        
                        # URL 추출
                        if title_element.has_attr('href'):
                            href = title_element['href']
                            # JavaScript 함수 처리
                            if href.startswith('javascript:'):
                                # 다양한 자바스크립트 패턴 처리
                                match = re.search(r"['\(](\d+)['\)]", href)
                                if match:
                                    article_id = match.group(1)
                                    # URL 패턴 추측
                                    domain = re.search(r'https?://(?:www\.)?([^/]+)', url).group(0)
                                    letter_data["url"] = f"{domain}/board/view?id={article_id}"
                            # 상대 경로 처리
                            elif not href.startswith(('http://', 'https://')):
                                letter_data["url"] = urljoin(url, href)
                            else:
                                letter_data["url"] = href
                    else:
                        letter_data["title"] = columns[1].get_text(strip=True)
                    
                    # 날짜와 조회수 처리
                    if len(columns) >= 4:
                        # 마지막에서 두 번째 열이 날짜
                        letter_data["date"] = columns[-2].get_text(strip=True)
                        # 마지막 열이 조회수
                        letter_data["views"] = columns[-1].get_text(strip=True)
                    else:
                        # 열이 3개인 경우 마지막 열이 날짜
                        letter_data["date"] = columns[-1].get_text(strip=True)
                        letter_data["views"] = "0"  # 조회수 정보가 없는 경우
                    
                    letters.append(letter_data)
            except Exception as e:
                logging.error(f"데이터 추출 중 오류 발생: {e}")
                continue
        
        logging.info(f"가정통신문 크롤링 완료: {len(letters)}개")
        
    except Exception as e:
        logging.error(f"크롤링 중 오류 발생: {e}")
    
    # 메타 정보 추가
    result = {
        "letters": letters,
        "meta": {
            "total_count": len(letters),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": site_name,
            "url": url
        }
    }
    
    # 결과 JSON 파일로 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(log_dir, f"{site_name.replace('.', '_')}_family_letters_api_{timestamp}.json")
    try:
        # 새 데이터 저장
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logging.info(f"크롤링 완료: {len(letters)}개 가정통신문이 {filename}에 저장되었습니다.")
    except Exception as e:
        logging.error(f"파일 저장 중 오류 발생: {e}")
    
    return result

if __name__ == "__main__":
    # 예제 URL
    test_url = "https://isc.icehs.kr/boardCnts/list.do?boardID=11107&m=0203&s=inchon_ii"
    result = crawl_school_letters(test_url, "인천반도체고등학교")
    
    # 모든 가정통신문 출력
    print("\n가정통신문 목록:")
    for i, letter in enumerate(result["letters"], 1):
        print(f"{i}. {letter.get('title')} ({letter.get('date')})") 