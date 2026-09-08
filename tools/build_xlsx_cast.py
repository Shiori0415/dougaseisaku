# -*- coding: utf-8 -*-
"""出演者（①④⑦のモデル像）を色分けした表で書き出す。
   実行: python3 tools/build_xlsx_cast.py → pdf/05_出演者_モデル像.xlsx

   Googleドライブに上げて「Googleスプレッドシートで開く」でそのまま編集できる。
   本ごとに色を決めてある（①＝テラコッタ／④＝青灰／⑦＝緑）。
   ①だけ人を探す必要があるので、①の列がいちばん濃い。
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
JP = "Meiryo"

INK, MUTED, ACCENT = "1A1A1A", "5B6266", "A8672A"
DEEP = "6E3C12"        # 目立たせるマスの文字（薄い地の上でも読める濃さ）
LINE = "D9D4CB"
LBL_HEAD, LBL_FILL = "2E2A24", "F4F1EA"
WHITE = "FFFFFF"

# 本ごとの色（濃い＝見出し、薄い＝本文の地）
C = {
    "1": dict(head="C9743F", tint="FAECE1", strong="F2D9C4"),
    "4": dict(head="5C7D94", tint="E9F0F5", strong="D3E1EA"),
    "7": dict(head="7A8F5C", tint="EEF3E6", strong="DDE7CE"),
}
HILITE = "FFF3D9"

thin = Side(style="thin", color=LINE)
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)


def style(c, size=9.5, bold=False, color=INK, fill=None, wrap=True,
          va="top", ha="left", border=True):
    c.font = Font(name=JP, size=size, bold=bold, color=color)
    c.alignment = Alignment(vertical=va, horizontal=ha, wrap_text=wrap)
    if fill:
        c.fill = PatternFill("solid", fgColor=fill)
    if border:
        c.border = BORDER
    return c


def title_block(ws, title, lead, widths):
    ws["A1"] = "BROOKLYN MUSEUM ／ 向島工房　動画制作"
    ws["A1"].font = Font(name=JP, size=8.5, color=MUTED)
    ws["A2"] = title
    ws["A2"].font = Font(name=JP, size=17, bold=True, color=INK)
    ws["A3"] = lead
    ws["A3"].font = Font(name=JP, size=9.5, color=MUTED)
    ws["A3"].alignment = Alignment(vertical="top", wrap_text=True)
    ws.row_dimensions[2].height = 26
    ws.row_dimensions[3].height = 32
    ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=len(widths))
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


# ────────────────────────────────────────────────────────────────
# 1枚目　三本まとめ（項目 × 本のマス目）
# ────────────────────────────────────────────────────────────────
HEADS = [
    "項　目",
    "①　その日の服に、その日の色。",
    "④　What You Carry Makes You",
    "⑦　朝も仕事も、スマートに。",
]

# (項目, ①, ④, ⑦, 目立たせるか)
MATRIX = [
    ("尺・ショット", "三十秒 ／ 十七ショット", "三十秒 ／ 十一ショット", "二十五秒 ／ 十四ショット", False),
    ("顔", "出る。主役", "主役にしない（引き・後ろ姿・ぼかし）", "入らない", True),
    ("いちばん見る点", "歩き方。次に笑顔", "立ち姿と姿勢。次に手", "ものを置く速さが一定か", True),
    ("年齢", "二十八〜三十五歳（中心は三十歳前後）",
     "二十五〜三十五歳", "三十〜四十代の手", False),
    ("性別・人数", "女性 一人",
     "男性 一人（①が女性なので対になる。女性でも可）", "問わない。手だけ", False),
    ("身長・体型", "百六十〜百七十センチ。細すぎない。背中がまっすぐ",
     "百七十五センチ前後、細身。姿勢がいいこと", "―（映らない）", False),
    ("髪", "肩より短いか、まとめられる長さ。五色を通して変えない。明るすぎない色",
     "指定なし。街に馴染めばよい", "―（映らない）", False),
    ("表情", "すまし顔（S2）・笑う（S3）・急ぎ足（S4）・いちばん明るく笑う（S5）",
     "―（顔を主役にしない）", "―（映らない）", False),
    ("歩き方・動き", "カメラの前を五回歩き直す。テンポよく、まっすぐ、硬くならない",
     "後ろ姿と横向きで歩く。立ち止まる",
     "入れる動作が九回。速さが一定であること", True),
    ("手・爪", "冒頭のキーケースの寄りだけ。爪は短く。指輪は外す",
     "真俯瞰の寄りが二カット。爪は短く、時計は外す。手だけ別の人でも可",
     "全編ここだけ。爪は短く、傷なし。指輪と腕時計は外す", False),
    ("服・靴", "五色ぶん着替える。色は鞄に合わせて撮影前に決める。靴は共通でも可",
     "一着でよい。無地・暗い色。靴は最後の置き画に入るので履き古していない一足",
     "袖が映る。白か淡い色のシャツ。袖口が汚れていないもの", False),
    ("ほかに要る人", "通りすぎる人 二〜四人。知人・友人かエキストラ",
     "なし", "なし", False),
    ("探し方", "モデル事務所（リアルクローズ系）、Instagramの通勤スナップ、知人",
     "知人・友人、またはモデル事務所の安い枠。SNSで直接声をかけてもよい",
     "宮下さんご自身の手で撮れる。人を探さなくてよい唯一の一本", False),
    ("拘束", "一日", "半日", "半日", False),
    ("撮影場所", "玄関・並木道・駅・会社のロビーの四か所",
     "街の三〜四か所（フェンス・石壁・高い通路）", "机の上だけ。正面固定", False),
    ("費　用", "事務所により幅が大きい。二〜三社に見積を取る",
     "知人なら謝礼のみ。事務所を使うなら要見積", "かからない", False),
]


def sheet_matrix(wb):
    ws = wb.create_sheet("三本まとめ")
    title_block(ws, "出演者　── ①④⑦のモデル像",
                "三本のうち、顔が要るのは①だけ。④は顔を主役にせず、⑦は顔が入らない。"
                "だから探す手間が三本でまるで違う。①は本気で探す一本、④は知人に頼めば足り、⑦は宮下さんの手で撮れる。",
                [16, 40, 40, 40])

    r = 5
    for i, h in enumerate(HEADS):
        c = ws.cell(row=r, column=i + 1, value=h)
        fill = LBL_HEAD if i == 0 else C[str([0, 1, 4, 7][i])]["head"]
        style(c, size=10, bold=True, color=WHITE, fill=fill, va="center", ha="center")
    ws.row_dimensions[r].height = 34

    for label, v1, v4, v7, hi in MATRIX:
        r += 1
        c = ws.cell(row=r, column=1, value=label)
        style(c, size=9.5, bold=True, color=INK,
              fill=HILITE if hi else LBL_FILL, va="center")
        for i, (key, val) in enumerate((("1", v1), ("4", v4), ("7", v7))):
            c = ws.cell(row=r, column=i + 2, value=val)
            style(c, size=9.5, bold=hi,
                  color=DEEP if hi else INK,
                  fill=C[key]["strong"] if hi else C[key]["tint"])
        ws.row_dimensions[r].height = 34 if hi else 30

    ws.freeze_panes = "B6"
    return ws


# ────────────────────────────────────────────────────────────────
# 2枚目　①の細かいところ
# ────────────────────────────────────────────────────────────────
DETAIL1 = [
    ("年齢", "二十八〜三十五歳。中心は三十歳前後",
     "財布からバッグまで同じ革で揃える買い方をするのがこの年代。学生に見えると価格が浮く。"
     "四十代以上だと「服を替えると気分が変わる」という話が生活実感から離れ、二十五歳より下だと通勤ではなく休日の外出に見える"),
    ("性別・人数", "女性 一人",
     "五色のバッグが並ぶ締めの画（S7）は、女性の持ち物として並べたほうが色の差が出る。参考動画（innovator SWEDEN）も女性が主役。"
     "男女二人で交互に出す案もあるが、この一本は「同じ人が、着るものだけ変わる」という決まりごとでできているので、二人になると仕掛けが崩れる"),
    ("イメージ", "会社に通っている人に見えること。そのうえで服を選ぶのが好きそうに見える人",
     "モデル然としすぎない。ポーズを取る人ではなく歩いている人。"
     "華やかさより清潔感と姿勢。派手な顔立ちだと鞄より顔を見てしまう。"
     "「雑誌の表紙の人」ではなく「街のスナップに写っていて、つい二度見する人」"),
    ("身長・体型", "百六十〜百七十センチ。背中がまっすぐ",
     "鞄との比率がいちばん自然に見える範囲。細すぎると鞄が重そうに見えて「毎日持てる」に見えない。"
     "肩に厚みがある人のほうが大きめの鞄が似合う。全身の引きが十枚あるので、猫背だと五場面すべてに出る"),
    ("髪", "肩より短いか、まとめられる長さ。五色を通して髪型は変えない",
     "服だけが変わるから仕掛けが分かる。髪まで変えると「別の人」に見えて成立しない。"
     "明るすぎる色は避ける。金髪に近いと、革の色より髪の色が先に目に入る"),
    ("表情", "すまし顔と笑顔の差が、腰より上の寄り一枚で分かること",
     "S5（会社に着いて肩の鞄を掛け直して笑う）が三十秒でいちばん明るい表情になる。ここで自然に笑えるかを必ず見る。"
     "巻き戻りのシーンは横移動で追うので、横顔・後ろ姿もきれいなこと"),
    ("歩き方", "ここがいちばん大事。顔よりも歩き方で選ぶ",
     "この一本はほとんどが歩いている画で、カメラの前を五回歩き直す。歩きが硬い人だと三十秒がもたない。"
     "テンポよく、まっすぐ、カメラを意識しないで歩ける人"),
    ("手・爪", "爪は短く、色は透明か薄いベージュまで。指輪は外す",
     "手元の超アップは冒頭のキーケース（S1-1）だけだが、そこは寄りなので手がはっきり映る。"
     "革の色を見せる一本なので、手元に別の色を入れない"),
    ("服・靴", "五色ぶん。本人の私服＋足りない色をこちらで用意",
     "何色にするかは鞄の色に合わせて撮影前に決める（企画書にも「何色を使うかは撮影までに決めます」と入れてある）。"
     "靴も替わって見えるほうがよいが、無理なら共通で構わない。全身の引きでも足元は小さい"),
    ("通りすぎる人（S5）", "二〜四人",
     "画面の手前を横切るだけなので年齢・性別はばらけてよい。知人・友人に頼むか、エキストラを手配する。"
     "カメラを見ないこと、歩く速さが一定であることの二つだけ守ってもらう ── 通る速さがばらつくと、巻き戻りのテンポが崩れる"),
    ("探し方", "モデル事務所（リアルクローズ系・ノンモデル系の枠）、Instagramの通勤スナップ、知人からの紹介",
     "知人からの紹介でも、上の条件に合えば十分。事務所を使う場合は費用の幅が大きいので二〜三社に見積を取る"),
    ("拘束", "一日",
     "玄関・並木道・駅・会社のロビーの四か所で撮り切る。着替えが五回あるので余裕を見る"),
]

DETAIL4 = [
    ("年齢", "二十五〜三十五歳", "①より少し若くてよい。顔が出ないぶん、年齢は服と姿勢で伝わる"),
    ("性別", "男性 一人を推す（女性でも可）",
     "①を女性でいくので、並べたときに対になる。フェンス・石壁・高い通路という画は、男性の立ち姿のほうが背景に負けない"),
    ("イメージ", "街に馴染む人。服は無地・暗い色、一着でよい",
     "この一本は鞄が主役で、人は背景に近い扱い。柄物やロゴが入ると鞄が負ける。着替えはなし"),
    ("身長・体型", "百七十五センチ前後、細身。姿勢がいいこと",
     "石壁・フェンス・高い通路と直線の多い背景なので、線の細い立ち姿が合う。"
     "全身の引きが多く後ろ姿・横向きで撮るので、顔を見せないぶん姿勢だけで印象が決まる"),
    ("手", "爪は短く、傷や絆創膏がないこと。時計は外す。手だけ別の人でも可",
     "真俯瞰の寄りが二カット（鞄の口を開ける／中身を整える）。ここだけは手がはっきり映る。"
     "顔が出ないので、立ち姿の人と手の人を分けても誰も気づかない"),
    ("靴", "履き古していない一足を用意",
     "最後の置き画（S4-2 真俯瞰で鞄と持ち物と靴を並べる）に入る"),
    ("探し方・拘束", "知人・友人、またはモデル事務所の安い枠。半日",
     "顔を主役にしないので、事務所を通さず知人に頼んでも成立する。街の三〜四か所、着替えなし"),
]

DETAIL7 = [
    ("年齢", "三十〜四十代の手",
     "顔が出ないので年齢は手の質感でしか伝わらない。若すぎる手だと「仕事道具として毎日使う」という話に説得力が乗らない。"
     "逆に手が荒れているときれいに映すのが難しい"),
    ("手の条件", "爪が短く整っている。塗らないか透明。傷・絆創膏なし",
     "撮影の直前に切り傷ができると撮り直しになる"),
    ("外すもの", "指輪と腕時計は外す",
     "正面固定で九回同じ動作を撮るので、金属が光るたびに目がそちらへ行く"),
    ("服", "白か淡い色のシャツ。袖口が汚れていないもの", "袖が画面に入る"),
    ("動き", "ここがいちばん大事。ものを置く速さが一定であること",
     "この一本は音がすべて。入れる音を一つずつ拾うので、手が速い人・途中で迷う人だとテンポが崩れて音が揃わない。"
     "実際に机の上のものを鞄に入れてもらって、その一分で決める。顔を見る必要はない"),
    ("誰でよいか", "宮下さんご自身の手で撮れる。人を探さなくてよい",
     "三脚で正面固定、カメラを一度も動かさないので、一人で回せる唯一の一本"),
]


def sheet_detail(wb, name, title, lead, key, rows):
    ws = wb.create_sheet(name)
    title_block(ws, title, lead, [16, 34, 58])
    r = 5
    for i, h in enumerate(("項　目", "決めたこと", "な　ぜ")):
        c = ws.cell(row=r, column=i + 1, value=h)
        style(c, size=10, bold=True, color=WHITE,
              fill=LBL_HEAD if i == 0 else C[key]["head"], va="center", ha="center")
    ws.row_dimensions[r].height = 30
    for label, decided, why in rows:
        r += 1
        style(ws.cell(row=r, column=1, value=label), bold=True, fill=LBL_FILL, va="center")
        style(ws.cell(row=r, column=2, value=decided), bold=True,
              color=DEEP, fill=C[key]["strong"])
        style(ws.cell(row=r, column=3, value=why), color=MUTED, fill=C[key]["tint"])
        ws.row_dimensions[r].height = 46
    ws.freeze_panes = "A6"
    return ws


# ────────────────────────────────────────────────────────────────
# 4枚目　選ぶときに見ること／注意
# ────────────────────────────────────────────────────────────────
CHECK = [
    ("1", "①", "十メートルほど、まっすぐ歩いて戻ってきてもらう（二往復）", "歩きが硬くないか。ここで決まる"),
    ("1", "①", "笑ってもらう", "目まで笑うか。S5の表情になるか"),
    ("1", "①", "同じ位置に立ち直してもらう（二回）", "立ち位置がぶれないか。巻き戻りで同じ画角に戻せるか"),
    ("1", "①", "鞄を肩に掛け直してもらう", "S5-2 の動きがぎこちなくないか"),
    ("1", "①", "五色のうち二色を着てもらう", "着替えが似合うか。髪型を変えずに済むか"),
    ("4", "④", "横向きに立ってもらう", "姿勢を直さずに、まっすぐ立てているか"),
    ("4", "④", "後ろ姿で歩いてもらう", "後ろ姿だけで年齢が伝わるか"),
    ("4", "④", "手の甲と爪を見せてもらう", "真俯瞰の寄り二カットに耐えるか"),
    ("7", "⑦", "机の上に並べたものを、鞄に一つずつ入れてもらう（一分）", "速さが揃うか。それだけ"),
]

NOTES = [
    ("①のモデルは、ほかの本には出さない",
     "同じ顔が何本にも出ると、八本が一つの広告に見えて、それぞれの本が持っている別々の話が薄まる"),
    ("①と④を同じ日に撮ろうとしない",
     "①は着替えが五回あるので、一日まるごと使う"),
    ("人選より先に、撮影の許可を押さえる",
     "①は駅の構内と会社のロビー、④は街の三〜四か所を使う。場所が押さえられないと人選がやり直しになる"),
    ("⑦は先に撮っておける",
     "机の上だけで完結し、宮下さんの手で足りる。①④の人選を待たずに進められる"),
]


def sheet_check(wb):
    ws = wb.create_sheet("見ること・注意")
    title_block(ws, "選ぶときに、その場で見ること",
                "会って十分で決められるように、見る順に並べてある。チェック欄は使いながら埋めてください。",
                [6, 46, 40, 8])
    r = 5
    for i, h in enumerate(("本", "見ること", "何を確かめるか", "済")):
        c = ws.cell(row=r, column=i + 1, value=h)
        style(c, size=10, bold=True, color=WHITE, fill=LBL_HEAD, va="center", ha="center")
    ws.row_dimensions[r].height = 28
    for key, mark, what, why in CHECK:
        r += 1
        style(ws.cell(row=r, column=1, value=mark), bold=True, color=WHITE,
              fill=C[key]["head"], va="center", ha="center")
        style(ws.cell(row=r, column=2, value=what), bold=True, fill=C[key]["strong"], va="center")
        style(ws.cell(row=r, column=3, value=why), color=MUTED, fill=C[key]["tint"], va="center")
        style(ws.cell(row=r, column=4, value=""), fill="FFFFFF", va="center", ha="center")
        ws.row_dimensions[r].height = 30

    r += 2
    c = ws.cell(row=r, column=1, value="注　意")
    style(c, size=12, bold=True, color=ACCENT, fill=None, border=False, va="center")
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
    ws.row_dimensions[r].height = 26
    r += 1
    for i, h in enumerate(("", "こ　と", "な　ぜ", "")):
        c = ws.cell(row=r, column=i + 1, value=h)
        style(c, size=10, bold=True, color=WHITE, fill=LBL_HEAD, va="center", ha="center")
    for head, why in NOTES:
        r += 1
        style(ws.cell(row=r, column=1, value=""), fill=LBL_FILL)
        style(ws.cell(row=r, column=2, value=head), bold=True, fill=HILITE, va="center")
        style(ws.cell(row=r, column=3, value=why), color=MUTED, fill=LBL_FILL, va="center")
        style(ws.cell(row=r, column=4, value=""), fill=LBL_FILL)
        ws.row_dimensions[r].height = 34
    return ws


def main():
    wb = Workbook()
    wb.remove(wb.active)
    sheet_matrix(wb)
    sheet_detail(wb, "①の細かいところ", "①　その日の服に、その日の色。",
                 "三本のなかで唯一、人選が結果を決める一本。顔よりも歩き方で選ぶ。", "1", DETAIL1)
    sheet_detail(wb, "④の細かいところ", "④　What You Carry Makes You",
                 "顔を主役にしない。選ぶのは立ち姿と手だけ。知人に頼めば足りる。", "4", DETAIL4)
    sheet_detail(wb, "⑦の細かいところ", "⑦　朝も仕事も、スマートに。",
                 "顔は入らない。実質ハンドモデル。宮下さんご自身の手でも撮れる。", "7", DETAIL7)
    sheet_check(wb)
    out = os.path.join(ROOT, "pdf", "05_出演者_モデル像.xlsx")
    wb.save(out)
    print(out)


if __name__ == "__main__":
    main()
