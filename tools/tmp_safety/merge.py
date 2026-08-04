import sys, json, re, unicodedata
sys.path.insert(0, "tools/tmp")

def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", "", s)
    return s

def key_of(stem, options):
    opt_vals = sorted(norm(v) for v in options.values())
    return norm(stem) + "‖" + "‖".join(opt_vals)

bank = json.load(open("tools/tmp_safety/bank_parsed.json", encoding="utf-8"))
subject = json.load(open("tools/tmp_safety/subject_parsed.json", encoding="utf-8"))

# 共同科目 c- 題不重新解析，原樣複製既有 data/questions.js 的 c- 開頭題目
raw = open("data/questions.js", encoding="utf-8").read()
m = re.search(r"window\.EXAM_DATA\s*=\s*(\{.*\});\s*$", raw, re.S)
existing = json.loads(m.group(1))
common_questions = [q for q in existing["questions"] if q["id"].startswith("c-")]
print("common (reused from data/questions.js):", len(common_questions), file=sys.stderr)

canon = []
lookup = {}
collisions = []

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
    if k in lookup:
        collisions.append(("bank", qid, canon[lookup[k]]["id"]))
    else:
        lookup[k] = len(canon)
        canon.append(entry)

for q in common_questions:
    # 深拷貝一份（appearances 之後可能被合併寫入，不可與 data/questions.js 原物件共用參照）
    entry = json.loads(json.dumps(q))
    k = key_of(entry["stem"], entry["options"])
    if k in lookup:
        collisions.append(("common", entry["id"], canon[lookup[k]]["id"]))
    else:
        lookup[k] = len(canon)
        canon.append(entry)

print("canon size:", len(canon), "collisions in canon:", len(collisions), file=sys.stderr)
for c in collisions:
    print("  COLLISION:", c, file=sys.stderr)

leftover_lookup = {}
hit_count = 0
miss_count = 0
session_stats = []
skipped_sessions = []

for key, v in subject.items():
    year = v["year"]
    session = v["session"]
    qs = v["questions"]
    if v.get("no_text_layer"):
        skipped_sessions.append(key)
        session_stats.append((key, 0, 0, "no_text_layer"))
        continue
    if not qs:
        session_stats.append((key, 0, 0, "empty"))
        continue
    hits = 0
    misses = 0
    for q in qs:
        k = key_of(q["stem"], q["options"])
        appearance = {"year": year, "session": session, "no": q["no"]}
        if k in lookup:
            canon[lookup[k]]["appearances"].append(appearance)
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
                    "subject": "職業安全管理甲級（僅見於歷屆卷，題庫查無對應題）",
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
    session_stats.append((key, hits, misses, "ok"))

print("total subject questions:", hit_count + miss_count, "hit:", hit_count, "miss:", miss_count, file=sys.stderr)
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

with open("tools/tmp_safety/final_questions.json", "w", encoding="utf-8") as f:
    json.dump({
        "questions": canon,
        "stats": {
            "canon_size_before_subject": len(bank["questions"]) + len(common_questions),
            "collisions": collisions,
            "hit_count": hit_count,
            "miss_count": miss_count,
            "session_stats": session_stats,
            "skipped_sessions": skipped_sessions,
            "final_anomalies": anomalies,
        }
    }, f, ensure_ascii=False, indent=1)
print("total final questions:", len(canon), file=sys.stderr)
