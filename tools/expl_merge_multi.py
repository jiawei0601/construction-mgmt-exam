# 職安三職類（osh/safety/hygiene）專業題解析合併，重用 tools/expl_merge.py 的
# 條號抽取＋保守模糊比對邏輯（同一套 0.6/0.12 門檻與 g:1 標記），不重寫演算法。
#
# 輸入：
#   - tools/expl_batches_v2/{trade}-batch-*.json  題目原文（stem/options/answer），
#     由 tools/expl_split_multi.py 產生，供模糊比對查詢串使用。
#   - tools/expl_out_v2/{trade}-batch-*.json      haiku agent 分批撰寫好的解析，
#     格式與 tools/expl_merge.py 的輸入格式相同：
#       {"<id>": {"c": "正解理由", "w": {"1": "錯因", ...}, "ref": "法規名稱§第X條" | "法規名稱" | null}, ...}
#
# 輸出：
#   - data/{trade}-explanations.js：window.EXAM_EXPL = {...};
#     內容＝該職類專業題解析（b-/s- 開頭）＋ 從既有 data/explanations.js 原樣併入的
#     400 筆 c- 共同科目解析（讓每頁 script src 只需載入單一 explanations 檔即可自足，
#     不用像 cm.html 系列頁那樣額外靠 gen_job_pages.py 過濾 id 命名空間）。
#   - tools/expl_out_v2/UNMATCHED_{trade}.txt、AUTOMATCH_SAMPLE_{trade}.txt
#     （沿用 expl_merge.py 同名輸出，分職類分別存放，避免互相覆寫）。
#
# 用法:
#   python -X utf8 tools/expl_merge_multi.py            # 合併 osh/safety/hygiene 三職類
#   python -X utf8 tools/expl_merge_multi.py osh         # 只合併單一職類
#   python -X utf8 tools/expl_merge_multi.py --selftest  # 跑內建假資料自測，不動真實輸出檔

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

sys.path.insert(0, HERE)
import expl_merge as em  # noqa: E402  重用條號抽取＋模糊比對邏輯

SPLIT_DIR = os.path.join(HERE, 'expl_batches_v2')  # 題目原文（expl_split_multi.py 產物）
OUT_DIR = os.path.join(HERE, 'expl_out_v2')         # haiku 解析輸出（本腳本讀取的來源）
CM_EXPL_PATH = os.path.join(ROOT, 'data', 'explanations.js')  # 既有營造甲級解析（借出 c- 400 筆）

TRADES = ['osh', 'safety', 'hygiene']


def load_common_explanations(path=CM_EXPL_PATH):
    """從既有 data/explanations.js 讀出 c- 開頭（共同科目400題）解析，原樣供三職類頁面自足使用。"""
    raw = open(path, encoding='utf-8').read()
    m = re.search(r'window\.EXAM_EXPL\s*=\s*(\{.*\});?\s*$', raw, re.S)
    if not m:
        raise SystemExit(f'找不到 window.EXAM_EXPL 賦值，請確認 {path} 格式未變')
    data = json.loads(m.group(1))
    common = {k: v for k, v in data.items() if k.startswith('c-')}
    return common


def merge_trade(trade, split_dir=SPLIT_DIR, out_dir=OUT_DIR, dest_path=None,
                 common_expl=None, verbose=True):
    """合併單一職類。回傳 (combined_dict, stats_dict)。

    common_expl 可由呼叫端注入（selftest 用假資料），預設讀取真實 data/explanations.js。
    dest_path 預設為 data/{trade}-explanations.js；selftest 可指向暫存檔避免污染真實輸出。
    """
    if dest_path is None:
        dest_path = os.path.join(ROOT, 'data', f'{trade}-explanations.js')
    if common_expl is None:
        common_expl = load_common_explanations()

    # 借用 expl_merge.py 的全域狀態做本職類專屬設定（含快取重置，避免跨職類殘留）。
    em.BATCH_SRC_DIR = split_dir
    em.BATCH_GLOB_PATTERN = f'{trade}-batch-*.json'
    em.OUT_DIR = out_dir
    em.UNMATCHED_PATH = os.path.join(out_dir, f'UNMATCHED_{trade}.txt')
    em.AUTOMATCH_SAMPLE_PATH = os.path.join(out_dir, f'AUTOMATCH_SAMPLE_{trade}.txt')
    em._question_cache = None  # 强制依本職類 split_dir 重新載入題目原文

    os.makedirs(out_dir, exist_ok=True)

    batch_glob = os.path.join(out_dir, f'{trade}-batch-*.json')
    if verbose:
        print(f'=== {trade} ===')
    # 新政策（僅職安三職類專業題適用，c- 共同科目不受影響）：一律先模糊比對驗證再掛條文
    # （g:1），未過門檻則 ref 降級為純法規名稱，不再盲信 haiku 自標的 § 條號。
    merged_prof, unmatched, downgraded, rewritten = em.merge(
        batch_glob, dest_path, verbose=verbose,
        write_automatch_sample=True, verify_native_article=True,
    )

    combined = dict(merged_prof)
    combined.update(common_expl)

    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write('window.EXAM_EXPL = ')
        json.dump(combined, f, ensure_ascii=False, indent=1)
        f.write(';\n')

    law_mounted = sum(1 for v in merged_prof.values() if v.get('g') == 1)
    stats = {
        'trade': trade,
        'professional_merged': len(merged_prof),
        'common_injected': len(common_expl),
        'combined_total': len(combined),
        'unmatched': len(unmatched),
        'law_mounted': law_mounted,          # 掛條文筆數（全部應為 g:1，模糊比對驗證通過）
        'downgraded': len(downgraded),       # ref 降級筆數（模糊比對未達門檻，去除 § 條號）
        'rewritten': len(rewritten),         # 原生§被模糊比對結果改寫條號筆數
        'dest_path': dest_path,
    }
    if verbose:
        print(f'職類={trade}  專業題解析筆數={stats["professional_merged"]}'
              f'  併入共同科目 c- 筆數={stats["common_injected"]}'
              f'  合併後總筆數={stats["combined_total"]}')
        print(f'  掛條文筆數(g:1)={law_mounted}  ref降級筆數={len(downgraded)}'
              f'  原生§被改寫條號筆數={len(rewritten)}')
        print(f'寫入: {dest_path}')
        print()
    return combined, stats


# ==================== 假資料自測 ====================

def selftest():
    print('=== expl_merge_multi selftest 開始 ===')
    import shutil

    tmp_root = os.path.join(HERE, 'tmp', '_selftest_merge_multi')
    tmp_split = os.path.join(tmp_root, 'split')
    tmp_out = os.path.join(tmp_root, 'out')
    tmp_dest = os.path.join(tmp_root, 'osh-explanations_test.js')
    shutil.rmtree(tmp_root, ignore_errors=True)
    os.makedirs(tmp_split, exist_ok=True)
    os.makedirs(tmp_out, exist_ok=True)

    trade = 'osh'

    # 假題目原文（模糊比對查詢串來源），格式同 expl_split_multi.py 產物。
    # 新政策下 merge_trade() 一律先跑模糊比對再決定是否掛條文，因此假題幹須刻意設計成
    # 「與真實語料某條文逐字相同」（必定命中）或「與該法規完全無重疊」（必定未達門檻），
    # 才能穩定測到兩條新路徑，不能像舊版那樣只造一句概念性題幹（分數會落在門檻邊界、不穩定）。
    fake_questions = [
        {
            'id': 'b-01-999',
            # 與 tools/law_corpus/政府採購法.txt 第1條全文逐字相同 → 模糊比對必中第1條。
            'stem': '為建立政府採購制度，依公平、公開之採購程序，提升採購效率與功能，確保採購品質，爰制定本法。',
            'options': {'1': 'x', '2': 'y', '3': 'z', '4': 'w'},
            'answer': [],
        },
        {
            'id': 's-90-001',
            # 與政府採購法任何條文皆無字面重疊的亂碼 → 模糊比對必未達門檻。
            'stem': 'ZzQQ亂碼測試字串999無意義內容XyKw隨機拼湊不含任何政府採購法用詞',
            'options': {'1': 'x', '2': 'y', '3': 'z', '4': 'w'},
            'answer': [],
        },
    ]
    with open(os.path.join(tmp_split, f'{trade}-batch-01.json'), 'w', encoding='utf-8') as f:
        json.dump(fake_questions, f, ensure_ascii=False, indent=1)

    # 假 haiku 解析輸出，格式同 expl_merge.py 既有輸入格式
    fake_batch = {
        'b-01-999': {
            'c': '依政府採購法規定，本法之立法目的如題述。',
            'w': {'2': 'x', '3': 'x', '4': 'x'},
            # haiku 故意自標錯誤條號（真正對應的是第1條，非第99條），
            # 用來驗證新政策會以模糊比對結果改寫條號，不再盲信原生 §。
            'ref': '政府採購法§第99條',
        },
        's-90-001': {
            'c': '本題非法規題，屬一般管理常識。',
            'w': {'2': 'x', '3': 'x', '4': 'x'},
            # name-only，但題幹與政府採購法完全無重疊，用來驗證「降級」路徑。
            'ref': '政府採購法',
        },
    }
    with open(os.path.join(tmp_out, f'{trade}-batch-01.json'), 'w', encoding='utf-8') as f:
        json.dump(fake_batch, f, ensure_ascii=False, indent=1)

    # 假共同科目 c- 解析（驗證合併/自足邏輯，不碰真實 data/explanations.js）
    fake_common = {
        'c-90006-001': {'c': '假共同科目解析，供 selftest 驗證合併用。', 'w': {}, 'ref': None},
    }

    ok = True

    combined, stats = merge_trade(
        trade, split_dir=tmp_split, out_dir=tmp_out, dest_path=tmp_dest,
        common_expl=fake_common, verbose=False,
    )

    # 檢查1：新政策——haiku 原標「第99條」是錯的，模糊比對命中真正的第1條，
    # 應以模糊比對結果改寫 ref 並掛上第1條全文、標記 g:1。
    entry1 = combined.get('b-01-999', {})
    law1 = entry1.get('law', '')
    if '《政府採購法》第1條：' not in law1:
        print(f'[FAIL] b-01-999 law 抽取異常: {law1[:80]!r}')
        ok = False
    elif entry1.get('ref') != '政府採購法§第1條':
        print(f'[FAIL] b-01-999 ref 應被模糊比對結果改寫為「政府採購法§第1條」，實際={entry1.get("ref")!r}')
        ok = False
    elif entry1.get('g') != 1:
        print('[FAIL] b-01-999 應標記 g:1（模糊比對驗證通過）')
        ok = False
    else:
        print(f'[OK] b-01-999 -> ref 已由錯誤的第99條改寫為 {entry1["ref"]}，g:1，law={law1[:40]}...')

    # 檢查2：name-only ref 但題幹與該法規完全無重疊 → 模糊比對未達門檻 → 不掛 law、ref 降級
    entry2 = combined.get('s-90-001', {})
    if 'law' in entry2:
        print('[FAIL] s-90-001 不應有 law 欄位（模糊比對應未達門檻）')
        ok = False
    elif entry2.get('ref') != '政府採購法':
        print(f'[FAIL] s-90-001 ref 應降級為純法規名稱「政府採購法」，實際={entry2.get("ref")!r}')
        ok = False
    else:
        print('[OK] s-90-001 -> 無 law 欄位、ref 降級為純法規名稱（符合新政策）')

    # 檢查2b：merge_trade() 回傳的統計應正確反映「掛條文1／降級1／原生§被改寫1」
    if stats.get('law_mounted') != 1 or stats.get('downgraded') != 1 or stats.get('rewritten') != 1:
        print(f'[FAIL] 統計異常: law_mounted={stats.get("law_mounted")} '
              f'downgraded={stats.get("downgraded")} rewritten={stats.get("rewritten")}（皆應為1）')
        ok = False
    else:
        print('[OK] stats -> law_mounted=1 downgraded=1 rewritten=1（符合新政策）')

    # 檢查3：假共同科目 c- 條目應原樣併入
    if combined.get('c-90006-001', {}).get('c') != fake_common['c-90006-001']['c']:
        print('[FAIL] c-90006-001（假共同科目）未正確併入')
        ok = False
    else:
        print('[OK] c-90006-001 -> 假共同科目原樣併入')

    # 檢查4：合併後總筆數 = 專業題2筆 + 共同科目1筆
    if stats['combined_total'] != 3:
        print(f'[FAIL] combined_total 應為3，實際={stats["combined_total"]}')
        ok = False
    else:
        print('[OK] combined_total == 3（2 專業 + 1 假共同科目）')

    # 檢查5：輸出檔案格式應為合法 window.EXAM_EXPL = {...}; 可被解析
    raw = open(tmp_dest, encoding='utf-8').read()
    m = re.match(r'window\.EXAM_EXPL = (\{.*\});\n$', raw, re.S)
    if not m:
        print('[FAIL] 輸出檔案格式不符 window.EXAM_EXPL = {...};')
        ok = False
    else:
        json.loads(m.group(1))  # 應可正常解析，解析失敗會丟例外
        print('[OK] 輸出檔案格式正確且可解析')

    # 檢查6：跨職類快取應正確隔離——換第二個假職類跑一次，不應看到前一職類的題目
    trade2 = 'safety'
    tmp_split2 = os.path.join(tmp_root, 'split2')
    tmp_out2 = os.path.join(tmp_root, 'out2')
    tmp_dest2 = os.path.join(tmp_root, 'safety-explanations_test.js')
    os.makedirs(tmp_split2, exist_ok=True)
    os.makedirs(tmp_out2, exist_ok=True)
    with open(os.path.join(tmp_split2, f'{trade2}-batch-01.json'), 'w', encoding='utf-8') as f:
        json.dump([{'id': 'b-02-888', 'stem': '假題目2', 'options': {'1': 'a', '2': 'b', '3': 'c', '4': 'd'}, 'answer': ['1']}],
                   f, ensure_ascii=False)
    with open(os.path.join(tmp_out2, f'{trade2}-batch-01.json'), 'w', encoding='utf-8') as f:
        json.dump({'b-02-888': {'c': '假解析2', 'w': {}, 'ref': None}}, f, ensure_ascii=False)
    combined2, stats2 = merge_trade(
        trade2, split_dir=tmp_split2, out_dir=tmp_out2, dest_path=tmp_dest2,
        common_expl={}, verbose=False,
    )
    if 'b-01-999' in combined2 or 's-90-001' in combined2:
        print('[FAIL] 職類快取未隔離，safety 合併結果混入 osh 的題目')
        ok = False
    elif combined2.get('b-02-888', {}).get('c') != '假解析2':
        print('[FAIL] safety 職類合併結果異常')
        ok = False
    else:
        print('[OK] 跨職類快取正確隔離（safety 合併結果不含 osh 假資料）')

    shutil.rmtree(tmp_root, ignore_errors=True)
    print('=== selftest 清理完成（假輸出已刪除） ===')
    print('=== expl_merge_multi selftest 全部通過 ===' if ok else '=== expl_merge_multi selftest 有失敗項目，見上方 [FAIL] ===')
    return ok


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        success = selftest()
        sys.exit(0 if success else 1)

    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    trades = args if args else TRADES

    common = load_common_explanations()
    all_stats = []
    for trade in trades:
        if trade not in TRADES:
            raise SystemExit(f'未知職類: {trade}（應為 {TRADES} 之一）')
        _, stats = merge_trade(trade, common_expl=common)
        all_stats.append(stats)

    print('=== 全部職類合併總計 ===')
    for s in all_stats:
        print(f'{s["trade"]}: 專業={s["professional_merged"]} 共同={s["common_injected"]} '
              f'合計={s["combined_total"]} 掛條文(g:1)={s["law_mounted"]} '
              f'ref降級={s["downgraded"]} 原生§被改寫={s["rewritten"]}')
