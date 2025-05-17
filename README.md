# 학교 공지사항 크롤러

인천반도체고등학교의 공지사항과 가정통신문을 자동으로 수집하여 웹 페이지로 제공하는 프로젝트입니다.

## 기능

- 공지사항 자동 수집
- 가정통신문 자동 수집
- 깔끔한 웹 인터페이스 제공
- GitHub Pages를 통한 자동 배포
- 매일 자동 업데이트

## 페이지 구성

- `index.html`: 메인 페이지
- `digital_signage.html`: 공지사항 페이지
- `family_letters.html`: 가정통신문 페이지

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
python src/crawler.py
```

실행이 완료되면 `digital_signage.html`과 `family_letters.html` 파일이 생성됩니다.

## GitHub Pages 설정

1. 저장소의 Settings > Pages 메뉴로 이동
2. Source를 'GitHub Actions'로 설정
3. 저장소의 Actions 탭에서 워크플로우가 정상적으로 실행되는지 확인

## 자동 업데이트

- 매일 자정에 자동으로 업데이트됩니다.
- 수동 업데이트가 필요한 경우:
  1. GitHub 저장소의 Actions 탭으로 이동
  2. '일일 크롤링 및 배포' 워크플로우 선택
  3. 'Run workflow' 버튼 클릭

## 프로젝트 구조

```
school_notice_crawl/
├── src/
│   ├── crawler.py          # 메인 크롤러 스크립트
│   ├── notice_crawler.py   # 공지사항 크롤러
│   └── family_letter_crawler.py  # 가정통신문 크롤러
├── .github/
│   └── workflows/
│       ├── daily_crawl.yml # 일일 크롤링 워크플로우
│       └── gh-pages.yml    # GitHub Pages 배포 워크플로우
├── images/                 # 이미지 파일들
├── index.html             # 메인 페이지
├── digital_signage.html   # 공지사항 페이지
├── family_letters.html    # 가정통신문 페이지
└── requirements.txt       # 필요한 패키지 목록
```

## 주의사항

- 크롤링 시 학교 서버에 과도한 부하를 주지 않도록 주의해주세요.
- 개인정보가 포함된 내용은 공개하지 않도록 주의해주세요.
- 학교의 이용약관을 준수해주세요.

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 