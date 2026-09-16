# -*- coding: utf-8 -*-
"""モデル渡し用の香盤表（①④⑤だけ）を、A4横のPDF用HTMLに書き出す。
   実行: python3 tools/build_model_kouban.py
   本編用の香盤表（build_shotlist_pdf.py）とは別物。
   出演者に渡す紙なので、カット番号や機材の話は入れない。
"""
import html, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
INK, PROSE, MUTED, FAINT = "#15191c", "#3d4448", "#5b6266", "#8a8f92"
GOLD, LINE, HAIR, BAND = "#a8672a", "#ddd7cd", "#ebe6dd", "#f4efe7"

MODEL = "難 波 遥　さん"
TEL = "090-1748-0280"
DAY = "10月13日（火）"
RAIN = "10月14日（水）"
HOURS = "9:00 〜 15:00 前後"

# (時刻, 場所, 本, 撮るもの, 衣装)
ROWS = [
 ("band", "表 参 道 　── 　店 舗 と 街"),
 ("9:00〜9:30", "BROOKLYN MUSEUM 表参道店", "",
  "集合・支度。着替えて、髪を整えます。",
  "④の一そろいに着替え"),
 ("9:30〜10:10", "店内 ・ レジまわり", "⑤",
  "<b>買う人の役。</b>店の人から鞄を受け取って、笑顔で見送られる。そのあと、使っている手元。"
  "<span class='sm'>顔が映ります。セリフはありません。</span>",
  "④と同じ一そろいのまま"),
 ("10:25〜11:00", "けやき並木の歩道（柵のあるところ）", "④",
  "<span class='sm'>店舗から歩いて数分です。</span><br>"
  "<b>鞄を柵に掛けて立つ。</b>カメラは止めたまま、背景の街だけが動きます。"
  "同じ場所で、立ち止まって終わるカットも撮ります。",
  "同じ"),
 ("11:00〜11:30", "ベンチか石段", "④",
  "<b>真上から。</b>鞄の口を開けて、中身を整える手。<b>手が寄りで映ります。</b>",
  "同じ"),
 ("11:30〜11:55", "並木の裏の路地", "④",
  "<b>歩く。</b>引きで一回、肩の鞄に寄って一回。最後に鞄と持ち物・靴を並べて置きます。",
  "同じ"),

 ("11:55〜12:55", "ラ ン チ 　／ 　表 参 道 　→ 　有 楽 町 へ 移 動", "",
  "そのまま東京国際フォーラムへ。<span class='sm'>地下鉄で二十分ほど。</span>", "―"),

 ("band", "東 京 国 際 フ ォ ー ラ ム 　── 　四 色 を 一 巡 ず つ"),
 ("12:55〜13:35", "フォーラム付近の並木 　→ 　廊下 　→ 　ベンチ", "①",
  "<span class='sm'>着いたら一色目に着替え。ここから四回、色を変えます。</span><br>"
  "<b>歩いてくる全身の引き</b>と、腰から上の寄り。表情はすまし顔。<br>"
  "そのまま建物に入って、<b>廊下を歩くところ</b>と、<b>ベンチで立ち姿を一枚</b>。",
  "<b>一色目</b>"),
 ("13:35〜14:00", "横断歩道 　→ 　廊下 　→ 　ベンチ", "①",
  "<b>道を渡りきるところ。</b>寄りではサングラスを直します。<b>ここは笑った表情で。</b>"
  "そのあと、廊下とベンチを同じように。",
  "<b>二色目</b>　<span class='sm'>着替え十分</span>"),
 ("14:00〜14:25", "渡った先のけやきぎわ 　→ 　廊下 　→ 　ベンチ", "①",
  "<b>木の後ろを通って歩く。</b>少し急ぎ足の表情で。<br>そのあと、廊下とベンチ。",
  "<b>三色目</b>　<span class='sm'>着替え十分</span>"),
 ("14:25〜15:05", "ガラス棟の扉 　→ 　廊下 　→ 　ベンチ", "①",
  "<b>扉をまたいで中へ入る。</b>寄りでは肩の鞄を掛け直して笑う。そのあと、廊下とベンチ。"
  "<span class='sm'>最後に撮り足して終わります。</span>",
  "<b>四色目</b>　<span class='sm'>着替え十分</span>"),
]

SHITAKU = [
 ("持ってくるもの",
  "<b>衣装は五そろい。</b>①の四色ぶんと、④の一そろい。<br>"
  "④の一そろいは、そのまま⑤（店舗）でも着ます。"),
 ("①の四色",
  "<b>鞄の色と喧嘩しない服。</b>四色それぞれ、色がはっきり違うものを。<br>"
  "<b>前開きの上着だと、着替えで髪が乱れません。</b>"),
 ("④の一そろい",
  "街に馴染む色。<b>ベージュや白、グレーなど。</b>"),
 ("靴",
  "<b>履き慣れたもの。</b>歩く距離があります。"
  "④の最後に、鞄と一緒に並べて撮ります。"),
 ("手元",
  "<b>爪を切りそろえてください。</b>④で手が寄りで映ります。<br>時計と指輪は外します。"),
 ("髪・メイク",
  "<b>ヘアメイクは付きません。</b>ふだんどおりで大丈夫です。<br>鏡はこちらで用意します。"),
 ("荷物",
  "着替え場所と荷物置き場は、こちらで用意します。"),
]

CHUI = [
 "<b>①も④も、映るのは難波さん一人です。</b>ほかの出演者と一緒に映る場面はありません。",
 "<b>⑤（店舗）だけ、店の人と二人で映ります。</b>鞄を受け取って、見送られるところ。セリフはありません。",
 "<b>①は四色を一巡ずつ撮ります。</b>一つの色で、外を歩く → 廊下 → ベンチまで通して撮ってから、次の色に着替えます。"
 "<b>行ったり来たりしないので、着替えは四回で済みます。</b>",
 "<b>雨のときは、10月14日（水）に振り替えます。</b>前日の夕方までにご連絡します。",
 "撮影中に困ったこと・体調のことは、その場でいつでも言ってください。<b>何度でも撮り直せます。</b>",
]

CSS = f'''
@page {{ size: A4 landscape; margin: 10mm 12mm; }}
* {{ box-sizing: border-box; }}
html {{ color-scheme: light; background: #fff; }}
body {{ margin: 0; background: #fff; font-family: 'IPAPGothic','IPAGothic',sans-serif;
  color: {INK}; font-size: 7.9pt; line-height: 1.4;
  -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
.head {{ border-bottom: 1.2pt solid {INK}; padding-bottom: 2.2mm; margin-bottom: 2.4mm; }}
.eyebrow {{ font-size: 7.4pt; font-weight: 700; color: {GOLD}; letter-spacing: .14em; margin-bottom: 1.4mm; }}
.titlerow {{ display: flex; align-items: baseline; gap: 5mm; }}
.title {{ font-size: 17pt; font-weight: 700; letter-spacing: -.01em; }}
.sub {{ font-size: 9pt; color: {FAINT}; }}
.right {{ margin-left: auto; font-size: 11pt; font-weight: 700; color: {GOLD}; }}

.dhead {{ width: 100%; border-collapse: collapse; margin: 0 0 2.6mm;
  border-bottom: .8pt solid {INK}; }}
.dhead td {{ padding: 0.7mm 0; border-bottom: .4pt solid {LINE}; vertical-align: top;
  font-size: 8.4pt; line-height: 1.45; }}
.dhead td:nth-child(odd) {{ width: 28mm; color: {FAINT}; font-size: 8.4pt;
  letter-spacing: .06em; white-space: nowrap; }}
.tel {{ font-size: 11pt; font-weight: 700; color: {GOLD}; letter-spacing: .04em; }}

table.main {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
thead {{ display: table-header-group; }}
tr {{ break-inside: avoid; }}
th {{ text-align: left; font-size: 8pt; font-weight: 400; color: {FAINT};
  letter-spacing: .08em; border-bottom: .6pt solid {INK}; padding: 0 3mm 1.6mm 0; }}
td {{ padding: 0.55mm 3mm 0.55mm 0; border-bottom: .4pt solid {HAIR};
  vertical-align: top; word-wrap: break-word; }}
tr.band td {{ background: {BAND}; padding: 0.7mm 2.4mm; border-bottom: .5pt solid {LINE};
  font-size: 9.4pt; font-weight: 700; letter-spacing: .04em; break-after: avoid; }}
.tm {{ color: {GOLD}; font-weight: 700; white-space: nowrap; font-size: 9.2pt; }}
.pl {{ font-weight: 700; }}
.no {{ font-weight: 700; color: {GOLD}; font-size: 11pt; }}
.sm {{ font-size: 8pt; color: {FAINT}; }}
.dim {{ color: {MUTED}; }}

.chui {{ margin: 0 0 2.2mm; padding-bottom: 2mm; border-bottom: .8pt solid {INK}; }}
.chui .cap {{ display: block; }}
.two {{ display: flex; gap: 9mm; margin-top: 2.6mm; padding-top: 2.2mm;
  border-top: .8pt solid {INK}; break-inside: avoid; }}
.two > div {{ flex: 1; }}
.cap {{ font-size: 8pt; color: {FAINT}; letter-spacing: .1em; margin-bottom: 2.2mm; }}
.st {{ display: flex; gap: 3mm; margin-bottom: 1.6mm; font-size: 8.8pt; line-height: 1.55; }}
.st b.k {{ flex: 0 0 22mm; color: {GOLD}; font-weight: 700; }}
ul {{ margin: 0; padding-left: 4.4mm; font-size: 8.4pt; line-height: 1.55; }}
ul.two-col {{ column-count: 2; column-gap: 9mm; }}
ul.two-col li {{ break-inside: avoid; }}
li {{ margin-bottom: 1mm; }}
b {{ font-weight: 700; }}
.page2 {{ break-before: page; }}
.p2head {{ display: flex; align-items: baseline; gap: 5mm;
  border-bottom: 1.2pt solid {INK}; padding-bottom: 2.4mm; margin-bottom: 3.4mm; }}
.p2title {{ font-size: 17pt; font-weight: 700; letter-spacing: -.01em; }}
.p2sub {{ font-size: 8.6pt; color: {FAINT}; }}
.p2r {{ margin-left: auto; font-size: 9pt; font-weight: 700; color: {GOLD}; }}
.cols {{ display: flex; gap: 8mm; }}
.cols > div {{ flex: 1; }}
.vhead {{ display: flex; align-items: baseline; gap: 3mm;
  border-bottom: .8pt solid {INK}; padding-bottom: 1.6mm; margin-bottom: 2.4mm; }}
.vno {{ font-size: 15pt; font-weight: 700; color: {GOLD}; }}
.vname {{ font-size: 10.5pt; font-weight: 700; }}
.vtag {{ margin-left: auto; font-size: 8pt; color: {MUTED}; }}
.lede {{ font-size: 8.6pt; line-height: 1.55; color: {PROSE}; margin: 0 0 2.2mm; }}
table.sty {{ width: 100%; border-collapse: collapse; table-layout: fixed;
  margin-bottom: 2mm; }}
table.sty td {{ padding: 0.85mm 2.6mm 0.85mm 0; border-bottom: .4pt solid {HAIR};
  vertical-align: top; font-size: 8.6pt; line-height: 1.5; }}
table.sty td.k {{ width: 21mm; color: {GOLD}; font-weight: 700; font-size: 8.4pt; }}
.sub2 {{ font-size: 8pt; color: {FAINT}; letter-spacing: .1em; margin: 2.2mm 0 1.4mm;
  padding-top: 1.8mm; border-top: .5pt solid {LINE}; }}
.ng {{ background: {BAND}; padding: 1.8mm 2.6mm; font-size: 8.2pt; line-height: 1.5;
  border-left: 1.4pt solid {GOLD}; margin-top: 2mm; break-inside: avoid; }}
'''


# ══ 2枚目 ── 服装と佇まい ═══════════════════════════════════════
# (見出し, 中身)
STY01 = [
 ("考え方",
  "<b>色で語るのは鞄だけ。服は引く。</b>二十秒で四回色が変わるので、"
  "服と鞄の両方が主張すると、何が変わったのか分からなくなります。"),
 ("トップス",
  "<b>無地。無彩色か、くすんだ一色。</b>白（オフホワイト）／ グレー ／ ベージュ ／ "
  "チャコールの四色で組むと、どの色の鞄も立ちます。<br>"
  "<b>前開きの上着</b>（シャツ・カーディガン・ジャケット）。着替えで髪が乱れません。"),
 ("ボトムス",
  "<b>四色とも同じものを穿きっぱなし。</b>黒か濃紺のストレートパンツ、"
  "またはくるぶし丈のスカート。<br>"
  "<span class='sm'>下を固定すると、上と鞄の色だけが変わって見えます。着替えも上だけで済むので、四回が二、三分ずつで終わります。</span>"),
 ("靴",
  "<b>四色とも同じ。</b>歩くので履き慣れたもの。革のローファーかショートブーツ。"),
 ("素材",
  "コットン ／ ウール ／ リネン。<b>テカらないもの。</b>"
  "光沢のある生地は、屋外で白く飛びます。"),
 ("小物",
  "サングラスを一つ（二色目で掛け直します）。<br>"
  "時計・指輪は外します。揺れる長いアクセサリーも外してください。"),
]

POSE01 = [
 ("一色目", "<b>すまし顔。</b>口角は上げない。顎を引かず、まっすぐ前を見て歩く。"),
 ("二色目", "<b>笑う。</b>サングラスを直しながら。歯は見せすぎない。"),
 ("三色目", "<b>少し急ぎ足。</b>歩幅を広く、視線は遠くへ。"),
 ("四色目", "<b>肩の鞄を掛け直して笑う。</b>一度手元に視線を落としてから、前へ戻す。"),
 ("四色に共通",
  "<b>歩く速さを四色とも同じに。</b>速さが変わると、色の切り替わりが成立しません。<br>"
  "<b>鞄は必ず同じ側の肩に。</b>カメラは見ません。"),
]

STY04 = [
 ("考え方",
  "<b>主役はブラウンの鞄。服は鞄より明るく。</b>"
  "暗い服だと、表参道の日中でも鞄が沈みます。"),
 ("色",
  "<b>三色まで。</b>ベージュ ／ グレージュ ／ 白 ／ チャコールの中から。<br>"
  "<b>鞄と同じブラウンは着ない。</b>鞄が服に溶けます。"),
 ("シルエット",
  "<b>ロング丈の上着かコート。</b>歩く画で裾が揺れると、それだけで画が動きます。<br>"
  "ボトムスは細すぎないストレート。真俯瞰で鞄の横に立つので、形が出るもの。"),
 ("靴",
  "<b>革のローファーかショートブーツ。</b>スニーカーだと大人っぽさが出ません。<br>"
  "<span class='sm'>最後に鞄・持ち物と並べて置き画にするので、汚れを落としておいてください。</span>"),
 ("素材",
  "ウール ／ コットン ／ リネン。<b>マットな質感で。</b>"
  "参考動画から起こした絵コンテも、光らない生地で成立しています。"),
 ("この服のまま",
  "<b>⑤（店舗）も同じ服で撮ります。</b>着替えは午後の四色ぶんだけです。"),
]

POSE04 = [
 ("顔", "<b>主役にしない。</b>引きが多く、カメラに視線は向けません。"),
 ("立ち姿", "<b>片足に重心。</b>まっすぐ立つと固く見えます。"),
 ("歩く", "<b>ふだんより少しゆっくり。</b>歩幅は広く、速くない。"),
 ("表情", "<b>笑わない。無表情でもない。</b>何かを考えている顔で。"),
 ("手", "鞄を持たない側の手は自然に下ろす。ポケットに入れてもかまいません。"),
 ("手元の寄り",
  "<b>動きをゆっくり。</b>真俯瞰で中身を整えるところは、ふだんの速さだと速すぎます。"),
]

NAKAMI = [
 "ノートPC（十三インチ）か、A4のファイル　── <b>これが入ることを見せたい</b>",
 "長財布　／　折りたたみ傘　／　水筒（五百ミリリットル）",
 "文庫本か手帳　／　鍵とイヤホンの小物ポーチ",
]

NG04 = ("<b>中身は色をそろえてください。</b>ベージュ・黒・こげ茶あたりで。"
        "真俯瞰で一度に映るので、色がばらばらだと散らかって見えます。<br>"
        "<b>出す順番も決めておいてください。</b>一度だけ撮るので、迷うと手が止まります。")

NG01 = ("<b>①で避けるもの</b>　── 柄物、大きいロゴ、光沢のある生地、"
        "フリンジや揺れる飾り、鞄と同じ色の服。<br>"
        "二十秒で四回変わる画なので、柄が入ると目が散って、鞄の色が読めなくなります。")


def sty_table(rows):
    return '<table class="sty">%s</table>' % "".join(
        '<tr><td class="k">%s</td><td>%s</td></tr>' % (a, b) for a, b in rows)


def style_page():
    return f"""<div class="page2">
<div class="p2head">
  <div class="p2title">服 装 と 佇 ま い</div>
  <div class="p2sub">Styling &amp; Direction</div>
  <div class="p2r">{MODEL}</div>
</div>

<div class="cols">
  <div>
    <div class="vhead"><span class="vno">&#9312;</span>
      <span class="vname">服装ごとに画が変わる</span>
      <span class="vtag">三十五秒　／　四色を着替える</span></div>
    <p class="lede"><b>鞄が差し色です。</b>四色の鞄が主役で、服はその台になります。</p>
    {sty_table(STY01)}
    <div class="sub2">佇 ま い と 表 情</div>
    {sty_table(POSE01)}
    <div class="ng">{NG01}</div>
  </div>

  <div>
    <div class="vhead"><span class="vno">&#9315;</span>
      <span class="vname">鞄を持って街を歩く</span>
      <span class="vtag">三十秒　／　一そろい</span></div>
    <p class="lede"><b>街に馴染む色で、大人っぽく。</b>
    ブラウンの大きめの鞄を、毎日使っている人に見えるように。</p>
    {sty_table(STY04)}
    <div class="sub2">佇 ま い と 表 情</div>
    {sty_table(POSE04)}
    <div class="sub2">鞄 に 入 れ る も の 　── 　中 身 を 見 せ ま す</div>
    <ul>{"".join("<li>%s</li>" % x for x in NAKAMI)}</ul>
    <div class="ng">{NG04}</div>
  </div>
</div>
</div>"""


def esc(s):
    return html.escape(s or "", quote=True)


def build():
    rows = []
    for r in ROWS:
        if r[0] == "band":
            rows.append('<tr class="band"><td colspan="5">%s</td></tr>' % r[1])
            continue
        tm, place, no, what, cloth = r
        rows.append(
            '<tr><td class="tm">%s</td><td class="pl">%s</td><td class="no">%s</td>'
            '<td>%s</td><td class="dim">%s</td></tr>' % (tm, place, no, what, cloth))
    st = "".join('<div class="st"><b class="k">%s</b><div>%s</div></div>' % (a, b)
                 for a, b in SHITAKU)
    ch = "".join("<li>%s</li>" % x for x in CHUI)
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8">
<title>香盤表　モデル用</title>
<style>{CSS}</style></head><body>
<div class="head">
  <div class="eyebrow">BROOKLYN MUSEUM ／ 向島工房</div>
  <div class="titlerow">
    <div class="title">撮影スケジュール</div>
    <div class="sub">Shooting Schedule</div>
    <div class="right">{MODEL}</div>
  </div>
</div>

<table class="dhead">
  <tr><td>撮 影 日</td><td><b>{DAY}</b>　{HOURS}</td>
      <td>雨 天 予 備 日</td><td><b>{RAIN}</b>　同じ時間</td></tr>
  <tr><td>場 所</td>
      <td colspan="3"><b>午前</b>　BROOKLYN MUSEUM 表参道店 ・ 表参道けやき並木　／
        <b>午後</b>　東京国際フォーラム（有楽町）</td></tr>
  <tr><td>撮 る 動 画</td>
      <td colspan="3">
        <span class="no">①</span> 服装ごとに画が変わる　／
        <span class="no">④</span> 鞄を持って街を歩く　／
        <span class="no">⑤</span> コーポレートムービー（店舗の場面だけ）</td></tr>
  <tr><td>緊 急 時 連 絡 先</td>
      <td colspan="3"><span class="tel">{TEL}</span>
        　<span class="sm">遅れる・迷った・体調が悪い、いつでもこちらへ。</span></td></tr>
</table>

<div class="chui"><span class="cap">当 日 の こ と</span>
  <ul class="two-col">{ch}</ul></div>

<table class="main">
  <colgroup><col style="width:11%"><col style="width:22%"><col style="width:4%">
    <col><col style="width:16%"></colgroup>
  <thead><tr><th>時 刻</th><th>場 所</th><th></th><th>す る こ と</th><th>衣 装</th></tr></thead>
  <tbody>{"".join(rows)}</tbody>
</table>

{style_page()}
</body></html>'''


if __name__ == "__main__":
    out = os.path.join(ROOT, "pdf", "model_kouban.html")
    open(out, "w", encoding="utf-8").write(build())
    print(out, os.path.getsize(out), "バイト")
