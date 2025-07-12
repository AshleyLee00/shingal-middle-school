#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
공지사항 RSS 피드 생성기
크롤링된 공지사항 데이터를 RSS 피드로 변환하는 모듈입니다.
"""

import json
import os
import logging
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
import re

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='feed_generator.log',
    filemode='a'
)

def generate_rss_feed(json_file, output_file=None, feed_url=None):
    """
    크롤링된 JSON 파일을 RSS 피드로 변환합니다.
    
    Args:
        json_file (str): 크롤링된 공지사항 JSON 파일 경로
        output_file (str, optional): 출력할 RSS 파일 경로, 없으면 기본 이름 사용
        feed_url (str, optional): 피드 URL, 없으면 기본값 사용
    
    Returns:
        str: 생성된 RSS 파일 경로
    """
    try:
        # JSON 파일 로드
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 사이트 정보 추출
        site_name = data['meta']['source']
        site_url = data['meta']['url']
        
        # 출력 파일 이름 설정
        if not output_file:
            output_file = f"{site_name.replace('.', '_').replace(' ', '_')}_feed.xml"
        
        # 피드 생성기 초기화
        fg = FeedGenerator()
        
        # 피드 기본 정보 설정
        fg.id(site_url)
        fg.title(f'{site_name} 공지사항')
        fg.subtitle(f'{site_name} 공지사항 자동 피드')
        fg.link(href=site_url, rel='alternate')
        
        # 피드 URL이 제공된 경우 self 링크 추가
        if feed_url:
            fg.link(href=feed_url, rel='self')
        else:
            # 기본 feed_url 생성
            feed_url = f"http://localhost:5000/feeds/{output_file}"
            fg.link(href=feed_url, rel='self')
        
        fg.language('ko')
        fg.author({'name': site_name})
        fg.logo('https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Feed-icon.svg/128px-Feed-icon.svg.png')
        
        # 최종 업데이트 시간 (타임존 추가)
        update_time = datetime.strptime(data['meta']['last_updated'], '%Y-%m-%d %H:%M:%S')
        update_time = update_time.replace(tzinfo=timezone.utc)  # UTC 타임존 추가
        fg.updated(update_time)
        
        # 공지사항을 피드 항목으로 추가
        for notice in data['notices']:
            fe = fg.add_entry()
            
            # 고유 ID 설정 (URL이 있으면 URL 사용, 없으면 번호와 제목으로 생성)
            if notice.get('url'):
                fe.id(notice['url'])
            else:
                # 제목과 번호로 가상 ID 생성
                notice_id = f"{site_url}/notice/{notice.get('number', '')}-{re.sub(r'[^\w]', '-', notice.get('title', ''))}"
                fe.id(notice_id)
            
            # 제목 설정
            fe.title(notice.get('title', '제목 없음'))
            
            # 링크 설정
            if notice.get('url'):
                fe.link(href=notice['url'])
            else:
                fe.link(href=site_url)
            
            # 본문 생성 (간단한 HTML 형식)
            content = f"""
            <div>
                <h3>{notice.get('title', '제목 없음')}</h3>
                <p>작성자: {notice.get('author', '정보 없음')}</p>
                <p>날짜: {notice.get('date', '정보 없음')}</p>
                <p>조회수: {notice.get('views', '정보 없음')}</p>
                <a href="{notice.get('url', site_url)}">원문 보기</a>
            </div>
            """
            fe.content(content, type='html')
            
            # 요약
            fe.summary(f"{notice.get('title', '제목 없음')} - {notice.get('date', '')}")
            
            # 날짜 변환 시도
            try:
                # 다양한 날짜 형식 처리
                date_str = notice.get('date', '')
                date_formats = [
                    '%Y-%m-%d',              # 2023-01-15
                    '%Y.%m.%d',              # 2023.01.15
                    '%Y/%m/%d',              # 2023/01/15
                    '%Y-%m-%d %H:%M',        # 2023-01-15 14:30
                    '%Y.%m.%d %H:%M',        # 2023.01.15 14:30
                    '%Y/%m/%d %H:%M',        # 2023/01/15 14:30
                    '%Y-%m-%d %H:%M:%S',     # 2023-01-15 14:30:45
                ]
                
                parsed_date = None
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                
                if parsed_date:
                    # 타임존 정보 추가
                    parsed_date = parsed_date.replace(tzinfo=timezone.utc)
                    fe.published(parsed_date)
                    fe.updated(parsed_date)
                else:
                    # 날짜 파싱 실패시 현재 시간 사용 (타임존 정보 추가)
                    now = datetime.now(timezone.utc)
                    fe.published(now)
                    fe.updated(now)
            except Exception as e:
                logging.warning(f"날짜 변환 실패: {e}")
                # 현재 시간 사용 (타임존 정보 추가)
                now = datetime.now(timezone.utc)
                fe.published(now)
                fe.updated(now)
            
            # 작성자 정보
            if notice.get('author'):
                fe.author({'name': notice.get('author')})
        
        # RSS 파일 생성
        fg.rss_file(output_file, pretty=True)
        logging.info(f"RSS 피드 생성 완료: {output_file}")
        
        return output_file
        
    except Exception as e:
        logging.error(f"RSS 피드 생성 중 오류 발생: {e}")
        return None

if __name__ == "__main__":
    # JSON 파일 목록 찾기
    json_files = [f for f in os.listdir('.') if f.endswith('_notices_api.json')]
    
    for json_file in json_files:
        print(f"'{json_file}' 파일을 RSS 피드로 변환 중...")
        output_file = generate_rss_feed(json_file)
        if output_file:
            print(f"RSS 피드 생성 완료: {output_file}")
        else:
            print(f"RSS 피드 생성 실패: {json_file}") 