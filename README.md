# 로직플로우 홈페이지

[logicflow.ai.kr](https://logicflow.ai.kr) · GitHub Pages로 호스팅됩니다.

**이 문서만 보면 홈페이지 내용을 혼자 수정할 수 있습니다.**
코드를 건드릴 필요 없이 `data/` 폴더의 JSON 파일만 고치면 됩니다.

---

## 1. 가장 자주 하는 작업

### 강의 이력 추가하기

`data/lectures.json` 을 열고, `기관·기업 강의` 그룹의 `items` **맨 위**에 한 줄 추가합니다.

```json
{ "title": "생성형 AI 활용 업무혁신 과정", "client": "한국전력공사" },
```

- `title` : 강의명 (필수)
- `client` : 기관·기업명 (선택)
- `year` : 연도 (선택, 넣으면 옆에 작게 표시됨)
- `url` : 신청 페이지 주소 (선택, 넣으면 클릭 가능해짐)

> 쉼표 위치를 조심하세요. 마지막 항목 뒤에는 쉼표를 붙이지 않습니다.

### 누적 수강생 수 바꾸기

`data/stats.json` 에서 숫자만 고칩니다.

```json
{ "value": 2500, "suffix": "명+", "label": "누적 수강생", "icon": "fas fa-users" }
```

`value`는 **숫자만** 적습니다(쉼표·단위 없이). 화면에서는 자동으로 `2,500명+` 으로 표시되고,
스크롤해서 보일 때 0부터 올라가는 애니메이션이 붙습니다.

### 활동사진 추가하기

1. 사진 파일 이름을 `20261120_부산시_01.jpg` 형식(`날짜_지역_번호`)으로 바꿉니다.
2. `홍보/활동사진_모자이크` 폴더에 넣습니다.
3. 아래 명령을 실행합니다.

```bash
python tools/build_gallery.py
```

리사이즈·EXIF 제거·`data/gallery.json` 갱신이 한 번에 됩니다.
그 다음 `data/gallery.json` 에서 `caption`을 실제 기관명으로 고치면 더 좋습니다.

> **사진은 반드시 모자이크 처리된 것만 올리세요.** 수강생 얼굴이 식별되면 초상권 문제가 됩니다.

### 유튜브 영상 추가하기

`data/videos.json` 에서 해당 시리즈의 `videos` 배열 맨 아래에 추가합니다.

```json
{ "id": "dErLAh4kDxI", "title": "영상 제목" }
```

`id`는 유튜브 주소 `watch?v=` **뒤에 오는 값**입니다.

---

## 2. 수정한 내용을 사이트에 반영하기

```bash
git add . && git commit -m "강의 이력 추가" && git push
```

푸시하면 GitHub Pages가 **1~2분 안에** 자동 반영합니다.
브라우저에 바로 안 보이면 `Ctrl + F5` 로 새로고침하세요.

> GitHub 웹사이트에서 파일을 직접 편집해도 됩니다. 저장소 → 파일 클릭 → 연필 아이콘 →
> 수정 → Commit changes. **휴대폰에서도 가능합니다.**

---

## 3. 폴더 구조

```
landing/
├── index.html              ← 레이아웃 껍데기 (내용 없음)
├── data/                   ← ★ 내용은 전부 여기 있습니다
│   ├── site.json           소개 영상 · 아키텍트 소개 · 연락처
│   ├── stats.json          누적 수강생 등 성과 지표
│   ├── courses.json        사업 영역 · 모집 중인 교육 · 수강생 페이지
│   ├── lectures.json       강의 이력
│   ├── automation.json     자동화 개발 이력
│   ├── education.json      학력
│   ├── videos.json         유튜브 영상 목록
│   └── gallery.json        활동사진 목록
├── assets/
│   ├── brand.css           ★ 브랜드 색상·폰트 (한 곳에서 관리)
│   └── render.js           JSON을 읽어 화면을 그리는 코드
├── images/
│   ├── brand/              로고 · 파비콘 · OG 이미지 · 프로필
│   └── gallery/            활동사진 (thumb/ = 격자용 축소본)
├── tools/                  이미지 가공 스크립트
├── class/                  수강생 전용 페이지
└── report/                 리포팅 솔루션 소개 페이지
```

---

## 4. 브랜드 컬러

`assets/brand.css` 상단의 `--brand-*` 값과 `index.html` 의 `tailwind.config`
**두 곳**에 같은 값이 들어 있습니다. 색을 바꿀 때는 양쪽을 함께 수정하세요.

| 토큰 | 값 | 용도 |
|---|---|---|
| 브랜드 그린 | `#0B4D3B` | 메인 |
| 그로스 그린 | `#166B52` | 보조 |
| 라이트 그린 | `#3DA37A` | 포인트 |
| 민트 그린 | `#E8F4EE` | 배경 |

로고 원본: `10_LogicFlow/11_Assets/logo/`

---

## 5. 수정 전 로컬에서 확인하기

```bash
python -m http.server 8765 -d .
```

브라우저에서 `http://localhost:8765` 로 접속합니다.
화면이 비어 보이면 **F12 → Console** 에 JSON 오류가 찍혀 있습니다
(대부분 쉼표를 빠뜨렸거나 더 붙인 경우입니다).

JSON 문법만 미리 검사하려면:

```bash
python -c "import json,glob; [json.load(open(f,encoding='utf-8')) for f in glob.glob('data/*.json')]; print('이상 없음')"
```

---

## 6. 주의사항

- `data/*.json` 에서 `_주석`, `_항목형식` 으로 시작하는 키는 설명용입니다. 지우지 마세요.
- 페이지 제목·설명·OG 태그·히어로 문구는 검색엔진 노출을 위해 `index.html` 에 직접 적혀 있습니다.
  이 부분은 JSON이 아니라 HTML을 고쳐야 합니다.
- `CNAME` 파일은 도메인 연결 설정입니다. 지우면 `logicflow.ai.kr` 접속이 끊깁니다.
