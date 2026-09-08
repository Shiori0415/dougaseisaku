# -*- coding: utf-8 -*-
"""この画面で読むページ（kouban.html など）に共通の見た目。
   背景は白で固定する ── 見る人の設定が暗い画面でも、白のまま出す。
"""

CSS = """
:root {
  color-scheme: light;
  --ground: #ffffff; --surface: #ffffff; --band: #f4efe7;
  --ink: #15191c; --prose: #3d4448; --muted: #5b6266; --faint: #8a8f92;
  --gold: #a8672a; --line: #ddd7cd; --hair: #ebe6dd;
}
* { box-sizing: border-box; }
html { background: #ffffff; }
body {
  margin: 0; background: var(--ground); color: var(--ink);
  font-family: 'Zen Kaku Gothic New', 'Hiragino Sans', 'Yu Gothic', system-ui, sans-serif;
  font-size: 15px; line-height: 1.75; font-feature-settings: "palt";
}
b, strong { font-weight: 700; }
a { color: var(--gold); }
.wrap { max-width: 1180px; margin: 0 auto; padding: 0 24px 96px; }

nav { position: sticky; top: 0; z-index: 10; background: #ffffffee;
  backdrop-filter: blur(8px); border-bottom: 1px solid var(--line); }
.navin { max-width: 1180px; margin: 0 auto; padding: 10px 24px;
  display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.navlab { font-size: 12px; letter-spacing: .1em; color: var(--faint); margin-right: 4px; }
nav a { font-size: 13px; color: var(--muted); text-decoration: none;
  padding: 3px 9px; border-radius: 999px; border: 1px solid transparent; white-space: nowrap; }
nav a:hover, nav a:focus-visible { color: var(--gold); border-color: var(--line); background: #fdfbf8; }
nav a:focus-visible { outline: 2px solid var(--gold); outline-offset: 1px; }
.navsep { width: 1px; height: 16px; background: var(--line); margin: 0 6px; }

header.top { padding: 52px 0 26px; border-bottom: 2px solid var(--ink); }
.eyebrow { font-size: 12px; font-weight: 700; letter-spacing: .18em; color: var(--gold); }
h1 { font-size: clamp(30px, 4.4vw, 44px); font-weight: 700; letter-spacing: -.02em;
  margin: 12px 0 6px; text-wrap: balance; }
.en { font-size: 14px; letter-spacing: .08em; color: var(--faint); }
.count { margin-top: 14px; font-size: 15px; font-weight: 700; }
.lead { margin: 22px 0 0; color: var(--prose); max-width: 74ch; }

section { scroll-margin-top: 62px; padding-top: 44px; }
.shead { display: flex; align-items: baseline; gap: 14px; flex-wrap: wrap;
  border-bottom: 1px solid var(--ink); padding-bottom: 12px; }
.daynum { font-size: 26px; font-weight: 700; letter-spacing: -.01em; }
.place { font-size: 17px; font-weight: 700; color: var(--gold); }
.theme { font-size: 14px; color: var(--muted); }
.when { margin-left: auto; font-size: 14px; font-weight: 700;
  font-variant-numeric: tabular-nums; white-space: nowrap; }
.cuts { font-size: 13px; color: var(--faint); white-space: nowrap; }
.note { margin: 16px 0 0; color: var(--prose); max-width: 78ch; }

.scroll { overflow-x: auto; margin-top: 18px; }
table { width: 100%; border-collapse: collapse; min-width: 880px; }
th { text-align: left; font-size: 12px; font-weight: 400; letter-spacing: .1em;
  color: var(--faint); border-bottom: 1px solid var(--line); padding: 0 14px 9px 0; }
td { padding: 14px 14px 14px 0; border-bottom: 1px solid var(--hair); vertical-align: top; }
tr.band td { background: var(--band); padding: 9px 12px; border-bottom: 1px solid var(--line); }
.tm { color: var(--gold); font-weight: 700; font-variant-numeric: tabular-nums; white-space: nowrap; }
.sc { font-weight: 700; font-size: 16px; }
.sub { color: var(--faint); font-size: 13px; }
.dim { color: var(--muted); }
.no { font-weight: 700; font-variant-numeric: tabular-nums; }
.box { display: inline-block; width: 17px; height: 17px; border: 1px solid var(--line); border-radius: 3px; }
.pin { color: var(--gold); font-size: 13px; }
.tag { display: inline-block; font-size: 12px; font-weight: 700; letter-spacing: .06em;
  padding: 2px 9px; border-radius: 999px; border: 1px solid var(--line); color: var(--muted); }
.tag.paid { color: var(--gold); border-color: var(--gold); }

.foot { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 28px; margin-top: 26px; padding-top: 20px; border-top: 1px solid var(--line); }
.cap { font-size: 12px; letter-spacing: .1em; color: var(--faint); margin-bottom: 8px; }
.foot ul { margin: 0; padding-left: 18px; }
.foot li { margin-bottom: 6px; }
.foot .body { color: var(--prose); }
@media (max-width: 640px) {
  .wrap { padding: 0 16px 72px; }
  .navin { padding: 8px 16px; }
  body { font-size: 14px; }
}
"""

FONT = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        'family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap">')
