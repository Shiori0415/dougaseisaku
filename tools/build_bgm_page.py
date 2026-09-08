# -*- coding: utf-8 -*-
"""BGMの資料を、この画面でそのまま読める一枚のページに書き出す。
   実行: python3 tools/build_bgm_page.py  →  bgm.html
   中身は build_bgm_canvas.py と同じものを読む。
"""
import html, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from page_style import CSS, FONT
import build_bgm_canvas as B

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
MARU = {"01": "①", "02": "②", "03": "③", "04": "④",
        "05": "⑤", "06": "⑥", "07": "⑦", "08": "⑧"}


def esc(s):
    return html.escape(s or "", quote=True)


def music_rows():
    out = []
    for no, jp, sec, role, tempo, arc, kw in B.MUSIC:
        out.append(
            '<tr><td><span class="daynum" style="font-size:20px;color:var(--gold)">%s</span><br>'
            '<b>%s</b><br><span class="sub">%s</span></td>'
            '<td>%s</td><td>%s</td><td>%s</td>'
            '<td class="dim" style="font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px">%s</td></tr>'
            % (MARU[no], esc(jp), esc(sec), role, tempo, arc, esc(kw).replace("／", "<br>")))
    return "".join(out)


def shop_rows():
    out = []
    for kind, name, scope, why, url in B.SHOPS:
        cls = "tag paid" if kind.startswith("有料") else "tag"
        out.append('<tr><td><span class="%s">%s</span></td>'
                   '<td><b style="font-size:16px">%s</b><br>'
                   '<a href="%s" target="_blank" rel="noopener" style="font-size:13px">%s</a></td>'
                   '<td>%s</td><td class="dim">%s</td></tr>'
                   % (cls, esc(kind), esc(name), esc(url),
                      esc(url.replace("https://", "").rstrip("/")), scope, why))
    return "".join(out)


def note_blocks():
    return "".join(
        '<div><div class="cap">%s</div><div class="body">%s</div></div>'
        % (esc(t), b) for t, b in B.NOTES)


def main():
    body = f'''<nav><div class="navin">
  <span class="navlab">BGM</span>
  <a href="#music">八本の音楽の方向</a><a href="#shops">どこで手に入れるか</a><a href="#notes">気をつけること</a>
</div></nav>
<div class="wrap">
<header class="top">
  <div class="eyebrow">BROOKLYN MUSEUM ／ 向島工房</div>
  <h1>BGMの選び方</h1>
  <div class="en">Music Direction &amp; Where to Get It</div>
  <div class="count">八本ぶんの音楽の方向　／　無料で揃える手順</div>
  <p class="lead">{B.INTRO_A}</p>
</header>

<section id="music">
  <div class="shead">
    <div class="daynum">八本の音楽の方向</div>
    <div class="theme">テンポ・楽器・展開・検索の言葉</div>
    <div class="when">歌の入った曲は八本とも使わない</div>
  </div>
  <div class="scroll"><table style="min-width:1040px">
    <colgroup><col style="width:17%"><col style="width:19%"><col style="width:20%"><col style="width:26%"><col></colgroup>
    <thead><tr><th>本</th><th>役 割</th><th>テ ン ポ ・ 楽 器</th><th>展 開</th><th>検 索 の 言 葉（英語）</th></tr></thead>
    <tbody>{music_rows()}</tbody>
  </table></div>
</section>

<section id="shops">
  <div class="shead">
    <div class="daynum">どこで手に入れるか</div>
    <div class="theme">無料七つ・有料四つ</div>
    <div class="when">八本とも無料で揃えられる</div>
  </div>
  <div class="scroll"><table style="min-width:1000px">
    <colgroup><col style="width:8%"><col style="width:22%"><col style="width:28%"><col></colgroup>
    <thead><tr><th>区 分</th><th>サ イ ト</th><th>使 え る 範 囲</th><th>ど ん な と き に</th></tr></thead>
    <tbody>{shop_rows()}</tbody>
  </table></div>
</section>

<section id="notes">
  <div class="shead">
    <div class="daynum">気をつけること</div>
    <div class="theme">曲を決める前に読む</div>
  </div>
  <div class="foot" style="border-top:none;margin-top:20px;padding-top:0">{note_blocks()}</div>
</section>
</div>'''
    out = ('<title>BGMの選び方</title>\n%s\n<style>%s</style>\n%s\n' % (FONT, CSS, body))
    p = os.path.join(ROOT, "bgm.html")
    open(p, "w", encoding="utf-8").write(out)
    print(p, len(out), "バイト")


if __name__ == "__main__":
    main()
