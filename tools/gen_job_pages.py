# -*- coding: utf-8 -*-
"""
由 cm.html 產生 osh.html / safety.html / hygiene.html。
與 cm.html 同源複製，僅替換：<title>／data script src（題庫＋解析兩者皆改
指向本職類專屬檔）／localStorage 前綴／匯出檔名前綴／首頁標題比對字串／
首頁「術科詳解＋備考重點」兩卡片改為單一「術科歷屆試題」卡片。

2026-08-04 起：三職類頁改載入各自 data/{prefix}-explanations.js（由
tools/expl_merge_multi.py 產生，內容＝本職類專業題解析＋原樣併入的400筆
c- 共同科目解析，單檔自足），**不再**沿用 cm.html 那套「載入 explanations.js
後過濾只留 c- 開頭」的邏輯——因為每頁的解析檔本身 id 命名空間已經是本職類
專屬（不含其他職類同名 b-/s- id），不會有錯掛風險。
若 data/{prefix}-explanations.js 尚未產生（haiku 解析管線尚未跑完），
<script> 標籤會 404，但這不會拋例外——window.EXAM_EXPL 就是保持
undefined，走 cm.html 既有的「EXAM_EXPL 缺項/整檔缺失一律優雅降級」路徑
（getExpl() 等函式對 undefined 直接回傳 null，不報錯，見 cm.html 第160行
附近註解與 __selftest 的「EXAM_EXPL整檔缺失時解析函式不報錯」項）。

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

def build(job):
    text = SRC.read_text(encoding="utf-8")
    prefix = job["prefix"]
    title = f"{job['job']}{job['level']} 學科測驗"

    # 1. <title>
    text = text.replace(f"<title>{CM_TITLE}</title>", f"<title>{title}</title>")

    # 2. data script src：題庫與解析兩者皆改指向本職類專屬檔。
    #    data/{prefix}-explanations.js 由 tools/expl_merge_multi.py 產生，尚未產生前
    #    此 <script> 會 404，但不影響頁面——window.EXAM_EXPL 保持 undefined，
    #    走 cm.html 既有的優雅降級路徑（見本檔頭部註解）。
    text = text.replace(
        '<script src="data/questions.js"></script>',
        f'<script src="data/{prefix}-questions.js"></script>',
    )
    assert '<script src="data/explanations.js"></script>' in text, "explanations.js script tag not found"
    text = text.replace(
        '<script src="data/explanations.js"></script>',
        f'<script src="data/{prefix}-explanations.js"></script>',
    )

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
