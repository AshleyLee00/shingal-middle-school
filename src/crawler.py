#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
학교 홈페이지 공지사항과 가정통신문 크롤러
두 크롤러를 통합하여 실행하는 메인 스크립트입니다.
"""

import os
from notice_crawler import crawl_school_notices
from family_letter_crawler import crawl_school_letters

def main():
    # 학교 정보
    school_info = {
        "name": "인천반도체고등학교",
        "notice_url": "https://isc.icehs.kr/boardCnts/list.do?boardID=11101&m=0202&s=inchon_ii",
        "letter_url": "https://isc.icehs.kr/boardCnts/list.do?boardID=11107&m=0203&s=inchon_ii"
    }
    
    # data 디렉토리 생성
    os.makedirs("data", exist_ok=True)
    
    # 공지사항 크롤링
    print(f"{school_info['name']} 공지사항 크롤링 시작...")
    notices_result = crawl_school_notices(
        school_info["notice_url"],
        school_info["name"]
    )
    print(f"공지사항 크롤링 완료: {len(notices_result['notices'])}개")
    
    # 가정통신문 크롤링
    print(f"{school_info['name']} 가정통신문 크롤링 시작...")
    letters_result = crawl_school_letters(
        school_info["letter_url"],
        school_info["name"]
    )
    print(f"가정통신문 크롤링 완료: {len(letters_result['letters'])}개")

if __name__ == "__main__":
    main() 