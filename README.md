# 학교 공지사항 크롤러

안양초등학교의 공지사항과 가정통신문을 자동으로 수집하여 웹 페이지로 제공하는 프로젝트입니다.

## 기능

- 공지사항 자동 수집
- 가정통신문 자동 수집
- 깔끔한 웹 인터페이스 제공
- GitHub Pages를 통한 자동 배포
- **스마트한 크롤링 주기**: 데이터 특성에 맞는 최적화된 크롤링
- 급식 정보 NEIS OpenAPI 자동 수집 및 제공
- **실시간 날씨 및 대기질 정보 제공**

## 페이지 구성

- `index.html`: 메인 페이지
- `digital_signage.html`: 공지사항 페이지
- `family_letters.html`: 가정통신문 페이지
- `school_schedule.html`: 학사일정(월간) 페이지
- `meal_info.html`: 급식 정보 페이지 (NEIS OpenAPI 기반)
- `weather_widget.html`: **날씨 및 대기질 정보 페이지**

## GitHub Actions 자동화

이 프로젝트는 GitHub Actions를 통해 완전 자동화되어 있습니다:

### 크롤링 주기

1. **공지사항 & 가정통신문**: 매일 오전 6시, 오후 6시
   - 새로운 공지사항이 언제든 올라올 수 있으므로 하루 2회 크롤링
   - 워크플로우: `deploy.yml`

2. **급식정보**: 매주 토요일 밤 11시
   - 주간 단위로 제공되는 급식정보이므로 주 1회 크롤링
   - 워크플로우: `weekly-crawl.yml`

3. **학사일정**: 매월 마지막날 밤 11시
   - 월간 단위로 제공되는 학사일정이므로 월 1회 크롤링
   - 워크플로우: `monthly-crawl.yml`

### 워크플로우 구성

```
.github/workflows/
├── deploy.yml           # 일일 공지사항 크롤링 (매일 6시, 18시)
├── weekly-crawl.yml     # 주간 급식정보 크롤링 (토요일 23시)
└── monthly-crawl.yml    # 월간 학사일정 크롤링 (월말 23시)
```

### 수동 실행

GitHub 저장소의 **Actions** 탭에서 각 워크플로우를 수동으로 실행할 수 있습니다:
1. GitHub 저장소 → **Actions** 탭
2. 원하는 워크플로우 선택
3. "Run workflow" 버튼 클릭

## API 키 설정

이 프로젝트는 여러 API 키를 사용합니다. 보안을 위해 환경변수나 GitHub Secrets를 통해 관리됩니다.

### 필요한 API 키

1. **OpenWeather API 키** - 날씨 정보 제공
   - [OpenWeather API](https://openweathermap.org/api) 사이트에서 발급
   
2. **NEIS OpenAPI 키** - 급식 정보 및 학사일정 제공
   - [NEIS OpenAPI](https://open.neis.go.kr/) 사이트에서 발급
   
3. **에어코리아 API 키** - 대기질 정보 제공
   - [공공데이터포털](https://www.data.go.kr/data/15073861/openapi.do)에서 발급

### 로컬 개발 환경 설정

1. `env.example` 파일을 복사하여 `.env` 파일 생성:
```bash
cp env.example .env
```

2. `.env` 파일에 실제 API 키 입력:
```bash
# API Keys
OPENWEATHER_API_KEY=your_openweather_api_key_here
NEIS_API_KEY=your_neis_api_key_here
AIRKOREA_API_KEY=your_airkorea_api_key_here
```

### GitHub Secrets 설정 (자동 배포용)

GitHub 저장소의 **Settings > Secrets and variables > Actions**에서 다음 시크릿을 추가:

1. `OPENWEATHER_API_KEY`: OpenWeather API 키
2. `NEIS_API_KEY`: NEIS OpenAPI 키  
3. `AIRKOREA_API_KEY`: 에어코리아 API 키

### 설정 방법
```bash
# 로컬에서 .env 파일 생성
echo "OPENWEATHER_API_KEY=your_key_here" > .env
echo "NEIS_API_KEY=your_key_here" >> .env
echo "AIRKOREA_API_KEY=your_key_here" >> .env
```

**⚠️ 보안 주의사항**: 
- `.env` 파일을 `.gitignore`에 추가하여 API 키가 공개되지 않도록 주의하세요
- GitHub Secrets를 사용하여 자동 배포 시에도 API 키를 안전하게 관리하세요

## 로컬에서 실행하기

1. 저장소 클론
```bash
git clone https://github.com/[사용자명]/school_notice_crawl.git
cd school_notice_crawl
```

2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

3. 크롤러 실행
```bash
# 모든 크롤러 한번에 실행
python main_crawler.py

# 개별 크롤러 실행
python src/crawler.py  # 공지/가정통신문
python src/meal_crawler.py  # 급식 정보 (NEIS OpenAPI 기반)
python src/school_schedule_crawler.py  # 학사일정(월간)
```

실행이 완료되면 `digital_signage.html`, `family_letters.html`, `meal_info.html`, `school_schedule.html` 파일이 생성됩니다.

## GitHub Pages 설정

1. 저장소의 **Settings > Pages** 메뉴로 이동
2. Source를 'GitHub Actions'로 설정
3. 저장소의 **Actions** 탭에서 워크플로우가 정상적으로 실행되는지 확인

## 프로젝트 구조

```
school_notice_crawl/
├── .github/
│   └── workflows/
│       ├── deploy.yml           # 일일 공지사항 크롤링
│       ├── weekly-crawl.yml     # 주간 급식정보 크롤링
│       └── monthly-crawl.yml    # 월간 학사일정 크롤링
├── src/
│   ├── crawler.py                # 메인 크롤러 스크립트(공지/가정통신문)
│   ├── meal_crawler.py           # 급식 정보 크롤러 (NEIS OpenAPI)
│   ├── school_schedule_crawler.py # 학사일정(월간) 크롤러
│   ├── notice_crawler.py         # 공지사항 크롤러
│   └── family_letter_crawler.py  # 가정통신문 크롤러
├── main_crawler.py               # 모든 크롤러를 한번에 실행하는 메인 스크립트
├── images/                       # 이미지 파일들
├── font/                         # 폰트 파일들
├── index.html                    # 메인 페이지
├── digital_signage.html          # 공지사항 페이지
├── family_letters.html           # 가정통신문 페이지
├── meal_info.html                # 급식 정보 페이지 (NEIS OpenAPI 기반)
├── school_schedule.html          # 학사일정(월간) 페이지
├── weather_widget.html           # **날씨 및 대기질 정보 페이지**
├── config.js                     # **API 키 설정 파일**
└── requirements.txt              # 필요한 패키지 목록
```

## 날씨 위젯 기능

- **실시간 날씨 정보**: 현재 온도, 날씨 상태, 습도, 풍속, 기압
- **3일 날씨 예보**: 향후 3일간의 날씨 예보
- **실시간 대기질 정보**: 미세먼지(PM10), 초미세먼지(PM2.5) 농도 및 등급
- **디지털 사이니지 최적화**: 큰 글씨와 명확한 레이아웃
- **반응형 디자인**: 다양한 화면 크기에 대응

## 문제 해결

### GitHub Actions 실행 실패 시
1. **Actions** 탭에서 실패한 워크플로우 확인
2. 로그를 통해 오류 원인 파악
3. API 키가 올바르게 설정되었는지 확인
4. 네트워크 연결 상태 확인

### 크롤링 데이터가 업데이트되지 않는 경우
1. 학교 홈페이지 서버 상태 확인
2. RSS 피드 URL이 변경되었는지 확인
3. 수동으로 워크플로우 실행해보기
