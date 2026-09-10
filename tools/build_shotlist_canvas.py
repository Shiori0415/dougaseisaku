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
# インタビューの収録で先に撮ってしまうカット（本, シーン）→ （カット番号, その日）
MOVED = {("05", 1): ([3], "店の日"), ("05", 8): ([1, 2], "店の日"),
         ("05", 6): ([1], "店の日"),
         ("06", 2): ([3], "工房の日"), ("06", 8): ([3], "工房の日")}
REUSE = {("05", 5): "⑥から引っ張る"}

# シーンごとの登場（人 ／ 物）
CASTPROP = {
("01",1):("モデル", "一色目の衣装・鞄"),
("01",2):("モデル", "二色目の衣装・鞄"),
("01",3):("モデル", "三色目の衣装・鞄"),
("01",4):("モデル", "四色目の衣装・鞄"),
("01",5):("モデル、通行人（すれ違う役）", "四色ぶんの衣装・鞄"),
("01",6):("―", "鞄 四種類、ロゴ"),
("02",1):("職人（手だけ）", "完成した鞄"),
("02",2):("―", "革のロールが並ぶ棚"),
("02",3):("職人（手だけ）", "抜き型、革、裁断機"),
("02",4):("職人（手だけ）", "革 二枚、型"),
("02",5):("職人（手と上半身）", "ミシン、糸、革"),
("02",6):("職人（手だけ）", "刃、道具、革"),
("02",7):("職人（手だけ）", "コバ塗料、道具、断面"),
("02",8):("職人（手と上半身）", "木槌、道具、立ち上がった鞄"),
("02",9):("職人（手だけ）", "完成した鞄、ロゴ"),
("03",1):("―", "鞄の一部（光の帯だけ）、黒い布"),
("03",2):("手だけ（時計・指輪は外す）", "革 二枚、染料、道具"),
("03",3):("手だけ", "革"),
("03",4):("手だけ（白手袋）", "金具"),
("03",5):("―", "完成品、工房の道具、ロゴ"),
("04",1):("モデル", "鞄、鉄のフェンス"),
("04",2):("手だけ", "鞄、中に入れる持ち物"),
("04",3):("モデル（後ろ姿）", "鞄"),
("04",4):("モデル", "鞄、持ち物、靴、ロゴ"),
("05",1):("永尾社長", "表参道の並木通り（高いところから）"),
("05",2):("―", "店舗の外観、昔の写真"),
("05",3):("永尾社長ともう一人（覗き込む役）", "色見本、革、店舗の机"),
("05",4):("手だけ", "図面、型紙"),
("05",5):("―（⑥の画を使う）", "―"),
("05",6):("くさがやさん", "店内の商品、ショーウィンドウ"),
("05",7):("くさがやさん、お客さま役", "商品、ノートPC"),
("05",8):("永尾社長", "ロゴ"),
("06",1):("作業する人（顔は出さない）", "工房の入口、通路、機械"),
("06",2):("佐藤さん、作業する人", "材料の壁、機械"),
("06",3):("手だけ", "革の棚、金型、型紙"),
("06",4):("手だけ", "裁断機、革包丁、裁ち上がったパーツ"),
("06",5):("職人（手と目）", "へら、スプレー、コバ塗料"),
("06",6):("職人（両手）", "ミシン、糸、部品"),
("06",7):("職人（手と横顔）", "上がった品"),
("06",8):("佐藤さん、梱包場の人", "不織布、箱、テープ"),
("06",9):("―", "文字のカード、ロゴ"),
("07",1):("出演者（手と肩だけ）", "鞄、机"),
("07",2):("出演者（手だけ）", "A4書類、13インチPC"),
("07",3):("出演者（手だけ）", "手帳、鍵、サングラス、ペン、傘、水筒"),
("07",4):("出演者（手と肩だけ）", "鞄"),
("07",5):("―", "何も乗っていない机、ロゴ"),
("08",1):("購入者（入口に立つ）", "店の外観、商品"),
("08",2):("―", "商品、ロゴの壁"),
("08",3):("購入者", "商品、手前に置く植物"),
("08",4):("購入者", "商品、窓辺"),
("08",5):("購入者", "鞄、屋上からの景色"),
("08",6):("購入者", "―"),
("08",7):("購入者、くさがやさん（見送る役）", "ロゴ"),
("08",8):("―", "ロゴ"),
}

DAYS = [
 dict(key="d2", no="店の日", place="店舗・事務所・屋上", theme="固定で撮れるものから始める",
      date="10月1日（木）",
      toc=[("05", "永尾社長・くさがやさんのインタビュー、店の外観と歴史、企画・設計、店内、購入・使う"),
           ("08", "店の前、店内、窓辺のインタビュー、屋上、見送り"),
           ("07", "五シーンすべて（事務所の机・正面固定）")],
      cond="製作日を待たなくてよい。<b>いちばん先に、いちばんやさしい日から始める</b>── ほとんどが三脚を据えたままの固定。購入者の予定が合わなければ、窓辺・屋上・見送りだけ別の日に切り出す。",
      gear="カメラ／三脚／ピンマイク 二本／ガンマイク／PLフィルター／白い板／手前に置く植物／"
           "鞄に入れる物 一式（A4書類・13インチPC・手帳・鍵・サングラス・ペン・傘・水筒）",
      keys=["インタビューは窓を横に置く。二人とも同じ椅子・同じ画角で撮る。",
            "店の外観は午前。看板に日が当たる時間に撮る。",
            "ショーウィンドウ越しは、向かいの建物が映り込まない立ち位置を先に探す。",
            "⑦は三脚を立てたら最後まで触らない。十四カット全部が同じ画角。"],
      talks=[("10:15〜10:45", "永尾社長", "店内（窓を横に・インタビューの一角）",
              "⑤のインタビューを全部（七十五秒ぶん・八シーン）。<br>画は <b>⑤S1③</b>（バストショット）と <b>⑤S8</b>（締めの一言）。",
              "S1③とS8は同じ画角のまま続けて撮る。空撮の続きに見えるよう、背景は大きくボカす。",
              [("05", 8)]),
             ("10:50〜11:20", "くさがやさん", "同じ場所（椅子も画角もそのまま）",
              "⑤のインタビューのうち、店のところ（二シーン）。<br>画は <b>⑤S6①</b>（横顔）。",
              "空いた側に見出しテロップが入るので、画面の片側を空けて撮る。", [])],
      setups=[("9:30〜10:05", "店の外・店の前（向かいの歩道から）", [("05", 2), ("08", 1)],
               "<b>⑤の歴史と⑧のつかみを、同じ立ち位置でまとめて撮る。</b>三脚を一度組めば両方いける。"),
              ("11:20〜12:20", "店内（ショーウィンドウ越し・レジまわり・ロゴの壁）",
               [("05", 6), ("05", 7), ("08", 2)],
               "<b>店内の三シーンをまとめて撮る。</b>インタビューの収録に続けて、そのまま店内へ。"),
              ("13:20〜14:05", "店舗の机（打ち合わせの場所）", [("05", 3), ("05", 4)],
               "<b>⑤の企画と設計。</b>机を一度組んだら、二シーンを続けて撮る。"),
              ("14:10〜15:25", "事務所（バックヤード）の机・正面固定",
               [("07", 1), ("07", 2), ("07", 3), ("07", 4), ("07", 5)],
               "十四カット全部が同じ画角。物を並べてから、一度通してもらって本番。"),
              ("15:35〜16:35", "店の窓辺（手前に植物を置いてボカす）", [("08", 3), ("08", 4), ("08", 6)],
               "<b>購入者インタビューの三シーンを続けて撮る。</b>カメラは一度も動かさない。"),
              ("16:45〜17:10", "屋上、または近くの見晴らしのよい場所", [("08", 5)],
               "斜めの光が出る時間に合わせる。日が短い時期は、窓辺と順番を入れ替える。"),
              ("17:15〜17:30", "店の前（見送り）", [("08", 7)],
               "朝と同じ立ち位置。カメラは動かさない。"),
              ("―", "白バック（撮影せず、編集で作る）", [("08", 8)],
               "⑧の締め。映像が白に抜けて、ロゴだけが残る。")]),
 dict(key="d4", no="モデルの日", place="東京国際フォーラム → 表参道",
      theme="出演者を立てて撮る二本", date="10月2日（金）",
      toc=[("05", "冒頭の俯瞰（表参道を高いところから）"),
           ("01", "ロビーの四シーン（一色目〜四色目）、巻き戻る、ベンチで並べる"),
           ("04", "柵（最初と最後）、置き画、けやき並木の歩道を歩く")],
      cond="出演者と衣装・鞄 四色ぶんが揃ってから。会場の撮影申請も先に出す。曇りの日に合わせ、予備日を一日置く。",
      gear="カメラ／三脚／三脚キャスター／養生テープ／脚立／水準器／衣装と鞄 四色ぶん",
      keys=["四色ぶんは同じ立ち位置で撮る。床にテープで足の位置を貼る。",
            "カメラの高さは胸で固定し、最後まで変えない。",
            "午後の④は三脚を止めて、背景だけを動かす。顔は主役にしない。",
            "雨上がりの翌日は避ける。濡れた地面が白く光って革の色が出ない。"],
      setups=[("9:00〜10:10", "ガラス棟ロビー（北端 → 柱の列 → ガラスの扉 → 南端の階段前）",
               [("01", 1), ("01", 2), ("01", 3), ("01", 4)],
               "<b>進む側の四シーン。</b>四色ぶんの着替えはここでまとめる。画角を控えておく。"),
              ("10:10〜10:45", "ロビー中央のまっすぐな通路（キャスターが十メートル走れるところ）", [("01", 5)],
               "<b>戻る側。進んだときとまったく同じ画角・立ち位置で撮る。</b>"),
              ("10:45〜11:05", "ロビーのベンチ（真俯瞰で並べる）", [("01", 6)], "四種類を並べて締める。"),
              ("13:10〜13:30", "表参道が見下ろせる高いところ（歩道橋・商業施設の上階など）", [("05", 1)],
               "<b>⑤の冒頭の俯瞰。ドローンは使わない。</b>並木通りを見下ろし、寄っていく動きを何度か撮って選ぶ。"),
              ("13:30〜14:10", "表参道 けやき並木の歩道（柵・手すり）", [("04", 1), ("04", 4)],
               "<b>④の最初と最後は同じ柵。設営は一度でよい。</b>"),
              ("14:20〜14:45", "ベンチか石段（真俯瞰が組めるところ）", [("04", 2)], "脚立か手すりの上から。"),
              ("14:55〜15:15", "けやき並木の下の歩道", [("04", 3)], "顔は主役にしない。")]),
 dict(key="d3", no="工房の日", place="向島工房", theme="佐藤さんのインタビューと、機械の前ごとに二本",
      date="10月5日（月）　※仮",
      toc=[("06", "佐藤さんのインタビュー、入口と通路、革と金型、裁断、下仕事、縫製、検品、梱包"),
           ("02", "九シーンすべて（作業台・革の棚・裁断機・下仕事・コバ塗り・ミシン）"),
           ("05", "製造シーンは撮らず、⑥の画を使う")],
      cond="<b>日付は仮。ブルックリンの品を作っている日に合わせて動かす。</b>佐藤さんに製作日を確認してから決める。",
      gear="カメラ（広角）／三脚／ガンマイク／ピンマイク／白い板（発泡スチロール）／脚立／養生テープ",
      keys=["<b>画に入れるのはブルックリンの品だけ。</b>他社の品・金型・ラベルは画角の外へ出す。",
            "蛍光灯と窓の光を混ぜない。明るさとホワイトバランスはマニュアルで固定する。",
            "②のコバ塗りだけは切らずに六秒回す。カメラ位置を決めてから始める。",
            "機械の前を離れる前に、②のぶんと⑥のぶんが両方撮れているか、その場で確かめる。"],
      talks=[("9:00〜9:30", "佐藤さん", "向島工房（窓を横に・他社の品が入らない一角）",
              "⑥のインタビューを全部（二分二十秒ぶん・九工程）。<br>画は <b>⑥S2③</b>（引き）と <b>⑥S8③</b>（バストショット）。",
              "工程ごとに区切って録る。話す順は工程の順。機械の名前は言わない。", [])],
      setups=[("9:40〜10:20", "工房の入口・通路（歩きながら）", [("06", 1), ("06", 2)],
               "<b>⑤S5の「工房の全体」と「大型機械」もここから引っ張る。</b>通路のトラッキングは切らずに長めに回す。"),
              ("10:20〜11:25", "作業台（窓ぎわ・真俯瞰の三脚が組める台）",
               [("02", 1), ("02", 4), ("02", 8), ("02", 9)],
               "<b>②の四シーンをこの台でまとめて撮る。</b>完成形（S1）と完成（S9）は同じ画角なので続けて。"),
              ("11:35〜12:00", "革の棚・金型の棚", [("02", 2), ("06", 3)],
               "<b>②の革を選ぶと⑥の革・金型を続けて撮る。</b>棚の奥行きが出る位置から。"),
              ("13:00〜13:40", "裁断機のまわり", [("02", 3), ("06", 4)],
               "<b>②の裁つと⑥の裁断をまとめて撮る。⑤S5の「手元」もここから引っ張る。</b>"),
              ("13:40〜14:20", "下仕事・コバ塗りの台", [("02", 6), ("02", 7), ("06", 5)],
               "<b>②の仕上げる①・コバ塗りと、⑥の下仕事をまとめて撮る。</b>コバ塗りは六秒回しを何度か。"),
              ("14:35〜15:15", "ミシンのまわり", [("02", 5), ("06", 6)],
               "<b>②の縫うと⑥の縫製をまとめて撮る。</b>手縫いのカットも忘れずに。"),
              ("15:15〜15:35", "検品の台", [("06", 7)], "ここで作業音がいったん消える。"),
              ("15:35〜15:55", "梱包の台", [("06", 8)], "紙とテープの音を拾う。"),
              ("―", "撮影しない ── ⑥の画をそのまま使う", [("05", 5)],
               "⑤の製造シーン。入口の通路・機械と人・裁断機の三カットを充てる。"),
              ("―", "白バック（撮影せず、編集で作る）", [("06", 9)],
               "⑥の締めカード。対応技法の一覧 → 問い合わせ先 → ロゴ。")]),
 dict(key="d1", no="暗い一本の日", place="向島工房", theme="いちばん照明が難しい一本。最後に撮る",
      date="10月6日（火）",
      toc=[("03", "五シーンすべて（窓を塞いだ一角）")],
      cond="八本でいちばん照明が難しい。ほかの三日で手が慣れてから、最後に撮る。窓を塞いで暗室にするので、時間帯は選ばない ── 夕方や休日にする必要はない。",
      gear="カメラ／三脚／白い板／黒い布／段ボール／ライト一灯",
      keys=["③はライト一灯だけ。当たっていない側は黒く落とし、レフ板で起こさない。",
            "③はシャッターが遅くなるので三脚は必須。ピントは手で合わせて固定する。",
            "画に入れるのはブルックリンの品だけ。"],
      setups=[("9:00〜11:00", "工房の隅（窓を段ボールと黒い布で塞いだ台）",
               [("03", 1), ("03", 2), ("03", 3), ("03", 4), ("03", 5)],
               "暗室を組むのに四十分みておく。組んだら五シーンを続けて撮り切る。")]),
]


# ── ショットリスト（一カット一行） ──────────────────────────

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


def moved_cuts(no, si):
    return MOVED.get((no, si), ([], ""))[0]


def day_scenes(day):
    for t in day.get("talks", []):
        for no, si in (t[5] if len(t) > 5 else []):
            yield no, si
    for _, _, sc, _ in day.get("setups", []):
        for no, si in sc:
            yield no, si


def day_counts(day):
    shoot = edit = 0
    for no, si in day_scenes(day):
        n = len(cuts_of(no, si)[1]) - len(moved_cuts(no, si))
        if is_edit_only(no, si) or (no, si) in REUSE:
            edit += n
        else:
            shoot += n
    for (no, si), (cuts, d) in MOVED.items():
        if d == day["no"]:
            shoot += len(cuts)
    return shoot, edit


def mins(t):
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def day_span(day):
    ts = [t for t, *_ in day.get("talks", [])]
    ts += [t for t, *_ in day.get("setups", []) if t != "―"]
    if not ts:
        return ""
    first = min(ts, key=lambda t: mins(t.split("〜")[0]))
    last = max(ts, key=lambda t: mins(t.split("〜")[1]))
    return first.split("〜")[0] + "〜" + last.split("〜")[1]


# ─────────────────────────────────────────────────────────────
def scene_row(no, si):
    nm, cuts = cuts_of(no, si)
    place, _, _, when = S.SPOT[no][si]
    cam, note = split_cam(S.D[no][si][0])
    td = f"padding: 15px 16px; border-bottom: 1px solid {LINE}; vertical-align: top"
    edit = is_edit_only(no, si)
    if (no, si) in REUSE:
        tcell = f'<span style="color: {GOLD}">撮影しない<br>{REUSE[(no, si)]}</span>'
    elif edit:
        tcell = f'<span style="color: {FAINT}">撮影しない（編集で作る）</span>'
    else:
        tcell = f'<span style="font-size: 19px; font-weight: 700; color: {GOLD}">{esc(when)}</span>'
    who, prop = CASTPROP.get((no, si), ("―", "―"))
    mv, mvday = MOVED.get((no, si), ([], ""))
    if mv and len(mv) == len(cuts):
        cnt = f'{len(cuts)}カット<br><span style="color: {GOLD}">インタビューの収録で撮る</span>'
    else:
        cnt = f'{len(cuts) - len(mv)}カット'
        if mv:
            cnt += f'<br><span style="color: {GOLD}">{"".join(CIR[k - 1] for k in mv)}は{mvday}</span>'
    return f'''<tr>
      <td style="{td}; padding-left: 0; white-space: nowrap">{tcell}</td>
      <td style="{td}">
        <div style="font-size: 19px; font-weight: 700; color: {INK}">
          <span style="color: {GOLD}">{MARU[no]}</span> {esc(nm)}</div>
        <div style="font-size: 15px; color: {FAINT}; margin-top: 4px; line-height: 1.6">{cnt}</div>
      </td>
      <td style="{td}; font-size: 17px; line-height: 1.7; color: {INK}">{place if place != "同じ" else f'<span style="color:{MUTED}">同じ</span>'}</td>
      <td style="{td}; font-size: 16px; line-height: 1.7; color: {INK}">{who}<div style="color: {MUTED}; margin-top: 3px">{prop}</div></td>
      <td style="{td}; font-size: 17px; line-height: 1.75; color: {INK}">{cam}</td>
      <td style="{td}; padding-right: 0; font-size: 16px; line-height: 1.75; color: {MUTED}">{note}</td>
    </tr>'''


def band_row(no):
    pg = PG[no]
    return f'''<tr>
      <td colspan="6" style="background: {BAND}; padding: 13px 0 13px 0; border-bottom: 1px solid {LINE}">
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
    for t in day["talks"]:
        when, who, place, what, note = t[:5]
        out.append(f'''<tr>
      <td style="{td}; padding-left: 0; white-space: nowrap">
        <span style="font-size: 19px; font-weight: 700; color: {GOLD}">{esc(when)}</span></td>
      <td style="{td}"><div style="font-size: 20px; font-weight: 700; color: {INK}">{esc(who)}</div></td>
      <td style="{td}; font-size: 17px; line-height: 1.7; color: {INK}">{place}</td>
      <td style="{td}; font-size: 16px; line-height: 1.7; color: {INK}">{esc(who)}<div style="color: {MUTED}; margin-top: 3px">椅子、ピンマイク</div></td>
      <td style="{td}; font-size: 17px; line-height: 1.75; color: {INK}">{what}</td>
      <td style="{td}; padding-right: 0; font-size: 16px; line-height: 1.75; color: {MUTED}">{note}</td>
    </tr>''')
        for no, si in (t[5] if len(t) > 5 else []):
            out.append(scene_row(no, si))
    return "".join(out)


def day_artboard(day):
    shoot, edit = day_counts(day)
    th = ("text-align: left; font-size: 15px; font-weight: 400; color: " + FAINT +
          "; letter-spacing: 0.08em; border-bottom: 1px solid " + INK + "; padding-bottom: 11px")
    rows = []
    if day.get("talks"):
        rows.append(f'<tr><td colspan="6" style="padding: 4px 0 10px">'
                    f'<span style="font-size: 17px; font-weight: 700; color: {INK}">イ ン タ ビ ュ ー の 収 録</span></td></tr>')
        rows.append(talk_rows(day))
    if day.get("setups"):
        if day.get("talks"):
            rows.append(f'<tr><td colspan="6" style="padding: 24px 0 10px">'
                        f'<span style="font-size: 17px; font-weight: 700; color: {INK}">セ ッ ト ご と の 撮 影</span></td></tr>')
        for when, place, sc, note in day["setups"]:
            books = "　".join(
                MARU[no] + " " + "・".join(re.sub(r"^S\d+\s*", "", cuts_of(no, si)[0])
                                          for n2, si in sc if n2 == no)
                for no in dict.fromkeys(n for n, _ in sc))
            rows.append(
                f'<tr><td colspan="6" style="background: {BAND}; padding: 12px 0; '
                f'border-bottom: 1px solid {LINE}">'
                f'<div style="display: flex; align-items: baseline; gap: 14px; padding: 0 4px">'
                f'<div style="font-size: 19px; font-weight: 700; color: {GOLD}">{esc(when)}</div>'
                f'<div style="font-size: 19px; font-weight: 700; color: {INK}">{esc(place)}</div>'
                f'<div style="font-size: 16px; color: {MUTED}">{books}</div>'
                f'<div style="margin-left: auto; font-size: 15px; color: {MUTED}; '
                f'padding-right: 4px">{note}</div></div></td></tr>')
            for no, si in sc:
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
    <div style="font-size: 32px; font-weight: 700; color: {INK}">{esc(day["no"])}</div>
    <div style="font-size: 19px; font-weight: 700; color: {GOLD}; border: 1px solid {LINE}; border-radius: 6px; padding: 3px 13px">日付　{esc(day["date"])}</div>
    <div style="font-size: 19px; font-weight: 700; color: {INK}">{esc(day["place"])}</div>
    <div style="font-size: 16px; color: {MUTED}">{esc(day["theme"])}</div>
    <div style="margin-left: auto; font-size: 17px; font-weight: 700; color: {INK}">{esc(day_span(day))}</div>
    <div style="font-size: 15px; color: {FAINT}">撮るカット {shoot}{"（ほかに編集で作る " + str(edit) + "）" if edit else ""}</div>
  </div>
  <div style="font-size: 16px; line-height: 1.7; color: {GOLD}">{day["cond"]}</div>
  <table>
    <colgroup>
      <col style="width: 148px"><col style="width: 205px"><col style="width: 255px"><col style="width: 235px"><col style="width: 420px"><col>
    </colgroup>
    <tr>
      <th style="{th}; padding-left: 0">時 刻</th>
      <th style="{th}; padding-left: 16px">{"話 す 人 ／ 本 ・ シ ー ン" if day.get("talks") else "本 ・ シ ー ン"}</th>
      <th style="{th}; padding-left: 16px">場 所 （ セ ッ ト ）</th>
      <th style="{th}; padding-left: 16px">登 場 （ 人 ／ 物 ）</th>
      <th style="{th}; padding-left: 16px">{"録 る こ と ／ 画 角 の 並 び" if day.get("talks") else "画 角 の 並 び"}</th>
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
        books = "".join(
            f'<div style="margin-top: 6px; line-height: 1.6">'
            f'<span style="color: {GOLD}; font-weight: 700">{MARU[no]}</span>'
            f'　<b>{esc(PG[no]["jp"])}</b>'
            f'<span style="color: {MUTED}">　── {t}</span></div>'
            for no, t in d["toc"])
        rows.append(f'''<tr>
      <td style="{td}; padding-left: 0; font-size: 21px; font-weight: 700; color: {GOLD}; white-space: nowrap">{esc(d["date"])}</td>
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
      <div style="margin-left: auto; font-size: 18px; font-weight: 700; color: {INK}">全八本　{tot_s + tot_e}カット　／　撮影 六日</div>
    </div>
  </div>

  <table>
    <colgroup>
      <col style="width: 130px"><col style="width: 270px"><col><col style="width: 190px"><col style="width: 140px">
    </colgroup>
    <tr>
      <th style="{th}; padding-left: 0">日 付</th>
      <th style="{th}; padding-left: 16px">場 所</th>
      <th style="{th}; padding-left: 16px">内 容</th>
      <th style="{th}; padding-left: 16px">時 間</th>
      <th style="{th}; padding-left: 16px">カ ッ ト</th>
    </tr>
    {"".join(rows)}
  </table>
  <div style="border-top: 1px solid {LINE}; padding-top: 20px; display: flex; gap: 44px">
    <div style="flex: 1">
      <div style="font-size: 15px; color: {FAINT}; letter-spacing: 0.08em; margin-bottom: 9px">先 に 決 め て お く こ と</div>
      <div style="font-size: 17px; line-height: 1.9; color: {INK}">
        <b>ブルックリンの製作日</b>を佐藤さんに確認する ── 工房案内の日とASMRの日は、これで決まる。<br>
        <b>インタビューの日</b>── 永尾社長・佐藤さんの予定。工房が動いていない日でも撮れる。<br>
        <b>店の日</b>── くさがやさんの予定と、⑦で鞄に物を入れて持ち出す方（顔は映らないので、手と肩だけ）。<br>
        <b>購入者の日</b>── 出演していただく方と、顔出しの範囲。<br>
        <b>モデルの日</b>── 出演者と、衣装・鞄 四色ぶん。会場の撮影申請。④は曇りの日に合わせるので、予備日を一日置く。<br>
        <span style="color: #a8672a">出演者の支度は、最後の一枚「出演者と支度」にまとめています。</span>
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

CIR = "①②③④⑤⑥⑦⑧⑨"
SHOT_ORDER = ["02", "03", "06", "05", "08", "07", "04", "01"]


def shot_angles(no, si):
    """カメラの一文を①②③…で割って、カットごとの画角にする。
       「⑥S1③」のような他の本への参照は、割るときの番号として数えない。"""
    cam, _ = split_cam(S.D[no][si][0])
    mask = re.sub(r"[①-⑨]S\d[①-⑨]", "※S9※", cam)
    idx = [(mask.index(c), c) for c in CIR if c in mask]
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
        mv, mvday = MOVED.get((no, si), ([], ""))
        rows.append(f'''<tr>
      <td colspan="6" style="background: {BAND}; padding: 11px 0; border-bottom: 1px solid {LINE}">
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
                tag = f'<div style="font-size: 14px; color: {GOLD}; margin-top: 3px">{mvday}に撮影</div>'
            if (no, si) in REUSE:
                tag = f'<div style="font-size: 14px; color: {GOLD}; margin-top: 3px">撮影しない ── {REUSE[(no, si)]}</div>'
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
 ("①", "01", "モデルの日", "映る（腰より上の寄りがある）",
  "鏡だけ。四回の着替えのあと、髪の乱れを直す。",
  "四色ぶんの服と鞄。<b>鞄の色と喧嘩しない服</b>を選ぶ。<br>ヘアメイクを付けないので、<b>髪型が崩れない服</b>にする ──<br>前開きの上着なら、着替えで髪が乱れない。",
  "着替え場所と荷物置き場。四回の着替えを見込んで、<br>会場の使用時間を長めに申請する。"),
 ("④", "04", "モデルの日", "主役にしない（引きと後ろ姿）",
  "爪を切りそろえる。<b>手が寄りで映る。</b>",
  "一そろい。街に馴染む色。<br>鞄より目立つ柄は避ける。",
  "時計・指輪は外す。<br>歩く距離があるので、履き慣れた靴で。"),
 ("⑦", "07", "店の日", "映らない（手と肩だけ）",
  "爪を切り、手を洗っておく。<br>時計・指輪は外す。",
  "袖口の見える無地の上着。<br>柄物だと、手の動きより袖に目が行く。",
  "物を置く速さが一定にできる方を選ぶ。<br>一度通してもらってから本番。"),
 ("⑧", "08", "購入者の日", "映る（バストショット）",
  "テカリ止めのパウダーだけ用意する。<br>窓の光で額と鼻が光る。",
  "本人のふだんの服。<br>細かい柄は画面で目がちらつくので避ける。",
  "顔出しの範囲を、撮る前に本人へ確認する。<br>名前は出さず「購入者Aさん」とだけ出す。"),
 ("⑤⑥", None, "店の日・工房の日", "映る（バストショット・横顔）",
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
HEIGHT = {"cover": 1044, "d1": 1009, "d2": 2972, "d3": 3003, "d4": 1859, "cast": 1062,
          "sl01": 1203, "sl02": 2173, "sl03": 1235, "sl04": 993,
          "sl05": 2297, "sl06": 2595, "sl07": 1185, "sl08": 1845}


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
