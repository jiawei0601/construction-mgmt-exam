# 技術士考古題題庫（一站四職類）

技術士技能檢定考古題整理專案，涵蓋**四個職類**的學科題庫線上模擬測驗，其中營造工程管理甲級並附**術科歷屆試題參考詳解**。純靜態網頁、無需伺服器與資料庫，開啟 `index.html` 即可使用。

線上網址：`https://jiawei0601.github.io/construction-mgmt-exam/`（佔位，尚未發佈）

## 四職類總覽

`index.html` 為統一入口，四張職類卡分別連往各職類的學科測驗頁與術科試題頁：

| 職類 | 級別 | 對應職稱 | 學科測驗頁 | 術科頁 | 題庫題數 |
|---|---|---|---|---|---|
| 營造工程管理 | 甲級 | 工地負責人 | `cm.html` | `practical.html`（AI參考詳解，105–111年）＋`study.html`（備考重點） | 1,519 |
| 職業安全衛生管理 | 乙級 | 職業安全衛生管理員 | `osh.html` | `osh-practical.html`（官方原卷，105–109年） | 1,602 |
| 職業安全管理 | 甲級 | 職業安全管理師 | `safety.html` | `safety-practical.html`（官方原卷，105–115年） | 1,455 |
| 職業衛生管理 | 甲級 | 職業衛生管理師 | `hygiene.html` | `hygiene-practical.html`（官方原卷，105–115年） | 1,849 |

各職類測驗頁功能一致（沿用同一套引擎，`osh.html`／`safety.html`／`hygiene.html` 與 `cm.html` 同源複製，見〈架構與同步規則〉）：

- 模擬考模式：比照正式學科考試抽 60 題單選＋20 題複選（單選 1 分／複選 2 分，全對才給分，滿分 100、60 分及格），單題線性作答、答完自動前進、不可回頭修改。
- 快速測驗：隨機抽 30 題，計分不加權（答對題數 / 總題數）。
- 馬拉松模式：連續抽題不重複、每題即時顯示對錯與解析，隨時可結束結算。
- 錯題加強模式：從錯題本抽題複習，連續答對 2 次自動移出錯題本；可瀏覽錯題本逐題檢視正解與錯因。
- 成績紀錄與科目弱點統計、匯出／匯入作答紀錄（JSON）。
- 各職類作答紀錄與錯題本各自獨立存放於瀏覽器 localStorage（前綴分別為 `cmexam_`／`oshexam_`／`safetyexam_`／`hygieneexam_`），互不影響、互不覆蓋。

## 學科解析（EXAM_EXPL）與共同科目共用

`data/explanations.js` 為**營造工程管理甲級**題庫（`b-`／`c-`／`s-` 三種 id 前綴）的全題解析。四職類的共同科目（90006–90009，`c-` 開頭 400 題）內容與 id 完全相同、四職類原樣共用；但各職類的專業科目雖然 id 命名規則同樣是 `b-`／`s-` 開頭，代表的卻是完全不同的題目——**id 命名空間重複但內容不同**。

因此 `osh.html`／`safety.html`／`hygiene.html` 載入 `explanations.js` 後，會立即在頁面腳本最前面過濾只保留 `c-` 開頭的解析（見各檔案內 `_filteredExpl` 區塊），避免把營造甲級的專業解析錯掛到其他職類的專業題上。過濾後三個職類各自的解析覆蓋率皆為「共同科目 400 題有解析、專業科目顯示既有的『解析生成中』降級樣式」。`cm.html` 本身不受影響，維持完整的 905＋214＋400 題解析。

## 架構與同步規則

- `cm.html`：原 `index.html`，同目錄改名，`data/`／`assets/` 相對引用不變。
- `osh.html`／`safety.html`／`hygiene.html`：由 `tools/gen_job_pages.py` 讀取 `cm.html` 產生，差異僅限於 `<title>`、題庫 `<script src>`、localStorage 前綴、首頁標題比對字串、首頁術科卡片連結、以及上述 EXAM_EXPL 過濾片段。**若要修改測驗引擎共用邏輯（計分／抽題／渲染等），請先改 `cm.html`，再重跑 `python tools/gen_job_pages.py` 重新生成三份職類頁，不要手動分別修改四份檔案**（各檔案頭也附註此規則）。
- `osh-practical.html`／`safety-practical.html`／`hygiene-practical.html`：由 `tools/gen_practical_pages.py` 掃描 `raw-{osh,safety,hygiene}/practical/` 目錄動態產生年度／梯次 PDF 連結頁，官方原卷、尚無 AI 參考詳解。

## 營造工程管理甲級：學科題庫統計

`data/questions.js` 共 **1,519 題**：

| 來源 | 題數 |
|---|---|
| 官方題庫（甲級題庫＋共同科目以外之專業科目） | 905 |
| 共同科目（90006–90009） | 400 |
| 歷屆試卷獨有（題庫查無對應原題，僅見於歷屆考卷） | 214 |
| **合計** | **1,519** |

分類統計：專業科目 1,119 題（905＋214）、共同科目 400 題。

驗證方式：以官方歷屆學科試卷逐題比對 `appearances`（出現年度／梯次／題號），並執行硬規則驗證（每題 4 個選項、`answer` 皆存在於選項 key、複選答案長度 ≥2 等），全數通過、0 項異常。詳細生成紀錄見 `data/PARSE_REPORT.md`（其餘三職類分別見 `data/OSH_PARSE_REPORT.md`／`SAFETY_PARSE_REPORT.md`／`HYGIENE_PARSE_REPORT.md`）。

## 術科範圍

- **營造工程管理甲級**（`practical.html`）：AI 參考詳解涵蓋民國 **105–111 年**（共 7 個年度），每年當日配發 A／B／C／D 四份平行試卷，每卷各自獨立、共 5 大題、每題配分 20 分（單卷合計 100 分），依卷別＋題序將四卷共 20 大題完整收錄於各年度頁面。民國 112–115 年因窮盡搜尋官方系統與第三方管道皆查無公開流通試題原文，故缺，詳見 `raw/practical/SOURCES.md`。
- **職業安全衛生管理乙級**（`osh-practical.html`）：官方原卷 **105–109 年**（共 5 個年度、每年 3 梯次）。**本職類（乙級）自 110 年起術科測試改採電腦化測試，故原卷止於 109 年**，尚無參考擬答。
- **職業安全管理甲級**（`safety-practical.html`）與**職業衛生管理甲級**（`hygiene-practical.html`）：官方原卷 **105–115 年**（共 11 個年度，含 114 年第 2 梯次颱風延期考區試卷），尚無參考擬答。

## 資料來源

- **學科題庫暨歷屆試卷**：勞動部勞動力發展署技能檢定中心官網（`owinform.wdasec.gov.tw`，原 `techbank.wdasec.gov.tw`）。
- **營造工程管理甲級術科歷屆試題**：105–111 年官方系統查詢介面本身未逐梯次公開術科原始試題，改由第三方教學網站（ACI建築營造室內工程管理教學網）取得掃描件，其中 109–111 年並取得官方主機一手 PDF 交叉驗證（110 年並附完整逐字轉錄），詳見 `raw/practical/SOURCES.md`。
- **職業安全衛生管理乙級／職業安全管理甲級／職業衛生管理甲級**之學科題庫、歷屆試卷與術科原卷，來源同上官網。
- 依《著作權法》第 9 條，依法令舉行之各類考試「試題」非著作權標的，本專案僅收錄題目原文；第三方之詳解、解答則有著作權，一律不收錄他人解答內容。

## 免責聲明

- **學科題庫答案**：取自官方公告之學科試題暨答案 PDF，為官方標準答案。
- **營造工程管理甲級術科參考詳解**（`practical.html`）：**為 AI 彙整之參考擬答，非官方標準答案**。官方不公布術科標準答案，本詳解僅供讀者理解考點方向與相關法規依據，法規條號與內容請以最新公告版本為準，正式作答仍應以授課教師意見及最新法規為準。
- **其餘三職類之術科頁**（`osh-practical.html`／`safety-practical.html`／`hygiene-practical.html`）：僅收錄官方原卷 PDF，尚未提供 AI 參考詳解（候補中）。

## 本機使用方式

無需安裝任何套件，直接以瀏覽器開啟 `index.html` 即可（本機檔案系統 `file://` 開啟即可運作；若瀏覽器對本機檔案的 `<script src>` 有限制，也可用任一靜態伺服器開啟，例如 `python -m http.server`）。

## 資料重建方式

`tools/` 目錄下為題庫與各頁面的重建腳本：

- `tools/fetch_sessions.py`：掃描官網各梯次場次序號（`yserno`），列出職類涵蓋之考試梯次。
- `tools/download_subject.py`：下載歷年「學科試題暨答案」PDF。
- `tools/build_practical.py`：讀取 `solutions/105.md`～`111.md`（營造甲級術科參考詳解原始 Markdown），組成靜態頁面 `practical.html`。執行方式：
  ```
  python tools/build_practical.py
  ```
  （需先 `pip install markdown`；產出的 HTML 為 build time 靜態轉換結果，頁面本身不依賴任何 JS 轉換或外部 CDN。）
- `tools/gen_job_pages.py`：由 `cm.html` 產生 `osh.html`／`safety.html`／`hygiene.html`（差異點見〈架構與同步規則〉）。執行方式：
  ```
  python tools/gen_job_pages.py
  ```
- `tools/gen_practical_pages.py`：掃描 `raw-{osh,safety,hygiene}/practical/` 目錄，產生 `osh-practical.html`／`safety-practical.html`／`hygiene-practical.html`。執行方式：
  ```
  python tools/gen_practical_pages.py
  ```

`data/questions.js`／`data/osh-questions.js`／`data/safety-questions.js`／`data/hygiene-questions.js`（各職類學科題庫本體）與 `solutions/*.md`（營造甲級術科詳解原始內容）為既有產出資料，其解析與撰寫紀錄分別見 `data/PARSE_REPORT.md`（及其餘三份 `*_PARSE_REPORT.md`）與 `raw/practical/SOURCES.md`；如需重新解析原始 PDF 或重新撰寫詳解，請參閱上述報告了解既有流程與規則後再行處理，避免覆蓋既有驗證結果。
