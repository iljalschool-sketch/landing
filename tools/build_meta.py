# -*- coding: utf-8 -*-
"""data/brand.json 의 문구를 index.html 과 OG 이미지에 반영한다.

브랜드 메시지를 한 곳에서 관리하기 위한 스크립트다.
index.html 의 아래 두 구간을 통째로 다시 쓴다.

    <!-- brand:seo:start -->  ... </!-- brand:seo:end -->
    <!-- brand:hero:start --> ... </!-- brand:hero:end -->

검색엔진은 JS 렌더링 결과를 제대로 읽지 못하므로, 이 문구들은
JSON에서 직접 그리지 않고 HTML에 '써넣는' 방식을 쓴다.

사용법:  python tools/build_meta.py
"""
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

브랜드_경로 = Path("data/brand.json")
HTML_경로 = Path("index.html")
출력_이미지 = Path("images/brand")

브랜드_딥 = (7, 48, 36)
그로스_그린 = (22, 107, 82)
포인트_옐로우 = (249, 248, 113)


def 한글_폰트(크기: int) -> ImageFont.FreeTypeFont:
    """윈도우 기본 한글 폰트를 불러온다."""
    for 경로 in (r"C:\Windows\Fonts\malgunbd.ttf", r"C:\Windows\Fonts\malgun.ttf"):
        if Path(경로).exists():
            return ImageFont.truetype(경로, 크기)
    return ImageFont.load_default()


def escape(값: str) -> str:
    """HTML 속성에 넣을 수 있게 특수문자를 바꾼다."""
    return (str(값).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def 구간_바꾸기(내용: str, 이름: str, 새_내용: str) -> str:
    """<!-- brand:이름:start --> ~ end 사이를 새 내용으로 교체한다.

    시작 표식의 들여쓰기를 읽어 끝 표식에도 똑같이 적용한다.
    """
    무늬 = re.compile(
        rf"([ \t]*)(<!-- brand:{이름}:start -->)(.*?)([ \t]*)(<!-- brand:{이름}:end -->)",
        re.S,
    )
    if not 무늬.search(내용):
        raise SystemExit(f"[중단] index.html에서 brand:{이름} 표식을 찾지 못했습니다")

    def 치환(맞춤):
        들여쓰기 = 맞춤.group(1)
        return (f"{들여쓰기}{맞춤.group(2)}\n"
                f"{새_내용}\n"
                f"{들여쓰기}{맞춤.group(5)}")

    return 무늬.sub(치환, 내용)


def SEO_블록(브랜드: dict) -> str:
    """검색엔진·공유용 메타태그를 만든다."""
    seo = 브랜드["seo"]
    도메인 = 브랜드["company"]["domain"]
    회사 = 브랜드["company"]["name"]

    return "\n".join([
        f'    <title>{escape(seo["title"])}</title>',
        f'    <meta name="description" content="{escape(seo["description"])}">',
        f'    <meta name="keywords" content="{escape(seo["keywords"])}">',
        f'    <meta name="author" content="{escape(브랜드["company"]["nameEn"])}">',
        f'    <link rel="canonical" href="https://{도메인}/">',
        "",
        '    <meta property="og:type" content="website">',
        f'    <meta property="og:site_name" content="{escape(회사)}">',
        f'    <meta property="og:title" content="{escape(seo["ogTitle"])}">',
        f'    <meta property="og:description" content="{escape(seo["ogDescription"])}">',
        f'    <meta property="og:url" content="https://{도메인}/">',
        f'    <meta property="og:image" content="https://{도메인}/images/brand/og-image.png">',
        '    <meta property="og:image:width" content="1200">',
        '    <meta property="og:image:height" content="630">',
        '    <meta name="twitter:card" content="summary_large_image">',
    ])


def 히어로_블록(브랜드: dict) -> str:
    """첫 화면 문구를 만든다. 강조 부분만 포인트 컬러로 감싼다."""
    카피 = 브랜드["mainCopy"]
    강조 = 카피.get("emphasis")

    def 강조_적용(줄: str) -> str:
        if 강조 and 강조 in 줄:
            return 줄.replace(강조, f'<span class="text-point">{강조}</span>')
        return 줄

    소개 = 브랜드["companyIntro"]
    # 긴 문장은 데스크톱에서 두 줄로 끊어 읽기 쉽게 한다
    자르는_곳 = 소개.find("통해 ")
    if 자르는_곳 > 0:
        앞, 뒤 = 소개[:자르는_곳 + 3], 소개[자르는_곳 + 3:]
        소개_html = f'{앞}<br class="hidden md:block">\n                {뒤}'
    else:
        소개_html = 소개

    return "\n".join([
        # 슬로건은 확정된 브랜드 문구이므로 작게 흘리지 않고 또렷하게 보여준다
        f'            <p class="text-point font-bold mb-5 tracking-wide text-xl md:text-2xl">{브랜드["slogan"]}</p>',
        '            <h1 class="text-4xl md:text-6xl font-extrabold mb-8 leading-tight">',
        f'                {강조_적용(카피["line1"])} <br>',
        f'                {강조_적용(카피["line2"])}',
        '            </h1>',
        '            <p class="text-lg text-mint mb-12 opacity-90 max-w-2xl mx-auto leading-relaxed">',
        f'                {소개_html}',
        '            </p>',
    ])


def OG_이미지_만들기(브랜드: dict) -> None:
    """카톡·슬랙 공유 썸네일을 다시 그린다."""
    문구 = 브랜드["ogImage"]
    폭, 높이 = 1200, 630

    og = Image.new("RGB", (폭, 높이), 브랜드_딥)
    그리기 = ImageDraw.Draw(og)

    # 위에서 아래로 딥 그린 → 그로스 그린 그라데이션
    for y in range(높이):
        비율 = y / 높이
        색 = tuple(round(시작 + (끝 - 시작) * 비율)
                   for 시작, 끝 in zip(브랜드_딥, 그로스_그린))
        그리기.line([(0, y), (폭, y)], fill=색)

    # 우하단 심볼 워터마크
    심볼_경로 = 출력_이미지 / "symbol-white.png"
    if 심볼_경로.exists():
        with Image.open(심볼_경로) as 심볼:
            워터마크 = 심볼.resize((420, 420), Image.LANCZOS)
            투명도 = 워터마크.getchannel("A").point(lambda 값: round(값 * 0.08))
            워터마크.putalpha(투명도)
            og.paste(워터마크, (폭 - 330, 높이 - 300), 워터마크)

    # 가로형 화이트 로고
    로고_경로 = 출력_이미지 / "logo-horizontal-white.png"
    if 로고_경로.exists():
        with Image.open(로고_경로) as 로고:
            로고_폭 = 400
            로고_높이 = round(로고.height * 로고_폭 / 로고.width)
            og.paste(로고.resize((로고_폭, 로고_높이), Image.LANCZOS), (80, 95),
                     로고.resize((로고_폭, 로고_높이), Image.LANCZOS))

    그리기.text((80, 265), 문구["line1"], font=한글_폰트(52), fill=(255, 255, 255))
    그리기.text((80, 340), 문구["line2"], font=한글_폰트(52), fill=포인트_옐로우)
    그리기.text((80, 470), 문구["tagline"], font=한글_폰트(28), fill=(168, 224, 199))
    그리기.text((80, 520), 브랜드["company"]["domain"], font=한글_폰트(26), fill=(130, 180, 160))

    저장_경로 = 출력_이미지 / "og-image.png"
    og.save(저장_경로, "PNG", optimize=True)
    print(f"  og-image.png 재생성 ({저장_경로.stat().st_size // 1024} KB)")


def 실행() -> None:
    브랜드 = json.loads(브랜드_경로.read_text(encoding="utf-8"))
    내용 = HTML_경로.read_text(encoding="utf-8")

    내용 = 구간_바꾸기(내용, "seo", SEO_블록(브랜드))
    내용 = 구간_바꾸기(내용, "hero", 히어로_블록(브랜드))
    HTML_경로.write_text(내용, encoding="utf-8")

    print("index.html 반영 완료")
    print(f"  제목   : {브랜드['seo']['title']}")
    print(f"  슬로건 : {브랜드['slogan']}")
    print(f"  메인   : {브랜드['mainCopy']['line1']} {브랜드['mainCopy']['line2']}")

    OG_이미지_만들기(브랜드)


if __name__ == "__main__":
    실행()
