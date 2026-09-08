/**
 * 議事録ドキュメント → スプレッドシート「個人todo」自動転記
 *
 * Geminiが生成する会議メモの「次のステップ」から [担当者名] で始まる行を拾い、
 * 対象シートの「個人todo」ブロックに追記する。
 *
 * 設置方法:
 *   1. 対象スプレッドシートを開く
 *   2. 拡張機能 → Apps Script
 *   3. このファイルの中身を全部貼り付けて保存
 *   4. 関数 setupTrigger を一度だけ実行（権限の承認を求められる）
 *   5. 以後は毎朝8時に自動実行。手動実行はシート上部のメニュー「TODO同期」から
 */

// ============ 設定 ============
var CONFIG = {
  // 転記先シートのgid（URLの #gid= の数字）
  SHEET_GID: 627178532,

  // 拾う担当者名（ドキュメント上の表記と完全一致させる）
  OWNER_NAME: '宮下詩織',

  // 「個人todo」ブロックを探すときの見出し文字列（B列）
  SECTION_LABEL: '個人todo',

  // 何日前までの議事録を対象にするか
  LOOKBACK_DAYS: 14,

  // 議事録ドキュメントを絞り込む本文キーワード
  DOC_KEYWORD: '次のステップ',

  // 列の位置（1=A, 2=B, ...）。シートの構成を変えたらここを直す
  COL: {
    SECTION: 2,   // B: セクション見出し
    MARK:    3,   // C: 行頭記号
    TASK:    4,   // D: タスク名
    PRIORITY:5,   // E: 優先度
    START:   6,   // F: 開始
    END:     7,   // G: 終了
    STATUS:  8    // H: ステータス
  },

  // 新規行の既定値。日付を勝手に作らないため終了日は空のまま
  DEFAULT_PRIORITY: '中',
  DEFAULT_STATUS: '未着手',
  FILL_START_DATE: true
};
// ==============================


/** シートを開いたときにメニューを出す */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('TODO同期')
    .addItem('議事録から取り込む', 'syncTodos')
    .addItem('取り込み履歴をリセット', 'resetHistory')
    .addToUi();
}


/** 毎朝8時の自動実行を登録する（一度だけ実行すればよい） */
function setupTrigger() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'syncTodos') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('syncTodos').timeBased().atHour(8).everyDays(1).create();
  Logger.log('毎日8時の自動実行を登録しました');
}


/** 本体 */
function syncTodos() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = getSheetByGid(ss, CONFIG.SHEET_GID);
  if (!sheet) throw new Error('gid=' + CONFIG.SHEET_GID + ' のシートが見つかりません');

  var docs = findRecentMeetingDocs_();
  var seen = loadHistory_();
  var existing = loadExistingTasks_(sheet);

  var added = [];

  docs.forEach(function (file) {
    var docId = file.getId();
    if (seen[docId]) return;                       // 取り込み済みは飛ばす

    var text = readDocText_(docId);
    var tasks = extractTasks_(text, CONFIG.OWNER_NAME);

    tasks.forEach(function (task) {
      var key = normalize_(task);
      if (existing[key]) return;                   // 既にシートにあるものは飛ばす
      existing[key] = true;
      added.push({ task: task, docName: file.getName(), docUrl: file.getUrl() });
    });

    seen[docId] = true;
  });

  if (added.length === 0) {
    Logger.log('新しいTODOはありませんでした');
    saveHistory_(seen);
    return;
  }

  writeTasks_(sheet, added);
  saveHistory_(seen);
  Logger.log(added.length + '件を追記しました');
}


/** 取り込み履歴を消して、次回に全部読み直させる */
function resetHistory() {
  PropertiesService.getDocumentProperties().deleteProperty('processedDocs');
  Logger.log('履歴をリセットしました');
}


// ---------- 以下、内部処理 ----------

function getSheetByGid(ss, gid) {
  var sheets = ss.getSheets();
  for (var i = 0; i < sheets.length; i++) {
    if (sheets[i].getSheetId() === gid) return sheets[i];
  }
  return null;
}


/** 直近の議事録ドキュメントをDriveから探す */
function findRecentMeetingDocs_() {
  var since = new Date();
  since.setDate(since.getDate() - CONFIG.LOOKBACK_DAYS);
  var iso = Utilities.formatDate(since, 'UTC', "yyyy-MM-dd'T'HH:mm:ss'Z'");

  var query = 'mimeType = "application/vnd.google-apps.document"'
            + ' and modifiedDate > "' + iso + '"'
            + ' and fullText contains "' + CONFIG.DOC_KEYWORD + '"'
            + ' and trashed = false';

  var it = DriveApp.searchFiles(query);
  var out = [];
  while (it.hasNext() && out.length < 50) out.push(it.next());
  return out;
}


/** ドキュメント本文を取り出す（タブ対応） */
function readDocText_(docId) {
  var doc = DocumentApp.openById(docId);
  var text = '';

  if (typeof doc.getTabs === 'function') {
    var walk = function (tabs) {
      tabs.forEach(function (tab) {
        try { text += tab.asDocumentTab().getBody().getText() + '\n'; } catch (e) {}
        walk(tab.getChildTabs());
      });
    };
    walk(doc.getTabs());
  }

  if (!text) text = doc.getBody().getText();
  return text;
}


/** [担当者名] で始まる行からタスクを抜き出す */
function extractTasks_(text, owner) {
  var re = new RegExp('\\[\\s*' + owner + '\\s*\\]\\s*(.+)', 'g');
  var out = [];
  var m;
  while ((m = re.exec(text)) !== null) {
    var task = m[1].replace(/\s+/g, ' ').trim();
    if (task) out.push(task);
  }
  return out;
}


/** シートに既にあるタスク名を集める */
function loadExistingTasks_(sheet) {
  var last = sheet.getLastRow();
  if (last < 1) return {};
  var values = sheet.getRange(1, CONFIG.COL.TASK, last, 1).getValues();
  var map = {};
  values.forEach(function (row) {
    var v = String(row[0] || '').trim();
    if (v) map[normalize_(v)] = true;
  });
  return map;
}


/** 「個人todo」ブロックの範囲を返す */
function findSectionRange_(sheet) {
  var last = sheet.getLastRow();
  var col = sheet.getRange(1, CONFIG.COL.SECTION, last, 1).getValues();

  var start = -1;
  for (var i = 0; i < col.length; i++) {
    if (String(col[i][0] || '').trim() === CONFIG.SECTION_LABEL) { start = i + 2; break; }
  }
  if (start === -1) throw new Error('「' + CONFIG.SECTION_LABEL + '」の見出しが B列に見つかりません');

  var end = last;
  for (var j = start - 1; j < col.length; j++) {
    if (String(col[j][0] || '').trim() !== '') { end = j; break; }
  }
  return { start: start, end: end };
}


/** タスクを書き込む。空行があればそこへ、無ければ行を挿入する */
function writeTasks_(sheet, items) {
  var range = findSectionRange_(sheet);
  var today = CONFIG.FILL_START_DATE
    ? Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yy/M/d')
    : '';

  var cursor = range.start;

  items.forEach(function (item) {
    var row = -1;

    // ブロック内の空行を探す
    for (var r = cursor; r <= range.end; r++) {
      if (String(sheet.getRange(r, CONFIG.COL.TASK).getValue() || '').trim() === '') { row = r; break; }
    }

    // 空行が無ければブロック末尾に1行挿入
    if (row === -1) {
      sheet.insertRowAfter(range.end);
      row = range.end + 1;
      range.end = row;
    }

    sheet.getRange(row, CONFIG.COL.MARK).setValue('・');
    sheet.getRange(row, CONFIG.COL.TASK).setValue(item.task);
    if (!sheet.getRange(row, CONFIG.COL.PRIORITY).getValue()) {
      sheet.getRange(row, CONFIG.COL.PRIORITY).setValue(CONFIG.DEFAULT_PRIORITY);
    }
    if (today && !sheet.getRange(row, CONFIG.COL.START).getValue()) {
      sheet.getRange(row, CONFIG.COL.START).setValue(today);
    }
    sheet.getRange(row, CONFIG.COL.STATUS).setValue(CONFIG.DEFAULT_STATUS);

    // 出典をセルのメモに残す
    sheet.getRange(row, CONFIG.COL.TASK)
      .setNote('出典: ' + item.docName + '\n' + item.docUrl
             + '\n取込日: ' + Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy/MM/dd HH:mm'));

    cursor = row + 1;
  });
}


function normalize_(s) {
  return String(s).replace(/[\s　]/g, '').replace(/[（）()]/g, '').toLowerCase();
}

function loadHistory_() {
  var raw = PropertiesService.getDocumentProperties().getProperty('processedDocs');
  return raw ? JSON.parse(raw) : {};
}

function saveHistory_(obj) {
  PropertiesService.getDocumentProperties().setProperty('processedDocs', JSON.stringify(obj));
}
