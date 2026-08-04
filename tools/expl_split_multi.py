# 把 data/{osh,safety,hygiene}-questions.js（window.EXAM_DATA）依序平均切成約125題一批，
# 寫入 tools/expl_batches_v2/{trade}-batch-NN.json，供 haiku agent 分批撰寫解析。
# 只取專業題（id 不以 c- 開頭；c- 共同科目400題與營造工程管理甲級共用既有
# data/explanations.js，本管線不重複解析）。
# 每題只留 {id, stem, options, answer}（answer 保留給 agent 判斷「為何對」用），
# 與 tools/expl_split.py 同格式，供 tools/expl_merge_multi.py 讀回原文做模糊比對查詢串。
# 用法: python -X utf8 tools/expl_split_multi.py
import json, os, re, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'expl_batches_v2')
TARGET_BATCH_SIZE = 125

TRADES = {
    'osh': os.path.join(ROOT, 'data', 'osh-questions.js'),
    'safety': os.path.join(ROOT, 'data', 'safety-questions.js'),
    'hygiene': os.path.join(ROOT, 'data', 'hygiene-questions.js'),
}

os.makedirs(OUT, exist_ok=True)


def load_questions(path):
    raw = open(path, encoding='utf-8').read()
    m = re.search(r'window\.EXAM_DATA\s*=\s*(\{.*\});?\s*$', raw, re.S)
    if not m:
        raise SystemExit(f'找不到 window.EXAM_DATA 賦值，請確認 {path} 格式未變')
    data = json.loads(m.group(1))
    return data['questions']


def split_trade(trade, path):
    questions = load_questions(path)
    professional = [q for q in questions if not q['id'].startswith('c-')]
    total_all = len(questions)
    total = len(professional)

    n_batches = max(1, math.ceil(total / TARGET_BATCH_SIZE))
    base = total // n_batches
    extra = total % n_batches

    slim = [
        {
            'id': q['id'],
            'stem': q['stem'],
            'options': q['options'],
            'answer': q['answer'],
        }
        for q in professional
    ]

    idx = 0
    counts = []
    for b in range(n_batches):
        size = base + (1 if b < extra else 0)
        chunk = slim[idx:idx + size]
        idx += size
        out_path = os.path.join(OUT, f'{trade}-batch-{b + 1:02d}.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, indent=1)
        counts.append((f'{trade}-batch-{b + 1:02d}.json', len(chunk)))

    print(f'=== {trade} ===')
    print(f'題庫總題數: {total_all}（其中 c- 共同科目 {total_all - total} 題不切批）')
    print(f'專業題總數: {total}')
    print(f'批次數: {n_batches}（目標每批約 {TARGET_BATCH_SIZE} 題）')
    for name, n in counts:
        print(f'  {name}\t{n} 題')
    checksum = sum(n for _, n in counts)
    ok = checksum == total
    print(f'切分後總計: {checksum} 題（{"OK" if ok else "!! 不等於專業題總數 !!"}）')
    print()
    return total, n_batches, ok


if __name__ == '__main__':
    all_ok = True
    grand_total = 0
    for trade, path in TRADES.items():
        total, n_batches, ok = split_trade(trade, path)
        grand_total += total
        all_ok = all_ok and ok
    print(f'=== 全部職類專業題合計: {grand_total} 題 ===')
    if not all_ok:
        raise SystemExit('!! 有職類切分後總計對不上，請檢查上方輸出 !!')
