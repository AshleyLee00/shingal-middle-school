#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from datetime import datetime, timedelta
import calendar
import os

# 학교 및 API 정보
API_KEY = "dafe93db7c0d4c6eb8ba9a8f5aaee96b"  # 실제 서비스 시 본인 키로 교체
ATPT_OFCDC_SC_CODE = "J10"  # 경기도교육청
SD_SCHUL_CODE = "7569032"   # 안양초등학교
SCHOOL_NAME = "안양초등학교"

# 학사일정 가져오기 함수
def get_schedule_info(api_key, atpt_code, school_code, year, month):
    base_url = "https://open.neis.go.kr/hub/SchoolSchedule"
    start_date = f"{year}{str(month).zfill(2)}01"
    last_day = calendar.monthrange(year, month)[1]
    end_date = f"{year}{str(month).zfill(2)}{str(last_day).zfill(2)}"
    params = {
        "KEY": api_key,
        "Type": "json",
        "ATPT_OFCDC_SC_CODE": atpt_code,
        "SD_SCHUL_CODE": school_code,
        "AA_FROM_YMD": start_date,
        "AA_TO_YMD": end_date,
        "pIndex": 1,
        "pSize": 100
    }
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        if 'SchoolSchedule' not in data:
            return []
        rows = data['SchoolSchedule'][1]['row']
        return rows
    except Exception as e:
        print(f"학사일정 정보 가져오기 실패: {str(e)}")
        return []

def generate_schedule_html(schedules, school_name, year, month):
    # 날짜별 일정 매핑
    schedule_map = {}
    for item in schedules:
        date = item['AA_YMD']
        event = item['EVENT_NM']
        if date not in schedule_map:
            schedule_map[date] = []
        schedule_map[date].append(event)

    # 달력 한 줄(숫자) + 한 줄(요일) 생성 (동그라미/색상 적용)
    last_day = calendar.monthrange(year, month)[1]
    days_row = ''
    for d in range(1, last_day+1):
        date_str = f"{year}{str(month).zfill(2)}{str(d).zfill(2)}"
        has_event = date_str in schedule_map
        weekday = calendar.weekday(year, month, d)
        is_sun = (weekday == 6)
        circle_class = 'event-circle' if has_event else ''
        sun_class = 'sunday' if is_sun else ''
        days_row += f'<th><span class="calendar-num {circle_class} {sun_class}">{d}</span></th>'
    week_names = ['월', '화', '수', '목', '금', '토', '일']
    week_row = ''
    for d in range(1, last_day+1):
        weekday = calendar.weekday(year, month, d)
        is_sun = (weekday == 6)
        sun_class = 'sunday' if is_sun else ''
        week_row += f'<td class="{sun_class}">{week_names[weekday]}</td>'
    calendar_html = f'<table class="schedule-calendar" style="margin-bottom:18px;">'
    calendar_html += f'<tr>{days_row}</tr>'
    calendar_html += f'<tr>{week_row}</tr>'
    calendar_html += '</table>'

    # 일정 리스트 (날짜순, 표 형태)
    sorted_events = sorted([(d, e) for d, evs in schedule_map.items() for e in evs], key=lambda x: x[0])
    event_list_html = ''
    for date, event in sorted_events:
        event_list_html += f'<tr><td>{date[:4]}.{date[4:6]}.{date[6:]}</td><td>{event}</td></tr>'
    if not event_list_html:
        event_list_html = '<tr><td colspan="2">이번 달 학사일정이 없습니다.</td></tr>'

    # CSS: 달력 한 줄, 일정 표 스타일 추가
    css_style = '''
        @font-face {
            font-family: 'SeoulAlrim';
            src: url('font/SeoulAlrimTTF-Medium.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
        }
        body { background: #9B7EDC; font-family: 'SeoulAlrim', sans-serif; margin: 0; padding: 0; min-height: 100vh; }
        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(90deg, #9B7EDC, #6C4EB6);
            padding: 30px 90px;
            box-shadow: 0 8px 32px rgba(74, 27, 140, 0.18);
            flex-shrink: 0;
            min-height: 80px;
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
        .main-content {
            background: #fff;
            border-radius: 20px;
            box-shadow: 0 8px 40px rgba(74, 27, 140, 0.18);
            margin: 40px auto;
            padding: 40px 60px;
            max-width: 2000px;
            width: 95%;
        }
        .calendar-section { margin-bottom: 30px; }
        .calendar-section h2 {
            font-size: 2.5rem;
            color: #6C4EB6;
            margin-bottom: 20px;
        }
        .schedule-calendar {
            width: 100%;
            border-collapse: collapse;
            font-size: 2.2rem;
            margin-bottom: 30px;
            table-layout: fixed;
        }
        .schedule-calendar th, .schedule-calendar td {
            text-align: center;
            padding: 8px 0;
            border: none;
            width: calc(100% / 31);
        }
        .calendar-num {
            display: inline-block;
            width: 2.5rem;
            height: 2.5rem;
            line-height: 2.5rem;
            border-radius: 50%;
            font-size: 1.8rem;
            font-weight: 700;
            color: #222;
            background: transparent;
            transition: background 0.2s;
        }
        .event-circle {
            background: #E7E5F5;
            color: #9B7EDC;
        }
        .sunday {
            color: #e23a3a !important;
        }
        .schedule-calendar td.sunday {
            color: #e23a3a !important;
        }
        .event-list-section { margin-top: 20px; }
        .event-list-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 2.2rem;
        }
        .event-list-table td {
            border-bottom: 1px solid #eee;
            padding: 12px 8px;
            text-align: left;
        }
        .event-list-table td:first-child {
            color: #6C4EB6;
            font-weight: 700;
            width: 120px;
            font-size: 2rem;
        }
        .event-list-table td:last-child {
            color: #222;
            font-size: 2.2rem;
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
            .main-content { padding: 30px 40px; }
        }
        @media (max-width: 900px) {
            .main-content { padding: 20px; }
            .header-main-title { font-size: 4rem; }
            .calendar-section h2 { font-size: 2rem; }
            .schedule-calendar { font-size: 1.8rem; }
            .calendar-num {
                width: 2rem;
                height: 2rem;
                line-height: 2rem;
                font-size: 1.5rem;
            }
            .event-list-table { font-size: 1.8rem; }
            .event-list-table td:first-child { font-size: 1.6rem; }
            .event-list-table td:last-child { font-size: 1.8rem; }
        }
        @media (max-width: 600px) {
            .main-content { padding: 15px; }
            .header-main-title { font-size: 3rem; }
            .page-header { padding: 15px; }
            .calendar-section h2 { font-size: 1.8rem; }
            .schedule-calendar { font-size: 1.5rem; }
            .calendar-num {
                width: 1.8rem;
                height: 1.8rem;
                line-height: 1.8rem;
                font-size: 1.3rem;
            }
            .event-list-table { font-size: 1.5rem; }
            .event-list-table td:first-child { font-size: 1.4rem; }
            .event-list-table td:last-child { font-size: 1.5rem; }
        }
    '''
    js_code = '''
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
        setInterval(updateDateTime, 1000);
        updateDateTime();
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
                'Rain': { text: '비', icon: 'climate-forecast-rain-svgrepo-com.svg' },
                'Drizzle': { text: '이슬비', icon: 'drizzle.svg' },
                'Thunderstorm': { text: '뇌우', icon: 'cloud-forecast-lightning-svgrepo-com.svg' },
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
        fetchWeather();
    '''
    html_content = f'''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>{school_name} {year}년 {month}월 학사일정</title>
        <style>{css_style}</style>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
    </head>
    <body>
        <header class="page-header">
            <div class="header-left">
                <div class="header-main-title">학사일정</div>
            </div>
            <div class="header-right">
                <div class="weather">날씨 정보를 불러오는 중...</div>
                <div class="date-time" id="date-time"></div>
                <div class="school-name">{school_name}</div>
            </div>
        </header>
        <div class="main-content">
            <div class="calendar-section">
                <h2 style="font-size:1.3rem; color:#6C4EB6; margin-bottom:10px;">{year}년 {month}월</h2>
                {calendar_html}
            </div>
            <div class="event-list-section">
                <table class="event-list-table">
                    {event_list_html}
                </table>
            </div>
        </div>
        <script>{js_code}</script>
    </body>
    </html>
    '''
    return html_content

def main():
    # 오늘 기준 월
    now = datetime.now()
    year = now.year
    month = now.month
    schedules = get_schedule_info(API_KEY, ATPT_OFCDC_SC_CODE, SD_SCHUL_CODE, year, month)
    html_content = generate_schedule_html(schedules, SCHOOL_NAME, year, month)
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(parent_dir, "school_schedule.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    print("학사일정 HTML 파일이 생성되었습니다.")

if __name__ == "__main__":
    main() 