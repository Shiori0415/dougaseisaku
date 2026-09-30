# -*- coding: utf-8 -*-
"""小道具・備品チェックリストを、出演者ごとのHTML（Googleドキュメント取り込み用）で書き出す。
   実行: python3 tools/build_kodougu_doc.py → pdf/kodougu_<名前>.html
   中身は build_xlsx_kodougu_kojin.py の PEOPLE をそのまま読む。
   Googleドライブの create_file（contentMimeType: text/html）で上げると、表・色・太字が残る。
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_xlsx_kodougu_kojin import PEOPLE, ROOT

TD = 'style="border:1px solid #BFB8AC;padding:5px 8px;font-size:10.5pt'


def build(name, groups):
    rows, n = [], 0
    for kind, items in groups:
        rows.append(f'<tr><td colspan="5" {TD};background:#EDE6DA;font-weight:bold">{kind}</td></tr>')
        for item, qty, note, state in items:
            n += 1
            if state == "要確認":
                note = f'<span style="color:#A8672A;font-weight:bold">要確認</span>　{note}'
            rows.append(
                f'<tr><td {TD};text-align:center;font-size:14pt">☐</td>'
                f'<td {TD};text-align:center">{n}</td>'
                f'<td {TD};font-weight:bold">{item}</td>'
                f'<td {TD};text-align:center">{qty}</td>'
                f'<td {TD};color:#3D4448">{note}</td></tr>')
    head = "".join(
        f'<td {TD};background:#15191C;color:#FFFFFF;font-weight:bold;text-align:center;width:{w}">{h}</td>'
        for h, w in [("確認", "8%"), ("No.", "6%"), ("品目", "30%"), ("数", "14%"), ("使う場面・備考", "42%")])
    return (f'<html><head><meta charset="utf-8"></head><body>'
            f'<h2>{name}　小道具・備品チェックリスト</h2>'
            f'<p>撮影日：　　月　　日　／　全 {n} 点</p>'
            f'<table style="border-collapse:collapse;width:100%"><tr>{head}</tr>{"".join(rows)}</table>'
            f'</body></html>')


if __name__ == "__main__":
    for name, groups in PEOPLE.items():
        out = os.path.join(ROOT, "pdf", f"kodougu_{name}.html")
        open(out, "w").write(build(name, groups))
        print(out, os.path.getsize(out))
