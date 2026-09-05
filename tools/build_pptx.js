// Googleスライドで編集できる .pptx を tools/deck_data.json から生成する。
// 実行: node tools/build_pptx.js   (プロジェクト直下に node_modules/pptxgenjs が必要)
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const ROOT = path.join(__dirname, "..");
const DATA = JSON.parse(fs.readFileSync(path.join(__dirname, "deck_data.json"), "utf-8"));
const OUT = path.join(ROOT, "pdf", "00_動画8本_企画と絵コンテ.pptx");
const IMG_DIR = path.join(ROOT, "assets", "ref4");

// pptxgenjsのsizing:{type:"cover"}は実画像の縦横比を自分では読み取らず、箱のサイズをそのまま
// 画像サイズとして扱ってしまうため（縦横比が常に1:1と誤認され、srcRectが0になり、結果的に画像が
// 箱いっぱいに引き伸ばされる＝ご指摘の「画像が伸びきっている」の原因）。JPEGのSOFセグメントから
// 実際のピクセル寸法を読み、addImageのw/hに渡して正しい縦横比でクロップさせる。
const imgSizeCache = {};
function jpegSize(filePath) {
  const buf = fs.readFileSync(filePath);
  let i = 2;
  while (i < buf.length - 9) {
    if (buf[i] !== 0xff) break;
    const marker = buf[i + 1];
    if (marker >= 0xc0 && marker <= 0xc3) {
      return { width: buf.readUInt16BE(i + 7), height: buf.readUInt16BE(i + 5) };
    }
    i += 2 + buf.readUInt16BE(i + 2);
  }
  return null;
}
function getImgSize(imgPath) {
  if (!(imgPath in imgSizeCache)) imgSizeCache[imgPath] = jpegSize(imgPath) || { width: 1, height: 1 };
  return imgSizeCache[imgPath];
}

// ---------- 色 ----------
const INK = "1A1A1A";
const MUTED = "6B5F4D";
const FAINT = "8A7A63";
const GOLD = "A8763E";
const LINE = "E6DED0";
const CREAM = "FDFCF9";
const DASH = "C9BDA6";

// ---------- 簡易HTMLパーサ（<b> <br> <span style="color:#..."> <a href="..."> のみ対応） ----------
const TAG_RE = /<br\s*\/?>|<\/?b(?:\s+style=["']color:#[0-9A-Fa-f]{6}["'])?>|<\/?span(?:\s+style=["']color:#[0-9A-Fa-f]{6}["'])?>|<a\s+href=["'][^"']+["']>|<\/a>/gi;

function decode(s) {
  return s.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&nbsp;/g, " ");
}

function parseRich(html, baseOpts) {
  baseOpts = baseOpts || {};
  if (!html) return [];
  const runs = [];
  const stack = [];
  let last = 0;
  let m;
  TAG_RE.lastIndex = 0;
  const flush = (text) => {
    text = decode(text);
    if (!text) return;
    const opts = Object.assign({}, baseOpts);
    if (stack.some((s) => s.kind === "b")) opts.bold = true;
    for (let i = stack.length - 1; i >= 0; i--) {
      if (stack[i].color) { opts.color = stack[i].color; break; }
    }
    for (let i = stack.length - 1; i >= 0; i--) {
      if (stack[i].kind === "a") { opts.hyperlink = { url: stack[i].url }; break; }
    }
    runs.push({ text, options: opts });
  };
  while ((m = TAG_RE.exec(html))) {
    flush(html.slice(last, m.index));
    last = TAG_RE.lastIndex;
    const raw = m[0];
    const tag = raw.toLowerCase();
    const colorM = /color:#([0-9a-f]{6})/i.exec(tag);
    if (tag.startsWith("<br")) {
      runs.push({ text: "", options: Object.assign({}, baseOpts, { breakLine: true }) });
    } else if (tag.startsWith("<b")) {
      stack.push({ kind: "b", color: colorM ? "#" + colorM[1] : undefined });
    } else if (tag === "</b>") {
      for (let i = stack.length - 1; i >= 0; i--) if (stack[i].kind === "b") { stack.splice(i, 1); break; }
    } else if (tag.startsWith("<span")) {
      stack.push({ kind: "span", color: colorM ? "#" + colorM[1] : undefined });
    } else if (tag === "</span>") {
      for (let i = stack.length - 1; i >= 0; i--) if (stack[i].kind === "span") { stack.splice(i, 1); break; }
    } else if (tag.startsWith("<a")) {
      const url = /href=["']([^"']+)["']/i.exec(raw)[1];
      stack.push({ kind: "a", url });
    } else if (tag === "</a>") {
      for (let i = stack.length - 1; i >= 0; i--) if (stack[i].kind === "a") { stack.splice(i, 1); break; }
    }
  }
  flush(html.slice(last));
  // pptxgenjs corrupts on options.color without '#'? -> strip '#'
  runs.forEach((r) => { if (r.options.color) r.options.color = r.options.color.replace("#", ""); });
  return runs;
}

function plainText(html) {
  return parseRich(html).map((r) => r.text + (r.options.breakLine ? "\n" : "")).join("");
}

// 日本語（全角）と半角の文字幅をざっくり見積もって行数を出す
// すべてのテキストボックスは margin:0 で描画するので、見積もりも「箱の幅ほぼそのまま」で計算する。
// フォント計量の誤差を吸収するため、行数計算後に SAFETY 分だけ高さを底上げする。
const SAFETY = 1.14;
function estimateHeight(html, widthIn, fontPt, opts) {
  opts = opts || {};
  const lineMult = opts.lineMult || 1.32;
  const pad = opts.pad != null ? opts.pad : 0.04;
  const text = plainText(html);
  const paras = text.split("\n");
  let lines = 0;
  const wFull = (fontPt / 72) * 1.02;
  const wHalf = (fontPt / 72) * 0.58;
  for (const p of paras) {
    if (p === "") { lines += 1; continue; }
    let w = 0, l = 1;
    for (const ch of p) {
      const cw = ch.charCodeAt(0) > 0x2000 ? wFull : wHalf;
      if (w + cw > widthIn - pad * 2) { l++; w = cw; } else { w += cw; }
    }
    lines += l;
  }
  return (lines * (fontPt / 72) * lineMult) * SAFETY + pad * 2;
}

// ---------- キャンバス ----------
const SW = 13.333, SH = 7.5;
const MARGIN = 0.45;
// 縦型（Instagram）動画の絵コンテなので、1本＝1スライドではなく1本＝2スライド
// （シーン2つずつ）に分け、写真1枚あたりの表示を大きく・縦長寄りにする。
// シーン数は本によって違う（②は6シーン）ので、2シーンごとに1枚として数える
const SCENES_PER_SLIDE = 2;
const TOTAL_SLIDES = 2 + DATA.pages.reduce(
  (n, p) => n + Math.ceil(p.rows.length / SCENES_PER_SLIDE), 0);

const pres = new pptxgen();
pres.defineLayout({ name: "WIDE169", width: SW, height: SH });
pres.layout = "WIDE169";
pres.theme = { headFontFace: "Meiryo", bodyFontFace: "Meiryo" };

function footerAndPage(slide, footer, pn, total) {
  slide.addText(footer, { x: MARGIN, y: SH - 0.42, w: 5, h: 0.3, fontFace: "Meiryo", fontSize: 8, color: FAINT, margin: 0 });
  slide.addText(`${pn} / ${total}`, { x: SW - MARGIN - 1.5, y: SH - 0.42, w: 1.5, h: 0.3, align: "right", fontFace: "Meiryo", fontSize: 8, color: FAINT, margin: 0 });
}

// ================= 表紙 =================
{
  const slide = pres.addSlide();
  slide.background = { color: "FFFFFF" };
  const c = DATA.cover;
  slide.addText(c.eyebrow, { x: MARGIN, y: 1.5, w: 8, h: 0.3, fontFace: "Meiryo", fontSize: 10, color: FAINT, charSpacing: 2, margin: 0 });
  slide.addShape("line", { x: MARGIN, y: 1.9, w: 1.5, h: 0, line: { color: INK, width: 2.2 } });
  slide.addText(c.title_jp_plain, { x: MARGIN, y: 2.1, w: 10, h: 1.6, fontFace: "Meiryo", fontSize: 40, bold: true, color: INK, lineSpacingMultiple: 1.25, margin: 0 });
  slide.addText(c.subtitle_en, { x: MARGIN, y: 3.75, w: 10, h: 0.5, fontFace: "Meiryo", fontSize: 15, color: MUTED, charSpacing: 1.5, margin: 0 });

  slide.addShape("line", { x: MARGIN, y: 6.0, w: SW - MARGIN * 2, h: 0, line: { color: LINE, width: 1 } });
  slide.addText(c.meta_lines.join("\n"), { x: MARGIN, y: 6.14, w: 9, h: 0.85, fontFace: "Meiryo", fontSize: 11, color: MUTED, lineSpacingMultiple: 1.5, margin: 0 });
  footerAndPage(slide, c.footer, 1, TOTAL_SLIDES);
}

// ================= 目次 =================
{
  const slide = pres.addSlide();
  const c = DATA.cover;
  slide.addText("目 次　CONTENTS", { x: MARGIN, y: 0.4, w: 8, h: 0.3, fontFace: "Meiryo", fontSize: 10, color: FAINT, charSpacing: 2, margin: 0 });
  slide.addText("8本の動画", { x: MARGIN, y: 0.68, w: 8, h: 0.55, fontFace: "Meiryo", fontSize: 24, bold: true, color: INK, margin: 0 });
  slide.addText(c.toc_intro, { x: MARGIN, y: 1.28, w: SW - MARGIN * 2, h: 0.4, fontFace: "Meiryo", fontSize: 10, color: MUTED, margin: 0 });

  const colW = [0.55, 3.3, 1.55, 2.85, 4.2];
  const header = ["#", "タイトル", "尺・本数", "届ける相手", "参考動画"].map((t, i) => ({
    text: t, options: { fontFace: "Meiryo", fontSize: 9, color: FAINT, bold: false, fill: { color: "FFFFFF" }, border: { pt: 0 } },
  }));
  const rows = [header];
  DATA.toc.forEach((r) => {
    rows.push([
      { text: r.n, options: { fontFace: "Meiryo", fontSize: 12, bold: true, color: GOLD, valign: "top" } },
      { text: [{ text: r.jp, options: { fontFace: "Meiryo", fontSize: 12, bold: true, color: INK, breakLine: true } },
                { text: r.en, options: { fontFace: "Meiryo", fontSize: 9, color: FAINT } }], options: { valign: "top" } },
      { text: r.len, options: { fontFace: "Meiryo", fontSize: 10, color: MUTED, valign: "top" } },
      { text: r.target, options: { fontFace: "Meiryo", fontSize: 10, color: INK, valign: "top" } },
      { text: parseRich(r.ref_html, { fontFace: "Meiryo", fontSize: 9, color: FAINT }), options: { valign: "top" } },
    ]);
  });
  slide.addTable(rows, {
    x: MARGIN, y: 1.85, w: SW - MARGIN * 2, colW,
    border: { type: "solid", color: LINE, pt: 0.75 },
    autoPage: false, valign: "top",
    margin: [0.06, 0.08, 0.06, 0.08],
    rowH: [0.32, 0.62, 0.62, 0.62, 0.62, 0.62, 0.62, 0.62, 0.62],
  });
  footerAndPage(slide, c.footer, 2, TOTAL_SLIDES);
}

// ================= 8本の各ページ（用紙は16:9のまま。1本＝2スライド、シーン2つずつ） =================
// 絵コンテの写真はInstagramのリールと同じ9:16の縦長にする。そのぶん横に細くなるので、
// シーンを縦に積まず「シーン2つを左右に並べ、写真6枚を一列」にして、1枚あたりを大きく取る。
// 文章は写真の上に2段組で置く（左＝企画／右＝この1本で言うこと・テロップ・追加）。
const HEADER_TOP = 0.35;
const TITLE_W = 6.4;
const RULE_Y = 1.40;
const BODY_Y = 1.54;
const CONTENT_W = SW - MARGIN * 2;
const GRID_BOTTOM = SH - 0.52;

const TEXT_COL_GAP = 0.5;
const TEXT_COL_W = (CONTENT_W - TEXT_COL_GAP) / 2;

const LABEL_H = 0.28;          // シーン名（S1 支度 0-4秒）
const CAP_H = 0.62;            // 写真の下のキャプション
const SHOT_GAP = 0.10;         // 同じシーン内の写真どうしの間
const GROUP_GAP = 0.45;        // シーンとシーンの間
const REEL = 9 / 16;           // 写真の縦横比（リールと同じ）
// 横幅から決まる写真の上限。6枚＋余白が用紙に収まる幅を超えないようにする。
const MAX_PHOTO_W = (CONTENT_W - SHOT_GAP * 4 - GROUP_GAP) / 6;
const MAX_PHOTO_H = MAX_PHOTO_W / REEL;
const MIN_PHOTO_H = 2.25;
// 文章に使ってよい高さの上限。これを超える場合はフォントを縮めて写真の場所を確保する。
const TEXT_MAX_H = GRID_BOTTOM - (LABEL_H + MIN_PHOTO_H + CAP_H) - BODY_Y - 0.22;

// 文章は2段組。左段＝企画、右段＝この1本で言うこと／テロップ／追加ブロック。
function textColumns(d) {
  const right = [{ kind: "text", label: "こ の 1 本 で 言 う こ と", html: d.says, fontPt: 9.5 }];
  if (d.telop_jp) right.push({ kind: "telop" });
  if (d.extra) right.push({ kind: "text", label: d.extra[0], html: d.extra[1], fontPt: 8.5 });
  return [[{ kind: "text", label: "企　画", html: d.plan, fontPt: 9.5 }], right];
}

function columnHeight(d, blocks, scale) {
  const gap = Math.max(0.12, 0.18 * scale);
  let h = 0;
  for (const b of blocks) {
    if (b.kind === "telop") {
      const enH = d.telop_en ? estimateHeight(d.telop_en, TEXT_COL_W - 0.4, 9 * scale) : 0;
      const jpH = estimateHeight(d.telop_jp, TEXT_COL_W - 0.4, 14 * scale);
      h += 0.32 + jpH + (enH ? enH + 0.05 : 0) + 0.16 + gap;
    } else {
      h += estimateHeight(b.html, TEXT_COL_W, b.fontPt * scale) + 0.26 + gap;
    }
  }
  return h;
}

// 2段のうち高いほうが TEXT_MAX_H に収まる倍率を探す
function textBandHeight(d, scale) {
  const cols = textColumns(d);
  return Math.max(columnHeight(d, cols[0], scale), columnHeight(d, cols[1], scale));
}

// pptx内の通し番号（表紙1・目次2の次から）。data_pdf.py由来のd.pn/d.totalはPDF（1本＝1ページ）の
// ページ番号なので、1本＝2スライドになるpptxではここで別に数え直す。
let pageCounter = 3;

DATA.pages.forEach((d) => {
  let scale = 1.0;
  for (let s = 1.0; s >= 0.6; s -= 0.02) {
    scale = s;
    if (textBandHeight(d, s) <= TEXT_MAX_H) break;
  }
  const gap = Math.max(0.12, 0.18 * scale);

  // シーンを2つずつに分け、1本＝複数スライドにする（通常は4シーン→2スライド）
  const sceneChunks = [];
  for (let i = 0; i < d.rows.length; i += SCENES_PER_SLIDE) {
    sceneChunks.push(d.rows.slice(i, i + SCENES_PER_SLIDE));
  }

  sceneChunks.forEach((rowsChunk, partIdx) => {
    const slide = pres.addSlide();
    const partLabel = sceneChunks.length > 1 ? `${partIdx + 1} / ${sceneChunks.length}` : "";

    // ---- ヘッダー ----
    slide.addText(d.no, { x: MARGIN, y: HEADER_TOP, w: 0.55, h: 0.22, fontFace: "Meiryo", fontSize: 9, bold: true, color: GOLD, charSpacing: 2, margin: 0 });
    if (partLabel) {
      slide.addText(partLabel, { x: MARGIN + 0.62, y: HEADER_TOP, w: 1.0, h: 0.22, fontFace: "Meiryo", fontSize: 8, color: FAINT, margin: 0 });
    }
    slide.addText(d.jp, { x: MARGIN, y: HEADER_TOP + 0.22, w: TITLE_W, h: 0.44, fontFace: "Meiryo", fontSize: 22, bold: true, color: INK, valign: "top", margin: 0 });
    slide.addText(d.en, { x: MARGIN, y: HEADER_TOP + 0.68, w: TITLE_W, h: 0.28, fontFace: "Meiryo", fontSize: 11, color: FAINT, charSpacing: 1, margin: 0 });

    const metaW = SW - MARGIN - (MARGIN + TITLE_W + 0.2);
    const metaRuns = [
      { text: d.meta_len, options: { fontFace: "Meiryo", fontSize: 11, bold: true, color: INK, breakLine: true } },
      { text: d.meta_target, options: { fontFace: "Meiryo", fontSize: 8.5, color: MUTED, breakLine: true } },
    ].concat(parseRich(d.ref, { fontFace: "Meiryo", fontSize: 7.5, color: FAINT }));
    slide.addText(metaRuns, { x: SW - MARGIN - metaW, y: HEADER_TOP, w: metaW, h: 1.0, align: "right", valign: "top", lineSpacingMultiple: 1.32, margin: 0 });

    slide.addShape("line", { x: MARGIN, y: RULE_Y, w: CONTENT_W, h: 0, line: { color: INK, width: 1.5 } });

    // ---- 文章（2段組。両方のスライドに同じ内容を出す） ----
    const cols = textColumns(d);
    cols.forEach((blocks, ci) => {
      const cx = MARGIN + ci * (TEXT_COL_W + TEXT_COL_GAP);
      let y = BODY_Y;
      for (const b of blocks) {
        if (b.kind === "telop") {
          const fpJp = 14 * scale, fpEn = 9 * scale;
          const enH = d.telop_en ? estimateHeight(d.telop_en, TEXT_COL_W - 0.4, fpEn) : 0;
          const jpH = estimateHeight(d.telop_jp, TEXT_COL_W - 0.4, fpJp);
          const boxH = 0.32 + jpH + (enH ? enH + 0.05 : 0) + 0.16;
          slide.addShape("rect", { x: cx, y, w: TEXT_COL_W, h: boxH, fill: { color: INK }, line: { type: "none" } });
          slide.addText("テ ロ ッ プ", { x: cx + 0.18, y: y + 0.10, w: TEXT_COL_W - 0.36, h: 0.2, fontFace: "Meiryo", fontSize: 7, color: "C9B79A", charSpacing: 1.5, margin: 0 });
          slide.addText(d.telop_jp, { x: cx + 0.18, y: y + 0.32, w: TEXT_COL_W - 0.36, h: jpH, fontFace: "Meiryo", fontSize: fpJp, bold: true, color: "FFFFFF", lineSpacingMultiple: 1.3, valign: "top", margin: 0 });
          if (d.telop_en) {
            slide.addText(d.telop_en, { x: cx + 0.18, y: y + 0.32 + jpH + 0.05, w: TEXT_COL_W - 0.36, h: enH, fontFace: "Meiryo", fontSize: fpEn, color: "C9B79A", valign: "top", margin: 0 });
          }
          y += boxH + gap;
        } else {
          const fontPt = b.fontPt * scale;
          const h = estimateHeight(b.html, TEXT_COL_W, fontPt) + 0.26;
          slide.addText(b.label, { x: cx, y, w: TEXT_COL_W, h: 0.20, fontFace: "Meiryo", fontSize: 7.5, color: FAINT, charSpacing: 1.5, margin: 0 });
          slide.addText(parseRich(b.html, { fontFace: "Meiryo", fontSize: fontPt, color: INK }), {
            x: cx, y: y + 0.20, w: TEXT_COL_W, h: h - 0.20, fontFace: "Meiryo", fontSize: fontPt, color: INK, lineSpacingMultiple: 1.34, valign: "top", margin: 0,
          });
          y += h + gap;
        }
      }
    });

    // ---- 絵コンテ：シーン2つ分の写真6枚を、9:16の縦長で一列に並べる ----
    const gridTop = BODY_Y + textBandHeight(d, scale) + 0.22;
    const avail = GRID_BOTTOM - gridTop;
    const photoH = Math.max(MIN_PHOTO_H, Math.min(avail - LABEL_H - CAP_H, MAX_PHOTO_H));
    const photoW = photoH * REEL;
    const groupW = photoW * 3 + SHOT_GAP * 2;
    const totalW = groupW * SCENES_PER_SLIDE + GROUP_GAP;
    const gridX = MARGIN + (CONTENT_W - totalW) / 2;

    rowsChunk.forEach((row, ri) => {
      const [sceneName, sceneTime, shots] = row;
      const gx = gridX + ri * (groupW + GROUP_GAP);
      slide.addText(
        [
          { text: sceneName, options: { fontFace: "Meiryo", fontSize: 11.5, bold: true, color: INK } },
          { text: "　" + sceneTime, options: { fontFace: "Meiryo", fontSize: 9, color: MUTED } },
        ],
        { x: gx, y: gridTop, w: groupW, h: LABEL_H, valign: "top", margin: 0 }
      );
      const py = gridTop + LABEL_H;
      shots.forEach((shot, si) => {
        const [photo, cap] = shot;
        const sx = gx + si * (photoW + SHOT_GAP);
        if (cap === "―") return; // 使わないマス
        if (photo) {
          // pptxgenjsのsizing:{type:"contain"}はOOXMLのsrcRect+stretchで実装されており、
          // 画像が箱より縦長（幅が余る）の場合に不正な負の値を生成してしまい正しく動かない。
          // そのため、箱いっぱいの黒背景を敷いた上で、実寸から自前でレターボックス配置する。
          const imgPath = path.join(IMG_DIR, photo + ".jpg");
          const nat = getImgSize(imgPath);
          slide.addShape("rect", { x: sx, y: py, w: photoW, h: photoH, fill: { color: "000000" }, line: { type: "none" } });
          const imgRatio = nat.height / nat.width;
          const boxRatio = photoH / photoW;
          let dw, dh;
          if (imgRatio > boxRatio) { dh = photoH; dw = photoH / imgRatio; }
          else { dw = photoW; dh = photoW * imgRatio; }
          slide.addImage({ path: imgPath, x: sx + (photoW - dw) / 2, y: py + (photoH - dh) / 2, w: dw, h: dh });
          slide.addShape("rect", { x: sx, y: py, w: photoW, h: photoH, fill: { type: "none" }, line: { color: "DDD5C6", width: 0.75 } });
        } else if (cap) {
          slide.addShape("rect", { x: sx, y: py, w: photoW, h: photoH, fill: { color: "FBF9F4" }, line: { color: DASH, width: 0.75, dashType: "dash" } });
          slide.addText("撮影して\n差し替え", { x: sx, y: py, w: photoW, h: photoH, align: "center", valign: "middle", fontFace: "Meiryo", fontSize: 7.5, color: "B3A894", margin: 0 });
        }
        if (cap) {
          slide.addText(parseRich(cap, { fontFace: "Meiryo", fontSize: 7.2, color: "3A3226" }), {
            x: sx, y: py + photoH + 0.04, w: photoW, h: CAP_H, fontFace: "Meiryo", fontSize: 7.2, color: "3A3226", lineSpacingMultiple: 1.24, valign: "top", margin: 0,
          });
        }
      });
    });

    footerAndPage(slide, DATA.cover.footer, pageCounter, TOTAL_SLIDES);
    pageCounter++;
  });
});

pres.writeFile({ fileName: OUT }).then(() => {
  console.log("wrote", OUT);
});
