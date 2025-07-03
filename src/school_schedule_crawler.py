#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from datetime import datetime, timedelta
import calendar
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 학교 및 API 정보
API_KEY = os.getenv("NEIS_API_KEY", "dafe93db7c0d4c6eb8ba9a8f5aaee96b")  # 환경변수에서 가져오거나 기본값 사용
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

    # 달력 생성 (기본: 한 줄 형태, 세로 축소시: 표 형태)
    last_day = calendar.monthrange(year, month)[1]
    
    # 기본 달력 (한 줄 형태)
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
    
    # 표 형태 달력 (세로 축소시 사용)
    table_calendar_html = ''
    week_names = ['월', '화', '수', '목', '금', '토', '일']
    
    # 첫 주 시작일 계산
    first_weekday = calendar.weekday(year, month, 1)
    current_day = 1
    
    table_calendar_html += '<table class="table-calendar">'
    # 요일 헤더 추가
    table_calendar_html += '<tr>'
    for day_name in week_names:
        is_sun = (day_name == '일')
        sun_class = 'sunday' if is_sun else ''
        table_calendar_html += f'<th class="{sun_class}">{day_name}</th>'
    table_calendar_html += '</tr>'
    table_calendar_html += '<tr>'
    for i in range(7):
        if i < first_weekday:
            table_calendar_html += '<td></td>'
        else:
            date_str = f"{year}{str(month).zfill(2)}{str(current_day).zfill(2)}"
            has_event = date_str in schedule_map
            is_sun = (i == 6)
            circle_class = 'event-circle' if has_event else ''
            sun_class = 'sunday' if is_sun else ''
            table_calendar_html += f'<td class="{sun_class}"><span class="calendar-num {circle_class}">{current_day}</span></td>'
            current_day += 1
    table_calendar_html += '</tr>'
    
    # 나머지 주들
    while current_day <= last_day:
        table_calendar_html += '<tr>'
        for i in range(7):
            if current_day <= last_day:
                date_str = f"{year}{str(month).zfill(2)}{str(current_day).zfill(2)}"
                has_event = date_str in schedule_map
                is_sun = (i == 6)
                circle_class = 'event-circle' if has_event else ''
                sun_class = 'sunday' if is_sun else ''
                table_calendar_html += f'<td class="{sun_class}"><span class="calendar-num {circle_class}">{current_day}</span></td>'
                current_day += 1
            else:
                table_calendar_html += '<td></td>'
        table_calendar_html += '</tr>'
    
    table_calendar_html += '</table>'
    
    calendar_html = f'<div class="calendar-wrapper">'
    calendar_html += f'<table class="schedule-calendar" style="margin-bottom:18px;">'
    calendar_html += f'<tr>{days_row}</tr>'
    calendar_html += f'<tr>{week_row}</tr>'
    calendar_html += '</table>'
    calendar_html += f'<div class="table-calendar-wrapper">{table_calendar_html}</div>'
    calendar_html += '</div>'

    # 일정 리스트 (날짜순, 표 형태)
    sorted_events = sorted([(d, e) for d, evs in schedule_map.items() for e in evs], key=lambda x: x[0])
    
    # 일정을 두 부분으로 나누기
    total_events = len(sorted_events)
    if total_events == 0:
        event_list_html = '<tr><td colspan="2">이번 달 학사일정이 없습니다.</td></tr>'
    else:
        # 첫 번째 부분 (처음 6개)
        first_part_html = ''
        for i, (date, event) in enumerate(sorted_events[:6]):
            first_part_html += f'<tr><td>{date[:4]}.{date[4:6]}.{date[6:]}</td><td>{event}</td></tr>'
        
        # 두 번째 부분 (나머지)
        second_part_html = ''
        for date, event in sorted_events[6:]:
            second_part_html += f'<tr><td>{date[:4]}.{date[4:6]}.{date[6:]}</td><td>{event}</td></tr>'
        
        event_list_html = {
            'first_part': first_part_html,
            'second_part': second_part_html,
            'has_second_part': len(sorted_events) > 6
        }

    # CSS: 달력 한 줄, 일정 표 스타일 추가
    css_style = '''
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
            height: 100vh; 
            overflow: hidden;
        }
        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(90deg, #9B7EDC, #6C4EB6);
            padding: 30px 90px;
            box-shadow: 0 8px 32px rgba(74, 27, 140, 0.18);
            flex-shrink: 0;
            min-height: 80px;
            box-sizing: border-box;
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
            margin: 20px auto;
            padding: 20px 60px;
            max-width: 2000px;
            width: 95%;
            max-height: calc(100vh - 140px);
            box-sizing: border-box;
            overflow-y: auto;
        }
        .calendar-section { 
            margin-bottom: 20px; 
        }
        .calendar-section h2 {
            font-size: 3.5rem;
            color: #6C4EB6;
            margin-bottom: 15px;
            font-weight: 700;
        }
        .calendar-wrapper {
            position: relative;
        }
        .schedule-calendar {
            width: 100%;
            border-collapse: collapse;
            font-size: 2.2rem;
            margin-bottom: 20px;
            table-layout: fixed;
        }
        .schedule-calendar th, .schedule-calendar td {
            text-align: center;
            padding: 8px 0;
            border: none;
            width: calc(100% / 31);
        }
        .table-calendar-wrapper {
            display: none;
        }
        .table-calendar {
            width: 100%;
            border-collapse: collapse;
            font-size: 1.8rem;
            margin-bottom: 20px;
        }
        .table-calendar td {
            text-align: center;
            padding: 8px 4px;
            border: 1px solid #eee;
            height: 40px;
            vertical-align: middle;
        }
        .table-calendar th {
            text-align: center;
            padding: 10px 4px;
            background: #E7E5F5;
            color: #6C4EB6;
            font-weight: 700;
            border: 1px solid #eee;
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
        .event-list-section { 
            margin-top: 15px; 
        }
        .event-list-container {
            display: flex;
            gap: 40px;
            margin-top: 15px;
        }
        .event-list-part {
            flex: 1;
        }
        .event-list-part h3 {
            font-size: 2rem;
            color: #6C4EB6;
            margin-bottom: 10px;
            font-weight: 700;
        }
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
                height: auto;
                min-height: 80px;
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
            .main-content { 
                padding: 20px 40px; 
                max-height: calc(100vh - 140px);
            }
            .calendar-section h2 {
                font-size: 3rem;
            }
            .schedule-calendar {
                display: none;
            }
            .table-calendar-wrapper {
                display: block;
            }
            .event-list-container {
                flex-direction: column;
                gap: 20px;
            }
        }
        @media (max-width: 900px) {
            .main-content { 
                padding: 20px; 
                max-height: calc(100vh - 140px);
            }
            .header-main-title { font-size: 4rem; }
            .calendar-section h2 { font-size: 2.5rem; }
            .schedule-calendar { 
                display: none;
                font-size: 1.8rem; 
            }
            .table-calendar-wrapper {
                display: block;
            }
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
            .main-content { 
                padding: 15px; 
                max-height: calc(100vh - 140px);
            }
            .header-main-title { font-size: 3rem; }
            .page-header { padding: 15px; }
            .calendar-section h2 { font-size: 2rem; }
            .schedule-calendar { 
                display: none;
                font-size: 1.5rem; 
            }
            .table-calendar-wrapper {
                display: block;
            }
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
        @media (max-height: 800px) {
            .page-header {
                padding: 15px 20px;
                min-height: 60px;
            }
            .header-main-title {
                font-size: 3.5rem;
            }
            .page-header .weather, 
            .page-header .date-time,
            .page-header .school-name {
                font-size: 1.8rem;
            }
            .page-header .weather-icon {
                width: 40px;
                height: 40px;
            }
            .main-content {
                margin: 20px auto;
                padding: 25px 30px;
                max-height: calc(100vh - 100px);
            }
            .calendar-section h2 {
                font-size: 1.8rem;
                margin-bottom: 15px;
            }
            .schedule-calendar {
                display: none;
            }
            .table-calendar-wrapper {
                display: block;
            }
            .table-calendar {
                font-size: 1.6rem;
                margin-bottom: 15px;
            }
            .table-calendar td {
                padding: 6px 3px;
                height: 35px;
            }
            .table-calendar th {
                padding: 8px 3px;
                font-size: 1.4rem;
            }
            .calendar-num {
                width: 1.8rem;
                height: 1.8rem;
                line-height: 1.8rem;
                font-size: 1.2rem;
            }
            .event-list-section {
                margin-top: 15px;
            }
            .event-list-table {
                font-size: 1.6rem;
            }
            .event-list-table td {
                padding: 8px 6px;
            }
            .event-list-table td:first-child {
                font-size: 1.4rem;
                width: 100px;
            }
            .event-list-table td:last-child {
                font-size: 1.6rem;
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
            .main-content {
                margin: 15px auto;
                padding: 20px 25px;
                max-height: calc(100vh - 80px);
            }
            .calendar-section h2 {
                font-size: 1.6rem;
                margin-bottom: 10px;
            }
            .schedule-calendar {
                display: none;
            }
            .table-calendar-wrapper {
                display: block;
            }
            .table-calendar {
                font-size: 1.4rem;
                margin-bottom: 10px;
            }
            .table-calendar td {
                padding: 4px 2px;
                height: 30px;
            }
            .table-calendar th {
                padding: 6px 2px;
                font-size: 1.2rem;
            }
            .calendar-num {
                width: 1.6rem;
                height: 1.6rem;
                line-height: 1.6rem;
                font-size: 1.1rem;
            }
            .event-list-section {
                margin-top: 10px;
            }
            .event-list-table {
                font-size: 1.4rem;
            }
            .event-list-table td {
                padding: 6px 4px;
            }
            .event-list-table td:first-child {
                font-size: 1.2rem;
                width: 90px;
            }
            .event-list-table td:last-child {
                font-size: 1.4rem;
            }
        }
        @media (max-width: 480px) {
            .page-header {
                padding: 15px 10px;
                gap: 15px;
                height: auto;
                min-height: 80px;
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
            .main-content { 
                padding: 15px 10px; 
                margin: 15px auto;
                width: 98%;
                max-height: calc(100vh - 140px);
            }
            .calendar-section h2 { 
                font-size: 1.8rem; 
                margin-bottom: 15px;
            }
            .schedule-calendar { 
                display: none;
                font-size: 1.3rem; 
                margin-bottom: 20px;
            }
            .table-calendar-wrapper {
                display: block;
            }
            .schedule-calendar th, 
            .schedule-calendar td {
                padding: 6px 2px;
            }
            .calendar-num {
                width: 1.6rem;
                height: 1.6rem;
                line-height: 1.6rem;
                font-size: 1.1rem;
            }
            .event-list-table { 
                font-size: 1.3rem; 
            }
            .event-list-table td {
                padding: 10px 6px;
            }
            .event-list-table td:first-child { 
                font-size: 1.2rem; 
                width: 100px;
            }
            .event-list-table td:last-child { 
                font-size: 1.3rem; 
            }
        }
        @media (max-height: 600px) {
            .page-header {
                padding: 15px 20px;
                min-height: 60px;
            }
            .header-main-title {
                font-size: 3.5rem;
            }
            .page-header .weather, 
            .page-header .date-time,
            .page-header .school-name {
                font-size: 1.8rem;
            }
            .page-header .weather-icon {
                width: 40px;
                height: 40px;
            }
            .main-content {
                margin: 20px auto;
                padding: 25px 30px;
            }
            .calendar-section h2 {
                font-size: 1.8rem;
                margin-bottom: 15px;
            }
            .schedule-calendar {
                font-size: 1.6rem;
                margin-bottom: 20px;
            }
            .calendar-num {
                width: 1.8rem;
                height: 1.8rem;
                line-height: 1.8rem;
                font-size: 1.3rem;
            }
            .event-list-table {
                font-size: 1.6rem;
            }
            .event-list-table td {
                padding: 8px 6px;
            }
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
        // 날씨 캐시 설정
        const WEATHER_CACHE_KEY = 'headerWeatherData_v2';
        const WEATHER_TIMESTAMP_KEY = 'headerWeatherTimestamp_v2';
        const WEATHER_UPDATE_INTERVAL = 60 * 60 * 1000; // 1시간 (밀리초)

        // 캐시에서 날씨 데이터 가져오기
        function getCachedWeatherData() {
            try {
                const cachedData = localStorage.getItem(WEATHER_CACHE_KEY);
                const timestamp = localStorage.getItem(WEATHER_TIMESTAMP_KEY);
                
                if (cachedData && timestamp) {
                    const data = JSON.parse(cachedData);
                    const lastUpdate = parseInt(timestamp);
                    const now = Date.now();
                    
                    // 1시간이 지나지 않았다면 캐시된 데이터 사용
                    if (now - lastUpdate < WEATHER_UPDATE_INTERVAL) {
                        console.log('캐시된 헤더 날씨 데이터 사용 중...');
                        return data;
                    }
                }
            } catch (error) {
                console.error('날씨 캐시 데이터 읽기 실패:', error);
            }
            return null;
        }

        // 날씨 데이터를 캐시에 저장하기
        function saveWeatherDataToCache(data) {
            try {
                localStorage.setItem(WEATHER_CACHE_KEY, JSON.stringify(data));
                localStorage.setItem(WEATHER_TIMESTAMP_KEY, Date.now().toString());
                console.log('헤더 날씨 데이터가 캐시에 저장되었습니다.');
            } catch (error) {
                console.error('날씨 캐시 저장 실패:', error);
            }
        }

        // 날씨 데이터를 화면에 표시하는 함수
        function displayWeatherData(weatherData) {
            const temp = Math.round(weatherData.main.temp);
            const weatherInfo = getWeatherInfo(
                weatherData.weather[0].main, 
                weatherData.weather[0].description, 
                weatherData.isDay
            );
            document.querySelector('.weather').innerHTML =
                `<img class='weather-icon' src='images/${weatherInfo.icon}' alt='날씨아이콘'>
                 <div class='weather-content'>
                    <div>${weatherInfo.text}</div>
                    <div class='weather-temp'>${temp}℃</div>
                 </div>`;
        }

        // 초기 날씨 데이터 로드 함수
        async function loadInitialWeather() {
            // 먼저 캐시에서 데이터 확인
            const cachedData = getCachedWeatherData();
            if (cachedData) {
                console.log('캐시된 헤더 날씨 데이터로 초기 로드 중...');
                displayWeatherData(cachedData);
                return;
            }
            
            // 캐시에 데이터가 없거나 만료된 경우에만 API 호출
            console.log('헤더 날씨 데이터 초기 로드 중...');
            await fetchWeather();
        }

        // 날씨 정보 업데이트 함수 (1시간마다)
        async function updateWeatherIfNeeded() {
            // 먼저 캐시에서 데이터 확인
            const cachedData = getCachedWeatherData();
            if (cachedData) {
                // 캐시가 유효하면 표시 함수 호출하지 않음 (이미 표시되어 있음)
                console.log('캐시된 헤더 날씨 데이터가 유효합니다.');
                return;
            }
            
            // 캐시에 데이터가 없거나 만료된 경우에만 API 호출
            console.log('헤더 날씨 정보 업데이트 중...');
            await fetchWeather();
        }

        async function fetchWeather() {
            const apiKey = '""" + os.getenv("OPENWEATHER_API_KEY", "") + """';
            const lat = 37.401;
            const lon = 126.922;
            const url = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${apiKey}&units=metric`;
            
            try {
                const res = await fetch(url);
                const data = await res.json();
                
                if (!data.weather || !data.weather[0]) throw new Error('Invalid weather data');
                
                // 현재 시간을 기준으로 낮/밤 판단
                const now = new Date();
                const currentHour = now.getHours();
                const isDay = currentHour >= 6 && currentHour < 18; // 6시~18시는 낮
                
                // isDay 정보를 데이터에 추가
                data.isDay = isDay;
                
                // 데이터를 화면에 표시
                displayWeatherData(data);
                
                // 성공적으로 데이터를 가져왔다면 캐시에 저장
                saveWeatherDataToCache(data);
                
            } catch (e) {
                console.error("Weather fetch error: ", e);
                document.querySelector('.weather').textContent = '날씨 정보를 불러올 수 없습니다';
            }
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
            function getNightIcon(weatherMain) {
                if (weatherMain === 'Clear') {
                    return 'weather/15.png'; // 달과 별 아이콘
                }
                // 다른 날씨는 동일한 아이콘 사용
                return mainWeatherMap[weatherMain]?.icon || 'weather/1.png';
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

        // 초기 로드 및 주기적 업데이트 설정
        setInterval(updateDateTime, 1000);
        updateDateTime();
        loadInitialWeather();
        
        // 5분마다 날씨 업데이트 체크
        setInterval(updateWeatherIfNeeded, 5 * 60 * 1000);
        
        // 페이지가 포커스를 받았을 때 업데이트 체크
        window.addEventListener('focus', function() {
            updateWeatherIfNeeded();
        });
        
        // 페이지가 보이게 될 때 업데이트 체크 (탭 전환 시)
        document.addEventListener('visibilitychange', function() {
            if (!document.hidden) {
                updateWeatherIfNeeded();
            }
        });
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
                <h2 style="font-size:3.3rem; color:#6C4EB6; margin-bottom:10px;">{year}년 {month}월</h2>
                {calendar_html}
            </div>
            <div class="event-list-section">
                {f'''
                <div class="event-list-container">
                    <div class="event-list-part">
                           <table class="event-list-table">
                            {event_list_html['first_part']}
                        </table>
                    </div>
                    {f'''
                    <div class="event-list-part">
                          <table class="event-list-table">
                            {event_list_html['second_part']}
                        </table>
                    </div>
                    ''' if event_list_html['has_second_part'] else ''}
                </div>
                ''' if isinstance(event_list_html, dict) else f'''
                <table class="event-list-table">
                    {event_list_html}
                </table>
                '''}
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