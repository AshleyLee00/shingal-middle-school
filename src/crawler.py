#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
학교 홈페이지 공지사항과 가정통신문 크롤러
두 크롤러를 통합하여 실행하는 메인 스크립트입니다.
"""

import os
import requests
from notice_crawler import crawl_school_notices
from family_letter_crawler import crawl_school_letters
from datetime import datetime
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def generate_notice_html(notices, school_name):
    # CSS 스타일을 일반 문자열로 정의
    css_style = """
        @font-face {
            font-family: 'NanumSquare';
            src: url('https://cdn.jsdelivr.net/gh/moonspam/NanumSquare@1.0/nanumsquare.css');
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'NanumSquare', 'Noto Sans KR', sans-serif;
            background-color: #0a192f;
            color: white;
            overflow: hidden;
            margin: 0;
            padding: 0;
            line-height: 1.4;
        }
        
        .container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            width: 100vw;
            padding: 30px;
        }
        
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 20px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 20px;
        }
        
        .school-logo {
            height: 80px;
            width: auto;
        }
        
        .title {
            font-size: 3.5rem;
            font-weight: 800;
            text-align: center;
            flex-grow: 1;
            color: #ffffff;
            margin: 0 20px;
        }
        
        .clock {
            font-size: 2.5rem;
            font-weight: 500;
            color: #f1c40f;
            text-align: right;
        }
        
        .date {
            font-size: 1.8rem;
            font-weight: 400;
            color: #f1c40f;
            margin-top: 5px;
        }
        
        .content {
            display: flex;
            flex-grow: 1;
            overflow: hidden;
        }
        
        .notice-container {
            flex: 1;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        
        .notice-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background-color: #1a365d;
            border-radius: 10px 10px 0 0;
            margin-bottom: 10px;
        }
        
        .notice-title {
            font-size: 2.2rem;
            font-weight: 700;
            color: #ffffff;
        }
        
        .notice-source {
            font-size: 1.6rem;
            color: #f1c40f;
        }
        
        .notice-list {
            list-style: none;
            overflow: hidden;
            flex-grow: 1;
        }
        
        .notice-item {
            display: flex;
            flex-direction: column;
            margin-bottom: 20px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            transition: transform 0.5s ease;
            animation: fadeIn 1s;
        }
        
        .notice-item-title {
            font-size: 3.2rem;
            font-weight: 700;
            margin-bottom: 15px;
            color: #ffffff;
            word-break: keep-all;
            line-height: 1.3;
        }
        
        .notice-item-info {
            display: flex;
            justify-content: flex-end;
            font-size: 2.4rem;
            margin-bottom: 10px;
            color: #8bc6fc;
        }
        
        .notice-item-date {
            color: #f39c12;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideUp {
            from { transform: translateY(0); }
            to { transform: translateY(-100%); }
        }
        
        /* 반응형 디자인 */
        @media (max-width: 1200px) {
            .title {
                font-size: 3.2rem;
            }
            .clock {
                font-size: 2.4rem;
            }
            .notice-item-title {
                font-size: 2.8rem;
            }
            .notice-item-info {
                font-size: 2rem;
            }
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            .title {
                font-size: 2.6rem;
            }
            .clock {
                font-size: 2.2rem;
            }
            .notice-header {
                flex-direction: column;
                align-items: flex-start;
            }
            .notice-title {
                font-size: 2.4rem;
                margin-bottom: 5px;
            }
            .notice-source {
                font-size: 2rem;
            }
            .notice-item-title {
                font-size: 2.4rem;
            }
            .notice-item-info {
                flex-direction: column;
                font-size: 1.8rem;
            }
        }
    """

    # JavaScript 코드를 일반 문자열로 정의
    js_code = """
        // 시계 업데이트 함수
        function updateClock() {
            const now = new Date();
            
            // 시간 표시
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            document.getElementById('clock').textContent = `${hours}:${minutes}:${seconds}`;
            
            // 날짜 표시
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            
            const weekDays = ['일', '월', '화', '수', '목', '금', '토'];
            const weekDay = weekDays[now.getDay()];
            
            document.getElementById('date').textContent = 
                `${year}년 ${month}월 ${day}일 (${weekDay})`;
        }
        
        // 1초마다 시계 업데이트
        setInterval(updateClock, 1000);
        updateClock(); // 초기 업데이트
        
        // 공지사항 순환 설정
        function setupNoticeRotation() {
            const noticeItems = document.querySelectorAll('.notice-item');
            if (noticeItems.length <= 1) return;
            
            let currentIndex = 0;
            const visibleCount = 6;
            
            function updateVisibleNotices() {
                noticeItems.forEach((item, index) => {
                    const shouldShow = Array.from({length: visibleCount}, (_, i) => 
                        (currentIndex + i) % noticeItems.length
                    ).includes(index);
                    
                    item.style.display = shouldShow ? 'flex' : 'none';
                });
            }
            
            updateVisibleNotices();
            
            setInterval(() => {
                currentIndex = (currentIndex + 1) % noticeItems.length;
                updateVisibleNotices();
            }, 8000);
        }
        
        // 페이지 로드 시 공지사항 순환 시작
        document.addEventListener('DOMContentLoaded', setupNoticeRotation);
    """

    # HTML 템플릿 생성
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{school_name} 공지사항</title>
    <style>
    {css_style}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <header class="header">
            <img class="school-logo" id="school-logo" src="images/인천반도체고.jpg" alt="{school_name} 로고">
            <h1 class="title">{school_name} 공지사항</h1>
            <div>
                <div class="clock" id="clock">00:00:00</div>
                <div class="date" id="date">0000년 00월 00일</div>
            </div>
        </header>
        
        <main class="content">
            <div class="notice-container">
                <div class="notice-header">
                    <div class="notice-title">최신 공지사항</div>
                    <div class="notice-source">총 {len(notices)}개의 공지사항</div>
                </div>
                <ul class="notice-list" id="notice-list">
"""
    
    # 공지사항 추가
    for notice in notices:
        html_content += f"""
                    <li class="notice-item">
                        <div class="notice-item-title">{notice['title']}</div>
                        <div class="notice-item-info">
                            <div class="notice-item-date">{notice['date']}</div>
                        </div>
                    </li>"""
    
    # HTML 닫기
    html_content += f"""
                </ul>
            </div>
        </main>
    </div>

    <script>
    {js_code}
    </script>
</body>
</html>"""
    
    return html_content

def generate_letter_html(letters, school_name):
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{school_name} 가정통신문</title>
    <style>
        @font-face {{
            font-family: 'NanumSquare';
            src: url('https://cdn.jsdelivr.net/gh/moonspam/NanumSquare@1.0/nanumsquare.css');
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: 'NanumSquare', 'Noto Sans KR', sans-serif;
            background-color: #0a192f;
            color: white;
            overflow: hidden;
            margin: 0;
            padding: 0;
            line-height: 1.4;
        }}
        
        .container {{
            display: flex;
            flex-direction: column;
            height: 100vh;
            width: 100vw;
            padding: 30px;
        }}
        
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 20px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 20px;
        }}
        
        .school-logo {{
            height: 80px;
            width: auto;
        }}
        
        .title {{
            font-size: 3.5rem;
            font-weight: 800;
            text-align: center;
            flex-grow: 1;
            color: #ffffff;
            margin: 0 20px;
        }}
        
        .clock {{
            font-size: 2.5rem;
            font-weight: 500;
            color: #f1c40f;
            text-align: right;
        }}
        
        .date {{
            font-size: 1.8rem;
            font-weight: 400;
            color: #f1c40f;
            margin-top: 5px;
        }}
        
        .content {{
            display: flex;
            flex-grow: 1;
            overflow: hidden;
        }}
        
        .letter-container {{
            flex: 1;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        
        .letter-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background-color: #1a365d;
            border-radius: 10px 10px 0 0;
            margin-bottom: 10px;
        }}
        
        .letter-title {{
            font-size: 2.2rem;
            font-weight: 700;
            color: #ffffff;
        }}
        
        .letter-source {{
            font-size: 1.6rem;
            color: #f1c40f;
        }}
        
        .letter-list {{
            list-style: none;
            overflow: hidden;
            flex-grow: 1;
        }}
        
        .letter-item {{
            display: flex;
            flex-direction: column;
            margin-bottom: 20px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            transition: transform 0.5s ease;
            animation: fadeIn 1s;
        }}
        
        .letter-item-title {{
            font-size: 3.2rem;
            font-weight: 700;
            margin-bottom: 15px;
            color: #ffffff;
            word-break: keep-all;
            line-height: 1.3;
        }}
        
        .letter-item-info {{
            display: flex;
            justify-content: flex-end;
            font-size: 2.4rem;
            margin-bottom: 10px;
            color: #8bc6fc;
        }}
        
        .letter-item-date {{
            color: #f39c12;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        @keyframes slideUp {{
            from {{ transform: translateY(0); }}
            to {{ transform: translateY(-100%); }}
        }}
        
        /* 반응형 디자인 */
        @media (max-width: 1200px) {{
            .title {{
                font-size: 3.2rem;
            }}
            .clock {{
                font-size: 2.4rem;
            }}
            .letter-item-title {{
                font-size: 2.8rem;
            }}
            .letter-item-info {{
                font-size: 2rem;
            }}
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}
            .title {{
                font-size: 2.6rem;
            }}
            .clock {{
                font-size: 2.2rem;
            }}
            .letter-header {{
                flex-direction: column;
                align-items: flex-start;
            }}
            .letter-title {{
                font-size: 2.4rem;
                margin-bottom: 5px;
            }}
            .letter-source {{
                font-size: 2rem;
            }}
            .letter-item-title {{
                font-size: 2.4rem;
            }}
            .letter-item-info {{
                flex-direction: column;
                font-size: 1.8rem;
            }}
        }}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <header class="header">
            <img class="school-logo" id="school-logo" src="images/인천반도체고.jpg" alt="{school_name} 로고">
            <h1 class="title">{school_name} 가정통신문</h1>
            <div>
                <div class="clock" id="clock">00:00:00</div>
                <div class="date" id="date">0000년 00월 00일</div>
            </div>
        </header>
        
        <main class="content">
            <div class="letter-container">
                <div class="letter-header">
                    <div class="letter-title">최신 가정통신문</div>
                    <div class="letter-source">총 {len(letters)}개의 가정통신문</div>
                </div>
                <ul class="letter-list" id="letter-list">
"""
    
    # 가정통신문 추가
    for letter in letters:
        html_content += f"""
                    <li class="letter-item">
                        <div class="letter-item-title">{letter['title']}</div>
                        <div class="letter-item-info">
                            <div class="letter-item-date">{letter['date']}</div>
                        </div>
                    </li>"""
    
    html_content += """
                </ul>
            </div>
        </main>
    </div>

    <script>
        // 시계 업데이트 함수
        function updateClock() {
            const now = new Date();
            
            // 시간 표시
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            document.getElementById('clock').textContent = `${hours}:${minutes}:${seconds}`;
            
            // 날짜 표시
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            
            const weekDays = ['일', '월', '화', '수', '목', '금', '토'];
            const weekDay = weekDays[now.getDay()];
            
            document.getElementById('date').textContent = 
                `${year}년 ${month}월 ${day}일 (${weekDay})`;
        }
        
        // 1초마다 시계 업데이트
        setInterval(updateClock, 1000);
        updateClock(); // 초기 업데이트
        
        // 가정통신문 순환 설정
        function setupLetterRotation() {
            const letterItems = document.querySelectorAll('.letter-item');
            if (letterItems.length <= 1) return;
            
            let currentIndex = 0;
            const visibleCount = 6;
            
            function updateVisibleLetters() {
                letterItems.forEach((item, index) => {
                    const shouldShow = Array.from({length: visibleCount}, (_, i) => 
                        (currentIndex + i) % letterItems.length
                    ).includes(index);
                    
                    item.style.display = shouldShow ? 'flex' : 'none';
                });
            }
            
            updateVisibleLetters();
            
            setInterval(() => {
                currentIndex = (currentIndex + 1) % letterItems.length;
                updateVisibleLetters();
            }, 8000);
        }
        
        // 페이지 로드 시 가정통신문 순환 시작
        document.addEventListener('DOMContentLoaded', setupLetterRotation);
    </script>
</body>
</html>"""
    
    return html_content

def main():
    # 학교 정보
    school_info = {
        "name": "인천반도체고등학교",
        "notice_url": "https://isc.icehs.kr/boardCnts/list.do?boardID=11101&m=0202&s=inchon_ii",
        "letter_url": "https://isc.icehs.kr/boardCnts/list.do?boardID=11107&m=0203&s=inchon_ii"
    }
    
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
    
    # HTML 파일 생성
    notice_html = generate_notice_html(notices_result['notices'], school_info['name'])
    letter_html = generate_letter_html(letters_result['letters'], school_info['name'])
    
    # HTML 파일 저장 (상위 디렉토리에 저장)
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(parent_dir, "digital_signage.html"), "w", encoding="utf-8") as f:
        f.write(notice_html)
    with open(os.path.join(parent_dir, "family_letters.html"), "w", encoding="utf-8") as f:
        f.write(letter_html)
    print("HTML 파일들이 생성되었습니다.")

if __name__ == "__main__":
    main() 