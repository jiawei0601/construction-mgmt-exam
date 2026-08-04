# -*- coding: utf-8 -*-
"""
產生 osh-practical.html / safety-practical.html / hygiene-practical.html：
按年度／梯次列出 raw-{prefix}/practical/ 下的官方術科原卷 PDF 連結（相對路徑）。
與 cm.html 的 practical.html（AI 參考詳解、逐題摺疊）不同——這三頁只收錄官方原卷，
無詳解內容，頁首註明「官方原卷；AI 參考詳解候補中」。
用法：python tools/gen_practical_pages.py
"""
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

JOBS = [
    {
        "prefix": "osh",
        "job": "職業安全衛生管理",
        "level": "乙級",
        "raw_dir": "raw-osh/practical",
        "extra_note": "本職類（乙級）自110年起術科測試改採電腦化測試，故本頁原卷僅收錄至109年止。",
    },
    {
        "prefix": "safety",
        "job": "職業安全管理",
        "level": "甲級",
        "raw_dir": "raw-safety/practical",
        "extra_note": "",
    },
    {
        "prefix": "hygiene",
        "job": "職業衛生管理",
        "level": "甲級",
        "raw_dir": "raw-hygiene/practical",
        "extra_note": "",
    },
]

FNAME_RE = re.compile(r"^(\d{3})_(第\d梯次(?:_颱風延期考區)?)_術科試題\.pdf$")

STYLE = """
  :root{
    --blue:#1565c0; --blue-d:#0d47a1; --grey:#757575; --bg:#f4f5f7; --card:#ffffff;
    --border:#e0e0e0; --text:#222; --orange:#ef6c00;
  }
  *{box-sizing:border-box;}
  body{
    margin:0; font-family:"Microsoft JhengHei","PingFang TC",-apple-system,BlinkMacSystemFont,sans-serif;
    background:var(--bg); color:var(--text); line-height:1.7;
  }
  #app{max-width:900px; margin:0 auto; padding:16px;}
  h1,h2,h3{margin:0 0 12px;}
  .topbar{
    display:flex; justify-content:space-between; align-items:center;
    background:var(--blue); color:#fff; padding:12px 16px; margin-bottom:16px; border-radius:8px;
    flex-wrap:wrap; gap:8px;
  }
  .topbar a{color:#fff; text-decoration:none;}
  .topbar-title{font-weight:bold; font-size:18px;}
  .topbar-actions{display:flex; gap:8px; flex-wrap:wrap;}
  .btn{
    display:inline-block; cursor:pointer; border:none; border-radius:6px; padding:8px 14px; font-size:14px;
    background:var(--blue); color:#fff; text-decoration:none; transition:opacity .15s;
  }
  .btn:hover{opacity:.85;}
  .btn.secondary{background:#fff; color:var(--blue); border:1px solid var(--blue);}
  .card{
    background:var(--card); border:1px solid var(--border); border-radius:10px;
    padding:18px; margin-bottom:16px; box-shadow:0 1px 3px rgba(0,0,0,.06);
  }
  .disclaimer{
    background:#fff8e1; border:1px solid var(--orange); border-radius:10px;
    padding:14px 18px; margin-bottom:16px; color:#5d4300;
  }
  .disclaimer b{color:var(--red, #c62828);}
  .disclaimer .small{color:#6d5b28; margin-top:6px;}
  .year-nav{
    display:flex; flex-wrap:wrap; gap:8px; margin-bottom:16px; position:sticky; top:8px;
    background:var(--bg); padding:8px 0; z-index:5;
  }
  .year-link{min-width:56px; text-align:center;}
  .year-section{
    background:var(--card); border:1px solid var(--border); border-radius:10px;
    padding:18px; margin-bottom:20px; scroll-margin-top:16px;
  }
  .year-title{color:var(--blue-d); border-bottom:2px solid var(--blue); padding-bottom:8px;}
  .year-count{font-weight:normal; margin-left:8px; font-size:13px; color:var(--grey);}
  .pdf-list{list-style:none; margin:0; padding:0; display:flex; flex-wrap:wrap; gap:10px;}
  .pdf-list li{flex:0 0 auto;}
  .pdf-list a{
    display:inline-block; padding:8px 14px; border:1px solid var(--border); border-radius:8px;
    color:var(--blue-d); text-decoration:none; background:#f7f9fc;
  }
  .pdf-list a:hover{background:#eef3fa; border-color:var(--blue);}
  .small{font-size:12px; color:var(--grey);}
  @media (max-width:600px){
    #app{padding:10px;}
    .card{padding:14px;}
  }
"""


def collect_years(raw_dir: pathlib.Path):
    years = {}
    for f in sorted(raw_dir.iterdir()):
        m = FNAME_RE.match(f.name)
        if not m:
            raise ValueError(f"未預期的檔名格式: {f.name}")
        year, label = m.group(1), m.group(2)
        years.setdefault(year, []).append((label, f.name))
    return years


def build(job):
    prefix = job["prefix"]
    raw_dir = ROOT / job["raw_dir"]
    years = collect_years(raw_dir)
    year_keys = sorted(years.keys())

    nav_html = "\n      ".join(
        f'<a class="btn secondary year-link" href="#y{y}">{y}年</a>' for y in year_keys
    )

    sections = []
    for y in year_keys:
        items = years[y]
        items_html = "\n      ".join(
            f'<li><a href="{job["raw_dir"]}/{fname}" target="_blank" rel="noopener">{label}</a></li>'
            for label, fname in items
        )
        sections.append(f'''  <section id="y{y}" class="year-section">
    <h2 class="year-title">民國{y}年<span class="year-count">（共 {len(items)} 份）</span></h2>
    <ul class="pdf-list">
      {items_html}
    </ul>
  </section>''')
    sections_html = "\n\n".join(sections)

    extra_note_html = f'\n    <div class="small">{job["extra_note"]}</div>' if job["extra_note"] else ""

    title = f'{job["job"]}{job["level"]} 術科歷屆試題'

    html = f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>{STYLE}</style>
</head>
<body>
<div id="app">
  <div class="topbar">
    <div class="topbar-title">{title}</div>
    <div class="topbar-actions">
      <a class="btn secondary" href="index.html">☰ 職類入口</a>
      <a class="btn secondary" href="{prefix}.html">回{job["job"]}測驗</a>
    </div>
  </div>

  <div class="disclaimer">
    <b>⚠️ 官方原卷；AI 參考詳解候補中</b>
    <div class="small">本頁僅收錄官方公告之歷屆術科試題 PDF 原文，尚未提供參考擬答；如需練習方向，請先參考學科題庫測驗。</div>{extra_note_html}
  </div>

  <div class="card">
    <div class="year-nav">
      {nav_html}
    </div>
    <div class="small">共 {len(year_keys)} 個年度，依年度／梯次列出官方術科試題 PDF，點擊於新分頁開啟。</div>
  </div>

{sections_html}
</div>
</body>
</html>
'''
    out_path = ROOT / f"{prefix}-practical.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"wrote {out_path} ({len(html)} bytes, {len(year_keys)} years)")


if __name__ == "__main__":
    for job in JOBS:
        build(job)
