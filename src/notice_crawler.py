#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
학교 홈페이지 공지사항 범용 크롤러
URL을 입력받아 공지사항을 크롤링하는 범용 모듈입니다.
"""

import json
import logging
import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='crawler.log',
    filemode='a'
)

def detect_table_structure(soup):
    """
    공지사항 테이블 구조를 자동으로 감지합니다.
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
        # 테이블 중 가장 행이 많은 테이블 선택 (공지사항일 가능성이 높음)
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

def crawl_school_notices(url, site_name=None):
    """
    학교 홈페이지 공지사항을 크롤링합니다.
    
    Args:
        url (str): 공지사항 페이지 URL
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
    
    logging.info(f"{site_name} 공지사항 크롤러 시작...")
    
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
    
    # HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 테이블 구조 감지
    table_selector = detect_table_structure(soup)
    
    if not table_selector:
        logging.error(f"공지사항 테이블을 찾을 수 없습니다: {url}")
        return {
            "notices": [],
            "meta": {
                "total_count": 0,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": site_name,
                "url": url,
                "error": "공지사항 테이블을 찾을 수 없습니다."
            }
        }
    
    # 공지사항 목록 추출
    notices = []
    
    try:
        notice_rows = soup.select(f"{table_selector} > tbody > tr:not(.notice)")
        if not notice_rows:
            notice_rows = soup.select(f"{table_selector} > tbody > tr")
        
        if not notice_rows:
            logging.error(f"공지사항 행을 찾을 수 없습니다: {url}")
            return {
                "notices": [],
                "meta": {
                    "total_count": 0,
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source": site_name,
                    "url": url,
                    "error": "공지사항 행을 찾을 수 없습니다."
                }
            }
        
        for row in notice_rows:
            try:
                # 각 컬럼 데이터 추출
                columns = row.select("td")
                
                if len(columns) >= 3:  # 최소 3개 컬럼(번호, 제목, 날짜)이 있는지 확인
                    # 기본값 설정
                    notice_data = {
                        "number": "",
                        "title": "",
                        "author": "",
                        "date": "",
                        "views": "",
                        "url": ""
                    }
                    
                    # 번호 (첫번째 컬럼)
                    notice_data["number"] = columns[0].get_text(strip=True)
                    
                    # 제목 및 URL (두번째 컬럼)
                    title_element = columns[1].select_one("a")
                    if title_element:
                        notice_data["title"] = title_element.get_text(strip=True)
                        
                        # URL 추출
                        if title_element.has_attr('href'):
                            href = title_element['href']
                            # JavaScript 함수 처리
                            if href.startswith('javascript:'):
                                # 다양한 자바스크립트 패턴 처리
                                # 예: javascript:fnView('123456')
                                # 또는: javascript:view(123)
                                match = re.search(r"['\(](\d+)['\)]", href)
                                if match:
                                    article_id = match.group(1)
                                    # URL 패턴 추측
                                    domain = re.search(r'https?://(?:www\.)?([^/]+)', url).group(0)
                                    notice_data["url"] = f"{domain}/board/view?id={article_id}"
                            # 상대 경로 처리
                            elif not href.startswith(('http://', 'https://')):
                                notice_data["url"] = urljoin(url, href)
                            else:
                                notice_data["url"] = href
                    else:
                        notice_data["title"] = columns[1].get_text(strip=True)
                    
                    # 날짜와 조회수 처리
                    if len(columns) >= 4:
                        # 마지막에서 두 번째 열이 날짜
                        notice_data["date"] = columns[-2].get_text(strip=True)
                        # 마지막 열이 조회수
                        notice_data["views"] = columns[-1].get_text(strip=True)
                    else:
                        # 열이 3개인 경우 마지막 열이 날짜
                        notice_data["date"] = columns[-1].get_text(strip=True)
                        notice_data["views"] = "0"  # 조회수 정보가 없는 경우
                    
                    notices.append(notice_data)
            except Exception as e:
                logging.error(f"데이터 추출 중 오류 발생: {e}")
                continue
        
        logging.info(f"공지사항 크롤링 완료: {len(notices)}개")
        
    except Exception as e:
        logging.error(f"크롤링 중 오류 발생: {e}")
    
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
    
    # 결과 JSON 파일로 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join("..", "data", f"{site_name.replace('.', '_')}_notices_api_{timestamp}.json")
    try:
        # 백업 로직 제거 (이제 매번 새 파일이 생성되므로 백업 불필요)
        
        # 새 데이터 저장
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logging.info(f"크롤링 완료: {len(notices)}개 공지사항이 {filename}에 저장되었습니다.")
    except Exception as e:
        logging.error(f"파일 저장 중 오류 발생: {e}")
    
    return result

if __name__ == "__main__":
    # 예제 URL
    test_url = "https://isc.icehs.kr/boardCnts/list.do?boardID=11101&m=0202&s=inchon_ii"
    result = crawl_school_notices(test_url, "인천반도체고등학교")
    
    # 모든 공지사항 출력
    print("\n공지사항 목록:")
    for i, notice in enumerate(result["notices"], 1):
        print(f"{i}. {notice.get('title')} ({notice.get('date')})") 