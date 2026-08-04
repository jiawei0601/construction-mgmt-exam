import json, re, datetime

d = json.load(open("tools/tmp_osh/final_questions.json", encoding="utf-8"))
qs = d["questions"]

def sort_key(q):
    if q["id"].startswith("b-"):
        m = re.match(r"b-(\d+)-(\d+)", q["id"])
        return (0, m.group(1), int(m.group(2)))
    if q["id"].startswith("s-"):
        m = re.match(r"s-(\d+)-(\S+?)-(\d+)", q["id"])
        return (1, "", 0, q["id"])
    if q["id"].startswith("c-"):
        m = re.match(r"c-(\d+)-(\d+)", q["id"])
        return (2, m.group(1), int(m.group(2)))
    return (9, "", 0)

qs_sorted = sorted(qs, key=sort_key)

sources = [
    "raw-osh/bank/22200_職業安全衛生管理_乙級_學科題庫.pdf",
    "data/questions.js（c- 開頭 400 題原樣複製，未重新解析 raw-osh/common，因為該職類不含此資料夾；共同科目沿用既有題庫）",
    "raw-osh/subject/107_第1梯次_學科試題暨答案.pdf",
    "raw-osh/subject/107_第2梯次_學科試題暨答案.pdf",
    "raw-osh/subject/107_第3梯次_學科試題暨答案.pdf",
    "raw-osh/subject/108_第1梯次_學科試題暨答案.pdf",
    "raw-osh/subject/108_第2梯次_學科試題暨答案.pdf",
    "raw-osh/subject/108_第3梯次_學科試題暨答案.pdf",
    "raw-osh/subject/109_第1梯次_學科試題暨答案.pdf",
    "raw-osh/subject/109_第2梯次_學科試題暨答案.pdf",
    "raw-osh/subject/109_第3梯次_學科試題暨答案.pdf",
    "raw-osh/subject/105_第1梯次_學科試題暨答案.pdf (未收錄:純掃描影像PDF、無文字層，依規則不做OCR，見OSH_PARSE_REPORT.md)",
    "raw-osh/subject/105_第2梯次_學科試題暨答案.pdf (未收錄:同上)",
    "raw-osh/subject/105_第3梯次_學科試題暨答案.pdf (未收錄:同上)",
    "raw-osh/subject/106_第1梯次_學科試題暨答案.pdf (未收錄:同上)",
    "raw-osh/subject/106_第2梯次_學科試題暨答案.pdf (未收錄:同上)",
    "raw-osh/subject/106_第3梯次_學科試題暨答案.pdf (未收錄:同上)",
]

meta = {
    "job": "職業安全衛生管理",
    "level": "乙級",
    "generated": datetime.date.today().isoformat(),
    "sources": sources,
}

out = {"meta": meta, "questions": qs_sorted}

json_str = json.dumps(out, ensure_ascii=False, indent=2)

js = (
    "// 職業安全衛生管理乙級 題庫資料（自動產生，來源見 meta.sources；解析報告見 data/OSH_PARSE_REPORT.md）\n"
    "// schema 與 data/questions.js 一致，不可改動：見 AGENTS.md / 任務說明\n"
    "window.EXAM_DATA = " + json_str + ";\n"
)

with open("data/osh-questions.js", "w", encoding="utf-8") as f:
    f.write(js)

print("written, total questions:", len(qs_sorted))
