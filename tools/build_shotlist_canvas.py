# -*- coding: utf-8 -*-
"""香盤表を、1日＝1シートの .dc.html で書き出す。
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
# インタビューの日に先に撮ってしまうカット（本, シーン）→ カット番号
MOVED = {("05", 1): [3], ("05", 6): [1], ("05", 8): [1, 2],
         ("06", 2): [3], ("06", 8): [3]}
TALK_DAY = "三日目"

DAYS = [
 dict(key="d1", no="一日目", place="向島工房", theme="窓の光だけで撮る日",
      lead="照明を持ち込まず、窓の光と三脚だけで撮れる一本から始める。四十秒の短い一本なので、撮って編集するまでを一度通せる。",
      gear="カメラ／三脚／ガンマイク／白い板（発泡スチロール）／脚立／養生テープ",
      keys=["蛍光灯と窓の光を混ぜない。どちらか一方に揃える。",
            "明るさとホワイトバランスはマニュアルで固定する。",
            "一カットは十秒回す。使うのは一〜二秒でも、前後に余裕がないとつながらない。"],
      blocks=[("02", [1, 2, 3, 4, 5, 6, 7, 8, 9])]),

 dict(key="d2", no="二日目", place="向島工房", theme="照明をつくる日",
      lead="窓を塞いだ一角で、ライト一灯だけで撮る。二十八秒の短い一本で、人を待たせないので納得いくまで撮り直せる。",
      gear="カメラ／三脚／黒い布／段ボール／ライト一灯／白い板",
      keys=["ライトは一灯だけ。当たっていない側は黒く落とし、レフ板で起こさない。",
            "シャッターが遅くなるので三脚は必須。ピントは手で合わせて固定する。",
            "背景の黒い布は、たるませずに張る。しわが光ると目立つ。"],
      blocks=[("03", [1, 2, 3, 4, 5])]),

 dict(key="d3", no="三日目", place="向島工房・店舗", theme="三人の話を録る日",
      lead="⑤と⑥の語りを、この日に全部録り切る。一人三十分。四日目からは、録れた声に画を当てていく。声が先にあると、どの画を何秒使うかが決まるので、撮る量に無駄が出ない。",
      gear="カメラ／三脚／ピンマイク 三本／白い板／予備の電池とカード",
      keys=["窓を横に置く。背にすると顔が黒くつぶれ、向くと目が細くなる。",
            "カメラは目の高さ、バストショットで固定。話が長くなっても画角は変えない。",
            "質問者はカメラのすぐ横に座る。カメラを直接見てもらわない。",
            "話し終わって三秒待ってから止める。",
            "シーンごとに区切って録る。三十分に収めるには、通しで話さず、言い直したところだけ録り直す。",
            "録った音は、その場で聞き返す。聞き取れないところは、その人がいるうちに録り直す。"],
      talks=[("9:30〜10:00", "永尾社長", "向島工房のインタビューの一角（窓を横に）",
              "⑤の語りを全部（七十五秒ぶん・八シーン）。<br>画は <b>S1③</b>（バストショット）と <b>S8</b>（締めの一言）。",
              "シーンごとに区切って録る。S1③とS8は同じ画角のまま続けて撮る。"),
             ("10:15〜10:45", "佐藤さん", "向島工房（梱包の台の横・窓を横に）",
              "⑥の語りを全部（二分二十秒ぶん・九工程）。<br>画は <b>S2③</b>（引き）と <b>S8③</b>（バストショット）。",
              "工程ごとに区切って録る。話す順は工程の順。機械の名前は言わない。"),
             ("11:30〜12:00", "くさがやさん", "店内（窓を横に）",
              "⑤の語りのうち、店のところ（二シーン）。<br>画は <b>S6①</b>（横顔）。",
              "空いた側に見出しテロップが入るので、画面の片側を空けて撮る。")]),

 dict(key="d4", no="四日目", place="向島工房", theme="順路どおりに歩いて撮る日",
      lead="三日目に録れた佐藤さんの語りに合わせて、入口から梱包まで工程の順に一度で回る。撮った順が、そのまま編集の順になる。",
      gear="カメラ（広角）／三脚／ガンマイク／白い板",
      keys=["入口から順路どおりに撮る。あとで並べ替えない。",
            "一工程につき三カット ── ①場所の引き ②手元の寄り ③道具の超クローズ。",
            "工房は狭いので、望遠ではなく広角で近づく。"],
      blocks=[("06", [1, 2, 3, 4, 5, 6, 7, 8, 9])]),

 dict(key="d5", no="五日目", place="向島工房", theme="会社の仕事を撮る日",
      lead="永尾社長の語りに当てる画。空撮から入って、企画・設計・製造の順に撮る。企画と設計は工房の机で行われるので、この日にまとめて撮れる。",
      gear="ドローン／カメラ／三脚／白い板／脚立",
      keys=["空撮は、建物に寄っていく動きを何度か撮って選ぶ。",
            "企画も設計も工房の机。店舗へ移る必要はない。",
            "製造は工程の説明をしない。引き・機械・手元の三カットだけ。"],
      blocks=[("05", [1, 3, 4, 5])]),

 dict(key="d6", no="六日目", place="店舗・屋上", theme="店とお客さまの日",
      lead="午前が店の顔と接客、午後が購入者のインタビュー。購入の場面と使っている場面を続けて撮るので、出演していただく方は一度で済む。",
      gear="カメラ／三脚／ピンマイク／PLフィルター／白い板／手前に置く植物",
      keys=["店の外観は午前。看板に日が当たる時間に撮る。",
            "ショーウィンドウ越しは、向かいの建物が映り込まない立ち位置を先に探す。",
            "購入者のインタビューはバストショットで固定。質問はテロップで出し、声で質問しない。"],
      blocks=[("05", [2, 6, 7]), ("08", [1, 2, 3, 4, 5, 6, 7, 8])]),

 dict(key="d7", no="七日目", place="店舗の事務所", theme="机だけを撮る日",
      lead="机が一つと横からの窓があれば撮れる。三脚を立てたら、最後まで触らない。顔は映らないので、支度は手元だけ。",
      gear="カメラ／三脚／ガンマイク／白い板／鞄に入れる物 一式（A4書類・13インチPC・手帳・鍵・サングラス・ペン・傘・水筒）",
      keys=["十四カット全部が同じ画角。三脚を立てたら最後まで触らない。",
            "机の後ろは何もない壁を選ぶ。棚やコードが映ると、そこに目が行く。",
            "物を置く速さを一定にする。この一本は音がすべて。一度通してから本番。"],
      blocks=[("07", [1, 2, 3, 4, 5])]),

 dict(key="d8", no="八日目", place="すみだリバーウォーク・隅田公園・東京ミズマチ", theme="曇りの日に撮る",
      lead="屋外の一本だけ。晴れの正午は影が真下に出て鞄の形がつぶれるので、曇りの日を待って撮る。",
      gear="カメラ／三脚／脚立／水準器",
      keys=["三脚を止めて、背景だけを動かす。",
            "顔を主役にしない。顔が入りそうならカメラの高さを腰まで下げる。",
            "雨上がりの翌日は避ける。濡れた地面が白く光って革の色が出ない。"],
      blocks=[("04", [1, 2, 3, 4])]),

 dict(key="d9", no="九日目", place="東京国際フォーラム ガラス棟", theme="四色をそろえる日",
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
        cnt += f'<br><span style="color: {GOLD}">{"".join("①②③④⑤⑥⑦⑧⑨"[k - 1] for k in mv)}は{TALK_DAY}</span>'
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
    <div>BROOKLYN MUSEUM ／ 向島工房　動画制作　／　香盤表</div>
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
      <div style="font-size: 40px; font-weight: 700; color: {INK}; letter-spacing: -0.01em">動画八本　香盤表とショットリスト</div>
      <div style="font-size: 17px; color: {FAINT}; letter-spacing: 0.06em">Shooting Schedule &amp; Shot List</div>
      <div style="margin-left: auto; font-size: 18px; font-weight: 700; color: {INK}">全八本　{tot_s + tot_e}カット　／　撮影 九日</div>
    </div>
  </div>
  <div style="font-size: 18px; line-height: 1.9; color: {MUTED}">
    はじめの二日で短い二本（②③）を撮り、編集まで一度通します。<b>三日目に三人の語りを全部録り、四日目からは、<br>
    録れた声に画を当てていきます。</b>声が先にあると、どの画を何秒使うかが決まるので、撮る量に無駄が出ません。<br>
    出演者の手配が要る⑧⑦④①は、支度の重い順に、あとの四日へ置いています。<br>
    {tot_s}カットを撮影し、残りの{tot_e}カット（白バックと文字だけの画面）は編集で作ります。<br>
    日ごとの香盤表のあとに、<b>本ごとのショットリスト</b>を八枚付けています ── 一カット一行、画角と尺の目安、済のチェック欄つき。
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
        三日目 ── 三人の予定を一日で押さえる。永尾社長・佐藤さんが工房、くさがやさんが店。<br>
        六日目 ── 購入者インタビューの出演者と、顔出しの範囲。予定が合わないときは、午前の⑤だけで終える。<br>
        七日目 ── 鞄に物を入れて持ち出す方。顔は映らないので、手と肩だけ。<br>
        八日目 ── 曇りの日に合わせるため、前後に予備日を一日置く。<br>
        九日目 ── 出演者と、衣装・鞄 四色ぶん。会場の撮影申請。<br>
        <span style="color: #a8672a">出演者の支度は、最後の一枚「出演者と支度」にまとめています。</span>
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
    <div>BROOKLYN MUSEUM ／ 向島工房　動画制作　／　香盤表</div>
    <div>表紙</div>
  </div>
</div>
</x-dc>
</body>
</html>
'''


# ── ショットリスト（一カット一行） ──────────────────────────
CIR = "①②③④⑤⑥⑦⑧⑨"
SHOT_ORDER = ["02", "03", "06", "05", "08", "07", "04", "01"]


def shot_angles(no, si):
    """カメラの一文を①②③…で割って、カットごとの画角にする"""
    cam, _ = split_cam(S.D[no][si][0])
    idx = [(cam.index(c), c) for c in CIR if c in cam]
    idx.sort()
    out = []
    for k, (pos, _) in enumerate(idx):
        end = idx[k + 1][0] if k + 1 < len(idx) else len(cam)
        t = cam[pos + 1:end].strip()
        t = re.sub(r"^(→|、|・)\s*", "", t)
        t = re.sub(r"\s*(→|。)\s*$", "", t)
        out.append(t)
    return out


def sec_span(tm):
    m = re.match(r"\s*(\d+)-(\d+)秒", tm)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.match(r"\s*(\d+)秒", tm)
    if m:
        return int(m.group(1)), int(m.group(1))
    return None


def shot_rows(no):
    pg = PG[no]
    rows, n = [], 0
    for si in range(1, len(pg["rows"]) + 1):
        nm, tm, shots = pg["rows"][si - 1]
        cuts = [sh for sh in shots if sh[1] != "―"]
        angles = shot_angles(no, si)
        place, _, day, when = S.SPOT[no][si]
        span = sec_span(tm)
        each = (span[1] - span[0]) / len(cuts) if span and len(cuts) else None
        mv = MOVED.get((no, si), [])
        rows.append(f'''<tr>
      <td colspan="5" style="background: {BAND}; padding: 11px 0; border-bottom: 1px solid {LINE}">
        <div style="display: flex; align-items: baseline; gap: 14px; padding: 0 4px">
          <div style="font-size: 18px; font-weight: 700; color: {INK}">{esc(nm)}</div>
          <div style="font-size: 15px; color: {MUTED}">{esc(re.sub(r"　｜.*", "", tm))}</div>
          <div style="font-size: 15px; color: {MUTED}">{place if place != "同じ" else "同じ場所"}</div>
          <div style="margin-left: auto; font-size: 15px; color: {GOLD}; font-weight: 700; padding-right: 4px">{esc(day)}　{esc(when)}</div>
        </div>
      </td>
    </tr>''')
        for k, sh in enumerate(cuts):
            n += 1
            td = f"padding: 11px 14px; border-bottom: 1px solid {LINE}; vertical-align: top"
            sec = ""
            if each:
                sec = f"{span[0] + each * k:.1f}〜{span[0] + each * (k + 1):.1f}秒"
            tag = ""
            if k + 1 in mv:
                tag = f'<div style="font-size: 14px; color: {GOLD}; margin-top: 3px">{TALK_DAY}に撮影</div>'
            rows.append(f'''<tr>
      <td style="{td}; padding-left: 0; white-space: nowrap">
        <span style="font-size: 17px; font-weight: 700; color: {INK}">{n:02d}</span>
        <span style="font-size: 15px; color: {FAINT}">　S{si}-{CIR[k]}</span></td>
      <td style="{td}; font-size: 16px; line-height: 1.6; color: {INK}">{angles[k] if k < len(angles) else ""}{tag}</td>
      <td style="{td}; font-size: 16px; line-height: 1.7; color: {INK}">{sh[1]}</td>
      <td style="{td}; font-size: 15px; color: {MUTED}; white-space: nowrap">{sec}</td>
      <td style="{td}; padding-right: 0"><div style="width: 22px; height: 22px; border: 1px solid {LINE}; border-radius: 3px"></div></td>
    </tr>''')
    return "".join(rows), n


def shotlist_artboard(no):
    pg = PG[no]
    body, n = shot_rows(no)
    th = ("text-align: left; font-size: 15px; font-weight: 400; color: " + FAINT +
          "; letter-spacing: 0.08em; border-bottom: 1px solid " + INK + "; padding-bottom: 11px")
    days = []
    for si in sorted(S.SPOT[no]):
        d = S.SPOT[no][si][2]
        if d != "―" and d not in days:
            days.append(d)
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
<div style="width: {PAGE_W}px; height: {HEIGHT["sl" + no]}px; background: #ffffff; padding: {MARGIN}px; box-sizing: border-box; display: flex; flex-direction: column; gap: 18px">
  <div style="display: flex; align-items: baseline; gap: 14px; border-bottom: 2px solid {INK}; padding-bottom: 13px">
    <div style="font-size: 26px; font-weight: 700; color: {GOLD}">{MARU[no]}</div>
    <div style="font-size: 28px; font-weight: 700; color: {INK}">{esc(pg["jp"])}</div>
    <div style="font-size: 15px; color: {FAINT}">{esc(pg["en"])}</div>
    <div style="font-size: 16px; font-weight: 700; color: {INK}; margin-left: 16px">{esc(plain(pg["meta_len"]))}</div>
    <div style="margin-left: auto; font-size: 16px; font-weight: 700; color: {GOLD}">{"・".join(days)}</div>
  </div>
  <table>
    <colgroup>
      <col style="width: 150px"><col style="width: 430px"><col><col style="width: 150px"><col style="width: 60px">
    </colgroup>
    <tr>
      <th style="{th}; padding-left: 0">№　／　カット</th>
      <th style="{th}; padding-left: 14px">画 角</th>
      <th style="{th}; padding-left: 14px">撮 る も の</th>
      <th style="{th}; padding-left: 14px">尺 の 目 安</th>
      <th style="{th}; padding-left: 14px">済</th>
    </tr>
    {body}
  </table>
  <div style="margin-top: auto; display: flex; justify-content: space-between; font-size: 13px; color: {FAINT}">
    <div>BROOKLYN MUSEUM ／ 向島工房　動画制作　／　ショットリスト</div>
    <div>{MARU[no]}　全{n}カット</div>
  </div>
</div>
</x-dc>
</body>
</html>
'''

CAST = [
 ("①", "01", "九日目", "映る（腰より上の寄りがある）",
  "鏡だけ。四回の着替えのあと、髪の乱れを直す。",
  "四色ぶんの服と鞄。<b>鞄の色と喧嘩しない服</b>を選ぶ。<br>ヘアメイクを付けないので、<b>髪型が崩れない服</b>にする ──<br>前開きの上着なら、着替えで髪が乱れない。",
  "着替え場所と荷物置き場。四回の着替えを見込んで、<br>会場の使用時間を長めに申請する。"),
 ("④", "04", "八日目", "主役にしない（引きと後ろ姿）",
  "爪を切りそろえる。<b>手が寄りで映る。</b>",
  "一そろい。街に馴染む色。<br>鞄より目立つ柄は避ける。",
  "時計・指輪は外す。<br>歩く距離があるので、履き慣れた靴で。"),
 ("⑦", "07", "七日目", "映らない（手と肩だけ）",
  "爪を切り、手を洗っておく。<br>時計・指輪は外す。",
  "袖口の見える無地の上着。<br>柄物だと、手の動きより袖に目が行く。",
  "物を置く速さが一定にできる方を選ぶ。<br>一度通してもらってから本番。"),
 ("⑧", "08", "六日目", "映る（バストショット）",
  "テカリ止めのパウダーだけ用意する。<br>窓の光で額と鼻が光る。",
  "本人のふだんの服。<br>細かい柄は画面で目がちらつくので避ける。",
  "顔出しの範囲を、撮る前に本人へ確認する。<br>名前は出さず「購入者Aさん」とだけ出す。"),
 ("⑤⑥", None, "三日目", "映る（バストショット・横顔）",
  "襟元と髪だけ、撮る直前に鏡で見る。",
  "ふだんの仕事着。<br>三人とも同じ日に撮るので、その日の服で揃う。",
  "永尾社長・佐藤さん・くさがやさん。<br>三人とも三十分ずつ。"),
]


def cast_artboard():
    th = ("text-align: left; font-size: 15px; font-weight: 400; color: " + FAINT +
          "; letter-spacing: 0.08em; border-bottom: 1px solid " + INK + "; padding-bottom: 11px")
    td = f"padding: 20px 16px; border-bottom: 1px solid {LINE}; vertical-align: top"
    rows = []
    for maru, no, day, face, hm, cloth, other in CAST:
        name = PG[no]["jp"] if no else "永尾社長・佐藤さん・くさがやさん"
        rows.append(f'''<tr>
      <td style="{td}; padding-left: 0">
        <div style="font-size: 21px; font-weight: 700; color: {GOLD}">{maru}</div>
        <div style="font-size: 16px; font-weight: 700; color: {INK}; margin-top: 5px">{esc(name)}</div>
        <div style="font-size: 15px; color: {FAINT}; margin-top: 5px">{esc(day)}</div>
      </td>
      <td style="{td}; font-size: 17px; line-height: 1.7; color: {INK}">{esc(face)}</td>
      <td style="{td}; font-size: 17px; line-height: 1.75; color: {INK}">{hm}</td>
      <td style="{td}; font-size: 17px; line-height: 1.75; color: {INK}">{cloth}</td>
      <td style="{td}; padding-right: 0; font-size: 16px; line-height: 1.75; color: {MUTED}">{other}</td>
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
<div style="width: {PAGE_W}px; height: {HEIGHT["cast"]}px; background: #ffffff; padding: {MARGIN}px; box-sizing: border-box; display: flex; flex-direction: column; gap: 20px">
  <div style="display: flex; align-items: baseline; gap: 16px; border-bottom: 2px solid {INK}; padding-bottom: 14px">
    <div style="font-size: 32px; font-weight: 700; color: {INK}">出演者と支度</div>
    <div style="font-size: 16px; color: {FAINT}; letter-spacing: 0.06em">Cast &amp; Preparation</div>
    <div style="margin-left: auto; font-size: 17px; color: {MUTED}">ヘアメイクは付けない</div>
  </div>
  <div style="font-size: 17px; line-height: 1.8; color: {MUTED}">
    ヘアメイクは付けません。当日の支度は、鏡・テカリ止めのパウダー・爪の手入れだけです。顔が寄りで映るのは①と⑧の二本だけで、ほかは顔を主役にしないか、まったく映しません。
  </div>
  <table>
    <colgroup>
      <col style="width: 230px"><col style="width: 280px"><col style="width: 400px"><col style="width: 400px"><col>
    </colgroup>
    <tr>
      <th style="{th}; padding-left: 0">本　／　撮 影 日</th>
      <th style="{th}; padding-left: 16px">顔 が 映 る か</th>
      <th style="{th}; padding-left: 16px">当 日 の 支 度</th>
      <th style="{th}; padding-left: 16px">衣 装</th>
      <th style="{th}; padding-left: 16px">そ の ほ か</th>
    </tr>
    {"".join(rows)}
  </table>
  <div style="border-top: 1px solid {LINE}; padding-top: 20px; font-size: 17px; line-height: 1.9; color: {INK}">
    <div style="font-size: 15px; color: {FAINT}; letter-spacing: 0.08em; margin-bottom: 9px">全 員 に 共 通 す る こ と</div>
    出演承諾書を、①④⑦⑧の出演者全員からいただく ── 使う範囲（Instagram・EC商品ページ・展示会）、期間、媒体を書いたもの。<br>
    交通費と拘束時間を、依頼するときに先に伝える。<br>
    体調不良に備えて、①と④は予備日を一日置く。
  </div>
  <div style="margin-top: auto; display: flex; justify-content: space-between; font-size: 13px; color: {FAINT}">
    <div>BROOKLYN MUSEUM ／ 向島工房　動画制作　／　香盤表</div>
    <div>出演者と支度</div>
  </div>
</div>
</x-dc>
</body>
</html>
'''

# 実際に描かせて測った高さ
HEIGHT = {"cover": 1492, "d1": 1277, "d2": 960, "d3": 864,
          "d4": 1347, "d5": 858, "d6": 1513, "d7": 937, "d8": 859, "d9": 1011, "cast": 1062,
          "sl01": 1149, "sl02": 1847, "sl03": 1181, "sl04": 939,
          "sl05": 1855, "sl06": 2075, "sl07": 1131, "sl08": 1710}


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    arts, x, y, col = [], 0, 0, 0
    items = ([("Main", "cover", cover_artboard)] +
             [(d["key"].upper(), d["key"], (lambda dd: (lambda: day_artboard(dd)))(d)) for d in DAYS] +
             [("Shot" + no, "sl" + no, (lambda n: (lambda: shotlist_artboard(n)))(no)) for no in SHOT_ORDER] +
             [("Cast", "cast", cast_artboard)])
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
