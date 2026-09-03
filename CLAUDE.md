# BROOKLYN MUSEUM ／ 向島工房　動画制作

## 資料づくりの恒久ルール

**資料に入れてはいけないもの ── 今後どの資料でも、何においても一切入れない。**

1. 動画をカードで並べた一覧・サマリーのページ
2. 「5人で決めたこと」「共通ルール」「議論の結果」の類のページ
3. 「INSTAGRAMに出す順番」のような配信順の説明ブロック

資料に入れてよいのは **表紙／目次／各本の企画書・構成・絵コンテ** だけ。
議論の結果や判断の根拠は、資料ではなく **チャットで伝える。**

## 絵コンテの形式

- A4横・**1本あたり1ページ**
- 左に企画とテロップ、右に **シーン（縦）× ショット（横）の格子**
- シーンごとに複数の画角の参考写真を並べる
- **参考写真は必ず、いただいた参考動画から抽出する**（ストック画像で代用しない）
- 参考動画がない本は、写真枠を空にして画角の指定を文字で書く

## 言葉のルール

- **テロップはすべて日本語と英語を併記する**
- 数字は漢数字（四割・千百六十グラム）
- 使わない言葉：丁寧・こだわり・職人技・本物・想い

## 生成方法

### PDF版

```
python3 tools/data_pdf.py          # pdf/kakutei.html を生成
cd pdf && /opt/pw-browsers/chromium --headless --disable-gpu --no-sandbox \
  --no-pdf-header-footer --print-to-pdf="00_動画8本_企画と絵コンテ.pdf" "file://$PWD/kakutei.html"
```

内容は `tools/data_pdf.py` に、版面は `tools/build_pdf.py` にある。
日本語フォントは IPAGothic ／ IPAPGothic。

### Googleスライドで編集できるpptx版

文言・写真の割り当ては `tools/data_pdf.py` が唯一の情報源。`python3 tools/data_pdf.py` を実行すると
`tools/deck_data.json` も同時に書き出され、これを `tools/build_pptx.js`（pptxgenjs）が読んで
`pdf/00_動画8本_企画と絵コンテ.pptx` を生成する。PDF版と内容は同じで、レイアウトのみワイド16:9で作り直している。

```
python3 tools/data_pdf.py          # deck_data.json を書き出す（PDFも同時に更新される）
node tools/build_pptx.js           # pdf/00_動画8本_企画と絵コンテ.pptx を生成（要 npm install pptxgenjs）
```

`.pptx` はGoogleドライブにアップロードして「Googleスライドで開く」でそのまま編集できる。
左カラム（企画・この1本で言うこと・テロップ・追加ブロック）の文章が長いページは、フッターと重ならないよう
`build_pptx.js` が自動でフォントを縮小してレイアウトを収める。
