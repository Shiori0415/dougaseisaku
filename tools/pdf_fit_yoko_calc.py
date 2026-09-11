# -*- coding: utf-8 -*-
"""横A4で、1日を1枚に収める。収まらない日だけ2枚に分ける。
   実行: python3 tools/pdf_fit_yoko_calc.py
   → tools/pdf_scale_yoko.json と tools/pdf_split.json を書き出し、pdf/kouban.html を組み直す"""
import json, os, re, subprocess, sys
DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(DIR, "..")
W, H = 1031, 707          # A4横 297×210mm − 余白 ＝ 273×187mm
FLOOR = float(os.environ.get("KOUBAN_FLOOR", "0.80"))              # これより小さくすると読めない
CONT = 46                 # 「つづき」の見出しぶん
JS = ("<script>window.addEventListener('load',function(){var o=[];"
      "document.querySelectorAll('.page').forEach(function(el,i){"
      "var t=el.querySelector('table[data-t]');"
      "o.push('S|'+i+'|'+(t?t.dataset.t:'')+'|'+Math.round(el.getBoundingClientRect().height)"
      "+'|'+(t?Math.round(t.getBoundingClientRect().height):0));});"
      "document.querySelectorAll('tr[data-r]').forEach(function(tr){"
      "o.push('R|'+tr.dataset.r+'|'+Math.round(tr.getBoundingClientRect().height));});"
      "document.title='M '+o.join(' ');});</script>")


def write(name, obj):
    json.dump(obj, open(os.path.join(DIR, name), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


def build():
    subprocess.run([sys.executable, os.path.join(DIR, "build_shotlist_pdf.py")],
                   capture_output=True)


def measure():
    s = open(os.path.join(ROOT, "pdf", "kouban.html"), encoding="utf-8").read()
    tmp = os.path.join(ROOT, "pdf", "_meas.html")
    open(tmp, "w", encoding="utf-8").write(s.replace("</style>", "</style>" + JS, 1))
    out = subprocess.run(["/opt/pw-browsers/chromium", "--headless", "--disable-gpu",
        "--no-sandbox", "--window-size=%d,%d" % (W, H), "--virtual-time-budget=5000",
        "--dump-dom", "file://" + os.path.abspath(tmp)], capture_output=True, text=True).stdout
    os.remove(tmp)
    toks = re.search(r"<title>M (.*?)</title>", out, re.S).group(1).split()
    sec, rows = [], {}
    for t in toks:
        p = t.split("|")
        if p[0] == "S":
            sec.append((p[2], int(p[3]), int(p[4])))
        else:
            rows.setdefault(p[1], []).append((int(p[2]), int(p[3])))
    return sec, rows


def chunks_for(rs, head, thead, npage):
    """npage 枚に分ける。収まらなければ None"""
    def hs(ch):
        o, i = [], 0
        for k, n in enumerate(ch):
            o.append((head if k == 0 else CONT) + thead + sum(rs[i:i + n]))
            i += n
        return o

    def fits(ch):
        return len(ch) == npage and all(n > 0 for n in ch) and max(hs(ch)) <= H

    if npage == 1:
        ch = [len(rs)]
        return ch if fits(ch) else None
    ch, cur, used = [], 0, head + thead
    for h in rs:
        if cur and used + h > H:
            ch.append(cur)
            cur, used = 0, CONT + thead
        cur += 1
        used += h
    ch.append(cur)
    if len(ch) > npage:
        return None
    while len(ch) < npage:                       # 足りなければ後ろを割る
        k = max(range(len(ch)), key=lambda j: ch[j])
        if ch[k] < 2:
            return None
        ch = ch[:k] + [ch[k] - ch[k] // 2, ch[k] // 2] + ch[k + 1:]
    for _ in range(400):
        best, bs = None, None
        a = sum(hs(ch)) / len(ch)
        cs = sum((h - a) ** 2 for h in hs(ch))
        for k in range(len(ch)):
            for j in (k + 1, k - 1):
                if not (0 <= j < len(ch)) or ch[k] <= 1:
                    continue
                t2 = list(ch)
                t2[k] -= 1
                t2[j] += 1
                if not fits(t2):
                    continue
                a2 = sum(hs(t2)) / len(t2)
                c2 = sum((h - a2) ** 2 for h in hs(t2))
                if c2 < cs and (bs is None or c2 < bs):
                    best, bs = t2, c2
        if best is None:
            break
        ch = best
    return ch if fits(ch) else None


def main():
    scale, split = {}, {}
    write("pdf_scale_yoko.json", scale)
    write("pdf_split.json", split)
    build()
    # ① 1枚に収まるところまで縮める（下限 FLOOR）
    for _ in range(10):
        sec, _ = measure()
        done = True
        for day, sh, th in sec:
            if not day:
                continue
            v = float(scale.get(day, 1.0))
            if sh <= H or v <= FLOOR + 1e-9:
                continue
            scale[day] = round(max(FLOOR, v * (H - 6) / sh), 4)
            done = False
        if done:
            break
        write("pdf_scale_yoko.json", scale)
        build()
    # ② それでも入らない日は、縮めずに2枚に分ける
    sec, _ = measure()
    two = [day for day, sh, th in sec if day and sh > H]
    for day in two:
        scale.pop(day, None)
    for day, sh, th in sec:
        if day and day not in two:
            print("  %s ── 1枚（文字 %.0f%%）" % (day, scale.get(day, 1.0) * 100))
    if two:
        write("pdf_scale_yoko.json", scale)
        build()
        sec, rows = measure()
        need = {}
        for day, sh, th in sec:
            if day not in two:
                continue
            rs = [h for _, h in sorted(rows[day])]
            head, thead = sh - th, th - sum(rs)
            ch = chunks_for(rs, head, thead, 2)
            if ch:
                split[day] = ch
                print("  %s ── 2枚 %s（文字 100%%）" % (day, ch))
            else:
                need[day] = round(max(FLOOR, (2 * H - CONT - 24) / sh), 4)
        if need:
            scale.update(need)
            write("pdf_scale_yoko.json", scale)
            build()
            sec, rows = measure()
            for day, sh, th in sec:
                if day not in need:
                    continue
                rs = [h for _, h in sorted(rows[day])]
                head, thead = sh - th, th - sum(rs)
                ch = chunks_for(rs, head, thead, 2) or [len(rs) // 2, len(rs) - len(rs) // 2]
                split[day] = ch
                print("  %s ── 2枚 %s（文字 %.0f%%）" % (day, ch, scale[day] * 100))
    write("pdf_scale_yoko.json", scale)
    write("pdf_split.json", split)
    build()
    print("書き出し: pdf_scale_yoko.json ／ pdf_split.json")


main()
