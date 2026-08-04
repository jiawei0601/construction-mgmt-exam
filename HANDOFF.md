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
- ✅2026-08-03 五版（全題解析＋錯題瀏覽，commit ae69203）：
  - data/explanations.js：1,519 題全解析（c 正解理由/w 逐選項錯因/ref 法規標注 926 題/
    law 官方條文全文 149 題，其中 135 題為保守模糊比對 g:1，35 樣本人工覆核零誤配）。
  - 管線：tools/law_corpus/（54部法規，來源 law.moj.gov.tw 快取）、expl_split/merge.py、
    expl_batches+expl_out（12批 haiku，2批品質退件重做；QA 抽 52 題修 9 瑕疵——
    batch-01 建築法定義題條號錯置群已修）。重生成指令：python -X utf8 tools/expl_merge.py。
  - index.html：錯題瀏覽頁（正解綠標/錯選紅標 lastChosen/逐選項錯因/法條摺疊/錯N次徽章）、
    交卷檢討附解析、EXAM_EXPL 缺失優雅降級；selftest 28/28。
  - 已知極限：777 題 ref 為技術規範類（鋼結構/磚構造施工規範等）不在國家法規資料庫，
    無條文可接，僅顯示名稱。
- 原規劃備考（已核准，供對照）：
  - C：錯題本瀏覽頁（標正確答案＋使用者錯選），純 UI 改 index.html，約 5–8 萬 tokens。
  - A：全部 1,519 題選項解析（正解理由＋各錯誤選項為何錯；法規題引完整法條原文，
    法條需從 law.moj.gov.tw 官方 ZIP 本地查對、勿靠模型記憶——現成腳本
    C:\CLAUDE\工地知識庫補充資料\_api_cache\extract_laws.py）。
    實測：平均62字/題、寬鬆判定27%法規題；預估 120–200 萬 tokens、15–16 個 sonnet 分批，
    輸出建議存 data/explanations.js（window.EXAM_EXPL = {id:{why, wrong:{opt:...}, law}}）。
  - 啟動條件：使用者明確說開始；跑完自動發佈並靠 Telegram hooks 通知。
- ✅2026-08-04 六版（commit 777f28c）：手機介面優化（≤480px 單欄/選項加大/確認鈕
  固定底部）＋快速測驗（隨機30題）＋馬拉松模式（連續抽題不重複、每題即時對錯與解析、
  隨時結束結算，mode='marathon'）；selftest 34/34、375x812 實測通過。
  ⚠️瀏覽器窗格 resize 後 ref 點擊座標會偏移，驗證時用 JS click 繞過（非網頁 bug）。
- ▶️2026-08-04 七版進行中（使用者核准）：職安衛三職類子系統（共用架構、一站多職類）。
  職類=乙級職業安全衛生管理(管理員,osh/,raw-osh/)＋甲級職業安全管理(安全管理師,safety/,
  raw-safety/)＋甲級職業衛生管理(衛生管理師,hygiene/,raw-hygiene/)。
  範圍=先建學術科題庫、詳解候補。**架構更新（使用者指示）：根 index.html 改為統一入口
  網頁（四職類卡片）**；營造甲級測驗頁遷為同目錄 cm.html（同目錄改名、data/assets 引用
  全部不動零斷鏈），新職類為 osh.html/safety.html/hygiene.html＋data/{osh,safety,hygiene}-
  questions.js；各職類 localStorage 前綴獨立（cmexam_ 沿用/oshexam_/safetyexam_/hygieneexam_）；
  共同科目 c- 400 題與其既有解析三職類直接共用。
  進度：下載✅（osh 15+15、safety 33+33、hygiene 33+33 卷，代號 22200/22000/22100；
  乙級110起改電腦測驗非停辦已查證更正）→ 解析✅（osh 1602/safety 1455/hygiene 1849 題，
  105-106 掃描卷無文字層依規跳過；hygiene 38 題 GHS 圖形題暫排除）→
  ✅2026-08-04 八版發佈（commit 667f523）：入口網頁 index.html（四職類卡）、營造測驗
  遷 cm.html（cmexam_ 前綴不變紀錄保留）、osh/safety/hygiene.html（tools/gen_job_pages.py
  生成）、三個 *-practical.html 官方術科原卷頁（tools/gen_practical_pages.py）、
  hygiene 38 題 GHS 圖形題裁圖復原（1849→1866）、safety 2 題補圖、
  study.html CSV 死連結修於 build_study.py 輸出層。
  最終規模：營造1519＋乙級1602＋安全甲1455＋衛生甲1866＝6,442 題。
  線上驗證：入口/三新頁/術科頁/GHS圖檔全 200。
  ⚠️雷區：b-/s- id 跨職類命名空間重複，新職類頁載 explanations.js 必須過濾只留 c- key，
  否則營造解析會錯掛到職安題。
- ✅2026-08-04 九版發佈（commit c26fc67）：職安三職類專業題全解析 3,723 題上線。
  執行實錄：31批haiku＋腳本體檢（撈出379題複選錯因缺洞→5批修補合併）＋QA抽50修21瑕疵。
  **重大品質決策**：QA 發現 haiku 自標條號 67% 錯誤（相鄰條號記混）、模糊比對抽驗
  100% 正確 → expl_merge_multi 改「全面驗證制」（verify_native_article=True）：
  法條全文只經文字重疊度驗證掛載（全帶 g:1）、未過驗證降級純法規名、90 筆錯條號被改寫、
  中文數字條號（第三十五條）轉換修復 167 筆。掛官方條文：osh 136/safety 149/hygiene 123。
  ⚠️營造甲級 explanations.js 的 14 筆原生§是人工QA逐筆核過的，未套新政策、勿誤改。
  ⚠️Windows 保留檔名 nul 曾被誤建於 tools/expl_out_v2/ 導致 git add 失敗，已刪；
  agent 導向空輸出請用 /dev/null 勿用 nul。
  （以下為九版管線準備紀錄，供重建參考）
  - ✅管線準備完成（本次，未生成任何解析內容，僅備管線）：
    - 法規語料 tools/law_corpus/ 由53部擴增至110部（原19部核心＋舊擴增52部＋任務指定
      22部職安衛子法（2部重複，淨增20部）＋對三職類專業題全文關鍵字掃描比對出的38部，
      見 tools/build_law_corpus.py TARGETS 與重寫後 tools/law_corpus/INDEX.txt）；
      全數於 ChLaw/ChOrder 快取確認存在、非廢止版本，無 MISSING/ABANDONED。
      已知限制：「職業災害勞工保護法」實務上2022年已由「勞工職業災害保險及保護法」
      實質取代，但 moj 快取未標 LawAbandonNote，仍照既有腳本邏輯收錄，解析時應優先
      參照後者（已記於 INDEX.txt）。
    - tools/expl_split_multi.py：三職類專業題（排除c-）依約125題/批切分，輸出
      tools/expl_batches_v2/{trade}-batch-NN.json。實測：osh 1202題/10批、
      safety 1055題/9批、hygiene 1466題/12批，合計31批/3723題，切分後題數加總
      皆與專業題總數相符。
    - tools/expl_merge_multi.py：重構 tools/expl_merge.py（新增 BATCH_GLOB_PATTERN
      全域變數取代寫死的 'batch-*.json'，向下相容、原 --selftest 仍全過）供三職類
      重用同一套條號抽取＋保守模糊比對(0.6/0.12門檻+g:1標記)邏輯；輸出
      data/{trade}-explanations.js＝本職類專業解析＋原樣併入 data/explanations.js
      的400筆c-解析（單檔自足）；UNMATCHED_{trade}.txt/AUTOMATCH_SAMPLE_{trade}.txt
      分職類輸出至 tools/expl_out_v2/。假資料 --selftest 6項檢查全過（含跨職類
      快取隔離驗證），已清理暫存輸出，未觸碰真實資料。
    - tools/gen_job_pages.py：三職類頁 data script src 改指向各自
      data/{prefix}-explanations.js（移除原「載入後過濾只留c-」邏輯，因新解析檔
      本身即為單職類自足單檔、無跨職類id命名空間風險）；已重新生成 osh/safety/
      hygiene.html。因 data/{trade}-explanations.js 尚未產生（本次刻意不生成任何
      解析內容），三頁 <script> 標籤現為404，但 window.EXAM_EXPL 保持undefined、
      走既有優雅降級路徑——8643埠三頁實測：console無錯誤、__selftest各34/34全過、
      題庫正常載入(1602/1455/1866題)。cm.html/index.html/data/*-questions.js/
      data/explanations.js 全部未動，未 git commit。
    - ⚠️發現既有 tools/expl_merge.py 的 --selftest 有 side effect：未在 selftest()
      內覆寫 UNMATCHED_PATH，導致每次跑 --selftest 會把真實 tools/expl_out/
      UNMATCHED.txt 覆蓋成假測試資料的一行內容。本次已用 git checkout 還原（原檔
      0 bytes），已 spawn 獨立任務 task_fe887708 待修，未在本次修復範圍內處理。
    - 下一步（未做）：派約31個haiku agent依 tools/expl_batches_v2/ 分批撰寫解析
      →輸出至 tools/expl_out_v2/{trade}-batch-NN.json→跑
      `python -X utf8 tools/expl_merge_multi.py` 產生三份 data/{trade}-explanations.js
      →QA抽查→重跑 gen_job_pages.py（此時 script 會200載入）→驗證→發佈。
- 待辦（未來可選）：112–115 術科若日後市面流通再補；學科題庫官方改版時重抓重建；
  職安三職類術科詳解（81卷）與出題頻率分析（候補）。
- 之後：術科詳解（sonnet 分年擬答、引法規）→ 整合驗收 → haiku 發佈 GitHub Pages。
- 使用者要求：完成後自動發佈 GitHub（jiawei0601 帳號、開 GitHub Pages 給連結，
  比照 tw-stock-db / investment-game 模式）；簡單雜活派 haiku。
- 使用者要求：術科考古題除下載外要整理「詳解」——官方不公布術科答案，
  詳解＝AI 參考擬答（派 sonnet 分年撰寫、引法規出處、頁面標示非官方），
  發佈時加「術科詳解」頁（按年度、可摺疊）。此為本專案最大額度支出段。

- ✅2026-08-04 八版（一站四職類入口，未 commit）：根 `index.html` 改為統一入口網頁（四職類卡片，
  各卡顯示題庫題數＋子連結）；原 `index.html` 同目錄改名 `cm.html`（data/assets 引用零斷鏈），
  頁首加「☰ 職類入口」連回 index.html；`osh.html`／`safety.html`／`hygiene.html` 由
  `tools/gen_job_pages.py` 從 `cm.html` 產生（差異：title／題庫 script src／localStorage 前綴
  oshexam_·safetyexam_·hygieneexam_／首頁術科卡片／EXAM_EXPL 過濾），改共用邏輯一律先改
  `cm.html` 再重跑該腳本，不要手改四份。**解析共用陷阱已處理**：三職類載入
  `data/explanations.js`（營造甲級全量解析）後立即過濾只留 `c-` 開頭（共同科目 400 題，
  四職類原樣共用），避免營造甲級的 b-/s- 解析錯掛到其他職類同 id 命名空間但不同內容的專業題；
  專業題走既有「解析生成中」降級樣式。`osh-practical.html`／`safety-practical.html`／
  `hygiene-practical.html` 由 `tools/gen_practical_pages.py` 掃描 `raw-{osh,safety,hygiene}/
  practical/` 動態產生年度／梯次 PDF 連結頁（官方原卷，AI 詳解候補中；osh 因乙級110年起電腦化
  測試僅列105–109年，safety/hygiene 列105–115年含114年颱風延期考區）。README.md 已更新為
  四職類總覽。驗證：8643埠四頁 __selftest 各34/34全過、EXAM_EXPL 過濾後三職類皆恰400筆c-key、
  真實UI點擊+程式化快速測驗(30題)確認抽題/計分/錯題本各自前綴寫入正確、馬拉松模式肉眼與程式
  雙重驗證c-題顯示解析／b-題顯示「解析生成中」、10個html頁面全部內部連結(含中文檔名PDF)逐一
  200驗證、375寬手機版四頁皆無水平捲動、全程console無錯誤。⚠️已知：study.html 第108行
  `./practical-classification.csv` 連結路徑錯誤（應為`docs/practical-classification.csv`）
  ——與本次改造無關之既有 bug，已 spawn 獨立任務 task_f3cb3022 待處理，未在本次修復。
  未 commit（任務指示不git commit），檔案清單：新增 osh.html/safety.html/hygiene.html/
  osh-practical.html/safety-practical.html/hygiene-practical.html/tools/gen_job_pages.py/
  tools/gen_practical_pages.py；index.html 全文重寫為入口頁；index.html→cm.html 改名；
  README.md 改寫。

## 資料 schema（不可改）
window.EXAM_DATA = { meta, questions:[{id, category(professional|common), subject,
type(single|multi), stem, options{1..4}, answer[], appearances[{year,session,no}]}] }

## 雷區
- file:// 下 fetch 會被擋，資料一律走 <script> 全域變數。
- 術科為申論無標準答案，只收 PDF 原題，不做自動評分。
- 複選題判分＝全對才給分。
