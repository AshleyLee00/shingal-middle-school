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

        @media (max-width: 480px) {
            .page-header {
                padding: 15px 10px;
                gap: 15px;
            }
            .header-left, .header-right {
                gap: 20px;
            }
            .header-main-title { 
                font-size: 2.5rem; 
                text-align: center;
            }
            .page-header .weather, 
            .page-header .date-time,
            .page-header .school-name {
                font-size: 1.6rem;
            }
            .page-header .weather-icon {
                width: 35px;
                height: 35px;
            }
            .page-header .weather-temp {
                font-size: 1.6rem;
            }
            .meal-container {
                margin: 20px auto;
                padding: 15px;
                width: 98%;
                flex-direction: column;
                flex-wrap: nowrap;
                max-height: none;
                overflow-x: visible;
                gap: 15px;
            }
            .meal-day-container {
                min-width: auto;
                flex: none;
                width: 100%;
            }
            .meal-date {
                font-size: 1.8rem;
                padding: 12px;
            }
            .meal-menu {
                font-size: 1.6rem;
                line-height: 1.3;
            }
            .meal-menu span {
                margin-bottom: 6px;
            }
            .allergen {
                font-size: 1.4rem;
                margin-top: 10px;
                padding-top: 10px;
            }
            .notice-text {
                font-size: 1.5rem;
                margin: 15px auto;
                padding: 15px;
                width: 98%;
            }
        }

        @media (max-height: 600px) {
            .page-header {
                padding: 10px 15px;
                min-height: 50px;
            }
            .header-main-title {
                font-size: 3rem;
            }
            .page-header .weather, 
            .page-header .date-time,
            .page-header .school-name {
                font-size: 1.6rem;
            }
            .page-header .weather-icon {
                width: 35px;
                height: 35px;
            }
            .meal-container {
                margin: 10px auto;
                padding: 10px;
                flex-direction: column;
                flex-wrap: nowrap;
                max-height: none;
                overflow-x: visible;
                gap: 10px;
            }
            .meal-day-container {
                min-width: auto;
                flex: none;
                width: 100%;
            }
            .meal-date {
                font-size: 1.6rem;
                padding: 6px;
            }
            .meal-menu {
                font-size: 1.5rem;
                line-height: 1.2;
            }
            .meal-menu span {
                margin-bottom: 4px;
            }
            .allergen {
                font-size: 1.3rem;
                margin-top: 6px;
                padding-top: 6px;
            }
            .notice-text {
                font-size: 1.4rem;
                margin: 8px auto;
                padding: 8px;
            }
        }

        .meal-container {
            display: flex; 
            flex-wrap: wrap;
            gap: 12px;
            margin: 20px auto;
            padding: 15px;
            width: 95%;
            max-width: 2000px;
            background: #FFFFFF;
            border-radius: 20px;
            box-shadow: 0 8px 40px rgba(74, 27, 140, 0.18);
            overflow-x: visible;
            max-height: none;
        }

        .meal-day-container {
            display: flex;
            flex-direction: column;
            gap: 0;
            flex: 1 1 300px;
            min-width: 200px;
        }

        .meal-date {
            background: #E7E5F5;
            border-radius: 15px 15px 0 0;
            padding: 12px;
            font-size: 2rem;
            font-weight: 900;
            color: #222;
            text-align: center;
            text-shadow: 1px 1px 0 rgba(255, 255, 255, 0.5);
        }

        .meal-card {
            background: white;
            border-radius: 0 0 15px 15px;
            padding: 15px;
            flex: 1;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            border: 1px solid #E5E5E5;
            border-top: none;
            overflow: visible;
        }

        .meal-menu {
            font-size: 2rem;
            line-height: 1.4;
            color: #333;
            white-space: pre-line;
            font-weight: 500;
            letter-spacing: -0.02em;
        }

        .meal-menu span {
            display: block;
            margin-bottom: 8px;
            text-shadow: 0 0 1px rgba(0, 0, 0, 0.08);
        }

        .allergen {
            font-size: 1.6rem;
            color: #666;
            margin-top: 12px;
            font-weight: 500;
            border-top: 1px solid #eee;
            padding-top: 12px;
        }

        /* 반응형 디자인 수정 */
        @media (max-width: 1400px) {
            .meal-container {
                flex-wrap: wrap;
                overflow-x: visible;
                max-height: none;
            }
            .meal-day-container {
                flex: 1 1 280px;
                min-width: 280px;
            }
            .meal-date {
                font-size: 2.2rem;
                padding: 10px;
            }
            .meal-menu {
                font-size: 2.2rem;
                line-height: 1.3;
            }
            .meal-menu span {
                margin-bottom: 8px;
            }
            .allergen {
                font-size: 1.8rem;
                margin-top: 10px;
                padding-top: 10px;
            }
        }

        @media (max-height: 800px) {
            .meal-container {
                flex-direction: column;
                flex-wrap: nowrap;
                max-height: none;
                overflow-x: visible;
                gap: 15px;
            }
            .meal-day-container {
                min-width: auto;
                flex: none;
                width: 100%;
            }
            .meal-menu {
                font-size: 1.8rem;
                line-height: 1.3;
            }
            .meal-menu span {
                margin-bottom: 6px;
            }
            .allergen {
                font-size: 1.5rem;
                margin-top: 10px;
                padding-top: 10px;
            }
        }



        .notice-text {
            text-align: center;
            color: #666;
            font-size: 1.6rem;
            margin: 15px auto;
            line-height: 1.4;
            max-width: 2000px;
            width: 95%;
            padding: 15px;
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
                    
                    // 현재 시간을 기준으로 낮/밤 판단
                    const now = new Date();
                    const currentHour = now.getHours();
                    const isDay = currentHour >= 6 && currentHour < 18; // 6시~18시는 낮
                    
                    const weatherInfo = getWeatherInfo(
                        data.weather[0].main, 
                        data.weather[0].description, 
                        isDay
                    );
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

        // OpenWeatherMap API 2.5와 커스텀 날씨 아이콘 매핑
        function getWeatherInfo(weatherMain, weatherDescription, isDay = true) {
            // 메인 날씨 조건별 매핑
            const mainWeatherMap = {
                'Clear': { 
                    text: '맑음', 
                    icon: 'weather/1.png' // 태양 아이콘
                },
                'Clouds': {
                    text: '구름',
                    icon: getCloudIcon(weatherDescription) // 구름 정도에 따라 다른 아이콘
                },
                'Rain': {
                    text: '비',
                    icon: getRainIcon(weatherDescription) // 비의 강도에 따라 다른 아이콘
                },
                'Drizzle': {
                    text: '이슬비',
                    icon: 'weather/14.png' // 물방울 아이콘
                },
                'Thunderstorm': {
                    text: '뇌우',
                    icon: 'weather/7.png' // 번개 아이콘
                },
                'Snow': {
                    text: '눈',
                    icon: 'weather/5.png' // 눈송이 아이콘
                },
                'Mist': {
                    text: '안개',
                    icon: 'weather/16.png' // 안개 아이콘
                },
                'Fog': {
                    text: '짙은 안개',
                    icon: 'weather/16.png' // 안개 아이콘
                },
                'Smoke': {
                    text: '연기',
                    icon: 'weather/16.png' // 안개 아이콘 (비슷한 시야 제한)
                },
                'Haze': {
                    text: '실안개',
                    icon: 'weather/16.png' // 안개 아이콘
                },
                'Dust': {
                    text: '먼지',
                    icon: 'weather/11.png' // 바람 아이콘
                },
                'Sand': {
                    text: '모래바람',
                    icon: 'weather/11.png' // 바람 아이콘
                },
                'Ash': {
                    text: '화산재',
                    icon: 'weather/16.png' // 안개 아이콘
                },
                'Squall': {
                    text: '돌풍',
                    icon: 'weather/11.png' // 바람 아이콘
                },
                'Tornado': {
                    text: '토네이도',
                    icon: 'weather/11.png' // 바람 아이콘
                }
            };

            // 구름 상태에 따른 아이콘 선택
            function getCloudIcon(description) {
                const desc = description.toLowerCase();
                if (desc.includes('few clouds')) {
                    return 'weather/3.png'; // 부분적으로 구름 낀 맑은 날씨
                } else if (desc.includes('scattered clouds') || desc.includes('broken clouds')) {
                    return 'weather/2.png'; // 구름 많음
                } else if (desc.includes('overcast')) {
                    return 'weather/8.png'; // 완전히 흐림
                }
                return 'weather/2.png'; // 기본 구름 아이콘
            }

            // 비의 강도에 따른 아이콘 선택
            function getRainIcon(description) {
                const desc = description.toLowerCase();
                if (desc.includes('light rain') || desc.includes('drizzle')) {
                    return 'weather/14.png'; // 가벼운 비 (물방울)
                } else if (desc.includes('heavy rain') || desc.includes('extreme rain')) {
                    return 'weather/6.png'; // 폭우
                } else if (desc.includes('thunderstorm')) {
                    return 'weather/10.png'; // 천둥번개를 동반한 비
                }
                return 'weather/4.png'; // 기본 비 아이콘
            }

            // 야간 모드 처리 (달 아이콘 사용)
            function getNightIcon(mainWeather) {
                if (mainWeather === 'Clear') {
                    return 'weather/15.png'; // 달과 별 아이콘
                }
                // 다른 날씨는 동일한 아이콘 사용
                return mainWeatherMap[mainWeather]?.icon || 'weather/1.png';
            }

            // 메인 날씨 정보 가져오기
            let weatherInfo = mainWeatherMap[weatherMain] || { 
                text: weatherMain, 
                icon: 'weather/1.png' 
            };

            // 야간인 경우 아이콘 변경
            if (!isDay && weatherMain === 'Clear') {
                weatherInfo.icon = getNightIcon(weatherMain);
            }

            return weatherInfo;
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
            알레르기 유발 식품에 대한 정보는 각 메뉴 옆의 숫자로 표시됩니다.<br>
            (1)난류, (2)우유, (3)메밀, (4)땅콩, (5)대두, (6)밀, (7)고등어, (8)게, (9)새우, (10)돼지고기, (11)복숭아, (12)토마토, (13)아황산류, (14)호두, (15)닭고기, (16)쇠고기, (17)오징어, (18)조개류(굴, 전복, 홍합 포함), (19)잣
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