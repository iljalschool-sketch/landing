# -*- coding: utf-8 -*-
"""Excel로 통합문서를 재계산하고 수식 오류를 보고한다.

openpyxl은 수식을 문자열로만 써넣고 계산 결과를 저장하지 않는다.
이 스크립트가 Excel을 띄워 실제로 계산시킨 뒤 같은 자리에 저장한다.

사용법:  python tools/recalc_excel.py data/강의이력.xlsx
"""
import sys
from pathlib import Path

import win32com.client as win32
from openpyxl.utils import get_column_letter

# Excel이 오류 셀에 남기는 값들
오류_문자열 = ("#N/A", "#VALUE!", "#REF!", "#DIV/0!", "#NUM!", "#NAME?", "#NULL!")


def 재계산(파일_경로: Path) -> int:
    """파일을 재계산해 저장하고, 발견된 오류 개수를 반환한다."""
    엑셀 = win32.DispatchEx("Excel.Application")
    엑셀.Visible = False
    엑셀.DisplayAlerts = False

    오류_수 = 0
    수식_수 = 0
    try:
        통합문서 = 엑셀.Workbooks.Open(str(파일_경로.resolve()))

        # 늦은 바인딩(late binding)에서는 메서드 이름이 바로 안 잡힐 때가 있어
        # 강한 순서대로 시도한다.
        for 메서드_이름 in ("CalculateFullRebuild", "CalculateFull", "Calculate"):
            try:
                getattr(엑셀, 메서드_이름)()
                break
            except AttributeError:
                continue
        else:
            raise RuntimeError("Excel 재계산 메서드를 호출하지 못했습니다")

        for 시트 in 통합문서.Worksheets:
            사용범위 = 시트.UsedRange
            마지막_행 = 사용범위.Row + 사용범위.Rows.Count - 1
            마지막_열 = 사용범위.Column + 사용범위.Columns.Count - 1

            # Rows/Cells 컬렉션을 순회하면 COM 오류가 날 때가 있어
            # 좌표로 직접 접근한다.
            for 행 in range(사용범위.Row, 마지막_행 + 1):
                for 열 in range(사용범위.Column, 마지막_열 + 1):
                    try:
                        칸 = 시트.Cells(행, 열)
                        수식 = 칸.Formula
                        if not isinstance(수식, str) or not 수식.startswith("="):
                            continue
                        수식_수 += 1
                        값 = 칸.Text
                        주소 = f"{시트.Name}!{get_column_letter(열)}{행}"
                    except Exception as 오류내용:
                        print(f"  [읽기실패] {시트.Name} {행}행 {열}열: {오류내용}")
                        continue

                    if any(오류 in str(값) for 오류 in 오류_문자열):
                        오류_수 += 1
                        print(f"  [오류] {주소} = {수식}  →  {값}")
                    else:
                        print(f"  [정상] {주소}  →  {값}")

        통합문서.Save()
        통합문서.Close(SaveChanges=True)
    finally:
        엑셀.Quit()

    print(f"\n수식 {수식_수}개 중 오류 {오류_수}개")
    return 오류_수


if __name__ == "__main__":
    경로 = Path(sys.argv[1] if len(sys.argv) > 1 else "data/강의이력.xlsx")
    if not 경로.exists():
        sys.exit(f"파일을 찾을 수 없습니다: {경로}")
    sys.exit(1 if 재계산(경로) else 0)
