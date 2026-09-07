# -*- coding: utf-8 -*-
"""台本（8本ぶん）のデザインキャンバス用に、1本＝1シートの .dc.html を書き出す。
   実行: python3 tools/build_script_canvas.py <出力ディレクトリ>

   ・画（何を撮るか）は tools/deck_data.json の絵コンテからそのまま持ってくる
     ── 絵コンテと台本が食い違わないようにするため、ここでは書き直さない
   ・カメラ・音・テロップ／セリフはこのファイルに書く（シーン単位）
   ・カットの秒数は、シーンの秒数をカット数で割って割り当てる
"""
import html, json, os, re, sys

INK, MUTED, FAINT = "#15191c", "#5b6266", "#8a8f92"
GOLD, LINE, PAPER = "#a8672a", "#ded9d0", "#fbfaf7"
MARGIN = 40
PAGE_W = 1640

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
# 話す人がいる三本だけが「台本」。ほかの五本はセリフがないので「撮影メモ」
TALK = {"05", "06", "08"}
SLUG = {"01": "Main", "02": "Video02", "03": "Video03", "04": "Video04",
        "05": "Video05", "06": "Video06", "07": "Video07", "08": "Video08"}

# 実際に描かせて測った高さ（内容を足したら測り直して入れ替える）
HEIGHT = {"01": 1085, "02": 1270, "03": 860, "04": 690,
          "05": 1530, "06": 1610, "07": 820, "08": 1140}


def esc(s):
    return html.escape(s, quote=True)


def plain(s):
    s = re.sub(r"<br\s*/?>", " ", s or "")
    return re.sub(r"<[^>]+>", "", s).strip()


# ─────────────────────────────────────────────────────────────
# 本ごとの前書き
# ─────────────────────────────────────────────────────────────
LEAD = {
"01": ("音楽で持たせる三十秒。セリフはなく、最後にナレーションが一言だけ入る。"
       "<b>支度が一色目、そこから四回替えて全部で五色。</b>切り替わりは必ず手前を何かが横切る前ボケで行い、"
       "抜けた瞬間に服と革の色が変わっている。<b>何色を使うかは撮影までに決める。</b>"),
"02": ("作業音だけで持たせる四十秒。ナレーションは入れない。<b>画面の下に工程名を一行だけ日英で出す。</b>"
       "完成形を最初に一度見せてから工程の頭に戻り、最後にもう一度同じ鞄で閉じる。"
       "<b>S6のコバ塗りだけカットを割らず、七秒そのまま回す。</b>"),
"03": ("黒い布一枚とライト一灯で撮る二十八秒。<b>工房の蛍光灯は全部消す。</b>手だけ、三脚固定、BGMのみ。"
       "作業音もテロップも入れない。<b>最後の一カットだけ、明るい工房の作業台に置いて実景に戻す。</b>"),
"04": ("カメラを一度も動かさない三十秒。<b>動くのは背景だけ。</b>自然光のみ、曇りの日でよい。"
       "テロップは画面に出さず、言葉は投稿の本文に置く。"),
"05": ("語り手は二人。永尾社長（冒頭から製造まで、そして締め）とくさがやさん（店舗と購入）。"
       "<b>台本は読み上げず、自分の言葉で言い直してもらう。</b>言い回しは変えてよいが、秒数と各シーンで触れることは変えない。"
       "<b>つなぎはJカット。</b>次に話す人の声を、画が切り替わる前から流しはじめる。"),
"06": ("語り手は佐藤さん一人。画に映るのは<b>S1の頭</b>と<b>S8の終わり</b>の二カットだけで、"
       "あとは声だけが全編に流れ続ける。<b>工房を歩きながら、自分の言葉で言い直してもらう。</b>"
       "この一本で言うのは三つ ── ①小ロットから量産まで同じ場所でできる ②裁断から梱包まで自社で完結する ③誰が作っているか顔が見える。"),
"07": ("正面固定、カメラは一度も動かさない二十五秒。<b>机に置かれた鞄から始める。</b>"
       "入る量と、入れ終わってそのまま持って出られることだけを見せる。"
       "<b>人も鞄もフレームから出て、何も乗っていない机だけが残る。</b>"),
"08": ("八本のうち、これだけが「聞く」動画。<b>買った人自身の言葉で語ってもらう。</b>"
       "<span style='color:#a8763e'>出演者・顔出しの範囲・撮影場所がまだ決まっていないため、下の質問と答えは仮です。"
       "決まり次第、実際に話してもらった言葉に差し替えます。</span>"
       "<b>話した言葉はすべてテロップで出す</b>（音を出さずに見る人が多いため）。"),
}

# ─────────────────────────────────────────────────────────────
# シーンごとの演出（カメラ ／ 音 ／ テロップ・セリフ）
#   キーは 本番号 → シーン番号（1始まり）
# ─────────────────────────────────────────────────────────────
D = {
"01": {
 1: ("手持ち。キーケースは開放でボケから合焦させる（フォーカス送り）。"
     "鏡は正面やや斜め・腰の高さ。玄関は逆光にして、露出はドアの外に合わせる。",
     "音楽が先に始まる。鍵の金属音とドアノブの音だけ小さく足す。",
     "出さない。"),
 2: ("全体＝全身が入る引き、歩いてくる正面。腰より上＝同じ位置から寄るだけで、立ち位置は変えない。"
     "水平を崩さない（三脚かジンバル）。",
     "音楽。足音を薄く。", "出さない。"),
 3: ("同じ画角のまま。<b>手前を車が横切った瞬間に人と色が変わる。</b>"
     "車が必ず前ボケになるよう、車道側に寄って撮る。",
     "音楽。車の通過音を一つ。", "出さない。"),
 4: ("駅の柱を前ボケに使う。<b>柱が画面を覆いきる一瞬でつなぐ。</b>構内の自然光のみ。",
     "音楽。構内のアナウンスは入れない。", "出さない。"),
 5: ("人が横切る前ボケでつなぐ。<b>横移動で追う</b>（スライダーか、歩きながら）。",
     "音楽。足音と人のざわめきを薄く。", "出さない。"),
 6: ("ロビーの柱でつなぐ。到着点なので少し引く。立ち止まったらカメラも止める。",
     "音楽。ここでいちばん明るくなる。", "出さない。"),
 7: ("バッグのアップ＝寄りで固定。五色＝真俯瞰で固定。ロゴ＝白バック。",
     "<b>音楽が一段落ちて、ナレーションが一言だけ入る ──「毎日をカラフルに」。</b>",
     "五色が並ぶ画に重ねる。<br><b>同じ道を、違う私で。</b><br>THE SAME ROUTE, A DIFFERENT ME."),
},
"02": {
 1: ("寄り、手持ち。<b>完成形は一度だけ、全部は見せない。</b>",
     "作業音のみ。BGMは入れない。", "出さない。"),
 2: ("引き＝広角で棚の奥行きを出す。運ぶ＝横から追う。",
     "棚の音、革がこすれる音。", "<b>革を選ぶ</b> ／ Choosing the leather"),
 3: ("真俯瞰（型を置く）→ 機械の横（刃が入る）→ 手元の寄り。三つとも三脚。",
     "<b>プレスが下りる一音を大きく。</b>", "<b>裁つ</b> ／ Cutting"),
 4: ("真俯瞰 → 超マクロ（重なった層）→ 斜め上から手元。",
     "革がこすれる音、押さえる音。", "<b>貼る</b> ／ Laminating"),
 5: ("引き（工房が入る）→ 針の超マクロ → 別の角度から寄り → <b>手縫いの寄り</b> → <b>刃の超マクロ</b>。"
     "五カットで、機械と手の両方でやっていることを見せる。",
     "<b>ミシンの連続音 → 糸を引き締める音 → 刃が入る一音。</b>ここだけ少し長く聞かせる。",
     "<b>縫う</b> ／ Stitching<br><span style='color:#8a7a63'>手縫いのカットでは替えず、シーンを通して一枚のまま。</span>"),
 6: ("<b>超マクロ・三脚固定。カットを割らず七秒そのまま回す。</b>"
     "塗った側と塗っていない側が同じ画面に入る位置に置く。",
     "<b>摩擦音だけ。BGMを一段下げる。</b>",
     "<b>コバを塗る</b> ／ Painting the edge<br>"
     "<span style='color:#a8763e'>ここだけ二行を足す ── 一つの製品の、四割の時間は、この断面に使われます。／ "
     "Forty percent of the making goes into this one edge.</span>"),
 7: ("引き（人が入る）→ 手元の寄り → 縁の寄り。",
     "磨く音。", "<b>仕上げる</b> ／ Finishing"),
 8: ("寄り → 横 → 白バックのロゴ。",
     "<b>作業音が引いて、無音になる。</b>",
     "<b>神は細部に宿る。</b><br>God is in the details."),
},
"03": {
 1: ("<b>黒い布一枚、ライト一灯。工房の蛍光灯は全部消す。</b>超マクロ、三脚固定。"
     "動くのは光の帯だけ。", "無音から低いBGMが立ち上がる。", "出さない。"),
 2: ("一灯のまま、手だけ。三脚固定。カメラは動かさない。", "BGMのみ。作業音は入れない。", "出さない。"),
 3: ("同じ一灯。手が形を作るところだけを追う。", "BGMのみ。", "出さない。"),
 4: ("<b>白手袋。</b>金具に一灯が反射する角度をつくる。", "BGMのみ。", "出さない。"),
 5: ("<b>最後の一カットだけ、明るい工房の作業台に置く。</b>ここで初めて実景に戻る。",
     "<b>BGMが終わり、ロゴが0.5秒。それで終える。</b>", "出さない。"),
},
"04": {
 1: ("<b>三脚で完全に固定。カメラは一度も動かさない。</b>動くのは背景だけ。",
     "街の環境音のみ。BGMは薄く。", "出さない。"),
 2: ("真俯瞰（脚立か手すりから）→ 手元の寄り → <b>次の画へ横にスライドしてつなぐ。</b>",
     "中身が触れる音を拾う。", "出さない。"),
 3: ("引きの固定 → 肩に掛かった鞄に寄る。<b>顔は主役にしない。</b>",
     "街の環境音。", "出さない。"),
 4: ("固定 → 真俯瞰の置き画 → ロゴ。<b>最初の画角には戻らない。</b>",
     "音が引いて、ロゴ。", "出さない。言葉は投稿の本文に置く。"),
},
"05": {
 1: ("空撮。高度を下げて建物に寄る。<b>永尾社長＝バストショット、顔の下に役職テロップ。背景は大きくボカす。</b>",
     "街の音 → 声。<b>声は空撮に寄るところから先に入る（Jカット）。</b>",
     "<b>永尾社長</b>「東京・向島。ここに、うちの工房があります。始まりは、一九七九年でした。」<br>"
     "役職テロップ（日英二行）＝ BROOKLYN MUSEUM ／ 代表取締役　永尾 ○○ ／ ○○ Nagao"),
 2: ("昔の写真と今の外観を<b>同じ構図で撮る。</b>白黒からカラーへ変わる。",
     "声が続く。BGMは薄く。",
     "<b>永尾社長</b>「千駄ヶ谷の小さな店から始めました。じきに、名前の知られたところから声をかけていただくようになりました。"
     "SHIPS、BEAMS、ユナイテッドアローズ、ポール・スミス。四十年以上、裏で作ってきました。」<br>"
     "<span style='color:#a8763e'>年号テロップは<b>画面の右端</b>に出す ── 1979 東京千駄ヶ谷にて創業／1980 SHIPS／1982 BEAMS／"
     "1984 To Boot New York／1990 UNITED ARROWS／1991 Paul Smith／2011 RALPH LAUREN 全直営店のカルトン</span>"),
 3: ("俯瞰気味に二人が覗き込む画 → 革を並べる寄り → 机の引き。",
     "打ち合わせの音を少し聞かせ、その上に声。",
     "<b>永尾社長</b>「仕事は、色を決めるところから始まります。革を並べて、手に取って、その場で決めます。」"),
 4: ("図面をなぞる手の寄り → 型紙の俯瞰 → 机の引き。",
     "紙とペンの音。声は続く。",
     "<b>永尾社長</b>「そこから型紙を起こして、寸法を詰めます。図面の上で決まったことが、そのまま形になります。」"),
 5: ("工房の全体（引き）→ 大型機械（引き）→ 手元（寄り）。<b>工程の説明はしない。</b>",
     "機械の音。<b>終わりぎわにくさがやさんの声が重なりはじめる（Jカット）。</b>",
     "<b>永尾社長</b>「作るのは、この工房です。大きな機械も、手でしかできない仕事も、同じ場所にあります。"
     "少ない数でも、まとまった数でも、ここで受けられます。」"),
 6: ("<b>くさがやさん＝横顔、空いた側に見出しテロップ。</b>店内の引き → ショーウィンドウ越し。",
     "店の環境音。声は次のカットにかぶったまま続く。",
     "<b>くさがやさん</b>「店には、実際に作ったものが並んでいます。同じ形でも、革の色で表情が変わります。"
     "手に取っていただくのが、いちばん早いです。」"),
 7: ("会計の引き → 手渡しと笑顔 → 使っている手元。",
     "店の音。<b>終わりぎわに永尾社長の声が戻る（Jカット）。</b>",
     "<b>くさがやさん</b>「選んでいただいて、お渡しして、使っていただく。そこまで見えるのが、この場所のいいところです。」"),
 8: ("<b>冒頭とまったく同じ画角に戻す。</b>言い終えて口を閉じるところまで残す。",
     "声が終わり、音が引く。",
     "<b>永尾社長</b>「一九七九年から続けてきた会社が、いま、この工房と一つになりました。」<br>"
     "<span style='color:#a8763e'>締めのテロップは出さない。最後はロゴだけ。"
     "<b>この一言は収録の最後に、締め用として一本言い切ってもらう。</b></span>"),
},
"06": {
 1: ("空撮で降りて建物へ。<b>佐藤さん＝引き、背景に工房。</b>ここから最後まで声が流れ続ける。",
     "街の音 → 工房の音。声が乗る。",
     "<b>佐藤さん</b>「向島の、この建物です。ここで、ブランドさんのお品を作っています。中をご案内します。」"),
 2: ("入口を抜けて中へ。工房の全景（引き）→ 機械と人 → 職人の横顔（寄り）。<b>歩くカメラ。</b>",
     "工房の作業音。声はその上に。",
     "<b>佐藤さん</b>「機械はひととおりそろっています。人の手が要るところは、人がやります。"
     "数が少なくても、まとまっても、動かす場所は同じです。」"),
 3: ("棚は<b>奥行きが出る位置</b>から。金型が並ぶ棚 → 型紙を置く手の寄り。",
     "棚の音、金型を抜く音。",
     "<b>佐藤さん</b>「革は、お預かりするものも、こちらで用意するものもあります。金型は品番ごとに置いてあります。"
     "一度作った型は残しますので、二回目からは早いです。」"),
 4: ("裁断機が下りる（横）→ 革包丁の寄り → 裁ち上がったパーツの俯瞰。",
     "プレスの音、包丁の音。",
     "<b>佐藤さん</b>「裁ちは、金型で抜くところと、包丁で切るところがあります。数が出るものは型で、"
     "細かいところや少ない数は手で切ります。同じ日に両方できるのが、うちの形です。」<br>"
     "テロップ＝<b>金型裁断 Die Cutting</b> ／ <b>手裁断 Hand Cutting</b>"),
 5: ("折り目つけ（寄り）→ スプレー（寄り）→ <b>コバ塗りは超マクロ</b> → 職人の目だけの超マクロ。",
     "<b>ここは言葉を減らして作業音を聞かせる。</b>スプレーの音、塗る音。",
     "<b>佐藤さん</b>「折り目をつけて、裏に糊を吹いて、貼り合わせます。断面は塗って止めます。"
     "仕上がりの差が出るのは、ここです。」<br>"
     "テロップ＝<b>折り目つけ Creasing</b> ／ <b>貼り合わせ Bonding</b> ／ <b>コバ塗り Edge Painting</b>"),
 6: ("部品を手に取る（寄り・背景ボケ）→ 針が革に落ちる超マクロ → 両手が生地を送る（引き寄り）。",
     "ミシンの音。声はその上に。",
     "<b>佐藤さん</b>「縫うのは機械です。革の厚みと硬さで送りが変わりますので、そこは人が見ながら送ります。"
     "糸の色も、指定があればそのとおりに出します。」<br>テロップ＝<b>機械縫製 Machine Stitching</b>"),
 7: ("光にかざす → 開いて内側を確かめる（寄り）→ 職人の作業（寄り）。",
     "<b>ここで作業音がいったん消える。</b>",
     "<b>佐藤さん</b>「上がったものは、一点ずつ見ます。表だけでなく、開いて内側と縫い目まで確かめます。"
     "ここで止めれば、お客さまのところで止まることはありません。」<br>テロップ＝<b>検品 Inspection</b>"),
 8: ("包む手元の寄り → 梱包場の引き（奥にも人）→ <b>佐藤さんのバストショットに戻る。</b>",
     "紙の音、テープの音。",
     "<b>佐藤さん</b>「包んで、箱に納めて、そのままお届けします。裁ちから箱詰めまで、外に出さずに、"
     "この建物の中で終わります。作っているのは、ここにいる人間です。」<br>テロップ＝<b>梱包 Packing</b><br>"
     "<span style='color:#a8763e'>言い終えて口を閉じるところまで残す。</span>"),
 9: ("文字だけのカード三枚。黒地 → 黒地 → 白に反転してロゴ。",
     "<b>声は入れない。ロゴでBGMも切る。</b>",
     "<b>つくる、確かめる、包む。</b><br>Make. Check. Pack.<br>"
     "<span style='color:#8a7a63'>対応技法の一覧 → 問い合わせ先 → ロゴ。"
     "展示会用の無音版は、この構成のまま音だけ落とす。</span>"),
},
"07": {
 1: ("<b>正面固定、三脚。ここから最後までこの画角のまま。カメラは一度も動かさない。</b>"
     "手前に入れるものを並べておく。顔は入れない。",
     "入れる音を一つずつ拾う。BGMは薄く。", "出さない。"),
 2: ("同じ画角。A4書類とノートPCが底まで収まるのが見える高さに置く。",
     "PCが底に当たる音。", "出さない。"),
 3: ("同じ画角。小物を一つずつ。<b>それでもまだ閉まる</b>ことが分かるように。",
     "入れる音を一つずつ。", "出さない。"),
 4: ("同じ画角。<b>人も鞄もフレームの外へ出ていく。</b>台は動かさない。",
     "持ち上げる音、足音が遠ざかる。", "出さない。"),
 5: ("<b>何も乗っていない机だけが残る。</b>そのままテロップ → ロゴ。",
     "音が引く。",
     "<b>支度も、仕事も、スマートに。</b><br>SMART FROM MORNING TO WORK.<br>"
     "小さく添える ── A4・13インチPC対応 ／ 返品送料無料<br>"
     "<span style='color:#a8763e'>※タイトルは「朝も仕事も、スマートに。」に変わっています。"
     "テロップも合わせるかどうかは未決です。</span>"),
},
"08": {
 1: ("外観のロー（見上げ）→ 全景の引き → 手元の寄り。<b>ここまで人の顔は出さない。</b>",
     "環境音とBGM。", "ロゴを重ねる。"),
 2: ("商品の寄り → 真俯瞰 → 空間。まだ人は出さない。", "環境音とBGM。", "出さない。"),
 3: ("<b>バストショット。窓を背にして、手前に植物や花を置いてボカす。カメラは一度も動かさない。</b>"
     "そのあとはBロールに変わるが、声は流し続ける。",
     "声。BGMを一段下げる。",
     "<span style='color:#a8763e'>（仮）</span><b>質問</b>「まず、どなたか教えてください。この鞄はいつから使っていますか。」<br>"
     "<b>答え</b>「〇〇です。この鞄を、毎日使っています。買ってから〇年になります。」<br>"
     "<span style='color:#8a7a63'>話した言葉をそのまま画面の下に一行で出す。英訳も一行添える。</span>"),
 4: ("インタビューに戻る（同じ画角）→ 空間の引き → 窓辺の一枚。",
     "声の上にBロール。",
     "<span style='color:#a8763e'>（仮）</span><b>質問</b>「なぜこれを選びましたか。ほかにも見ましたか。」<br>"
     "<b>答え</b>「ほかも見たのですが、これがいちばん〇〇でした。」"),
 5: ("別の場所へ移る（引き）→ 落ち着いた場所 → 外に出て空を入れる。",
     "外の音に変わる。声は続く。",
     "<span style='color:#a8763e'>（仮）</span><b>質問</b>「どんなときに使っていますか。」<br>"
     "<b>答え</b>「〇〇のときです。〇〇が入るので、これ一つで足ります。」"),
 6: ("<b>表情のアップ。</b>そのあと外の引きに人が入る → 静かな一枚。",
     "声だけ。BGMをさらに下げる。",
     "<span style='color:#a8763e'>（仮）</span><b>質問</b>「買う前に迷ったことはありますか。買ってから変わったことは。」<br>"
     "<b>答え</b>「〇〇が心配でした。使ってみたら〇〇でした。」<br>"
     "<span style='color:#8a7a63'>台本にない一言が出たら、そこを使う。</span>"),
 7: ("店の前の引き → 手を振って見送る → <b>同じ引きの画面の中央にロゴが重なる。</b>カメラは動かさない。",
     "外の音。BGMが上がる。",
     "<span style='color:#a8763e'>締めのテロップの文言は、出演者と話す内容が決まってから決めます。</span>"),
 8: ("<b>映像が白に抜けて、ロゴだけが残る。</b>八本のうち、この終わり方はこの一本だけ。",
     "ここで音も切る。", "出さない。"),
},
}


def split_times(tm, n):
    """シーンの秒数をカット数で割って、カットごとの秒を出す"""
    m = re.match(r"(\d+)-(\d+)秒", tm)
    if not m or n <= 0:
        return [""] * n
    a, b = int(m.group(1)), int(m.group(2))
    step = (b - a) / n

    def f(x):
        return str(int(round(x))) if abs(x - round(x)) < 0.05 else f"{x:.1f}"

    return [f"{f(a + step * i)}-{f(a + step * (i + 1))}秒" for i in range(n)]


def scene_rows(pg):
    out = []
    for si, (nm, tm, shots) in enumerate(pg["rows"], 1):
        cuts = [s for s in shots if s[1] != "―"]
        times = split_times(tm, len(cuts))
        cam, snd, tel = D[pg["no"]].get(si, ("", "", ""))
        picture = "".join(
            f'<div style="display: flex; gap: 8px; margin-bottom: 5px">'
            f'<div style="flex: 0 0 62px; font-size: 10px; color: {GOLD}; padding-top: 2px">{esc(times[i])}</div>'
            f'<div style="font-size: 11.5px; line-height: 1.6; color: {INK}">{esc(plain(sh[1]))}</div></div>'
            for i, sh in enumerate(cuts))
        out.append(f'''<tr>
      <td style="padding: 13px 12px 13px 0; border-bottom: 1px solid {LINE}; vertical-align: top">
        <div style="font-size: 12.5px; font-weight: 700; color: {INK}">{esc(nm)}</div>
        <div style="font-size: 10.5px; color: {MUTED}; margin-top: 3px">{esc(re.sub(r"　｜.*", "", tm))}</div>
        <div style="font-size: 10px; color: {FAINT}; margin-top: 3px">{len(cuts)}カット</div>
      </td>
      <td style="padding: 13px 14px; border-bottom: 1px solid {LINE}; vertical-align: top; background: {PAPER}">{picture}</td>
      <td style="padding: 13px 14px; border-bottom: 1px solid {LINE}; vertical-align: top">
        <div style="font-size: 11px; line-height: 1.65; color: {INK}">{cam}</div></td>
      <td style="padding: 13px 14px; border-bottom: 1px solid {LINE}; vertical-align: top">
        <div style="font-size: 11px; line-height: 1.65; color: {INK}">{snd}</div></td>
      <td style="padding: 13px 0 13px 14px; border-bottom: 1px solid {LINE}; vertical-align: top">
        <div style="font-size: 11px; line-height: 1.7; color: {INK}">{tel}</div></td>
    </tr>''')
    return "\n".join(out)


def artboard(pg):
    n = sum(1 for _, _, sh in pg["rows"] for s in sh if s[1] != "―")
    th = ("text-align: left; font-size: 10.5px; font-weight: 400; color: " + FAINT +
          "; letter-spacing: 0.08em; border-bottom: 1px solid " + INK)
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
<div style="width: {PAGE_W}px; height: {HEIGHT[pg["no"]]}px; background: #ffffff; padding: {MARGIN}px; box-sizing: border-box; display: flex; flex-direction: column; gap: 16px">
  <div style="display: flex; flex-direction: column; gap: 9px; border-bottom: 2px solid {INK}; padding-bottom: 13px">
    <div style="display: flex; align-items: baseline; gap: 14px">
      <div style="font-size: 12px; font-weight: 700; color: {GOLD}; letter-spacing: 0.12em">{esc(pg["no"])}</div>
      <div style="font-size: 25px; font-weight: 700; color: {INK}; letter-spacing: -0.01em">{esc(pg["jp"])}</div>
      <div style="font-size: 13px; color: {FAINT}; letter-spacing: 0.06em">{esc(pg["en"])}</div>
      <div style="margin-left: auto; font-size: 11px; color: {GOLD}; border: 1px solid {LINE}; border-radius: 20px; padding: 3px 12px">{"台本（話す言葉あり）" if pg["no"] in TALK else "撮影メモ（セリフなし）"}</div>
    </div>
    <div style="font-size: 11.5px; font-weight: 700; color: {INK}">{esc(plain(pg["meta_len"]))}　／　{esc(plain(pg["meta_target"]))}</div>
    <div style="font-size: 12.5px; line-height: 1.7; color: {INK}; max-width: 1240px">{LEAD[pg["no"]]}</div>
  </div>
  <table>
    <colgroup>
      <col style="width: 128px"><col style="width: 396px"><col style="width: 292px"><col style="width: 186px"><col>
    </colgroup>
    <tr>
      <th style="{th}; padding: 0 12px 7px 0">シ ー ン</th>
      <th style="{th}; padding: 0 14px 7px">画 （ 何 を 撮 る か ）</th>
      <th style="{th}; padding: 0 14px 7px">カ メ ラ</th>
      <th style="{th}; padding: 0 14px 7px">音</th>
      <th style="{th}; padding: 0 0 7px 14px">{"セ リ フ ／ テ ロ ッ プ" if pg["no"] in TALK else "テ ロ ッ プ"}</th>
    </tr>
    {scene_rows(pg)}
  </table>
  <div style="margin-top: auto; display: flex; justify-content: space-between; font-size: 10px; color: {FAINT}">
    <div>BROOKLYN MUSEUM ／ 向島工房　動画制作　／　{"台本" if pg["no"] in TALK else "撮影メモ"}</div>
    <div>{esc(pg["no"])} ／ 全{n}カット</div>
  </div>
</div>
</x-dc>
</body>
</html>
'''


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    data = json.load(open(os.path.join(ROOT, "tools", "deck_data.json"), encoding="utf-8"))
    arts, x, y, col = [], 0, 0, 0
    for pg in data["pages"]:
        f = SLUG[pg["no"]] + ".dc.html"
        with open(os.path.join(outdir, f), "w", encoding="utf-8") as fh:
            fh.write(artboard(pg))
        arts.append({"file": f, "x": x, "y": y, "w": PAGE_W, "h": HEIGHT[pg["no"]]})
        col += 1
        if col % 4 == 0:
            x, y = 0, y + 1700
        else:
            x += PAGE_W + 120
        print(f, PAGE_W, HEIGHT[pg["no"]])
    with open(os.path.join(outdir, "canvas.json"), "w", encoding="utf-8") as fh:
        json.dump({"artboards": arts, "launch": {"view": "canvas"}}, fh, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "script_out"))
