# -*- coding: utf-8 -*-
"""data/강의이력.xlsx 를 읽어 lectures.json 과 stats.json 을 갱신한다.

엑셀은 '회차' 단위로 기록하고, 결과물은 두 갈래로 나뉜다.
  - lectures.json : 같은 과정의 반복분은 한 줄로 합친다 (목록이므로)
  - stats.json    : 전체 회차를 합산한다 (누적 지표이므로)

사용법:  python tools/build_lectures.py
"""
import json
from collections import OrderedDict
from datetime import date, datetime
from pathlib import Path

from openpyxl import load_workbook

엑셀_경로 = Path("data/강의이력.xlsx")
강의_경로 = Path("data/lectures.json")
지표_경로 = Path("data/stats.json")
과정_경로 = Path("data/courses.json")   # '사업 영역'의 수강 가능 교육 목록

헤더_행 = 4
첫_데이터_행 = 5

# 엑셀의 '구분' 값 → lectures.json의 그룹 id
구분_매핑 = OrderedDict([
    ("기관·기업", "institution"),
    ("자체과정", "own"),
])

# 모집상태가 아래 값이면 구분과 상관없이 '수강 신청 가능' 영역으로 올린다.
모집중_상태 = ("신청가능", "오픈예정")

그룹_설정 = OrderedDict([
    ("enrollable",  {"label": "수강 신청 가능", "highlight": True}),
    ("institution", {"label": "기관·기업 강의", "highlight": False}),
    ("own",         {"label": "자체 교육 과정", "highlight": False}),
])


def 행_읽기() -> list[dict]:
    """엑셀에서 유효한 강의 회차만 읽어 딕셔너리 목록으로 돌려준다."""
    통합문서 = load_workbook(엑셀_경로, data_only=True)
    시트 = 통합문서["강의이력"]

    # 헤더 이름으로 열 번호를 찾는다 (열 순서가 바뀌어도 동작하도록)
    열번호 = {}
    for 칸 in 시트[헤더_행]:
        if 칸.value:
            열번호[str(칸.value).strip()] = 칸.column

    필수_헤더 = ["일자", "강의명", "표시기관명", "구분", "홈페이지표시"]
    빠진_헤더 = [이름 for 이름 in 필수_헤더 if 이름 not in 열번호]
    if 빠진_헤더:
        raise SystemExit(f"[중단] 엑셀 헤더가 바뀌었습니다. 찾을 수 없는 열: {빠진_헤더}")

    def 값(행, 헤더):
        if 헤더 not in 열번호:
            return None
        원값 = 시트.cell(row=행, column=열번호[헤더]).value
        return 원값.strip() if isinstance(원값, str) else 원값

    회차들 = []
    for 행 in range(첫_데이터_행, 시트.max_row + 1):
        강의명 = 값(행, "강의명")
        if not 강의명:
            continue

        비고 = 값(행, "비고") or ""
        if str(비고).startswith("예시"):      # 예시 행은 건너뛴다
            continue

        def 날짜값(헤더):
            원값 = 값(행, 헤더)
            if isinstance(원값, datetime):
                원값 = 원값.date()
            return 원값 if isinstance(원값, date) else None

        일자 = 날짜값("일자")
        모집마감일 = 날짜값("모집마감일")

        # 모집마감일이 지났으면 모집 중이 아니다 (끝난 과정이 계속 노출되는 것을 막는다)
        모집상태 = 값(행, "모집상태") or ""
        마감됨 = 모집마감일 is not None and 모집마감일 < date.today()
        if 마감됨:
            모집상태 = ""

        회차들.append({
            "일자": 일자,
            "강의명": 강의명,
            "기관": 값(행, "표시기관명"),
            "대상": 값(행, "교육대상"),
            "에이전시": 값(행, "에이전시"),
            "형태": 값(행, "형태") or "오프라인",
            "시간": 값(행, "교육시간") or 0,
            "인원": 값(행, "수강인원") or 0,
            "구분": 값(행, "구분") or "기관·기업",
            "모집상태": 모집상태,
            "모집마감일": 모집마감일,
            "마감됨": 마감됨,
            "표시": str(값(행, "홈페이지표시") or "Y").upper() != "N",
            "링크": 값(행, "신청링크"),
            "행번호": 행,
        })

    return 회차들


def 입력_점검(회차들: list[dict]) -> list[str]:
    """흔한 입력 실수를 찾아 경고 문구 목록으로 돌려준다."""
    경고들 = []
    for 회차 in 회차들:
        위치 = f"{회차['행번호']}행 「{회차['강의명']}」"

        if 회차["마감됨"]:
            경고들.append(f"{위치}: 모집마감일({회차['모집마감일']})이 지나 "
                          f"'수강 신청 가능'에서 내려갔습니다. "
                          f"계속 모집한다면 마감일을 미래로 바꾸세요.")
            continue   # 이미 내려간 건은 나머지를 점검할 필요가 없다

        if 회차["모집상태"] == "신청가능" and not 회차["링크"]:
            경고들.append(f"{위치}: 모집상태가 '신청가능'인데 신청링크가 없습니다. "
                          f"링크를 넣거나 '오픈예정'으로 바꾸세요.")

        if 회차["모집상태"] and not 회차["모집마감일"]:
            경고들.append(f"{위치}: 모집상태가 '{회차['모집상태']}'인데 모집마감일이 없습니다. "
                          f"마감일을 적어두면 그날 이후 자동으로 내려갑니다.")

        if 회차["모집상태"] and not 회차["표시"]:
            경고들.append(f"{위치}: 모집상태가 '{회차['모집상태']}'인데 홈페이지표시가 N입니다. "
                          f"신청 가능 영역에 나오지 않습니다.")

        if 회차["모집상태"] not in ("", *모집중_상태):
            경고들.append(f"{위치}: 모집상태 '{회차['모집상태']}'를 알 수 없습니다. "
                          f"비워두거나 {' / '.join(모집중_상태)} 중에서 고르세요.")

    return 경고들


def 강의목록_만들기(회차들: list[dict]) -> list[dict]:
    """같은 과정의 반복 회차를 한 줄로 합쳐 그룹별 목록을 만든다."""
    # (강의명, 기관)이 같으면 같은 과정으로 본다
    묶음 = OrderedDict()
    for 회차 in 회차들:
        if not 회차["표시"]:
            continue
        열쇠 = (회차["강의명"], 회차["기관"])
        if 열쇠 not in 묶음:
            묶음[열쇠] = {"회차목록": [], **회차}
        묶음[열쇠]["회차목록"].append(회차)

    그룹별 = {그룹id: [] for 그룹id in 그룹_설정}

    for (강의명, 기관), 묶인것 in 묶음.items():
        회차목록 = 묶인것["회차목록"]

        # 비어 있지 않은 값을 쓰되, 가장 최근 회차의 정보를 우선한다
        최신순 = sorted(회차목록, key=lambda 항목: 항목["일자"] or date.min, reverse=True)

        def 첫값(열쇠):
            return next((항목[열쇠] for 항목 in 최신순 if 항목[열쇠]), None)

        # 한 회차라도 모집 중이면 '수강 신청 가능' 영역으로 올린다
        모집상태 = next((항목["모집상태"] for 항목 in 최신순
                         if 항목["모집상태"] in 모집중_상태), "")
        그룹id = "enrollable" if 모집상태 else 구분_매핑.get(묶인것["구분"], "institution")

        항목 = {"title": 강의명}
        if 기관:
            항목["client"] = 기관
        if 첫값("대상"):
            항목["target"] = 첫값("대상")
        if 첫값("에이전시"):
            항목["agency"] = 첫값("에이전시")      # 화면에는 표시되지 않음

        형태 = 첫값("형태")
        if 형태 and 형태 != "오프라인":
            항목["format"] = 형태                  # 온라인 / VOD 배지

        if 모집상태:
            항목["status"] = 모집상태
            # 브라우저에서도 마감을 한 번 더 확인하도록 날짜를 함께 내보낸다.
            # (변환·푸시를 깜빡해도 끝난 과정이 '신청 가능'으로 노출되지 않게 하는 안전망)
            마감일 = next((항목2["모집마감일"] for 항목2 in 최신순 if 항목2["모집마감일"]), None)
            if 마감일:
                항목["expires"] = 마감일.isoformat()
        if len(회차목록) > 1:
            항목["count"] = len(회차목록)
        if 최신순[0]["일자"]:
            항목["year"] = 최신순[0]["일자"].year

        # 모집 중이 아닌데 링크만 남아 있으면 '끝난 과정 신청 유도'가 되므로 붙이지 않는다
        if 첫값("링크") and (모집상태 == "신청가능" or 그룹id != "enrollable"):
            항목["url"] = 첫값("링크")

        그룹별[그룹id].append((최신순[0]["일자"] or date.min, 항목))

    # 각 그룹 안에서 최신 강의가 위로 오도록 정렬
    결과 = []
    for 그룹id, 설정 in 그룹_설정.items():
        항목들 = [항목 for _, 항목 in sorted(그룹별[그룹id],
                                            key=lambda 쌍: 쌍[0], reverse=True)]
        if 항목들:
            결과.append({"id": 그룹id, **설정, "items": 항목들})
    return 결과


def 모집중_목록(강의_그룹들: list[dict]) -> list[dict]:
    """'사업 영역' 섹션에 넣을 수강 가능 교육 목록을 만든다.

    강의 이력과 같은 엑셀에서 나오므로 두 곳이 어긋날 일이 없다.
    """
    신청가능_그룹 = next((그룹 for 그룹 in 강의_그룹들 if 그룹["id"] == "enrollable"), None)
    if not 신청가능_그룹:
        return []

    목록 = []
    for 항목 in 신청가능_그룹["items"]:
        제목 = 항목["title"]
        if 항목.get("client"):
            제목 = f"{제목} ({항목['client']})"

        과정 = {"title": 제목}
        if 항목.get("url"):
            과정["url"] = 항목["url"]
            과정["cta"] = "바로가기 →"
        else:
            과정["cta"] = "개설 예정"       # 오픈예정: 링크 없이 안내만
        목록.append(과정)

    return 목록


def 진행완료(회차: dict) -> bool:
    """이미 진행한 강의인지 판단한다.

    일자가 미래면 아직 하지 않은 강의이므로 누적 실적에서 뺀다.
    일자가 비어 있으면 '날짜를 아직 안 적은 지난 강의'로 본다.
    """
    return 회차["일자"] is None or 회차["일자"] <= date.today()


def 지표_계산(회차들: list[dict]) -> dict:
    """누적 지표를 계산한다.

    - 홈페이지 미표시(N) 건도 집계에는 포함한다 (비공개 사내 교육 등).
    - 아직 하지 않은 강의(일자가 미래)는 제외한다.
    """
    완료된_회차 = [회차 for 회차 in 회차들 if 진행완료(회차)]
    return {
        "students": sum(int(회차["인원"] or 0) for 회차 in 완료된_회차),
        "sessions": len(완료된_회차),
        "hours": sum(int(회차["시간"] or 0) for 회차 in 완료된_회차),
        # 기관 수는 예정 건까지 포함한다 (이미 확정된 협력 관계이므로)
        "orgs": len({회차["기관"] for 회차 in 회차들 if 회차["기관"]}),
    }


def 저장(경로: Path, 자료: dict) -> None:
    경로.write_text(json.dumps(자료, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def 실행() -> None:
    if not 엑셀_경로.exists():
        raise SystemExit(f"[중단] 엑셀을 찾을 수 없습니다: {엑셀_경로}")

    회차들 = 행_읽기()
    if not 회차들:
        raise SystemExit("[중단] 엑셀에서 읽을 강의가 없습니다.")

    경고들 = 입력_점검(회차들)
    if 경고들:
        print("[확인 필요]")
        for 경고 in 경고들:
            print(f"  - {경고}")
        print()

    # ── lectures.json : 설명용 키(_로 시작)는 그대로 두고 groups만 교체 ──
    강의_자료 = json.loads(강의_경로.read_text(encoding="utf-8"))
    강의_자료["groups"] = 강의목록_만들기(회차들)
    저장(강의_경로, 강의_자료)

    # ── courses.json : 사업 영역의 '수강 가능 교육'도 같은 출처에서 채운다 ──
    과정_자료 = json.loads(과정_경로.read_text(encoding="utf-8"))
    과정_자료["education"]["open"] = 모집중_목록(강의_자료["groups"])
    저장(과정_경로, 과정_자료)

    # ── stats.json : source가 지정된 항목만 값을 채운다 ──
    지표_자료 = json.loads(지표_경로.read_text(encoding="utf-8"))
    계산값 = 지표_계산(회차들)
    갱신된_지표 = []
    for 항목 in 지표_자료["items"]:
        출처 = 항목.get("source")
        if 출처 in 계산값:
            항목["value"] = 계산값[출처]
            갱신된_지표.append(f"{항목['label']} {계산값[출처]:,}")
    저장(지표_경로, 지표_자료)

    # ── 결과 보고 ──
    표시_건수 = sum(1 for 회차 in 회차들 if 회차["표시"])
    예정_건수 = sum(1 for 회차 in 회차들 if not 진행완료(회차))
    예정_안내 = f", 아직 진행 전 {예정_건수}건은 누적 집계에서 제외" if 예정_건수 else ""
    print(f"엑셀에서 {len(회차들)}개 회차를 읽었습니다 "
          f"(홈페이지 표시 {표시_건수}건{예정_안내}).")
    print("\n[lectures.json]")
    for 그룹 in 강의_자료["groups"]:
        print(f"  {그룹['label']}: {len(그룹['items'])}개 과정")
        for 항목 in 그룹["items"]:
            반복 = f" ×{항목['count']}회" if "count" in 항목 else ""
            기관 = f" ({항목['client']})" if "client" in 항목 else ""
            표식 = "".join(f" [{항목[열쇠]}]" for 열쇠 in ("status", "format") if 열쇠 in 항목)
            링크 = " [링크]" if "url" in 항목 else ""
            print(f"    - {항목['title']}{기관}{반복}{표식}{링크}")
    print("\n[courses.json] 사업 영역 · 수강 가능 교육")
    for 과정 in 과정_자료["education"]["open"]:
        print(f"  - {과정['title']} ({과정['cta']})")

    print("\n[stats.json]")
    for 줄 in 갱신된_지표:
        print(f"  {줄}")


if __name__ == "__main__":
    실행()
