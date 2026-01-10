#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
학교 홈페이지 공지사항 크롤러
HTML 페이지를 직접 크롤링하여 공지사항을 수집하는 모듈입니다.
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
log_file = os.path.join(log_dir, 'notice_crawler.log')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_file,
    filemode='w',
    encoding='utf-8'
)

def crawl_school_notices(url, site_name=None):
    """
    학교 홈페이지 공지사항을 HTML 페이지에서 직접 크롤링합니다.
    
    Args:
        url (str): 공지사항 목록 페이지 URL
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
    
    logging.info(f"{site_name} 공지사항 HTML 크롤러 시작...")
    
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
            "notices": [],
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
        
        # 공지사항 테이블 찾기
        # #subContent > div > div.BD_list > table > tbody
        tbody = soup.select_one('#subContent > div > div.BD_list > table > tbody')
        
        if not tbody:
            # 단계별로 찾기 시도
            sub_content = soup.find(id='subContent')
            if sub_content:
                div = sub_content.find('div')
                if div:
                    bd_list = div.find('div', class_='BD_list')
                    if bd_list:
                        table = bd_list.find('table')
                        if table:
                            tbody = table.find('tbody')
        
        if not tbody:
            logging.error("공지사항 테이블을 찾을 수 없습니다.")
            return {
                "notices": [],
                "meta": {
                    "total_count": 0,
                    "last_updated": datetime.now().strftime("%Y-%m-%d"),
                    "source": site_name,
                    "url": url,
                    "error": "공지사항 테이블을 찾을 수 없습니다."
                }
            }
        
        # 테이블의 모든 행(tr)을 찾습니다
        rows = tbody.find_all('tr')
        notices = []
        
        for row in rows:
            # 헤더 행은 건너뜁니다
            if row.find('th'):
                continue
                
            # td 요소들을 찾습니다
            cells = row.find_all('td')
            if len(cells) < 4:  # 최소 4개 컬럼 필요 (번호, 제목, 작성자, 등록일)
                continue
                
            try:
                # 번호 추출
                number_cell = cells[0]
                number = number_cell.get_text(strip=True)
                
                # 제목과 링크 추출 - td.ta_l 클래스를 가진 셀의 a 태그
                title_cell = row.find('td', class_='ta_l')
                if title_cell:
                    title_link = title_cell.find('a')
                    if title_link:
                        title = title_link.get_text(strip=True)
                        link = title_link.get('href', '')
                        
                        # JavaScript 링크 처리
                        if link.startswith('javascript:'):
                            onclick = title_link.get('onclick', '')
                            if onclick:
                                # onclick에서 파라미터 추출
                                match = re.search(r"['\"](\d+)['\"]", onclick)
                                if match:
                                    ntt_sn = match.group(1)
                                    # 상세보기 URL 생성
                                    link = f"/shingal-m/na/ntt/selectNttView.do?mi=14328&bbsId=8186&nttSn={ntt_sn}"
                                else:
                                    link = ""
                        
                        if link and not link.startswith('http'):
                            link = urljoin(url, link)
                    else:
                        title = title_cell.get_text(strip=True)
                        link = ""
                else:
                    # fallback: 두 번째 셀에서 제목 찾기
                    title_cell = cells[1]
                    title_link = title_cell.find('a')
                    if title_link:
                        title = title_link.get_text(strip=True)
                        link = title_link.get('href', '')
                        if link and not link.startswith('http'):
                            link = urljoin(url, link)
                    else:
                        title = title_cell.get_text(strip=True)
                        link = ""
                
                # 작성자 추출
                author = ""
                for cell in cells:
                    cell_text = cell.get_text(strip=True)
                    # 한글 이름 패턴
                    if re.match(r'^[가-힣\*]+$', cell_text) and 2 <= len(cell_text) <= 10:
                        author = cell_text
                        break
                
                # 날짜 추출 (일반적으로 4번째 셀, 인덱스 3)
                date_text = ""
                # 먼저 특정 인덱스에서 찾기 시도
                if len(cells) > 3:
                    date_cell = cells[3]
                    cell_text = date_cell.get_text(strip=True)
                    # YYYY.MM.DD 형식 찾기 (셀에 다른 텍스트가 있을 수 있음)
                    date_match = re.search(r'(\d{4}\.\d{2}\.\d{2})', cell_text)
                    if date_match:
                        date_text = date_match.group(1)
                
                # 인덱스에서 못 찾았으면 모든 셀에서 찾기
                if not date_text:
                    for idx, cell in enumerate(cells):
                        cell_text = cell.get_text(strip=True)
                        # YYYY.MM.DD 형식 찾기 (셀에 다른 텍스트가 있을 수 있음)
                        date_match = re.search(r'(\d{4}\.\d{2}\.\d{2})', cell_text)
                        if date_match:
                            date_text = date_match.group(1)
                            logging.debug(f"날짜를 인덱스 {idx}에서 찾았습니다: {date_text}")
                            break
                
                if not date_text:
                    logging.warning(f"날짜를 찾을 수 없습니다. 셀 내용: {[cell.get_text(strip=True) for cell in cells]}")
                
                # 조회수 추출 (있는 경우, 보통 마지막 셀)
                views = "0"
                if len(cells) > 4:
                    # 마지막 셀이 조회수일 가능성이 높음
                    views_cell = cells[-1]
                    views_text = views_cell.get_text(strip=True)
                    if views_text.isdigit() and int(views_text) > 0:
                        views = views_text
                else:
                    # 모든 셀에서 숫자 찾기 (번호 제외)
                    for idx, cell in enumerate(cells):
                        cell_text = cell.get_text(strip=True)
                        # 번호 셀(첫 번째)은 제외하고, 작은 숫자는 조회수일 가능성 낮음
                        if idx > 0 and cell_text.isdigit() and int(cell_text) > 0 and int(cell_text) < 100000:
                            views = cell_text
                
                # 날짜 형식 정리 (YYYY.MM.DD 형식을 YYYY-MM-DD로 변환)
                try:
                    if re.match(r'\d{4}\.\d{2}\.\d{2}', date_text):
                        formatted_date = date_text.replace('.', '-')
                    else:
                        formatted_date = date_text
                except:
                    formatted_date = date_text
                
                notice_data = {
                    "number": number,
                    "title": title,
                    "author": author,
                    "date": formatted_date,
                    "views": views,
                    "url": link
                }
                
                notices.append(notice_data)
                    
            except Exception as e:
                logging.error(f"행 파싱 중 오류 발생: {e}")
                continue
        
        logging.info(f"공지사항 HTML 크롤링 완료: {len(notices)}개")
        
    except Exception as e:
        logging.error(f"HTML 파싱 오류: {e}")
        return {
            "notices": [],
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
        "notices": notices,
        "meta": {
            "total_count": len(notices),
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "source": site_name,
            "url": url
        }
    }
    
    logging.info(f"공지사항 HTML 크롤링 완료: {len(notices)}개")
    return result

if __name__ == "__main__":
    # 신갈중학교 공지사항 목록 페이지 URL
    test_url = "https://shingal-m.goeyi.kr/shingal-m/na/ntt/selectNttList.do?mi=14328&bbsId=8186"
    result = crawl_school_notices(test_url, "신갈중학교")
    
    # 모든 공지사항 출력
    print("\n공지사항 목록:")
    for i, notice in enumerate(result["notices"], 1):
        print(f"{notice.get('title')}\t{notice.get('date')}") 