# -*- coding: utf-8 -*-
"""BGMの選び方（8本ぶんの音楽の方向 ＋ どこで買うか）のデザインキャンバスを書き出す。
   実行: python3 tools/build_bgm_canvas.py <出力ディレクトリ>
"""
import html, json, os, sys

INK, MUTED, FAINT = "#15191c", "#5b6266", "#8a8f92"
GOLD, LINE, PAPER = "#a8672a", "#ded9d0", "#fbfaf7"
MARGIN = 40
PAGE_W = 1640
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

HEIGHT = {"A": 1091, "B": 1257}


def esc(s):
    return html.escape(s, quote=True)


INTRO_A = (
    "「品がいい」を音で言うと、<b>派手にしない・メロディを立てすぎない・生の楽器の音</b>、の三つになる。"
    "ピアノ、アコースティックギター、弦、軽いパーカッション。打ち込みの派手な音と、"
    "歌の入った曲は八本とも使わない。<br><br>"
    "<b>八本の曲をばらばらに選ばない。</b>同じサービスの、できれば同じ作曲家・同じアルバムから選ぶ。"
    "並べたときに一つのブランドに見えるかどうかは、映像より先に音で決まる。"
    "<span style='color:#a8763e'>キーワードは英語で検索する。日本語で探すと候補がほとんど出てこない。</span>"
)

# 本 → （役割 ／ テンポ・楽器 ／ 展開 ／ 検索キーワード）
MUSIC = [
 ("01", "服装ごとに画が変わる", "30秒",
  "<b>音楽が主役。</b>セリフがないので、カットの切り替わりを音に合わせる。",
  "<b>100〜115BPM。</b>ピアノ＋軽いパーカッション＋ベース。明るいが、軽薄にしない。",
  "四秒ごとに小さなアクセントが来る曲を選び、<b>色が替わる位置に合わせる。</b>"
  "二十五秒で一段落として、ナレーション「毎日をカラフルに」が入る隙間を作る。",
  "uplifting minimal pop ／ light indie pop ／ playful piano beat ／ fashion lookbook upbeat"),
 ("02", "ASMRで製造の姿を撮る", "40秒",
  "<b>音楽は脇役。作業音が主役。</b>メロディが立つ曲を選ぶと、刃の音と槌の音が消える。",
  "<b>70〜85BPM。</b>ピアノ単体か、弦の持続音（ドローン）だけ。",
  "<b>コバ塗り（27-33秒）でさらに一段下げる。</b>四十秒で無音に落として終わる。",
  "ambient underscore ／ minimal piano bed ／ sparse cinematic texture ／ documentary underscore"),
 ("03", "暗めでエレガントにブランドを映す", "28秒",
  "<b>音楽だけで持たせる。</b>作業音もテロップも入れない、唯一の一本。",
  "<b>60〜75BPM。</b>低い弦＋ピアノの単音＋かすかなシンセ。暗く、重心を低く。",
  "<b>無音から立ち上がり、十九秒（完成品が明るい作業台に立つ）で一度だけ開く。</b>"
  "二十八秒でロゴとともに終わる。",
  "dark elegant cinematic ／ luxury brand film ／ slow build strings ／ minimal dark piano"),
 ("04", "鞄を持って街を歩く（海外ドラマ風）", "30秒",
  "街の環境音の下に薄く敷くだけ。",
  "<b>85〜100BPM。</b>アコースティックギターかエレピ。都会的で、乾いた音。",
  "<b>平坦でよい。盛り上げない。</b>置き画で終わるので、最後は自然に消す。",
  "chill lo-fi acoustic ／ urban minimal groove ／ clean guitar loop ／ understated fashion"),
 ("05", "コーポレートムービー", "75秒",
  "<b>語りの下地。</b>声を邪魔しないことがいちばん大事。",
  "<b>75〜90BPM。</b>ピアノ＋弦。<b>中域が空いている曲</b>を選ぶ（声の帯域とぶつからない）。",
  "S2（歴史）で一度厚くし、S8（締め）でまた薄くする。<b>永尾社長の締めの一言の下では、ほぼ聞こえないところまで下げる。</b>",
  "corporate documentary warm ／ hopeful piano strings ／ company profile film ／ understated inspiring"),
 ("06", "OEM工房案内", "2分20秒",
  "<b>語りの下地。</b>二分二十秒あるので、一本調子の曲だと途中で飽きる。",
  "<b>80〜95BPM。⑤と同じ作曲家の別の曲</b>にすると、二本が姉妹に見える。",
  "工程が進むにつれて楽器が増えていく曲を選ぶ。<b>締めカード（133秒〜）で切る。</b>"
  "<span style='color:#a8763e'>展示会用の無音版では、ここも含めて音を全部外す。</span>",
  "manufacturing documentary ／ steady rhythmic underscore ／ industrial warm minimal ／ factory tour"),
 ("07", "製品の中身と使い勝手", "25秒",
  "入れる音を聞かせたいので、音楽はいちばん薄く。",
  "<b>95〜110BPM。</b>軽いパーカッションと、短いメロディだけ。",
  "<b>二十秒（何も乗っていない机だけが残る）で一段落として、テロップを見せる。</b>",
  "light minimal pop ／ clean product video ／ simple percussive loop ／ morning routine"),
 ("08", "購入者インタビュー", "60秒",
  "<b>声の下地。八本でいちばん薄く。</b>",
  "<b>70〜85BPM。</b>ピアノかアコースティックギターの単音。",
  "<b>S7（見送り）で一度だけ上げ、白に抜けるところで切る。</b>",
  "warm acoustic underscore ／ customer story ／ gentle documentary bed ／ sincere piano"),
]

SHOPS = [
 ("無料", "DOVA-SYNDROME（日本）", "商用利用可。クレジット表示は原則不要（作曲者が個別に条件を付けている曲もある）。",
  "<b>まずはここ。</b>曲数がいちばん多く、<b>作曲者のページから同じ人の曲を辿れる</b>ので、"
  "八本を一人の作曲者で揃えられる。規約が日本語。2026年3月から株式会社TRACKSが運営。",
  "https://dova-s.jp/"),
 ("無料", "甘茶の音楽工房（日本）", "商用利用可。クレジット表示不要。",
  "落ち着いたピアノとアコースティックが多く、<b>この八本の方向にいちばん近い。</b>"
  "曲数はDOVAより少ないので、二つ見て決めるとよい。",
  "https://amachamusic.chagasi.com/"),
 ("無料", "MusMus（日本）", "商用利用可。クレジット表示不要。",
  "静かな曲・アンビエントが多い。<b>②③⑧のような、音楽を前に出したくない本に向く。</b>",
  "https://musmus.main.jp/"),
 ("無料", "魔王魂（日本）", "商用利用可（規約は必ず確認）。",
  "日本でいちばん名前が知られている。<b>曲がかぶりやすい</b>ので、"
  "ブランド映像で使うなら他と比べてから決める。",
  "https://maou.audio/"),
 ("無料", "Pixabay Music", "商用利用可。クレジット表示不要。",
  "海外の曲。<b>左の表の英語キーワードがそのまま使える。</b>ピアノ・アンビエントの層が厚い。",
  "https://pixabay.com/music/"),
 ("無料", "YouTube オーディオ ライブラリ", "商用利用可。<b>ただし曲ごとに条件が違う</b>（クレジット必須の曲がある）。",
  "YouTube以外でも使える。曲を選ぶたびにライセンス欄を確認すること。YouTubeのアカウントが必要。",
  "https://studio.youtube.com/"),
 ("無料〜", "Uppbeat", "商用利用可。<b>無料プランはクレジット表示が必要。</b>有料にすると不要。",
  "曲の質は無料の中でいちばん高い。<b>クレジットを出したくないときだけ月額（数百円台）にする。</b>",
  "https://uppbeat.io/"),
 ("有料", "Artlist", "商用・放送まで。クレジット不要。使えるアカウント数に制限なし。",
  "<b>八本まとめて有料にするならこれ。</b>曲の質がそろっていて、同じ作曲家で八本を統一しやすい。"
  "<span style='color:#a8763e'>年 $299 前後（目安）</span>",
  "https://artlist.io/pricing"),
 ("有料", "Epidemic Sound", "商用可。Instagram・TikTokでの著作権の申し立てから守られる。",
  "安く始められる。<b>リール中心ならこれで足りる。</b>アカウント数に上限がある。"
  "<span style='color:#a8763e'>月 $25 ／ 年 $300 前後（目安）</span>",
  "https://www.epidemicsound.com/pricing/"),
 ("有料", "Audiostock（日本）", "商用可。<b>1曲ごとの買い切り</b>で、継続課金なしで使い続けられる。",
  "<b>日本語でサポートが受けられる。</b>月額を持ちたくない場合はこれ。曲ごとに探す手間はかかる。",
  "https://audiostock.jp/"),
 ("有料", "Musicbed", "商用・ブランド映像向け。クレジット不要。",
  "曲の格はいちばん高いが、単価も高い。<b>③のような一本だけに使うなら検討の価値あり。</b>",
  "https://www.musicbed.com/pricing"),
]

NOTES = [
 ("ま ず は 無 料 で 十 分",
  "<b>八本とも無料で揃えられます。</b>上の七つはいずれも商用利用が認められています。"
  "<b>同じ作曲者の曲を八本ぶん選べば、無料でも統一感は作れます。</b>"
  "DOVA-SYNDROMEも甘茶の音楽工房も、作曲者のページから同じ人の他の曲を辿れます。"),
 ("規 約 は 曲 ご と に 違 う",
  "<b>「商用利用可」のサイトでも、作曲者が個別の条件を付けていることがあります</b>"
  "（クレジット表示が必要、改変禁止、など）。"
  "<span style='color:#a8763e'>使う前に、その曲のページを必ず最後まで読む。</span>"),
 ("使 っ た 曲 の 記 録 を 残 す",
  "曲名・作曲者名・ダウンロードしたURL・取得日を一覧にして、"
  "<b>そのときの規約ページをスクリーンショットで保存しておく。</b>"
  "規約はあとから変わることがあり、使った時点の規約が証拠になります。"),
 ("有 料 を 検 討 す る な ら ③ だ け",
  "無料の弱点は<b>他社の動画と曲がかぶること。</b>八本のうち<b>③（The Making of the Voyage）だけは"
  "音楽だけで持たせる一本</b>なので、曲の格がそのまま作品の格になります。ここだけ有料、という使い分けが現実的です。<br>"
  "また、<b>Instagramの編集画面から選べる内蔵音源は使わない。</b>"
  "ビジネスアカウントでは使えない曲が多く、あとから音だけ消されることがあります。<br>"
  "<span style='color:#a8763e'>有料の金額は外部の記事に出ている目安で、こちらでは確認できていません。契約前に公式ページで確認を。</span>"),
]


def head(no, jp, en, badge):
    return f'''<div style="display: flex; flex-direction: column; gap: 9px; border-bottom: 2px solid {INK}; padding-bottom: 13px">
    <div style="display: flex; align-items: baseline; gap: 14px">
      <div style="font-size: 12px; font-weight: 700; color: {GOLD}; letter-spacing: 0.12em">{esc(no)}</div>
      <div style="font-size: 25px; font-weight: 700; color: {INK}; letter-spacing: -0.01em">{esc(jp)}</div>
      <div style="font-size: 13px; color: {FAINT}; letter-spacing: 0.06em">{esc(en)}</div>
      <div style="margin-left: auto; font-size: 11px; color: {GOLD}; border: 1px solid {LINE}; border-radius: 20px; padding: 3px 12px">{esc(badge)}</div>
    </div>'''


def page(inner, h):
    return f'''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap">
  <style>
    body {{ margin: 0; background: #ffffff;
      font-family: 'Zen Kaku Gothic New', 'Hiragino Sans', 'Yu Gothic', sans-serif; }}
    table {{ border-collapse: collapse; width: 100%; table-layout: fixed; }}
    a {{ color: {GOLD}; }}
  </style>
</helmet>
<div style="width: {PAGE_W}px; height: {h}px; background: #ffffff; padding: {MARGIN}px; box-sizing: border-box; display: flex; flex-direction: column; gap: 16px">
{inner}
  <div style="margin-top: auto; display: flex; justify-content: space-between; font-size: 10px; color: {FAINT}">
    <div>BROOKLYN MUSEUM ／ 向島工房　動画制作　／　BGM</div>
    <div>音楽の方向と、無料で揃える手順</div>
  </div>
</div>
</x-dc>
</body>
</html>
'''


def sheet_a():
    th = ("text-align: left; font-size: 12px; font-weight: 400; color: " + FAINT +
          "; letter-spacing: 0.08em; border-bottom: 1px solid " + INK)
    rows = "".join(f'''<tr>
      <td style="padding: 13px 12px 13px 0; border-bottom: 1px solid {LINE}; vertical-align: top">
        <div style="font-size: 12px; color: {GOLD}; font-weight: 700">{esc(no)}</div>
        <div style="font-size: 14px; font-weight: 700; color: {INK}; margin-top: 3px">{esc(jp)}</div>
        <div style="font-size: 12px; color: {MUTED}; margin-top: 3px">{esc(ln)}</div></td>
      <td style="padding: 13px 14px; border-bottom: 1px solid {LINE}; vertical-align: top; background: {PAPER}">
        <div style="font-size: 13px; line-height: 1.8; color: {INK}">{role}</div></td>
      <td style="padding: 13px 14px; border-bottom: 1px solid {LINE}; vertical-align: top">
        <div style="font-size: 13px; line-height: 1.8; color: {INK}">{tempo}</div></td>
      <td style="padding: 13px 14px; border-bottom: 1px solid {LINE}; vertical-align: top">
        <div style="font-size: 13px; line-height: 1.8; color: {INK}">{arc}</div></td>
      <td style="padding: 13px 0 13px 14px; border-bottom: 1px solid {LINE}; vertical-align: top">
        <div style="font-size: 12.5px; line-height: 1.85; color: {GOLD}">{esc(kw)}</div></td>
    </tr>''' for no, jp, ln, role, tempo, arc, kw in MUSIC)
    inner = f'''{head("別紙", "八本の音楽の方向", "Music Direction", "BGM")}
    <div style="font-size: 14px; line-height: 1.85; color: {INK}; max-width: 1400px">{INTRO_A}</div>
  </div>
  <table>
    <colgroup><col style="width: 190px"><col style="width: 300px"><col style="width: 300px"><col style="width: 360px"><col></colgroup>
    <tr>
      <th style="{th}; padding: 0 12px 7px 0">本 ／ 尺</th>
      <th style="{th}; padding: 0 14px 7px">音 楽 の 役 割</th>
      <th style="{th}; padding: 0 14px 7px">テ ン ポ ・ 楽 器</th>
      <th style="{th}; padding: 0 14px 7px">展 開 （ ど こ で 上 げ 下 げ す る か ）</th>
      <th style="{th}; padding: 0 0 7px 14px">検 索 キ ー ワ ー ド （ 英 語 ）</th>
    </tr>
    {rows}
  </table>'''
    return page(inner, HEIGHT["A"])


def sheet_b():
    th = ("text-align: left; font-size: 12px; font-weight: 400; color: " + FAINT +
          "; letter-spacing: 0.08em; border-bottom: 1px solid " + INK)
    rows = "".join(f"""<tr>
      <td style="padding: 13px 10px 13px 0; border-bottom: 1px solid {LINE}; vertical-align: top">
        <div style="font-size: 12px; font-weight: 700; color: {'#15191c' if kind.startswith('有料') else GOLD}">{esc(kind)}</div></td>
      <td style="padding: 13px 14px 13px 0; border-bottom: 1px solid {LINE}; vertical-align: top">
        <div style="font-size: 14px; font-weight: 700; color: {INK}">{esc(name)}</div>
        {'<div style="font-size: 11px; margin-top: 4px"><a href="' + esc(url) + '" target="_blank" rel="noopener" style="color: ' + GOLD + '; text-decoration: underline">' + esc(url.replace("https://", "").rstrip("/")) + "</a></div>" if url else ""}</td>
      <td style="padding: 13px 14px; border-bottom: 1px solid {LINE}; vertical-align: top; background: {PAPER}">
        <div style="font-size: 13px; line-height: 1.75; color: {INK}">{scope}</div></td>
      <td style="padding: 13px 0 13px 14px; border-bottom: 1px solid {LINE}; vertical-align: top">
        <div style="font-size: 13px; line-height: 1.75; color: {INK}">{note}</div></td>
    </tr>""" for kind, name, scope, note, url in SHOPS)
    notes = "".join(f"""<div style="flex: 1; min-width: 0">
        <div style="font-size: 11.5px; color: {FAINT}; letter-spacing: 0.1em; margin-bottom: 6px">{esc(t)}</div>
        <div style="font-size: 13px; line-height: 1.8; color: {INK}">{b}</div>
      </div>""" for t, b in NOTES)
    inner = f'''{head("別紙", "どこで手に入れるか", "Where to Get the Music", "BGM")}
    <div style="font-size: 14px; line-height: 1.8; color: {INK}; max-width: 1400px">
      八本とも商用（EC・Instagram・商談・展示会）で使うので、<b>規約に「商用利用可」と書かれている音源だけを使ってください。</b>
      下は<b>よく使われている無料・有料のサイトをまとめたもの</b>です。<b>一つに決めて、八本ともそこから選ぶ。</b></div>
  </div>
  <table>
    <colgroup><col style="width: 76px"><col style="width: 250px"><col style="width: 430px"><col></colgroup>
    <tr>
      <th style="{th}; padding: 0 10px 8px 0">区 分</th>
      <th style="{th}; padding: 0 14px 8px 0">サ ー ビ ス</th>
      <th style="{th}; padding: 0 14px 8px">使 え る 範 囲</th>
      <th style="{th}; padding: 0 0 8px 14px">向 い て い る 点</th>
    </tr>
    {rows}
  </table>
  <div style="display: flex; gap: 30px; margin-top: 8px">{notes}</div>'''
    return page(inner, HEIGHT["B"])


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, "Main.dc.html"), "w", encoding="utf-8").write(sheet_a())
    open(os.path.join(outdir, "Video02.dc.html"), "w", encoding="utf-8").write(sheet_b())
    cv = {"artboards": [
        {"file": "Main.dc.html", "x": 0, "y": 0, "w": PAGE_W, "h": HEIGHT["A"]},
        {"file": "Video02.dc.html", "x": PAGE_W + 120, "y": 0, "w": PAGE_W, "h": HEIGHT["B"]},
    ], "launch": {"view": "canvas"}}
    json.dump(cv, open(os.path.join(outdir, "canvas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("BGM 2枚を書き出しました →", outdir)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "bgm_out"))
