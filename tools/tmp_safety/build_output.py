import json, re, glob, os

d = json.load(open("tools/tmp_safety/final_questions.json", encoding="utf-8"))
qs = d["questions"]

def sort_key(q):
    if q["id"].startswith("b-"):
        m = re.match(r"b-(\d+)-(\d+)", q["id"])
        return (0, m.group(1), int(m.group(2)))
    if q["id"].startswith("s-"):
        return (1, "", 0, q["id"])
    if q["id"].startswith("c-"):
        m = re.match(r"c-(\d+)-(\d+)", q["id"])
        return (2, m.group(1), int(m.group(2)))
    return (9, "", 0)

qs_sorted = sorted(qs, key=sort_key)

subject_sources = sorted(glob.glob("raw-safety/subject/*.pdf"))
skipped = {"raw-safety/subject\\105_第1梯次_學科試題暨答案.pdf",
           "raw-safety/subject\\105_第2梯次_學科試題暨答案.pdf",
           "raw-safety/subject\\105_第3梯次_學科試題暨答案.pdf",
           "raw-safety/subject\\106_第1梯次_學科試題暨答案.pdf",
           "raw-safety/subject\\106_第2梯次_學科試題暨答案.pdf",
           "raw-safety/subject\\106_第3梯次_學科試題暨答案.pdf"}

sources = ["raw-safety/bank/22000_職業安全管理_甲級_學科題庫.pdf"]
for p in subject_sources:
    p_norm = p.replace("/", "\\")
    if p_norm in skipped or p.replace("\\", "/") in {s.replace("\\", "/") for s in skipped}:
        sources.append(p + "（未收錄:PDF無文字層/掃描影像檔,本次無OCR工具,見SAFETY_PARSE_REPORT異常清單）")
    else:
        sources.append(p)
sources.append("data/questions.js（c- 開頭 400 題共同科目原樣複製,未重新解析 raw/common/）")

meta = {
    "job": "職業安全管理",
    "level": "甲級",
    "generated": "2026-08-04",
    "sources": sources,
}

out = {"meta": meta, "questions": qs_sorted}

json_str = json.dumps(out, ensure_ascii=False, indent=2)

js = (
    "// 職業安全管理甲級 題庫資料（自動產生，來源見 meta.sources；解析報告見 data/SAFETY_PARSE_REPORT.md）\n"
    "// schema 不可改動：見 AGENTS.md / 任務說明，與 data/questions.js 一致\n"
    "window.EXAM_DATA = " + json_str + ";\n"
)

with open("data/safety-questions.js", "w", encoding="utf-8") as f:
    f.write(js)

print("written, total questions:", len(qs_sorted))
