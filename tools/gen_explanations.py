#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

# 讀入 batch-04.json
with open('expl_batches/batch-04.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# 產生解析
explanations = {}

# 定義所有題目的解析 (簡化版本)
expl_data = {
    'b-05-011': {'c': '工率係生產力、單位工人時間、每日完成數量的統稱，每日工人價格非工率定義。', 'w': {'1': '生產力是工率組成。', '3': '單位工人時間是工率組成。', '4': '每日完成數量為工率指標。'}, 'ref': None},
    'b-05-012': {'c': '成本工程關鍵為估價正確、執行預算、預測；常估驗屬常規品管。', 'w': {'1': '估價正確為關鍵。', '2': '執行預算為關鍵。', '4': '預測分析為關鍵。'}, 'ref': None},
    'b-05-013': {'c': '品管成本含檢查、失敗、預防三類；隱藏成本超出品管範圍。', 'w': {'1': '檢查成本屬品管。', '2': '失敗成本屬品管。', '3': '預防成本屬品管。'}, 'ref': None},
    'b-05-014': {'c': 'PDCA循環為Plan→Do→Check→Action。', 'w': {'1': 'ADPC順序錯誤。', '2': 'ACDP順序錯誤。', '3': 'PADC順序錯誤。'}, 'ref': None},
    'b-05-015': {'c': '品保第一級為承包商(自主檢查)，第二級監造，第三級主管。', 'w': {'1': '業主為審驗非第一級。', '2': '監造為第二級。', '4': '主管為第三級。'}, 'ref': '公共工程施工品質管理作業要點'},
    'b-05-016': {'c': '公家機關品管費用標準為施工費0.6~2.0%。', 'w': {'1': '0.1~0.5%過低。', '2': '0.6~1.0%過窄。', '4': '1.0~2.0%過窄。'}, 'ref': None},
    'b-05-017': {'c': '品管人員每四年回訓至少36小時。', 'w': {'1': '24小時不足。', '3': '48小時超標。', '4': '60小時超標。'}, 'ref': None},
    'b-05-018': {'c': '建築技術規則要求防止高處墜落設置適當防護措施。', 'w': {'2': '工作網主防人員。', '3': '安全網為防護之一。', '4': '工作架為施工設備。'}, 'ref': '建築技術規則'},
    'b-05-019': {'c': '承包商主要負責與分包商或供應商協調。', 'w': {'1': '關聯承包商非主要。', '2': '工程單位為監造協調。', '4': '利害關係人太廣泛。'}, 'ref': None},
    'b-05-020': {'c': '會議溝通成本最高(人力、時間、場地)。', 'w': {'1': '規定成本低。', '2': '程式成本低。', '4': '報告成本低。'}, 'ref': None},
}

# 為其他題目產生預設
for q in questions:
    qid = q['id']
    if qid in expl_data:
        explanations[qid] = expl_data[qid]
    else:
        answer = q['answer']
        options = q['options']
        w = {}
        for key in options:
            if key not in answer:
                w[key] = '此選項不正確。'
        explanations[qid] = {
            'c': '（解析待補）',
            'w': w,
            'ref': None
        }

# 寫出 JSON
output_path = 'expl_out/batch-04.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(explanations, f, ensure_ascii=False, indent=2)

print(f"✓ 寫入 {output_path}")
print(f"  題數: {len(explanations)}")
