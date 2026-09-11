# -*- coding: utf-8 -*-
"""縦A4で、文字を縮めずに1日を何枚に分ければ収まるかを測る"""
import json, os, re, subprocess, sys
SP = os.path.dirname(os.path.abspath(__file__))
ROOT = "/home/user/dougaseisaku"
W, H = 718, 1047
CONT_HEAD = 46
JS = ("<script>window.addEventListener('load',function(){var o=[];"
      "document.querySelectorAll('.page').forEach(function(el,i){"
      "var t=el.querySelector('table[data-t]');"
      "o.push('S|'+i+'|'+(t?t.dataset.t:'')+'|'+Math.round(el.getBoundingClientRect().height)"
      "+'|'+(t?Math.round(t.getBoundingClientRect().height):0));});"
      "document.querySelectorAll('tr[data-r]').forEach(function(tr){"
      "o.push('R|'+tr.dataset.r+'|'+Math.round(tr.getBoundingClientRect().height));});"
      "document.title='M '+o.join(' ');});</script>")

def build():
    e = dict(os.environ, KOUBAN_TATE="1")
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_shotlist_pdf.py")],
                   env=e, capture_output=True)

for f in ("pdf_scale.json", "pdf_split_tate.json"):
    q = os.path.join(ROOT, "tools", f)
    if os.path.exists(q):
        os.remove(q)
build()
s = open(os.path.join(ROOT, "pdf", "kouban_tate.html"), encoding="utf-8").read()
open(os.path.join(SP, "meas_t.html"), "w", encoding="utf-8").write(
    s.replace("</style>", "</style>" + JS, 1))
out = subprocess.run(["/opt/pw-browsers/chromium", "--headless", "--disable-gpu",
    "--no-sandbox", "--window-size=%d,%d" % (W, H), "--virtual-time-budget=5000",
    "--dump-dom", "file://%s/meas_t.html" % SP], capture_output=True, text=True).stdout
toks = re.search(r"<title>M (.*?)</title>", out, re.S).group(1).split()
sec, rows = [], {}
for t in toks:
    p = t.split("|")
    if p[0] == "S":
        sec.append((p[2], int(p[3]), int(p[4])))
    else:
        rows.setdefault(p[1], []).append((int(p[2]), int(p[3])))
split = {}
for day, sh, th in sec:
    if not day:
        print("  枠外 高さ %d" % sh)
        continue
    rs = [h for _, h in sorted(rows[day])]
    head, thead = sh - th, th - sum(rs)

    def fits(ch):
        i = 0
        for k, n in enumerate(ch):
            if n <= 0:
                return False
            if (head if k == 0 else CONT_HEAD) + thead + sum(rs[i:i + n]) > H:
                return False
            i += n
        return i == len(rs)

    def hs(ch):
        o, i = [], 0
        for k, n in enumerate(ch):
            o.append((head if k == 0 else CONT_HEAD) + thead + sum(rs[i:i + n]))
            i += n
        return o
    ch, cur, used = [], 0, head + thead
    for h in rs:
        if cur and used + h > H:
            ch.append(cur); cur, used = 0, CONT_HEAD + thead
        cur += 1; used += h
    ch.append(cur)
    for _ in range(400):
        best, bs = None, None
        a = sum(hs(ch)) / len(ch)
        cs = sum((h - a) ** 2 for h in hs(ch))
        for k in range(len(ch)):
            for j in (k + 1, k - 1):
                if not (0 <= j < len(ch)) or ch[k] <= 1:
                    continue
                t2 = list(ch); t2[k] -= 1; t2[j] += 1
                if not fits(t2):
                    continue
                a2 = sum(hs(t2)) / len(t2)
                c2 = sum((h - a2) ** 2 for h in hs(t2))
                if c2 < cs and (bs is None or c2 < bs):
                    best, bs = t2, c2
        if best is None:
            break
        ch = best
    split[day] = ch
    print("  %s 高さ%d 行%d → %s" % (day, sh, len(rs), ch))
json.dump(split, open(os.path.join(ROOT, "tools", "pdf_split_tate.json"), "w",
                      encoding="utf-8"), ensure_ascii=False, indent=1)
build()
print("書き出し: tools/pdf_split_tate.json")
