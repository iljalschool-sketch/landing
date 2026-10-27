# CLAUDE.md — 로직플로우 홈페이지

이 저장소에서 작업할 때 Claude가 지켜야 할 규칙입니다.
사용자용 수정 가이드는 [README.md](README.md)에 있습니다.

## 프로젝트 개요

- **배포**: GitHub Pages (`iljalschool-sketch/landing`) → https://logicflow.ai.kr
- **빌드 없음**: 정적 HTML + Tailwind CDN. 푸시하면 1~2분 내 반영
- **설계 원칙**: 데이터(`data/*.json`)와 표현(`assets/`, `index.html`)을 분리한다

## 핵심 규칙

1. **콘텐츠는 JSON에만 둔다.** 강의 이력·영상·사진·지표를 `index.html`이나
   `render.js`에 하드코딩하지 않는다. 이 분리가 이 프로젝트의 존재 이유다.

2. **단, SEO 요소는 HTML에 정적으로 유지한다.** `<head>` 메타태그와 히어로 `<h1>`은
   JSON으로 빼지 않는다. 네이버·다음 크롤러는 JS 렌더링 결과를 제대로 읽지 못한다.

3. **브랜드 색상은 두 곳에 있다.** `assets/brand.css`의 `--brand-*` 변수와
   `index.html`의 `tailwind.config`. 색을 바꿀 때 반드시 양쪽을 함께 고친다.

4. **이미지는 반드시 `tools/`의 스크립트로 가공한다.** 원본을 그대로 커밋하지 않는다.
   활동사진 원본은 장당 1~2.5MB다.

5. **활동사진은 모자이크 처리된 것만 사용한다.** 원본 폴더(`홍보/Photos-*`)가 아니라
   `홍보/활동사진_모자이크`를 쓴다. EXIF는 스크립트가 제거한다.

6. **`lectures.json`의 `groups`, `stats.json`의 `source` 항목, `courses.json`의 `education.open`은 손으로 고치지 않는다.**
   `data/강의이력.xlsx`가 원본이고, `tools/build_lectures.py`가 생성한다.
   직접 고치면 다음 실행 때 덮어쓰기 된다. 사용자가 "강의이력 업데이트해줘"라고 하면
   이 스크립트를 실행한다.

7. **`agency`(경유 에이전시)는 절대 화면에 렌더링하지 않는다.** 내부 기록 전용이다.
   기관명 노출 기준은 `lectures.json`의 `_표기원칙`을 따른다.

## 파일 구조

| 경로 | 역할 |
|---|---|
| `index.html` | 레이아웃 껍데기 + SEO 메타 + Tailwind 설정 |
| `assets/brand.css` | 브랜드 토큰(색·폰트·형태) 및 컴포넌트 스타일 |
| `assets/render.js` | `data/*.json` → DOM 렌더링 |
| `data/*.json` | 모든 콘텐츠 |
| `data/강의이력.xlsx` | 강의 회차 기록의 **원본**. 사용자가 직접 입력한다 |
| `tools/build_lectures.py` | 엑셀 → `lectures.json` + `stats.json` + `courses.json`의 `education.open` |
| `tools/build_gallery.py` | 활동사진 리사이즈 + EXIF 제거 + `gallery.json` 생성 |
| `tools/build_brand.py` | 로고 웹용 변환 + 파비콘 + OG 이미지 + 프로필 |
| `tools/recalc_excel.py` | Excel COM으로 수식 재계산·오류 검사 (LibreOffice 없는 환경용) |
| `tools/make_lecture_workbook.py` | 엑셀 양식 최초 생성. **재실행하면 입력 내용이 사라진다** |
| `class/<슬러그>/` | 수강생 전용 페이지 (페이지마다 독립 HTML) |
| `report/` | 리포팅 솔루션 소개 페이지 |

## 강의 이력 파이프라인

```
data/강의이력.xlsx  ──(build_lectures.py)──┬──> data/lectures.json  (중복 제거: 같은 강의명+기관은 1줄 + count)
   회차 단위로 기록                        ├──> data/stats.json     (전체 합산: 수강생·횟수·시간·기관 수)
                                           └──> data/courses.json   (education.open = 모집 중인 과정)
```

- 엑셀은 **회차**를, JSON은 **목록과 합계**를 담는다. 이 분리가 핵심이다.
- `홈페이지표시 = N`인 행은 `lectures.json`에서 빠지지만 `stats.json` 집계에는 포함된다.
- 비고가 `예시`로 시작하는 행은 모두에서 제외된다.
- **`courses.json`의 `education.open`도 이 스크립트가 덮어쓴다.** 손으로 고치지 않는다.
  (같은 '수강 가능 교육'이 두 군데 적혀 어긋나는 것을 막기 위해 한 출처로 묶었다.)

### 분류 축이 두 개다

| 축 | 열 | 값 | 뜻 |
|---|---|---|---|
| 성격 | `구분` | 기관·기업 / 자체과정 | 누가 기획·모집했나 |
| 모집 | `모집상태` | (빈칸) / 신청가능 / 오픈예정 | 지금 신청할 수 있나 |

`모집상태`가 차 있으면 **`구분`과 무관하게** `enrollable` 그룹(「수강 신청 가능」)으로 올라간다.
단, `stats.json` 집계는 그룹과 독립적으로 **전체 행**을 세므로 기관 수에서 누락되지 않는다.
(이전의 3분할 `대표강의` 구조에서는 대표로 지정하면 기관 집계에서 빠지는 문제가 있었다.)

- `오픈예정`에는 `url`을 붙이지 않는다. 끝나거나 아직 안 열린 과정으로 신청을 유도하지 않기 위해서다.
- `형태`가 `오프라인`이 아닐 때만 `format` 필드를 내보낸다 (온라인 / VOD 배지).
- 열은 **헤더 이름**으로 찾으므로 순서가 바뀌어도 동작한다. 헤더가 없으면 중단한다.
- 엑셀 수식을 고쳤으면 `tools/recalc_excel.py`로 재계산·검증한다.
  (`xlsx` 스킬의 `recalc.py`는 LibreOffice가 필요한데 이 환경에는 없다.)

## 렌더링 흐름

`render.js`는 즉시실행 함수 하나로 구성된다.

1. `시작()`이 `data/`의 JSON 8개를 `Promise.all`로 병렬 로드
2. 섹션별 `*_그리기()` 함수가 해당 `id`의 요소에 HTML 문자열을 주입
3. 이벤트 연결(탭 전환, 시리즈 토글, 라이트박스, 카운트업)
4. `body`에 `loaded` 클래스 부여

JSON 로드에 실패하면 `읽기()`가 `null`을 반환하고, 각 `*_그리기()`가
조용히 빠져나간다. **한 파일이 깨져도 나머지 섹션은 정상 표시된다.**

## 작업 시 주의

- 사용자 입력이 아닌 자체 콘텐츠지만 `render.js`의 `esc()`로 이스케이프한다.
  `body`, `quote` 처럼 의도적으로 HTML 태그를 넣는 필드만 예외다.
- 새 섹션을 추가할 때는 `index.html`에 빈 컨테이너(`id` 부여) →
  `data/`에 JSON → `render.js`에 `*_그리기()` 순서로 만든다.
- 수정 후에는 로컬 서버로 확인한다: `python -m http.server 8765 -d .`
- JSON 문법 검사: `python -c "import json,glob; [json.load(open(f,encoding='utf-8')) for f in glob.glob('data/*.json')]"`

## 아직 안 한 일 (향후 과제)

- `class/` 페이지들이 서로 복붙 구조다 (`sejong`은 2,200줄). 공통 템플릿화 필요.
- `test1/` 은 용도 불명의 실험 페이지. 라이브 URL이라 임의 삭제하지 않고 보류 중.
- 2단계로 Astro 도입 시, 현재 `data/*.json`을 그대로 입력으로 재사용할 수 있다.

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-10-27 | 분류를 `구분`(성격) + `모집상태`(신청 가능 여부) 두 축으로 분리. 기존 `대표강의` 3분할 폐지. `형태`(온라인/VOD) 추가. `courses.json`의 수강 가능 교육도 엑셀 단일 출처로 통합 |
| 2026-10-27 | 강의 이력 엑셀 파이프라인 도입. `data/강의이력.xlsx` → `lectures.json` + `stats.json` 자동 생성. 기관명 표기 원칙(`_표기원칙`)과 비노출 `agency` 필드 추가 |
| 2026-10-27 | 데이터/표현 분리 개편. 단일 774줄 `index.html` → `data/*.json` + `assets/`. 신규 브랜드(그린) 적용, 누적 성과 지표·활동사진 갤러리 신설, OG 이미지 복구(기존 404), Pretendard 폰트 로드 경로 수정, 레거시 자산 정리 |
