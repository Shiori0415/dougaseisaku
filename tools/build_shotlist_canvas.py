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
MOVED = {("05", 7): ([1, 2], "一日目"),
         ("02", 4): ([2, 3, 4], "二日目"),
         ("06", 2): ([3], "四日目"), ("06", 8): ([3], "四日目"),
         ("03", 3): ([4], "四日目"), ("03", 5): ([1], "四日目")}
REUSE = {("05", 4): "⑥から引っ張る"}
# 同じ日に別のシーンで撮ったカットをそのまま使うもの → （本, シーン）: （カット番号, どこから）
QUOTE = {}

# シーンごとの登場（人 ／ 物）
CASTPROP = {
("01",1):("モデル", "一色目の衣装・鞄"),
("01",2):("モデル", "二色目の衣装・鞄"),
("01",3):("モデル", "三色目の衣装・鞄"),
("01",4):("モデル", "四色目の衣装・鞄"),
("01",5):("モデル、通行人", "四色ぶんの衣装・鞄"),
("01",6):("モデル", "鞄 四種類、ロゴ"),
("02",1):("工房のチーム", "革のロールが並ぶ棚"),
("02",2):("佐藤さん、工房のチーム", "抜き型、革、裁断機"),
("02",3):("佐藤さん、工房のチーム", "革 二枚、型"),
("02",4):("佐藤さん、工房のチーム、くさがやさん", "ミシン、糸、革、手縫いの道具"),
("02",5):("佐藤さん、工房のチーム", "刃、道具、革"),
("02",6):("佐藤さん、工房のチーム", "コバ塗料、道具、断面"),
("02",7):("佐藤さん、工房のチーム", "木槌、道具、立ち上がった鞄"),
("02",8):("佐藤さん、工房のチーム", "完成した鞄、ロゴ"),
("03",1):("―", "鞄の一部（光の帯だけ）、黒スチレンボード"),
("03",2):("くさがやさん", "革 二枚、染料、道具"),
("03",3):("くさがやさん、佐藤さん", "革"),
("03",4):("くさがやさん", "金具、白手袋"),
("03",5):("くさがやさん、佐藤さん", "完成品、工房の道具、ロゴ"),
("04",1):("モデル", "鞄、鉄のフェンス"),
("04",2):("モデル", "鞄、中に入れる持ち物"),
("04",3):("モデル", "鞄"),
("04",4):("モデル", "鞄、持ち物、靴、ロゴ"),
("05",1):("―", "表参道の並木通り（高いところから）"),
("05",2):("永尾社長、くさがやさん", "色見本、革、店舗の机"),
("05",3):("永尾社長、くさがやさん", "図面、型紙"),
("05",4):("―", "―"),
("05",5):("―", "店内の商品、ショーウィンドウ"),
("05",6):("くさがやさん、購入者", "商品、ノートPC"),
("05",7):("永尾社長", "ロゴ"),
("06",1):("工房のチーム", "工房の入口、通路、機械"),
("06",2):("佐藤さん、工房のチーム", "材料の壁、機械"),
("06",3):("職人", "革の棚、金型、型紙"),
("06",4):("職人", "裁断機、革包丁、裁ち上がったパーツ"),
("06",5):("職人", "へら、スプレー、コバ塗料"),
("06",6):("職人", "ミシン、糸、部品"),
("06",7):("職人", "上がった品"),
("06",8):("佐藤さん、梱包場の人", "不織布、箱、テープ"),
("06",9):("―", "文字のカード、ロゴ"),
("07",1):("出演者", "鞄、机"),
("07",2):("出演者", "A4書類、13インチPC"),
("07",3):("出演者", "手帳、鍵、サングラス、ペン、傘、水筒"),
("07",4):("出演者", "鞄"),
("07",5):("―", "何も乗っていない机、ロゴ"),
("08",1):("購入者、店の人", "店の外観、入口の扉、商品と棚、レジ"),
("08",2):("―", "商品、ロゴの壁"),
("08",3):("購入者", "商品、手前に置く植物"),
("08",4):("購入者", "商品、窓辺"),
("08",5):("購入者", "鞄、店の前の通り、空"),
("08",6):("購入者", "表情のアップ"),
("08",7):("購入者、くさがやさん", "ロゴ"),
("08",8):("―", "ロゴ"),
}

DAYS = [
 dict(key="d1", no="一日目", place="店舗・事務所", theme="⑤の語りと机まわり、そのまま⑦",
      date="一日目", date2="一日目　── 10月中（日にちは未定・月曜か火曜）",
      toc=[("05", "永尾社長・くさがやさんのインタビュー、店内、企画・設計"),
           ("07", "五シーンすべて（事務所の机・正面固定）")],
      cond="<b>店の休みの日（月曜か火曜）に撮る。</b>お客さんが入らないので、時間の縛りはない。",
      gear="カメラ／三脚／ガンマイク／レコーダー／PLフィルター／白い板／可変ND／"
           "鞄に入れる物 一式（A4書類・13インチPC・手帳・鍵・サングラス・ペン・傘・水筒）",
      keys=["インタビューは窓を横に。二人は別の場所・別の画角。",
            "店内の雰囲気は人を入れない。",
            "企画と設計は続けて撮る。あいだに別の本を入れない。",
            "⑦は三脚を立てたら最後まで触らない。五シーンを一度で通す。"],
      talks=[("9:00〜9:30", "永尾社長", "店内（窓を横に・インタビューの一角）",
              "", "",
              [("05", 7)], "⑤ インタビュー"),
             ("9:35〜10:05", "くさがやさん", "店内の別の一角（棚を背に）",
              "", "永尾社長とは別の場所・別の画角。横顔で撮る。", [], "⑤ インタビュー（店）")],
      setups=[('10:15〜11:00', '店舗の机（打ち合わせの場所）', [("05", 2), ("05", 3)],
               '<b>企画から設計まで、続けて撮る。</b>机は一度組んだら動かさない。'),
              ('11:10〜12:10', '事務所の机（正面固定）',
               [("07", 1), ("07", 2), ("07", 3), ("07", 4), ("07", 5)],
               '<b>五シーンを切らずに、頭から終わりまで一度で通す。</b>三テイク。'),
              ('12:10〜13:10', '昼休み', [], ''),
              ('13:10〜13:40', 'Bロール（まとめて撮る）', [("05", 5)],
               '人が映らないカット。<b>棚・照明・ショーウィンドウは、'
               'インタビューで出た言葉に合うものだけ選んで撮る。</b>')]),

 dict(key="d2", no="二日目", place="店舗", theme="購入者と、くさがやさんの手仕事",
      date="二日目", date2="二日目　── 10月中（日にちは未定・月曜か火曜）",
      toc=[("08", "店の前と店内、窓辺のインタビュー、外に出て使う場面、見送り"),
           ("05", "購入・使う（会計・手渡し・使っている手元）"),
           ("02", "くさがやさんの引き二枚と目元一枚（S4のぶんだけ）"),
           ("03", "五シーンすべて（店舗内の作業台）　くさがやさんが通しで作る")],
      cond="<b>店の休みの日（月曜か火曜）に撮る。</b>"
           "②でこの日に撮るのは<b>引きと目元だけ</b>なので、くさがやさんの手元には"
           "<b>縫いかけのパーツが一つあればよい</b>。仕上がっている必要はない。"
           "③は窓の光が入らない一角で、蛍光灯を全部消す。",
      gear="カメラ／三脚／ガンマイク／レコーダー／PLフィルター／可変ND／白い板／手前に置く植物／"
           "商品／黒スチレンボード／ライト一灯／裁断と貼り合わせを済ませたパーツ",
      keys=["購入者の拘束は 9:00〜12:35。",
            "<b>撮る場面を先に済ませてから、インタビューに入る。</b>",
            "撮る順は ⑧S1 → ⑧S7 → ⑧S5 → ⑤S6 → ⑧S3 → ⑧S4 → ⑧S6。",
            "<b>②はくさがやさんの引きと目元だけ。手元が読める寄りは撮らない。</b>",
            "③はライト一灯だけ。当たっていない側は黒く落とす。",
            "②③は、光の向き・高さ・距離とケルビンを数字で控える。四日目に同じに組む。"],
      setups=[('9:00〜9:55', '店の前（外から中へ・見送り・開店準備）', [("08", 1), ("08", 7)],
               '<b>つかみと見送りは同じ立ち位置。設営は一度。</b>'
               '<b>商品と手元の寄りは、購入者が入ってくる前にこの枠で撮る。</b>'),
              ('10:05〜10:30', '店の前の通り', [("08", 5)],
               '使っている場面。外で動いてもらって、体をほぐす。'),
              ('10:40〜11:15', '店内のレジまわり', [("05", 6)],
               '会計から使う場面まで。<b>ここまでで、話す前にカメラに慣れてもらう。</b>'
               '<b>⑧S1の4枚目（店に入って選んで買う引き）も、ここで続けて撮る。</b>'
               '<b>応対するのは⑧S1の3枚目で手元が映る人。服は変えない。</b>'),
              ('11:25〜12:35', '店の窓辺（手前に植物を置いてボカす）',
               [("08", 3), ("08", 4), ("08", 6)],
               '<b>ここからインタビュー。</b>三シーン続けて。カメラは動かさない。'),
              ('12:35〜13:25', '昼休み', [], ''),
              ('13:25〜13:40', 'Bロール（まとめて撮る）', [("08", 2)],
               '人が映らないカット。③の台に組み替える前に済ませる。'),
              ('13:40〜14:05', '店舗の作業台（②・くさがやさんの引きと目元）', [],
               '<b>手元の品が読める寄りは撮らない。</b>四日目と同じ光の向き・高さ・距離、'
               '同じケルビンで組む。',
               '<b>②S4 2枚目・3枚目・4枚目</b><br>'
               '引き（手縫いをしている全身）／目元だけの寄り（手も品も入れない）／もう一段引く。',
               'くさがやさん<div style="color: #5b6266; margin-top: 3px">'
               '縫いかけのパーツ、手縫いの道具</div>'),
              ('14:05〜16:07', '店舗内の作業台（③・黒スチレンボード）',
               [("03", 1), ("03", 2), ("03", 3), ("03", 4), ("03", 5)],
               '<b>五シーンとも、くさがやさんが頭から通して作る。工程は分けない。</b>'
               '佐藤さんの二枚（S3 4枚目の目元・S5 1枚目の引き）だけ四日目に工房で撮る。')]),

 dict(key="d3", no="三日目", place="向島工房", theme="⑥を工程順に、平日の工房で",
      date="三日目", date2="三日目　── 10月中（日にちは未定・平日）",
      toc=[("06", "工房の全体と機械、革と金型、裁断、下仕事、縫製、検品、梱包")],
      cond="<b>平日に撮る。</b>機械が動いていて、人がいる時間。"
           "引きの画に人が入るので、⑥はこの日でないと成立しない。",
      gear="カメラ（広角）／三脚／ガンマイク／白い板（発泡スチロール）／脚立／養生テープ",
      keys=["画に入れるのはブルックリンの品だけ。",
            "蛍光灯と窓の光を混ぜない。明るさとWBはマニュアル固定。",
            "工程ごとにカメラを置き直す。歩いて見せない。",
            "一工程につき三カット（引き・手元の寄り・道具の超クローズ）。"],
      setups=[("9:30〜9:50", "工房の全体が入る位置", [("06", 1)],
               "歩かずに置く位置を変える。⑤S4の画もここから。"),
              ("9:50〜10:10", "材料の棚と機械の並び", [("06", 2)],
               "佐藤さんの引きだけは四日目に撮る。"),
              ("10:10〜10:45", "革の棚・金型の棚", [("06", 3)], "棚の奥行きが出る位置から。"),
              ("10:45〜11:20", "裁断機のまわり", [("06", 4)], "⑤S4の手元もここから。"),
              ("11:20〜12:05", "下仕事の台", [("06", 5)], ""),
              ("12:05〜13:05", "昼休み", [], "工房の昼休みに合わせる。"),
              ("13:05〜13:50", "ミシンのまわり", [("06", 6)], "手縫いのカットも一つ撮る。"),
              ("13:50〜14:25", "検品の台", [("06", 7)], "ここで作業音がいったん消える。"),
              ("14:25〜14:55", "梱包の台", [("06", 8)], "紙とテープの音を拾う。")]),

 dict(key="d4", no="四日目", place="向島工房（休日）", theme="②を工程順に、静かな工房で",
      date="四日目", date2="四日目　── 10月中（日にちは未定・佐藤さんの休日）",
      toc=[("02", "八シーンすべて　佐藤さんが一つの鞄を頭から作りきる"),
           ("06", "佐藤さんのインタビュー"),
           ("03", "佐藤さんの二枚（目元と引き・工房の一角）")],
      cond="<b>佐藤さんの休日に合わせる。</b>工房が止まっているので、出入りの音が入らない。"
           "②の録音にはこの日でないといけない。機械は佐藤さんに動かしてもらう。"
           "<b>佐藤さんは店舗には行かない。②③で佐藤さんが映るカットは、すべてこの日にまとめる。</b>",
      gear="カメラ（広角）／マクロ／三脚／ガンマイク／レコーダー／白い板／脚立／"
           "黒スチレンボード／ライト一灯／②で作りきる鞄 一つぶんの材料",
      keys=["<b>②は一つの鞄を頭から作りきる。</b>作る順のとおりで、順番は入れ替えられない。",
            "<b>引きには工房のチームも入れる。</b>手元の寄りだけは佐藤さんでそろえる。",
            "<b>③でこの日に撮るのは佐藤さんの二枚だけ。工程シーンは二日目に全部ある。</b>",
            "③は二日目に組んだのと同じ光・同じ距離・同じケルビンで組む。",
            "②のコバ塗り以外は、機械の音を主役にする。"],
      talks=[("15:05〜15:35", "佐藤さん", "向島工房（窓を横に・他社の品が入らない一角）",
              "", "", [], "⑥ インタビュー")],
      setups=[("9:30〜9:50", "革のロールが並ぶ棚", [("02", 1)], "一枚だけ、三秒。"),
              ("9:50〜10:25", "裁断機のまわり", [("02", 2)], "型を置く・刃が入る・抜いたパーツ。"),
              ("10:25〜10:50", "作業台（真俯瞰の三脚が組める台）", [("02", 3)],
               "真俯瞰は台の上に直接置くか、脚立から。"),
              ("10:50〜11:35", "ミシンのまわり", [("02", 4)], "寄りと引きを交互に。"),
              ("11:35〜12:35", "昼休み", [], ""),
              ("12:35〜13:30", "作業台（②の下仕事とコバ塗り・超マクロ）",
               [("02", 5), ("02", 6)],
               "S4までと<b>同じ鞄をそのまま続けて撮る。</b>コバ塗りは切らずに六秒回す。"),
              ("13:30〜14:20", "同じ台（引きが撮れる位置まで下がる）",
               [("02", 7), ("02", 8)], "二シーンとも同じ画角。続けて撮る。"),
              ("14:30〜14:55", "工房の一角（③・黒スチレンボード）", [],
               "<b>二日目と同じ光の向き・高さ・距離・同じケルビンで組む。</b>"
               "<b>手も品も画に入れない。</b>だから工程が切れない。",
               "<b>③S3 4枚目</b><br>闇の中に、目元だけが光に入る（寄り）。<br>"
               "<b>③S5 1枚目</b><br>黒の中に、作業する人のシルエット（引き）。顔も手も見えない。",
               "佐藤さん<div style=\"color: #5b6266; margin-top: 3px\">黒スチレンボード、ライト一灯</div>")]),

 dict(key="d5", no="五日目", place="東京国際フォーラム → 表参道",
      theme="出演者を立てて撮る二本", date="五日目", date2="五日目　── 10月中（日にちは未定）",
      toc=[("01", "六シーンすべて（外の歩道 → 横断歩道 → 渡った先の通り → 扉 → ロビー）"),
           ("04", "柵（最初と最後）、置き画、けやき並木の歩道を歩く"),
           ("05", "冒頭の俯瞰（表参道を高いところから）")],
      cond="出演者と衣装・鞄 四色ぶんが揃ってから。永尾さんの車も要る（①の合図）。"
           "曇りの日に合わせる。晴れたら可変NDを付ける。予備日を一日とる。",
      gear="カメラ／三脚／三脚キャスター／可変ND／養生テープ／脚立／水準器／衣装と鞄 四色ぶん",
      keys=["<b>①は歩いて続く一本道で撮り切る。</b>丸の内仲通り → 東京国際フォーラム東交差点の横断歩道 → 地上広場 → ガラス棟の扉 → ロビー。",
            "四色ぶんは同じ立ち位置。床にテープを貼る。",
            "カメラの高さは胸で固定。",
            "<b>横断歩道は信号待ちが入る。ここだけ三十分見ておく。</b>",
            "<b>フォーラムの敷地と丸の内仲通りは、どちらも撮影の事前申請が要る。</b>"
            "横断歩道は都道。三脚を歩道に置くなら所轄への道路使用許可も要る。",
            "表参道は人が多い。交差点から離れた端と裏の路地を使う。",
            "④は三脚を止めて、背景だけを動かす。",
            "雨上がりの翌日は避ける。"],
      setups=[('9:00〜9:54', '丸の内仲通りのけやき並木 → 東京国際フォーラム東交差点の横断歩道',
               [("01", 1), ("01", 2)],
               '一色目は仲通りの並木が奥まで抜ける位置。二色目は<b>横断歩道を渡りきるところ</b>で、'
               '目の前を車が通り過ぎた一コマでつなぐ。<b>信号待ちが入るので三十分取る。</b>'),
              ('9:54〜10:31', '渡った先 ── 地上広場のけやきぎわ → ガラス棟の扉',
               [("01", 3), ("01", 4)],
               '三色目は<b>けやきの後ろを通った一瞬</b>、四色目は<b>扉をまたいだ一コマ</b>でつなぐ。'
               '<b>仲通りから扉まで、歩く向きを一度も変えない。</b>'),
              ('10:31〜11:41', '東京国際フォーラム ガラス棟ロビー（通路・ベンチ）',
               [("01", 5), ("01", 6)],
               '通路を歩いて巻き戻る。四色を並べるポーズもここで。'),
              ('11:41〜12:41', '移動（有楽町 → 表参道）', [], ''),
              ('12:41〜13:35', '昼休み', [], '出演者の拘束は 9:00〜16:05。'),
              ('13:35〜14:25', 'けやき並木の歩道（柵・手すり・青山通り寄りの端）', [("04", 1), ("04", 4)],
               '最初と最後は同じ柵。設営は一度。'),
              ('14:35〜15:03', 'ベンチか石段（真俯瞰が組めるところ）', [("04", 2)],
               '<b>モデルの手が真俯瞰で映る。</b>鞄に入れる持ち物を先に並べておく。'),
              ('15:10〜15:35', 'けやき並木の裏の路地（人がほとんど通らない側）', [("04", 3)],
               '人の少ない裏側で。'),
              ('15:35〜16:05', 'けやき並木の歩道（出演者はここまで）', [],
               '切らずに長めに三本。',
               '<b>⑤ 使用シーンの追加素材</b><br>街で鞄を持って歩く・手に取る・肩に掛け直す。',
               'モデル<div style="color: #5b6266; margin-top: 3px">鞄</div>'),
              ('16:15〜16:37', 'Bロール（まとめて撮る）', [("05", 1)],
               '人が映らないカット。<b>モデルが帰ったあとでよい。</b>')]),
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
    for _, _, sc, _ in [t[:4] for t in day.get("setups", [])]:
        for no, si in sc:
            yield no, si


def quote_cuts(no, si):
    return QUOTE.get((no, si), ([], ""))[0]


def day_counts(day):
    shoot = edit = 0
    for no, si in day_scenes(day):
        n = len(cuts_of(no, si)[1]) - len(moved_cuts(no, si))
        if is_edit_only(no, si) or (no, si) in REUSE:
            edit += n
        else:
            shoot += n - len(quote_cuts(no, si))
            edit += len(quote_cuts(no, si))
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
def day_of(no, si):
    return S.SPOT[no][si][2]


def plain_row(when, place, note, what="", who=""):
    td = f"padding: 14px 14px; border-bottom: 1px solid {LINE}; vertical-align: top"
    h, m = when.split("〜")
    a = int(h.split(":")[0]) * 60 + int(h.split(":")[1])
    b = int(m.split(":")[0]) * 60 + int(m.split(":")[1])
    mn = b - a
    length = f"{mn // 60}時間{mn % 60}分" if mn >= 60 else f"{mn}分"
    return f'''<tr style="background: {BAND}">
      <td style="{td}; padding-left: 0; white-space: nowrap">
        <span style="font-size: 18px; font-weight: 700; color: {GOLD}">{esc(when)}</span></td>
      <td style="{td}; font-size: 16px; font-weight: 700; color: {INK}">{esc(place)}</td>
      <td style="{td}; font-size: 15px; line-height: 1.65; color: {INK}">{who if who else "―"}</td>
      <td style="{td}; font-size: 16px; line-height: 1.65; color: {INK}">{what if what else "―"}</td>
      <td style="{td}; font-size: 15px; color: {MUTED}; white-space: nowrap">{length}</td>
      <td style="{td}; padding-right: 0; font-size: 15px; line-height: 1.65; color: {MUTED}">{note}</td>
    </tr>'''


def scene_len(no, si):
    """絵コンテの秒数から、そのシーンの尺を出す"""
    pg = pages().get(no)
    if not pg or si > len(pg["rows"]):
        return "―"
    sp = sec_span(pg["rows"][si - 1][1])
    if not sp:
        return "―"
    return "%d秒" % (sp[1] - sp[0]) if sp[1] != sp[0] else "%d秒" % sp[0]


def scene_row(no, si, extra=""):
    nm, cuts = cuts_of(no, si)
    place, _, _, when = S.SPOT[no][si]
    cam, note = split_cam(S.D[no][si][0])
    td = f"padding: 14px 14px; border-bottom: 1px solid {LINE}; vertical-align: top"
    who, prop = CASTPROP.get((no, si), ("―", "―"))
    mv, mvday = MOVED.get((no, si), ([], ""))
    memo = []
    if extra:
        memo.append(extra)
    if mv and len(mv) == len(cuts):
        memo.append(f'{len(cuts)}カット。<span style="color: {GOLD}">インタビューの収録で撮る</span>')
    else:
        qc, qfrom = QUOTE.get((no, si), ([], ""))
        m = f'{len(cuts) - len(mv) - len(qc)}カット'
        if mv:
            where = "インタビューの収録で撮る" if mvday == day_of(no, si) else f"{mvday}に撮る"
            m += f'（<span style="color: {GOLD}">{"・".join(str(k) + "枚目" for k in mv)}は{where}</span>）'
        if qc:
            m += f'（<span style="color: {GOLD}">{"・".join(str(k) + "枚目" for k in qc)}は撮らない ── {qfrom}</span>）'
        memo.append(m)
    return f'''<tr>
      <td style="{td}; padding-left: 0; white-space: nowrap">
        <span style="font-size: 18px; font-weight: 700; color: {GOLD}">{esc(when)}</span></td>
      <td style="{td}; font-size: 16px; line-height: 1.65; color: {INK}">{place if place != "同じ" else f'<span style="color:{MUTED}">同じ</span>'}</td>
      <td style="{td}; font-size: 15px; line-height: 1.65; color: {INK}">{who}<div style="color: {MUTED}; margin-top: 3px">{prop}</div></td>
      <td style="{td}; font-size: 16px; line-height: 1.65; color: {INK}">
        <div style="font-weight: 700"><span style="color: {GOLD}">{MARU[no]}</span> {esc(nm)}</div>
        <div style="margin-top: 4px">{cam}</div></td>
      <td style="{td}; font-size: 15px; color: {MUTED}; white-space: nowrap">{scene_len(no, si)}</td>
      <td style="{td}; padding-right: 0; font-size: 15px; line-height: 1.65; color: {MUTED}">{"<br>".join(memo)}</td>
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


def start_min(when):
    if not when or when == "―":
        return 10 ** 6
    h, m = when.split("〜")[0].split(":")
    return int(h) * 60 + int(m)


def talk_rows(day, t):
    td = f"padding: 14px 14px; border-bottom: 1px solid {LINE}; vertical-align: top"
    when, who, place, what, note = t[:5]
    label = t[6] if len(t) > 6 else "インタビュー"
    out = [f'''<tr>
      <td style="{td}; padding-left: 0; white-space: nowrap">
        <span style="font-size: 18px; font-weight: 700; color: {GOLD}">{esc(when)}</span></td>
      <td style="{td}; font-size: 16px; line-height: 1.65; color: {INK}">{place}</td>
      <td style="{td}; font-size: 15px; line-height: 1.65; color: {INK}">{esc(who)}<div style="color: {MUTED}; margin-top: 3px">椅子、レコーダー</div></td>
      <td style="{td}; font-size: 16px; line-height: 1.65; color: {INK}">
        <div style="font-weight: 700">{esc(label)}</div>
        <div style="margin-top: 4px">{what}</div></td>
      <td style="{td}; font-size: 15px; color: {MUTED}; white-space: nowrap">三十分</td>
      <td style="{td}; padding-right: 0; font-size: 15px; line-height: 1.65; color: {MUTED}">{note}</td>
    </tr>''']
    return "".join(out)


def day_titles(day):
    pg = pages()
    return "　／　".join(MARU[no] + " " + pg[no]["jp"] for no, _ in day["toc"])


def day_artboard(day):
    shoot, edit = day_counts(day)
    hl = (f"font-size: 15px; color: {FAINT}; letter-spacing: 0.08em; padding: 9px 0; "
          f"vertical-align: top; border-bottom: 1px solid {LINE}")
    hv = (f"font-size: 17px; line-height: 1.7; color: {INK}; padding: 9px 0 9px 4px; "
          f"vertical-align: top; border-bottom: 1px solid {LINE}")
    th = ("text-align: left; font-size: 15px; font-weight: 400; color: " + FAINT +
          "; letter-spacing: 0.08em; border-bottom: 1px solid " + INK + "; padding-bottom: 11px")
    blocks = []
    for t in day.get("talks", []):
        blocks.append((start_min(t[0]), talk_rows(day, t)))
    for setup in day.get("setups", []):
        when, place, sc, note = setup[:4]
        sc_what = setup[4] if len(setup) > 4 else ""
        sc_who = setup[5] if len(setup) > 5 else ""
        if not sc:
            blocks.append((start_min(when), plain_row(when, place, note, sc_what, sc_who)))
            continue
        for k, (no, si) in enumerate(sc):
            blocks.append((start_min(S.SPOT[no][si][3]) if S.SPOT[no][si][3] != "―" else start_min(when),
                           scene_row(no, si, note if k == 0 else "")))
    blocks.sort(key=lambda b: b[0])
    rows = [b for _, b in blocks]
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
  <table style="border-bottom: 2px solid {INK}; padding-bottom: 0">
    <colgroup><col style="width: 190px"><col></colgroup>
    {"".join(f'<tr><td style="{hl}">{a}</td><td style="{hv}">{b}</td></tr>' for a, b in [
      ("タ イ ト ル", f'<span style="font-size: 24px; font-weight: 700">{day_titles(day)}</span>'),
      ("撮 影 日", f'<span style="font-size: 20px; font-weight: 700">{esc(day["date2"])}</span>'),
      ("場 所", esc(day["place"])),
      ("時 間", f'{esc(day_span(day))}　<span style="color: {FAINT}">撮るカット {shoot}</span>'),
      ("緊 急 時 連 絡 先", "　"),
      ("注 意 事 項", day["cond"]),
    ])}
  </table>
  <table>
    <colgroup>
      <col style="width: 130px"><col style="width: 300px"><col style="width: 230px"><col><col style="width: 80px"><col style="width: 300px">
    </colgroup>
    <tr>
      <th style="{th}; padding-left: 0">時 刻</th>
      <th style="{th}; padding-left: 14px">場 所 の 詳 細</th>
      <th style="{th}; padding-left: 14px">登 場 人 物</th>
      <th style="{th}; padding-left: 14px">シ ー ン 内 容 詳 細</th>
      <th style="{th}; padding-left: 14px">尺</th>
      <th style="{th}; padding-left: 14px; padding-right: 0">備 考</th>
    </tr>
    {"".join(rows)}
  </table>
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
      <td style="{td}; padding-left: 0; font-size: 21px; font-weight: 700; color: {GOLD}; white-space: nowrap">{esc(d["date"].split("　※")[0])}</td>
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
      <div style="font-size: 40px; font-weight: 700; color: {INK}; letter-spacing: -0.01em">動画八本　香盤表</div>
      <div style="font-size: 17px; color: {FAINT}; letter-spacing: 0.06em">Shooting Schedule</div>
      <div style="margin-left: auto; font-size: 18px; font-weight: 700; color: {INK}">全八本　{tot_s}カット　／　撮影 五日</div>
      <div style="font-size: 15px; color: {GOLD}">日付は10月中で未定</div>
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
    """カメラの一文を「一枚目・二枚目…」で割って、カットごとの画角にする。
       「⑥S1 1枚目」のような他の本への参照は、割るときの番号として数えない。"""
    cam, _ = split_cam(S.D[no][si][0])
    mask = re.sub(r"[①-⑨]S\d \d枚目", lambda m: "※" * len(m.group(0)), cam)
    idx = []
    for m in re.finditer(r"(\d)枚目", mask):
        k = int(m.group(1))
        if any(k == j for j, _, _ in idx):
            continue
        idx.append((k, m.start(), m.end()))
    idx.sort(key=lambda t: t[1])
    out = []
    for k, (_, pos, end0) in enumerate(idx):
        end = idx[k + 1][1] if k + 1 < len(idx) else len(cam)
        t = cam[end0:end].strip()
        t = re.sub(r"^(→|、|・)\s*", "", t)
        t = re.sub(r"\s*(→|。|／)\s*$", "", t)
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
            if k + 1 in quote_cuts(no, si):
                tag = f'<div style="font-size: 14px; color: {GOLD}; margin-top: 3px">撮影しない ── {QUOTE[(no, si)][1]}</div>'
            if (no, si) in REUSE:
                tag = f'<div style="font-size: 14px; color: {GOLD}; margin-top: 3px">撮影しない ── {REUSE[(no, si)]}</div>'
            rows.append(f'''<tr>
      <td style="{td}; padding-left: 0; white-space: nowrap">
        <span style="font-size: 17px; font-weight: 700; color: {INK}">{n:02d}</span>
        <span style="font-size: 15px; color: {FAINT}">　S{si} {k + 1}枚目</span></td>
      <td style="{td}; font-size: 16px; line-height: 1.6; color: {INK}">{angles[k] if k < len(angles) else ""}{tag}</td>
      <td style="{td}; font-size: 16px; line-height: 1.7; color: {INK}">{sh[1]}</td>
      <td style="{td}; padding-right: 0; font-size: 15px; color: {MUTED}; white-space: nowrap">{sec}</td>
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
      <col style="width: 150px"><col style="width: 470px"><col><col style="width: 150px">
    </colgroup>
    <tr>
      <th style="{th}; padding-left: 0">№　／　カット</th>
      <th style="{th}; padding-left: 14px">画 角</th>
      <th style="{th}; padding-left: 14px">撮 る も の</th>
      <th style="{th}; padding-left: 14px; padding-right: 0">尺 の 目 安</th>
    </tr>
    {body}
  </table>
  <div style="margin-top: auto; display: flex; justify-content: space-between; font-size: 13px; color: {FAINT}">
    <div>BROOKLYN MUSEUM ／ 向島工房　動画制作　／　香盤表</div>
    <div>{MARU[no]}　全{n}カット</div>
  </div>
</div>
</x-dc>
</body>
</html>
'''

CAST = [
 ("①", "01", "五日目", "映る（腰より上の寄りがある）",
  "鏡だけ。四回の着替えのあと、髪の乱れを直す。",
  "四色ぶんの服と鞄。<b>鞄の色と喧嘩しない服</b>を選ぶ。<br>ヘアメイクを付けないので、<b>髪型が崩れない服</b>にする ──<br>前開きの上着なら、着替えで髪が乱れない。",
  "着替え場所と荷物置き場。四回の着替えを見込んで、<br>東京国際フォーラムは使用時間を長めに申請する。"),
 ("④", "04", "五日目", "主役にしない（引きと後ろ姿）",
  "爪を切りそろえる。<b>手が寄りで映る。</b>",
  "一そろい。街に馴染む色。<br>鞄より目立つ柄は避ける。",
  "時計・指輪は外す。<br>歩く距離があるので、履き慣れた靴で。"),
 ("⑦", "07", "一日目", "映らない",
  "爪を切り、手を洗っておく。<br>時計・指輪は外す。",
  "袖口の見える無地の上着。<br>柄物だと、手の動きより袖に目が行く。",
  "物を置く速さが一定にできる方を選ぶ。<br>一度通してもらってから本番。"),
 ("⑧", "08", "二日目", "映る（バストショット）",
  "―",
  "本人のふだんの服。<br>細かい柄は画面で目がちらつくので避ける。",
  "顔出しの範囲を、撮る前に本人へ確認する。<br>名前は出さず「購入者Aさん」とだけ出す。<br>拘束は 9:00〜12:35。日は購入者が決まってから決める。"),
 ("⑤⑥", None, "一日目・四日目", "映る（バストショット・横顔）",
  "襟元と髪だけ、撮る直前に鏡で見る。",
  "ふだんの仕事着。<br>永尾社長・くさがやさんは一日目、佐藤さんは四日目。",
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
HEIGHT = {"cover": 964, "d1": 1517, "d2": 2057, "d3": 1459, "d4": 1489, "d5": 1786, "cast": 1217}


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    arts, x, y, col = [], 0, 0, 0
    items = ([("Main", "cover", cover_artboard)] +
             [(d["key"].upper(), d["key"], (lambda dd: (lambda: day_artboard(dd)))(d)) for d in DAYS] +
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
