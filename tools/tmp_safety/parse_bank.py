import sys, json, re
sys.path.insert(0, "tools/tmp")
from lib import extract_pages, parse_question_block, FOOTER_RE

path = r"raw-safety/bank/22000_職業安全管理_甲級_學科題庫.pdf"
pages_text = extract_pages(path)

HEADER_RE = re.compile(r"22000\s*職業安全管理\s*甲級\s*工作項目\s*(\d+)\s*[:：]\s*(.+)")

chapters = []
cur = None
for pi, text in enumerate(pages_text):
    if pi == 0:
        continue
    lines = text.split("\n")
    for line in lines:
        m = HEADER_RE.search(line)
        if m:
            if cur is not None:
                chapters.append(cur)
            cur = {"code": m.group(1).strip(), "title": m.group(2).strip(), "text": ""}
            continue
        if FOOTER_RE.search(line):
            continue
        if cur is not None:
            # 部分頁面 PDF 抽字時題號數字中間會插入雜訊空白（如「19 1.」應為「191.」），
            # 與歷屆卷相同做法：整行去除全部空白字元後再接續，避免題號被切斷誤判。
            cur["text"] += re.sub(r"\s+", "", line) + "\n"
if cur is not None:
    chapters.append(cur)

print("chapters found:", len(chapters), file=sys.stderr)
for c in chapters:
    print(c["code"], c["title"], file=sys.stderr)

anomalies = []
all_questions = []
for c in chapters:
    qs = parse_question_block(c["text"], anomalies, tag=f"bank chapter {c['code']}({c['title']})")
    for q in qs:
        q["chapter_code"] = c["code"]
        q["chapter_title"] = c["title"]
    all_questions.extend(qs)

print("total questions parsed:", len(all_questions), file=sys.stderr)
print("anomalies:", len(anomalies), file=sys.stderr)
for a in anomalies:
    print("ANOMALY:", a, file=sys.stderr)

with open("tools/tmp_safety/bank_parsed.json", "w", encoding="utf-8") as f:
    json.dump({"chapters": [{"code": c["code"], "title": c["title"]} for c in chapters],
               "questions": all_questions, "anomalies": anomalies}, f, ensure_ascii=False, indent=1)
