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


def nav():
    days = "".join('<a href="#%s">%s</a>' % (d["key"], d["no"][:-2] if d["no"].endswith("日目") else d["no"])
                   for d in L.DAYS)
    shots = "".join('<a href="#sl%s">%s</a>' % (no, L.MARU[no]) for no in L.SHOT_ORDER)
    return ('<nav><div class="navin"><span class="navlab">香盤表</span>%s'
            '<span class="navsep"></span><span class="navlab">ショットリスト</span>%s'
            '<span class="navsep"></span><a href="#cast">出演者と支度</a>'
            '</div></nav>' % (days, shots))


def cover():
    rows, ts, te = [], 0, 0
    for d in L.DAYS:
        a, b = L.day_counts(d)
        ts += a
        te += b
        if d.get("talks"):
            books = '永尾社長・佐藤さん・くさがやさん　<span class="sub">⑤と⑥の語りを全部</span>'
        else:
            books = "<br>".join(
                '<span style="color:var(--gold);font-weight:700">%s</span>　%s'
                '<span class="sub">　%s</span>'
                % (L.MARU[no], esc(L.PG[no]["jp"]), esc(plain(L.PG[no]["meta_len"])))
                for no, _ in d["blocks"])
        rows.append(
            '<tr><td><a href="#%s" style="color:inherit;text-decoration:none">'
            '<span class="sc">%s</span></a><br><span class="sub">%s</span></td>'
            '<td><b>%s</b></td><td>%s</td>'
            '<td class="tm">%s</td><td class="no">%dカット</td></tr>'
            % (d["key"], esc(d["no"]), esc(d["theme"]), esc(d["place"]), books,
               esc(L.day_span(d)), a))
    return f'''<header class="top">
  <div class="eyebrow">BROOKLYN MUSEUM ／ 向島工房</div>
  <h1>動画八本　香盤表とショットリスト</h1>
  <div class="en">Shooting Schedule &amp; Shot List</div>
  <div class="count">全八本　{ts + te}カット　／　撮影 九日</div>
  <p class="lead">はじめの二日で短い二本（②③）を撮り、編集まで一度通します。<b>三日目に三人の語りを全部録り、四日目からは、録れた声に画を当てていきます。</b>
  声が先にあると、どの画を何秒使うかが決まるので、撮る量に無駄が出ません。出演者の手配が要る⑧⑦④①は、支度の重い順に、あとの四日へ置いています。
  {ts}カットを撮影し、残りの{te}カット（白バックと文字だけの画面）は編集で作ります。</p>
</header>
<section id="schedule">
  <div class="scroll"><table>
    <colgroup><col style="width:16%"><col style="width:20%"><col><col style="width:13%"><col style="width:10%"></colgroup>
    <thead><tr><th>日 ／ ねらい</th><th>場所</th><th>撮る本</th><th>時間</th><th>カット</th></tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table></div>
  <div class="foot">
    <div><div class="cap">先に決めておくこと</div><div class="body">
      三日目 ── 三人の予定を一日で押さえる。永尾社長・佐藤さんが工房、くさがやさんが店。<br>
      六日目 ── 購入者インタビューの出演者と、顔出しの範囲。<br>
      七日目 ── 鞄に物を入れて持ち出す方。顔は映らないので、手と肩だけ。<br>
      八日目 ── 曇りの日に合わせるため、前後に予備日を一日置く。<br>
      九日目 ── 出演者と、衣装・鞄 四色ぶん。会場の撮影申請。</div></div>
    <div><div class="cap">全日に共通すること</div><div class="body">
      明るさとホワイトバランスはマニュアルで固定する。<br>
      一カットは十秒回す。使うのは一〜二秒でも、前後に余裕がないとつながらない。<br>
      同じ動作は三回撮る ── 手が入る前、動作中、手が抜けたあと。</div></div>
  </div>
</section>'''


def day_section(d):
    shoot, edit = L.day_counts(d)
    rows = []
    if d.get("talks"):
        head = ("時 刻", "話 す 人", "場 所（セット）", "録 る こ と ・ 撮 る 画", "気 を つ け る こ と")
        for when, who, place, what, note in d["talks"]:
            rows.append('<tr><td class="tm">%s</td><td class="sc">%s</td><td>%s</td>'
                        '<td>%s</td><td class="dim">%s</td></tr>'
                        % (esc(when), esc(who), place, what, note))
    else:
        head = ("時 刻", "シ ー ン", "場 所（セット）", "画 角 の 並 び", "気 を つ け る こ と")
        for no, sis in d["blocks"]:
            pg = L.PG[no]
            rows.append('<tr class="band"><td colspan="5">'
                        '<span style="color:var(--gold);font-weight:700">%s</span>　<b>%s</b>　'
                        '<span class="sub">%s　%s</span></td></tr>'
                        % (L.MARU[no], esc(pg["jp"]), esc(pg["en"]), esc(plain(pg["meta_len"]))))
            for si in sis:
                nm, cuts = L.cuts_of(no, si)
                place, _, _, when = S.SPOT[no][si]
                cam, note = L.split_cam(S.D[no][si][0])
                mv = L.MOVED.get((no, si), [])
                cnt = "%dカット" % (len(cuts) - len(mv))
                if mv:
                    cnt += '<br><span class="pin">%sは%s</span>' % (
                        "".join(L.CIR[k - 1] for k in mv), L.TALK_DAY)
                tc = ('<span class="sub">撮影しない</span>' if L.is_edit_only(no, si)
                      else '<span class="tm">%s</span>' % esc(when))
                rows.append('<tr><td>%s</td><td><span class="sc">%s</span><br>'
                            '<span class="sub">%s</span></td><td>%s</td><td>%s</td>'
                            '<td class="dim">%s</td></tr>'
                            % (tc, esc(nm), cnt,
                               place if place != "同じ" else '<span class="dim">同じ</span>',
                               cam, note))
    keys = "".join("<li>%s</li>" % k for k in d["keys"])
    return f'''<section id="{d["key"]}">
  <div class="shead">
    <div class="daynum">{esc(d["no"])}</div>
    <div class="place">{esc(d["place"])}</div>
    <div class="theme">{esc(d["theme"])}</div>
    <div class="when">{esc(L.day_span(d))}</div>
    <div class="cuts">撮るカット {shoot}{"（ほかに編集で作る %d）" % edit if edit else ""}</div>
  </div>
  <p class="note">{d["lead"]}</p>
  <div class="scroll"><table>
    <colgroup><col style="width:11%"><col style="width:15%"><col style="width:21%"><col style="width:29%"><col></colgroup>
    <thead><tr>{"".join("<th>%s</th>" % h for h in head)}</tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table></div>
  <div class="foot">
    <div><div class="cap">持 ち 物</div><div class="body">{d["gear"]}</div></div>
    <div><div class="cap">こ の 日 の 要 点</div><div class="body"><ul>{keys}</ul></div></div>
  </div>
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
        mv = L.MOVED.get((no, si), [])
        rows.append('<tr class="band"><td colspan="5"><b>%s</b>　<span class="sub">%s　%s</span>'
                    '　<span class="tm" style="float:right">%s　%s</span></td></tr>'
                    % (esc(nm), esc(re.sub(r"　｜.*", "", tm)),
                       esc(place if place != "同じ" else "同じ場所"), esc(day), esc(when)))
        for k, sh in enumerate(cuts):
            n += 1
            sec = "%.1f〜%.1f秒" % (sp[0] + each * k, sp[0] + each * (k + 1)) if each else ""
            tag = '<br><span class="pin">%sに撮影</span>' % L.TALK_DAY if k + 1 in mv else ""
            rows.append('<tr><td><span class="no">%02d</span>'
                        '<span class="sub">　S%d-%s</span></td><td>%s%s</td><td>%s</td>'
                        '<td class="dim" style="white-space:nowrap;font-variant-numeric:tabular-nums">%s</td>'
                        '<td><span class="box"></span></td></tr>'
                        % (n, si, L.CIR[k], ang[k] if k < len(ang) else "", tag, sh[1], sec))
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
            "".join(shot_section(no) for no in L.SHOT_ORDER) +
            cast_section() + "</div>")
    out = ('<title>動画八本 香盤表とショットリスト</title>\n%s\n'
           '<style>%s</style>\n%s\n' % (FONT, CSS, body))
    p = os.path.join(ROOT, "kouban.html")
    open(p, "w", encoding="utf-8").write(out)
    print(p, len(out), "バイト")


if __name__ == "__main__":
    main()
