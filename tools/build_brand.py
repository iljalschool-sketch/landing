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


OG_폭, OG_높이 = 1200, 630
og = Image.new("RGB", (OG_폭, OG_높이), 브랜드_딥)
그리기 = ImageDraw.Draw(og)

# 대각선 그라데이션 배경 (브랜드 그라데이션과 동일한 방향)
for y in range(OG_높이):
    비율 = y / OG_높이
    색 = tuple(
        round(시작 + (끝 - 시작) * 비율)
        for 시작, 끝 in zip(브랜드_딥, 그로스_그린)
    )
    그리기.line([(0, y), (OG_폭, y)], fill=색)

# 우하단 심볼 워터마크
with Image.open(출력 / "symbol-white.png") as 심볼:
    워터마크 = 심볼.resize((420, 420), Image.LANCZOS)
    투명도 = 워터마크.getchannel("A").point(lambda 값: round(값 * 0.08))
    워터마크.putalpha(투명도)
    og.paste(워터마크, (OG_폭 - 330, OG_높이 - 300), 워터마크)

# 가로형 화이트 로고
with Image.open(출력 / "logo-horizontal-white.png") as 로고:
    로고_폭 = 440
    로고_높이 = round(로고.height * 로고_폭 / 로고.width)
    로고 = 로고.resize((로고_폭, 로고_높이), Image.LANCZOS)
    og.paste(로고, (80, 110), 로고)

그리기.text((80, 285), "데이터 기반 리포팅 솔루션", font=한글_폰트(54), fill=(255, 255, 255))
그리기.text((80, 365), "메타로직 아키텍처를 설계합니다", font=한글_폰트(54), fill=(168, 224, 199))
그리기.text((80, 490), "logicflow.ai.kr", font=한글_폰트(30), fill=(140, 190, 170))

og.save(출력 / "og-image.png", "PNG", optimize=True)
print(f"  og-image.png: {OG_폭}x{OG_높이} ({(출력 / 'og-image.png').stat().st_size // 1024} KB)")


# ── 4. 프로필 사진 ────────────────────────────────────────────────
# 원본은 세로 전신 사진이므로, 얼굴과 상반신이 들어가도록 정사각형으로 자른다.
# 더 고화질이 필요하면 같은 폴더의 PNG를 쓰면 된다 (현재 PNG 사용 중).
프로필_원본 = Path(
    r"C:\Users\User\OneDrive\Files\10_LogicFlow\11_Assets\대표정보\강혜진_프로필사진_F.png"
)

if 프로필_원본.exists():
    with Image.open(프로필_원본) as 사진:
        사진 = 사진.convert("RGB")
        자르기_크기 = 880
        왼쪽 = (사진.width - 자르기_크기) // 2
        위 = 60                        # 머리 위 여백을 조금만 남긴다
        상반신 = 사진.crop((왼쪽, 위, 왼쪽 + 자르기_크기, 위 + 자르기_크기))
        상반신 = 상반신.resize((560, 560), Image.LANCZOS)   # 표시 크기(224px)의 2배
        상반신.save(출력 / "profile.jpg", "JPEG", quality=88, optimize=True, progressive=True)
    print(f"  profile.jpg: 560x560 ({(출력 / 'profile.jpg').stat().st_size // 1024} KB)")
else:
    print("  [건너뜀] 프로필 원본을 찾지 못했습니다")
