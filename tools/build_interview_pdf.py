# -*- coding: utf-8 -*-
"""インタビュー質問事項を、A4横で流れるPDF用HTMLに書き出す。
   実行: python3 tools/build_interview_pdf.py
   中身は build_interview.py の COMMON / PEOPLE をそのまま読む。
   行は途中で切らない（tr は break-inside: avoid、見出し帯は break-after: avoid）。
"""
import html, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_interview as B

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
INK, PROSE, MUTED, FAINT = "#15191c", "#3d4448", "#5b6266", "#8a8f92"
GOLD, LINE, HAIR, BAND = "#a8672a", "#ddd7cd", "#ebe6dd", "#f4efe7"
BASEPT = os.environ.get("SHITSUMON_PT", "7.4")


def esc(s):
    return html.escape(s or "", quote=True)


def th():
    return ('text-align:left;font-size:7pt;font-weight:400;color:%s;letter-spacing:.08em;'
            'border-bottom:.6pt solid %s;padding:0 3mm 1.6mm 0' % (FAINT, INK))


def common():
    rows = "".join(
        '<tr><td class="pt">%s</td><td class="dim">%s</td></tr>' % (a, b) for a, b in B.COMMON)
    return f'''<section class="psec">
  <div class="phead"><span class="pname">四 人 に 共 通</span>
    <span class="prole">撮る前に、その場で伝えること</span></div>
  <table>
    <colgroup><col style="width:26%"><col></colgroup>
    <tbody>{rows}</tbody>
  </table>
</section>'''


def person(p):
    rows, i = [], 0
    for x in p["qs"]:
        if isinstance(x, str):
            rows.append('<tr class="band"><td colspan="4">%s</td></tr>' % x)
            continue
        i += 1
        q, ex, pick = x
        rows.append('<tr><td class="no">%d</td><td class="q">%s</td>'
                    '<td class="ex">%s</td><td class="dim">%s</td></tr>' % (i, q, ex, pick))
    use = '<p class="use">%s</p>' % p["use"] if p["use"] else ""
    return f'''<section class="psec">
  <div class="phead"><span class="pname">{p["name"]}</span>
    <span class="prole">{esc(p["role"])}</span>
    <span class="pvid">{esc(p["video"])}　／　{esc(p["length"])}</span>
    <span class="pn">{i}問</span></div>
  {use}
  <table>
    <colgroup><col style="width:3.4%"><col style="width:26%"><col style="width:32%"><col></colgroup>
    <thead><tr><th style="{th()}"></th><th style="{th()}">質 問</th>
      <th style="{th()}">こ う 答 え て も ら え れ ば 十 分</th>
      <th style="{th()}">な ぜ 聞 く か 　── 誰 に 、 何 の た め に</th></tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
</section>'''


CSS = f'''
@page {{ size: A4 landscape; margin: 9mm 11mm; }}
* {{ box-sizing: border-box; }}
html {{ color-scheme: light; background: #fff; }}
body {{ margin: 0; background: #fff; font-family: 'IPAPGothic','IPAGothic',sans-serif;
  color: {INK}; font-size: {BASEPT}pt; line-height: 1.42;
  -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
.head {{ border-bottom: 1.2pt solid {INK}; padding-bottom: 2.6mm; margin-bottom: 3.4mm; }}
.eyebrow {{ font-size: 7pt; font-weight: 700; color: {GOLD}; letter-spacing: .14em; margin-bottom: 1.4mm; }}
.titlerow {{ display: flex; align-items: baseline; gap: 5mm; }}
.title {{ font-size: 19pt; font-weight: 700; letter-spacing: -.01em; }}
.sub {{ font-size: 9pt; color: {FAINT}; }}
.right {{ margin-left: auto; font-size: 9pt; font-weight: 700; }}
.lead {{ margin: 0 0 3.4mm; font-size: 8pt; line-height: 1.7; color: {MUTED}; }}

.psec {{ margin-top: 4.2mm; }}
.psec:first-of-type {{ margin-top: 0; }}
.phead {{ display: flex; align-items: baseline; gap: 4mm; flex-wrap: wrap;
  border-bottom: 1pt solid {INK}; padding-bottom: 1.8mm; break-after: avoid; }}
.pname {{ font-size: 13pt; font-weight: 700; letter-spacing: -.01em; }}
.prole {{ font-size: 8pt; color: {MUTED}; }}
.pvid {{ font-size: 8.6pt; font-weight: 700; color: {GOLD}; }}
.pn {{ margin-left: auto; font-size: 8pt; font-weight: 700; color: {FAINT}; }}
.use {{ margin: 2mm 0 0; font-size: 7.6pt; line-height: 1.65; color: {PROSE};
  break-after: avoid; }}

table {{ width: 100%; border-collapse: collapse; table-layout: fixed; margin-top: 2.4mm; }}
thead {{ display: table-header-group; }}
tr {{ break-inside: avoid; }}
td {{ padding: 0.95mm 2.6mm 0.95mm 0; border-bottom: .4pt solid {HAIR};
  vertical-align: top; word-wrap: break-word; }}
tr.band td {{ background: {BAND}; padding: 0.85mm 2.2mm; border-bottom: .5pt solid {LINE};
  font-size: 8.2pt; font-weight: 700; break-after: avoid; }}
.no {{ font-weight: 700; color: {GOLD}; }}
.q {{ font-weight: 700; font-size: 8.2pt; }}
.dim {{ color: {MUTED}; }}
.pt {{ font-weight: 700; font-size: 8.2pt; }}
.ex::before {{ content: "「"; color: {FAINT}; }}
.ex::after {{ content: "」"; color: {FAINT}; }}
.tag {{ display: inline-block; font-size: 6.6pt; font-weight: 700; letter-spacing: .06em;
  padding: 0 1.4mm; margin: 0 1mm .6mm 0; border-radius: 2mm;
  border: .4pt solid {LINE}; color: {MUTED}; white-space: nowrap; }}
.tag.hon {{ color: {GOLD}; border-color: {GOLD}; }}
.tag.oem {{ color: {PROSE}; border-color: {PROSE}; }}
.tag.med {{ color: {MUTED}; }}
.tag.saiyo {{ color: {FAINT}; }}
.sm {{ font-size: 6.9pt; color: {FAINT}; }}
.eng {{ font-weight: 400; font-size: 7pt; color: {FAINT}; }}
b {{ font-weight: 700; }}
'''


def build():
    n = sum(B.qcount(p) for p in B.PEOPLE)
    body = common() + "".join(person(p) for p in B.PEOPLE)
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8">
<title>インタビュー　質問事項</title>
<style>{CSS}</style></head><body>
<div class="head">
  <div class="eyebrow">BROOKLYN MUSEUM ／ 向島工房</div>
  <div class="titlerow">
    <div class="title">インタビュー　質問事項</div>
    <div class="sub">Interview Questions</div>
    <div class="right">四人　／　{n}問</div>
  </div>
</div>
<p class="lead"><b>聞く順は、画の順。</b>一問ずつ、乗る画と、
<b>誰に向けて、なぜ聞くのか</b>を添えてある。</p>
{body}
</body></html>'''


if __name__ == "__main__":
    out = os.path.join(ROOT, "pdf", "shitsumon.html")
    open(out, "w", encoding="utf-8").write(build())
    print(out, os.path.getsize(out), "バイト")
