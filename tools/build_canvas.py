# -*- coding: utf-8 -*-
"""絵コンテのデザインキャンバス用に、1本＝1シートの .dc.html を書き出す。
   実行: python3 tools/build_canvas.py <出力ディレクトリ>

   ・1シートに「企画の要約（上部）＋絵コンテ12コマ」を収める
   ・ワンシーン3枚、4シーンを2×2に並べる
   ・コマの縦横は動画に合わせる（Instagram/EC向けの①②③④⑦⑧は9:16、
     コーポレート/商談向けの⑤⑥は16:9）
   ・この1本で言うこと／テロップ／追加ブロックは載せない（絵コンテ主体にするため）
"""
import json, os, re, sys, html, shutil
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ORIENT = {"01": "v", "02": "v", "03": "v", "04": "v",
          "05": "h", "06": "h", "07": "v", "08": "v"}
SLUG = {"01": "Main", "02": "Video02", "03": "Video03", "04": "Video04",
        "05": "Video05", "06": "Video06", "07": "Video07", "08": "Video08"}

# 縦型シート／横型シートの寸法（CSS px・96dpiで印刷1枚）
SPEC = {
    "v": dict(page_w=1180, page_h=1060, cell_w=170, cell_h=302),
    "h": dict(page_w=1540, page_h=760,  cell_w=230, cell_h=129),
}
MARGIN, CAP_H, LABEL_H, SHOT_GAP, BLOCK_GAP_X, BLOCK_GAP_Y = 40, 46, 28, 10, 44, 30

INK, MUTED, FAINT = "#15191c", "#5b6266", "#8a8f92"
GOLD, LINE, PAPER, FRAME_BG = "#a8672a", "#ded9d0", "#fbfaf7", "#0f0f0f"


def strip_tags(s):
    """絵コンテの本文は簡易HTMLなので、キャンバスでは太字だけ残して他は落とす"""
    if not s:
        return ""
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"</?span[^>]*>", "", s)
    s = re.sub(r"<a\s+href=\"([^\"]+)\">(.*?)</a>", r"\2", s)
    return s


def plain(s):
    return re.sub(r"<[^>]+>", "", strip_tags(s)).strip()


def plan_summary(page):
    """企画の文章から、上部に置く2〜3文の要約を作る"""
    text = plain(page["plan"])
    text = re.sub(r"\s+", " ", text)
    parts = [p for p in re.split(r"(?<=。)", text) if p.strip()]
    out, n = [], 0
    for p in parts:
        if n + len(p) > 170 and out:
            break
        out.append(p)
        n += len(p)
    return "".join(out)


def esc(s):
    return html.escape(s, quote=True)


def rich(s):
    """<b> だけ通して、それ以外はエスケープする"""
    s = strip_tags(s)
    parts = re.split(r"(</?b>)", s)
    buf, bold = [], 0
    for t in parts:
        if t == "<b>":
            bold += 1
            buf.append('<span style="font-weight: 700">')
        elif t == "</b>":
            if bold:
                bold -= 1
                buf.append("</span>")
        else:
            buf.append(html.escape(t))
    buf.append("</span>" * bold)
    return "".join(buf)


def frame(shot, sp, imgmap):
    photo, cap = imgmap.get(id(shot)) or shot[0], shot[1]
    w, h = sp["cell_w"], sp["cell_h"]
    if cap == "―":
        inner = f'<div style="width: {w}px; height: {h}px"></div>'
        return f'<div style="display: flex; flex-direction: column; gap: 6px; width: {w}px">{inner}</div>'
    if photo:
        box = (f'<div style="width: {w}px; height: {h}px; background: {FRAME_BG}; '
               f'border: 1px solid {LINE}; overflow: hidden; display: flex; '
               f'align-items: center; justify-content: center">'
               f'<img src="{esc(photo)}.jpg" alt="" style="max-width: 100%; max-height: 100%; '
               f'object-fit: contain; display: block" /></div>')
    else:
        box = (f'<div style="width: {w}px; height: {h}px; background: {PAPER}; '
               f'border: 1px dashed #c9c2b6; display: flex; align-items: center; '
               f'justify-content: center; color: #b3a894; font-size: 11px; text-align: center">'
               f'撮影して<br />差し替え</div>')
    cap_html = (f'<div style="width: {w}px; height: {CAP_H}px; font-size: 10.5px; '
                f'line-height: 1.45; color: #3a3226; overflow: hidden">{rich(cap)}</div>')
    return (f'<div style="display: flex; flex-direction: column; gap: 6px; width: {w}px">'
            f'{box}{cap_html}</div>')


def scene_block(row, sp, imgmap):
    name, time, shots = row[0], row[1], row[2]
    frames = "".join(frame(s, sp, imgmap) for s in shots)
    label = (f'<div style="display: flex; align-items: baseline; gap: 10px; height: {LABEL_H}px">'
             f'<div style="font-size: 14px; font-weight: 700; color: {INK}">{esc(name)}</div>'
             f'<div style="font-size: 11px; color: {MUTED}">{esc(time)}</div></div>')
    return (f'<div style="display: flex; flex-direction: column; gap: 4px">{label}'
            f'<div style="display: flex; gap: {SHOT_GAP}px">{frames}</div></div>')


def artboard(page, imgmap):
    o = ORIENT[page["no"]]
    sp = SPEC[o]
    blocks = "".join(scene_block(r, sp, imgmap) for r in page["rows"])
    ref = plain(page["ref"]).replace("参考動画＝", "")
    orient_label = "縦型 9:16" if o == "v" else "横型 16:9"

    header = f'''<div style="display: flex; flex-direction: column; gap: 10px; border-bottom: 2px solid {INK}; padding-bottom: 14px">
      <div style="display: flex; align-items: baseline; gap: 14px">
        <div style="font-size: 12px; font-weight: 700; color: {GOLD}; letter-spacing: 0.12em">{esc(page["no"])}</div>
        <div style="font-size: 26px; font-weight: 700; color: {INK}; letter-spacing: -0.01em">{esc(page["jp"])}</div>
        <div style="font-size: 13px; color: {FAINT}; letter-spacing: 0.06em">{esc(page["en"])}</div>
        <div style="margin-left: auto; font-size: 11px; color: {GOLD}; border: 1px solid {LINE}; border-radius: 20px; padding: 3px 12px">{orient_label}</div>
      </div>
      <div style="display: flex; gap: 20px; font-size: 11.5px; color: {MUTED}">
        <div style="font-weight: 700; color: {INK}">{esc(plain(page["meta_len"]))}</div>
        <div>{esc(plain(page["meta_target"]))}</div>
      </div>
      <div style="font-size: 12.5px; line-height: 1.7; color: {INK}; max-width: 900px">{esc(plan_summary(page))}</div>
      <div style="font-size: 10.5px; color: {FAINT}">参考動画：{esc(ref)}</div>
    </div>'''

    return f'''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
  <style>
    body {{ margin: 0; background: #ffffff;
      font-family: 'Zen Kaku Gothic New', 'Hiragino Sans', 'Yu Gothic', sans-serif; }}
    a {{ color: {GOLD}; }} a:hover {{ color: #7d4c1e; }}
  </style>
</helmet>
<div style="width: {sp["page_w"]}px; height: {sp["page_h"]}px; background: #ffffff; padding: {MARGIN}px; box-sizing: border-box; display: flex; flex-direction: column; gap: 20px">
  {header}
  <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: {BLOCK_GAP_Y}px {BLOCK_GAP_X}px; justify-items: start">
    {blocks}
  </div>
  <div style="margin-top: auto; display: flex; justify-content: space-between; font-size: 10px; color: {FAINT}">
    <div>BROOKLYN MUSEUM ／ 向島工房　動画制作</div>
    <div>ワンシーン3枚 ／ 全12コマ</div>
  </div>
</div>
</x-dc>
</body>
</html>
'''


def export_images(data, outdir):
    """コマごとに p<番号>_s<シーン>_<ショット>.jpg で書き出す（キャンバスはASCII名のみ）"""
    imgdir = os.path.join(outdir, "img")
    if os.path.isdir(imgdir):
        shutil.rmtree(imgdir)
    os.makedirs(imgdir)
    imgmap, missing = {}, []
    for page in data["pages"]:
        sp = SPEC[ORIENT[page["no"]]]
        for si, row in enumerate(page["rows"], start=1):
            for hi, shot in enumerate(row[2], start=1):
                if not shot[0]:
                    continue
                src = os.path.join(ROOT, "assets", "ref4", shot[0] + ".jpg")
                if not os.path.exists(src):
                    missing.append(shot[0])
                    continue
                name = f"p{page['no']}_s{si}_{hi}.jpg"
                im = Image.open(src).convert("RGB")
                im.thumbnail((max(sp["cell_w"], sp["cell_h"]) * 2, max(sp["cell_w"], sp["cell_h"]) * 2))
                im.save(os.path.join(imgdir, name), quality=66, optimize=True)
                imgmap[id(shot)] = name[:-4]
    if missing:
        print("画像が見つかりません:", ", ".join(missing))
    total = sum(os.path.getsize(os.path.join(imgdir, f)) for f in os.listdir(imgdir))
    print(f"画像 {len(imgmap)}枚 / {total // 1024} KB")
    return imgmap


def main(outdir):
    data = json.load(open(os.path.join(ROOT, "tools", "deck_data.json"), encoding="utf-8"))
    os.makedirs(outdir, exist_ok=True)
    imgmap = export_images(data, outdir)
    boards, x, y, row_h = [], 0, 0, 0
    for i, page in enumerate(data["pages"]):
        name = SLUG[page["no"]]
        with open(os.path.join(outdir, f"{name}.dc.html"), "w", encoding="utf-8") as f:
            f.write(artboard(page, imgmap))
        sp = SPEC[ORIENT[page["no"]]]
        if i % 3 == 0 and i:
            x, y = 0, y + row_h + 160
            row_h = 0
        boards.append({"file": f"{name}.dc.html", "x": x, "y": y,
                       "w": sp["page_w"], "h": sp["page_h"]})
        x += sp["page_w"] + 120
        row_h = max(row_h, sp["page_h"])
    canvas = {"artboards": boards, "launch": {"view": "canvas"}}
    with open(os.path.join(outdir, "canvas.json"), "w", encoding="utf-8") as f:
        json.dump(canvas, f, ensure_ascii=False, indent=2)
    print(f"{len(boards)}枚のシートと canvas.json を書き出しました → {outdir}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "canvas_out")
