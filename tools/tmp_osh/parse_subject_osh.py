import sys, json, re
sys.path.insert(0, "tools/tmp")
from lib import extract_pages, split_options

HEADER_PATTERNS = [
    re.compile(r"^\d{2,3}年度22200職業安全衛生管理乙級.*學科測試試題$"),
    re.compile(r"^\d{2,3}職業安全衛生管理乙\d+-\d+\(序\d+\)$"),
    re.compile(r"^本試卷有選擇題"),
    re.compile(r"^為?\d*分鐘，請在答案卡上作答，答錯不倒扣；未作答者，不予計分。$"),
    re.compile(r"^准考證號碼[:：]?$"),
    re.compile(r"^姓名[:：]?$"),
    re.compile(r"^單選題[:：]?$"),
    re.compile(r"^複選題[:：]?$"),
]

# 題號在抽取時可能被插入空白（如「27 3.」＝「273.」），容忍題號與答案括號內部空白。
Q_START = re.compile(r"\n\s*((?:\d\s*){1,3})\.\s{0,3}\(\s*((?:\d\s*){1,4})\)\s*")

# 105、106 年度(共 6 份)為純掃描影像 PDF，pypdf/pdftotext/PyMuPDF 均抽不出文字層，
# 依專案慣例「不做 OCR、不虛構」，本次略過，於報告中列為待補清單。
SKIPPED_NO_TEXT_LAYER = [
    "105_第1梯次_學科試題暨答案.pdf",
    "105_第2梯次_學科試題暨答案.pdf",
    "105_第3梯次_學科試題暨答案.pdf",
    "106_第1梯次_學科試題暨答案.pdf",
    "106_第2梯次_學科試題暨答案.pdf",
    "106_第3梯次_學科試題暨答案.pdf",
]

FILES = [
    ("107", 1, "raw-osh/subject/107_第1梯次_學科試題暨答案.pdf"),
    ("107", 2, "raw-osh/subject/107_第2梯次_學科試題暨答案.pdf"),
    ("107", 3, "raw-osh/subject/107_第3梯次_學科試題暨答案.pdf"),
    ("108", 1, "raw-osh/subject/108_第1梯次_學科試題暨答案.pdf"),
    ("108", 2, "raw-osh/subject/108_第2梯次_學科試題暨答案.pdf"),
    ("108", 3, "raw-osh/subject/108_第3梯次_學科試題暨答案.pdf"),
    ("109", 1, "raw-osh/subject/109_第1梯次_學科試題暨答案.pdf"),
    ("109", 2, "raw-osh/subject/109_第2梯次_學科試題暨答案.pdf"),
    ("109", 3, "raw-osh/subject/109_第3梯次_學科試題暨答案.pdf"),
]

def matches_header(compact):
    return compact == "" or any(p.match(compact) for p in HEADER_PATTERNS)

def parse_one(path):
    pages_text = extract_pages(path)
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
        qno = int(re.sub(r"\s+", "", m.group(1)))
        ans = re.sub(r"\s+", "", m.group(2))
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
        anomalies.append(f"numbering mismatch: n={len(nums_seen)} first5={nums_seen[:5]} last5={nums_seen[-5:]} missing={sorted(set(expected)-set(nums_seen))}")
    return out, anomalies, dropped_sample

result = {}
report = []
for year, session, path in FILES:
    key = f"{year}-{session}"
    qs, anomalies, dropped = parse_one(path)
    single = [q for q in qs if len(q["answer_raw"]) == 1]
    multi = [q for q in qs if len(q["answer_raw"]) >= 2]
    result[key] = {"year": year, "session": session, "path": path, "questions": qs}
    line = f"{key}: total={len(qs)} single={len(single)} multi={len(multi)} anomalies={len(anomalies)}"
    report.append(line)
    print(line, file=sys.stderr)
    for a in anomalies:
        print("  ANOMALY:", a, file=sys.stderr)
    result[key]["anomalies"] = anomalies
    result[key]["dropped_header_lines_sample"] = list(dict.fromkeys(dropped))[:30]

with open("tools/tmp_osh/subject_parsed.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)

print("skipped (no text layer, scanned image):", SKIPPED_NO_TEXT_LAYER, file=sys.stderr)
