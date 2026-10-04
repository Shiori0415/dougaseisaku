# -*- coding: utf-8 -*-
"""上里さん❷の絵コンテ：参考写真のないショットをラフ（線画）で描く。
   実行: python3 tools/build_ue1008_rough.py → assets/ue1008/s{1,2,5,6,7,9}.jpg（800×600）
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "assets", "ue1008")
F = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
W, H = 800, 600
INK, GRAY, LIGHT, RED = (30, 30, 30), (150, 150, 150), (228, 228, 228), (200, 60, 50)


def canvas():
    im = Image.new("RGB", (W, H), "white")
    return im, ImageDraw.Draw(im)


def tag(d, text):
    f = ImageFont.truetype(F, 26)
    d.rectangle((0, 0, 20 + 26 * len(text), 44), fill=INK)
    d.text((10, 8), text, font=f, fill="white")


def arrow(d, p0, p1, label=None, color=RED, w=7, dash=False):
    (x0, y0), (x1, y1) = p0, p1
    if dash:
        n = 10
        for i in range(0, n, 2):
            a, b = i / n, (i + 1) / n
            d.line((x0 + (x1 - x0) * a, y0 + (y1 - y0) * a, x0 + (x1 - x0) * b, y0 + (y1 - y0) * b), fill=color, width=w)
    else:
        d.line((x0, y0, x1, y1), fill=color, width=w)
    import math
    ang = math.atan2(y1 - y0, x1 - x0)
    L = 34
    pts = [(x1, y1),
           (x1 - L * math.cos(ang - 0.45), y1 - L * math.sin(ang - 0.45)),
           (x1 - L * math.cos(ang + 0.45), y1 - L * math.sin(ang + 0.45))]
    d.polygon(pts, fill=color)
    if label:
        f = ImageFont.truetype(F, 30)
        d.text(((x0 + x1) / 2 - 15 * len(label), min(y0, y1) - 46), label, font=f, fill=color)


def bag(d, box, scratch=False, handle=True):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=26, outline=INK, width=6, fill=(205, 190, 170))
    fy = y0 + (y1 - y0) * 0.42
    d.line((x0 + 8, fy, x1 - 8, fy), fill=INK, width=4)
    cx = (x0 + x1) / 2
    d.rectangle((cx - 18, fy - 4, cx + 18, fy + 22), outline=INK, width=4, fill="white")
    if handle:
        hw = (x1 - x0) * 0.28
        d.arc((cx - hw, y0 - (y1 - y0) * 0.45, cx + hw, y0 + (y1 - y0) * 0.25), 180, 360, fill=INK, width=6)
    if scratch:
        sx, sy = x0 + (x1 - x0) * 0.18, y0 + (y1 - y0) * 0.72
        d.line((sx, sy, sx + 30, sy - 10, sx + 50, sy + 5, sx + 85, sy - 8), fill=RED, width=6)


def leg(d, top, foot, wid=70, fill=(70, 70, 80)):
    (tx, ty), (fx, fy) = top, foot
    d.polygon([(tx - wid / 2, ty), (tx + wid / 2, ty), (fx + wid / 2.6, fy), (fx - wid / 2.6, fy)], fill=fill, outline=INK)


def shoe(d, x, y, right=True):
    d.ellipse((x - 40, y - 18, x + 40, y + 12), fill=INK) if True else None


def s1():
    im, d = canvas()
    d.rectangle((0, 480, W, H), fill=LIGHT)
    d.line((0, 480, W, 480), fill=INK, width=4)
    # 鞄を斜めから：正面＋右の側面（マチ）
    body, side = (205, 190, 170), (180, 165, 145)
    d.polygon([(90, 270), (200, 220), (560, 220), (450, 270)], fill=(220, 207, 190), outline=INK)
    d.polygon([(450, 270), (560, 220), (560, 430), (450, 480)], fill=side, outline=INK)
    d.rectangle((90, 270, 450, 480), fill=body, outline=INK, width=6)
    d.line((450, 270, 560, 220), fill=INK, width=6)
    d.line((560, 220, 560, 430), fill=INK, width=6)
    d.line((560, 430, 450, 480), fill=INK, width=6)
    d.line((98, 360, 442, 360), fill=INK, width=4)
    d.rectangle((252, 356, 288, 382), outline=INK, width=4, fill="white")
    d.arc((190, 165, 460, 335), 190, 350, fill=INK, width=6)
    # 傷は側面に
    sx, sy = 470, 400
    d.line((sx, sy, sx + 20, sy - 12, sx + 38, sy - 2, sx + 62, sy - 18), fill=RED, width=6)
    d.ellipse((sx - 25, sy - 55, sx + 90, sy + 30), outline=RED, width=4)
    f = ImageFont.truetype(F, 28)
    d.text((400, 495), "側面の傷を確かめる", font=f, fill=RED)
    # 手のひらで側面を払う
    skin = (235, 205, 185)
    d.polygon([(800, 200), (800, 300), (700, 300), (700, 220)], fill=skin, outline=INK)
    d.ellipse((620, 205, 760, 315), fill=skin, outline=INK, width=3)
    for i, y in enumerate((212, 236, 260, 284)):
        d.rounded_rectangle((530 + i * 6, y, 650, y + 22), radius=11, fill=skin, outline=INK, width=3)
    for k in range(3):
        d.arc((560 - k * 25, 240 - k * 20, 700 + k * 25, 420 + k * 20), 100, 150, fill=GRAY, width=4)
    d.text((600, 140), "手で払う", font=f, fill=RED)
    arrow(d, (600, 330), (560, 380))
    pass  # 左上の「ラフ」表記は入れない
    return im


def s2():
    im, d = canvas()
    d.rectangle((0, 0, W, 90), fill=(60, 60, 65))  # 上着のすそ
    leg(d, (330, 80), (230, 600), 110)
    leg(d, (450, 80), (560, 600), 110, fill=(90, 90, 100))
    d.line((560, 0, 545, 250), fill=INK, width=22)  # 腕
    bag(d, (380, 280, 640, 470))
    for y in (300, 360, 420):
        d.line((70, y, 180, y), fill=GRAY, width=5)
    arrow(d, (600, 545), (770, 545), "歩く")
    pass  # 左上の「ラフ」表記は入れない
    return im


def entrance(d):
    d.rectangle((0, 0, W, 520), fill=(240, 238, 232))
    d.rectangle((60, 40, 290, 520), fill=(120, 110, 100), outline=INK, width=6)  # 入り口
    d.line((175, 40, 175, 520), fill=INK, width=3)
    d.rectangle((0, 520, W, H), fill=LIGHT)
    d.line((0, 520, W, 520), fill=INK, width=4)


def walker(d, cx, facing):
    # 下半身：すそから足元まで
    d.polygon([(cx - 90, 60), (cx + 90, 60), (cx + 100, 200), (cx - 100, 200)], fill=(60, 60, 65), outline=INK)
    leg(d, (cx - 35, 190), (cx - 70 * facing, 510), 65)
    leg(d, (cx + 35, 190), (cx + 70 * facing, 510), 65, fill=(90, 90, 100))
    for fx in (cx - 70 * facing, cx + 70 * facing):
        d.ellipse((fx - 45 + 15 * facing, 495, fx + 45 + 15 * facing, 525), fill=INK)
    bx = cx + 60 * facing
    bag(d, (bx - 75, 200, bx + 75, 320))


def s5():
    im, d = canvas()
    entrance(d)
    walker(d, 500, -1)
    arrow(d, (700, 570), (320, 570), "入る")
    pass  # 左上の「ラフ」表記は入れない
    return im


def s6():
    im, d = canvas()
    entrance(d)
    walker(d, 420, 1)
    arrow(d, (480, 570), (780, 570), "出る")
    pass  # 左上の「ラフ」表記は入れない
    return im


def s7():
    im, d = canvas()
    for x in range(0, W, 120):
        d.line((x, 0, x + 60, 520), fill=LIGHT, width=30)  # 流れる背景
    bag(d, (170, 170, 630, 470))
    for p in ((230, 200), (580, 210)):
        d.line((p[0] - 14, p[1], p[0] + 14, p[1]), fill=GRAY, width=3)
        d.line((p[0], p[1] - 14, p[0], p[1] + 14), fill=GRAY, width=3)
    # カメラが横に並んでついていく
    d.rounded_rectangle((60, 510, 150, 570), radius=8, fill=INK)
    d.ellipse((90, 520, 130, 560), fill="white")
    arrow(d, (170, 540), (760, 540), "鞄と並んで追う")
    pass  # 左上の「ラフ」表記は入れない
    return im


def s9():
    from PIL import ImageFilter
    im, d = canvas()
    # 背景の店：ピントを外してぼかす
    d.rectangle((0, 0, W, 520), fill=(240, 238, 232))
    d.rectangle((120, 60, 560, 150), fill=INK)
    f = ImageFont.truetype(F, 44)
    t = "BROOKLYN MUSEUM"
    d.text((340 - d.textlength(t, font=f) / 2, 82), t, font=f, fill="white")
    d.rectangle((20, 190, 220, 480), outline=INK, width=5, fill=(210, 220, 225))
    d.rectangle((460, 190, 660, 480), outline=INK, width=5, fill=(210, 220, 225))
    d.rectangle((280, 190, 400, 520), outline=INK, width=5, fill=(120, 110, 100))
    d.rectangle((0, 520, W, H), fill=LIGHT)
    im = im.filter(ImageFilter.GaussianBlur(5))
    d = ImageDraw.Draw(im)
    # 手前の人：斜め前からカメラの右手前へ抜ける（ピントは人）
    d.ellipse((560, 120, 700, 270), fill=(60, 50, 45), outline=INK, width=3)
    d.polygon([(520, 280), (760, 260), (840, 600), (480, 600)], fill=(55, 55, 60), outline=INK)
    bag(d, (700, 400, 830, 520))
    arrow(d, (120, 330), (460, 500), None)
    f2 = ImageFont.truetype(F, 28)
    d.text((30, 280), "斜め前から画面の外へ", font=f2, fill=RED)
    d.text((20, 540), "背景の店はぼかす", font=f2, fill=GRAY)
    pass  # 左上の「ラフ」表記は入れない
    return im


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for n, fn in ((1, s1), (2, s2), (5, s5), (6, s6), (7, s7), (9, s9)):
        p = os.path.join(OUT, f"s{n}.jpg")
        fn().convert("RGB").save(p, quality=92)
        print(p)
