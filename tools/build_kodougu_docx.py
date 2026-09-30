# -*- coding: utf-8 -*-
"""小道具・備品チェックリスト（三人分）を、Googleドキュメントに取り込める最小の .docx で書き出す。
   実行: python3 tools/build_kodougu_docx.py → pdf/04_小道具チェックリスト_三人分.docx
   HTML取り込みでは改ページが効かないので、docx の改ページ（w:br type=page）で一人一ページにする。
   中身は build_xlsx_kodougu_kojin.py の PEOPLE をそのまま読む。
"""
import os, sys, zipfile
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_xlsx_kodougu_kojin import PEOPLE, ROOT

FIT = "鞄に無理なく収まる量"
COLS = [700, 600, 3000, 1500, 4406]          # 列の幅（twip）。A4縦・左右15mm
LINE, INK, BAND, GOLD, MUTED = "BFB8AC", "15191C", "EDE6DA", "A8672A", "5B6266"


def run(t, b=False, color=None, sz=None):
    rpr = ("<w:b/>" if b else "") + (f'<w:color w:val="{color}"/>' if color else "") \
        + (f'<w:sz w:val="{sz}"/>' if sz else "")
    return f'<w:r>{"<w:rPr>" + rpr + "</w:rPr>" if rpr else ""}<w:t xml:space="preserve">{escape(str(t))}</w:t></w:r>'


def para(runs, jc=None):
    j = f'<w:jc w:val="{jc}"/>' if jc else ""
    ppr = f'<w:pPr><w:spacing w:after="0"/>{j}</w:pPr>'
    return f"<w:p>{ppr}{runs}</w:p>"


def cell(w, runs, jc=None, fill=None, span=None):
    tcpr = f'<w:tcW w:w="{w}" w:type="dxa"/>' + (f'<w:gridSpan w:val="{span}"/>' if span else "") \
        + (f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>' if fill else "") + '<w:vAlign w:val="center"/>'
    return f"<w:tc><w:tcPr>{tcpr}</w:tcPr>{para(runs, jc)}</w:tc>"


def row(cells, header=False):
    trpr = "<w:cantSplit/>" + ("<w:tblHeader/>" if header else "") + '<w:trHeight w:val="400"/>'
    return f"<w:tr><w:trPr>{trpr}</w:trPr>{''.join(cells)}</w:tr>"


def table(groups):
    b = f'w:val="single" w:sz="4" w:color="{LINE}"'
    rows = [row([cell(w, run(h, True, "FFFFFF"), "center", INK)
                 for w, h in zip(COLS, ["確認", "No.", "品目", "数", "使う場面・備考"])], header=True)]
    n = 0
    for kind, items in groups:
        label = run(kind, True) + (run(f"　（どれも{FIT}）", color=MUTED) if kind == "鞄の中身" else "")
        rows.append(row([cell(sum(COLS), label, fill=BAND, span=5)]))
        for item, qty, note, state in items:
            n += 1
            note = "" if note == FIT else note
            nr = (run("要確認", True, GOLD) + run("　") if state == "要確認" else "") + run(note)
            rows.append(row([cell(COLS[0], run("☐", sz=24), "center"), cell(COLS[1], run(n), "center"),
                             cell(COLS[2], run(item, True)), cell(COLS[3], run(qty), "center"),
                             cell(COLS[4], nr)]))
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in COLS)
    tblpr = (f'<w:tblW w:w="{sum(COLS)}" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
             f'<w:tblBorders><w:top {b}/><w:left {b}/><w:bottom {b}/><w:right {b}/>'
             f'<w:insideH {b}/><w:insideV {b}/></w:tblBorders>'
             '<w:tblCellMar><w:left w:w="80" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar>')
    return f"<w:tbl><w:tblPr>{tblpr}</w:tblPr><w:tblGrid>{grid}</w:tblGrid>{''.join(rows)}</w:tbl>", n


def document():
    body = []
    for i, (name, groups) in enumerate(PEOPLE.items()):
        tbl, n = table(groups)
        if i:
            body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        body.append(para(run(f"{name}　小道具・備品チェックリスト", True, sz=32)))
        body.append(para(run(f"撮影日：　　月　　日　／　全 {n} 点", sz=20)))
        body.append(para(""))
        body.append(tbl)
    sect = ('<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
            '<w:pgMar w:top="850" w:right="850" w:bottom="850" w:left="850" w:header="0" w:footer="0" w:gutter="0"/>'
            '</w:sectPr>')
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f'<w:body>{"".join(body)}{sect}</w:body></w:document>')


STYLES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
          '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Noto Sans JP"/>'
          '<w:sz w:val="19"/></w:rPr></w:rPrDefault></w:docDefaults></w:styles>')
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
    out = os.path.join(ROOT, "pdf", "04_小道具チェックリスト_三人分.docx")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr("[Content_Types].xml", CT)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/_rels/document.xml.rels", DOCRELS)
        z.writestr("word/styles.xml", STYLES)
        z.writestr("word/document.xml", document())
    print(out, os.path.getsize(out))
