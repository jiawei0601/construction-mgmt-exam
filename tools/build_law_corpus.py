# 從全國法規資料庫 Open API 整包快取（重用 C:\CLAUDE\工地知識庫補充資料\_api_cache\
# 的 ChLaw.json / ChOrder.json，避免重複下載）抽出本考科常用法規，
# 轉成 tools/law_corpus/ 下「一法規一檔」UTF-8 純文字，供 expl_merge.py 抽條文用。
# 用法: python -X utf8 tools/build_law_corpus.py
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'law_corpus')
CACHE = r'C:\CLAUDE\工地知識庫補充資料\_api_cache'

os.makedirs(OUT, exist_ok=True)

# 本考科（營造工程管理甲級）常用法規；已用 grep 對 data/questions.js 驗證過引用頻率。
TARGETS = [
    '營造業法',
    '建築法',
    '建築技術規則建築設計施工編',
    '政府採購法',
    '政府採購法施行細則',
    '職業安全衛生法',
    '職業安全衛生設施規則',
    '營造安全衛生設施標準',
    '營建工程空氣污染防制設施管理辦法',
    '噪音管制法',
    '噪音管制標準',
    '水污染防治法',
    '廢棄物清理法',
    '事業廢棄物貯存清除處理方法及設施標準',
    '營建事業廢棄物再利用管理辦法',
    '勞動基準法',
    '消防法',
    '各類場所消防安全設備設置標準',
    # 2026-08-03 擴充：expl_merge.py name-only ref 模糊比對用，補抓題目常引用
    # 但語料原本缺的正式法規（皆已在 in_moj_db 確認存在，非行政規則/技術規範）。
    '建築技術規則建築構造編',
    '建築技術規則建築設備編',
    '建築技術規則總則編',
    '營業秘密法',
    '個人資料保護法',
    '菸害防制法',
    '著作權法',
    '環境影響評估法',
    '貪污治罪條例',
    '商標法',
    '專利法',
    '勞動檢查法',
    '性別平等工作法',
    '氣候變遷因應法',
    '自來水用戶用水設備標準',
    '土壤及地下水污染整治法',
    '公職人員利益衝突迴避法',
    '空氣污染防制法',
    '職業安全衛生標示設置準則',
    '勞工職業災害保險及保護法',
    '毒性及關注化學物質管理法',
    '下水道用戶排水設備標準',
    '職業安全衛生教育訓練規則',
    '民法',
    '職業安全衛生法施行細則',
    '勞動部組織法',
    '勞動檢查法施行細則',
    '職業安全衛生管理辦法',
    '證人保護法',
    '性騷擾防治法',
    '環境教育法',
    '室內空氣品質管理法',
    '環境基本法',  # 原 UNMATCHED.txt 中唯一一筆 §條號接不到的法規，經查 moj_db 其實有收錄，一併補上
    '中華民國刑法',  # 題庫俗稱「刑法」，官方正式登記名稱為「中華民國刑法」，語料仍存成正式全名，靠別名比對
]


def load(path):
    d = json.load(open(path, encoding='utf-8-sig'))
    return d['Laws']


index = {}
for f, src in [('ChLaw/ChLaw.json', '法律'), ('ChOrder/ChOrder.json', '命令')]:
    for law in load(os.path.join(CACHE, f)):
        index[law['LawName']] = (law, src)


def to_txt(law, src):
    lines = [law['LawName'], '']
    lines.append(f"法規位階：{src}（{law.get('LawLevel', '')}）")
    lines.append(f"最新異動日期：{law.get('LawModifiedDate', '')}")
    lines.append('資料來源：全國法規資料庫 Open API（law.moj.gov.tw）')
    lines.append('')
    for a in law.get('LawArticles', []):
        t = a.get('ArticleType')
        no = (a.get('ArticleNo') or '').strip()
        content = (a.get('ArticleContent') or '').strip()
        if t == 'C':  # 編章節
            lines += [f'【{content or no}】', '']
        else:
            if no:
                lines += [no, content, '']
            else:
                lines += [content, '']
    return '\n'.join(lines)


report = []
for name in TARGETS:
    if name not in index:
        report.append(('MISSING', name, '', ''))
        continue
    law, src = index[name]
    if law.get('LawAbandonNote'):
        report.append(('ABANDONED', name, law.get('LawModifiedDate', ''), law.get('LawAbandonNote', '')))
        continue
    txt = to_txt(law, src)
    path = os.path.join(OUT, f'{name}.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(txt)
    n_arts = sum(1 for a in law.get('LawArticles', []) if a.get('ArticleType') != 'C')
    report.append(('OK', name, law.get('LawModifiedDate', ''), f'{n_arts} 條'))

for status, name, mod, note in report:
    print(f'{status}\t{name}\t{mod}\t{note}')
