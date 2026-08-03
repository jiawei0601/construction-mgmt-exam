#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并新的题目解析到 batch-11.json
"""
import json
import sys

# 9题的新解析数据
NEW_EXPLANATIONS = {
    "c-90008-010": {
        "c": "森林砍伐減少蓄水量、加劇全球暖化、物種棲地喪失；B減緩暖化選項邏輯錯誤。",
        "w": {
            "2": "B「減緩全球暖化」與題意矛盾，森林消失只會加劇而非減緩暖化。",
            "3": "D「降低生物多樣性」敘述正確，應為答案選項。",
            "4": "D屬答案組合中必須包含的選項，非錯誤。"
        },
        "ref": None
    },
    "c-90008-013": {
        "c": "環保標章為政府認可標誌，示產品符合環保規範與永續生產標準，供消費者辨識。",
        "w": {
            "2": "此選項為綠色環保標示但非政府環保標章，形式不同。",
            "3": "此選項為其他認證標誌，非經濟部公告的國家環保標章。",
            "4": "此選項為不同機構認證標誌，不符國內環保標章定義。"
        },
        "ref": None
    },
    "c-90008-019": {
        "c": "單位排碳由低至高順序：自行車零排→大眾運輸低排→私車高排；共享運輸最環保。",
        "w": {
            "2": "ACB順序錯誤—把低碳的自行車排在中間，高估了公共運輸相對私車的優勢。",
            "3": "BAC順序錯誤—未能正確判斷自行車為最低碳選項，公共運輸優於私車。",
            "4": "CBA順序完全相反—私車排碳最高應排最後，自行車最低應排最前。"
        },
        "ref": None
    },
    "c-90008-043": {
        "c": "瓶裝水產生塑膠廢棄物、運輸排放碳污、成本高且非必然安全；自來水煮沸更環保。",
        "w": {
            "2": "B「運送瓶裝水時卡車排放污染物」為真實環境負面影響，應為答案。",
            "3": "C「瓶裝水一定比煮沸自來水安全」絕對化錯誤—煮沸自來水足以安全使用。",
            "4": "C選項為錯誤敘述，不應包含於正確敘述的答案組合中。"
        },
        "ref": None
    },
    "c-90008-054": {
        "c": "蚊蟲需在積水孳生，清除積水根絕孳生源為最根本有效防治方法，勝於事後撲滅。",
        "w": {
            "1": "使用殺蟲劑只能事後滅蟲，無法消除蚊蟲持續孳生的源頭，治標不治本。",
            "3": "網子捕捉或人工拍打效率極低且無法大面積防治，不實用。",
            "4": "拍打蚊蟲只能事件式應對，難以根除蚊害，未抓住孳生源問題。"
        },
        "ref": None
    },
    "c-90008-057": {
        "c": "廢棄食用油脂含豐富油酸成分，經鹼化反應可製成天然肥皂，最佳循環利用。",
        "w": {
            "1": "食醋為調味品，不含油脂成分無法作為肥皂製造原料。",
            "2": "果皮含纖維與糖份，應進行堆肥製成有機肥料而非肥皂原料。",
            "4": "廚餘應回收堆肥製肥料，不適合作肥皂製造的油脂來源。"
        },
        "ref": None
    },
    "c-90008-071": {
        "c": "排放標準由中央訂定；但不同產業污染特性差異大，標準因行業而異非統一。",
        "w": {
            "2": "B「所有行業排放標準皆相同」錯誤—製造業、電廠、運輸等各業標準差異。",
            "3": "B敘述不符現況—不同污染源應適用不同標準以科學管制。",
            "4": "B「皆相同」完全相反—標準應因行業特性調整，不可一刀切。"
        },
        "ref": None
    },
    "c-90008-072": {
        "c": "自動監測需與手動標準方法對照驗證；手動檢測為判定依據；年平均值15 μg/m³正確。",
        "w": {
            "1": "A「自動監測儀測值即判定為不符」過於直接—需與手動方法對照後始為結論。",
            "3": "A錯誤導致評估錯誤—自動監測只為指標參考，標準方法為手動檢測。",
            "4": "A「監測儀讀值直接判定」忽略驗證程序，違反空氣品質標準檢測規範。"
        },
        "ref": None
    },
    "c-90008-073": {
        "c": "四行程機車已優於二行程；電動機車零排放；低硫油降低硫氧化物污染排放。",
        "w": {
            "1": "A「汰換四行程成二行程」邏輯反向—二行程污染更重應淘汰，四行程為升級。",
            "3": "A錯誤反轉—汽機車污染防制應從四行程升級到電動，不降級到二行程。",
            "4": "A「汰換成二行程」無助減污—二行程機車因技術原因污染物排放反而更多。"
        },
        "ref": None
    }
}

def main():
    # 讀取現有解析檔
    input_file = r"C:\CLAUDE\construction-mgmt-exam\tools\expl_out\batch-11.json"
    output_file = input_file

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Read failed: {e}")
        sys.exit(1)

    # 驗證新解析字數要求
    validation_errors = []
    for qid, expl in NEW_EXPLANATIONS.items():
        c_len = len(expl['c'])
        if c_len < 8 or c_len > 60:
            validation_errors.append(f"{qid} 正解長度 {c_len} 字，應 8-60 字")

        for option, w_text in expl['w'].items():
            w_len = len(w_text)
            if w_len < 6 or w_len > 40:
                validation_errors.append(f"{qid} 選項{option} 錯因長度 {w_len} 字，應 6-40 字")

    if validation_errors:
        print("[VALIDATION FAILED]")
        for err in validation_errors:
            print(f"  {err}")
        sys.exit(1)

    # 合併新解析
    replaced_count = 0
    for qid, new_expl in NEW_EXPLANATIONS.items():
        if qid in data:
            data[qid] = new_expl
            replaced_count += 1
        else:
            print(f"[WARNING] Question ID {qid} not found in original file")

    # 驗證總題數
    if len(data) != 126:
        print(f"[ERROR] Total questions: {len(data)}, expected 126")
        sys.exit(1)

    # 寫回檔案
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        print(f"[SUCCESS] Replaced {replaced_count} questions")
        print(f"[SUCCESS] Validation passed: {len(data)} total questions, JSON parseable")
        print(f"[SUCCESS] Written to {output_file}")
    except Exception as e:
        print(f"[ERROR] Write failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
