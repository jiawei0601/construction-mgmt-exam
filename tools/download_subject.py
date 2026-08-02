# -*- coding: utf-8 -*-
import os
import time
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
}

BASE = "https://owinform.wdasec.gov.tw/ExamNet/owInform/DLowFileQ/"

items = [
    ("115", "第2梯次", "202607060001/05/180001-1.pdf"),
    ("114", "第2梯次", "202507070001/06/180001-1.pdf"),
    ("114", "第2梯次_颱風延期考區", "202508250001/24/180001-1.pdf"),
    ("113", "第2梯次", "202407080001/07/180001-1.pdf"),
    ("112", "第2梯次", "202307100001/09/180001-1.pdf"),
    ("111", "第1梯次", "202203210001/20/180001-1.pdf"),
    ("111", "第2梯次", "202207110001/10/180001-1.pdf"),
    ("110", "第1梯次", "202103220001/21/180001-1.pdf"),
    ("110", "第2梯次", "202109270001/1004082900A2.pdf"),
    ("109", "第1梯次", "202003160001/15/180001-1.pdf"),
    ("109", "第2梯次", "202007130001/12/180001-1.pdf"),
    ("108", "第2梯次", "201907150001/14/180001-1.pdf"),
    ("107", "第1梯次", "201803190001/18/180001-1.pdf"),
    ("107", "第2梯次", "201807160001/15/180001-1.pdf"),
    ("106", "第2梯次", "201707170001/180001.pdf".replace("201707170001", "1062A")),
    ("105", "第1梯次", "1051A/180001.pdf"),
    ("105", "第2梯次", "1052A/180001.pdf"),
]

outdir = r"C:\CLAUDE\construction-mgmt-exam\raw\subject"
os.makedirs(outdir, exist_ok=True)

results = []
s = requests.Session()
s.headers.update(HEADERS)

for year, batch, path in items:
    url = BASE + path
    fn = os.path.join(outdir, f"{year}_{batch}_學科試題暨答案.pdf")
    ok = False
    last_err = ""
    for attempt in range(2):
        try:
            r = s.get(url, timeout=30)
            if r.status_code == 200 and len(r.content) > 10*1024 and r.content[:4] == b"%PDF":
                with open(fn, "wb") as f:
                    f.write(r.content)
                ok = True
                size = len(r.content)
                break
            else:
                last_err = f"status={r.status_code} size={len(r.content)} head={r.content[:20]}"
        except Exception as e:
            last_err = str(e)
        time.sleep(1)
    if ok:
        results.append((year, batch, "OK", size, url))
        print("OK", year, batch, size)
    else:
        results.append((year, batch, "FAIL", last_err, url))
        print("FAIL", year, batch, last_err)

print("\n--- SUMMARY ---")
for r in results:
    print(r)
