# 合併 12 個 haiku agent 分批寫好的解析（tools/expl_out/batch-*.json），
# 補接官方法條全文，輸出 data/explanations.js。
#
# 輸入格式（每個 batch 檔）：
#   {"<id>": {"c": "正解理由", "w": {"1": "錯因", ...}, "ref": "法規名稱§第X條" | "法規名稱" | null}, ...}
#
# 處理規則：
#   - ref 為 null 或空字串 → 不處理 law 欄位。
#   - ref 含「法規名稱§條號」→ 到 tools/law_corpus/<法規名稱>.txt 抽出該條全文，
#     加進 law = "《法規名》第X條：全文"。條號支援「第150條」「第150條之1」「第150-1條」等寫法。
#     找不到對應法規檔、或該法規檔內找不到該條號 → 記入 tools/expl_out/UNMATCHED.txt。
#   - ref 只有「法規名稱」（無 § 條號）→ 若該法規語料存在，用「保守模糊比對」
#     （見下方 name-only fuzzy match 區塊）嘗試補上條號；比對不到門檻則保留原 ref，不加 law。
#
# 輸出：data/explanations.js，內容 `window.EXAM_EXPL = {id:{c,w,ref,law?,g?}, ...};`
#   g:1 表示該筆 law 是自動模糊比對接上的（非人工/LLM 標註條號），供 QA 抽查與 UI 淡化顯示用。
#
# 用法: python -X utf8 tools/expl_merge.py
#       python -X utf8 tools/expl_merge.py --selftest   # 跑內建假資料自測，不動真實輸出檔

import glob
import json
import os
import random
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LAW_DIR = os.path.join(HERE, 'law_corpus')
BATCH_SRC_DIR = os.path.join(HERE, 'expl_batches')  # 題目原文（stem/options/answer），模糊比對查詢串用
# 題目原文檔名 glob pattern；預設對應本檔（單一營造工程管理甲級）的 batch-01.json 等命名。
# tools/expl_merge_multi.py 會在呼叫前把本變數與上面三個路徑改成各職類專用值，
# 藉此重用本檔的條號抽取＋模糊比對邏輯而不需複製貼上。
BATCH_GLOB_PATTERN = 'batch-*.json'
OUT_DIR = os.path.join(HERE, 'expl_out')
UNMATCHED_PATH = os.path.join(OUT_DIR, 'UNMATCHED.txt')
AUTOMATCH_SAMPLE_PATH = os.path.join(OUT_DIR, 'AUTOMATCH_SAMPLE.txt')
DEST = os.path.join(ROOT, 'data', 'explanations.js')

ARTICLE_HEADER_RE = re.compile(r'^第\s*(\d+)(?:-(\d+))?\s*條$')
CHAPTER_MARKER_RE = re.compile(r'^【.*】$')


def load_law_articles(law_name):
    """回傳 {(base, sub_or_None): article_text} 的 dict，law_name 對應 law_corpus/<law_name>.txt"""
    path = os.path.join(LAW_DIR, f'{law_name}.txt')
    if not os.path.isfile(path):
        return None
    lines = open(path, encoding='utf-8').read().split('\n')
    articles = {}
    cur_key = None
    cur_lines = []

    def flush():
        if cur_key is not None:
            articles[cur_key] = '\n'.join(cur_lines).strip()

    for line in lines:
        stripped = line.strip()
        m = ARTICLE_HEADER_RE.match(stripped)
        if m:
            flush()
            base = int(m.group(1))
            sub = int(m.group(2)) if m.group(2) else None
            cur_key = (base, sub)
            cur_lines = []
        elif CHAPTER_MARKER_RE.match(stripped):
            # 編/章/節標題（如「【貳、履約管理】」）：結束目前條文累積，
            # 但不視為新條文開頭，避免章節名稱混入條文內容。
            flush()
            cur_key = None
            cur_lines = []
        else:
            if cur_key is not None:
                cur_lines.append(line)
    flush()
    return articles


_law_cache = {}


def get_law_articles(law_name):
    if law_name not in _law_cache:
        _law_cache[law_name] = load_law_articles(law_name)
    return _law_cache[law_name]


# ==================== name-only ref 的保守模糊比對 ====================
#
# 背景：926 筆有 ref 的題目中，僅 14 筆帶條號（§），其餘 912 筆只有法規名稱。
# 官方學科題庫的法規題大多幾乎逐字取自法條文字，所以用「查詢字串（題幹＋正解選項）
# 對該法規逐條計算字元 bigram containment」可以找回相當一部分條號。
#
# 但並非所有題目都是逐字引用——不少是概念性/定義性問法（例如「下列何者為建築法
# 所規定之設計人」對應「建築師」），這種題目的查詢字串跟條文本身重疊率天生就低，
# 比對分數也低，不會被誤採用。這正是本比對法「文字重疊度低→自動篩掉」的特性，
# 不需要額外規則區分題型。
#
# 門檻校調紀錄（2026-08-03）：
#   - 對全部 626 筆「語料存在對應法規」的 name-only 題目跑過一輪，分數分布：
#     1.0~0.9: 42 筆／0.8~0.7: 84 筆／0.6~0.5: 93 筆／0.4以下: 407 筆，中間無斷崖，
#     故不能只看單一分數門檻，必須併用「與第二名的差距」防止在多條文字面相近時誤判。
#   - 對現有 13 筆人工/LLM 標註為 §條號的題目回測：正確條文的分數多落在 0.3~0.55、
#     且常常不是同法規中分數最高的一條（例如 b-01-001 標註第12條，但比對最高分是
#     第13條）——證實這批題目本身用詞是「概念問法」而非逐字引用，佐證帶§的 14 筆
#     跟本模糊比對鎖定的「逐字/近逐字引用」題型是兩個不同分布，用同一套分數尺度
#     判斷是合理的（不會因為前者分數普遍不高就誤導門檻設定）。
#   - 對 threshold=(score>=0.6, margin>=0.12) 通過的 135 筆中隨機／邊界抽測 20 筆
#     全數人工核對正確（20/20，含最高分群與margin剛好壓線 0.12~0.15 的邊界案例，
#     例如 b-07-049「營建工程空氣污染防制設施管理辦法」margin=0.132、
#     s-110-1-049「職業安全衛生教育訓練規則」margin=0.125，皆為正確比對）。
#   - 曾檢視 score=0.549（低於門檻，正確被排除）的一筆消防偵測器題目，其比對到的
#     條文用詞（3公尺）與題幹（1.5公尺）明顯兜不起來，證實 0.6 這條線落在
#     「逐字/近逐字引用」與「僅描述同主題但條文對不上」的自然分界上，不宜再降低。
#   - 結論：score>=0.6 且 margin(第一名−第二名)>=0.12 才採用；寧缺勿錯。
#
FUZZY_SCORE_THRESHOLD = 0.6
FUZZY_MARGIN_THRESHOLD = 0.12

# 題目本身用「法規全稱」但語料以其中一個分編／不同顆粒度儲存時的別名對照。
# 目前僅「建築技術規則」一項：官方題庫常只寫母法規名稱，未指明是哪一編，
# 語料則按「總則編／建築構造編／建築設備編／建築設計施工編」四檔分別存放，
# 故模糊比對時展開成四檔一起找最佳條文。
FUZZY_LAW_ALIAS = {
    '建築技術規則': [
        '建築技術規則建築設計施工編',
        '建築技術規則建築構造編',
        '建築技術規則建築設備編',
        '建築技術規則總則編',
    ],
    # 題庫俗稱「刑法」，語料按官方正式登記名稱存成「中華民國刑法」。
    '刑法': ['中華民國刑法'],
}

# 比對前先去除空白／標點雜訊，只留文字本體再切 bigram，避免標點差異拉低重疊率。
_FUZZY_NOISE_RE = re.compile(
    r'[\s　。,，、;；:：「」『』()（）\.\-—~～·\[\]{}?？!！"\'​]+'
)


def _fuzzy_norm(text):
    return _FUZZY_NOISE_RE.sub('', text or '')


def _fuzzy_bigrams(text):
    return [text[i:i + 2] for i in range(len(text) - 1)]


_question_cache = None


def _load_question_bank():
    """回傳 {qid: {'stem':..., 'options':{...}, 'answer':[...]}, ...}，取自 tools/expl_batches/。"""
    global _question_cache
    if _question_cache is None:
        _question_cache = {}
        for path in sorted(glob.glob(os.path.join(BATCH_SRC_DIR, BATCH_GLOB_PATTERN))):
            for item in json.load(open(path, encoding='utf-8')):
                _question_cache[item['id']] = item
    return _question_cache


def _fuzzy_query_for(qid):
    """查詢字串＝題幹＋正解選項文字（多選則串接）。找不到題目原文則回傳 None。"""
    q = _load_question_bank().get(qid)
    if not q:
        return None
    stem = q.get('stem', '')
    opts = q.get('options', {})
    ans_text = ''.join(opts.get(a, '') for a in q.get('answer', []))
    return stem + ans_text


def _fuzzy_candidate_files(law_name):
    """回傳要搜尋的語料檔名清單；優先走別名展開，否則檢查該法規名稱本身是否有語料。"""
    if law_name in FUZZY_LAW_ALIAS:
        return FUZZY_LAW_ALIAS[law_name]
    if os.path.isfile(os.path.join(LAW_DIR, f'{law_name}.txt')):
        return [law_name]
    return []


def fuzzy_match_name_only(qid, law_name):
    """對 name-only ref 的題目做保守模糊比對。

    回傳 (matched_law_name, base, sub, score, margin) 通過門檻時；
    否則回傳 None（含：無查詢字串、無對應語料、分數/差距未達門檻）。
    """
    query = _fuzzy_query_for(qid)
    if not query:
        return None
    query_bigrams = Counter(_fuzzy_bigrams(_fuzzy_norm(query)))
    total = sum(query_bigrams.values())
    if total == 0:
        return None

    candidates = _fuzzy_candidate_files(law_name)
    scored = []
    for fname in candidates:
        articles = get_law_articles(fname)
        if not articles:
            continue
        for key, article_text in articles.items():
            article_bigrams = Counter(_fuzzy_bigrams(_fuzzy_norm(article_text)))
            inter = sum(min(n, article_bigrams.get(b, 0)) for b, n in query_bigrams.items())
            scored.append((inter / total, fname, key))

    if not scored:
        return None
    scored.sort(key=lambda x: -x[0])
    best_score, best_fname, best_key = scored[0]
    second_score = scored[1][0] if len(scored) > 1 else 0.0
    margin = best_score - second_score

    if best_score < FUZZY_SCORE_THRESHOLD or margin < FUZZY_MARGIN_THRESHOLD:
        return None

    base, sub = best_key
    return (best_fname, base, sub, best_score, margin)


# ==================== /name-only ref 的保守模糊比對 ====================


# 從條號文字（如「第150條之1」「第150-1條」「150條」「第 8 條」）抽出 (base, sub)
ARTICLE_NO_RE = re.compile(r'第?\s*(\d+)\s*條?\s*(?:之|-)\s*(\d+)\s*條?|第?\s*(\d+)\s*條')

# 中文數字條號（如「第三十五條」「第五十九條之一」）→ 阿拉伯數字。範圍支援到 999。
_CN_DIGIT = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
_CN_NUM_RE = re.compile(r'[零一二三四五六七八九十百]+')


def _cn2num(s):
    total, cur = 0, 0
    for ch in s:
        if ch == '百':
            total += (cur or 1) * 100
            cur = 0
        elif ch == '十':
            total += (cur or 1) * 10
            cur = 0
        else:
            cur = _CN_DIGIT[ch]
    return total + cur


def _normalize_cn_numerals(text):
    return _CN_NUM_RE.sub(lambda m: str(_cn2num(m.group())), text)


def parse_article_no(text):
    text = _normalize_cn_numerals(text)
    m = ARTICLE_NO_RE.search(text)
    if not m:
        return None
    if m.group(1) is not None:
        return (int(m.group(1)), int(m.group(2)))
    return (int(m.group(3)), None)


def format_article_key(base, sub):
    return f'第{base}條之{sub}' if sub is not None else f'第{base}條'


def resolve_ref(ref, qid, unmatched):
    """回傳 law 欄位字串，或 None（無法解析/無條號可解析）"""
    if not ref:
        return None
    if '§' not in ref:
        return None  # 只有法規名稱，無條號，不處理
    law_name, article_text = ref.split('§', 1)
    law_name = law_name.strip()
    article_text = article_text.strip()

    articles = get_law_articles(law_name)
    if articles is None:
        unmatched.append(f'{qid}\tref={ref}\t原因=找不到法規檔 {law_name}.txt')
        return None

    parsed = parse_article_no(article_text)
    if parsed is None:
        unmatched.append(f'{qid}\tref={ref}\t原因=無法解析條號「{article_text}」')
        return None

    base, sub = parsed
    content = articles.get((base, sub))
    if content is None:
        unmatched.append(f'{qid}\tref={ref}\t原因={law_name} 內找不到 {format_article_key(base, sub)}')
        return None

    return f'《{law_name}》{format_article_key(base, sub)}：{content}'


def merge(batch_glob, dest_path, verbose=True, write_automatch_sample=True,
          verify_native_article=False):
    """合併批次解析檔並接上法條全文。

    verify_native_article=False（預設，供本檔自身 cm 單職類 pipeline 使用，行為完全不變）：
      - ref 含「§條號」→ 直接信任 haiku 標註的條號，原生抽取全文（無 g 標記）。
      - ref 只有法規名稱 → 保守模糊比對，命中才掛全文（g:1）。

    verify_native_article=True（供 tools/expl_merge_multi.py 職安三職類專業題呼叫的新政策，
    解決 haiku 自標條號誤配問題）：
      - 對每筆含法規名稱的 ref（無論原本有無 § 條號），一律先跑保守模糊比對；
        命中 → 掛該條全文（g:1），且 ref 的條號一律以模糊比對結果為準改寫
        （若與 haiku 原標條號不同，即為「原生§被改寫」）。
        未命中 → 不掛條文，且 ref 降級為純法規名稱（去掉 § 條號），寧缺勿錯。
      - 回傳的 downgraded / rewritten 供呼叫端統計「ref 降級筆數」「原生§被改寫條號筆數」。
    """
    unmatched = []
    automatch_log = []  # [(qid, orig_ref, new_ref, score, margin), ...]，供 AUTOMATCH_SAMPLE.txt 抽樣用
    downgraded = []     # [(qid, orig_ref, new_ref), ...]，僅 verify_native_article=True 時使用
    rewritten = []       # [(qid, orig_ref, new_ref, score, margin), ...]，原生§被模糊比對改寫條號
    merged = {}
    files = sorted(glob.glob(batch_glob))
    for path in files:
        data = json.load(open(path, encoding='utf-8'))
        for qid, entry in data.items():
            ref = entry.get('ref')
            out = {
                'c': entry.get('c'),
                'w': entry.get('w', {}),
                'ref': ref,
            }

            if verify_native_article:
                if ref:
                    if '§' in ref:
                        orig_law_name, orig_article_text = ref.split('§', 1)
                        orig_law_name = orig_law_name.strip()
                        orig_parsed = parse_article_no(orig_article_text.strip())
                    else:
                        orig_law_name = ref.strip()
                        orig_parsed = None

                    m = fuzzy_match_name_only(qid, orig_law_name)
                    if m:
                        matched_law_name, base, sub, score, margin = m
                        articles = get_law_articles(matched_law_name)
                        content = articles[(base, sub)]
                        artkey = format_article_key(base, sub)
                        new_ref = f'{matched_law_name}§{artkey}'
                        out['ref'] = new_ref
                        out['law'] = f'《{matched_law_name}》{artkey}：{content}'
                        out['g'] = 1
                        automatch_log.append((qid, ref, new_ref, score, margin))
                        if orig_parsed is not None and orig_parsed != (base, sub):
                            rewritten.append((qid, ref, new_ref, score, margin))
                    else:
                        out['ref'] = orig_law_name
                        downgraded.append((qid, ref, out['ref']))
                merged[qid] = out
                continue

            # ---- 原有行為（單職類 cm pipeline，verify_native_article=False，維持不變） ----
            if ref and '§' in ref:
                law = resolve_ref(ref, qid, unmatched)
                if law:
                    out['law'] = law
            elif ref:
                # name-only ref：保守模糊比對，只有 score/margin 都過門檻才採用
                m = fuzzy_match_name_only(qid, ref.strip())
                if m:
                    matched_law_name, base, sub, score, margin = m
                    articles = get_law_articles(matched_law_name)
                    content = articles[(base, sub)]
                    artkey = format_article_key(base, sub)
                    new_ref = f'{matched_law_name}§{artkey}'
                    out['ref'] = new_ref
                    out['law'] = f'《{matched_law_name}》{artkey}：{content}'
                    out['g'] = 1
                    automatch_log.append((qid, ref, new_ref, score, margin))
            merged[qid] = out

    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write('window.EXAM_EXPL = ')
        json.dump(merged, f, ensure_ascii=False, indent=1)
        f.write(';\n')

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(UNMATCHED_PATH, 'w', encoding='utf-8') as f:
        if verify_native_article:
            f.write(f'ref 降級筆數（模糊比對未達門檻，ref 已降級為純法規名稱，去除 § 條號）: {len(downgraded)}\n\n')
            for qid, orig_ref, new_ref in downgraded:
                f.write(f'{qid}\t原ref={orig_ref}\t降級後={new_ref}\n')
        else:
            f.write('\n'.join(unmatched))
            if unmatched:
                f.write('\n')

    if write_automatch_sample:
        _write_automatch_sample(automatch_log)

    total = len(merged)
    with_ref = sum(1 for v in merged.values() if v.get('ref'))
    with_law_native = sum(1 for v in merged.values() if v.get('law') and not v.get('g'))
    with_law_auto = sum(1 for v in merged.values() if v.get('law') and v.get('g'))
    with_law_total = with_law_native + with_law_auto
    still_no_law = with_ref - with_law_total

    if verbose:
        print(f'總筆數: {total}')
        print(f'含 ref 筆數: {with_ref}')
        if verify_native_article:
            print(f'掛條文筆數（全部為模糊比對驗證，g:1）: {with_law_auto}')
            print(f'ref 降級筆數（模糊比對未達門檻）: {len(downgraded)}')
            print(f'原生§被模糊比對改寫條號筆數: {len(rewritten)}')
        else:
            print(f'帶條號接取成功（原生 §）: {with_law_native}')
            print(f'帶條號接取成功（自動模糊比對）: {with_law_auto}')
            print(f'仍無條文筆數: {still_no_law}')
            print(f'UNMATCHED 筆數: {len(unmatched)}')

    return merged, unmatched, downgraded, rewritten


def _write_automatch_sample(automatch_log, n=15, seed=20260803):
    """從自動模糊比對成功的清單隨機抽 n 筆，列出題幹前50字＋接上條文前80字，供人工覆核。"""
    if not automatch_log:
        with open(AUTOMATCH_SAMPLE_PATH, 'w', encoding='utf-8') as f:
            f.write('(本次無自動模糊比對成功案例)\n')
        return

    rng = random.Random(seed)
    sample = rng.sample(automatch_log, min(n, len(automatch_log)))
    qbank = _load_question_bank()

    lines = [f'自動模糊比對成功共 {len(automatch_log)} 筆，隨機抽樣 {len(sample)} 筆供人工覆核：', '']
    for qid, orig_ref, new_ref, score, margin in sample:
        q = qbank.get(qid, {})
        stem = (q.get('stem') or '')[:50]
        articles = get_law_articles(new_ref.split('§', 1)[0])
        law_name, artkey = new_ref.split('§', 1)
        parsed = parse_article_no(artkey)
        art_text = articles.get(parsed, '') if articles and parsed else ''
        lines.append(f'qid={qid}  score={score:.3f} margin={margin:.3f}  原ref={orig_ref}  ->  {new_ref}')
        lines.append(f'  題幹前50字：{stem}')
        lines.append(f'  條文前80字：{art_text[:80]}')
        lines.append('')

    with open(AUTOMATCH_SAMPLE_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def selftest():
    print('=== selftest 開始 ===')
    tmp_dir = os.path.join(OUT_DIR, '_selftest')
    os.makedirs(tmp_dir, exist_ok=True)
    fake_batch = {
        'TEST-001': {
            'c': '依營造安全衛生設施標準第1-1條，本標準所稱之定義如題所述。',
            'w': {'2': '錯誤選項2不符定義', '3': '錯誤選項3不符定義', '4': '錯誤選項4不符定義'},
            'ref': '營造安全衛生設施標準§第1條之1',
        },
        'TEST-002': {
            'c': '依政府採購法規定，機關辦理採購應依公開原則。',
            'w': {'2': '違反公開原則', '3': '違反公開原則', '4': '違反公開原則'},
            'ref': '政府採購法§第1條',
        },
        'TEST-003': {
            'c': '本題屬一般管理常識，無特定法規條號可引。',
            'w': {'2': '不符常識', '3': '不符常識', '4': '不符常識'},
            'ref': '職業安全衛生法',  # 只有法規名稱，無條號
        },
        'TEST-004': {
            'c': '本題非法規題。',
            'w': {'2': 'x', '3': 'x', '4': 'x'},
            'ref': None,
        },
        'TEST-005': {
            'c': '故意引用不存在的法規測試 UNMATCHED。',
            'w': {'2': 'x', '3': 'x', '4': 'x'},
            'ref': '不存在的法規§第999條',
        },
    }
    batch_path = os.path.join(tmp_dir, 'batch-01.json')
    with open(batch_path, 'w', encoding='utf-8') as f:
        json.dump(fake_batch, f, ensure_ascii=False, indent=1)

    dest_path = os.path.join(tmp_dir, 'explanations_test.js')
    # merge() 會經由模組層級的 UNMATCHED_PATH / AUTOMATCH_SAMPLE_PATH 寫檔，
    # selftest 期間暫時改指到 tmp_dir，避免覆蓋真實的 expl_out/UNMATCHED.txt。
    global UNMATCHED_PATH, AUTOMATCH_SAMPLE_PATH
    orig_unmatched_path = UNMATCHED_PATH
    orig_automatch_path = AUTOMATCH_SAMPLE_PATH
    UNMATCHED_PATH = os.path.join(tmp_dir, 'UNMATCHED_test.txt')
    AUTOMATCH_SAMPLE_PATH = os.path.join(tmp_dir, 'AUTOMATCH_SAMPLE_test.txt')
    try:
        merged, unmatched, _downgraded, _rewritten = merge(
            os.path.join(tmp_dir, 'batch-*.json'), dest_path, verbose=False, write_automatch_sample=False
        )
    finally:
        UNMATCHED_PATH = orig_unmatched_path
        AUTOMATCH_SAMPLE_PATH = orig_automatch_path

    ok = True
    # TEST-001: 第1-1條 應抽到「本標準所稱高架作業...」等第1-1條原文
    law1 = merged.get('TEST-001', {}).get('law', '')
    if '《營造安全衛生設施標準》第1條之1：' not in law1 or len(law1) < 20:
        print(f'[FAIL] TEST-001 law 抽取異常: {law1[:80]!r}')
        ok = False
    else:
        print(f'[OK] TEST-001 -> {law1[:60]}...')

    law2 = merged.get('TEST-002', {}).get('law', '')
    if '《政府採購法》第1條：' not in law2:
        print(f'[FAIL] TEST-002 law 抽取異常: {law2[:80]!r}')
        ok = False
    else:
        print(f'[OK] TEST-002 -> {law2[:60]}...')

    if 'law' in merged.get('TEST-003', {}):
        print('[FAIL] TEST-003 不應有 law 欄位（僅法規名稱無條號）')
        ok = False
    else:
        print('[OK] TEST-003 -> 無 law 欄位（符合預期）')

    if 'law' in merged.get('TEST-004', {}):
        print('[FAIL] TEST-004 不應有 law 欄位（ref=null）')
        ok = False
    else:
        print('[OK] TEST-004 -> 無 law 欄位（符合預期）')

    if not any('TEST-005' in line for line in unmatched):
        print('[FAIL] TEST-005 應出現在 UNMATCHED')
        ok = False
    else:
        print('[OK] TEST-005 -> 正確記入 UNMATCHED')

    # 清掉假輸出
    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)
    print('=== selftest 清理完成（假輸出已刪除） ===')
    print('=== selftest 全部通過 ===' if ok else '=== selftest 有失敗項目，見上方 [FAIL] ===')
    return ok


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        success = selftest()
        sys.exit(0 if success else 1)
    else:
        merge(os.path.join(OUT_DIR, 'batch-*.json'), DEST)
