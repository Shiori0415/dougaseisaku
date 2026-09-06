# -*- coding: utf-8 -*-
"""撮影機材の「低価格版」と「アップグレード版」を1枚の表で比べられる .xlsx を書き出す。
   実行: python3 tools/build_xlsx_gear.py
     pdf/01_撮影機材_低価格版とアップグレード版.xlsx

   金額はすべて、この表の中で1か所にしか書かない（GEARの数字が唯一の出どころ）。
   合計・差額はExcelの式なので、黄色いセルを書き換えれば全部が計算し直される。
   価格の確度は「確度」列にはっきり書く（確認済／幅あり／概算）。
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
JP = "Meiryo"
INK, MUTED, ACCENT, WARN = "1A1A1A", "5B6266", "A8672A", "9A3B2E"
LINE, HEAD_FILL = "D6DADB", "E4E7E7"
INPUT_FILL, KEEP_FILL, UP_FILL = "FFF6D9", "F4F5F5", "E7F0EA"
thin = Side(style="thin", color=LINE)
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

# 優先度  A＝いちばん効く／B＝画づくりが変わる／—＝上げても差が出ない
# (優先度, 品目, 低価格版の商品, 低価格版の価格, 低価格版URL,
#          アップ版の商品,   アップ版の価格,   アップ版URL, 何が変わるか, 価格の確度)
GEAR = [
 ("A", "マイク（インタビュー用）",
  "買わない（ガンマイクで代用する）", 0, "",
  "DJI Mic 2（送信機2＋受信機＋充電ケース）", 34339, "https://www.amazon.co.jp/dp/B0CFZX734J",
  "インタビュー四人分の声が別物になる。服に留めるので口元三十センチで録れ、ガンマイクの「離れた音」ではなくなる。32bitフロート内部収録で音割れもしない",
  "低＝0円／上＝前回調査で実売を確認"),
 ("A", "三脚（雲台付き）",
  "Velbon EX-440", 3012, "https://www.amazon.co.jp/dp/B0053CEPQU",
  "Manfrotto Befree live アルミニウムT三脚 ビデオ雲台キット（MVKBFRT-LIVE）", 30800,
  "https://www.ginichi.com/shop/products/detail.php?product_id=118199",
  "フルード雲台になり、パン・ティルトがなめらかに止まる。三千円台の三脚は「置いて固定」はできるが、動かしながら撮るとカクつく",
  "低＝掲載に幅あり（3,012／6,018）／上＝店により幅あり（30,800〜40,800・表は銀一）"),
 ("B", "マクロレンズ",
  "SONY E 30mm F3.5 Macro（SEL30M35）", 27800, "https://www.amazon.co.jp/dp/B0055MFTHM",
  "SIGMA 70mm F2.8 DG MACRO Art（ソニーE・中古）", 52000, "https://kakaku.com/item/K0001065920/",
  "30mmは被写体に三センチまで寄る必要があり、カメラの影が革に落ちる。70mmなら離れて同じ大きさに撮れるので、コバ塗り・刻印の寄りが破綻しない",
  "低＝前回調査で実売を確認／上＝中古の幅あり（50,100〜53,700・表は中央値）"),
 ("B", "照明（LED1灯）",
  "Neewer 二色660 LEDビデオライト", 10949, "https://www.amazon.co.jp/dp/B077Z61TPN",
  "Godox SL-60IID ＋ ソフトボックス", 25000, "https://item.rakuten.co.jp/phototiroya/268-00/",
  "六十Wクラスの単灯になり、③の「黒背景に一灯」で光の芯が出る。ソフトボックスで影の硬さも調整できる。Bowensマウントなので後から拡張できる",
  "低＝前回調査で実売を確認／上＝概算（セット構成で変わる）"),
 ("B", "ジンバル",
  "買わない（三脚と手持ちで代替する）", 0, "",
  "Zhiyun Crane M3", 20710, "https://www.amazon.co.jp/dp/B09J4GXV63",
  "④の街歩きと⑥の「工房を歩くカメラ」が安定する。手持ちの揺れを演出として残す方針なら、なくても成立する",
  "低＝0円／上＝前回調査で実売を確認"),
 ("—", "音声レコーダー",
  "ZOOM H1essential", 12626, "https://www.amazon.co.jp/dp/B0CSL4PXDV",
  "同じもので十分", 12626, "https://www.amazon.co.jp/dp/B0CSL4PXDV",
  "32bitフロートで音割れしないので、これ以上のグレードは今回の用途では効果が薄い",
  "前回調査で実売を確認"),
 ("—", "ガンマイク",
  "RODE VideoMic GO II", 16364, "https://www.amazon.co.jp/dp/B09MRLGL7G",
  "同じもので十分", 16364, "https://www.amazon.co.jp/dp/B09MRLGL7G",
  "作業音（刃・ミシン・コバ磨き）を狙うのがこのマイクの役割。声はDJI Mic 2に任せるので据え置き",
  "前回調査で実売を確認"),
 ("—", "レフ板",
  "EMART レフ板 60cm 丸レフ板 5in1", 1099, "https://www.amazon.co.jp/dp/B0CHNY19K3",
  "同じもので十分", 1099, "https://www.amazon.co.jp/dp/B0CHNY19K3",
  "上げても画に差が出ない。一灯だけだと影が硬くなるので反対側から起こす",
  "前々回調査時の値（前回は再確認できず）"),
 ("—", "黒スチレンボード",
  "ブラックスチレンボード A2・5mm厚 ×2枚", 1122, "https://www.signmall.jp/item/10899910261.html",
  "同じもので十分", 1122, "https://www.signmall.jp/item/10899910261.html",
  "上げても画に差が出ない。③の黒背景と、余計な光を止める遮光板",
  "前回調査で実売を確認（1枚561円×2）"),
 ("—", "アクリル板",
  "PULUZ アクリル反射板 40cm（黒）", 3000, "https://www.amazon.co.jp/dp/B0C49DT18X",
  "同じもので十分", 3000, "https://www.amazon.co.jp/dp/B0C49DT18X",
  "上げても画に差が出ない。製品を映り込ませる台",
  "概算（購入時に要確認）"),
 ("—", "SDカード（任意）",
  "SanDisk Extreme 128GB（V30以上）", 2500, "https://www.amazon.co.jp/s?k=SanDisk+Extreme+SD+128GB+V30",
  "同じもので十分", 2500, "https://www.amazon.co.jp/s?k=SanDisk+Extreme+SD+128GB+V30",
  "四K動画ならV30で足りる。お使いのカメラのカードをそのまま使えるなら買わなくてよい",
  "概算（商品ページ未特定・リンクは検索結果）"),
 ("—", "予備バッテリー",
  "買わない（本体付属の一個で回す）", 0, "",
  "NP-FW50 互換2個＋充電器セット", 3300, "",
  "一日で撮り切らず日を分ければ、本体付属の一個で足りる。連日撮るなら足す",
  "低＝0円／上＝前回調査時の値（商品ページ未特定）"),
]


def asin(url):
    """amazon.co.jp の商品ページURLからASINを取り出す。商品ページでなければ None"""
    import re
    m = re.search(r"amazon\.co\.jp/(?:.*/)?dp/([A-Z0-9]{10})", url or "")
    return m.group(1) if m else None


def sakura(url):
    """サクラチェッカーの判定ページURL。Amazonの商品ページでなければ空"""
    a = asin(url)
    return f"https://sakura-checker.jp/search/{a}/" if a else ""


NOTES = [
 ("価格について（必ずお読みください）", WARN, True),
 ("・この資料を作った作業環境からは、Amazon・価格.com・楽天・サインモール・サクラチェッカーのいずれにも接続できません。", MUTED, False),
 ("　そのため、表の金額は前回調査した時点のものです。リンク先の今の金額と違っていることがあります。", MUTED, False),
 ("・「確度」列に、その金額がどこまで確かかを一件ずつ書いてあります。発注前に、リンクを開いて金額をご確認ください。", MUTED, False),
 ("・幅があるもの：三脚（低3,012／6,018、上30,800〜40,800）、マクロレンズの上（中古50,100〜53,700）。", MUTED, False),
 ("・概算のもの：照明の上、アクリル板、SDカード、予備バッテリー。", MUTED, False),
 ("", MUTED, False),
 ("表の見かた", ACCENT, True),
 ("・優先度A＝いちばん効く二つ（音と、カメラの支え）。B＝画づくりが変わる。「—」は上げても差が出ないので据え置きです。", MUTED, False),
 ("・「買わない」と書いた行は低価格版では0円です。アップグレード版で初めて買う機材です。", MUTED, False),
 ("・薄い黄色のセルを書き換えると、差額と三つの合計が自動で計算し直されます。", MUTED, False),
 ("・カメラ本体はお手持ちのものを使う前提のため、この表には入っていません。", MUTED, False),
 ("", MUTED, False),
 ("評価とサクラチェックについて", ACCENT, True),
 ("・カメラ用品はソニー純正、音声はZOOM・RODE・DJIという実績あるメーカーの製品から選びました。", MUTED, False),
 ("・無名ブランドの安価な音声機材は、レビューが操作されている可能性があるため外しています。", MUTED, False),
 ("・ZOOM H1essentialの評価（4.53／5・32件）はYahoo!ショッピングの掲載値です。リンク先のAmazonの評価ではありません。", MUTED, False),
 ("・サクラチェッカー（sakura-checker.jp）はこの環境から接続が遮断されており、こちらで判定を実行できませんでした。", MUTED, False),
 ("　代わりに「サクラチェッカー」列に、商品ごとの判定ページへのリンクを入れてあります。クリックすれば数秒で判定が出ます。", MUTED, False),
 ("　Amazon以外の販売ページ（サインモール・銀一・楽天・価格.com）はサクラチェッカーの対象外です。", MUTED, False),
 ("", MUTED, False),
 ("注意", ACCENT, True),
 ("・マクロレンズはソニーEマウント専用です。お使いのカメラが別マウントの場合は、同じ焦点距離帯のものに読み替えてください。", MUTED, False),
 ("・アップグレード版のマクロレンズは中古価格です。新品にする場合は金額が上がります。", MUTED, False),
 ("・撮影するカットの一覧は別ファイル「02_場面別ショットリスト.xlsx」にあります。", MUTED, False),
]


def build(path):
    wb = Workbook(); ws = wb.active
    ws.title = "機材と費用"
    ws.sheet_view.showGridLines = False

    ws["A1"] = "BROOKLYN MUSEUM ／ 向島工房　動画制作"
    ws["A1"].font = Font(name=JP, size=9, color=MUTED)
    ws["A2"] = "撮影機材と費用　低価格版とアップグレード版の比較"
    ws["A2"].font = Font(name=JP, size=18, bold=True, color=INK)
    ws["A3"] = "動画八本を一人で撮る前提。カメラはお手持ちのものを使い、それ以外に必要な機材を一枚にまとめています。"
    ws["A3"].font = Font(name=JP, size=10, color=MUTED)
    ws["A4"] = "金額は前回調査した時点のものです。この環境から通販サイトに接続できないため、発注前にリンク先でご確認ください。"
    ws["A4"].font = Font(name=JP, size=10, bold=True, color=WARN)

    hr = 6
    headers = ["優先度", "品目",
               "低価格版　商品", "低価格版　価格", "低価格版　商品ページ",
               "アップグレード版　商品", "アップグレード版　価格", "アップグレード版　商品ページ",
               "差額", "何が変わるか", "価格の確度", "サクラチェッカー"]
    widths = [8, 20, 34, 13, 24, 38, 15, 24, 11, 54, 40, 34]
    for i, (h, w) in enumerate(zip(headers, widths), start=1):
        c = ws.cell(row=hr, column=i, value=h)
        c.font = Font(name=JP, size=9, bold=True, color=MUTED)
        c.fill = PatternFill("solid", fgColor=HEAD_FILL)
        c.alignment = Alignment(vertical="center", wrap_text=True, horizontal="center")
        c.border = BORDER
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[hr].height = 30

    first = hr + 1
    for i, (pri, item, lo, lop, lou, up, upp, upu, why, conf) in enumerate(GEAR):
        row = first + i
        sk = sakura(lou) or sakura(upu)
        for col, v in enumerate([pri, item, lo, lop, lou, up, upp, upu, None, why, conf,
                                 (sk or "Amazon以外のため対象外")], start=1):
            c = ws.cell(row=row, column=col, value=v)
            c.border = BORDER
            c.font = Font(name=JP, size=10, color=INK)
            c.alignment = Alignment(vertical="top", wrap_text=(col in (3, 5, 6, 8, 10, 11)),
                                    horizontal="center" if col == 1 else
                                    ("right" if col in (4, 7, 9) else "left"))
        ws.cell(row=row, column=9, value=f"=G{row}-D{row}")
        for col in (4, 7, 9):
            ws.cell(row=row, column=col).number_format = '#,##0;(#,##0);-'
        ws.cell(row=row, column=4).fill = PatternFill("solid", fgColor=INPUT_FILL)
        ws.cell(row=row, column=7).fill = PatternFill("solid", fgColor=INPUT_FILL)
        fill = UP_FILL if pri in ("A", "B") else KEEP_FILL
        ws.cell(row=row, column=1).fill = PatternFill("solid", fgColor=fill)
        ws.cell(row=row, column=1).font = Font(name=JP, size=10, bold=(pri in ("A", "B")), color=INK)
        if sk:
            sc = ws.cell(row=row, column=12)
            sc.hyperlink = sk
            sc.font = Font(name=JP, size=9, color="0563C1", underline="single")
        else:
            ws.cell(row=row, column=12).font = Font(name=JP, size=9, color=MUTED)
        for col, u in ((5, lou), (8, upu)):
            if u:
                lc = ws.cell(row=row, column=col)
                lc.value = u
                lc.hyperlink = u
                lc.font = Font(name=JP, size=9, color="0563C1", underline="single")
        ws.row_dimensions[row].height = 58
    last = first + len(GEAR) - 1

    # ---- 合計 ----
    tr = last + 1
    ws.cell(row=tr, column=2, value="合計").font = Font(name=JP, size=12, bold=True, color=INK)
    for col in range(1, 13):
        ws.cell(row=tr, column=col).border = BORDER
    for col, formula in ((4, f"=SUM(D{first}:D{last})"), (7, f"=SUM(G{first}:G{last})"), (9, f"=G{tr}-D{tr}")):
        c = ws.cell(row=tr, column=col, value=formula)
        c.font = Font(name=JP, size=12, bold=True, color=INK)
        c.number_format = '#,##0;(#,##0);-'
        c.alignment = Alignment(horizontal="right")
    ws.row_dimensions[tr].height = 26

    # ---- 三つの選び方 ----
    r = tr + 2
    ws.cell(row=r, column=2, value="三つの選び方").font = Font(name=JP, size=12, bold=True, color=INK)
    r += 1
    a_rows = [first + i for i, g in enumerate(GEAR) if g[0] == "A"]
    opts = [
        ("① 低価格版のまま", f"=D{tr}", "いま組んである最小構成。八本すべて撮り切れます。"),
        ("② 音と支えだけ上げる（優先度A）", f"=D{tr}+" + "+".join(f"I{x}" for x in a_rows),
         "マイクと三脚だけアップグレード。インタビュー四人分の声と、動かすカットの安定がいちばん変わります。"),
        ("③ 全部上げる", f"=G{tr}", "アップグレード版の合計。"),
    ]
    for name, formula, note in opts:
        ws.cell(row=r, column=2, value=name).font = Font(name=JP, size=11, bold=True, color=INK)
        c = ws.cell(row=r, column=4, value=formula)
        c.font = Font(name=JP, size=12, bold=True, color=INK)
        c.number_format = '#,##0'
        c.alignment = Alignment(horizontal="right")
        ws.cell(row=r, column=6, value=note).font = Font(name=JP, size=9, color=MUTED)
        for col in (2, 3, 4, 5, 6):
            ws.cell(row=r, column=col).border = BORDER
        ws.row_dimensions[r].height = 22
        r += 1

    # ---- 注記 ----
    r += 2
    for text, color, bold in NOTES:
        c = ws.cell(row=r, column=1, value=text)
        c.font = Font(name=JP, size=(11 if bold else 9), bold=bold, color=color)
        r += 1

    ws.freeze_panes = ws.cell(row=first, column=3)
    wb.save(path)
    lo_total = sum(g[3] for g in GEAR)
    up_total = sum(g[6] for g in GEAR)
    a_diff = sum(g[6] - g[3] for g in GEAR if g[0] == "A")
    return path, lo_total, lo_total + a_diff, up_total


if __name__ == "__main__":
    out = os.path.join(ROOT, "pdf")
    os.makedirs(out, exist_ok=True)
    p, lo, mid, up = build(os.path.join(out, "01_撮影機材_低価格版とアップグレード版.xlsx"))
    print(f"{p}\n  ① 低価格版 {lo:,}円 ／ ② 音と支えだけ {mid:,}円 ／ ③ 全部上げる {up:,}円")
