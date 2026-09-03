# -*- coding: utf-8 -*-
"""pdf/kakutei.html を生成する。データを書き換えれば版面は自動で組まれる。"""
import html, os, io

R = "../assets/ref4/"

def esc(s): return html.escape(s, quote=False)

def cell(photo, cap):
    """photo=None なら罫線だけの空枠。cap が「―」なら何も置かない"""
    if cap == "―":
        return '<td></td>'
    if photo:
        img = f'<img src="{R}{photo}.jpg">'
    else:
        img = '<div class="ph0">撮影して差し替え</div>'
    return f'<td>{img}<div class="cap">{cap}</div></td>'

def grid(rows):
    out = ['<table class="grid"><tr><th>シーン</th><th>ショット 1</th><th>ショット 2</th><th>ショット 3</th></tr>']
    for name, t, shots in rows:
        tds = "".join(cell(p, c) for p, c in shots)
        out.append(f'<tr><td class="sc"><b>{name}</b><br>{t}</td>{tds}</tr>')
    out.append("</table>")
    return "\n".join(out)

def vpage(no, jp, en, meta_len, meta_target, ref, plan, says, telop_jp, telop_en, extra, rows, pn, total):
    tel = ""
    if telop_jp:
        tel = f'<div class="telop"><span class="lbl">テ ロ ッ プ</span><div class="jp">{telop_jp}</div><div class="en">{telop_en}</div></div>'
    ext = f'<div class="blk"><span class="lbl">{extra[0]}</span>{extra[1]}</div>' if extra else ""
    return f'''<div class="page">
  <div class="vhead">
    <div class="l"><div class="no">{no}</div><h2>{jp}</h2><div class="enh">{en}</div></div>
    <div class="r"><b>{meta_len}</b><br>{meta_target}<br><span class="lk">{ref}</span></div>
  </div>
  <div class="vbody">
    <div class="col">
      <div class="blk"><span class="lbl">企 画</span>{plan}</div>
      <div class="blk"><span class="lbl">こ の 1 本 で 言 う こ と</span>{says}</div>
      {tel}
      {ext}
    </div>
    {grid(rows)}
  </div>
  <div class="foot">BROOKLYN MUSEUM ／ 向島工房　動画制作</div>
  <div class="pagenum">{pn} / {total}</div>
</div>'''

CSS = """
@page { size: A4 landscape; margin: 0; }
* { margin:0; padding:0; box-sizing:border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family:"IPAPGothic","IPAGothic",sans-serif; color:#1a1a1a; background:#fff;
       font-size:9pt; line-height:1.65; letter-spacing:.02em; }
a { color:#1a1a1a; text-decoration:none; }
.page { width:297mm; height:210mm; padding:13mm 14mm; page-break-after:always;
        position:relative; overflow:hidden; background:#fff; }
.page:last-child { page-break-after:auto; }
.foot { position:absolute; left:14mm; bottom:8mm; font-size:7.5pt; color:#a89b86; letter-spacing:.06em; }
.pagenum { position:absolute; right:14mm; bottom:8mm; font-size:7.5pt; color:#a89b86; letter-spacing:.1em; }
.eyebrow { font-size:7.5pt; letter-spacing:.18em; color:#8a7a63; }

/* 表紙 */
.cover { display:flex; flex-direction:column; justify-content:center; }
.cover h1 { font-size:40pt; line-height:1.25; letter-spacing:.04em; margin:6mm 0 4mm; }
.cover .sub { font-size:13pt; color:#4a4136; letter-spacing:.1em; }
.cover .meta { margin-top:auto; padding-top:8mm; padding-bottom:6mm; border-top:1px solid #d8d0c2;
               font-size:8.5pt; color:#6b5f4d; line-height:1.9; }
.cover .rule { width:40mm; height:3px; background:#1a1a1a; margin-top:2mm; }

/* 目次 */
.h-sec { font-size:19pt; letter-spacing:.04em; }
.subline { font-size:8.5pt; color:#6b5f4d; margin-top:1.5mm; }
table.toc { width:100%; border-collapse:collapse; font-size:8.5pt; margin-top:6mm; }
table.toc th { text-align:left; font-size:7pt; letter-spacing:.12em; color:#8a7a63; font-weight:normal;
               border-bottom:1.5px solid #1a1a1a; padding:0 3mm 1.5mm 0; }
table.toc td { border-bottom:1px solid #e6ded0; padding:2.9mm 3mm 2.9mm 0; vertical-align:top; line-height:1.5; }
table.toc td.n { width:10mm; font-weight:bold; color:#a8763e; }
table.toc td.ti { width:52mm; }
table.toc td.ti b { font-size:10pt; }
table.toc td.ti span { font-size:7.5pt; color:#8a7a63; letter-spacing:.04em; }
table.toc td.ln { width:26mm; color:#6b5f4d; white-space:nowrap; }
table.toc td.tg { width:46mm; color:#4a4136; }
table.toc td.lk { font-size:7.3pt; color:#8a7a63; word-break:break-all; }
table.toc td.pg { width:12mm; text-align:right; color:#6b5f4d; }

/* 各本ページ */
.vhead { display:flex; justify-content:space-between; align-items:flex-end;
         border-bottom:2px solid #1a1a1a; padding-bottom:2.6mm; }
.vhead .l .no { font-size:7.5pt; letter-spacing:.16em; color:#a8763e; font-weight:bold; }
.vhead .l h2 { font-size:19pt; letter-spacing:.03em; line-height:1.15; margin-top:.8mm; }
.vhead .l .enh { font-size:9pt; letter-spacing:.1em; color:#8a7a63; margin-top:.8mm; }
.vhead .r { text-align:right; font-size:8pt; color:#6b5f4d; line-height:1.7; }
.vhead .r b { color:#1a1a1a; font-size:9.5pt; }
.vhead .r .lk { font-size:7.2pt; color:#8a7a63; }

.vbody { display:flex; gap:6mm; margin-top:4mm; }
.col { flex:0 0 96mm; }
.blk { margin-bottom:3.5mm; font-size:8.5pt; line-height:1.7; }
.blk .lbl { display:block; font-size:7pt; letter-spacing:.14em; color:#8a7a63; margin-bottom:1mm; }
.telop { background:#1a1a1a; color:#fff; padding:3mm 3.5mm; margin-bottom:3.5mm; }
.telop .lbl { display:block; font-size:7pt; letter-spacing:.16em; color:#c9b79a; margin-bottom:1.2mm; }
.telop .jp { font-size:11.5pt; line-height:1.4; }
.telop .en { font-size:8.5pt; color:#c9b79a; margin-top:1mm; letter-spacing:.03em; }

table.grid { flex:1; border-collapse:collapse; table-layout:fixed; }
table.grid th { text-align:left; font-size:7pt; letter-spacing:.12em; color:#8a7a63; font-weight:normal;
                border-bottom:1.5px solid #1a1a1a; padding:0 1.6mm 1.4mm 0; }
table.grid td { border-bottom:1px solid #e6ded0; padding:1.8mm 1.6mm 2.4mm 0; vertical-align:top; }
table.grid td.sc { width:25mm; font-size:8pt; line-height:1.45; color:#6b5f4d; }
table.grid td.sc b { color:#1a1a1a; font-size:8.5pt; }
table.grid img { width:100%; height:23mm; object-fit:cover; display:block; border:1px solid #ddd5c6; }
table.grid .ph0 { height:23mm; border:1px dashed #c9bda6; background:#fbf9f4; color:#b3a894;
                  font-size:6.8pt; display:flex; align-items:center; justify-content:center; }
table.grid .cap { font-size:7.1pt; line-height:1.45; margin-top:1.2mm; color:#3a3226; }
table.grid .cap b { border-bottom:1.2px solid #e0c9a4; }
"""

def build(pages, out="pdf/kakutei.html"):
    doc = ('<!DOCTYPE html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n'
           '<title>動画8本 企画・構成・絵コンテ</title>\n<style>' + CSS + '</style>\n</head>\n<body>\n'
           + "\n\n".join(pages) + "\n</body>\n</html>\n")
    with io.open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    return len(doc)
