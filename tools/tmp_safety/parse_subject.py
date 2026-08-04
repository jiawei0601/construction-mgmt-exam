import sys, json, re, glob, os
sys.path.insert(0, "tools/tmp")
from lib import extract_pages, split_options

HEADER_PATTERNS = [
    re.compile(r"^\d{2,3}職業安全管理甲\d+-\d+\(序\d+\)$"),
    re.compile(r"^\d{2,3}年度22000職業安全管理甲級技術士技能檢定學科測試試題$"),
    re.compile(r"^全國技術士技能檢定第\d+梯次$"),
    re.compile(r"^本試卷有選擇題"),
    re.compile(r"^准考證號碼[:：]?$"),
    re.compile(r"^姓名[:：]?$"),
    re.compile(r"^單選題[:：]?$"),
    re.compile(r"^複選題[:：]?$"),
    re.compile(r"^第\d+頁"),
    re.compile(r"共\d+頁$"),
    re.compile(r"^Page\d+of\d+$"),
]

Q_START = re.compile(r"\n(\d{1,3})\.\((\d{1,4})\)")

NAME_RE = re.compile(r"^(\d{3})_第(\d)梯次(_颱風延期考區)?_學科試題暨答案$")

FILES = []
SKIPPED_NO_TEXT = []
for path in sorted(glob.glob("raw-safety/subject/*.pdf")):
    base = os.path.splitext(os.path.basename(path))[0]
    m = NAME_RE.match(base)
    if not m:
        print("UNRECOGNIZED FILENAME:", base, file=sys.stderr)
        continue
    year = m.group(1)
    session = int(m.group(2))
    if m.group(3):
        session = f"{session}颱風延期考區"
    FILES.append((year, session, path))

def matches_header(compact):
    return compact == "" or any(p.match(compact) for p in HEADER_PATTERNS)

def parse_one(path):
    pages_text = extract_pages(path)
    total_text_len = sum(len(t) for t in pages_text)
    buf = ""
    dropped_sample = []
    for text in pages_text:
        for line in text.split("\n"):
            compact = re.sub(r"\s+", "", line)
            if matches_header(compact):
                if compact:
                    dropped_sample.append(compact)
                continue
            buf += compact + "\n"
    text = "\n" + buf
    matches = list(Q_START.finditer(text))
    out = []
    nums_seen = []
    anomalies = []
    for i, m in enumerate(matches):
        qno = int(m.group(1))
        ans = m.group(2)
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        chunk = text[start:end].replace("\n", "")
        stem, options = split_options(chunk)
        nums_seen.append(qno)
        if stem is None:
            anomalies.append(f"q{qno}: no options; raw={chunk[:80]!r}")
            continue
        out.append({"no": qno, "answer_raw": ans, "stem": stem, "options": options})
    expected = list(range(1, len(nums_seen) + 1))
    if nums_seen != expected:
        anomalies.append(f"numbering mismatch: n={len(nums_seen)} first5={nums_seen[:5]} last5={nums_seen[-5:]}")
    return out, anomalies, dropped_sample, total_text_len

result = {}
report = []
for year, session, path in FILES:
    key = f"{year}-{session}"
    qs, anomalies, dropped, total_text_len = parse_one(path)
    if total_text_len == 0:
        SKIPPED_NO_TEXT.append(path)
        result[key] = {"year": year, "session": session, "path": path, "questions": [],
                        "anomalies": ["PDF 無可抽取文字層（掃描影像檔），本次無 OCR 工具，未解析，見報告異常清單"],
                        "dropped_header_lines_sample": [], "no_text_layer": True}
        line = f"{key}: SKIPPED (無文字層/掃描檔)"
        report.append(line)
        print(line, file=sys.stderr)
        continue
    single = [q for q in qs if len(q["answer_raw"]) == 1]
    multi = [q for q in qs if len(q["answer_raw"]) >= 2]
    result[key] = {"year": year, "session": session, "path": path, "questions": qs}
    line = f"{key}: total={len(qs)} single={len(single)} multi={len(multi)} anomalies={len(anomalies)}"
    report.append(line)
    print(line, file=sys.stderr)
    for a in anomalies:
        print("  ANOMALY:", a, file=sys.stderr)
    result[key]["anomalies"] = anomalies
    result[key]["dropped_header_lines_sample"] = list(dict.fromkeys(dropped))[:20]

print("skipped (no text layer):", len(SKIPPED_NO_TEXT), file=sys.stderr)
for p in SKIPPED_NO_TEXT:
    print("  ", p, file=sys.stderr)

with open("tools/tmp_safety/subject_parsed.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
