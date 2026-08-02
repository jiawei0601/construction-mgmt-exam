# -*- coding: utf-8 -*-
import re
import json
import time
import os
import requests

BASE = "https://owinform.wdasec.gov.tw/ExamNet/owInform/PastQuestions.aspx"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
}

sessions = [
    ("115","第1梯次","202603160001"),
    ("115","第2梯次","202607060001"),
    ("114","第1梯次","202503170001"),
    ("114","第2梯次","202507070001"),
    ("114","第2梯次(颱風延期考區)","202508250001"),
    ("114","第3梯次","202511030001"),
    ("113","第1梯次","202403180001"),
    ("113","第2梯次","202407080001"),
    ("113","第3梯次","202411040001"),
    ("112","第1梯次","202303200001"),
    ("112","第2梯次","202307100001"),
    ("112","第3梯次","202311060001"),
    ("111","第1梯次","202203210001"),
    ("111","第2梯次","202207110001"),
    ("111","第3梯次","202211070001"),
    ("110","第1梯次","202103220001"),
    ("110","第2梯次","202109270001"),
    ("110","第3梯次","202112200001"),
    ("109","第1梯次","202003160001"),
    ("109","第2梯次","202007130001"),
    ("109","第3梯次","202011020001"),
    ("108","第1梯次","201903180001"),
    ("108","第2梯次","201907150001"),
    ("108","第3梯次","201911040001"),
    ("107","第1梯次","201803190001"),
    ("107","第2梯次","201807160001"),
    ("107","第3梯次","201811050001"),
    ("106","第1梯次","201703200001"),
    ("106","第2梯次","201707170001"),
    ("106","第3梯次","201711060001"),
    ("105","第1梯次","201603210001"),
    ("105","第2梯次","201607180001"),
    ("105","第3梯次","201611070002"),
]

session = requests.Session()
session.headers.update(HEADERS)

os.makedirs("session_html", exist_ok=True)
results = []

for year, batch, yserno in sessions:
    url = f"{BASE}?yserno={yserno}"
    fn = f"session_html/{year}_{batch}_{yserno}.html".replace("(", "_").replace(")", "_")
    try:
        r = session.get(url, timeout=30)
        status = r.status_code
        html = r.text
        with open(fn, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception as e:
        print(f"ERROR {year} {batch} {yserno}: {e}")
        results.append({"year": year, "batch": batch, "yserno": yserno, "error": str(e)})
        continue

    # find rows containing 營造工程管理
    rows = re.findall(r"<tr[^>]*>.*?</tr>", html, re.S)
    matches = []
    for row in rows:
        if "營造工程管理" in row:
            tds = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
            tds_clean = [re.sub(r"<[^>]+>", "", t).strip() for t in tds]
            hrefs = re.findall(r'''href=['"]([^'"]+\.(?:pdf|odf|doc|docx)[^'"]*)['"]''', row, re.I)
            matches.append({"tds": tds_clean, "hrefs": hrefs})
    results.append({"year": year, "batch": batch, "yserno": yserno, "status": status, "matches": matches})
    print(year, batch, yserno, status, "matches:", len(matches))
    time.sleep(0.3)

with open("sessions_result.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("DONE")
