# -*- coding: utf-8 -*-
"""撮影の順番（ショットリスト）を、1日＝1シートの .dc.html で書き出す。
   実行: python3 tools/build_shotlist_canvas.py <出力ディレクトリ>

   ・何を撮るかは tools/deck_data.json（絵コンテ）から
   ・画角の並びと時刻は tools/build_script_canvas.py（台本）から
     ── 絵コンテ・台本・ショットリストの三つが食い違わないようにするため、ここには書かない
"""
import html, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_script_canvas as S

INK, MUTED, FAINT = S.INK, S.MUTED, S.FAINT
GOLD, LINE = S.GOLD, S.LINE
BAND = "#f6f2ec"
MARGIN = 44
PAGE_W = 1800

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
MARU = {"01": "①", "02": "②", "03": "③", "04": "④",
        "05": "⑤", "06": "⑥", "07": "⑦", "08": "⑧"}

# 一日ぶんの組み立て。順番は、場所を動かさずに済む順に組んでいる
# インタビューの日に先に撮ってしまうカット（本, シーン, カット番号）
MOVED = {("05", 1): [3], ("05", 6): [1], ("05", 8): [1, 2],
         ("06", 2): [3], ("06", 8): [3]}

DAYS = [
 dict(key="d1", no="一日目", place="向島工房", theme="窓の光だけで撮る日",
      lead="照明を持ち込まず、窓の光と三脚だけで撮れる一本から始める。同じ作業が何度もくり返される場所なので、撮り直しがきく。",
      gear="カメラ／三脚／ガンマイク／白い板（発泡スチロール）／脚立／養生テープ",
      keys=["蛍光灯と窓の光を混ぜない。どちらか一方に揃える。",
            "明るさとホワイトバランスはマニュアルで固定する。",
            "一カットは十秒回す。使うのは一〜二秒でも、前後に余裕がないとつながらない。"],
      blocks=[("02", [1, 2, 3, 4, 5, 6, 7, 8, 9])]),

 dict(key="d2", no="二日目", place="向島工房・店舗", theme="三人の話を録る日",
      lead="⑤と⑥の語りを、この日に全部録り切る。三日目からは、録れた声に画を当てていく。声が先にあると、どの画を何秒使うかが決まるので、撮る量に無駄が出ない。",
      gear="カメラ／三脚／ピンマイク 三本／白い板／予備の電池とカード",
      keys=["窓を横に置く。背にすると顔が黒くつぶれ、向くと目が細くなる。",
            "カメラは目の高さ、バストショットで固定。話が長くなっても画角は変えない。",
            "質問者はカメラのすぐ横に座る。カメラを直接見てもらわない。",
            "話し終わって三秒待ってから止める。録った音は、その日のうちに一度通して聞く。"],
      talks=[("9:30〜11:00", "永尾社長", "向島工房のインタビューの一角（窓を横に）",
              "⑤の語りを全部。<br>画は <b>S1③</b>（バストショット）と <b>S8</b>（締めの一言）。",
              "S1③とS8は同じ画角のまま続けて撮る。締めの一言は、収録の最後に一本言い切ってもらう。"),
             ("11:15〜12:45", "佐藤さん", "向島工房（梱包の台の横・窓を横に）",
              "⑥の語りを全部（九工程ぶん）。<br>画は <b>S2③</b>（引き）と <b>S8③</b>（バストショット）。",
              "工程の順に話してもらう。あとで画を当てやすい。機械の名前は言わない。"),
             ("14:30〜15:30", "くさがやさん", "店内（窓を横に）",
              "⑤の語りのうち、店のところ。<br>画は <b>S6①</b>（横顔）。",
              "空いた側に見出しテロップが入るので、画面の片側を空けて撮る。")]),

 dict(key="d3", no="三日目", place="向島工房", theme="順路どおりに歩いて撮る日",
      lead="二日目に録れた佐藤さんの語りに合わせて、入口から梱包まで工程の順に一度で回る。撮った順が、そのまま編集の順になる。",
      gear="カメラ（広角）／三脚／ガンマイク／白い板",
      keys=["入口から順路どおりに撮る。あとで並べ替えない。",
            "一工程につき三カット ── ①場所の引き ②手元の寄り ③道具の超クローズ。",
            "工房は狭いので、望遠ではなく広角で近づく。"],
      blocks=[("06", [1, 2, 3, 4, 5, 6, 7, 8, 9])]),

 dict(key="d4", no="四日目", place="向島工房", theme="空から入る日／照明をつくる日",
      lead="午前に空撮と、永尾社長の語りに当てる画。午後は窓を塞ぎ、ライト一灯だけで撮る。午後の一本は人を待たせないので、納得いくまで撮り直せる。",
      gear="ドローン／カメラ／三脚／白い板／黒い布／段ボール／ライト一灯",
      keys=["空撮は、建物に寄っていく動きを何度か撮って選ぶ。",
            "暗い一本はライト一灯だけ。当たっていない側は黒く落とし、レフ板で起こさない。",
            "シャッターが遅くなるので三脚は必須。ピントは手で合わせて固定する。"],
      blocks=[("05", [1, 3, 4, 5]), ("03", [1, 2, 3, 4, 5])]),

 dict(key="d5", no="五日目", place="店舗・屋上", theme="店とお客さまの日",
      lead="午前が店の顔、午後が購入者のインタビュー。屋上は斜めの光が出る時間に合わせる。",
      gear="カメラ／三脚／ピンマイク／PLフィルター／白い板／手前に置く植物",
      keys=["店の外観は午前。看板に日が当たる時間に撮る。",
            "ショーウィンドウ越しは、向かいの建物が映り込まない立ち位置を先に探す。",
            "購入者のインタビューはバストショットで固定。質問はテロップで出し、声で質問しない。"],
      blocks=[("05", [2, 6, 7]), ("08", [1, 2, 3, 4, 5, 6, 7, 8])]),

 dict(key="d6", no="六日目", place="店舗の事務所", theme="机だけを撮る日",
      lead="机が一つと横からの窓があれば撮れる。三脚を立てたら、最後まで触らない。",
      gear="カメラ／三脚／ガンマイク／白い板／鞄に入れる物 一式（A4書類・13インチPC・手帳・鍵・サングラス・ペン・傘・水筒）",
      keys=["十四カット全部が同じ画角。三脚を立てたら最後まで触らない。",
            "机の後ろは何もない壁を選ぶ。棚やコードが映ると、そこに目が行く。",
            "物を置く速さを一定にする。この一本は音がすべて。一度通してから本番。"],
      blocks=[("07", [1, 2, 3, 4, 5])]),

 dict(key="d7", no="七日目", place="すみだリバーウォーク・隅田公園・東京ミズマチ", theme="曇りの日に撮る",
      lead="屋外の一本だけ。晴れの正午は影が真下に出て鞄の形がつぶれるので、曇りの日を待って撮る。",
      gear="カメラ／三脚／脚立／水準器",
      keys=["三脚を止めて、背景だけを動かす。",
            "顔を主役にしない。顔が入りそうならカメラの高さを腰まで下げる。",
            "雨上がりの翌日は避ける。濡れた地面が白く光って革の色が出ない。"],
      blocks=[("04", [1, 2, 3, 4])]),

 dict(key="d8", no="八日目", place="東京国際フォーラム ガラス棟", theme="四色をそろえる日",
      lead="出演者と衣装・鞄を四色ぶん用意して、平日の午前に一度で撮り切る。撮影は事前に申請する。",
      gear="カメラ／三脚／三脚キャスター／養生テープ／衣装と鞄 四色ぶん",
      keys=["四色ぶんは同じ立ち位置で撮る。床にテープで足の位置を貼る。",
            "カメラの高さは胸で固定し、最後まで変えない。",
            "床の目地・段差・継ぎ目を先に見る。十メートル継ぎ目なしで走れるところを探す。"],
      blocks=[("01", [1, 2, 3, 4, 5, 6])]),
]


def esc(s):
    return html.escape(s, quote=True)


def plain(s):
    s = re.sub(r"<br\s*/?>", " ", s or "")
    return re.sub(r"<[^>]+>", "", s).strip()


def pages():
    data = json.load(open(os.path.join(ROOT, "tools", "deck_data.json"), encoding="utf-8"))
    return {p["no"]: p for p in data["pages"]}


PG = pages()


def split_cam(cam):
    """カメラの一文を「画角の並び」と「気をつけること」に分ける"""
    if "<br>" in cam:
        a, b = cam.split("<br>", 1)
    elif "。<b>" in cam:
        i = cam.index("。<b>")
        a, b = cam[:i + 1], cam[i + 1:]
    else:
        a, b = cam, ""
    return a.strip(), b.strip()


def cuts_of(no, si):
    nm, tm, shots = PG[no]["rows"][si - 1]
    return nm, [s for s in shots if s[1] != "―"]


def is_edit_only(no, si):
    _, _, day, _ = S.SPOT[no][si]
    return day == "―"


def day_counts(day):
    if day.get("talks"):
        return sum(len(v) for v in MOVED.values()), 0
    shoot = edit = 0
    for no, sis in day.get("blocks", []):
        for si in sis:
            n = len(cuts_of(no, si)[1]) - len(MOVED.get((no, si), []))
            if is_edit_only(no, si):
                edit += n
            else:
                shoot += n
    return shoot, edit


def day_span(day):
    ts = []
    if day.get("talks"):
        ts = [t for t, *_ in day["talks"]]
        return ts[0].split("〜")[0] + "〜" + ts[-1].split("〜")[1]
    for no, sis in day.get("blocks", []):
        for si in sis:
            _, _, _, t = S.SPOT[no][si]
            if t != "―":
                ts.append(t)
    if not ts:
        return ""
    first = min(ts, key=lambda t: [int(x) for x in t.split("〜")[0].split(":")])
    last = max(ts, key=lambda t: [int(x) for x in t.split("〜")[1].split(":")])
    return first.split("〜")[0] + "〜" + last.split("〜")[1]


# ─────────────────────────────────────────────────────────────
def scene_row(no, si):
    nm, cuts = cuts_of(no, si)
    place, _, _, when = S.SPOT[no][si]
    cam, note = split_cam(S.D[no][si][0])
    td = f"padding: 15px 16px; border-bottom: 1px solid {LINE}; vertical-align: top"
    edit = is_edit_only(no, si)
    tcell = (f'<span style="color: {FAINT}">撮影しない（編集で作る）</span>' if edit
             else f'<span style="font-size: 19px; font-weight: 700; color: {GOLD}">{esc(when)}</span>')
    mv = MOVED.get((no, si), [])
    cnt = f'{len(cuts) - len(mv)}カット'
    if mv:
        cnt += f'<br><span style="color: {GOLD}">{"".join("①②③④⑤⑥⑦⑧⑨"[k - 1] for k in mv)}は二日目</span>'
    return f'''<tr>
      <td style="{td}; padding-left: 0; white-space: nowrap">{tcell}</td>
      <td style="{td}">
        <div style="font-size: 19px; font-weight: 700; color: {INK}">{esc(nm)}</div>
        <div style="font-size: 15px; color: {FAINT}; margin-top: 4px; line-height: 1.6">{cnt}</div>
      </td>
      <td style="{td}; font-size: 17px; line-height: 1.7; color: {INK}">{place if place != "同じ" else f'<span style="color:{MUTED}">同じ</span>'}</td>
      <td style="{td}; font-size: 17px; line-height: 1.75; color: {INK}">{cam}</td>
      <td style="{td}; padding-right: 0; font-size: 16px; line-height: 1.75; color: {MUTED}">{note}</td>
    </tr>'''


def band_row(no):
    pg = PG[no]
    return f'''<tr>
      <td colspan="5" style="background: {BAND}; padding: 13px 0 13px 0; border-bottom: 1px solid {LINE}">
        <div style="display: flex; align-items: baseline; gap: 14px; padding: 0 4px">
          <div style="font-size: 21px; font-weight: 700; color: {GOLD}">{MARU[no]}</div>
          <div style="font-size: 20px; font-weight: 700; color: {INK}">{esc(pg["jp"])}</div>
          <div style="font-size: 15px; color: {FAINT}">{esc(pg["en"])}</div>
          <div style="margin-left: auto; font-size: 15px; color: {MUTED}; padding-right: 4px">{esc(plain(pg["meta_len"]))}</div>
        </div>
      </td>
    </tr>'''


def talk_rows(day):
    out = []
    td = f"padding: 18px 16px; border-bottom: 1px solid {LINE}; vertical-align: top"
    for when, who, place, what, note in day["talks"]:
        out.append(f'''<tr>
      <td style="{td}; padding-left: 0; white-space: nowrap">
        <span style="font-size: 19px; font-weight: 700; color: {GOLD}">{esc(when)}</span></td>
      <td style="{td}"><div style="font-size: 20px; font-weight: 700; color: {INK}">{esc(who)}</div></td>
      <td style="{td}; font-size: 17px; line-height: 1.7; color: {INK}">{place}</td>
      <td style="{td}; font-size: 17px; line-height: 1.75; color: {INK}">{what}</td>
      <td style="{td}; padding-right: 0; font-size: 16px; line-height: 1.75; color: {MUTED}">{note}</td>
    </tr>''')
    return "".join(out)


def day_artboard(day):
    shoot, edit = day_counts(day)
    th = ("text-align: left; font-size: 15px; font-weight: 400; color: " + FAINT +
          "; letter-spacing: 0.08em; border-bottom: 1px solid " + INK + "; padding-bottom: 11px")
    rows = []
    if day.get("talks"):
        rows.append(talk_rows(day))
    else:
        for no, sis in day["blocks"]:
            rows.append(band_row(no))
            for si in sis:
                rows.append(scene_row(no, si))
    keys = "".join(
        f'<div style="display: flex; gap: 10px; margin-top: 7px">'
        f'<div style="flex: 0 0 14px; color: {GOLD}">・</div><div>{k}</div></div>' for k in day["keys"])
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
  </style>
</helmet>
<div style="width: {PAGE_W}px; height: {HEIGHT[day["key"]]}px; background: #ffffff; padding: {MARGIN}px; box-sizing: border-box; display: flex; flex-direction: column; gap: 20px">
  <div style="display: flex; align-items: baseline; gap: 16px; border-bottom: 2px solid {INK}; padding-bottom: 14px">
    <div style="font-size: 34px; font-weight: 700; color: {INK}">{esc(day["no"])}</div>
    <div style="font-size: 22px; font-weight: 700; color: {GOLD}">{esc(day["place"])}</div>
    <div style="font-size: 18px; color: {MUTED}">{esc(day["theme"])}</div>
    <div style="margin-left: auto; font-size: 17px; font-weight: 700; color: {INK}">{esc(day_span(day))}</div>
    <div style="font-size: 15px; color: {FAINT}">撮るカット {shoot}{"（ほかに編集で作る " + str(edit) + "）" if edit else ""}</div>
  </div>
  <div style="font-size: 17px; line-height: 1.8; color: {MUTED}">{day["lead"]}</div>
  <table>
    <colgroup>
      <col style="width: 168px"><col style="width: 232px"><col style="width: 330px"><col style="width: 500px"><col>
    </colgroup>
    <tr>
      <th style="{th}; padding-left: 0">時 刻</th>
      <th style="{th}; padding-left: 16px">{"話 す 人" if day.get("talks") else "シ ー ン"}</th>
      <th style="{th}; padding-left: 16px">場 所 （ セ ッ ト ）</th>
      <th style="{th}; padding-left: 16px">{"録 る こ と ・ 撮 る 画" if day.get("talks") else "画 角 の 並 び"}</th>
      <th style="{th}; padding-left: 16px">気 を つ け る こ と</th>
    </tr>
    {"".join(rows)}
  </table>
  <div style="display: flex; gap: 44px; margin-top: 8px; border-top: 1px solid {LINE}; padding-top: 20px">
    <div style="flex: 0 0 460px">
      <div style="font-size: 15px; color: {FAINT}; letter-spacing: 0.08em; margin-bottom: 9px">持 ち 物</div>
      <div style="font-size: 17px; line-height: 1.9; color: {INK}">{day["gear"]}</div>
    </div>
    <div style="flex: 1">
      <div style="font-size: 15px; color: {FAINT}; letter-spacing: 0.08em; margin-bottom: 4px">こ の 日 の 要 点</div>
      <div style="font-size: 17px; line-height: 1.8; color: {INK}">{keys}</div>
    </div>
  </div>
  <div style="margin-top: auto; display: flex; justify-content: space-between; font-size: 13px; color: {FAINT}">
    <div>BROOKLYN MUSEUM ／ 向島工房　動画制作　／　撮影の順番</div>
    <div>{esc(day["no"])}</div>
  </div>
</div>
</x-dc>
</body>
</html>
'''


def cover_artboard():
    th = ("text-align: left; font-size: 15px; font-weight: 400; color: " + FAINT +
          "; letter-spacing: 0.08em; border-bottom: 1px solid " + INK + "; padding-bottom: 11px")
    td = f"padding: 20px 16px; border-bottom: 1px solid {LINE}; vertical-align: top"
    rows = []
    tot_s = tot_e = 0
    for d in DAYS:
        s, e = day_counts(d)
        tot_s += s
        tot_e += e
        if d.get("talks"):
            books = (f'<div style="margin-top: 5px">永尾社長・佐藤さん・くさがやさん　'
                     f'<span style="color: {FAINT}">⑤と⑥の語りを全部</span></div>')
        else:
            books = "".join(
                f'<div style="margin-top: 5px"><span style="color: {GOLD}; font-weight: 700">{MARU[no]}</span>'
                f'　{esc(PG[no]["jp"])}<span style="color: {FAINT}">　{esc(plain(PG[no]["meta_len"]))}</span></div>'
                for no, _ in d["blocks"])
        rows.append(f'''<tr>
      <td style="{td}; padding-left: 0"><div style="font-size: 23px; font-weight: 700; color: {INK}">{esc(d["no"])}</div>
        <div style="font-size: 16px; color: {MUTED}; margin-top: 5px">{esc(d["theme"])}</div></td>
      <td style="{td}; font-size: 18px; font-weight: 700; color: {INK}">{esc(d["place"])}</td>
      <td style="{td}; font-size: 18px; color: {INK}">{books}</td>
      <td style="{td}; font-size: 18px; font-weight: 700; color: {GOLD}; white-space: nowrap">{esc(day_span(d))}</td>
      <td style="{td}; padding-right: 0; font-size: 18px; color: {INK}; white-space: nowrap">{s}カット</td>
    </tr>''')
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
  </style>
</helmet>
<div style="width: {PAGE_W}px; height: {HEIGHT["cover"]}px; background: #ffffff; padding: {MARGIN}px; box-sizing: border-box; display: flex; flex-direction: column; gap: 22px">
  <div style="border-bottom: 2px solid {INK}; padding-bottom: 16px">
    <div style="font-size: 15px; font-weight: 700; color: {GOLD}; letter-spacing: 0.14em">BROOKLYN MUSEUM ／ 向島工房</div>
    <div style="display: flex; align-items: baseline; gap: 18px; margin-top: 10px">
      <div style="font-size: 40px; font-weight: 700; color: {INK}; letter-spacing: -0.01em">動画八本　撮影の順番</div>
      <div style="font-size: 17px; color: {FAINT}; letter-spacing: 0.06em">Shooting Order</div>
      <div style="margin-left: auto; font-size: 18px; font-weight: 700; color: {INK}">全八本　{tot_s + tot_e}カット　／　撮影 八日</div>
    </div>
  </div>
  <div style="font-size: 18px; line-height: 1.9; color: {MUTED}">
    <b>二日目に三人の語りを全部録り、そのあとの日は、録れた声に画を当てていきます。</b>声が先にあると、<br>
    どの画を何秒使うかが決まるので、撮る量に無駄が出ません。一日目は、照明を持ち込まずに撮れる②で手を慣らします。<br>
    出演者の手配が要る①④⑦と購入者インタビュー⑧は、あとの四日に置いています。<br>
    {tot_s}カットを撮影し、残りの{tot_e}カット（白バックと文字だけの画面）は編集で作ります。
  </div>
  <table>
    <colgroup>
      <col style="width: 250px"><col style="width: 330px"><col><col style="width: 210px"><col style="width: 160px">
    </colgroup>
    <tr>
      <th style="{th}; padding-left: 0">日　／　ね ら い</th>
      <th style="{th}; padding-left: 16px">場 所</th>
      <th style="{th}; padding-left: 16px">撮 る 本</th>
      <th style="{th}; padding-left: 16px">時 間</th>
      <th style="{th}; padding-left: 16px">カ ッ ト</th>
    </tr>
    {"".join(rows)}
  </table>
  <div style="border-top: 1px solid {LINE}; padding-top: 20px; display: flex; gap: 44px">
    <div style="flex: 1">
      <div style="font-size: 15px; color: {FAINT}; letter-spacing: 0.08em; margin-bottom: 9px">先 に 決 め て お く こ と</div>
      <div style="font-size: 17px; line-height: 1.9; color: {INK}">
        二日目 ── 三人の予定を一日で押さえる。永尾社長・佐藤さんが工房、くさがやさんが店。<br>
        五日目 ── 購入者インタビューの出演者と、顔出しの範囲。予定が合わないときは、午前の⑤だけで終える。<br>
        六日目 ── 鞄に物を入れて持ち出す方。顔は映らないので、手と肩だけ。<br>
        七日目 ── 曇りの日に合わせるため、前後に予備日を一日置く。<br>
        八日目 ── 出演者と、衣装・鞄 四色ぶん。会場の撮影申請。
      </div>
    </div>
    <div style="flex: 1">
      <div style="font-size: 15px; color: {FAINT}; letter-spacing: 0.08em; margin-bottom: 9px">全 日 に 共 通 す る こ と</div>
      <div style="font-size: 17px; line-height: 1.9; color: {INK}">
        明るさとホワイトバランスはマニュアルで固定する。<br>
        一カットは十秒回す。使うのは一〜二秒でも、前後に余裕がないとつながらない。<br>
        同じ動作は三回撮る ── 手が入る前、動作中、手が抜けたあと。
      </div>
    </div>
  </div>
  <div style="margin-top: auto; display: flex; justify-content: space-between; font-size: 13px; color: {FAINT}">
    <div>BROOKLYN MUSEUM ／ 向島工房　動画制作　／　撮影の順番</div>
    <div>表紙</div>
  </div>
</div>
</x-dc>
</body>
</html>
'''


# 実際に描かせて測った高さ
HEIGHT = {"cover": 1342, "d1": 1277, "d2": 788, "d3": 1347,
          "d4": 1357, "d5": 1513, "d6": 937, "d7": 859, "d8": 1011}


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    arts, x, y, col = [], 0, 0, 0
    items = [("Main", "cover", cover_artboard)] + [
        (d["key"].upper(), d["key"], (lambda dd: (lambda: day_artboard(dd)))(d)) for d in DAYS]
    for name, key, fn in items:
        f = name + ".dc.html"
        with open(os.path.join(outdir, f), "w", encoding="utf-8") as fh:
            fh.write(fn())
        arts.append({"file": f, "x": x, "y": y, "w": PAGE_W, "h": HEIGHT[key]})
        col += 1
        if col % 4 == 0:
            x, y = 0, y + max(HEIGHT.values()) + 120
        else:
            x += PAGE_W + 120
        print(f, PAGE_W, HEIGHT[key])
    with open(os.path.join(outdir, "canvas.json"), "w", encoding="utf-8") as fh:
        json.dump({"artboards": arts, "launch": {"view": "canvas"}}, fh, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "shotlist_out"))
