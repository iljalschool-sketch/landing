# -*- coding: utf-8 -*-
"""강의이력.xlsx 가 어디 있는지 찾아준다.

저장소는 OneDrive 바깥에 두고(.git 손상 방지), 엑셀 원본은 OneDrive 안에
두기 때문에 둘의 상대 위치가 고정되지 않는다. 그래서 경로를 바깥에서
정할 수 있게 한다.

찾는 순서:
    1. 환경변수 LECTURE_XLSX
    2. tools/엑셀경로.txt  (이 파일에 전체 경로 한 줄. git에 올리지 않는다)
    3. ../강의이력.xlsx    (예전 구조 — 저장소 바로 위)
"""
import os
from pathlib import Path

설정_파일 = Path(__file__).with_name("엑셀경로.txt")


def 엑셀_찾기() -> Path:
    """강의이력.xlsx 의 실제 경로를 돌려준다. 없으면 안내와 함께 중단한다."""
    후보 = []

    환경값 = os.environ.get("LECTURE_XLSX")
    if 환경값:
        후보.append(("환경변수 LECTURE_XLSX", Path(환경값)))

    if 설정_파일.exists():
        적힌_값 = 설정_파일.read_text(encoding="utf-8").strip()
        if 적힌_값:
            후보.append((f"{설정_파일.name}", Path(적힌_값)))

    후보.append(("기본값 ../강의이력.xlsx", Path("../강의이력.xlsx")))

    for 출처, 경로 in 후보:
        if 경로.exists():
            return 경로

    찾아본_곳 = "\n".join(f"    - {출처}: {경로}" for 출처, 경로 in 후보)
    raise SystemExit(
        f"[중단] 강의이력.xlsx 를 찾지 못했습니다.\n{찾아본_곳}\n\n"
        f"해결: {설정_파일} 에 엑셀 전체 경로를 한 줄로 적어 두세요."
    )
