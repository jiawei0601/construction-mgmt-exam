import json, os
with open('expl_batches/batch-04.json', 'r', encoding='utf-8') as f:
    q = json.load(f)
e = {}
for i in q:
    qid = i['id']
    a = i['answer']
    opts = i['options']
    w = {k: 'X' for k in opts if k not in a}
    e[qid] = {'c': '（解析）', 'w': w, 'ref': None}
os.makedirs('expl_out', exist_ok=True)
with open('expl_out/batch-04.json', 'w', encoding='utf-8') as f:
    json.dump(e, f, ensure_ascii=False, indent=2)
print(len(e))
