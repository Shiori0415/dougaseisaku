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
const TOTAL_SLIDES = 2 + DATA.pages.length * 2;

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

// ================= 8本の各ページ（縦型動画の絵コンテなので、1本＝2スライド。シーン2つずつ） =================
const HEADER_TOP = 0.38;
const TITLE_W = 6.55;
const RULE_Y = 1.56;
const BODY_Y = 1.70;
const BODY_BOTTOM = SH - 0.55;
const BODY_H = BODY_BOTTOM - BODY_Y;

const LEFT_X = MARGIN;
const LEFT_W = 3.35;
const GRID_X = LEFT_X + LEFT_W + 0.3;
const GRID_W = SW - MARGIN - GRID_X;

const SCENES_PER_SLIDE = 2;
const ROW_GAP = 0.16;
const ROW_H = (BODY_H - ROW_GAP * (SCENES_PER_SLIDE - 1)) / SCENES_PER_SLIDE;
const PHOTO_H = ROW_H * 0.74;
const CAP_H = ROW_H - PHOTO_H - 0.06;

// 1スライドあたりのシーンが2つになった分、写真の箱を正方形〜縦長寄りにする。
// 3列がGRID_Wにちょうど収まる幅（RAW_SHOT_W）と、「これ以上横長にしない」という上限
// （PHOTO_H × PORTRAIT_MAX）のうち小さい方を採用し、余った横幅はシーン名の列と列間の余白に配る。
const SCENE_W_BASE = 1.15;
const SHOT_GAP_BASE = 0.22;
const PORTRAIT_MAX = 1.05;
const RAW_SHOT_W = (GRID_W - SCENE_W_BASE - SHOT_GAP_BASE * 3) / 3;
const SHOT_COL_W = Math.min(RAW_SHOT_W, PHOTO_H * PORTRAIT_MAX);
const LEFTOVER_W = (RAW_SHOT_W - SHOT_COL_W) * 3;
const SCENE_W = SCENE_W_BASE + LEFTOVER_W * 0.5;
const SHOT_GAP = SHOT_GAP_BASE + (LEFTOVER_W * 0.5) / 3;

// 左カラム（企画／この1本で言うこと／テロップ／追加）の合計高さを見積もる。
// フォントを scale 倍したときの高さを返す（gap もそれに応じて詰める）。
function textBlocksHeight(d, scale) {
  const gap = Math.max(0.14, 0.22 * scale);
  const blkH = (html, fontPt) => estimateHeight(html, LEFT_W, fontPt * scale) + 0.30;
  let h = blkH(d.plan, 9.5) + gap;
  h += blkH(d.says, 10) + gap;
  if (d.telop_jp) {
    const enH = d.telop_en ? estimateHeight(d.telop_en, LEFT_W - 0.4, 9.5 * scale) : 0;
    const jpH = estimateHeight(d.telop_jp, LEFT_W - 0.4, 15 * scale);
    const boxH = 0.34 + jpH + (enH ? enH + 0.06 : 0) + 0.18;
    h += boxH + gap;
  }
  if (d.extra) h += blkH(d.extra[1], 8.7) + gap;
  return h;
}

// pptx内の通し番号（表紙1・目次2の次から）。data_pdf.py由来のd.pn/d.totalはPDF（1本＝1ページ）の
// ページ番号なので、1本＝2スライードになるpptxではここで別に数え直す。
let pageCounter = 3;

DATA.pages.forEach((d) => {
  // 左カラムがBODY_Hに収まる最大のフォント倍率を探す（収まっていれば1.0のまま）
  let scale = 1.0;
  for (let s = 1.0; s >= 0.6; s -= 0.02) {
    scale = s;
    if (textBlocksHeight(d, s) <= BODY_H) break;
  }
  const gap = Math.max(0.14, 0.22 * scale);

  // シーンを2つずつに分け、1本＝複数スライドにする（通常は4シーン→2スライド）
  const sceneChunks = [];
  for (let i = 0; i < d.rows.length; i += SCENES_PER_SLIDE) {
    sceneChunks.push(d.rows.slice(i, i + SCENES_PER_SLIDE));
  }

  sceneChunks.forEach((rowsChunk, partIdx) => {
    const slide = pres.addSlide();
    const partLabel = sceneChunks.length > 1 ? `${partIdx + 1} / ${sceneChunks.length}` : "";

    // ---- ヘッダー ----
    slide.addText(d.no, { x: LEFT_X, y: HEADER_TOP, w: 0.55, h: 0.22, fontFace: "Meiryo", fontSize: 9, bold: true, color: GOLD, charSpacing: 2, margin: 0 });
    if (partLabel) {
      slide.addText(partLabel, { x: LEFT_X + 0.62, y: HEADER_TOP, w: 1.2, h: 0.22, fontFace: "Meiryo", fontSize: 8, color: FAINT, margin: 0 });
    }
    slide.addText(d.jp, { x: LEFT_X, y: HEADER_TOP + 0.20, w: TITLE_W, h: 0.46, fontFace: "Meiryo", fontSize: 24, bold: true, color: INK, margin: 0 });
    slide.addText(d.en, { x: LEFT_X, y: HEADER_TOP + 0.68, w: TITLE_W, h: 0.30, fontFace: "Meiryo", fontSize: 12, color: FAINT, charSpacing: 1, margin: 0 });

    const metaW = SW - MARGIN - (LEFT_X + TITLE_W + 0.2);
    const metaRuns = [
      { text: d.meta_len, options: { fontFace: "Meiryo", fontSize: 11, bold: true, color: INK, breakLine: true } },
      { text: d.meta_target, options: { fontFace: "Meiryo", fontSize: 9, color: MUTED, breakLine: true } },
    ].concat(parseRich(d.ref, { fontFace: "Meiryo", fontSize: 8, color: FAINT }));
    slide.addText(metaRuns, { x: SW - MARGIN - metaW, y: HEADER_TOP, w: metaW, h: 1.15, align: "right", valign: "top", lineSpacingMultiple: 1.35, margin: 0 });

    slide.addShape("line", { x: LEFT_X, y: RULE_Y, w: SW - MARGIN * 2, h: 0, line: { color: INK, width: 1.5 } });

    // ---- 左カラム：企画 / この1本で言うこと / テロップ / 追加（両方のスライドに同じ内容を出す） ----
    let y = BODY_Y;
    const blk = (label, html, opts) => {
      opts = opts || {};
      const fontPt = (opts.fontPt || 9.5) * scale;
      const h = estimateHeight(html, LEFT_W, fontPt) + 0.30;
      slide.addText(label, { x: LEFT_X, y, w: LEFT_W, h: 0.22, fontFace: "Meiryo", fontSize: 7.5, color: FAINT, charSpacing: 1.5, margin: 0 });
      slide.addText(parseRich(html, { fontFace: "Meiryo", fontSize: fontPt, color: INK }), {
        x: LEFT_X, y: y + 0.22, w: LEFT_W, h: h - 0.22, fontFace: "Meiryo", fontSize: fontPt, color: INK, lineSpacingMultiple: 1.34, valign: "top", margin: 0,
      });
      y += h + gap;
    };

    blk("企　画", d.plan, { fontPt: 9.5 });
    blk("こ の 1 本 で 言 う こ と", d.says, { fontPt: 10 });

    if (d.telop_jp) {
      const fpJp = 15 * scale, fpEn = 9.5 * scale;
      const enH = d.telop_en ? estimateHeight(d.telop_en, LEFT_W - 0.4, fpEn) : 0;
      const jpH = estimateHeight(d.telop_jp, LEFT_W - 0.4, fpJp);
      const boxH = 0.34 + jpH + (enH ? enH + 0.06 : 0) + 0.18;
      slide.addShape("rect", { x: LEFT_X, y, w: LEFT_W, h: boxH, fill: { color: INK }, line: { type: "none" } });
      slide.addText("テ ロ ッ プ", { x: LEFT_X + 0.2, y: y + 0.14, w: LEFT_W - 0.4, h: 0.2, fontFace: "Meiryo", fontSize: 7, color: "C9B79A", charSpacing: 1.5, margin: 0 });
      slide.addText(d.telop_jp, { x: LEFT_X + 0.2, y: y + 0.36, w: LEFT_W - 0.4, h: jpH, fontFace: "Meiryo", fontSize: fpJp, bold: true, color: "FFFFFF", lineSpacingMultiple: 1.3, valign: "top", margin: 0 });
      if (d.telop_en) {
        slide.addText(d.telop_en, { x: LEFT_X + 0.2, y: y + 0.36 + jpH + 0.06, w: LEFT_W - 0.4, h: enH, fontFace: "Meiryo", fontSize: fpEn, color: "C9B79A", valign: "top", margin: 0 });
      }
      y += boxH + gap;
    }

    if (d.extra) {
      const [exLabel, exHtml] = d.extra;
      blk(exLabel, exHtml, { fontPt: 8.7 });
    }

    // ---- 右：シーン×ショットの格子（このスライド分の2シーンのみ） ----
    rowsChunk.forEach((row, ri) => {
      const [sceneName, sceneTime, shots] = row;
      const ry = BODY_Y + ri * (ROW_H + ROW_GAP);
      slide.addText(
        [
          { text: sceneName, options: { fontFace: "Meiryo", fontSize: 12, bold: true, color: INK, breakLine: true } },
          { text: sceneTime, options: { fontFace: "Meiryo", fontSize: 9.5, color: MUTED } },
        ],
        { x: GRID_X, y: ry, w: SCENE_W, h: ROW_H, valign: "top", lineSpacingMultiple: 1.35, margin: 0 }
      );
      shots.forEach((shot, si) => {
        const [photo, cap] = shot;
        const sx = GRID_X + SCENE_W + SHOT_GAP + si * (SHOT_COL_W + SHOT_GAP);
        if (cap === "―") return; // 使わないマス
        if (photo) {
          // pptxgenjsのsizing:{type:"contain"}はOOXMLのsrcRect+stretchで実装されており、
          // 画像が箱より縦長（幅が余る）の場合に不正な負の値を生成してしまい正しく動かない。
          // そのため、箱いっぱいの黒背景を敷いた上で、実寸から自前でレターボックス配置する。
          const imgPath = path.join(IMG_DIR, photo + ".jpg");
          const nat = getImgSize(imgPath);
          slide.addShape("rect", { x: sx, y: ry, w: SHOT_COL_W, h: PHOTO_H, fill: { color: "000000" }, line: { type: "none" } });
          const imgRatio = nat.height / nat.width;
          const boxRatio = PHOTO_H / SHOT_COL_W;
          let dw, dh;
          if (imgRatio > boxRatio) { dh = PHOTO_H; dw = PHOTO_H / imgRatio; }
          else { dw = SHOT_COL_W; dh = SHOT_COL_W * imgRatio; }
          const dx = sx + (SHOT_COL_W - dw) / 2;
          const dy = ry + (PHOTO_H - dh) / 2;
          slide.addImage({ path: imgPath, x: dx, y: dy, w: dw, h: dh });
          slide.addShape("rect", { x: sx, y: ry, w: SHOT_COL_W, h: PHOTO_H, fill: { type: "none" }, line: { color: "DDD5C6", width: 0.75 } });
        } else if (cap) {
          slide.addShape("rect", { x: sx, y: ry, w: SHOT_COL_W, h: PHOTO_H, fill: { color: "FBF9F4" }, line: { color: DASH, width: 0.75, dashType: "dash" } });
          slide.addText("撮影して差し替え", { x: sx, y: ry, w: SHOT_COL_W, h: PHOTO_H, align: "center", valign: "middle", fontFace: "Meiryo", fontSize: 7.5, color: "B3A894", margin: 0 });
        }
        if (cap) {
          slide.addText(parseRich(cap, { fontFace: "Meiryo", fontSize: 7.8, color: "3A3226" }), {
            x: sx, y: ry + PHOTO_H + 0.04, w: SHOT_COL_W, h: CAP_H, fontFace: "Meiryo", fontSize: 7.8, color: "3A3226", lineSpacingMultiple: 1.28, valign: "top", margin: 0,
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
