# -*- coding: utf-8 -*-
"""香盤表とショットリストを、この画面でそのまま読める一枚のページに書き出す。
   実行: python3 tools/build_kouban_page.py  →  kouban.html
   中身は build_shotlist_canvas.py / build_script_canvas.py と同じものを読む。
"""
import html, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_script_canvas as S
import build_shotlist_canvas as L

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def esc(s):
    return html.escape(s or "", quote=True)


def plain(s):
    return re.sub(r"<[^>]+>", "", re.sub(r"<br\s*/?>", " ", s or "")).strip()


from page_style import CSS, FONT

DHEAD = """
.dhead { width:100%; border-collapse:collapse; margin:0 0 18px; border-bottom:2px solid var(--ink); }
.dhead td { padding:9px 0; border-bottom:1px solid var(--hair); vertical-align:top; font-size:15px; line-height:1.7; }
.dhead td:first-child { width:130px; color:var(--faint); font-size:13px; letter-spacing:.08em; white-space:nowrap; }
.dhead .dt { font-size:19px; }
"""


def nav():
    days = "".join('<a href="#%s">%s</a>' % (d["key"], d["no"][:-2] if d["no"].endswith("日目") else d["no"])
                   for d in L.DAYS)
    return ('<nav><div class="navin"><span class="navlab">香盤表</span>%s'
            '<span class="navsep"></span><a href="#cast">出演者と支度</a>'
            '</div></nav>' % days)


def cover():
    rows, ts, te = [], 0, 0
    for d in L.DAYS:
        a, b = L.day_counts(d)
        ts += a
        te += b
        if d.get("talks"):
            books = ""
        books = "".join(
            '<div style="margin-top:5px"><span style="color:var(--gold);font-weight:700">%s</span>'
            '　<b>%s</b><span class="dim">　── %s</span></div>'
            % (L.MARU[no], esc(L.PG[no]["jp"]), tx) for no, tx in d["toc"])
        rows.append(
            '<tr><td><a href="#%s" style="text-decoration:none">'
            '<span class="tm" style="font-size:17px">%s</span></a></td>'
            '<td><b>%s</b></td><td>%s</td>'
            '<td class="tm">%s</td><td class="no">%dカット</td></tr>'
            % (d["key"], esc(d["date"].split("　※")[0]), esc(d["place"]), books,
               esc(L.day_span(d)), a))
    return f'''<header class="top">
  <div class="eyebrow">BROOKLYN MUSEUM ／ 向島工房</div>
  <h1>動画八本　香盤表</h1>
  <div class="en">Shooting Schedule</div>
  <div class="count">全八本　{ts}カット　／　撮影 四日　<span style="color:var(--gold)">日付はすべて仮</span></div>

</header>
<section id="schedule">
  <div class="scroll"><table>
    <colgroup><col style="width:8%"><col style="width:17%"><col><col style="width:11%"><col style="width:8%"></colgroup>
    <thead><tr><th>日付</th><th>場所</th><th>内容</th><th>時間</th><th>カット</th></tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table></div>
</section>'''


def scene_line(no, si, extra=""):
    nm, cuts = L.cuts_of(no, si)
    pl_, _, _, wh = S.SPOT[no][si]
    cam, cnote = L.split_cam(S.D[no][si][0])
    who, prop = L.CASTPROP.get((no, si), ("―", "―"))
    mv, mvday = L.MOVED.get((no, si), ([], ""))
    memo = []
    if extra:
        memo.append(extra)
    if mv and len(mv) == len(cuts):
        memo.append('%dカット。<span class="pin">インタビューの収録で撮る</span>' % len(cuts))
    else:
        m = "%dカット" % (len(cuts) - len(mv))
        if mv:
            where = "インタビューの収録で撮る" if mvday == S.SPOT[no][si][2] else "%sに撮る" % mvday
            m += '（<span class="pin">%sは%s</span>）' % (
                "・".join("%d枚目" % k for k in mv), where)
        memo.append(m)
    return ('<tr><td class="tm">%s</td><td>%s</td>'
            '<td>%s<br><span class="dim">%s</span></td>'
            '<td><span class="sc"><span style="color:var(--gold)">%s</span> %s</span>'
            '<br>%s</td><td class="dim">%s</td><td class="dim">%s</td></tr>'
            % (esc(wh), pl_ if pl_ != "同じ" else '<span class="dim">同じ</span>',
               esc(who), esc(prop), L.MARU[no], esc(nm), cam,
               L.scene_len(no, si), "<br>".join(memo)))


def day_section(d):
    shoot, edit = L.day_counts(d)
    blocks = []
    head = ("時 刻", "場 所 の 詳 細", "登 場 人 物", "シ ー ン 内 容 詳 細", "尺", "備 考")
    for tk in d.get("talks", []):
        when, who, place, what, note = tk[:5]
        b = ['<tr><td class="tm">%s</td><td>%s</td>'
             '<td>%s<br><span class="dim">椅子、ピンマイク</span></td>'
             '<td><span class="sc">%s</span><br>%s</td>'
             '<td class="dim">三十分</td><td class="dim">%s</td></tr>'
             % (esc(when), place, esc(who),
                esc(tk[6] if len(tk) > 6 else "インタビュー"), what, note)]
        blocks.append((L.start_min(when), "".join(b)))
    for setup in d.get("setups", []):
        when, place, sc, note = setup[:4]
        what = setup[4] if len(setup) > 4 else ""
        who = setup[5] if len(setup) > 5 else ""
        if not sc:
            a, b = [int(x.split(":")[0]) * 60 + int(x.split(":")[1]) for x in when.split("〜")]
            blocks.append((L.start_min(when),
                '<tr class="band"><td class="tm">%s</td><td><b>%s</b></td><td>%s</td>'
                '<td>%s</td><td class="dim">%s</td><td class="dim">%s</td></tr>'
                % (esc(when), esc(place), who or "―", what or "―",
                   ("%d時間%d分" % ((b - a) // 60, (b - a) % 60)) if b - a >= 60 else ("%d分" % (b - a)),
                   note)))
            continue
        for k, (no, si) in enumerate(sc):
            t = S.SPOT[no][si][3]
            blocks.append((L.start_min(t if t != "―" else when),
                           scene_line(no, si, note if k == 0 else "")))
    blocks.sort(key=lambda b: b[0])
    rows = [b for _, b in blocks]
    keys = "".join("<li>%s</li>" % k for k in d["keys"])
    return f'''<section id="{d["key"]}">
  <table class="dhead">
    <tr><td>タイトル</td><td><b class="dt">{L.day_titles(d)}</b></td></tr>
    <tr><td>撮影日</td><td><b>{esc(d["date2"])}</b></td></tr>
    <tr><td>場所</td><td>{esc(d["place"])}</td></tr>
    <tr><td>時間</td><td>{esc(L.day_span(d))}　<span class="dim">撮るカット {shoot}</span></td></tr>
    <tr><td>緊急時連絡先</td><td>&nbsp;</td></tr>
    <tr><td>注意事項</td><td>{d["cond"]}</td></tr>
  </table>
  <div class="scroll"><table>
    <colgroup><col style="width:9%"><col style="width:17%"><col style="width:14%"><col><col style="width:5%"><col style="width:19%"></colgroup>
    <thead><tr>{"".join("<th>%s</th>" % h for h in head)}</tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table></div>
</section>'''


def shot_section(no):
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
        rows.append('<tr class="band"><td colspan="4"><b>%s</b>　<span class="sub">%s　%s</span>'
                    '　<span class="tm" style="float:right">%s　%s</span></td></tr>'
                    % (esc(nm), esc(re.sub(r"　｜.*", "", tm)),
                       esc(place if place != "同じ" else "同じ場所"), esc(day), esc(when)))
        for k, sh in enumerate(cuts):
            n += 1
            sec = "%.1f〜%.1f秒" % (sp[0] + each * k, sp[0] + each * (k + 1)) if each else ""
            tag = '<br><span class="pin">%sに撮影</span>' % mvday if k + 1 in mv else ""
            if (no, si) in L.REUSE:
                tag = '<br><span class="pin">撮影しない ── %s</span>' % L.REUSE[(no, si)]
            rows.append('<tr><td><span class="no">%02d</span>'
                        '<span class="sub">　S%d %d枚目</span></td><td>%s%s</td><td>%s</td>'
                        '<td class="dim" style="white-space:nowrap;font-variant-numeric:tabular-nums">%s</td>'
                        '</tr>'
                        % (n, si, k + 1, ang[k] if k < len(ang) else "", tag, sh[1], sec))
    days = []
    for si in sorted(S.SPOT[no]):
        d = S.SPOT[no][si][2]
        if d != "―" and d not in days:
            days.append(d)
    return f'''<section id="sl{no}">
  <div class="shead">
    <div class="daynum" style="color:var(--gold)">{L.MARU[no]}</div>
    <div class="daynum">{esc(pg["jp"])}</div>
    <div class="theme">{esc(pg["en"])}　{esc(plain(pg["meta_len"]))}</div>
    <div class="when">{esc("・".join(days))}</div>
    <div class="cuts">全{n}カット</div>
  </div>
  <div class="scroll"><table>
    <colgroup><col style="width:11%"><col style="width:25%"><col><col style="width:11%"><col style="width:5%"></colgroup>
    <thead><tr><th>№ ／ カット</th><th>画 角</th><th>撮 る も の</th><th>尺 の 目 安</th><th>済</th></tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table></div>
</section>'''


def cast_section():
    rows = []
    for maru, no, day, face, prep, cloth, other in L.CAST:
        name = L.PG[no]["jp"] if no else "永尾社長・佐藤さん・くさがやさん"
        rows.append('<tr><td><span class="daynum" style="font-size:20px;color:var(--gold)">%s</span><br>'
                    '<b>%s</b><br><span class="sub">%s</span></td>'
                    '<td>%s</td><td>%s</td><td>%s</td><td class="dim">%s</td></tr>'
                    % (maru, esc(name), esc(day), esc(face), prep, cloth, other))
    return f'''<section id="cast">
  <div class="shead">
    <div class="daynum">出演者と支度</div>
    <div class="theme">Cast &amp; Preparation</div>
    <div class="when">ヘアメイクは付けない</div>
  </div>
  <p class="note">ヘアメイクは付けません。当日の支度は、鏡・テカリ止めのパウダー・爪の手入れだけです。
  顔が寄りで映るのは①と⑧の二本だけで、ほかは顔を主役にしないか、まったく映しません。</p>
  <div class="scroll"><table>
    <colgroup><col style="width:17%"><col style="width:16%"><col style="width:23%"><col style="width:23%"><col></colgroup>
    <thead><tr><th>本 ／ 撮影日</th><th>顔 が 映 る か</th><th>当 日 の 支 度</th><th>衣 装</th><th>そ の ほ か</th></tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table></div>
  <div class="foot"><div><div class="cap">全 員 に 共 通 す る こ と</div><div class="body">
    出演承諾書を、①④⑦⑧の出演者全員からいただく ── 使う範囲（Instagram・EC商品ページ・展示会）、期間、媒体を書いたもの。<br>
    交通費と拘束時間を、依頼するときに先に伝える。<br>
    体調不良に備えて、①と④は予備日を一日置く。</div></div></div>
</section>'''


def main():
    body = (nav() + '<div class="wrap">' + cover() +
            "".join(day_section(d) for d in L.DAYS) +
            cast_section() + "</div>")
    out = ('<title>動画八本 香盤表</title>\n%s\n'
           '<style>%s%s</style>\n%s\n' % (FONT, CSS, DHEAD, body))
    p = os.path.join(ROOT, "kouban.html")
    open(p, "w", encoding="utf-8").write(out)
    print(p, len(out), "バイト")


if __name__ == "__main__":
    main()
