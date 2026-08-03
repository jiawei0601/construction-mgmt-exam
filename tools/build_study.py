#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_study.py — 讀取 docs/study-guide.md（營造工程管理甲級 術科 備考內容與出題頻率分析），
組成單一靜態頁面 study.html。

用法：
    python tools/build_study.py

輸出：
    study.html（repo 根目錄）

設計原則：
- md→HTML 轉換在 build time 完成（pip 的 markdown 套件，含 tables 擴充套件），
  頁面本身不跑任何 JS 轉換、不依賴任何外部 CDN。
- 以原始檔案中的 `## ` 標題切分章節，每個章節組成一個 <details> 摺疊區塊
  （第一個章節「出題頻率總表」預設展開，其餘預設收合）。
- 樣式沿用 index.html / practical.html 的 CSS 變數與配色，RWD 適配手機。
"""
import html
import re
from pathlib import Path

import markdown

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_FILE = BASE_DIR / "docs" / "study-guide.md"
OUTPUT_FILE = BASE_DIR / "study.html"

MD_EXTENSIONS = ["tables", "fenced_code", "sane_lists"]

H1_PATTERN = re.compile(r"^# (.+)$", re.MULTILINE)
H2_PATTERN = re.compile(r"^## (.+)$", re.MULTILINE)
H3_PATTERN = re.compile(r"^### (.+)$", re.MULTILINE)


def parse_source():
    """回傳 (標題, intro的markdown, [(章節標題, 章節內容markdown), ...])"""
    text = SOURCE_FILE.read_text(encoding="utf-8")

    h1_match = H1_PATTERN.search(text)
    title = h1_match.group(1).strip() if h1_match else "備考內容與出題頻率分析"

    first_h2 = H2_PATTERN.search(text)
    if first_h2 is None:
        raise ValueError(f"{SOURCE_FILE} 找不到任何 '## ' 章節標題")

    intro_md = text[h1_match.end() if h1_match else 0: first_h2.start()].strip()
    body_text = text[first_h2.start():]

    matches = list(H2_PATTERN.finditer(body_text))
    sections = []
    for i, m in enumerate(matches):
        heading = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body_text)
        content = body_text[start:end].strip()
        content = re.sub(r"\n?-{3,}\s*$", "", content).strip()
        sections.append((heading, content))

    return title, intro_md, sections


def split_by_h3(content):
    """把一個 '## ' 章節內容依 '### ' 子標題切分為 (章節導言markdown, [(子主題標題, 子主題內容markdown), ...])。
    若章節內無 '### ' 子標題，回傳 (整段content, [])。"""
    matches = list(H3_PATTERN.finditer(content))
    if not matches:
        return content, []
    intro = content[:matches[0].start()].strip()
    subs = []
    for i, m in enumerate(matches):
        heading = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        subs.append((heading, content[start:end].strip()))
    return intro, subs


# 只有「高頻主題深度整理」這個章節底下的 '### ' 子標題，才是真正的「各主題」，
# 應各自摺疊；其餘章節（頻率總表、計算題專區、中低頻主題、準備順序）維持固定展開，
# 讓使用者一進頁面就能看到最重要的頻率表與統計數字，不需先展開才看得到。
COLLAPSIBLE_SECTION_KEYWORD = "高頻主題深度整理"


def render_sections(sections):
    """每個 '## ' 章節渲染為固定顯示區塊（h2標題＋內容）；「高頻主題深度整理」章節底下
    每個 '### ' 子標題（各主題）各自組成一個可摺疊的 <details>，其餘章節之 '### ' 維持一般標題。"""
    blocks_html = []
    topic_count = 0
    for heading, content in sections:
        if COLLAPSIBLE_SECTION_KEYWORD in heading:
            intro, subs = split_by_h3(content)
            intro_html = markdown.markdown(intro, extensions=MD_EXTENSIONS) if intro else ""

            subs_html = []
            for heading3, content3 in subs:
                topic_count += 1
                body_html = markdown.markdown(content3, extensions=MD_EXTENSIONS)
                subs_html.append(
                    f'<details class="topic">\n'
                    f'  <summary>{html.escape(heading3)}</summary>\n'
                    f'  <div class="topic-body">{body_html}</div>\n'
                    f'</details>'
                )
        else:
            intro_html = markdown.markdown(content, extensions=MD_EXTENSIONS)
            subs_html = []

        blocks_html.append(
            f'<section class="sitem">\n'
            f'  <h2>{html.escape(heading)}</h2>\n'
            f'  <div class="sbody">{intro_html}{"".join(subs_html)}</div>\n'
            f'</section>'
        )
    return "\n".join(blocks_html), topic_count


def build_page():
    title, intro_md, sections = parse_source()
    intro_html = markdown.markdown(intro_md, extensions=MD_EXTENSIONS) if intro_md else ""
    sections_html, topic_count = render_sections(sections)

    page = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
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
  #app{{max-width:960px; margin:0 auto; padding:16px;}}
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
  .disclaimer p{{margin:0 0 8px;}}
  .disclaimer p:last-child{{margin-bottom:0;}}
  .disclaimer blockquote{{margin:0 0 8px; padding:0; border:none;}}
  .disclaimer blockquote:last-child{{margin-bottom:0;}}
  .sitem{{
    background:var(--card); border:1px solid var(--border); border-radius:10px;
    margin-bottom:16px; overflow:hidden; padding:18px 20px;
  }}
  .sitem > h2{{font-size:19px; color:var(--blue-d); margin:0 0 12px; border-left:4px solid var(--blue); padding-left:10px;}}
  .sbody{{font-size:15px;}}
  .sbody h3{{font-size:15px; color:var(--blue-d); margin:14px 0 8px;}}
  .sbody p{{margin:0 0 10px;}}
  .sbody ul, .sbody ol{{margin:0 0 10px; padding-left:24px;}}
  .sbody li{{margin-bottom:5px;}}
  .sbody table{{width:100%; border-collapse:collapse; font-size:13.5px; margin:10px 0; display:block; overflow-x:auto; white-space:nowrap;}}
  .sbody th, .sbody td{{border:1px solid var(--border); padding:6px 10px; text-align:center;}}
  .sbody th{{background:#f0f0f0; color:var(--blue-d);}}
  .sbody tr:nth-child(even) td{{background:#fafbfc;}}
  .sbody strong{{color:var(--blue-d);}}
  .sbody code{{background:#f0f0f0; padding:1px 5px; border-radius:4px; font-size:13px;}}
  .sbody blockquote{{margin:0 0 10px; padding:6px 12px; border-left:3px solid var(--border); color:#555; background:#f7f8fa; border-radius:0 6px 6px 0;}}
  .topic{{
    border:1px solid var(--border); border-radius:8px; margin-bottom:10px; overflow:hidden;
  }}
  .topic summary{{
    cursor:pointer; padding:10px 14px; background:#eef3fa; font-weight:bold; color:var(--blue-d);
    list-style:none; font-size:15.5px;
  }}
  .topic summary::-webkit-details-marker{{display:none;}}
  .topic summary::before{{content:"▸ "; color:var(--blue);}}
  .topic[open] summary::before{{content:"▾ "; }}
  .topic summary:hover{{background:#e3ecf8;}}
  .topic-body{{padding:14px 16px; font-size:14.5px;}}
  .topic-body h3{{font-size:14.5px; color:var(--blue-d); margin:12px 0 6px;}}
  .topic-body h3:first-child{{margin-top:0;}}
  .topic-body p{{margin:0 0 10px;}}
  .topic-body ul, .topic-body ol{{margin:0 0 10px; padding-left:22px;}}
  .topic-body li{{margin-bottom:5px;}}
  .topic-body table{{width:100%; border-collapse:collapse; font-size:13px; margin:10px 0; display:block; overflow-x:auto; white-space:nowrap;}}
  .topic-body th, .topic-body td{{border:1px solid var(--border); padding:6px 8px; text-align:center;}}
  .topic-body th{{background:#f0f0f0;}}
  .topic-body strong{{color:var(--blue-d);}}
  .topic-body code{{background:#f0f0f0; padding:1px 5px; border-radius:4px; font-size:12.5px;}}
  .small{{font-size:12px; color:var(--grey);}}
  @media (max-width:600px){{
    #app{{padding:10px;}}
    .sitem{{padding:14px;}}
    .sbody{{font-size:14px;}}
    .topic summary{{font-size:14px; padding:10px 12px;}}
    .topic-body{{font-size:13.5px; padding:12px;}}
    .sbody table, .topic-body table{{font-size:12px;}}
  }}
</style>
</head>
<body>
<div id="app">
  <div class="topbar">
    <div class="topbar-title">{html.escape(title)}</div>
    <a class="btn secondary" href="index.html">回學科測驗首頁</a>
  </div>

  <div class="disclaimer">
    {intro_html}
  </div>

  {sections_html}

  <div style="text-align:center; margin:24px 0;">
    <a class="btn secondary" href="practical.html">前往術科詳解</a>
    <a class="btn" href="index.html">回學科測驗首頁</a>
  </div>
</div>
</body>
</html>
"""
    return page, topic_count


def main():
    page, topic_count = build_page()
    OUTPUT_FILE.write_text(page, encoding="utf-8")
    print(f"已產出 {OUTPUT_FILE}")
    print(f"共 {topic_count} 個可摺疊主題")


if __name__ == "__main__":
    main()
