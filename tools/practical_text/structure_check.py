#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
結構抽查腳本：檢查 solutions-{osh,safety,hygiene}/*.md
- 大題數是否正確（osh=10, safety=5, hygiene=5）
- 各大題配分合計是否 = 100
- 每大題四個必要小節（題目/參考擬答/法規與依據/考點提示）是否齊備
- 標題格式是否一致（# 開頭全名, ## 第X題（配分：XX分）)
輸出寫入 UTF-8 檔案，避免 console 中文亂碼。
"""
import re
import os
import io
import sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TRADES = {
    "osh": {"dir": "solutions-osh", "expect_n": 10},
    "safety": {"dir": "solutions-safety", "expect_n": 5},
    "hygiene": {"dir": "solutions-hygiene", "expect_n": 5},
}

REQUIRED_SECTIONS = ["### 題目", "### 參考擬答", "### 法規與依據", "### 考點提示"]

CN_NUM = ["一","二","三","四","五","六","七","八","九","十"]

def big_title_pattern(idx):
    # ## 第X題（配分：XX分）
    cn = CN_NUM[idx-1]
    return re.compile(r"^##\s*第" + cn + r"題\s*（配分：(\d+)分）\s*$")

def check_file(path, expect_n):
    issues = []
    with io.open(path, encoding="utf-8") as f:
        text = f.read()
    lines = text.splitlines()

    # H1 title check
    h1 = [l for l in lines if l.startswith("# ")]
    if not h1:
        issues.append("缺少 H1 標題")
    elif not re.match(r"^# .+術科參考詳解 — 民國\d+年第\d+梯次$", h1[0]):
        issues.append(f"H1 標題格式不符: {h1[0]!r}")

    # split by big question headers (## 第X題)
    header_re = re.compile(r"^##\s*第(.+?)題\s*（配分：(\d+)分）\s*$")
    headers = []  # (line_idx, cn_num_text, score)
    for i, l in enumerate(lines):
        m = header_re.match(l.strip())
        if m:
            headers.append((i, m.group(1), int(m.group(2))))

    n = len(headers)
    if n != expect_n:
        issues.append(f"大題數={n}，應為{expect_n}")

    # check sequential numbering
    expected_cn = CN_NUM[:n]
    actual_cn = [h[1] for h in headers]
    if actual_cn != expected_cn[:len(actual_cn)]:
        # only flag if mismatched, allow it to still report
        mismatches = [(a, e) for a, e in zip(actual_cn, expected_cn) if a != e]
        if mismatches:
            issues.append(f"大題編號順序異常: 實際={actual_cn} 預期={expected_cn}")

    total_score = sum(h[2] for h in headers)
    if total_score != 100:
        issues.append(f"配分合計={total_score}，應為100")

    # check required sections within each big question block
    for idx, (line_i, cn, score) in enumerate(headers):
        start = line_i
        end = headers[idx+1][0] if idx+1 < len(headers) else len(lines)
        block = "\n".join(lines[start:end])
        missing = [s for s in REQUIRED_SECTIONS if s not in block]
        if missing:
            issues.append(f"第{cn}題缺少小節: {missing}")
        # check section order
        positions = []
        for s in REQUIRED_SECTIONS:
            p = block.find(s)
            positions.append(p if p >= 0 else 10**9)
        if positions != sorted(positions):
            issues.append(f"第{cn}題小節順序不符: {REQUIRED_SECTIONS}")

    return issues

def main():
    out_lines = []
    fail_files = []
    total_files = 0
    for trade, cfg in TRADES.items():
        d = os.path.join(BASE, cfg["dir"])
        files = sorted(f for f in os.listdir(d) if f.endswith(".md"))
        out_lines.append(f"\n=== {trade} ({cfg['dir']}, expect {cfg['expect_n']} big Q) : {len(files)} files ===")
        for fn in files:
            total_files += 1
            path = os.path.join(d, fn)
            issues = check_file(path, cfg["expect_n"])
            if issues:
                fail_files.append((trade, fn, issues))
                out_lines.append(f"[FAIL] {fn}")
                for iss in issues:
                    out_lines.append(f"    - {iss}")
            else:
                out_lines.append(f"[OK]   {fn}")

    out_lines.append(f"\n總檔案數: {total_files}, 不合格: {len(fail_files)}")

    outpath = os.path.join(BASE, "tools", "practical_text", "structure_check_result.txt")
    with io.open(outpath, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
    print(f"done, total={total_files}, fail={len(fail_files)}, result written to {outpath}")

if __name__ == "__main__":
    main()
