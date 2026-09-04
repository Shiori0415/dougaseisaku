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
// Instagramの縦型動画の絵コンテなので、スライドの用紙自体をスマホと同じ9:16の縦長にする。
const SW = 7.5, SH = 13.333;
const MARGIN = 0.42;
const CONTENT_W = SW - MARGIN * 2;
// 1本＝1スライドではなく1本＝2スライド（シーン2つずつ）に分け、写真1枚を大きく見せる。
const TOTAL_SLIDES = 2 + DATA.pages.length * 2;

const pres = new pptxgen();
pres.defineLayout({ name: "PHONE916", width: SW, height: SH });
pres.layout = "PHONE916";
pres.theme = { headFontFace: "Meiryo", bodyFontFace: "Meiryo" };

function footerAndPage(slide, footer, pn, total) {
  slide.addText(footer, { x: MARGIN, y: SH - 0.42, w: CONTENT_W - 1.2, h: 0.3, fontFace: "Meiryo", fontSize: 7.5, color: FAINT, margin: 0 });
  slide.addText(`${pn} / ${total}`, { x: SW - MARGIN - 1.2, y: SH - 0.42, w: 1.2, h: 0.3, align: "right", fontFace: "Meiryo", fontSize: 7.5, color: FAINT, margin: 0 });
}

// ================= 表紙 =================
{
  const slide = pres.addSlide();
  slide.background = { color: "FFFFFF" };
  const c = DATA.cover;
  slide.addText(c.eyebrow, { x: MARGIN, y: 3.1, w: CONTENT_W, h: 0.3, fontFace: "Meiryo", fontSize: 10, color: FAINT, charSpacing: 2, margin: 0 });
  slide.addShape("line", { x: MARGIN, y: 3.5, w: 1.5, h: 0, line: { color: INK, width: 2.2 } });
  slide.addText(c.title_jp_plain, { x: MARGIN, y: 3.72, w: CONTENT_W, h: 2.1, fontFace: "Meiryo", fontSize: 32, bold: true, color: INK, lineSpacingMultiple: 1.28, valign: "top", margin: 0 });
  slide.addText(c.subtitle_en, { x: MARGIN, y: 5.95, w: CONTENT_W, h: 0.45, fontFace: "Meiryo", fontSize: 13, color: MUTED, charSpacing: 1.2, margin: 0 });

  slide.addShape("line", { x: MARGIN, y: 11.15, w: CONTENT_W, h: 0, line: { color: LINE, width: 1 } });
  slide.addText(c.meta_lines.join("\n"), { x: MARGIN, y: 11.3, w: CONTENT_W, h: 1.1, fontFace: "Meiryo", fontSize: 10, color: MUTED, lineSpacingMultiple: 1.5, valign: "top", margin: 0 });
  footerAndPage(slide, c.footer, 1, TOTAL_SLIDES);
}

// ================= 目次 =================
{
  const slide = pres.addSlide();
  const c = DATA.cover;
  slide.addText("目 次　CONTENTS", { x: MARGIN, y: 0.42, w: CONTENT_W, h: 0.3, fontFace: "Meiryo", fontSize: 10, color: FAINT, charSpacing: 2, margin: 0 });
  slide.addText("8本の動画", { x: MARGIN, y: 0.72, w: CONTENT_W, h: 0.55, fontFace: "Meiryo", fontSize: 22, bold: true, color: INK, margin: 0 });
  slide.addText(c.toc_intro, { x: MARGIN, y: 1.32, w: CONTENT_W, h: 0.7, fontFace: "Meiryo", fontSize: 9, color: MUTED, lineSpacingMultiple: 1.35, valign: "top", margin: 0 });

  const colW = [0.32, 1.85, 0.92, 1.55, 2.02];
  const header = ["#", "タイトル", "尺・本数", "届ける相手", "参考動画"].map((t) => ({
    text: t, options: { fontFace: "Meiryo", fontSize: 8, color: FAINT, bold: false, fill: { color: "FFFFFF" }, border: { pt: 0 } },
  }));
  const rows = [header];
  DATA.toc.forEach((r) => {
    rows.push([
      { text: r.n, options: { fontFace: "Meiryo", fontSize: 11, bold: true, color: GOLD, valign: "top" } },
      { text: [{ text: r.jp, options: { fontFace: "Meiryo", fontSize: 10, bold: true, color: INK, breakLine: true } },
                { text: r.en, options: { fontFace: "Meiryo", fontSize: 7.5, color: FAINT } }], options: { valign: "top" } },
      { text: r.len, options: { fontFace: "Meiryo", fontSize: 8.5, color: MUTED, valign: "top" } },
      { text: r.target, options: { fontFace: "Meiryo", fontSize: 8.5, color: INK, valign: "top" } },
      { text: parseRich(r.ref_html, { fontFace: "Meiryo", fontSize: 7.5, color: FAINT }), options: { valign: "top" } },
    ]);
  });
  slide.addTable(rows, {
    x: MARGIN, y: 2.12, w: CONTENT_W, colW,
    border: { type: "solid", color: LINE, pt: 0.75 },
    autoPage: false, valign: "top",
    margin: [0.06, 0.07, 0.06, 0.07],
    rowH: [0.3, 1.15, 1.15, 1.15, 1.15, 1.15, 1.15, 1.15, 1.15],
  });
  footerAndPage(slide, c.footer, 2, TOTAL_SLIDES);
}

// ================= 8本の各ページ（縦型スライド。1本＝2スライド、シーン2つずつ） =================
// 用紙が縦長になったので、横並び（左＝文章／右＝格子）をやめ、上から
// ヘッダー → 文章 → シーンの格子、の縦積みにする。
// 文章は2枚に振り分ける（1枚目＝企画とこの1本で言うこと／2枚目＝テロップと追加ブロック）。
// 1枚に全部を載せると文章だけで紙の半分を使ってしまい、肝心の写真が潰れるため。
const HEADER_TOP = 0.40;
const RULE_Y = 2.28;
const BODY_Y = 2.42;
const BODY_BOTTOM = SH - 0.55;
const BODY_H = BODY_BOTTOM - BODY_Y;

const TEXT_W = CONTENT_W;

const SCENES_PER_SLIDE = 2;
const ROW_GAP = 0.22;
const LABEL_H = 0.30;          // シーン名（S1 支度 0-4秒）の帯
const CAP_H = 0.62;            // 写真の下のキャプション
const SHOT_GAP = 0.14;
const SHOT_COL_W = (CONTENT_W - SHOT_GAP * 2) / 3;
const MAX_PHOTO_H = SHOT_COL_W * 16 / 9;   // 9:16（スマホの画面）より縦長にはしない
const MIN_PHOTO_H = 1.55;
// 文章に使ってよい高さの上限。これを超える場合はフォントを縮めて格子の場所を確保する。
const TEXT_MAX_H = BODY_H - (2 * (LABEL_H + MIN_PHOTO_H + CAP_H) + ROW_GAP);

// そのスライドに載せる文章ブロックを返す
function textBlocksFor(d, partIdx) {
  if (partIdx === 0) {
    return [
      { kind: "text", label: "企　画", html: d.plan, fontPt: 9.5 },
      { kind: "text", label: "こ の 1 本 で 言 う こ と", html: d.says, fontPt: 10 },
    ];
  }
  const blocks = [];
  if (d.telop_jp) blocks.push({ kind: "telop" });
  if (d.extra) blocks.push({ kind: "text", label: d.extra[0], html: d.extra[1], fontPt: 8.7 });
  return blocks;
}

// 文章ブロックの合計高さを、フォントを scale 倍したときの値で見積もる
function textBlocksHeight(d, partIdx, scale) {
  const gap = Math.max(0.12, 0.20 * scale);
  let h = 0;
  for (const b of textBlocksFor(d, partIdx)) {
    if (b.kind === "telop") {
      const enH = d.telop_en ? estimateHeight(d.telop_en, TEXT_W - 0.4, 9.5 * scale) : 0;
      const jpH = estimateHeight(d.telop_jp, TEXT_W - 0.4, 15 * scale);
      h += 0.34 + jpH + (enH ? enH + 0.06 : 0) + 0.18 + gap;
    } else {
      h += estimateHeight(b.html, TEXT_W, b.fontPt * scale) + 0.28 + gap;
    }
  }
  return h;
}

// pptx内の通し番号（表紙1・目次2の次から）。data_pdf.py由来のd.pn/d.totalはPDF（1本＝1ページ）の
// ページ番号なので、1本＝2スライドになるpptxではここで別に数え直す。
let pageCounter = 3;

DATA.pages.forEach((d) => {
  // シーンを2つずつに分け、1本＝複数スライドにする（通常は4シーン→2スライド）
  const sceneChunks = [];
  for (let i = 0; i < d.rows.length; i += SCENES_PER_SLIDE) {
    sceneChunks.push(d.rows.slice(i, i + SCENES_PER_SLIDE));
  }

  sceneChunks.forEach((rowsChunk, partIdx) => {
    const slide = pres.addSlide();
    const partLabel = sceneChunks.length > 1 ? `${partIdx + 1} / ${sceneChunks.length}` : "";

    // このスライドの文章がTEXT_MAX_Hに収まる最大のフォント倍率を探す
    let scale = 1.0;
    for (let s = 1.0; s >= 0.6; s -= 0.02) {
      scale = s;
      if (textBlocksHeight(d, partIdx, s) <= TEXT_MAX_H) break;
    }
    const gap = Math.max(0.12, 0.20 * scale);

    // ---- ヘッダー ----
    slide.addText(d.no, { x: MARGIN, y: HEADER_TOP, w: 0.55, h: 0.22, fontFace: "Meiryo", fontSize: 9, bold: true, color: GOLD, charSpacing: 2, margin: 0 });
    if (partLabel) {
      slide.addText(partLabel, { x: MARGIN + 0.6, y: HEADER_TOP, w: 1.0, h: 0.22, fontFace: "Meiryo", fontSize: 8, color: FAINT, margin: 0 });
    }
    slide.addText(d.jp, { x: MARGIN, y: HEADER_TOP + 0.24, w: CONTENT_W, h: 0.46, fontFace: "Meiryo", fontSize: 21, bold: true, color: INK, valign: "top", margin: 0 });
    slide.addText(d.en, { x: MARGIN, y: HEADER_TOP + 0.74, w: CONTENT_W, h: 0.28, fontFace: "Meiryo", fontSize: 11, color: FAINT, charSpacing: 1, margin: 0 });

    const metaRuns = [
      { text: d.meta_len, options: { fontFace: "Meiryo", fontSize: 10.5, bold: true, color: INK, breakLine: true } },
      { text: d.meta_target, options: { fontFace: "Meiryo", fontSize: 8.5, color: MUTED, breakLine: true } },
    ].concat(parseRich(d.ref, { fontFace: "Meiryo", fontSize: 7.5, color: FAINT }));
    slide.addText(metaRuns, { x: MARGIN, y: HEADER_TOP + 1.06, w: CONTENT_W, h: 0.80, valign: "top", lineSpacingMultiple: 1.32, margin: 0 });

    slide.addShape("line", { x: MARGIN, y: RULE_Y, w: CONTENT_W, h: 0, line: { color: INK, width: 1.5 } });

    // ---- 文章 ----
    let y = BODY_Y;
    for (const b of textBlocksFor(d, partIdx)) {
      if (b.kind === "telop") {
        const fpJp = 15 * scale, fpEn = 9.5 * scale;
        const enH = d.telop_en ? estimateHeight(d.telop_en, TEXT_W - 0.4, fpEn) : 0;
        const jpH = estimateHeight(d.telop_jp, TEXT_W - 0.4, fpJp);
        const boxH = 0.34 + jpH + (enH ? enH + 0.06 : 0) + 0.18;
        slide.addShape("rect", { x: MARGIN, y, w: TEXT_W, h: boxH, fill: { color: INK }, line: { type: "none" } });
        slide.addText("テ ロ ッ プ", { x: MARGIN + 0.2, y: y + 0.12, w: TEXT_W - 0.4, h: 0.2, fontFace: "Meiryo", fontSize: 7, color: "C9B79A", charSpacing: 1.5, margin: 0 });
        slide.addText(d.telop_jp, { x: MARGIN + 0.2, y: y + 0.34, w: TEXT_W - 0.4, h: jpH, fontFace: "Meiryo", fontSize: fpJp, bold: true, color: "FFFFFF", lineSpacingMultiple: 1.3, valign: "top", margin: 0 });
        if (d.telop_en) {
          slide.addText(d.telop_en, { x: MARGIN + 0.2, y: y + 0.34 + jpH + 0.06, w: TEXT_W - 0.4, h: enH, fontFace: "Meiryo", fontSize: fpEn, color: "C9B79A", valign: "top", margin: 0 });
        }
        y += boxH + gap;
      } else {
        const fontPt = b.fontPt * scale;
        const h = estimateHeight(b.html, TEXT_W, fontPt) + 0.28;
        slide.addText(b.label, { x: MARGIN, y, w: TEXT_W, h: 0.20, fontFace: "Meiryo", fontSize: 7.5, color: FAINT, charSpacing: 1.5, margin: 0 });
        slide.addText(parseRich(b.html, { fontFace: "Meiryo", fontSize: fontPt, color: INK }), {
          x: MARGIN, y: y + 0.20, w: TEXT_W, h: h - 0.20, fontFace: "Meiryo", fontSize: fontPt, color: INK, lineSpacingMultiple: 1.34, valign: "top", margin: 0,
        });
        y += h + gap;
      }
    }

    // ---- シーンの格子（このスライド分の2シーン）。文章の下に、残りの高さいっぱいに置く ----
    const gridTop = Math.max(y + 0.12, BODY_Y);
    const gridH = BODY_BOTTOM - gridTop;
    let photoH = (gridH - ROW_GAP) / SCENES_PER_SLIDE - LABEL_H - CAP_H;
    photoH = Math.max(MIN_PHOTO_H, Math.min(photoH, MAX_PHOTO_H));
    const rowH = LABEL_H + photoH + CAP_H;
    // 9:16で頭打ちになって余った高さは、格子全体を少し下げて中央寄せにする
    const slack = Math.max(0, gridH - (rowH * SCENES_PER_SLIDE + ROW_GAP));
    const gridY = gridTop + slack / 2;

    rowsChunk.forEach((row, ri) => {
      const [sceneName, sceneTime, shots] = row;
      const ry = gridY + ri * (rowH + ROW_GAP);
      slide.addText(
        [
          { text: sceneName, options: { fontFace: "Meiryo", fontSize: 12, bold: true, color: INK } },
          { text: "　" + sceneTime, options: { fontFace: "Meiryo", fontSize: 9.5, color: MUTED } },
        ],
        { x: MARGIN, y: ry, w: CONTENT_W, h: LABEL_H, valign: "top", margin: 0 }
      );
      const py = ry + LABEL_H;
      shots.forEach((shot, si) => {
        const [photo, cap] = shot;
        const sx = MARGIN + si * (SHOT_COL_W + SHOT_GAP);
        if (cap === "―") return; // 使わないマス
        if (photo) {
          // pptxgenjsのsizing:{type:"contain"}はOOXMLのsrcRect+stretchで実装されており、
          // 画像が箱より縦長（幅が余る）の場合に不正な負の値を生成してしまい正しく動かない。
          // そのため、箱いっぱいの黒背景を敷いた上で、実寸から自前でレターボックス配置する。
          const imgPath = path.join(IMG_DIR, photo + ".jpg");
          const nat = getImgSize(imgPath);
          slide.addShape("rect", { x: sx, y: py, w: SHOT_COL_W, h: photoH, fill: { color: "000000" }, line: { type: "none" } });
          const imgRatio = nat.height / nat.width;
          const boxRatio = photoH / SHOT_COL_W;
          let dw, dh;
          if (imgRatio > boxRatio) { dh = photoH; dw = photoH / imgRatio; }
          else { dw = SHOT_COL_W; dh = SHOT_COL_W * imgRatio; }
          slide.addImage({ path: imgPath, x: sx + (SHOT_COL_W - dw) / 2, y: py + (photoH - dh) / 2, w: dw, h: dh });
          slide.addShape("rect", { x: sx, y: py, w: SHOT_COL_W, h: photoH, fill: { type: "none" }, line: { color: "DDD5C6", width: 0.75 } });
        } else if (cap) {
          slide.addShape("rect", { x: sx, y: py, w: SHOT_COL_W, h: photoH, fill: { color: "FBF9F4" }, line: { color: DASH, width: 0.75, dashType: "dash" } });
          slide.addText("撮影して差し替え", { x: sx, y: py, w: SHOT_COL_W, h: photoH, align: "center", valign: "middle", fontFace: "Meiryo", fontSize: 7.5, color: "B3A894", margin: 0 });
        }
        if (cap) {
          slide.addText(parseRich(cap, { fontFace: "Meiryo", fontSize: 7.8, color: "3A3226" }), {
            x: sx, y: py + photoH + 0.04, w: SHOT_COL_W, h: CAP_H, fontFace: "Meiryo", fontSize: 7.8, color: "3A3226", lineSpacingMultiple: 1.26, valign: "top", margin: 0,
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
