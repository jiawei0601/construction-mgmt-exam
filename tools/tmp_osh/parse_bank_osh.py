import sys, json, re
sys.path.insert(0, "tools/tmp")
from lib import extract_pages, split_options, FOOTER_RE

# 注意：本檔題號在 PDF 文字抽出時偶爾會被插入額外空白（例如「27 3.」實為「273.」），
# 沿用 tools/tmp/lib.py 的 parse_question_block 會漏題，故本檔另刻一份容忍題號內部空白的版本。
Q_START = re.compile(r"\n\s*((?:\d\s*){1,3})\.\s{0,3}\(\s*((?:\d\s*){1,4})\)\s*")

def parse_question_block(text, anomalies=None, tag=""):
    text = "\n" + text
    matches = list(Q_START.finditer(text))
    out = []
    nums_seen = []
    for i, m in enumerate(matches):
        qno = int(re.sub(r"\s+", "", m.group(1)))
        ans = re.sub(r"\s+", "", m.group(2))
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        chunk = text[start:end]
        stem, options = split_options(chunk)
        nums_seen.append(qno)
        if stem is None:
            if anomalies is not None:
                anomalies.append(f"{tag} q{qno}: no options found; raw={chunk[:80]!r}")
            continue
        out.append({"no": qno, "answer_raw": ans, "stem": stem, "options": options})
    expected = list(range(1, len(nums_seen) + 1))
    if nums_seen != expected and anomalies is not None:
        anomalies.append(f"{tag} numbering mismatch: got first5={nums_seen[:5]} last5={nums_seen[-5:]} count={len(nums_seen)} missing={sorted(set(expected)-set(nums_seen))}")
    return out

path = r"raw-osh/bank/22200_職業安全衛生管理_乙級_學科題庫.pdf"
pages_text = extract_pages(path)

HEADER_RE = re.compile(r"22200\s*職業安全衛生管理\s*乙級\s*工作項目\s*(\d+)\s*[:：]\s*(.+)")

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
            cur["text"] += line + "\n"
if cur is not None:
    chapters.append(cur)

print("chapters found:", len(chapters), file=sys.stderr)
for c in chapters:
    print(c["code"], c["title"], file=sys.stderr)

anomalies = []
all_questions = []
deleted_tagged = []
for c in chapters:
    qs = parse_question_block(c["text"], anomalies, tag=f"bank chapter {c['code']}({c['title']})")
    for q in qs:
        q["chapter_code"] = c["code"]
        q["chapter_title"] = c["title"]
        if "本題刪題" in q["stem"]:
            deleted_tagged.append(f"b-{c['code']}-{q['no']:03d}")
    all_questions.extend(qs)

print("total questions parsed:", len(all_questions), file=sys.stderr)
print("anomalies:", len(anomalies), file=sys.stderr)
for a in anomalies:
    print("ANOMALY:", a, file=sys.stderr)
print("deleted-tagged (本題刪題) questions kept verbatim:", len(deleted_tagged), file=sys.stderr)
for d in deleted_tagged:
    print("  ", d, file=sys.stderr)

with open("tools/tmp_osh/bank_parsed.json", "w", encoding="utf-8") as f:
    json.dump({"chapters": [{"code": c["code"], "title": c["title"]} for c in chapters],
               "questions": all_questions, "anomalies": anomalies,
               "deleted_tagged": deleted_tagged}, f, ensure_ascii=False, indent=1)
