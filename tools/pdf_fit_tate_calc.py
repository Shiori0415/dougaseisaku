# -*- coding: utf-8 -*-
"""縦組み（1日1ページ）の縮小率を、実測でそろえる"""
import json, os, re, subprocess, sys
SP = os.path.dirname(os.path.abspath(__file__))
ROOT = "/home/user/dougaseisaku"
W, H = 718, 1047          # A4縦 210×297mm − 余白10mm ＝ 190×277mm
JS = ("<script>window.addEventListener('load',function(){var o=[];"
      "document.querySelectorAll('.page').forEach(function(el,i){"
      "var f=el.querySelector('.fit');"
      "o.push(i+'|'+(f?f.dataset.f:'')+'|'+Math.round(el.getBoundingClientRect().height));});"
      "document.title='M '+o.join(' ');});</script>")

def build(scale):
    json.dump(scale, open(os.path.join(ROOT, "tools", "pdf_scale.json"), "w",
                          encoding="utf-8"), ensure_ascii=False)
    e = dict(os.environ, KOUBAN_TATE="1")
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_shotlist_pdf.py")],
                   env=e, capture_output=True)

def measure():
    s = open(os.path.join(ROOT, "pdf", "kouban_tate.html"), encoding="utf-8").read()
    open(os.path.join(SP, "meas_t.html"), "w", encoding="utf-8").write(
        s.replace("</style>", "</style>" + JS, 1))
    out = subprocess.run(["/opt/pw-browsers/chromium", "--headless", "--disable-gpu",
        "--no-sandbox", "--window-size=%d,%d" % (W, H), "--virtual-time-budget=5000",
        "--dump-dom", "file://%s/meas_t.html" % SP], capture_output=True, text=True).stdout
    m = re.search(r"<title>M (.*?)</title>", out, re.S)
    d = {}
    for t in m.group(1).split():
        i, day, h = t.split("|")
        if day:
            d[day] = int(h)
        else:
            print("  枠外 高さ %s" % h)
    return d

scale = {}
for it in range(6):
    build(scale)
    hs = measure()
    print("  %d回目 %s" % (it + 1, {k: v for k, v in sorted(hs.items())}))
    done = True
    for day, h in hs.items():
        v = scale.get(day, 1.0)
        if h > H:
            scale[day] = round(v * (H - 6) / h, 4)
            done = False
        elif h < H - 40 and v < 0.999:
            scale[day] = round(min(1.0, v * (H - 20) / h), 4)
            done = False
    if done:
        break
print("  縮小率:", scale)
build(scale)
