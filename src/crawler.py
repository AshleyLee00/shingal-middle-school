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

def generate_html_base(title, items, school_name, item_type):
    css_style = """
        @font-face {
            font-family: 'SeoulAlrim';
            src: url('font/SeoulAlrimTTF-Medium.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
        }

        body {
            background: #9B7EDC;
            font-family: 'SeoulAlrim', sans-serif;
            margin: 0; 
            padding: 0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(90deg, #9B7EDC, #6C4EB6);
            padding: 30px 90px;
            box-shadow: 0 8px 32px rgba(74, 27, 140, 0.18);
            flex-shrink: 0;
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 30px;
        }

        .header-main-title {
            font-size: 5.8rem;
            font-weight: 900; 
            color: #FFFFFF;
            letter-spacing: -2px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
            margin: 0;
        }

        .header-right {
            display: flex;
            align-items: center;
            gap: 60px;
        }

        .page-header .weather, 
        .page-header .date-time {
            font-size: 2.2rem;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            gap: 12px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
        }

        .page-header .date-time {
            line-height: 1.3;
            text-align: right;
            font-size: 1.8rem;
        }

        .page-header .weather {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .page-header .weather-content {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 5px;
        }

        .page-header .weather-icon {
            width: 45px;
            height: 45px;
            flex-shrink: 0;
        }

        .page-header .weather-temp {
            font-size: 2.2rem;
        }

        .page-header .school-name {
            font-size: 2.2rem;
            color: #FFFFFF;
            font-weight: 700;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
            white-space: nowrap;
        }

        @media (max-width: 1380px) {
            .page-header {
                flex-direction: column;
                padding: 25px;
                gap: 20px;
            }
            .header-left, .header-right {
                width: 100%;
                justify-content: center;
                gap: 40px;
            }
            .header-main-title {
                font-size: 5rem;
            }
            .page-header .school-name {
                font-size: 2.2rem;
            }
        }

        @media (max-width: 768px) {
            .page-header {
                padding: 20px;
            }
            .header-main-title {
                font-size: 4rem;
            }
            .header-left, .header-right {
                flex-direction: column;
                gap: 30px;
            }
            .page-header .school-name {
                font-size: 2rem;
            }
        }

        .main-content {
            display: flex; 
            justify-content: center; 
            align-items: stretch;
            margin: 40px auto;
            background: #FFFFFF;
            border-radius: 20px;
            box-shadow: 0 8px 40px rgba(74, 27, 140, 0.18);
            gap: 0;
            width: 95%;
            max-width: 2000px;
            flex: 1;
        }

        .content-box {
            background: #fff;
            padding: 30px 60px 30px 80px;
            box-shadow: 0 10px 40px rgba(74,27,140,0.18);
            border-radius: 20px 0 0 20px;
            flex: 1;
            min-width: 0;
            display: flex;
            align-items: stretch;
        }

        .content-list {
            width: 100%;
            border-collapse: collapse;
            height: 100%;
            table-layout: fixed;
        }

        .content-list tr {
            border-bottom: 1px solid #E5E5E5;
            height: calc(100% / 7);  /* 7개의 항목이 동일한 높이를 가지도록 설정 */
        }

        .content-list td {
            font-size: 2.2rem;
            padding: 0 20px;
            border-bottom: 1px solid #ccc;
            vertical-align: middle;
        }

        .content-list td:first-child {
            width: 80%;  /* 첫 번째 열(내용)의 너비를 80%로 설정 */
        }

        .content-list td:last-child {
            width: 20%;  /* 두 번째 열(날짜)의 너비를 20%로 설정 */
            text-align: right;
            color: #666666;
            font-size: 1.8rem;
            white-space: nowrap;  /* 날짜가 한 줄로 표시되도록 설정 */
        }

        .school-img {
            width: 800px;
            height: calc(100% - 60px);  /* 상하 패딩 30px을 고려하여 계산 */
            border-radius: 0 20px 20px 0;
            object-fit: cover; 
            box-shadow: 0 10px 40px rgba(74,27,140,0.18);
            flex-shrink: 0;
            align-self: center;
        }

        @media (max-width: 1380px) { 
            .main-content {
                flex-wrap: wrap; 
                justify-content: center;
                gap: 20px;
                margin: 60px auto;
            }
            .school-img {
                width: 100%;
                height: 400px;
                margin: 0;
            }
        }

        @media (max-width: 768px) { 
            .main-content { 
                flex-direction: column; 
                align-items: stretch; 
                margin: 40px auto;
                width: 95%;
                gap: 20px;
            }
            .school-img { 
                height: 300px;
            }
            .content-box { 
                min-width: auto; 
            }
        }
    """

    js_code = """
        function updateDateTime() {
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const weekDays = ['일', '월', '화', '수', '목', '금', '토'];
            const weekDay = weekDays[now.getDay()];

            let hours = now.getHours();
            const ampm = hours >= 12 ? '오후' : '오전';
            hours = hours % 12;
            hours = hours ? hours : 12; 
            const displayHours = String(hours).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');

            const dateString = `${year}.${month}.${day} ${weekDay}요일`;
            const timeString = `${ampm} ${displayHours}:${minutes}`;

            document.getElementById('date-time').innerHTML = `${dateString}<br>${timeString}`;
        }
        setInterval(updateDateTime, 1000); updateDateTime();

        function weatherDescKor(desc) {
            const map = {
                'Clear': { text: '맑음', icon: 'sunny.svg' },
                'Clouds': { text: '흐림', icon: 'cloudy.svg' },
                'Rain': { text: '비', icon: 'rainy.svg' },
                'Drizzle': { text: '이슬비', icon: 'drizzle.svg' },
                'Thunderstorm': { text: '뇌우', icon: 'thunder.svg' },
                'Snow': { text: '눈', icon: 'snowy.svg' },
                'Mist': { text: '안개', icon: 'foggy.svg' },
                'Fog': { text: '안개', icon: 'foggy.svg' },
                'Smoke': { text: '연기', icon: 'smoke.svg' },
                'Haze': { text: '실안개', icon: 'haze.svg' },
                'Dust': { text: '먼지', icon: 'dust.svg' },
                'Sand': { text: '모래', icon: 'sand.svg' },
                'Ash': { text: '재', icon: 'ash.svg' },
                'Squall': { text: '돌풍', icon: 'windy.svg' },
                'Tornado': { text: '토네이도', icon: 'tornado.svg' }
            };
            return map[desc] || { text: desc, icon: 'default.svg' };
        }

        function fetchWeather() {
            const apiKey = '91fff999310c2bdea1978b3f0925fb38';
            const lat = 37.401;
            const lon = 126.922;
            const url = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${apiKey}&units=metric`;
            fetch(url)
                .then(res => res.json())
                .then(data => {
                    if (!data.weather || !data.weather[0]) throw new Error('Invalid weather data');
                    const weatherInfo = weatherDescKor(data.weather[0].main);
                    const temp = Math.round(data.main.temp);
                    document.querySelector('.weather').innerHTML =
                        `<img class='weather-icon' src='images/${weatherInfo.icon}' alt='날씨아이콘'>
                         <div class='weather-content'>
                            <div>${weatherInfo.text}</div>
                            <div class='weather-temp'>${temp}℃</div>
                         </div>`;
                })
                .catch(e => {
                    console.error("Weather fetch error: ", e);
                    document.querySelector('.weather').textContent = '날씨 정보를 불러올 수 없습니다';
                });
        }
        fetchWeather();
    """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>{school_name} {title}</title>
        <style>{css_style}</style>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
    </head>
    <body>
        <header class="page-header">
            <div class="header-left">
                <div class="header-main-title">{title}</div>
            </div>
            <div class="header-right">
                <div class="weather">날씨 정보를 불러오는 중...</div>
                <div class="date-time" id="date-time"></div>
                <div class="school-name">{school_name}</div>
            </div>
        </header>
        <div class="main-content">
            <div class="content-box">
                <table class="content-list">
                    { "".join(f"<tr><td>{item['title']}</td><td>{item['date']}</td></tr>" for item in items) }
                </table>
            </div>
            <img class="school-img" src="images/안양초등학교.png" alt="학교 전경">
        </div>
        <script>{js_code}</script>
    </body>
    </html>
    """
    return html_content

def generate_notice_html(notices, school_name):
    return generate_html_base("공지사항", notices, school_name, "notice")

def generate_letter_html(letters, school_name):
    return generate_html_base("가정통신문", letters, school_name, "letter")

def main():
    # 학교 정보
    school_info = {
        "name": "안양초등학교",
        "notice_url": "https://anyang-e.goeay.kr/anyang-e/na/ntt/selectRssFeed.do?mi=4492&bbsId=1821",
        "letter_url": "https://anyang-e.goeay.kr/anyang-e/na/ntt/selectRssFeed.do?mi=4493&bbsId=1822"
    }
    
    # 공지사항 크롤링
    print(f"{school_info['name']} 공지사항 크롤링 시작...")
    notices_result = crawl_school_notices(
        school_info["notice_url"],
        school_info["name"]
    )
    if 'notices' in notices_result and notices_result['notices']:
        notices_result['notices'] = notices_result['notices'][:7]
    print(f"공지사항 크롤링 완료: {len(notices_result.get('notices', []))}개")
    
    # 가정통신문 크롤링
    print(f"{school_info['name']} 가정통신문 크롤링 시작...")
    letters_result = crawl_school_letters(
        school_info["letter_url"],
        school_info["name"]
    )
    if 'letters' in letters_result and letters_result['letters']:
        letters_result['letters'] = letters_result['letters'][:7]
    print(f"가정통신문 크롤링 완료: {len(letters_result.get('letters', []))}개")
    
    # HTML 파일 생성
    notice_html = generate_notice_html(notices_result.get('notices', []), school_info['name'])
    letter_html = generate_letter_html(letters_result.get('letters', []), school_info['name'])
    
    # HTML 파일 저장
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(parent_dir, "digital_signage.html"), "w", encoding="utf-8") as f:
        f.write(notice_html)
    with open(os.path.join(parent_dir, "family_letters.html"), "w", encoding="utf-8") as f:
        f.write(letter_html)
    print("HTML 파일들이 생성되었습니다.")

if __name__ == "__main__":
    main() 