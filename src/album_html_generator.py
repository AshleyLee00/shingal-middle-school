#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
앨범 HTML 생성기
크롤링된 앨범 데이터를 HTML로 변환하는 모듈입니다.
"""

import os

def generate_album_html(albums, school_name):
    """
    앨범 정보를 HTML로 변환합니다.
    """
    css_style = """
        @font-face {
            font-family: 'SeoulAlrim';
            src: url('font/SeoulAlrimTTF-Medium.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
        }

        body {
            background: #4A90E2;
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
            background: linear-gradient(90deg, #4A90E2, #357ABD);
            padding: 30px 90px;
            box-shadow: 0 8px 32px rgba(53, 122, 189, 0.18);
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
            box-shadow: 0 8px 40px rgba(53, 122, 189, 0.18);
            gap: 0;
            width: 95%;
            max-width: 2000px;
            flex: 1;
            padding: 40px;
            overflow-y: auto;
        }

        .album-container {
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 40px;
        }

        .album-item {
            background: #FFFFFF;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(53, 122, 189, 0.15);
            overflow: hidden;
            border: 1px solid #E3F2FD;
        }

        .album-header {
            background: linear-gradient(135deg, #4A90E2, #357ABD);
            color: white;
            padding: 25px 30px;
        }

        .album-title {
            font-size: 2.8rem;
            font-weight: 900;
            margin-bottom: 10px;
            line-height: 1.3;
        }

        .album-meta {
            font-size: 1.6rem;
            opacity: 0.9;
        }

        .album-content {
            padding: 30px;
        }

        .image-slider {
            position: relative;
            width: 100%;
            height: 500px;
            margin-bottom: 30px;
            border-radius: 15px;
            overflow: hidden;
            background: #f5f5f5;
        }

        .image-slide {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0;
            transition: opacity 0.5s ease-in-out;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .image-slide.active {
            opacity: 1;
        }

        .image-slide img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            border-radius: 15px;
        }

        .slider-controls {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 10px;
            z-index: 10;
        }

        .slider-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.5);
            cursor: pointer;
            transition: background 0.3s;
        }

        .slider-dot.active {
            background: white;
        }

        .slider-nav {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(0, 0, 0, 0.5);
            color: white;
            border: none;
            padding: 15px 10px;
            cursor: pointer;
            font-size: 1.8rem;
            border-radius: 5px;
            transition: background 0.3s;
        }

        .slider-nav:hover {
            background: rgba(0, 0, 0, 0.7);
        }

        .slider-prev {
            left: 20px;
        }

        .slider-next {
            right: 20px;
        }

        .album-text {
            font-size: 1.8rem;
            line-height: 1.6;
            color: #333;
            background: #F8F9FA;
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #4A90E2;
        }

        .no-images {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            font-size: 2rem;
            color: #666;
            background: #f5f5f5;
        }

        @media (max-width: 1200px) {
            .main-content {
                padding: 30px;
            }
            .album-title {
                font-size: 2.4rem;
            }
            .image-slider {
                height: 400px;
            }
            .album-text {
                font-size: 1.6rem;
            }
        }

        @media (max-width: 768px) {
            .main-content {
                padding: 20px;
                margin: 20px auto;
            }
            .album-container {
                gap: 30px;
            }
            .album-header {
                padding: 20px;
            }
            .album-title {
                font-size: 2rem;
            }
            .album-meta {
                font-size: 1.4rem;
            }
            .album-content {
                padding: 20px;
            }
            .image-slider {
                height: 300px;
            }
            .album-text {
                font-size: 1.5rem;
                padding: 20px;
            }
            .slider-nav {
                padding: 10px 8px;
                font-size: 1.4rem;
            }
        }

        @media (max-width: 480px) {
            .main-content {
                padding: 15px;
                margin: 15px auto;
                width: 98%;
            }
            .album-header {
                padding: 15px;
            }
            .album-title {
                font-size: 1.8rem;
            }
            .album-meta {
                font-size: 1.3rem;
            }
            .album-content {
                padding: 15px;
            }
            .image-slider {
                height: 250px;
            }
            .album-text {
                font-size: 1.4rem;
                padding: 15px;
            }
        }
    """

    js_code = """
        // 날씨 캐시 설정
        const WEATHER_CACHE_KEY = 'headerWeatherData_v2';
        const WEATHER_TIMESTAMP_KEY = 'headerWeatherTimestamp_v2';
        const WEATHER_UPDATE_INTERVAL = 60 * 60 * 1000; // 1시간 (밀리초)

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
            const lat = 37.2857;
            const lon = 127.1109;
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

        // 이미지 슬라이더 기능
        function initImageSliders() {
            const sliders = document.querySelectorAll('.image-slider');
            
            sliders.forEach((slider, sliderIndex) => {
                const slides = slider.querySelectorAll('.image-slide');
                const dots = slider.querySelectorAll('.slider-dot');
                const prevBtn = slider.querySelector('.slider-prev');
                const nextBtn = slider.querySelector('.slider-next');
                
                let currentSlide = 0;
                
                function showSlide(index) {
                    slides.forEach((slide, i) => {
                        slide.classList.toggle('active', i === index);
                    });
                    
                    dots.forEach((dot, i) => {
                        dot.classList.toggle('active', i === index);
                    });
                }
                
                function nextSlide() {
                    currentSlide = (currentSlide + 1) % slides.length;
                    showSlide(currentSlide);
                }
                
                function prevSlide() {
                    currentSlide = (currentSlide - 1 + slides.length) % slides.length;
                    showSlide(currentSlide);
                }
                
                // 초기 슬라이드 표시
                if (slides.length > 0) {
                    showSlide(0);
                }
                
                // 이벤트 리스너 추가
                if (prevBtn) {
                    prevBtn.addEventListener('click', prevSlide);
                }
                
                if (nextBtn) {
                    nextBtn.addEventListener('click', nextSlide);
                }
                
                dots.forEach((dot, index) => {
                    dot.addEventListener('click', () => {
                        currentSlide = index;
                        showSlide(currentSlide);
                    });
                });
                
                // 자동 슬라이드 (5초마다)
                if (slides.length > 1) {
                    setInterval(nextSlide, 5000);
                }
            });
        }

        // 초기 로드 및 주기적 업데이트 설정
        setInterval(updateDateTime, 1000);
        updateDateTime();
        loadInitialWeather();
        
        // 페이지 로드 시 이미지 슬라이더 초기화
        window.addEventListener('load', function() {
            initImageSliders();
        });
        
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
    """

    album_items = ""
    for album in albums:
        # 이미지 슬라이더 HTML 생성
        image_slider_html = ""
        if album['images']:
            for i, image_url in enumerate(album['images']):
                active_class = "active" if i == 0 else ""
                image_slider_html += f'<div class="image-slide {active_class}"><img src="{image_url}" alt="앨범 이미지"></div>'
            
            # 슬라이더 컨트롤 생성
            dots_html = ""
            for i in range(len(album['images'])):
                active_class = "active" if i == 0 else ""
                dots_html += f'<div class="slider-dot {active_class}"></div>'
            
            nav_html = ""
            if len(album['images']) > 1:
                nav_html = f'''
                    <button class="slider-nav slider-prev">‹</button>
                    <button class="slider-nav slider-next">›</button>
                '''
            
            image_slider_html = f'''
                <div class="image-slider">
                    {image_slider_html}
                    <div class="slider-controls">
                        {dots_html}
                    </div>
                    {nav_html}
                </div>
            '''
        else:
            image_slider_html = '<div class="image-slider"><div class="no-images">이미지가 없습니다</div></div>'
        
        # 내용 표시
        content_html = ""
        if album['content']:
            content_html = f'<div class="album-text">{album["content"]}</div>'
        
        album_items += f"""
            <div class="album-item">
                <div class="album-header">
                    <div class="album-title">{album['title']}</div>
                    <div class="album-meta">{album['date']} • {album['author'] if album['author'] else '신갈중학교'}</div>
                </div>
                <div class="album-content">
                    {image_slider_html}
                    {content_html}
                </div>
            </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>{school_name} 학교앨범</title>
        <style>{css_style}</style>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
    </head>
    <body>
        <header class="page-header">
            <div class="header-left">
                <div class="header-main-title">학교앨범</div>
            </div>
            <div class="header-right">
                <div class="weather">날씨 정보를 불러오는 중...</div>
                <div class="date-time" id="date-time"></div>
                <div class="school-name">{school_name}</div>
            </div>
        </header>
        
        <div class="main-content">
            <div class="album-container">
                {album_items}
            </div>
        </div>

        <script>{js_code}</script>
    </body>
    </html>
    """
    return html_content 