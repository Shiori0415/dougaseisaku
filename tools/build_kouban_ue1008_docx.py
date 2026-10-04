# -*- coding: utf-8 -*-
"""上里さん1008の香盤表（絵コンテ版）を、元の香盤表と同じ版面（レター横・余白28.3pt・列幅）の .docx で書き出す。
   中身は pdf/kouban_ue1008.html（build_kouban_ue1008.py の出力を整えたもの）をそのまま読む。
   実行: python3 tools/build_kouban_ue1008_docx.py → pdf/20261008_香盤表_絵コンテ版.docx
"""
import os, re, html, zipfile
from xml.sax.saxutils import escape
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
COLS = [1860, 1964, 8730, 2400]                      # 元の列幅 93 / 98.2 / 436.5 / 120pt（twip）
CLS = {"h": ("FFFFFF", True), "r": ("FF0000", False), "bb": ("0000FF", True), "b": (None, True), "g": ("38761D", False), "": (None, False)}


def run(t, cls=""):
    color, b = CLS[cls]
    rpr = ("<w:b/>" if b else "") + (f'<w:color w:val="{color}"/>' if color else "")
    return f'<w:r>{"<w:rPr>" + rpr + "</w:rPr>" if rpr else ""}<w:t xml:space="preserve">{escape(t)}</w:t></w:r>'


def para(inner):
    runs = ""
    for m in re.finditer(r'<span class="([a-z]*)">(.*?)</span>|([^<]+)', inner):
        runs += run(html.unescape(m.group(2)), m.group(1)) if m.group(2) is not None else run(html.unescape(m.group(3)))
    return f'<w:p><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>{runs}</w:p>'


def document(src):
    rows = re.findall(r"<tr>(.*?)</tr>", src, re.S)
    wb, bk = 'w:val="single" w:sz="8" w:color="FFFFFF"', 'w:val="single" w:sz="8" w:color="000000"'
    out = []
    for ri, r in enumerate(rows):
        cells = []
        for ci, td in enumerate(re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)):
            ps = re.findall(r"<p>(.*?)</p>", td, re.S) or [""]
            bd = (f"<w:tcBorders><w:top {wb}/><w:left {wb}/><w:bottom {bk}/><w:right {wb}/></w:tcBorders>"
                  '<w:shd w:val="clear" w:color="auto" w:fill="073763"/>') if ri == 0 else ""
            cells.append(f'<w:tc><w:tcPr><w:tcW w:w="{COLS[ci]}" w:type="dxa"/>{bd}</w:tcPr>{"".join(para(p) for p in ps)}</w:tc>')
        out.append("<w:tr>" + "".join(cells) + "</w:tr>")
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in COLS)
    tblpr = (f'<w:tblW w:w="{sum(COLS)}" w:type="dxa"/><w:tblInd w:w="-240" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
             f"<w:tblBorders><w:top {bk}/><w:left {bk}/><w:bottom {bk}/><w:right {bk}/><w:insideH {bk}/><w:insideV {bk}/></w:tblBorders>"
             '<w:tblCellMar><w:top w:w="100" w:type="dxa"/><w:left w:w="100" w:type="dxa"/>'
             '<w:bottom w:w="100" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar>')
    title = html.unescape(re.search(r"<p><b>(.*?)</b></p>", src).group(1))
    body = (f'<w:p><w:pPr><w:spacing w:after="60"/></w:pPr>{run(title, "b")}</w:p>'
            f'<w:tbl><w:tblPr>{tblpr}</w:tblPr><w:tblGrid>{grid}</w:tblGrid>{"".join(out)}</w:tbl><w:p/>')
    sect = ('<w:sectPr><w:pgSz w:w="15840" w:h="12240" w:orient="landscape"/>'
            '<w:pgMar w:top="566" w:right="566" w:bottom="566" w:left="566" w:header="0" w:footer="0" w:gutter="0"/></w:sectPr>')
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f"<w:body>{body}{sect}</w:body></w:document>")


STYLES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
          '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial"/>'
          '<w:sz w:val="22"/></w:rPr></w:rPrDefault></w:docDefaults></w:styles>')
CT = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
      '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
      '<Default Extension="xml" ContentType="application/xml"/>'
      '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
      '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
      '</Types>')
RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '</Relationships>')
DOCRELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
           '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
           '</Relationships>')

if __name__ == "__main__":
    src = open(os.path.join(ROOT, "pdf", "kouban_ue1008.html"), encoding="utf-8").read()
    out = os.path.join(ROOT, "pdf", "20261008_香盤表_絵コンテ版.docx")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr("[Content_Types].xml", CT)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/_rels/document.xml.rels", DOCRELS)
        z.writestr("word/styles.xml", STYLES)
        z.writestr("word/document.xml", document(src))
    print(out, os.path.getsize(out))
