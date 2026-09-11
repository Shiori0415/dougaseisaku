# -*- coding: utf-8 -*-
"""pdf/kouban.html の行の高さを測って、A4横一枚に収まる分け方を決める"""
import json, os, re, subprocess, sys
SP = os.path.dirname(os.path.abspath(__file__))
ROOT = "/home/user/dougaseisaku"
PAGE_H = 718          # A4横 210mm − 余白23mm ＝ 187mm ＝ 707px
CONT_HEAD = 46        # 「つづき」の見出しぶん

def measure():
    j = os.path.join(ROOT, "tools", "pdf_split.json")
    if os.path.exists(j):
        os.remove(j)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_shotlist_pdf.py")],
                   capture_output=True)
    s = open(os.path.join(ROOT, "pdf", "kouban.html"), encoding="utf-8").read()
    js = ("<script>window.addEventListener('load',function(){var o=[];"
          "document.querySelectorAll('.page').forEach(function(el,i){"
          "var t=el.querySelector('table[data-t]');"
          "o.push('S|'+i+'|'+(t?t.dataset.t:'')+'|'+Math.round(el.getBoundingClientRect().height)"
          "+'|'+(t?Math.round(t.getBoundingClientRect().height):0));});"
          "document.querySelectorAll('tr[data-r]').forEach(function(tr){"
          "o.push('R|'+tr.dataset.r+'|'+Math.round(tr.getBoundingClientRect().height));});"
          "document.title='M '+o.join(' ');});</script>")
    open(os.path.join(SP, "meas.html"), "w", encoding="utf-8").write(
        s.replace("</style>", "</style>" + js, 1))
    out = subprocess.run(["/opt/pw-browsers/chromium", "--headless", "--disable-gpu",
        "--no-sandbox", "--window-size=1031,707", "--virtual-time-budget=5000",
        "--dump-dom", "file://%s/meas.html" % SP], capture_output=True, text=True).stdout
    m = re.search(r"<title>M (.*?)</title>", out, re.S)
    return m.group(1).split()

def main():
    toks = measure()
    sec, rows = [], {}
    for t in toks:
        p = t.split("|")
        if p[0] == "S":
            sec.append((int(p[1]), p[2], int(p[3]), int(p[4])))
        else:
            rows.setdefault(p[1], []).append((int(p[2]), int(p[3])))
    split = {}
    for idx, day, sh, th in sec:
        if not day:
            print("  枠外（表紙など） 高さ %d" % sh)
            continue
        rs = [h for _, h in sorted(rows[day])]
        head = sh - th                       # 日の見出しぶん
        thead = th - sum(rs)                 # 表の見出しぶん
        def fits(ch):
            i = 0
            for k, n in enumerate(ch):
                if n <= 0:
                    return False
                top = (head if k == 0 else CONT_HEAD) + thead
                if top + sum(rs[i:i + n]) > PAGE_H:
                    return False
                i += n
            return i == len(rs)

        # まず最小の枚数を求める
        chunks, cur, used = [], 0, head + thead
        for h in rs:
            if cur and used + h > PAGE_H:
                chunks.append(cur)
                cur, used = 0, CONT_HEAD + thead
            cur += 1
            used += h
        chunks.append(cur)
        # 枚数を変えずに、行数をならす
        def heights(ch):
            out, i = [], 0
            for k, n in enumerate(ch):
                out.append((head if k == 0 else CONT_HEAD) + thead + sum(rs[i:i + n]))
                i += n
            return out

        def score(ch):
            hs = heights(ch)
            a = sum(hs) / len(hs)
            return sum((h - a) ** 2 for h in hs)

        for _ in range(400):
            best, bs = None, score(chunks)
            for k in range(len(chunks)):
                for j in (k + 1, k - 1):
                    if not (0 <= j < len(chunks)) or chunks[k] <= 1:
                        continue
                    t = list(chunks)
                    t[k] -= 1
                    t[j] += 1
                    if fits(t) and score(t) < bs:
                        best, bs = t, score(t)
            if best is None:
                break
            chunks = best
        split[day] = chunks
        print("  %s 高さ%d 見出し%d 表頭%d 行%d → %s" % (day, sh, head, thead, len(rs), chunks))
    json.dump(split, open(os.path.join(ROOT, "tools", "pdf_split.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_shotlist_pdf.py")],
                   capture_output=True)
    print("書き出し: tools/pdf_split.json ／ pdf/kouban.html を組み直しました")

main()
