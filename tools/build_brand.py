# -*- coding: utf-8 -*-
"""브랜드 로고를 웹용으로 변환하고 파비콘·OG 이미지를 생성한다."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

로고_원본 = Path(r"C:\Users\User\OneDrive\Files\10_LogicFlow\11_Assets\logo")
출력 = Path("images/brand")
출력.mkdir(parents=True, exist_ok=True)

브랜드_그린 = (11, 77, 59)
브랜드_딥 = (7, 48, 36)
그로스_그린 = (22, 107, 82)

# ── 1. 로고 PNG 웹용 축소 ──────────────────────────────────────────
변환_목록 = [
    ("01_그린_로고/LogicFlow_가로형_그린.png",    "logo-horizontal-green.png", 600),
    ("02_화이트_로고/LogicFlow_가로형_화이트.png", "logo-horizontal-white.png", 600),
    ("01_그린_로고/LogicFlow_심볼_그린.png",      "symbol-green.png",          256),
    ("02_화이트_로고/LogicFlow_심볼_화이트.png",   "symbol-white.png",          256),
]

for 원본_상대경로, 출력_파일명, 목표_폭 in 변환_목록:
    with Image.open(로고_원본 / 원본_상대경로) as 이미지:
        이미지 = 이미지.convert("RGBA")
        목표_높이 = round(이미지.height * 목표_폭 / 이미지.width)
        축소본 = 이미지.resize((목표_폭, 목표_높이), Image.LANCZOS)
        축소본.save(출력 / 출력_파일명, "PNG", optimize=True)
    print(f"  {출력_파일명}: {목표_폭}x{목표_높이}")

# ── 2. 파비콘 ─────────────────────────────────────────────────────
with Image.open(로고_원본 / "01_그린_로고/LogicFlow_앱아이콘_라이트.png") as 앱아이콘:
    앱아이콘 = 앱아이콘.convert("RGBA")
    앱아이콘.resize((180, 180), Image.LANCZOS).save(출력 / "favicon-180.png", "PNG", optimize=True)
    # .ico는 여러 해상도를 한 파일에 담는다
    앱아이콘.resize((256, 256), Image.LANCZOS).save(
        Path("favicon.ico"), "ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)]
    )
print("  favicon-180.png, favicon.ico")


# ── 3. OG 이미지 (카톡·슬랙 공유 썸네일) ───────────────────────────
def 한글_폰트(크기: int) -> ImageFont.FreeTypeFont:
    """윈도우 기본 한글 폰트를 불러온다."""
    for 경로 in (r"C:\Windows\Fonts\malgunbd.ttf", r"C:\Windows\Fonts\malgun.ttf"):
        if Path(경로).exists():
            return ImageFont.truetype(경로, 크기)
    return ImageFont.load_default()


# OG 이미지(공유 썸네일)는 여기서 만들지 않는다.
# 문구가 data/brand.json에 있으므로 tools/build_meta.py가 담당한다.
# 출처가 둘이면 문구를 바꿨을 때 한쪽만 바뀌어 어긋난다.
print("  og-image.png: tools/build_meta.py 에서 생성합니다")


# ── 4. 프로필 사진 ────────────────────────────────────────────────
# 원본이 3:4 세로 사진이다. 정사각형으로 자르면 화면의 1/4이 날아가고
# 인물이 답답해 보여서, 원본 비율을 그대로 살린다.
# 더 고화질이 필요하면 같은 폴더의 PNG를 쓰면 된다 (현재 PNG 사용 중).
프로필_원본 = Path(
    r"C:\Users\User\OneDrive\Files\10_LogicFlow\11_Assets\대표정보\강혜진_프로필사진_F.png"
)

if 프로필_원본.exists():
    with Image.open(프로필_원본) as 사진:
        사진 = 사진.convert("RGB")
        가로, 세로 = 600, 800                       # 3:4 — 표시 크기(300x400)의 2배
        목표비 = 가로 / 세로

        # 원본이 목표보다 넓으면 좌우를, 길면 위아래를 깎아 3:4를 맞춘다.
        # 위아래를 깎을 때는 얼굴이 위쪽에 있으므로 아래에서 더 덜어낸다.
        if 사진.width / 사진.height > 목표비:
            새_폭 = round(사진.height * 목표비)
            왼쪽 = (사진.width - 새_폭) // 2
            자른_사진 = 사진.crop((왼쪽, 0, 왼쪽 + 새_폭, 사진.height))
        else:
            새_높이 = round(사진.width / 목표비)
            위 = round((사진.height - 새_높이) * 0.3)
            자른_사진 = 사진.crop((0, 위, 사진.width, 위 + 새_높이))

        프로필 = 자른_사진.resize((가로, 세로), Image.LANCZOS)
        프로필.save(출력 / "profile.jpg", "JPEG", quality=88, optimize=True, progressive=True)
    print(f"  profile.jpg: {가로}x{세로} ({(출력 / 'profile.jpg').stat().st_size // 1024} KB)")
else:
    print("  [건너뜀] 프로필 원본을 찾지 못했습니다")
