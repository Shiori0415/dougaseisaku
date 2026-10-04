# -*- coding: utf-8 -*-
"""上里さん1008の絵コンテ（❶❷）をドキュメント用HTMLで書き出す。
   ショット名は画像に焼き込まず文字で入れる（ドキュメント上で直せるように）。
   実行: python3 tools/build_ue1008_ekonte.py → pdf/ue1008_ekonte.html
"""
import os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
B = "https://raw.githubusercontent.com/Shiori0415/dougaseisaku/claude/4-sheets-later-l5chh0/assets/ue1008/"
L1 = "https://www.instagram.com/reel/DbGnXCnRMrT/?stkn=MWhvbGVkamlwd3Nn"
L2 = "https://www.instagram.com/reel/DdEWeatvvig/?stkn=MWN1aDVpdzZnOGZ0ZQ=="
ONE = [("ショット1　服装１", "a1"), ("ショット2　車が通り　服装変化", "a2"),
       ("ショット3　服装２", "a3"), ("ショット4　服装３　手を振る", "a4")]
TWO = [("ショット1　傷を確認して払い、持ち上げてフレームアウト", "il_s1", 138),
       ("ショット2　bagアップ　歩く", "il_s2", 138),
       ("ショット3　正面から曲がってトラッキング", "s3", 150),
       ("ショット4　パンでブルックリンと後ろ姿", "s4", 150),
       ("ショット5　左方向で入り口に入る　下半身", "s5", 150),
       ("ショット6　右方向で入り口を出る　下半身", "il_s6", 149),
       ("ショット7　傷なしbagアップトラッキング", "s7", 150),
       ("ショット8　店バック　上半身前から　人すれ違って振り返り戻ってフレームアウト", "s8", 150),
       ("ショット9　店舗をぼかして背に、斜め前からフレームアウト", "s9", 150)]
TD = 'style="border:1px solid #999;padding:3px;vertical-align:top"'


def cell(title, img, w, h, pct):
    return (f'<td width="{pct}" {TD}><p style="margin:0 0 2pt;font-size:8pt"><b>{title}</b></p>'
            f'<img src="{B}{img}.jpg" width="{w}" height="{h}"></td>')


def main():
    h = '<html><head><meta charset="utf-8"></head><body style="font-family:Arial">'
    h += f'<h2 style="margin:0 0 4pt">❶絵コンテ　3秒　計12秒　参考<a href="{L1}">Link</a></h2>'
    h += '<table style="border-collapse:collapse"><tr>' + "".join(cell(t, i, 130, 282, "25%") for t, i in ONE) + "</tr></table>"
    h += f'<h2 style="margin:8pt 0 4pt">❷絵コンテ　1秒〜3秒　計20秒　参考<a href="{L2}">Link</a></h2>'
    h += '<table style="border-collapse:collapse">'
    cells = [cell(t, i, 200, hh, "50%") for t, i, hh in TWO] + [f'<td width="50%" {TD}></td>']
    for r in range(0, 10, 2):
        h += "<tr>" + "".join(cells[r:r + 2]) + "</tr>"
    h += "</table></body></html>"
    out = os.path.join(ROOT, "pdf", "ue1008_ekonte.html")
    open(out, "w").write(h)
    print(out, len(h))


if __name__ == "__main__":
    main()
