# -*- coding: utf-8 -*-
"""香盤表とショットリストを、A4横で流れるPDF用HTMLに書き出す。
   実行: python3 tools/build_shotlist_pdf.py
   中身は build_shotlist_canvas.py / build_script_canvas.py と同じものを読む。
"""
import html, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_script_canvas as S
import build_shotlist_canvas as L

INK, MUTED, FAINT = S.INK, S.MUTED, S.FAINT
GOLD, LINE, BAND = S.GOLD, S.LINE, "#f6f2ec"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def esc(s):
    return html.escape(s or "", quote=True)


def plain(s):
    return re.sub(r"<[^>]+>", "", re.sub(r"<br\s*/?>", " ", s or "")).strip()


def th(w=None):
    return ('text-align:left;font-size:8pt;font-weight:400;color:%s;letter-spacing:.08em;'
            'border-bottom:.6pt solid %s;padding:0 3mm 2mm 0' % (FAINT, INK))


def cover():
    rows = []
    ts = te = 0
    for d in L.DAYS:
        a, b = L.day_counts(d)
        ts += a
        te += b
        books = "".join(
            '<div style="margin-top:1mm"><span style="color:%s;font-weight:700">%s</span>'
            '　<b>%s</b><span style="color:%s">　── %s</span></div>'
            % (GOLD, L.MARU[no], esc(L.PG[no]["jp"]), MUTED, tx) for no, tx in d["toc"])
        rows.append(
            '<tr>'
            '<td class="c" style="color:%s;font-weight:700">%s</td><td class="c"><b>%s</b></td><td class="c">%s</td>'
            '<td class="c" style="color:%s;font-weight:700;white-space:nowrap">%s</td>'
            '<td class="c" style="white-space:nowrap">%dカット</td></tr>'
            % (GOLD, esc(d["date"]), esc(d["place"]), books, GOLD,
               esc(L.day_span(d)), a))
    return f'''<section class="page">
  <div class="head">
    <div class="eyebrow">BROOKLYN MUSEUM ／ 向島工房</div>
    <div class="titlerow">
      <div class="title">動画八本　香盤表とショットリスト</div>
      <div class="sub">Shooting Schedule &amp; Shot List</div>
      <div class="right">全八本　{ts + te}カット　／　撮影 四日</div>
    </div>
  </div>
  <p class="lead">
    はじめの二日で短い二本（②③）を撮り、編集まで一度通します。<b>三日目に三人のインタビューを全部録り、四日目からは、録れた声に画を当てていきます。</b>
    声が先にあると、どの画を何秒使うかが決まるので、撮る量に無駄が出ません。出演者の手配が要る⑧⑦④①は、支度の重い順に、あとの四日へ置いています。<br>
    {ts}カットを撮影し、残りの{te}カット（白バックと文字だけの画面）は編集で作ります。日ごとの香盤表のあとに、<b>本ごとのショットリスト</b>を八枚付けています。
  </p>
  <table>
    <colgroup><col style="width:7%"><col style="width:16%"><col><col style="width:10%"><col style="width:7%"></colgroup>
    <thead><tr><th style="{th()}">日付</th><th style="{th()}">場所</th><th style="{th()}">内容</th>
    <th style="{th()}">時間</th><th style="{th()}">カット</th></tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
  <div class="two">
    <div><div class="cap">先に決めておくこと</div>
      <b>佐藤さんに確認する二つ</b>── ブルックリンの製作日（工房の日が決まる）と、終業後に工房を使えるか（③の日が決まる）。<br>
      <b>インタビューの日</b>── 永尾社長・佐藤さんの予定。工房が動いていない日でも撮れる。<br>
      <b>店の日</b>── くさがやさんの予定、⑦で鞄に物を入れて持ち出す方、購入者と顔出しの範囲。<br>
      <b>モデルの日</b>── 出演者と、衣装・鞄 四色ぶん。会場の撮影申請。<br>
      ④は曇りの日に合わせるので、モデルの日の前後に予備日を一日置く。</div>
    <div>
  </div>
</section>'''


def day_page(d):
    shoot, edit = L.day_counts(d)
    rows = []
    head = ("時刻", "話す人 ／ 本・シーン", "場所（セット）", "録ること ／ 画角の並び", "気をつけること")
    if d.get("talks"):
        rows.append('<tr><td colspan="5" style="padding:2mm 0 1mm"><b>イ ン タ ビ ュ ー の 収 録</b></td></tr>')
        for tk in d["talks"]:
            when, who, place, what, note = tk[:5]
            rows.append('<tr><td class="c" style="color:%s;font-weight:700;white-space:nowrap">%s</td>'
                        '<td class="c"><b style="font-size:11pt">%s</b></td>'
                        '<td class="c">%s</td><td class="c">%s</td>'
                        '<td class="c" style="color:%s">%s</td></tr>'
                        % (GOLD, esc(when), esc(who), place, what, MUTED, note))
        rows.append('<tr><td colspan="5" style="padding:4mm 0 1mm"><b>セ ッ ト ご と の 撮 影</b></td></tr>')
    for when, place, sc, note in d.get("setups", []):
        books = "　".join(
            L.MARU[no] + " " + "・".join(re.sub(r"^S\\d+\\s*", "", L.cuts_of(no, si)[0])
                                        for n2, si in sc if n2 == no)
            for no in dict.fromkeys(n for n, _ in sc))
        rows.append('<tr class="band"><td colspan="5"><span style="color:%s;font-weight:700">%s</span>'
                    '　<b>%s</b>　<span style="color:%s">%s</span>'
                    '<span style="float:right;color:%s">%s</span></td></tr>'
                    % (GOLD, esc(when), esc(place), MUTED, books, MUTED, note))
        for no, si in sc:
            nm, cuts = L.cuts_of(no, si)
            pl_, _, _, wh = S.SPOT[no][si]
            cam, cnote = L.split_cam(S.D[no][si][0])
            mv, mvday = L.MOVED.get((no, si), ([], ""))
            if mv and len(mv) == len(cuts):
                cnt = "%dカット<br><span style='color:%s'>インタビューの収録で撮る</span>" % (len(cuts), GOLD)
            else:
                cnt = "%dカット" % (len(cuts) - len(mv))
                if mv:
                    cnt += '<br><span style="color:%s">%sは%s</span>' % (
                        GOLD, "".join(L.CIR[k - 1] for k in mv), mvday)
            if (no, si) in L.REUSE:
                tc = '<span style="color:%s">撮影しない<br>%s</span>' % (GOLD, L.REUSE[(no, si)])
            elif L.is_edit_only(no, si):
                tc = '<span style="color:%s">撮影しない</span>' % FAINT
            else:
                tc = '<span style="color:%s;font-weight:700">%s</span>' % (GOLD, esc(wh))
            rows.append('<tr><td class="c" style="white-space:nowrap">%s</td>'
                        '<td class="c"><b><span style="color:%s">%s</span> %s</b><br>'
                        '<span style="color:%s;font-size:8.5pt">%s</span></td>'
                        '<td class="c">%s</td><td class="c">%s</td>'
                        '<td class="c" style="color:%s">%s</td></tr>'
                        % (tc, GOLD, L.MARU[no], esc(nm), FAINT, cnt,
                           pl_ if pl_ != "同じ" else '<span style="color:%s">同じ</span>' % MUTED,
                           cam, MUTED, cnote))
    keys = "".join("<li>%s</li>" % k for k in d["keys"])
    return f'''<section class="page">
  <div class="head">
    <div class="titlerow">
      <div class="title" style="font-size:20pt">{esc(d["no"])}</div>
      <div class="sub" style="color:{GOLD};font-size:13pt;font-weight:700">{esc(d["place"])}</div>
      <div class="sub">{esc(d["theme"])}</div>
      <div class="right">{esc(L.day_span(d))}　／　撮るカット {shoot}{"（ほかに編集で作る %d）" % edit if edit else ""}</div>
    </div>
  </div>
  <p class="lead" style="color:{GOLD}">{d["cond"]}</p>
  <table>
    <colgroup><col style="width:10%"><col style="width:14%"><col style="width:20%"><col style="width:30%"><col></colgroup>
    <thead><tr>{"".join('<th style="%s">%s</th>' % (th(), h) for h in head)}</tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
  <div class="two">
    <div><div class="cap">持ち物</div>{d["gear"]}</div>
    <div><div class="cap">この日の要点</div><ul>{keys}</ul></div>
  </div>
</section>'''


def shot_page(no):
    pg = L.PG[no]
    rows, n = [], 0
    for si in range(1, len(pg["rows"]) + 1):
        nm, tm, shots = pg["rows"][si - 1]
        cuts = [sh for sh in shots if sh[1] != "―"]
        ang = L.shot_angles(no, si)
        place, _, day, when = S.SPOT[no][si]
        sp = L.sec_span(tm)
        each = (sp[1] - sp[0]) / len(cuts) if sp and cuts else None
        mv, mvday = L.MOVED.get((no, si), ([], ""))
        rows.append('<tr class="band"><td colspan="5"><b>%s</b>　<span style="color:%s">%s　%s</span>'
                    '<span style="float:right;color:%s;font-weight:700">%s　%s</span></td></tr>'
                    % (esc(nm), MUTED, esc(re.sub(r"　｜.*", "", tm)),
                       esc(place if place != "同じ" else "同じ場所"), GOLD, esc(day), esc(when)))
        for k, sh in enumerate(cuts):
            n += 1
            sec = "%.1f〜%.1f秒" % (sp[0] + each * k, sp[0] + each * (k + 1)) if each else ""
            tag = ('<br><span style="color:%s">%sに撮影</span>' % (GOLD, mvday)) if k + 1 in mv else ""
            if (no, si) in L.REUSE:
                tag = '<br><span style="color:%s">撮影しない ── %s</span>' % (GOLD, L.REUSE[(no, si)])
            rows.append('<tr><td class="c" style="white-space:nowrap"><b>%02d</b>'
                        '<span style="color:%s">　S%d-%s</span></td>'
                        '<td class="c">%s%s</td><td class="c">%s</td>'
                        '<td class="c" style="color:%s;white-space:nowrap">%s</td>'
                        '<td class="c"><span class="box"></span></td></tr>'
                        % (n, FAINT, si, L.CIR[k], ang[k] if k < len(ang) else "", tag,
                           sh[1], MUTED, sec))
    return f'''<section class="page">
  <div class="head">
    <div class="titlerow">
      <div class="title" style="font-size:19pt;color:{GOLD}">{L.MARU[no]}</div>
      <div class="title" style="font-size:19pt">{esc(pg["jp"])}</div>
      <div class="sub">{esc(pg["en"])}　{esc(plain(pg["meta_len"]))}</div>
      <div class="right">ショットリスト　全{n}カット</div>
    </div>
  </div>
  <table>
    <colgroup><col style="width:9%"><col style="width:24%"><col><col style="width:10%"><col style="width:4%"></colgroup>
    <thead><tr><th style="{th()}">№　／　カット</th><th style="{th()}">画角</th>
    <th style="{th()}">撮るもの</th><th style="{th()}">尺の目安</th><th style="{th()}">済</th></tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
</section>'''


def cast_page():
    rows = []
    for maru, no, day, face, prep, cloth, other in L.CAST:
        name = L.PG[no]["jp"] if no else "永尾社長・佐藤さん・くさがやさん"
        rows.append('<tr><td class="c"><b style="color:%s;font-size:13pt">%s</b><br><b>%s</b><br>'
                    '<span style="color:%s;font-size:8.5pt">%s</span></td>'
                    '<td class="c">%s</td><td class="c">%s</td><td class="c">%s</td>'
                    '<td class="c" style="color:%s">%s</td></tr>'
                    % (GOLD, maru, esc(name), FAINT, esc(day), esc(face), prep, cloth, MUTED, other))
    return f'''<section class="page">
  <div class="head">
    <div class="titlerow">
      <div class="title" style="font-size:20pt">出演者と支度</div>
      <div class="sub">Cast &amp; Preparation</div>
      <div class="right">ヘアメイクは付けない</div>
    </div>
  </div>
  <p class="lead">ヘアメイクは付けません。当日の支度は、鏡・テカリ止めのパウダー・爪の手入れだけです。
  顔が寄りで映るのは①と⑧の二本だけで、ほかは顔を主役にしないか、まったく映しません。</p>
  <table>
    <colgroup><col style="width:16%"><col style="width:15%"><col style="width:23%"><col style="width:23%"><col></colgroup>
    <thead><tr><th style="{th()}">本　／　撮影日</th><th style="{th()}">顔が映るか</th>
    <th style="{th()}">当日の支度</th><th style="{th()}">衣装</th><th style="{th()}">そのほか</th></tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
  <div class="two"><div><div class="cap">全員に共通すること</div>
    出演承諾書を、①④⑦⑧の出演者全員からいただく ── 使う範囲（Instagram・EC商品ページ・展示会）、期間、媒体を書いたもの。<br>
    交通費と拘束時間を、依頼するときに先に伝える。<br>
    体調不良に備えて、①と④は予備日を一日置く。</div></div>
</section>'''


CSS = f'''
@page {{ size: A4 landscape; margin: 11mm 12mm 12mm 12mm; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: 'IPAPGothic','IPAGothic',sans-serif; color: {INK};
        font-size: 9pt; line-height: 1.6; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
.page {{ break-after: page; }}
.page:last-child {{ break-after: auto; }}
.head {{ border-bottom: 1.2pt solid {INK}; padding-bottom: 3mm; margin-bottom: 4mm; }}
.eyebrow {{ font-size: 8pt; font-weight: 700; color: {GOLD}; letter-spacing: .14em; margin-bottom: 2mm; }}
.titlerow {{ display: flex; align-items: baseline; gap: 5mm; }}
.title {{ font-size: 22pt; font-weight: 700; }}
.sub {{ font-size: 10pt; color: {FAINT}; }}
.right {{ margin-left: auto; font-size: 10pt; font-weight: 700; }}
.lead {{ margin: 0 0 4mm; font-size: 9pt; line-height: 1.75; color: {MUTED}; }}
table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
thead {{ display: table-header-group; }}
tr {{ break-inside: avoid; }}
td.c {{ padding: 2mm 3mm 2mm 0; border-bottom: .5pt solid {LINE}; vertical-align: top;
        word-wrap: break-word; }}
tr.band td {{ background: {BAND}; padding: 1.6mm 2mm; border-bottom: .5pt solid {LINE}; font-size: 9.5pt; }}
.two {{ display: flex; gap: 10mm; margin-top: 5mm; padding-top: 3.5mm; border-top: .5pt solid {LINE};
        font-size: 8.5pt; line-height: 1.7; break-inside: avoid; }}
.two > div {{ flex: 1; }}
.cap {{ font-size: 8pt; color: {FAINT}; letter-spacing: .08em; margin-bottom: 1.5mm; }}
ul {{ margin: 0; padding-left: 4mm; }}
li {{ margin-bottom: 1mm; }}
.box {{ display: inline-block; width: 3.5mm; height: 3.5mm; border: .5pt solid {LINE}; border-radius: .5mm; }}
b {{ font-weight: 700; }}
'''


def main():
    parts = [cover()] + [day_page(d) for d in L.DAYS] + \
            [shot_page(no) for no in L.SHOT_ORDER] + [cast_page()]
    out = ('<!doctype html><html lang="ja"><head><meta charset="utf-8">'
           '<title>動画八本 香盤表とショットリスト</title><style>%s</style></head><body>%s</body></html>'
           % (CSS, "".join(parts)))
    p = os.path.join(ROOT, "pdf", "kouban.html")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(out)
    print(p, len(parts), "ページぶん")


if __name__ == "__main__":
    main()
