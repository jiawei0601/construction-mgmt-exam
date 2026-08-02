#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_practical.py — 讀取 solutions/{年}.md（民國105–111年 營造工程管理甲級 術科參考詳解），
組成單一靜態頁面 practical.html。

用法：
    python tools/build_practical.py

輸出：
    practical.html（repo 根目錄）

設計原則：
- md→HTML 轉換在 build time 完成（pip 的 markdown 套件），頁面本身不跑任何 JS 轉換、
  不依賴任何外部 CDN。
- 每個大題（原始檔案中的 `## ` 標題）組成一個 <details> 摺疊區塊，<summary> 直接沿用
  原始標題文字（各年格式不強制統一）。
- 樣式沿用 index.html 的 CSS 變數與配色。
"""
import html
import re
from pathlib import Path

import markdown

BASE_DIR = Path(__file__).resolve().parent.parent
SOLUTIONS_DIR = BASE_DIR / "solutions"
OUTPUT_FILE = BASE_DIR / "practical.html"

YEARS = ["105", "106", "107", "108", "109", "110", "111"]
MISSING_YEARS = ["112", "113", "114", "115"]

MD_EXTENSIONS = ["tables", "fenced_code", "sane_lists"]

H2_PATTERN = re.compile(r"^## (.+)$", re.MULTILINE)


def parse_year_file(year):
    """回傳 (年度標題, intro的markdown, [(大題標題, 大題內容markdown), ...])"""
    path = SOLUTIONS_DIR / f"{year}.md"
    text = path.read_text(encoding="utf-8")

    first_match = H2_PATTERN.search(text)
    if first_match is None:
        raise ValueError(f"{path} 找不到任何 '## ' 大題標題")

    header_block = text[: first_match.start()]
    body_text = text[first_match.start():]

    # 從 header_block 抽出 '# ' 標題，其餘（免責宣告／說明段落）當 intro
    title = None
    intro_lines = []
    for line in header_block.split("\n"):
        if title is None and line.startswith("# "):
            title = line[2:].strip()
            continue
        intro_lines.append(line)
    intro_md = "\n".join(intro_lines).strip()

    # 依 '## ' 標題切每個大題
    matches = list(H2_PATTERN.finditer(body_text))
    questions = []
    for i, m in enumerate(matches):
        heading = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body_text)
        content = body_text[start:end].strip()
        # 移除題目間的水平分隔線 '---'
        content = re.sub(r"\n?-{3,}\s*$", "", content).strip()
        questions.append((heading, content))

    return title or f"民國{year}年", intro_md, questions


def render_year_section(year):
    title, intro_md, questions = parse_year_file(year)
    intro_html = markdown.markdown(intro_md, extensions=MD_EXTENSIONS) if intro_md else ""

    items_html = []
    for heading, content in questions:
        body_html = markdown.markdown(content, extensions=MD_EXTENSIONS)
        items_html.append(
            f'<details class="qitem">\n'
            f'  <summary>{html.escape(heading)}</summary>\n'
            f'  <div class="qbody">{body_html}</div>\n'
            f'</details>'
        )

    section_html = f"""
<section id="y{year}" class="year-section">
  <h2 class="year-title">民國{year}年<span class="small year-count">（共 {len(questions)} 大題）</span></h2>
  <div class="year-intro">{intro_html}</div>
  {''.join(items_html)}
</section>
""".strip()

    return section_html, len(questions)


def build_nav():
    links = "\n".join(
        f'      <a class="btn secondary year-link" href="#y{y}">{y}年</a>' for y in YEARS
    )
    return links


def build_page():
    sections = []
    counts = {}
    for year in YEARS:
        section_html, count = render_year_section(year)
        sections.append(section_html)
        counts[year] = count

    missing_note = "、".join(f"{y}年" for y in MISSING_YEARS)

    page = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>營造工程管理甲級 術科詳解</title>
<style>
  :root{{
    --blue:#1565c0; --blue-d:#0d47a1; --green:#2e7d32; --red:#c62828;
    --grey:#757575; --bg:#f4f5f7; --card:#ffffff; --border:#e0e0e0; --text:#222;
    --orange:#ef6c00;
  }}
  *{{box-sizing:border-box;}}
  body{{
    margin:0; font-family:"Microsoft JhengHei","PingFang TC",-apple-system,BlinkMacSystemFont,sans-serif;
    background:var(--bg); color:var(--text); line-height:1.7;
  }}
  #app{{max-width:900px; margin:0 auto; padding:16px;}}
  h1,h2,h3{{margin:0 0 12px;}}
  .topbar{{
    display:flex; justify-content:space-between; align-items:center;
    background:var(--blue); color:#fff; padding:12px 16px; margin-bottom:16px; border-radius:8px;
    flex-wrap:wrap; gap:8px;
  }}
  .topbar a{{color:#fff; text-decoration:none;}}
  .topbar-title{{font-weight:bold; font-size:18px;}}
  .btn{{
    display:inline-block; cursor:pointer; border:none; border-radius:6px; padding:8px 14px; font-size:14px;
    background:var(--blue); color:#fff; text-decoration:none; transition:opacity .15s;
  }}
  .btn:hover{{opacity:.85;}}
  .btn.secondary{{background:#fff; color:var(--blue); border:1px solid var(--blue);}}
  .card{{
    background:var(--card); border:1px solid var(--border); border-radius:10px;
    padding:18px; margin-bottom:16px; box-shadow:0 1px 3px rgba(0,0,0,.06);
  }}
  .disclaimer{{
    background:#fff8e1; border:1px solid var(--orange); border-radius:10px;
    padding:14px 18px; margin-bottom:16px; color:#5d4300;
  }}
  .disclaimer b{{color:var(--red);}}
  .disclaimer .small{{color:#6d5b28;}}
  .year-nav{{
    display:flex; flex-wrap:wrap; gap:8px; margin-bottom:16px; position:sticky; top:8px;
    background:var(--bg); padding:8px 0; z-index:5;
  }}
  .year-link{{min-width:56px; text-align:center;}}
  .year-section{{
    background:var(--card); border:1px solid var(--border); border-radius:10px;
    padding:18px; margin-bottom:20px; scroll-margin-top:16px;
  }}
  .year-title{{color:var(--blue-d); border-bottom:2px solid var(--blue); padding-bottom:8px;}}
  .year-count{{font-weight:normal; margin-left:8px;}}
  .year-intro{{color:#444; font-size:14px; background:#f0f4f9; border-radius:8px; padding:10px 14px; margin-bottom:14px;}}
  .year-intro blockquote{{margin:0 0 8px; padding:0; border:none;}}
  .year-intro blockquote:last-child{{margin-bottom:0;}}
  .qitem{{
    border:1px solid var(--border); border-radius:8px; margin-bottom:10px; overflow:hidden;
  }}
  .qitem summary{{
    cursor:pointer; padding:10px 14px; background:#eef3fa; font-weight:bold; color:var(--blue-d);
    list-style:none;
  }}
  .qitem summary::-webkit-details-marker{{display:none;}}
  .qitem summary::before{{content:"▸ "; color:var(--blue);}}
  .qitem[open] summary::before{{content:"▾ "; }}
  .qitem summary:hover{{background:#e3ecf8;}}
  .qbody{{padding:14px 16px; font-size:15px;}}
  .qbody h3{{font-size:15px; color:var(--blue-d); margin:14px 0 6px; border-left:4px solid var(--blue); padding-left:8px;}}
  .qbody h3:first-child{{margin-top:0;}}
  .qbody p{{margin:0 0 10px;}}
  .qbody ul, .qbody ol{{margin:0 0 10px; padding-left:24px;}}
  .qbody li{{margin-bottom:4px;}}
  .qbody table{{width:100%; border-collapse:collapse; font-size:14px; margin:10px 0;}}
  .qbody th, .qbody td{{border:1px solid var(--border); padding:6px 8px; text-align:center;}}
  .qbody th{{background:#f0f0f0;}}
  .small{{font-size:12px; color:var(--grey);}}
  @media (max-width:600px){{
    #app{{padding:10px;}}
    .qbody{{font-size:14px; padding:12px;}}
  }}
</style>
</head>
<body>
<div id="app">
  <div class="topbar">
    <div class="topbar-title">營造工程管理甲級 術科參考詳解</div>
    <a class="btn secondary" href="index.html">回學科測驗首頁</a>
  </div>

  <div class="disclaimer">
    <b>⚠️ 本詳解為 AI 彙整之參考擬答，非官方標準答案</b>，法規內容以最新公告版本為準，
    引用條號請自行核對現行法規；作答時請以官方公告及授課教師意見為準。
    <div class="small" style="margin-top:6px;">
      民國{missing_note}術科試題官方未公開、市面亦無流通版本可考據，故本頁僅收錄 105–111 年（共 7 年）。
    </div>
  </div>

  <div class="card">
    <div class="year-nav">
{build_nav()}
    </div>
    <div class="small">共 {len(YEARS)} 個年度、每年 4 卷（A／B／C／D）合計 20 大題，點擊大題標題可展開／收合完整內容（題目／參考擬答／法規與依據／考點提示）。</div>
  </div>

  {''.join(sections)}

  <div style="text-align:center; margin:24px 0;">
    <a class="btn" href="index.html">回學科測驗首頁</a>
  </div>
</div>
</body>
</html>
"""
    return page, counts


def main():
    page, counts = build_page()
    OUTPUT_FILE.write_text(page, encoding="utf-8")
    total = sum(counts.values())
    print(f"已產出 {OUTPUT_FILE}")
    for year in YEARS:
        print(f"  {year}年：{counts[year]} 大題")
    print(f"合計：{total} 大題")


if __name__ == "__main__":
    main()
