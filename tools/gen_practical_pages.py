# -*- coding: utf-8 -*-
"""
產生 osh-practical.html / safety-practical.html / hygiene-practical.html：
按年度／梯次列出 raw-{prefix}/practical/ 下的官方術科原卷 PDF 連結，並在
solutions-{prefix}/{卷名}.md 存在時，把 AI 參考詳解轉成 HTML 嵌入（每個大題一個
<details> 摺疊區塊）。詳解尚未產出的卷只顯示 PDF 連結＋「詳解生成中」小字，不報錯。

md→HTML 轉換在 build time 完成（pip 的 markdown 套件），頁面本身不跑任何 JS 轉換、
不依賴任何外部 CDN。可重複執行：詳解陸續補齊後，重跑本腳本即可更新頁面。

用法：python tools/gen_practical_pages.py
"""
import html
import re
import pathlib

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent

JOBS = [
    {
        "prefix": "osh",
        "job": "職業安全衛生管理",
        "level": "乙級",
        "raw_dir": "raw-osh/practical",
        "solutions_dir": "solutions-osh",
        "extra_note": "本職類（乙級）自110年起術科測試改採電腦化測試，故本頁原卷僅收錄至109年止。",
    },
    {
        "prefix": "safety",
        "job": "職業安全管理",
        "level": "甲級",
        "raw_dir": "raw-safety/practical",
        "solutions_dir": "solutions-safety",
        "extra_note": "",
    },
    {
        "prefix": "hygiene",
        "job": "職業衛生管理",
        "level": "甲級",
        "raw_dir": "raw-hygiene/practical",
        "solutions_dir": "solutions-hygiene",
        "extra_note": "",
    },
]

FNAME_RE = re.compile(r"^(\d{3})_(第(\d)梯次(?:_(颱風延期考區))?)_術科試題\.pdf$")
MD_EXTENSIONS = ["tables", "fenced_code", "sane_lists"]
H2_PATTERN = re.compile(r"^## (.+)$", re.MULTILINE)

STYLE = """
  :root{
    --blue:#1565c0; --blue-d:#0d47a1; --green:#2e7d32; --red:#c62828;
    --grey:#757575; --bg:#f4f5f7; --card:#ffffff;
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
  .disclaimer b{color:var(--red);}
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
  .session-card{
    border:1px solid var(--border); border-radius:8px; padding:12px 14px; margin-top:14px;
    background:#fafbfc;
  }
  .session-header{
    display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px;
    margin-bottom:8px;
  }
  .session-title{font-weight:bold; color:var(--blue-d); font-size:15px;}
  .session-pdf-link{
    display:inline-block; padding:6px 12px; border:1px solid var(--border); border-radius:8px;
    color:var(--blue-d); text-decoration:none; background:#f7f9fc; font-size:13px;
  }
  .session-pdf-link:hover{background:#eef3fa; border-color:var(--blue);}
  .pending{font-style:italic; color:var(--grey); font-size:13px; padding:4px 0;}
  .qitem{
    border:1px solid var(--border); border-radius:8px; margin-top:8px; overflow:hidden; background:#fff;
  }
  .qitem summary{
    cursor:pointer; padding:9px 12px; background:#eef3fa; font-weight:bold; color:var(--blue-d);
    list-style:none; font-size:14px;
  }
  .qitem summary::-webkit-details-marker{display:none;}
  .qitem summary::before{content:"▸ "; color:var(--blue);}
  .qitem[open] summary::before{content:"▾ "; }
  .qitem summary:hover{background:#e3ecf8;}
  .qbody{padding:12px 14px; font-size:14px;}
  .qbody h3{font-size:14px; color:var(--blue-d); margin:12px 0 6px; border-left:4px solid var(--blue); padding-left:8px;}
  .qbody h3:first-child{margin-top:0;}
  .qbody p{margin:0 0 10px;}
  .qbody ul, .qbody ol{margin:0 0 10px; padding-left:24px;}
  .qbody li{margin-bottom:4px;}
  .qbody table{width:100%; border-collapse:collapse; font-size:13px; margin:10px 0;}
  .qbody th, .qbody td{border:1px solid var(--border); padding:6px 8px; text-align:center;}
  .qbody th{background:#f0f0f0;}
  .qbody strong{color:var(--blue-d);}
  .small{font-size:12px; color:var(--grey);}
  @media (max-width:600px){
    #app{padding:10px;}
    .card{padding:14px;}
    .session-card{padding:10px;}
    .qbody{font-size:13.5px; padding:10px;}
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


def parse_solution_md(path: pathlib.Path):
    """回傳 (intro的markdown, [(大題標題, 大題內容markdown), ...])"""
    text = path.read_text(encoding="utf-8")

    first_match = H2_PATTERN.search(text)
    if first_match is None:
        return "", []

    header_block = text[: first_match.start()]
    body_text = text[first_match.start():]

    intro_lines = []
    for line in header_block.split("\n"):
        if line.startswith("# "):
            continue
        intro_lines.append(line)
    intro_md = "\n".join(intro_lines).strip()

    matches = list(H2_PATTERN.finditer(body_text))
    questions = []
    for i, m in enumerate(matches):
        heading = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body_text)
        content = body_text[start:end].strip()
        content = re.sub(r"\n?-{3,}\s*$", "", content).strip()
        questions.append((heading, content))

    return intro_md, questions


def session_title_for(year: str, label: str):
    m = re.match(r"第(\d)梯次(?:_(颱風延期考區))?", label)
    n, typhoon = m.group(1), m.group(2)
    title = f"民國{year}年第{n}梯次"
    if typhoon:
        title += "（颱風延期考區）"
    return title


def render_session(job, year, label, fname):
    raw_dir_rel = job["raw_dir"]
    solutions_dir = ROOT / job["solutions_dir"]
    stem = fname[: -len(".pdf")]
    md_path = solutions_dir / f"{stem}.md"

    title = session_title_for(year, label)
    pdf_link = f'<a class="session-pdf-link" href="{raw_dir_rel}/{fname}" target="_blank" rel="noopener">📄 官方原卷 PDF</a>'

    if not md_path.exists():
        body_html = '<div class="pending">詳解生成中，請先參考官方原卷 PDF。</div>'
        count = 0
    else:
        intro_md, questions = parse_solution_md(md_path)
        intro_html = markdown.markdown(intro_md, extensions=MD_EXTENSIONS) if intro_md else ""
        items_html = []
        for heading, content in questions:
            content_html = markdown.markdown(content, extensions=MD_EXTENSIONS)
            items_html.append(
                f'<details class="qitem">\n'
                f'  <summary>{html.escape(heading)}</summary>\n'
                f'  <div class="qbody">{content_html}</div>\n'
                f'</details>'
            )
        body_html = intro_html + "".join(items_html)
        count = len(questions)

    session_html = f'''    <div class="session-card">
      <div class="session-header">
        <div class="session-title">{title}</div>
        {pdf_link}
      </div>
      {body_html}
    </div>'''
    return session_html, count


def build(job):
    prefix = job["prefix"]
    raw_dir = ROOT / job["raw_dir"]
    years = collect_years(raw_dir)
    year_keys = sorted(years.keys())

    nav_html = "\n      ".join(
        f'<a class="btn secondary year-link" href="#y{y}">{y}年</a>' for y in year_keys
    )

    sections = []
    total_count = 0
    for y in year_keys:
        items = years[y]
        session_blocks = []
        for label, fname in items:
            block_html, count = render_session(job, y, label, fname)
            session_blocks.append(block_html)
            total_count += count
        sections.append(f'''  <section id="y{y}" class="year-section">
    <h2 class="year-title">民國{y}年<span class="year-count">（共 {len(items)} 份）</span></h2>
{chr(10).join(session_blocks)}
  </section>''')
    sections_html = "\n\n".join(sections)

    extra_note_html = f'\n    <div class="small">{job["extra_note"]}</div>' if job["extra_note"] else ""

    title = f'{job["job"]}{job["level"]} 術科試題與詳解'

    html_out = f'''<!DOCTYPE html>
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
    <b>⚠️ 本詳解為 AI 彙整之參考擬答，非官方標準答案</b>，法規內容以最新公告版本為準，
    引用條號請自行核對現行法規；作答時請以官方公告及授課教師意見為準。
    <div class="small">部分梯次之詳解仍陸續生成中，尚未產出者僅提供官方原卷 PDF 連結。</div>{extra_note_html}
  </div>

  <div class="card">
    <div class="year-nav">
      {nav_html}
    </div>
    <div class="small">共 {len(year_keys)} 個年度，依年度／梯次列出官方術科試題 PDF 與 AI 參考詳解（如已產出），點擊大題標題可展開／收合。</div>
  </div>

{sections_html}

  <div style="text-align:center; margin:24px 0;">
    <a class="btn" href="index.html">回職類入口</a>
  </div>
</div>
</body>
</html>
'''
    out_path = ROOT / f"{prefix}-practical.html"
    out_path.write_text(html_out, encoding="utf-8")
    print(f"wrote {out_path} ({len(html_out)} bytes, {len(year_keys)} years, {total_count} 大題 details)")


if __name__ == "__main__":
    for job in JOBS:
        build(job)
