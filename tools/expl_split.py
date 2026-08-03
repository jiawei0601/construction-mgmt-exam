# 把 data/questions.js（window.EXAM_DATA）依序平均切成 12 批，寫入
# tools/expl_batches/batch-01.json ~ batch-12.json，供 haiku agent 分批撰寫解析。
# 每題只留 {id, stem, options, answer}（answer 保留給 agent 判斷「為何對」用）。
# 用法: python -X utf8 tools/expl_split.py
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, 'data', 'questions.js')
OUT = os.path.join(HERE, 'expl_batches')
N_BATCHES = 12

os.makedirs(OUT, exist_ok=True)

raw = open(SRC, encoding='utf-8').read()
m = re.search(r'window\.EXAM_DATA\s*=\s*(\{.*\});?\s*$', raw, re.S)
if not m:
    raise SystemExit('找不到 window.EXAM_DATA 賦值，請確認 data/questions.js 格式未變')
data = json.loads(m.group(1))
questions = data['questions']
total = len(questions)

slim = [
    {
        'id': q['id'],
        'stem': q['stem'],
        'options': q['options'],
        'answer': q['answer'],
    }
    for q in questions
]

# 平均切分：前 (total % N_BATCHES) 批多分 1 題，其餘平分
base = total // N_BATCHES
extra = total % N_BATCHES
idx = 0
counts = []
for b in range(N_BATCHES):
    size = base + (1 if b < extra else 0)
    chunk = slim[idx:idx + size]
    idx += size
    path = os.path.join(OUT, f'batch-{b + 1:02d}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(chunk, f, ensure_ascii=False, indent=1)
    counts.append((f'batch-{b + 1:02d}.json', len(chunk)))

print(f'總題數: {total}')
for name, n in counts:
    print(f'{name}\t{n} 題')
print(f'切分後總計: {sum(n for _, n in counts)} 題（應等於總題數）')
