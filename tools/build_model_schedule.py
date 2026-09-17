# -*- coding: utf-8 -*-
"""モデル渡しの香盤表を、本編の香盤表（build_shotlist_pdf.py）と同じ形・同じ文言で書き出す。
   実行: python3 tools/build_model_schedule.py
   出力: pdf/model_schedule.html （A4横の印刷用。そのままGoogleドキュメントにも変換できる）

   列は本編と同じ  時刻 ／ 場所の詳細 ／ 登場人物 ／ シーン内容詳細 ／ 尺 ／ 備考。
   画の並び（1枚目 → 2枚目 …）は絵コンテ（deck_data.json）から引くので、本編の香盤表とずれない。
   カット数・機材・段取りの裏は入れない。出演者に渡す紙のため。
"""
import html, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_shotlist_canvas as L
import build_script_canvas as S

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
INK, PROSE, MUTED, FAINT = "#15191c", "#3d4448", "#5b6266", "#8a8f92"
GOLD, LINE, HAIR, BAND = "#a8672a", "#ddd7cd", "#ebe6dd", "#f6f2ec"

MODEL = "難波遥さん"
TEL = "090-1748-0280"
DAY = "10月13日（火）"
RAIN = "10月14日（水）"
SPAN = "9:00〜15:00"

TITLE = "① 服装ごとに画が変わる　／　④ 鞄を持って街を歩く（海外ドラマ風）　／　⑤ コーポレートムービー"
PLACE = "BROOKLYN MUSEUM 表参道店（店休日）　→　表参道けやき並木"
COND = ("<b>一日、表参道から動きません。</b>着替えも荷物置き場も店内です。"
        "<b>①は四色を一巡ずつ撮ります。</b>一つの色で、外を歩く → 店の扉 → 店内まで通して撮ってから、"
        "次の色に着替えます。行ったり来たりしないので、着替えは四回で済みます。"
        "<b>ヘアメイクは付きません。</b>鏡はこちらで用意します。"
        "<b>雨のときは10月14日（水）に振り替えます。</b>前日の夕方までにご連絡します。")


def cam(no, si):
    """絵コンテから、その場面の画の並び（1枚目 → 2枚目 …）を引く"""
    return L.split_cam(S.D[no][si][0])[0]


def sec(no, si):
    return L.scene_len(no, si)


# (時刻, 場所の詳細, 登場人物, 持ち物, 見出し, 画の並び, 尺, 備考)
ROWS = [
 ("band", "午 前　──　店 舗 と 、 け や き 並 木"),

 ("9:00〜9:30", "BROOKLYN MUSEUM 表参道店（店内）", MODEL, "④の衣装 一そろい",
  "支度", "着替えて、髪を整える。カメラを置く位置と、歩いてもらう道を先に見てもらう。", "三十分",
  "<b>この日は店休日なので、一日、店内を使えます。</b>着替えも荷物置き場も店内です。"),

 ("9:30〜10:10", "店内のレジまわり　→　店の前", MODEL + "、店の人", "商品、鞄",
  "⑤ S6 購入・使う", cam("05", 6), sec("05", 6),
  "<b>店の人と二人で映るのは、ここだけです。</b>買う人の役。セリフはありません。"),

 ("10:10〜10:30", "けやき並木の歩道（柵・青山通り寄りの端）", MODEL, "鞄、鉄のフェンス",
  "④ S1 街に置く", cam("04", 1), sec("04", 1),
  "<b>最初と最後は同じ柵。</b>カメラは止めたままで、動くのは背景の街だけです。"),

 ("10:30〜10:45", "S1と同じ柵", MODEL, "鞄、持ち物、靴、ロゴ",
  "④ S4 立ち止まって終わる", cam("04", 4), sec("04", 4),
  "靴と持ち物も一緒に並べて撮ります。"),

 ("10:45〜11:15", "ベンチか石段（真上から撮れるところ）", MODEL, "鞄、中に入れる持ち物",
  "④ S2 中を見せる", cam("04", 2), sec("04", 2),
  "<b>手が真俯瞰で映ります。</b>鞄に入れる持ち物は、先に並べておきます。"),

 ("11:15〜11:40", "けやき並木の裏の路地（人がほとんど通らない側）", MODEL, "鞄",
  "④ S3 街を歩く", cam("04", 3), sec("04", 3),
  "人の少ない裏側で。顔は主役にしません。"),

 ("11:40〜12:30", "昼休み（店舗の近く）", "―", "",
  "―", "", "50分", "<b>午後も同じ場所に戻ります。移動はありません。</b>"),

 ("band", "午 後　──　四 色 を 一 巡 ず つ　（ 外　→　店 の 扉　→　店 内 ）"),

 ("12:30〜13:05", "けやき並木の歩道　→　店の扉　→　店内", MODEL, "一色目の衣装・鞄",
  "① S1 一色目",
  "1枚目 歩いてくる全身の引き・正面（並木が奥まで抜ける位置）→ 2枚目 同じ位置から腰より上 → "
  "3枚目 扉をまたいで中へ入る → 4枚目 店内を歩く → 5枚目 定位置の立ち姿。", sec("01", 1),
  "<b>店内で一色目に着替え。ここから四回、色を変えます。</b>表情はすまし顔で。"),

 ("13:05〜13:40", "横断歩道（交差点から離れた端）　→　店の扉　→　店内", MODEL, "二色目の衣装・鞄",
  "① S2 二色目",
  "1枚目 道を渡りきるところの引き → 2枚目 腰より上（サングラスを直す）。"
  "扉・店内・定位置は一色目と同じ。", sec("01", 2),
  "<b>ここは笑った表情で。</b>着替え十分。"),

 ("13:40〜14:15", "並木の木ぎわ　→　店の扉　→　店内", MODEL, "三色目の衣装・鞄",
  "① S3 三色目",
  "1枚目 木の後ろを通って歩く引き → 2枚目 腰より上。扉・店内・定位置は同じ。", sec("01", 3),
  "<b>少し急ぎ足の表情で。</b>着替え十分。"),

 ("14:15〜14:50", "店の前　→　店の扉　→　店内", MODEL, "四色目の衣装・鞄",
  "① S4 四色目",
  "1枚目 扉をまたいで中へ入る引き → 2枚目 腰より上（鞄を掛け直して笑う）。店内と定位置も同じ。",
  sec("01", 4), "<b>四色とも同じ立ち位置・同じ画角で撮ります。</b>着替え十分。"),

 ("14:50〜15:00", "店内（定位置）", MODEL, "四色ぶんの衣装・鞄",
  "① S5 巻き戻る", "店内の通路を歩くところを、色ごとに同じ画角で撮り足す。", sec("01", 5),
  "足りないところだけ撮り足して終わります。"
  "<b>四色を並べる最後のカットは、難波さんが帰ったあとに撮ります。</b>"),
]


def esc(s):
    return html.escape(s or "", quote=True)


TD = ("padding:1.15mm 3mm 1.15mm 0;border-bottom:.4pt solid %s;"
      "vertical-align:top;font-size:8.2pt;line-height:1.5" % HAIR)


def rows_html():
    out = []
    for x in ROWS:
        if x[0] == "band":
            out.append(
                '<tr class="band"><td colspan="6" style="background:%s;padding:1.0mm 2.4mm;'
                'border-bottom:.5pt solid %s;font-size:9.4pt;font-weight:700;'
                'letter-spacing:.04em;break-after:avoid;color:%s">%s</td></tr>' % (BAND, LINE, INK, x[1]))
            continue
        tm, place, who, prop, nm, what, sc, memo = x
        pr = ('<div style="color:%s;margin-top:1mm">%s</div>' % (MUTED, esc(prop))) if prop else ""
        body = ('<div style="margin-top:1mm">%s</div>' % what) if what else ""
        out.append(
            '<tr>'
            '<td style="%s;padding-left:0;white-space:nowrap;font-size:9.4pt;font-weight:700;color:%s">%s</td>'
            '<td style="%s;font-weight:700">%s</td>'
            '<td style="%s">%s%s</td>'
            '<td style="%s"><div style="font-weight:700">%s</div>%s</td>'
            '<td style="%s;color:%s;white-space:nowrap">%s</td>'
            '<td style="%s;padding-right:0;color:%s">%s</td></tr>'
            % (TD, GOLD, esc(tm), TD, place, TD, esc(who), pr, TD, nm, body,
               TD, MUTED, esc(sc), TD, MUTED, memo))
    return "".join(out)


def info_html():
    th = ("width:26mm;padding:0.85mm 0;border-bottom:.4pt solid %s;color:%s;"
          "font-size:8.4pt;letter-spacing:.06em;white-space:nowrap;vertical-align:top" % (LINE, FAINT))
    td = ("padding:0.85mm 0;border-bottom:.4pt solid %s;font-size:8.6pt;line-height:1.45;"
          "vertical-align:top" % LINE)
    tel = ('<span style="font-size:11pt;font-weight:700;color:%s">%s</span>'
           '　遅れる・迷った・体調が悪い、いつでもこちらへ。' % (GOLD, TEL))
    pairs = [("タイトル", TITLE, "", ""),
             ("撮影日", "<b>%s</b>　9:00集合" % DAY, "場所", PLACE),
             ("時間", "<b>%s</b>" % SPAN, "出演", "<b>%s</b>（一日）" % MODEL),
             ("雨天予備日", "<b>%s</b>　同じ時間・同じ場所" % RAIN,
              "緊急時連絡先（宮下）", tel)]
    out = []
    for a, b, c, d in pairs:
        if c:
            out.append('<tr><td style="%s">%s</td><td style="%s">%s</td>'
                       '<td style="%s">%s</td><td style="%s">%s</td></tr>'
                       % (th, a, td, b, th, c, td, d))
        else:
            out.append('<tr><td style="%s">%s</td><td style="%s" colspan="3">%s</td></tr>'
                       % (th, a, td, b))
    out.append('<tr><td style="%s">注意事項</td><td style="%s" colspan="3">%s</td></tr>'
               % (th, td, COND))
    return '<table style="width:100%%;border-collapse:collapse;margin:0 0 4mm;' \
           'border-bottom:.8pt solid %s">%s</table>' % (INK, "".join(out))


def build():
    hd = ("text-align:left;font-size:8pt;font-weight:400;color:%s;letter-spacing:.08em;"
          "border-bottom:.6pt solid %s;padding:0 3mm 1.8mm 0" % (FAINT, INK))
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8">
<title>撮影スケジュール　{MODEL}</title>
<style>
@page {{ size: A4 landscape; margin: 10mm 12mm; }}
html {{ color-scheme: light; background: #fff; }}
body {{ margin: 0; background: #fff; color: {INK};
  font-family: 'IPAPGothic','IPAGothic',sans-serif; font-size: 8.2pt; line-height: 1.5;
  -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
tr {{ break-inside: avoid; }}
tr.band, tr.band td {{ break-after: avoid; }}
thead {{ display: table-header-group; }}
b {{ font-weight: 700; }}
</style></head><body>
<div style="border-bottom:1.2pt solid {INK};padding-bottom:2.4mm;margin-bottom:3mm">
  <div style="font-size:7.4pt;font-weight:700;color:{GOLD};letter-spacing:.14em;margin-bottom:1.4mm">
    BROOKLYN MUSEUM ／ 向島工房</div>
  <table style="width:100%;border-collapse:collapse"><tr>
    <td style="font-size:17pt;font-weight:700;white-space:nowrap">撮影スケジュール</td>
    <td style="font-size:9pt;color:{FAINT};padding-left:5mm">Shooting Schedule</td>
    <td style="text-align:right;font-size:10pt;font-weight:700;color:{GOLD};white-space:nowrap">
      {esc(MODEL)}　／　{DAY}　／　{SPAN}</td>
  </tr></table>
</div>
{info_html()}
<table style="width:100%;border-collapse:collapse;table-layout:fixed">
  <colgroup><col style="width:11%"><col style="width:17%"><col style="width:12%">
    <col style="width:32%"><col style="width:6%"><col></colgroup>
  <thead><tr>
    <th style="{hd}">時刻</th><th style="{hd}">場所の詳細</th><th style="{hd}">登場人物</th>
    <th style="{hd}">シーン内容詳細</th><th style="{hd}">尺</th><th style="{hd}">備考</th>
  </tr></thead>
  <tbody>{rows_html()}</tbody>
</table>
</body></html>'''


if __name__ == "__main__":
    out = os.path.join(ROOT, "pdf", "model_schedule.html")
    open(out, "w", encoding="utf-8").write(build())
    print(out, os.path.getsize(out), "バイト")
