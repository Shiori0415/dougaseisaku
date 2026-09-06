# -*- coding: utf-8 -*-
"""機材と費用のページ（Artifact用HTML）を書き出す。
   実行: python3 tools/build_gear_page.py
   金額は tools/build_xlsx_gear.py の GEAR だけを見る。xlsxとページで数字が食い違わない。
"""
import os, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_xlsx_gear import GEAR, sakura

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

def yen(n): return f"¥{n:,}"
def esc(s): return html.escape(s or "")

LO   = sum(g[3] for g in GEAR)
UP   = sum(g[6] for g in GEAR)
ADIF = sum(g[6] - g[3] for g in GEAR if g[0] == "A")
MID  = LO + ADIF
SOUND = sum(g[3] for g in GEAR if g[1] in ("音声レコーダー", "ガンマイク"))

def sk_rows_html():
    out = []
    for pri, item, lo, lop, lou, up, upp, upu, why, conf in GEAR:
        for label, name, url in (("低価格版", lo, lou), ("アップグレード版", up, upu)):
            if name in ("同じもので十分",) or name.startswith("買わない"):
                continue
            link = sakura(url)
            cell = (f'<a href="{esc(link)}" target="_blank" rel="noopener">サクラ度を見る →</a>'
                    if link else '<span class="na">Amazon以外のため対象外</span>')
            out.append(f'<li><span class="sk-tag">{label}</span>'
                       f'<span class="sk-name">{esc(item)}　{esc(name)}</span>{cell}</li>')
    seen, uniq = set(), []
    for row in out:
        if row not in seen:
            seen.add(row); uniq.append(row)
    return "".join(uniq)


PRI_LABEL = {"A": "いちばん効く", "B": "画づくりが変わる", "—": "据え置き"}

def conf_chip(text):
    """確度の文言から、色分け用の種別を決める"""
    if "概算" in text or "未特定" in text: return "est", "概算"
    if "幅あり" in text or "前々回" in text or "再確認できず" in text: return "range", "幅あり"
    return "ok", "確認済"

def rows_html():
    out = []
    for pri, item, lo, lop, lou, up, upp, upu, why, conf in GEAR:
        kind, chip = conf_chip(conf)
        buy = lop == 0
        diff = upp - lop
        lo_cell = (f'<span class="none">{esc(lo)}</span>' if buy
                   else f'{esc(lo)}<br /><a href="{esc(lou)}" target="_blank" rel="noopener">商品ページ →</a>' if lou
                   else esc(lo))
        up_cell = (f'<span class="same">{esc(up)}</span>' if up == "同じもので十分"
                   else f'{esc(up)}<br /><a href="{esc(upu)}" target="_blank" rel="noopener">商品ページ →</a>' if upu
                   else esc(up))
        out.append(f'''
        <tr class="pri-{ "keep" if pri == "—" else pri.lower() }">
          <td class="pri"><span class="pill">{esc(pri)}</span><span class="pri-note">{PRI_LABEL[pri]}</span></td>
          <td class="item">{esc(item)}</td>
          <td class="name">{lo_cell}</td>
          <td class="price num{" zero" if buy else ""}">{yen(lop)}</td>
          <td class="name up">{up_cell}</td>
          <td class="price num">{yen(upp)}</td>
          <td class="diff num">{"—" if diff == 0 else "+" + f"{diff:,}"}</td>
          <td class="why">{esc(why)}</td>
          <td class="conf"><span class="chip {kind}">{chip}</span><span class="conf-text">{esc(conf)}</span></td>
        </tr>''')
    return "".join(out)

PAGE = f"""<title>撮影機材　低価格版とアップグレード版</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans+JP:wght@400;500;600;700&display=swap" />
<style>
  :root{{
    --bg:#eef0f0; --surface:#ffffff; --surface-2:#e4e7e7;
    --ink:#15191c; --muted:#5b6266; --faint:#868d90;
    --line:#d6dadb; --line-strong:#b9bfc0;
    --accent:#a8672a; --accent-ink:#5c3714; --accent-soft:#f1e2cd;
    --good:#3f7d5c; --good-soft:#dfeee6;
    --warn:#9a3b2e; --warn-soft:#f4e4e0;
    --up:#2f6b57; --up-soft:#e7f0ea;
    --mono:'IBM Plex Mono','SFMono-Regular',ui-monospace,monospace;
    --sans:'IBM Plex Sans JP','Hiragino Sans','Yu Gothic',system-ui,sans-serif;
    --shadow:0 1px 2px rgba(20,20,20,.04), 0 6px 20px -8px rgba(20,20,20,.14);
  }}
  /* 読みやすさを優先し、端末のダークモード設定に関わらず明るい配色で固定しています */
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.65}}
  h1,h2,h3{{margin:0;font-family:var(--mono);text-wrap:balance}}
  a{{color:var(--accent)}}
  .num{{font-family:var(--mono);font-variant-numeric:tabular-nums}}
  .wrap{{max-width:1340px;margin:0 auto;padding:0 28px 110px}}

  header.top{{padding:52px 28px 34px;border-bottom:1px solid var(--line);
    background:linear-gradient(180deg,var(--surface-2),var(--bg))}}
  header.top .inner{{max-width:1340px;margin:0 auto}}
  .eyebrow{{font-family:var(--mono);font-size:11px;letter-spacing:.14em;color:var(--faint);
    text-transform:uppercase;margin-bottom:14px}}
  header.top h1{{font-size:clamp(27px,3.6vw,38px);font-weight:700;letter-spacing:-.01em}}
  header.top .sub{{margin:14px 0 0;max-width:680px;color:var(--muted)}}
  .meta-row{{display:flex;gap:22px;flex-wrap:wrap;margin-top:20px;
    font-family:var(--mono);font-size:12px;color:var(--faint)}}
  .meta-row b{{color:var(--muted);font-weight:500}}

  .alert{{margin:28px 0 0;display:flex;gap:14px;align-items:flex-start;
    background:var(--warn-soft);border-left:3px solid var(--warn);border-radius:0 8px 8px 0;padding:16px 20px}}
  .alert .mark{{font-family:var(--mono);font-size:11px;font-weight:600;letter-spacing:.08em;
    color:var(--warn);white-space:nowrap;padding-top:2px}}
  .alert p{{margin:0;color:#5e2f27;font-size:13.5px}}
  .alert p + p{{margin-top:7px}}

  section.block{{padding:52px 0 0}}
  .block-head{{display:flex;align-items:baseline;justify-content:space-between;gap:16px}}
  .block-head h2{{font-size:20px}}
  .block-head .idx{{font-family:var(--mono);font-size:12px;letter-spacing:.08em;color:var(--faint)}}
  .block-lede{{color:var(--muted);max-width:720px;margin:10px 0 24px;font-size:14.5px}}

  .opts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1px;
    background:var(--line);border:1px solid var(--line);border-radius:10px;overflow:hidden}}
  .opt{{background:var(--surface);padding:22px}}
  .opt .tag{{font-family:var(--mono);font-size:11px;letter-spacing:.08em;color:var(--faint);text-transform:uppercase}}
  .opt .yen{{font-size:30px;font-weight:600;margin-top:8px}}
  .opt p{{margin:10px 0 0;color:var(--muted);font-size:13.5px}}
  .opt.lead{{background:var(--accent-soft)}}
  .opt.lead .tag{{color:var(--accent-ink)}}
  .opt.full{{background:var(--up-soft)}}
  .opt.full .tag{{color:var(--up)}}

  .table-shell{{border:1px solid var(--line);border-radius:12px;background:var(--surface);
    box-shadow:var(--shadow);overflow-x:auto}}
  table.cmp{{width:100%;border-collapse:collapse;font-size:13px;min-width:1240px}}
  table.cmp thead th{{text-align:left;padding:11px 12px;font-weight:500;font-size:11px;color:var(--faint);
    font-family:var(--mono);letter-spacing:.05em;border-bottom:1px solid var(--line);
    background:var(--surface-2);white-space:nowrap}}
  table.cmp thead th.g-lo{{background:#dfe3e3;color:var(--muted)}}
  table.cmp thead th.g-up{{background:var(--up-soft);color:var(--up)}}
  table.cmp tbody td{{padding:13px 12px;border-bottom:1px solid var(--line);vertical-align:top}}
  table.cmp tbody tr:last-child td{{border-bottom:none}}
  table.cmp .item{{font-weight:500;white-space:nowrap}}
  table.cmp .name{{max-width:200px;min-width:170px}}
  table.cmp .name.up{{background:#f6faf8}}
  table.cmp .name a{{display:inline-block;font-size:11px;margin-top:3px;font-family:var(--mono);text-decoration:none}}
  table.cmp .name a:hover{{text-decoration:underline}}
  table.cmp .none{{color:var(--faint)}}
  table.cmp .same{{color:var(--up);font-family:var(--mono);font-size:12px}}
  table.cmp .price{{text-align:right;white-space:nowrap;font-weight:600}}
  table.cmp .price.zero{{color:var(--faint);font-weight:400}}
  table.cmp .diff{{text-align:right;white-space:nowrap;color:var(--up)}}
  table.cmp .why{{color:var(--muted);font-size:12.5px;max-width:330px;min-width:250px}}
  table.cmp .conf{{max-width:200px;min-width:165px}}
  table.cmp .conf-text{{display:block;color:var(--muted);font-size:11.5px;margin-top:4px}}
  table.cmp .pri{{white-space:nowrap}}
  table.cmp .pri-note{{display:block;font-size:10.5px;color:var(--faint);margin-top:3px}}
  .pill{{display:inline-block;font-family:var(--mono);font-size:11px;font-weight:600;
    width:22px;text-align:center;border-radius:4px;padding:2px 0}}
  .pri-a .pill{{background:var(--accent-soft);color:var(--accent-ink)}}
  .pri-b .pill{{background:var(--up-soft);color:var(--up)}}
  .pri-keep .pill{{background:#e9ebeb;color:var(--faint)}}
  .chip{{display:inline-block;font-family:var(--mono);font-size:10px;letter-spacing:.04em;
    padding:2px 7px;border-radius:4px}}
  .chip.ok{{background:var(--good-soft);color:var(--good)}}
  .chip.range{{background:var(--accent-soft);color:var(--accent-ink)}}
  .chip.est{{background:var(--warn-soft);color:var(--warn)}}
  table.cmp tfoot td{{padding:15px 12px;border-top:2px solid var(--line-strong);font-weight:600}}
  table.cmp tfoot .price{{font-size:16px}}

  table.cmp.spec{{min-width:900px}}
  table.cmp.spec thead th{{text-align:left;padding:12px;font-family:var(--sans);font-size:13px;
    font-weight:600;color:var(--ink);text-transform:none;letter-spacing:0;white-space:normal;width:26%}}
  table.cmp.spec thead th:first-child{{width:14%;background:var(--surface)}}
  .th-sub{{display:block;font-family:var(--mono);font-size:10.5px;font-weight:400;
    color:var(--faint);margin-top:3px}}
  td.sp-k{{font-size:12px;color:var(--faint);white-space:nowrap;background:#f7f8f8}}
  td.sp-v{{font-size:13px}}
  .note-line{{margin-top:16px;font-size:13px;color:var(--muted)}}
  .panel{{border:1px solid var(--line);border-radius:12px;background:var(--surface);
    box-shadow:var(--shadow);padding:22px 24px}}
  .panel h3{{font-size:15px;font-weight:600;margin-bottom:10px;font-family:var(--sans)}}
  .panel p{{margin:0 0 10px;color:var(--muted);font-size:13.5px}}
  .panel p:last-child{{margin-bottom:0}}
  .panel b{{color:var(--ink)}}
  .two-col{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px}}
  ul.sk-list{{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:0}}
  ul.sk-list li{{display:grid;grid-template-columns:104px 1fr auto;gap:14px;align-items:baseline;
    padding:9px 0;border-bottom:1px solid var(--line);font-size:13.5px}}
  ul.sk-list li:last-child{{border-bottom:none}}
  .sk-tag{{font-family:var(--mono);font-size:10.5px;letter-spacing:.04em;color:var(--faint)}}
  .sk-name{{color:var(--ink)}}
  ul.sk-list a{{font-family:var(--mono);font-size:12px;text-decoration:none;white-space:nowrap}}
  ul.sk-list a:hover{{text-decoration:underline}}
  .na{{font-family:var(--mono);font-size:11.5px;color:var(--faint);white-space:nowrap}}
  dl.conf-list{{margin:0;display:grid;grid-template-columns:auto 1fr;gap:10px 16px;align-items:baseline}}
  dl.conf-list dt{{margin:0}}
  dl.conf-list dd{{margin:0;color:var(--muted);font-size:13.5px}}

  footer.foot{{margin-top:56px;padding:22px 0 0;border-top:1px solid var(--line);
    color:var(--faint);font-size:12px;line-height:1.8}}
  @media (prefers-reduced-motion:reduce){{*{{animation:none!important;transition:none!important}}}}
</style>

<header class="top">
  <div class="inner">
    <div class="eyebrow">BROOKLYN MUSEUM ／ 向島工房・動画制作</div>
    <h1>撮影機材　低価格版とアップグレード版</h1>
    <p class="sub">動画八本を私（宮下）一人で撮る前提で、必要な機材と金額を一枚にまとめました。カメラはお手持ちのものを使うため、それ以外に必要な機材の金額です。</p>
    <div class="meta-row">
      <span><b>作成：</b>2026年9月　株式会社B supply　宮下 詩織</span>
      <span><b>対象：</b>動画八本すべて</span>
      <span><b>項目：</b>{len(GEAR)}品目</span>
    </div>
    <div class="alert">
      <div class="mark">価格について</div>
      <div>
        <p>この資料を作った環境から <b>Amazon・価格.com・楽天・サインモール・サクラチェッカーのいずれにも接続できません。</b>表の金額は前回調査した時点のもので、リンク先の今の金額と違っていることがあります。</p>
        <p>そのため、金額を一つずつ「確認済／幅あり／概算」に分けて表に書きました。<b>発注前に、リンクを開いて金額をご確認ください。</b></p>
      </div>
    </div>
  </div>
</header>

<div class="wrap">

<section class="block" style="padding-top:40px">
  <div class="block-head"><h2>三つの選び方</h2><span class="idx">CHOOSE ONE</span></div>
  <p class="block-lede">カメラ本体は含みません。金額はすべて下の表の合計と一致しています。</p>
  <div class="opts">
    <div class="opt lead">
      <div class="tag">① 低価格版</div>
      <div class="yen num">{yen(LO)}</div>
      <p>いま組んである最小構成。これで八本すべて撮り切れます。</p>
    </div>
    <div class="opt">
      <div class="tag">② 音と支えだけ上げる</div>
      <div class="yen num">{yen(MID)}</div>
      <p>優先度Aの二つ（マイクと三脚）だけアップグレード。差額 {yen(ADIF)}。インタビュー四人分の声と、動かすカットの安定がいちばん変わります。</p>
    </div>
    <div class="opt full">
      <div class="tag">③ 全部上げる</div>
      <div class="yen num">{yen(UP)}</div>
      <p>アップグレード版の合計。低価格版との差額 {yen(UP - LO)}。</p>
    </div>
  </div>
</section>

<section class="block">
  <div class="block-head"><h2>品目ごとの比較</h2><span class="idx">{len(GEAR)} ITEMS</span></div>
  <p class="block-lede">優先度 <b>A</b> ＝いちばん効く二つ。<b>B</b> ＝画づくりが変わる。<b>—</b> ＝上げても差が出ないので据え置き。「買わない」の行は低価格版では0円で、アップグレード版で初めて買う機材です。</p>
  <div class="table-shell">
    <table class="cmp">
      <thead>
        <tr>
          <th>優先度</th><th>品目</th>
          <th class="g-lo">低価格版　商品</th><th class="g-lo" style="text-align:right">価格</th>
          <th class="g-up">アップグレード版　商品</th><th class="g-up" style="text-align:right">価格</th>
          <th style="text-align:right">差額</th><th>何が変わるか</th><th>価格の確度</th>
        </tr>
      </thead>
      <tbody>{rows_html()}
      </tbody>
      <tfoot>
        <tr>
          <td colspan="3">合計</td>
          <td class="price num">{yen(LO)}</td>
          <td></td>
          <td class="price num">{yen(UP)}</td>
          <td class="diff num">+{UP - LO:,}</td>
          <td colspan="2" style="font-weight:400;color:var(--faint);font-size:12.5px">
            カメラ本体は含みません。SDカードを買わない場合は低価格版が {yen(LO - 2500)} になります。</td>
        </tr>
      </tfoot>
    </table>
  </div>
</section>

<section class="block">
  <div class="block-head"><h2>三脚のアップグレード候補</h2><span class="idx">TWO AT THE SAME PRICE</span></div>
  <p class="block-lede">同じ二万五千円台で、性格の違う二つがあります。<b>ベルボン シェルパ635III N</b>（表に入れているのはこちら）と、<b>NEEWER LL27</b>です。決め手は「据えて撮るか、動かして撮るか」です。</p>
  <div class="table-shell">
    <table class="cmp spec">
      <thead>
        <tr><th></th>
          <th class="g-lo">Velbon EX-440<br /><span class="th-sub">低価格版・いま入っているもの</span></th>
          <th class="g-up">Velbon シェルパ 635III N<br /><span class="th-sub">アップグレード版・表に採用</span></th>
          <th>NEEWER LL27<br /><span class="th-sub">もう一つの候補</span></th></tr>
      </thead>
      <tbody>
        <tr><td class="sp-k">価格</td><td class="sp-v num">¥3,012</td><td class="sp-v num">約¥25,000</td><td class="sp-v num">¥24,999</td></tr>
        <tr><td class="sp-k">雲台</td><td class="sp-v">3ウェイ</td><td class="sp-v">3ウェイ（マグネシウム・クイックシュー）</td><td class="sp-v"><b>フルード（ビデオ雲台）</b></td></tr>
        <tr><td class="sp-k">段数・脚径</td><td class="sp-v">4段・細い</td><td class="sp-v"><b>3段・脚径29mm</b></td><td class="sp-v">—</td></tr>
        <tr><td class="sp-k">全高</td><td class="sp-v">153cm</td><td class="sp-v">179cm（EV含む）／139cm（EV無し）</td><td class="sp-v">89.4〜192cm</td></tr>
        <tr><td class="sp-k">縮長</td><td class="sp-v">—</td><td class="sp-v">67cm</td><td class="sp-v">—</td></tr>
        <tr><td class="sp-k">質量</td><td class="sp-v">—</td><td class="sp-v"><b>2.43kg</b></td><td class="sp-v">4.0kg</td></tr>
        <tr><td class="sp-k">耐荷重</td><td class="sp-v">2kg</td><td class="sp-v">3kg（脚は最大8kg）</td><td class="sp-v"><b>8kg</b></td></tr>
        <tr><td class="sp-k">得意なこと</td><td class="sp-v">置いて固定するだけ</td><td class="sp-v">据えて撮る画。揺れが止まるまでが速い。軽くて持ち運べる</td><td class="sp-v">動かして撮る画。パン・ティルトがなめらかに止まる</td></tr>
        <tr><td class="sp-k">弱いところ</td><td class="sp-v">伸ばすと揺れる。録画の頭に微振動が乗る</td><td class="sp-v">なめらかなパンは苦手（ビデオ雲台ではない）</td><td class="sp-v">4kgあり、一人で毎回持ち運ぶには重い</td></tr>
      </tbody>
    </table>
  </div>
  <div class="two-col" style="margin-top:18px">
    <div class="panel">
      <h3>シェルパを選ぶなら</h3>
      <p><b>③⑦の固定撮影と、①⑤⑥の真俯瞰</b>が中心。カメラを据えて回すカットが多く、機材を一人で毎回運ぶことを考えると、2.43kgという軽さが効きます。国内メーカーで品質のばらつきも少ない。</p>
    </div>
    <div class="panel">
      <h3>LL27を選ぶなら</h3>
      <p><b>⑥の「工房を歩くカメラ」や①の横移動</b>でパンを使うなら、フルード雲台のこちら。三ウェイ雲台は動かすとカクつくので、この差は編集で埋められません。ただし4kgあります。</p>
    </div>
  </div>
  <div class="note-line">NEEWERは照明でも採用しているブランドですが、メーカー公式ではない量販ブランドです。<a href="https://sakura-checker.jp/search/" target="_blank" rel="noopener">サクラチェッカー</a>で確認してから発注してください。</div>
</section>

<section class="block">
  <div class="block-head"><h2>金額の確からしさ</h2><span class="idx">HOW SURE</span></div>
  <p class="block-lede">表の「価格の確度」列の見かたです。数字を一点で書いていても、確かさは同じではありません。</p>
  <div class="panel">
    <dl class="conf-list">
      <dt><span class="chip ok">確認済</span></dt>
      <dd>前回の調査で、商品ページの実売価格を確認できたもの。それでも時価なので、発注時に変わっている可能性はあります。</dd>
      <dt><span class="chip range">幅あり</span></dt>
      <dd>掲載価格に幅があるもの。<b>三脚の低価格版</b>（3,012円と6,018円の両方の掲載あり）、<b>三脚のアップグレード版</b>（銀一30,800円／System5 33,048円／エディオン40,800円・表は銀一を採用）、<b>マクロレンズのアップグレード版</b>（中古50,100〜53,700円・表は中央値）、<b>レフ板</b>（前々回調査時の値で、前回は再確認できず）。</dd>
      <dt><span class="chip est">概算</span></dt>
      <dd>金額を確定できていないもの。<b>照明のアップグレード版</b>（セット構成で変わる）、<b>アクリル板</b>、<b>SDカード</b>（商品ページを特定できず、リンクは検索結果）、<b>予備バッテリー</b>（商品ページ未特定）。</dd>
    </dl>
  </div>
</section>

<section class="block">
  <div class="block-head"><h2>サクラチェッカーで確かめる</h2><span class="idx">CHECK IT YOURSELF</span></div>
  <p class="block-lede">この資料を作った環境からは <b>サクラチェッカー（sakura-checker.jp）への接続が遮断されており、こちらで判定を実行できませんでした。</b>代わりに、商品ごとの判定ページへのリンクを用意しました。クリックすれば数秒で結果が出ます。<b>発注前にご確認ください。</b></p>
  <div class="panel">
    <ul class="sk-list">{sk_rows_html()}</ul>
    <p style="margin-top:16px">Amazon以外の販売ページ（サインモール・銀一・楽天・価格.com）は、サクラチェッカーの対象外です。これらは販売店の実在と価格をリンク先でご確認ください。</p>
  </div>
</section>

<section class="block">
  <div class="block-head"><h2>音声にいちばんお金をかけています</h2><span class="idx">WHY</span></div>
  <p class="block-lede">低価格版 {yen(LO)} のうち、音声だけで {yen(SOUND)}（レコーダー＋ガンマイク）を占めます。理由は三つです。</p>
  <div class="two-col">
    <div class="panel">
      <h3>インタビューが四人分ある</h3>
      <p>永尾社長・佐藤さん・くさがやさん・購入者。⑤は社長の声だけで全編が進む構成なので、音が悪いと企画そのものが成立しません。</p>
    </div>
    <div class="panel">
      <h3>32bitフロートで録音ミスが起きない</h3>
      <p>ZOOM H1essentialは録音レベルの設定を誤っても音が割れません。初心者がいちばんやりがちな失敗を、機材側で防げます。</p>
    </div>
    <div class="panel">
      <h3>工房の音を選んで拾える</h3>
      <p>RODEのガンマイクは指向性があるため、機械の音の中から刃の音・コバを磨く音だけを狙えます。②はこの音が主役です。</p>
    </div>
  </div>
</section>

<section class="block">
  <div class="block-head"><h2>選び方とサクラチェックについて</h2><span class="idx">HOW WE CHECKED</span></div>
  <div class="panel">
    <p><b>選び方：</b>カメラ用品はソニー純正、音声はZOOM・RODE・DJIという実績のあるメーカーの製品から選びました。無名ブランドの安価な音声機材は、レビューが操作されている可能性があるため外しています（前回案のワイヤレスピンマイク13,999円もこれに該当するため差し替えました）。</p>
    <p><b>評価の出どころ：</b>ZOOM H1essentialの評価（4.53／5・32件）は<b>Yahoo!ショッピングの掲載値</b>です。リンク先のAmazonの評価ではありません。</p>
    <p><b>サクラチェック：</b>サクラチェッカーへの接続がこの環境から遮断されているため、判定を実行できませんでした。上の「サクラチェッカーで確かめる」の各リンクから、発注前にご確認ください。</p>
    <p><b>マウントの確認：</b>マクロレンズはソニーEマウント専用です。お使いのカメラが別マウントの場合は、同じ焦点距離帯のものに読み替えてください（低価格版で二〜四万円、アップグレード版で五〜七万円が目安）。カメラの機種を教えていただければ、こちらで合うものを調べ直します。</p>
    <p><b>中古について：</b>アップグレード版のマクロレンズは中古価格です。新品にする場合は金額が上がります。</p>
  </div>
</section>

<footer class="foot">
  <div>この表と、同じ内容の編集用ファイル「01_撮影機材_低価格版とアップグレード版.xlsx」は同じデータから作っているので、金額が食い違うことはありません。撮影するカットの一覧は別資料「場面別ショットリスト」にあります。</div>
  <div style="margin-top:6px">BROOKLYN MUSEUM ／ 向島工房　動画制作</div>
</footer>

</div>
"""

if __name__ == "__main__":
    out = os.path.join(ROOT, "pdf", "gear.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(PAGE)
    print(f"{out}\n  ① {LO:,}円 ／ ② {MID:,}円 ／ ③ {UP:,}円")
