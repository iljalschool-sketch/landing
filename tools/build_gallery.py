# -*- coding: utf-8 -*-
"""활동사진을 웹용으로 변환하고 gallery.json을 생성한다.

- 원본은 1920x800 배너 비율로 미리 잘라둔 것을 쓴다.
- EXIF(촬영 위치·기기 정보)를 제거해 개인정보 노출을 막는다.
- 격자용 썸네일(thumb)과 확대용 이미지(full)를 각각 생성한다.

파일명 규칙:  YYYYMMDD_기관명_번호.jpg   (예: 20260313_대성에너지_01.jpg)
"""
import json
import re
from pathlib import Path

from PIL import Image, ImageOps

원본_폴더 = Path(r"C:\Users\User\OneDrive\Files\10_LogicFlow\홍보\Photos-1-001_배너")
출력_폴더 = Path("images/gallery")
썸네일_폴더 = 출력_폴더 / "thumb"

FULL_폭 = 1600   # 라이트박스 확대용
THUMB_폭 = 640   # 격자 표시용 (작게 늘어놓으므로 2배 해상도면 충분)


def 리사이즈_저장(이미지: Image.Image, 목표_폭: int, 저장_경로: Path, 품질: int) -> int:
    """비율을 유지해 축소 후 저장하고 파일 크기(바이트)를 반환한다."""
    사본 = 이미지.copy()
    if 사본.width > 목표_폭:
        목표_높이 = round(사본.height * 목표_폭 / 사본.width)
        사본 = 사본.resize((목표_폭, 목표_높이), Image.LANCZOS)
    # EXIF를 넘기지 않고 저장 → 위치·기기 정보 제거
    사본.save(저장_경로, "JPEG", quality=품질, optimize=True, progressive=True)
    return 저장_경로.stat().st_size


def 파일명_해석(파일명: str) -> tuple[str, str]:
    """'20260313_대성에너지_01' → ('2026-03-13', '대성에너지')

    실수로 밑줄이 두 번 들어간 경우(20260514__대성에너지_01)도 처리한다.
    """
    맞춤 = re.match(r"(\d{4})(\d{2})(\d{2})_+(.+?)_+(\d+)$", 파일명)
    if not 맞춤:
        raise ValueError(f"파일명 형식이 다릅니다: {파일명}  (YYYYMMDD_기관명_번호)")
    연, 월, 일, 기관, _ = 맞춤.groups()
    return f"{연}-{월}-{일}", 기관.strip("_")


def 실행() -> None:
    if not 원본_폴더.exists():
        raise SystemExit(f"[중단] 원본 폴더가 없습니다: {원본_폴더}")

    # 이전 사진을 먼저 비운다 (교체 시 옛 파일이 남지 않도록)
    for 폴더 in (출력_폴더, 썸네일_폴더):
        폴더.mkdir(parents=True, exist_ok=True)
    for 기존 in list(출력_폴더.glob("*.jpg")) + list(썸네일_폴더.glob("*.jpg")):
        기존.unlink()

    항목_목록 = []
    원본_총량 = 변환_총량 = 0

    for 원본_경로 in sorted(원본_폴더.glob("*.jpg")):
        일자, 기관 = 파일명_해석(원본_경로.stem)
        원본_총량 += 원본_경로.stat().st_size

        # 저장할 때는 밑줄 중복 같은 흔들림을 없앤 이름으로 통일한다
        저장_이름 = f"{일자.replace('-', '')}_{기관}_{len(항목_목록) + 1:02d}.jpg"

        with Image.open(원본_경로) as 이미지:
            # 세로로 찍은 사진이 눕지 않도록 EXIF 회전값을 적용한 뒤 제거
            이미지 = ImageOps.exif_transpose(이미지).convert("RGB")
            가로세로비 = round(이미지.width / 이미지.height, 3)

            변환_총량 += 리사이즈_저장(이미지, FULL_폭, 출력_폴더 / 저장_이름, 84)
            변환_총량 += 리사이즈_저장(이미지, THUMB_폭, 썸네일_폴더 / 저장_이름, 80)

        연, 월, _ = 일자.split("-")
        항목_목록.append({
            "file": 저장_이름,
            "date": 일자,
            "client": 기관,
            "caption": f"{기관} · {연}.{월}",
            "ratio": 가로세로비,
        })

    # 최신 사진이 앞에 오도록 정렬
    항목_목록.sort(key=lambda 항목: 항목["date"], reverse=True)

    결과 = {
        "_주석": "활동사진 갤러리입니다. 사진을 바꾼 뒤 python tools/build_gallery.py 를 실행하세요.",
        "_원본폴더": str(원본_폴더),
        "_파일명규칙": "YYYYMMDD_기관명_번호.jpg  (예: 20260313_대성에너지_01.jpg)",
        "_주의": "수강생 얼굴이 식별되지 않도록 블러 처리된 사진만 넣으세요.",
        "_항목형식": {
            "file": "images/gallery/ 안의 파일명",
            "date": "YYYY-MM-DD (최신순 정렬 기준)",
            "client": "기관명 (파일명에서 자동으로 읽습니다)",
            "caption": "사진 위에 표시될 설명",
        },
        "heading": "강의 현장",
        "subheading": "수강생들과 함께한 기록입니다",
        "items": 항목_목록,
    }

    Path("data/gallery.json").write_text(
        json.dumps(결과, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"사진 {len(항목_목록)}장")
    for 항목 in 항목_목록:
        print(f"  {항목['date']}  {항목['caption']}")
    print(f"\n원본 {원본_총량 / 1024 / 1024:.1f} MB "
          f"→ 변환 {변환_총량 / 1024 / 1024:.1f} MB (thumb + full)")


if __name__ == "__main__":
    실행()
