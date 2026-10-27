# -*- coding: utf-8 -*-
"""활동사진을 웹용으로 변환하고 gallery.json을 생성한다.

- EXIF(촬영 위치·기기 정보)를 제거해 개인정보 노출을 막는다.
- 격자용 썸네일(thumb)과 확대용 이미지(full)를 각각 생성한다.
"""
import json
import re
from pathlib import Path

from PIL import Image, ImageOps

원본_폴더 = Path(r"C:\Users\User\OneDrive\Files\10_LogicFlow\홍보\활동사진_모자이크")
출력_폴더 = Path("images/gallery")
썸네일_폴더 = 출력_폴더 / "thumb"
출력_폴더.mkdir(parents=True, exist_ok=True)
썸네일_폴더.mkdir(parents=True, exist_ok=True)

FULL_폭 = 1400   # 라이트박스 확대용
THUMB_폭 = 640   # 격자 표시용


def 리사이즈_저장(이미지: Image.Image, 목표_폭: int, 저장_경로: Path, 품질: int) -> int:
    """비율을 유지해 축소 후 저장하고 파일 크기(바이트)를 반환한다."""
    사본 = 이미지.copy()
    if 사본.width > 목표_폭:
        목표_높이 = round(사본.height * 목표_폭 / 사본.width)
        사본 = 사본.resize((목표_폭, 목표_높이), Image.LANCZOS)
    # EXIF를 넘기지 않고 저장 → 위치·기기 정보 제거
    사본.save(저장_경로, "JPEG", quality=품질, optimize=True, progressive=True)
    return 저장_경로.stat().st_size


항목_목록 = []
원본_총량 = 변환_총량 = 0

for 원본_경로 in sorted(원본_폴더.glob("*.jpg")):
    원본_총량 += 원본_경로.stat().st_size

    with Image.open(원본_경로) as 이미지:
        # 세로로 찍은 사진이 눕지 않도록 EXIF 회전값을 실제로 적용한 뒤 제거
        이미지 = ImageOps.exif_transpose(이미지).convert("RGB")
        가로세로비 = round(이미지.width / 이미지.height, 3)

        변환_총량 += 리사이즈_저장(이미지, FULL_폭, 출력_폴더 / 원본_경로.name, 82)
        변환_총량 += 리사이즈_저장(이미지, THUMB_폭, 썸네일_폴더 / 원본_경로.name, 78)

    # 파일명 규칙: YYYYMMDD_지역_NN.jpg
    맞춤 = re.match(r"(\d{4})(\d{2})(\d{2})_(.+?)_(\d+)", 원본_경로.stem)
    연, 월, 일, 지역, _ = 맞춤.groups()

    항목_목록.append({
        "file": 원본_경로.name,
        "date": f"{연}-{월}-{일}",
        "location": 지역,
        "caption": f"{연}.{월} {지역} 강의",   # ← 실제 기관명으로 바꾸면 더 좋습니다
        "ratio": 가로세로비,
    })

# 최신 사진이 앞에 오도록 정렬
항목_목록.sort(key=lambda 항목: 항목["date"], reverse=True)

결과 = {
    "_주석": "활동사진 갤러리입니다. images/gallery/ 에 사진을 넣고 아래 items에 추가하세요.",
    "_사진추가방법": "python tools/build_gallery.py 를 실행하면 리사이즈와 목록 생성이 자동으로 됩니다.",
    "_항목형식": {
        "file": "images/gallery/ 안의 파일명",
        "date": "YYYY-MM-DD (최신순 정렬 기준)",
        "location": "지역",
        "caption": "사진 위에 표시될 설명. 기관명을 넣으면 신뢰도가 올라갑니다.",
    },
    "heading": "강의 현장",
    "subheading": "수강생들과 함께한 기록입니다",
    "items": 항목_목록,
}

Path("data/gallery.json").write_text(
    json.dumps(결과, ensure_ascii=False, indent=2), encoding="utf-8"
)

print(f"photos      : {len(항목_목록)}")
print(f"before      : {원본_총량 / 1024 / 1024:.1f} MB")
print(f"after       : {변환_총량 / 1024 / 1024:.1f} MB (thumb + full)")
print(f"reduction   : {(1 - 변환_총량 / 원본_총량) * 100:.0f}%")
