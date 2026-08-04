# -*- coding: utf-8 -*-
"""
由 cm.html 產生 osh.html / safety.html / hygiene.html。
與 cm.html 同源複製，僅替換：<title>／data script src／localStorage 前綴／
匯出檔名前綴／首頁標題比對字串／首頁「術科詳解＋備考重點」兩卡片改為單一
「術科歷屆試題」卡片／插入 EXAM_EXPL 過濾（只留 c- 開頭共同科目解析，避免
與本職類 b-/s- id 命名空間重複造成解析錯掛）。
修 bug 時：若改動的是共用邏輯（非上述差異點），四份檔案（cm.html 本身＋
osh.html/safety.html/hygiene.html）需同步修改，或重跑本腳本重新生成。
用法：python tools/gen_job_pages.py
"""
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "cm.html"

JOBS = [
    {
        "prefix": "osh",
        "job": "職業安全衛生管理",
        "level": "乙級",
        "practical_label": "術科歷屆試題",
        "practical_desc": "105–109年歷屆術科原卷 PDF，依年度／梯次列示（官方原卷；AI 參考詳解候補中）。110年起改採電腦測試，原卷止於109年。",
    },
    {
        "prefix": "safety",
        "job": "職業安全管理",
        "level": "甲級",
        "practical_label": "術科歷屆試題",
        "practical_desc": "105–115年歷屆術科原卷 PDF，依年度／梯次列示（官方原卷；AI 參考詳解候補中）。",
    },
    {
        "prefix": "hygiene",
        "job": "職業衛生管理",
        "level": "甲級",
        "practical_label": "術科歷屆試題",
        "practical_desc": "105–115年歷屆術科原卷 PDF，依年度／梯次列示（官方原卷；AI 參考詳解候補中）。",
    },
]

CM_TITLE = "營造工程管理甲級 學科測驗"

OLD_HOME_CARDS = '''      <div class="card home-card">
        <h2>術科詳解</h2>
        <div class="desc">105–111年歷屆術科試題（每年4卷20大題）AI參考擬答，按年度摺疊瀏覽。</div>
        <a class="btn secondary" href="practical.html" style="display:inline-block;">前往查看</a>
      </div>
      <div class="card home-card">
        <h2>備考重點與出題頻率</h2>
        <div class="desc">105–111年術科140大題逐題分類統計，高頻主題深度整理、計算題公式彙整、準備順序建議。</div>
        <a class="btn secondary" href="study.html" style="display:inline-block;">前往查看</a>
      </div>'''

FILTER_SNIPPET = '''/* 本頁與 cm.html 同源複製，修 bug 需同步四份（cm.html／osh.html／safety.html／hygiene.html），
   或改 cm.html 後重跑 tools/gen_job_pages.py 重新生成。 */
/* 解析共用陷阱防護：data/explanations.js 是營造工程管理甲級 b-/c-/s- 的全量解析，
   本職類題庫的 b-/s- id 命名空間與營造甲級重複但代表不同題目，若直接沿用會把
   營造甲級的專業解析錯掛到本職類的專業題上。因此載入後立刻只保留 c- 開頭
   （共同科目 90006–90009，四職類原樣共用同一批題目與解析）之解析；
   本職類 b-/s- 專業題一律走既有「解析生成中」降級樣式，不會顯示錯誤解析。 */
if(window.EXAM_EXPL){
  const _filteredExpl = {};
  Object.keys(window.EXAM_EXPL).forEach(function(k){ if(k.indexOf('c-') === 0) _filteredExpl[k] = window.EXAM_EXPL[k]; });
  window.EXAM_EXPL = _filteredExpl;
}

'''


def build(job):
    text = SRC.read_text(encoding="utf-8")
    prefix = job["prefix"]
    title = f"{job['job']}{job['level']} 學科測驗"

    # 1. <title>
    text = text.replace(f"<title>{CM_TITLE}</title>", f"<title>{title}</title>")

    # 2. data script src
    text = text.replace(
        '<script src="data/questions.js"></script>',
        f'<script src="data/{prefix}-questions.js"></script>',
    )

    # 3. insert filter snippet right after explanations.js script tag, at top of inline <script>
    marker = '<script src="data/explanations.js"></script>\n<script>\n'
    assert marker in text, "marker not found for inline script insertion"
    text = text.replace(marker, marker + FILTER_SNIPPET, 1)

    # 4. localStorage prefix cmexam_ -> {prefix}exam_
    text = text.replace("cmexam_attempts", f"{prefix}exam_attempts")
    text = text.replace("cmexam_wrongbook", f"{prefix}exam_wrongbook")
    text = text.replace("cmexam_backup_", f"{prefix}exam_backup_")

    # 5. topbar conditional title compare
    text = text.replace(f"title !== '{CM_TITLE}'", f"title !== '{title}'")

    # 6. renderHome() topbar title
    text = text.replace(f"topbar('{CM_TITLE}')", f"topbar('{title}')")

    # 7. home cards: replace 術科詳解＋備考重點 two cards with single 術科歷屆試題 card
    assert OLD_HOME_CARDS in text, "home cards block not found"
    new_card = f'''      <div class="card home-card">
        <h2>{job['practical_label']}</h2>
        <div class="desc">{job['practical_desc']}</div>
        <a class="btn secondary" href="{prefix}-practical.html" style="display:inline-block;">前往查看</a>
      </div>'''
    text = text.replace(OLD_HOME_CARDS, new_card)

    out_path = ROOT / f"{prefix}.html"
    out_path.write_text(text, encoding="utf-8")
    print(f"wrote {out_path} ({len(text)} bytes)")


if __name__ == "__main__":
    for job in JOBS:
        build(job)
