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
            % (GOLD, esc(d["date"].split("　※")[0]), esc(d["place"]), books, GOLD,
               esc(L.day_span(d)), a))
    return f'''<section class="page">
  <div class="head">
    <div class="eyebrow">BROOKLYN MUSEUM ／ 向島工房</div>
    <div class="titlerow">
      <div class="title">動画八本　香盤表</div>
      <div class="sub">Shooting Schedule</div>
      <div class="right">全八本　{ts}カット　／　撮影 四日　／　日付はすべて仮</div>
    </div>
  </div>
  <p class="lead">
    四日で八本ぶんを撮ります。同じ場所・同じ設営で撮れるものをまとめ、時刻の順に並べています。
    <b>⑧は開店前、③は終業後か休日。②と⑥は、ブルックリンの品を作っている日に合わせて動かします。</b>
  </p>
  <table>
    <colgroup><col style="width:7%"><col style="width:16%"><col><col style="width:10%"><col style="width:7%"></colgroup>
    <thead><tr><th style="{th()}">日付</th><th style="{th()}">場所</th><th style="{th()}">内容</th>
    <th style="{th()}">時間</th><th style="{th()}">カット</th></tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
  <div class="two">
    <div><div class="cap">先に決めておくこと</div>
      <b>佐藤さんに確認する二つ</b>── ブルックリンの製作日（工房で撮る日が決まる）と、終業後か休日に工房を使えるか（③の日が決まる）。<br>
      <b>インタビュー</b>── 永尾社長・くさがやさんは10月1日、佐藤さんは10月5日。三人とも三十分ずつ。<br>
      <b>10月1日（木）</b>── くさがやさんの予定、⑦で鞄に物を入れて持ち出す方、購入者と顔出しの範囲。<br>
      <b>10月2日（金）</b>── 出演者と、衣装・鞄 四色ぶん。会場の撮影申請。<br>
      ④は曇りの日に合わせるので、10月2日の前後に予備日を一日置く。</div>
    <div>
  </div>
</section>'''


def day_page(d):
    shoot, edit = L.day_counts(d)
    blocks = []
    head = ("時刻", "場所の詳細", "登場人物", "シーン内容詳細", "尺", "備考")
    for tk in d.get("talks", []):
        when, who, place, what, note = tk[:5]
        blocks.append((L.start_min(when),
            '<tr><td class="c" style="color:%s;font-weight:700;white-space:nowrap">%s</td>'
            '<td class="c">%s</td><td class="c">%s<br><span style="color:%s">椅子、ピンマイク</span></td>'
            '<td class="c"><b>%s</b><br>%s</td>'
            '<td class="c" style="color:%s;white-space:nowrap">三十分</td>'
            '<td class="c" style="color:%s">%s</td></tr>'
            % (GOLD, esc(when), place, esc(who), MUTED,
               esc(tk[6] if len(tk) > 6 else "インタビュー"), what, MUTED, MUTED, note)))
    for when, place, sc, note in d.get("setups", []):
        if not sc:
            a, b = [int(x.split(":")[0]) * 60 + int(x.split(":")[1]) for x in when.split("〜")]
            blocks.append((L.start_min(when),
                '<tr class="band"><td class="c" style="color:%s;font-weight:700;white-space:nowrap">%s</td>'
                '<td class="c"><b>%s</b></td><td class="c">―</td><td class="c">―</td>'
                '<td class="c" style="color:%s;white-space:nowrap">%d分</td>'
                '<td class="c" style="color:%s">%s</td></tr>'
                % (GOLD, esc(when), esc(place), MUTED, b - a, MUTED, note)))
            continue
        for k, (no, si) in enumerate(sc):
            nm, cuts = L.cuts_of(no, si)
            pl_, _, _, wh = S.SPOT[no][si]
            cam, cnote = L.split_cam(S.D[no][si][0])
            who, prop = L.CASTPROP.get((no, si), ("―", "―"))
            mv, mvday = L.MOVED.get((no, si), ([], ""))
            memo = []
            if k == 0 and note:
                memo.append(note)
            if mv and len(mv) == len(cuts):
                memo.append('%dカット。<span style="color:%s">インタビューの収録で撮る</span>' % (len(cuts), GOLD))
            else:
                m = "%dカット" % (len(cuts) - len(mv))
                if mv:
                    where = "インタビューの収録で撮る" if mvday == S.SPOT[no][si][2] else "%sに撮る" % mvday
                    m += '（<span style="color:%s">%sは%s</span>）' % (
                        GOLD, "・".join("%d枚目" % j for j in mv), where)
                memo.append(m)
            if cnote:
                memo.append(cnote)
            t = S.SPOT[no][si][3]
            blocks.append((L.start_min(t if t != "―" else when),
                '<tr><td class="c" style="color:%s;font-weight:700;white-space:nowrap">%s</td>'
                '<td class="c">%s</td>'
                '<td class="c">%s<br><span style="color:%s">%s</span></td>'
                '<td class="c"><b><span style="color:%s">%s</span> %s</b><br>%s</td>'
                '<td class="c" style="color:%s;white-space:nowrap">%s</td>'
                '<td class="c" style="color:%s">%s</td></tr>'
                % (GOLD, esc(wh),
                   pl_ if pl_ != "同じ" else '<span style="color:%s">同じ</span>' % MUTED,
                   esc(who), MUTED, esc(prop), GOLD, L.MARU[no], esc(nm), cam,
                   MUTED, L.scene_len(no, si), MUTED, "<br>".join(memo))))
    blocks.sort(key=lambda x: x[0])
    rows = [x for _, x in blocks]
    keys = "".join("<li>%s</li>" % k for k in d["keys"])
    return f'''<section class="page">
  <table class="dhead">
    <tr><td>タイトル</td><td><b style="font-size:13pt">{L.day_titles(d)}</b></td></tr>
    <tr><td>撮影日</td><td><b style="font-size:11.5pt">{esc(d["date2"])}</b></td></tr>
    <tr><td>場所</td><td>{esc(d["place"])}</td></tr>
    <tr><td>時間</td><td>{esc(L.day_span(d))}　<span style="color:{FAINT}">撮るカット {shoot}</span></td></tr>
    <tr><td>緊急時連絡先</td><td>&nbsp;</td></tr>
    <tr><td>注意事項</td><td>{d["cond"]}</td></tr>
  </table>
  <table>
    <colgroup><col style="width:9%"><col style="width:17%"><col style="width:14%"><col><col style="width:5%"><col style="width:19%"></colgroup>
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
        rows.append('<tr class="band"><td colspan="4"><b>%s</b>　<span style="color:%s">%s　%s</span>'
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
                        '<span style="color:%s">　S%d %d枚目</span></td>'
                        '<td class="c">%s%s</td><td class="c">%s</td>'
                        '<td class="c" style="color:%s;white-space:nowrap">%s</td>'
                        '</tr>'
                        % (n, FAINT, si, k + 1, ang[k] if k < len(ang) else "", tag,
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
.dhead {{ width:100%; border-collapse:collapse; margin:0 0 3mm; border-bottom:.8pt solid {INK}; }}
.dhead td {{ padding:1.4mm 0; border-bottom:.4pt solid {LINE}; vertical-align:top; font-size:9.5pt; line-height:1.55; }}
.dhead td:first-child {{ width:26mm; color:{FAINT}; font-size:8.5pt; letter-spacing:.06em; white-space:nowrap; }}
b {{ font-weight: 700; }}
'''


def main():
    parts = [cover()] + [day_page(d) for d in L.DAYS] + \
            [cast_page()]
    out = ('<!doctype html><html lang="ja"><head><meta charset="utf-8">'
           '<title>動画八本 香盤表</title><style>%s</style></head><body>%s</body></html>'
           % (CSS, "".join(parts)))
    p = os.path.join(ROOT, "pdf", "kouban.html")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(out)
    print(p, len(parts), "ページぶん")


if __name__ == "__main__":
    main()
