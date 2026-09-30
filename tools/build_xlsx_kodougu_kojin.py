# -*- coding: utf-8 -*-
"""小道具・備品チェックリストを、出演者ひとりにつき一枚のシートで書き出す。
   実行: python3 tools/build_xlsx_kodougu_kojin.py → pdf/04_小道具チェックリスト_個人別.xlsx
   シートは 難波さん／上里さん／北条さん の三枚。
   Googleドライブに上げて「Googleスプレッドシートで開く」と、
   プルダウン（未／済／不要）・色分け・進み具合の数式が残ったまま開く。
"""
import os

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
JP = "Meiryo"
INK, MUTED, GOLD, LINE, BAND, ALT = "15191C", "5B6266", "A8672A", "D9D4CB", "EDE6DA", "FAF7F2"

# (分類, [(品目, 数, 使う場面・備考, 状態)])  状態：未 か 要確認
FIT = "鞄に無理なく収まる量"
PEOPLE = {
    "難波さん": [
        ("鞄", [
            ("鞄（動画用）", "三パターン", "", "未"),
            ("鞄（スチール撮影用）", "色違いを複数", "ロケ地の移動中に持って運ぶ（運ぶ人は要確認）", "未"),
            ("バッグチャーム", "", "要否を確認", "要確認"),
        ]),
        ("衣装", [
            ("衣装", "三パターン", "", "未"),
            ("靴", "", "", "未"),
            ("アクセサリー", "", "", "未"),
            ("サングラス", "", "絵コンテ（Parisa Wang）のショット3・5でかけている", "要確認"),
        ]),
        ("小道具", [
            ("スマートフォン", "", "操作する場面で使う", "未"),
        ]),
        ("鞄の中身", [
            ("ノート", "", FIT, "未"),
            ("イヤホン", "", FIT, "未"),
            ("ファイル", "", FIT, "未"),
            ("手鏡", "", FIT, "未"),
            ("ポーチ", "", FIT, "未"),
            ("リップ", "", FIT, "未"),
            ("メイク道具", "", FIT, "未"),
        ]),
        ("雨対策・身支度", [
            ("傘", "", "雨の日に使う", "未"),
            ("鏡", "", "屋外で身なりを確かめる", "未"),
        ]),
    ],
    "上里さん": [
        ("鞄", [
            ("鞄（動画用）", "三パターン", "", "未"),
            ("鞄（スチール撮影用）", "色違いを複数", "ロケ地の移動中に持って運ぶ（運ぶ人は要確認）", "未"),
        ]),
        ("衣装", [
            ("衣装", "三パターン", "", "未"),
            ("靴", "", "", "未"),
            ("アクセサリー", "", "", "未"),
            ("サングラス", "", "任意", "要確認"),
            ("眼鏡", "", "絵コンテ（chloecleroux）のショット3でかけている", "要確認"),
        ]),
        ("小道具", [
            ("スマートフォン", "", "電話する場面で使う", "未"),
        ]),
        ("雨対策・身支度", [
            ("傘", "", "雨の日に使う", "未"),
            ("鏡", "", "屋外で身なりを確かめる", "未"),
        ]),
    ],
    "北条さん": [
        ("鞄", [
            ("鞄（動画用）", "三パターン", "", "未"),
            ("鞄（スチール撮影用）", "色違いを複数", "ロケ地の移動中に持って運ぶ（運ぶ人は要確認）", "未"),
        ]),
        ("衣装", [
            ("衣装", "三パターン", "", "未"),
            ("靴", "", "", "未"),
            ("アクセサリー", "", "絵コンテ（anticrag）のショット2・3で指輪・ネックレスが映る", "要確認"),
            ("サングラス", "", "絵コンテ（SELENT ÉTHER）のショット1で鞄に入れる", "要確認"),
        ]),
        ("小道具", [
            ("スマートフォン", "", "自撮りで使う", "未"),
            ("自撮り棒", "", "", "未"),
            ("飲み物", "", "", "未"),
        ]),
        ("鞄の中身", [
            ("ノート", "", FIT, "未"),
            ("ノートパソコン", "", FIT, "未"),
            ("ペンケース", "", FIT, "未"),
            ("イヤホン", "", FIT, "未"),
            ("ファイル", "", FIT, "未"),
            ("手鏡", "", FIT, "未"),
            ("ポーチ", "", FIT, "未"),
            ("リップ または 香水", "", "動画の中で使う（リップは塗る／香水は吹きかける）", "未"),
            ("メイク道具", "", FIT, "未"),
        ]),
        ("雨対策・身支度", [
            ("傘", "", "雨の日に使う", "未"),
            ("鏡", "", "屋外で身なりを確かめる", "未"),
        ]),
    ],
}

thin = Side(style="thin", color=LINE)
box = Border(left=thin, right=thin, top=thin, bottom=thin)
HEAD = ["確認", "No.", "品目", "数", "使う場面・備考"]
WIDTHS = [9, 5, 26, 14, 54]


def sheet(ws, name, groups):
    ws.sheet_view.showGridLines = False
    ws.page_setup.orientation = "portrait"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    ws["A1"] = f"{name}　小道具・備品チェックリスト"
    ws["A1"].font = Font(name=JP, size=15, bold=True, color=INK)
    ws.row_dimensions[1].height = 28
    ws["A2"] = "撮影日：　　月　　日"
    ws["A2"].font = Font(name=JP, size=10, color=INK)
    ws["C2"] = "「確認」の欄をプルダウンで「済」にする。"
    ws["C2"].font = Font(name=JP, size=9, color=MUTED)

    for c, h in enumerate(HEAD, 1):
        cell = ws.cell(row=4, column=c, value=h)
        cell.font = Font(name=JP, size=10, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=INK)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = box
    ws.row_dimensions[4].height = 22

    dv = DataValidation(type="list", formula1='"未,済,不要,要確認"', allow_blank=True)
    ws.add_data_validation(dv)

    r, n = 5, 0
    for kind, items in groups:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
        cell = ws.cell(row=r, column=1, value=kind)
        cell.font = Font(name=JP, size=10, bold=True, color=INK)
        cell.fill = PatternFill("solid", fgColor=BAND)
        cell.alignment = Alignment(vertical="center", indent=1)
        for col in range(1, 6):
            ws.cell(row=r, column=col).border = box
        ws.row_dimensions[r].height = 20
        r += 1
        for j, (item, qty, note, state) in enumerate(items):
            n += 1
            vals = [state, n, item, qty, note]
            for col, v in enumerate(vals, 1):
                cell = ws.cell(row=r, column=col, value=v)
                cell.font = Font(name=JP, size=10, color=INK if col != 5 else MUTED)
                cell.border = box
                cell.alignment = Alignment(
                    horizontal="center" if col in (1, 2, 4) else "left",
                    vertical="center", wrap_text=True)
                if j % 2:
                    cell.fill = PatternFill("solid", fgColor=ALT)
            dv.add(ws.cell(row=r, column=1))
            ws.row_dimensions[r].height = 22
            r += 1

    rng = f"A5:A{r - 1}"
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"済"'],
        fill=PatternFill("solid", fgColor="D8EBD3"), font=Font(color="2E6B2E", bold=True)))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"要確認"'],
        fill=PatternFill("solid", fgColor="FBE3C8"), font=Font(color=GOLD, bold=True)))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"不要"'],
        font=Font(color="9AA0A3")))

    ws["E2"] = f'="済 "&COUNTIF(A5:A{r - 1},"済")&" ／ 全 "&{n}&" 点"'
    ws["E2"].font = Font(name=JP, size=10, bold=True, color=INK)
    ws["E2"].alignment = Alignment(horizontal="right")

    for i, w in enumerate(WIDTHS):
        ws.column_dimensions["ABCDE"[i]].width = w
    ws.freeze_panes = "A5"


def main():
    wb = Workbook()
    wb.remove(wb.active)
    for name, groups in PEOPLE.items():
        sheet(wb.create_sheet(name), name, groups)
    out = os.path.join(ROOT, "pdf", "04_小道具チェックリスト_個人別.xlsx")
    wb.save(out)
    print(out)


if __name__ == "__main__":
    main()


def split():
    """一人一ファイルでも書き出す（Googleドライブに一人ずつ渡すとき用）。"""
    for name, groups in PEOPLE.items():
        wb = Workbook()
        wb.remove(wb.active)
        sheet(wb.create_sheet(name), name, groups)
        out = os.path.join(ROOT, "pdf", f"04_小道具チェックリスト_{name}.xlsx")
        wb.save(out)
        print(out)


if __name__ == "__main__":
    split()
