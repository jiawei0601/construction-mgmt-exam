# HANDOFF — 營造工程管理甲級 考古題題庫與測驗系統

## 任務
下載近10年（民國105–114）營造工程管理甲級學科＋術科考古題，建 JSON 題庫，
提供本機 HTML 測驗程式：模擬考抽 60單選+20複選（單選1分/複選2分全對才給、滿分100、
及格60）、單題線性流程答完自動前進、記分數、錯題本、錯題加強模式。

## 現況（2026-08-03）
- 職類確認：營造工程管理 甲級（使用者確認，非建築工程管理），職類代號 **18000**。
- 官方來源：owinform.wdasec.gov.tw（歷屆試題 PastQuestions.aspx + 測試參考資料），
  舊站 techbank.wdasec.gov.tw 已失效勿再用。
- **agent A 下載已完成**（見 `raw/INVENTORY.md` 完整清單）：
  - `raw/subject/`：105–115 年度共 17 份「學科試題暨答案」PDF，全數下載成功並驗證（>10KB 且 `%PDF` 檔頭）。
  - `raw/practical/`：**結構性缺漏，為空**——官網歷屆試題系統未逐梯次公開本職類術科原始試題
    （已逐一查證 17 個梯次的術科欄位皆空、且用同站命名規則反推 URL 一律 404，證據見 `raw/_evidence/`）。
    最接近的替代文件（現行公版＋修訂對照表）已存於 `raw/bank/`。
  - `raw/bank/`：甲級學科題庫 + 甲級術科現行版 + 甲級術科修訂對照表(115/03/24)，共3份。
  - `raw/common/`：90006–90009 共同科目題庫 PDF 各1份（音訊檔未下載，因任務僅要求文件）。
  - 下載用腳本在 `tools/fetch_sessions.py`（列出各梯次 yserno 並掃描營造工程管理列）與
    `tools/download_subject.py`（下載17份學科試題）；抓取證據快照在 `raw/_evidence/`。
  - 技術筆記：官網對 `requests`/`curl` 的 **POST** 會被 F5 WAF 擋下（Request Rejected），
    但**靜態檔案 GET 不受影響**；本次改用真實瀏覽器模擬 ASP.NET `__doPostBack` 逐頁翻頁取得
    各梯次 `yserno`，再用一般 GET 直接下載 PDF。
- 測驗網頁 index.html 已完成（22 項 selftest 全過、headless 實測 UI 流程 OK），
  現裝 12 題假資料待真題庫替換。
- 已確認 `raw/bank/術科現行版.pdf` 只有應檢人須知/工具表/時間配當，**不含題目**。
  術科改走第三方來源（著作權法§9：依法令舉行考試之試題非著作權標的，僅收題目不抄他人解答）。
- **agent C 學科解析完成**：data/questions.js 共 1,512 題（原1,519，主對話移除7題依賴
  內嵌圖形符號的破題：b-03-006~010, s-115-2-004, s-115-2-060）。專業1,112/共同400、
  單選1,311/複選201；16卷通過60+20驗證、appearances命中率80%；詳見 data/PARSE_REPORT.md。
  ⚠️ raw/subject/110_第2梯次_學科試題暨答案.pdf 實為**術科考卷**（官網標錯名），
  已通知術科 agent 轉錄為官方一手來源；110-2 學科卷因此缺（題庫覆蓋足夠，不補）。
  ⚠️ 114 颱風延期考區為獨立考卷，appearances.session 為字串 "2颱風延期考區"。
- 真資料冒煙測試通過（localhost:8642，launch.json 名稱 construction-exam）：
  抽足80題、單選點選自動前進、複選顯示確認作答鈕，console 無錯誤。
- **agent D 術科搜集完成**：105–111 共 7 年完整（109–111 為官方一手 PDF，110 另有
  逐字轉錄 md；105–108 為第三方掃描檔）；112–115 窮盡搜尋確認無流通版本，標缺，
  原因見 raw/practical/SOURCES.md。
  技術要訣：techbank 連結把主機名換成 owinform 即可下載官方檔案（兩站共用後端儲存）。
- **術科詳解 105–111 全部完成**：solutions/{105..111}.md 各 20 大題（每年四份平行卷
  A/B/C/D×5題，每卷配分驗證=100）。計算題均含完整演算（109/111 並經雙法交叉驗算、
  110 關鍵法條經網路查證）。標題格式兩系（105/108–111「第X題（卷別…）」、
  106/107「〔卷別〕第N題」），組頁時照原標題呈現。
- **整合完成**：practical.html（7年×20題=140摺疊區塊）、首頁「術科詳解」卡、README.md；
  __selftest 22/22、console 無錯誤。重建指令 `python tools/build_practical.py`。
- **✅ 2026-08-03 已發佈**：https://github.com/jiawei0601/construction-mgmt-exam
  Pages：https://jiawei0601.github.io/construction-mgmt-exam/（HTTP 200、140 details 驗證通過）
  初版 commit 8bed81a（raw/ 29M 一併入庫）。
- ✅2026-08-03 二版：新增 study.html 備考彙整與出題頻率（140題逐題分類
  docs/practical-classification.csv 為審計依據），commit e71d964。
- ✅2026-08-03 三版（圖片補充，commit 86ee6d8）：學科 7 題圖形題（門窗平面圖符號）
  裁圖復原，題庫回到 1,519 題、schema 新增可選欄位 img；術科 28 卷盤點出 9 題
  原卷附圖（105/110 無附圖）全數裁圖嵌入 practical.html。線上驗證圖片 200。
- ✅2026-08-03 四版（commit 0035ee3）：全面盤查 56 候選題，再補 24 題學科附圖
  （圖說符號/品管公式/測量表格/土方土壓圖/標章圖示），附圖題累計 31、總題數 1519 不變；
  32 題查證為純文字不需圖（清單見 tools/tmp/img_candidates.txt 與 agent 報告）。
- 待辦（未來可選）：112–115 術科若日後市面流通再補；學科題庫官方改版時重抓重建。
- 之後：術科詳解（sonnet 分年擬答、引法規）→ 整合驗收 → haiku 發佈 GitHub Pages。
- 使用者要求：完成後自動發佈 GitHub（jiawei0601 帳號、開 GitHub Pages 給連結，
  比照 tw-stock-db / investment-game 模式）；簡單雜活派 haiku。
- 使用者要求：術科考古題除下載外要整理「詳解」——官方不公布術科答案，
  詳解＝AI 參考擬答（派 sonnet 分年撰寫、引法規出處、頁面標示非官方），
  發佈時加「術科詳解」頁（按年度、可摺疊）。此為本專案最大額度支出段。

## 資料 schema（不可改）
window.EXAM_DATA = { meta, questions:[{id, category(professional|common), subject,
type(single|multi), stem, options{1..4}, answer[], appearances[{year,session,no}]}] }

## 雷區
- file:// 下 fetch 會被擋，資料一律走 <script> 全域變數。
- 術科為申論無標準答案，只收 PDF 原題，不做自動評分。
- 複選題判分＝全對才給分。
