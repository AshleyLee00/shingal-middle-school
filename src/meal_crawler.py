#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from datetime import datetime, timedelta
import json

def get_meal_info(api_key, school_code, start_date, end_date):
    """
    NEIS API를 통해 급식 정보를 가져옵니다.
    """
    base_url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    params = {
        "KEY": api_key,
        "Type": "json",
        "ATPT_OFCDC_SC_CODE": "J10",  # 경기도교육청
        "SD_SCHUL_CODE": school_code,  # 학교코드
        "MLSV_FROM_YMD": start_date,
        "MLSV_TO_YMD": end_date
    }
    
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if 'mealServiceDietInfo' not in data:
            return []
            
        meals = data['mealServiceDietInfo'][1]['row']
        return meals
    except Exception as e:
        print(f"급식 정보 가져오기 실패: {str(e)}")
        return []

def generate_meal_html(meals, school_name):
    """
    급식 정보를 HTML로 변환합니다.
    """
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

        .meal-container {
            display: flex; 
            flex-wrap: nowrap;
            gap: 12px;
            margin: 40px auto;
            padding: 20px;
            width: 95%;
            max-width: 2000px;
            background: #FFFFFF;
            border-radius: 20px;
            box-shadow: 0 8px 40px rgba(74, 27, 140, 0.18);
            overflow-x: auto;
        }

        .meal-day-container {
            display: flex;
            flex-direction: column;
            gap: 0;
            flex: 1;
            min-width: 200px;
        }

        .meal-date {
            background: #E7E5F5;
            border-radius: 15px 15px 0 0;
            padding: 15px;
            font-size: 2.2rem;
            font-weight: 900;
            color: #222;
            text-align: center;
            text-shadow: 1px 1px 0 rgba(255, 255, 255, 0.5);
        }

        .meal-card {
            background: white;
            border-radius: 0 0 15px 15px;
            padding: 20px;
            flex: 1;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            border: 1px solid #E5E5E5;
            border-top: none;
        }

        .meal-menu {
            font-size: 2.2rem;
            line-height: 1.5;
            color: #333;
            white-space: pre-line;
            font-weight: 500;
            letter-spacing: -0.02em;
        }

        .meal-menu span {
            display: block;
            margin-bottom: 10px;
            text-shadow: 0 0 1px rgba(0, 0, 0, 0.08);
        }

        .allergen {
            font-size: 1.8rem;
            color: #666;
            margin-top: 15px;
            font-weight: 500;
            border-top: 1px solid #eee;
            padding-top: 15px;
        }

        /* 반응형 디자인 수정 */
        @media (max-width: 1400px) {
            .meal-container {
                flex-wrap: nowrap;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                scrollbar-width: thin;
            }
            .meal-day-container {
                min-width: 300px;
            }
            .meal-date {
                font-size: 2.5rem;
            }
            .meal-menu {
                font-size: 2.5rem;
            }
            .allergen {
                font-size: 2rem;
            }
        }

        /* 스크롤바 스타일링 */
        .meal-container::-webkit-scrollbar {
            height: 12px;
        }

        .meal-container::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 6px;
        }

        .meal-container::-webkit-scrollbar-thumb {
            background: #B8B2E5;
            border-radius: 6px;
        }

        .meal-container::-webkit-scrollbar-thumb:hover {
            background: #9B7EDC;
        }

        .notice-text {
            text-align: center;
            color: #666;
            font-size: 1.8rem;
            margin: 20px auto;
            line-height: 1.5;
            max-width: 2000px;
            width: 95%;
            padding: 20px;
            background: #FFFFFF;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(74, 27, 140, 0.1);
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

        setInterval(updateDateTime, 1000);
        updateDateTime();
        fetchWeather();
    """

    meal_cards = ""
    for meal in meals:
        date = meal['MLSV_YMD']
        formatted_date = f"{date[4:6]}월 {date[6:8]}일 ({['월', '화', '수', '목', '금', '토', '일'][datetime.strptime(date, '%Y%m%d').weekday()]})"
        menu_items = meal['DDISH_NM'].split('<br/>')
        menu_html = ""
        
        for item in menu_items:
            # 알레르기 정보 추출
            allergens = []
            item_text = item
            for i in range(1, 20):
                if f"({i})" in item:
                    allergens.append(str(i))
                    item_text = item_text.replace(f"({i})", "")
            
            menu_html += f'<span>{item_text}</span>'
        
        allergen_text = ""
        if allergens:
            allergen_text = f'<div class="allergen">알레르기 유발 식품: {", ".join(allergens)}</div>'
        
        meal_cards += f"""
            <div class="meal-day-container">
                <div class="meal-date">{formatted_date}</div>
                <div class="meal-card">
                    <div class="meal-menu">
                        {menu_html}
                    </div>
                    {allergen_text}
                </div>
            </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>{school_name} 주간 식단표</title>
        <style>{css_style}</style>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
    </head>
    <body>
        <header class="page-header">
            <div class="header-left">
                <div class="header-main-title">주간 식단표</div>
            </div>
            <div class="header-right">
                <div class="weather">날씨 정보를 불러오는 중...</div>
                <div class="date-time" id="date-time"></div>
                <div class="school-name">{school_name}</div>
            </div>
        </header>
        
        <div class="meal-container">
            {meal_cards}
        </div>

        <div class="notice-text">
            위 식단은 학교 사정 및 기타 등에 따라 변경될 수 있습니다.<br>
            우리학교는 화학 조미료를 사용하지 않습니다.<br>
            국내산을 주재료로 사용하며 육류인 경우 식재료 검수시스템 등을 이용한 원산지 확인을 철저히 하고 있습니다.<br>
            김치도 국내산 재료만을 사용한 김치입니다.
        </div>

        <script>{js_code}</script>
    </body>
    </html>
    """
    return html_content

def main():
    # API 설정
    API_KEY = "dafe93db7c0d4c6eb8ba9a8f5aaee96b"
    SCHOOL_CODE = "7569032"  # 안양초등학교
    SCHOOL_NAME = "안양초등학교"
    
    # 날짜 설정 (이번 주 월~금)
    today = datetime.now()
    
    # 이번 주 월요일 찾기 (월요일=0, 일요일=6)
    days_since_monday = today.weekday()
    monday = today - timedelta(days=days_since_monday)
    friday = monday + timedelta(days=4)  # 월요일 + 4일 = 금요일
    
    # YYYYMMDD 형식으로 변환
    start_date_str = monday.strftime("%Y%m%d")
    end_date_str = friday.strftime("%Y%m%d")
    
    print(f"이번 주 급식 정보 가져오기: {start_date_str} ~ {end_date_str}")
    
    # 급식 정보 가져오기
    meals = get_meal_info(API_KEY, SCHOOL_CODE, start_date_str, end_date_str)
    
    if not meals:
        print("급식 정보를 가져오는데 실패했습니다.")
        return
    
    # HTML 생성
    html_content = generate_meal_html(meals, SCHOOL_NAME)
    
    # HTML 파일 저장
    import os
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(parent_dir, "meal_info.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    print("급식 정보 HTML 파일이 생성되었습니다.")

if __name__ == "__main__":
    main() 