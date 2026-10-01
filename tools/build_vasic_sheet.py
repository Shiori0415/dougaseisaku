# -*- coding: utf-8 -*-
"""VASIC参考写真を、A4（余白1cm）一枚に収まる画像二枚に組む。
   実行: python3 tools/build_vasic_sheet.py → assets/sheet/page1.jpg, page2.jpg
   1枚目：全身25枚／2枚目：全身の残り・腰下・階段。番号と分類は写真の左上に焼き込む。
"""
from PIL import Image, ImageDraw, ImageFont

KOSHI = [19, 20, 31, 12]
KAIDAN = [2, 27, 45]
ZEN = [i for i in range(1, 51) if i not in KOSHI + KAIDAN]
W, H = 1122, 1636            # 19cm × 27.7cm（A4から上下左右1cmを引いた本文域）
CW, CH, G, GG = 188, 235, 6, 10   # ショット帳と同じく詰めた格子
HEAD = 34
FONT = ImageFont.truetype("/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf", 26)
PAGES = [[("全身", ZEN[:25])], [("全身", ZEN[25:]), ("腰下", KOSHI), ("階段", KAIDAN)]]


HFONT = ImageFont.truetype("/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf", 24)


def cell(src, n):
    im = Image.open(f"assets/ref11/{src:02d}.jpg").convert("RGB").resize((CW, CH), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    t = str(n)
    d.rounded_rectangle((7, 7, 7 + d.textlength(t, font=FONT) + 16, 7 + 34), 6, fill=(20, 20, 20))
    d.text((15, 10), t, font=FONT, fill="white")
    mask = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, CW - 1, CH - 1), 8, fill=255)
    out = Image.new("RGB", (CW, CH), "white")
    out.paste(im, (0, 0), mask)
    return out


num = 0
x0 = (W - (5 * CW + 4 * G)) // 2
for pi, groups in enumerate(PAGES):
    pg = Image.new("RGB", (W, H), "white")
    y = 0
    for gi, (tag, ids) in enumerate(groups):
        if gi:
            y += GG
        ImageDraw.Draw(pg).text((x0, y + 6), " ".join(tag), font=HFONT, fill=(119, 115, 107))
        y += HEAD
        for r in range(0, len(ids), 5):
            for c, src in enumerate(ids[r:r + 5]):
                num += 1
                pg.paste(cell(src, num), (x0 + c * (CW + G), y))
            y += CH + G
    assert y <= H, y
    pg.save(f"assets/sheet/page{pi + 1}.jpg", quality=80)
    print(pi + 1, y)
