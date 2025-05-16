# Crawl4AI - 학교 공지사항 크롤러

학교 웹사이트의 공지사항을 수집하여 JSON API 및 RSS 피드로 제공하는 도구입니다.
GitHub Actions를 통해 매일 자동으로 공지사항을 크롤링하고 RSS 피드를 업데이트합니다.

## 기능

- 학교 공지사항 자동 크롤링
- 가정통신문 자동 크롤링
- JSON 형식 API 제공
- RSS 피드 생성 및 제공
- 디지털 사이니지용 공지사항 페이지 제공
- GitHub Actions로 자동 스케줄링 (일별 크롤링)
- GitHub Pages를 통한 웹 인터페이스

## 설치 방법

1. 저장소 복제:
   ```
   git clone https://github.com/yourusername/crawl4ai.git
   cd crawl4ai
   ```

2. 필요한 패키지 설치:
   ```
   pip install -r requirements.txt
   ```

## 사용 방법

### 1. 로컬에서 직접 실행

```bash
python notice_crawler.py  # 공지사항 크롤링
python rss_feed_generator.py  # RSS 피드 생성
```

### 2. GitHub Actions로 자동 실행하기

이 프로젝트는 GitHub Actions 워크플로우를 사용하여 매일 자동으로 학교 공지사항을 크롤링하고 RSS 피드를 업데이트합니다.

1. 이 저장소를 본인의 GitHub 계정으로 포크합니다.
2. GitHub 저장소 설정에서 GitHub Pages를 활성화합니다:
   - Settings > Pages > Source에서 `gh-pages` 브랜치를 선택합니다.
3. GitHub Actions 워크플로우가 자동으로 설정됩니다:
   - 매일 UTC 01:00 (한국 시간 약 10:00)에 크롤링이 실행됩니다.
   - Actions 탭에서 워크플로우 진행 상황을 확인할 수 있습니다.
   - 수동으로 실행도 가능합니다: Actions 탭 > 일일 크롤링 및 RSS 업데이트 > Run workflow

### 3. 크롤링할 사이트 추가하기

새로운 학교 사이트를 추가하려면:

1. `crawl_sites.json` 파일을 편집합니다:

```json
{
  "sites": [
    {
      "name": "인천반도체고등학교",
      "url": "https://isc.icehs.kr/boardCnts/list.do?boardID=11101&m=0202&s=inchon_ii"
    },
    {
      "name": "새로운학교명",
      "url": "https://school-website.edu/board"
    }
  ]
}
```

2. 변경 내용을 커밋하고 푸시합니다.
3. 다음 GitHub Actions 실행 시 자동으로 새 사이트가 크롤링됩니다.

### 4. RSS 피드 구독하기

생성된 RSS 피드는 다음 방법으로 구독할 수 있습니다:

1. GitHub Pages 사이트에서 원하는 피드를 선택합니다: `https://yourusername.github.io/crawl4ai/`
2. 또는 직접 RSS 피드 URL을 구독합니다: `https://yourusername.github.io/crawl4ai/feeds/학교명_feed.xml`
3. Feedly, Inoreader, Thunderbird 등의 RSS 리더에 피드 URL을 추가합니다.

### 5. 디지털 사이니지 활용하기

크롤링된 공지사항을 디지털 사이니지(전자게시판)에 표시할 수 있습니다:

1. 디지털 사이니지 URL: `https://yourusername.github.io/crawl4ai/signage/`
2. 이 페이지를 디지털 사이니지 기기의 브라우저에서 열면 자동으로 최신 공지사항이 표시됩니다.
3. 다음과 같은 기능을 제공합니다:
   - 크게 표시된 학교 공지사항 목록
   - 자동 순환 표시 (8초마다 업데이트)
   - 현재 시간 및 날짜 표시
   - 학교 로고 자동 표시
   - 모바일 및 대형 화면 지원을 위한 반응형 디자인

## API 엔드포인트 (로컬 서버 실행 시)

로컬에서 API 서버를 실행할 경우 다음 엔드포인트를 사용할 수 있습니다:

### 공지사항 API

- `GET /api/notices/{사이트명}`: 특정 사이트의 공지사항 목록
- `GET /api/sites`: 크롤링된 사이트 목록
- `POST /api/crawl-notices`: 새 사이트 크롤링 실행

### RSS 피드

- `GET /feeds`: RSS 피드 목록 페이지
- `GET /feeds/{사이트명}_feed.xml`: 특정 사이트의 RSS 피드
- `GET /api/generate-feed/{사이트명}`: RSS 피드 생성 API

## GitHub Actions 워크플로우 설명

`.github/workflows/daily_crawl.yml` 파일에 정의된 워크플로우는 다음 작업을 수행합니다:

1. Python 환경 설정
2. 필요한 패키지 설치
3. 공지사항 크롤링 실행
4. RSS 피드 생성
5. 디지털 사이니지 페이지 업데이트
6. 변경된 데이터를 자동으로 커밋 및 푸시

워크플로우 구성을 변경하려면 이 파일을 편집하세요.

## 개발자 정보

- 개발자: [개발자 이름]
- 라이센스: MIT

## 사용된 기술

- Python 3.8+
- BeautifulSoup4
- FeedGen (RSS 피드 생성)
- 바닐라 JavaScript (디지털 사이니지)
- GitHub Actions (자동화)
- GitHub Pages (웹 호스팅) 