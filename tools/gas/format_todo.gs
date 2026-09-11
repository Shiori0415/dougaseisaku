/**
 * TODOシートに書式を当てる（1回だけ実行すればよい）
 *
 * 使い方
 *   1. 対象スプレッドシートを開く
 *   2. 拡張機能 → Apps Script
 *   3. このファイルの中身を全部貼り付けて保存
 *   4. 関数 applyFormat を選んで実行（初回のみGoogleの承認画面が出る）
 *
 * 何度実行しても同じ結果になる（重ねがけしても崩れない）。
 */

var C = {
  TAB_NAME: '動画制作TODO',
  HEADER_BG: '#37474f', HEADER_TX: '#ffffff',
  SECTION_BG: '#e7eaed',
  DONE_BG: '#e6f4ea', DONE_TX: '#146c3a',
  WIP_BG:  '#fef3d8', WIP_TX:  '#9a6407',
  HOLD_BG: '#eceff1', HOLD_TX: '#546e7a',
  HIGH_TX: '#c0392b',
  NEW_BG:  '#fbe3e0', NEW_TX:  '#c0392b',
  MEMO_TX: '#5f6771',
  RULE:    '#c9ced4',
  WIDTHS: [30, 190, 70, 430, 55, 80, 85, 85, 80, 50, 260]  // A〜K
};

function applyFormat() {
  var sh = SpreadsheetApp.getActiveSheet();
  var last = sh.getLastRow();
  var n = C.WIDTHS.length;

  sh.setName(C.TAB_NAME);
  sh.setHiddenGridlines(true);

  // 列幅
  for (var i = 0; i < n; i++) sh.setColumnWidth(i + 1, C.WIDTHS[i]);

  // 全体をいったん素に戻す
  var all = sh.getRange(1, 1, last, n);
  all.setBackground(null)
     .setFontFamily('Arial').setFontSize(10).setFontColor('#1f2328')
     .setFontWeight('normal').setVerticalAlignment('top').setWrap(false)
     .setBorder(true, true, true, true, true, true, C.RULE, SpreadsheetApp.BorderStyle.SOLID);
  sh.getRange(1, 4, last, 1).setWrap(true);   // D タスク名
  sh.getRange(1, 11, last, 1).setWrap(true);  // K 備考

  // ヘッダ行
  sh.getRange(1, 1, 1, n)
    .setBackground(C.HEADER_BG).setFontColor(C.HEADER_TX)
    .setFontWeight('bold').setHorizontalAlignment('center')
    .setVerticalAlignment('middle');
  sh.setRowHeight(1, 30);

  var vals = sh.getRange(1, 1, last, n).getValues();

  for (var r = 2; r <= last; r++) {
    var row = vals[r - 1];
    var isSection = String(row[1] || '').trim() !== '';
    var rng = sh.getRange(r, 1, 1, n);

    if (isSection) {
      rng.setBackground(C.SECTION_BG).setFontWeight('bold').setFontSize(11)
         .setVerticalAlignment('middle');
      sh.setRowHeight(r, 28);
      continue;
    }

    if (!String(row[2] || '').trim()) { sh.setRowHeight(r, 21); continue; }

    sh.setRowHeight(r, 40);
    // 中央寄せにする列（番号・優先度・担当者・開始・終了・ステータス・New）
    [3, 5, 6, 7, 8, 9, 10].forEach(function (c) {
      sh.getRange(r, c).setHorizontalAlignment('center');
    });

    // 優先度
    if (String(row[4]).trim() === '高') {
      sh.getRange(r, 5).setFontColor(C.HIGH_TX).setFontWeight('bold');
    }

    // ステータス
    var st = String(row[8]).trim();
    var cell = sh.getRange(r, 9);
    if (st === '完了')      cell.setBackground(C.DONE_BG).setFontColor(C.DONE_TX).setFontWeight('bold');
    else if (st === '実施中') cell.setBackground(C.WIP_BG).setFontColor(C.WIP_TX).setFontWeight('bold');
    else if (st === '保留')   cell.setBackground(C.HOLD_BG).setFontColor(C.HOLD_TX);

    // New
    if (String(row[9]).trim() === 'New') {
      sh.getRange(r, 10).setBackground(C.NEW_BG).setFontColor(C.NEW_TX)
        .setFontWeight('bold').setFontSize(9);
    }

    // 備考
    sh.getRange(r, 11).setFontColor(C.MEMO_TX).setFontSize(9);
  }

  // 見出し行とA〜C列を固定
  sh.setFrozenRows(1);
  sh.setFrozenColumns(3);

  // フィルタ
  var f = sh.getFilter();
  if (f) f.remove();
  sh.getRange(1, 3, last, n - 2).createFilter();

  applyValidation_(sh, last);
  applyOverdueRule_(sh, last);

  SpreadsheetApp.getActiveSpreadsheet().toast('書式を適用しました', '完了', 5);
}

/** 優先度とステータスをプルダウンにする */
function applyValidation_(sh, last) {
  var pri = SpreadsheetApp.newDataValidation()
    .requireValueInList(['高', '中', '低'], true).setAllowInvalid(false).build();
  var sta = SpreadsheetApp.newDataValidation()
    .requireValueInList(['未着手', '実施中', '完了', '保留'], true).setAllowInvalid(false).build();
  sh.getRange(2, 5, last - 1, 1).setDataValidation(pri);
  sh.getRange(2, 9, last - 1, 1).setDataValidation(sta);
}

/** 終了日を過ぎていて完了していない行は、タスク名を赤字にする */
function applyOverdueRule_(sh, last) {
  var range = sh.getRange(2, 4, last - 1, 1);
  var rule = SpreadsheetApp.newConditionalFormatRule()
    .whenFormulaSatisfied(
      '=IFERROR(AND($I2<>"完了",$I2<>"",$H2<>"",$H2<>"-",DATEVALUE("20"&$H2)<TODAY()),FALSE)')
    .setFontColor(C.HIGH_TX)
    .setBold(true)
    .setRanges([range])
    .build();
  sh.setConditionalFormatRules([rule]);
}
