import sys, json, re, unicodedata
sys.path.insert(0, "tools/tmp")

def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", "", s)
    return s

def key_of(stem, options):
    opt_vals = sorted(norm(v) for v in options.values())
    return norm(stem) + "‖" + "‖".join(opt_vals)

bank = json.load(open("tools/tmp_osh/bank_parsed.json", encoding="utf-8"))
subject = json.load(open("tools/tmp_osh/subject_parsed.json", encoding="utf-8"))

# 共同科目：不解析 raw-osh/common，直接從既有 data/questions.js 原樣複製 c- 開頭題目
import subprocess
node_script = """
const fs = require('fs');
global.window = {};
eval(fs.readFileSync('data/questions.js', 'utf8'));
const c = window.EXAM_DATA.questions.filter(q => q.id.startsWith('c-'));
process.stdout.write(JSON.stringify(c));
"""
out = subprocess.run(["node", "-e", node_script], capture_output=True, text=True, cwd=".")
if out.returncode != 0:
    print("ERROR extracting c- questions:", out.stderr, file=sys.stderr)
    sys.exit(1)
common_questions = json.loads(out.stdout)
print("copied c- questions from data/questions.js:", len(common_questions), file=sys.stderr)

canon = []
lookup = {}  # key -> list of canon indices (content-duplicate ids are kept, not dropped)
collisions = []

def add_to_lookup(k, idx, src, qid):
    if k in lookup:
        collisions.append((src, qid, [canon[i]["id"] for i in lookup[k]]))
        lookup[k].append(idx)
    else:
        lookup[k] = [idx]

for q in bank["questions"]:
    code = q["chapter_code"]
    title = q["chapter_title"]
    qid = f"b-{code}-{q['no']:03d}"
    answer = list(q["answer_raw"])
    entry = {
        "id": qid,
        "category": "professional",
        "subject": f"工作項目{code} {title}",
        "type": "single" if len(answer) == 1 else "multi",
        "stem": q["stem"],
        "options": q["options"],
        "answer": answer,
        "appearances": [],
    }
    k = key_of(q["stem"], q["options"])
    add_to_lookup(k, len(canon), "bank", qid)
    canon.append(entry)

# c- 題目原樣複製（含原 appearances），且一律保留全部 400 筆原 id，
# 即使與題庫題內容重複也不刪除（僅記錄為 collision 供報告揭露，比對命中時兩邊都會加註 appearances）
for q in common_questions:
    entry = dict(q)  # shallow copy, preserve all original fields verbatim
    entry.setdefault("appearances", [])
    k = key_of(q["stem"], q["options"])
    add_to_lookup(k, len(canon), "common", q["id"])
    canon.append(entry)

print("canon size:", len(canon), "content-duplicate collisions (kept, not dropped):", len(collisions), file=sys.stderr)
for c in collisions:
    print("  COLLISION:", c, file=sys.stderr)

leftover_lookup = {}
hit_count = 0
miss_count = 0
session_stats = []

for key, v in subject.items():
    year = v["year"]
    session = v["session"]
    qs = v["questions"]
    if not qs:
        session_stats.append((key, 0, 0))
        continue
    hits = 0
    misses = 0
    for q in qs:
        k = key_of(q["stem"], q["options"])
        appearance = {"year": year, "session": session, "no": q["no"]}
        if k in lookup:
            for idx in lookup[k]:
                canon[idx]["appearances"].append(appearance)
            hits += 1
            hit_count += 1
        else:
            if k in leftover_lookup:
                canon[leftover_lookup[k]]["appearances"].append(appearance)
            else:
                sid = f"s-{year}-{session}-{q['no']:03d}"
                answer = list(q["answer_raw"])
                entry = {
                    "id": sid,
                    "category": "professional",
                    "subject": "職業安全衛生管理乙級",
                    "type": "single" if len(answer) == 1 else "multi",
                    "stem": q["stem"],
                    "options": q["options"],
                    "answer": answer,
                    "appearances": [appearance],
                }
                leftover_lookup[k] = len(canon)
                canon.append(entry)
            misses += 1
            miss_count += 1
    session_stats.append((key, hits, misses))

print("total subject questions:", hit_count + miss_count, "hit(matched to bank/common):", hit_count, "miss(new s- entries):", miss_count, file=sys.stderr)
for s in session_stats:
    print("  session", s, file=sys.stderr)

anomalies = []
for q in canon:
    if len(q["options"]) < 2:
        anomalies.append(f"{q['id']}: options<2")
    if not q["answer"]:
        anomalies.append(f"{q['id']}: empty answer")
    for a in q["answer"]:
        if a not in q["options"]:
            anomalies.append(f"{q['id']}: answer {a} not in options")
    if q["type"] == "multi" and len(q["answer"]) < 2:
        anomalies.append(f"{q['id']}: type multi but answer len<2")

print("final validation anomalies:", len(anomalies), file=sys.stderr)
for a in anomalies[:50]:
    print("  ", a, file=sys.stderr)

with open("tools/tmp_osh/final_questions.json", "w", encoding="utf-8") as f:
    json.dump({
        "questions": canon,
        "stats": {
            "canon_size_before_subject": len(bank["questions"]) + len(common_questions),
            "collisions": collisions,
            "hit_count": hit_count,
            "miss_count": miss_count,
            "session_stats": session_stats,
            "final_anomalies": anomalies,
        }
    }, f, ensure_ascii=False, indent=1)
print("total final questions:", len(canon), file=sys.stderr)
