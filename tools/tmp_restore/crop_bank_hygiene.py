import fitz, json, sys
sys.path.insert(0, "tools/tmp_restore")
from lib_locate import find_qstarts, find_footer_y

path = "raw-hygiene/bank/22100_職業衛生管理_甲級_學科題庫.pdf"
doc = fitz.open(path)
qs = find_qstarts(doc, 26)
qs.sort(key=lambda q: (q["page"], q["y0"]))

targets = [38,39,54,55,56,57,58,59,60,62,63,258]
by_page = {}
for q in qs:
    by_page.setdefault(q["page"], []).append(q)
for p in by_page:
    by_page[p].sort(key=lambda q: q["y0"])

import os
os.makedirs("assets/img/hygiene", exist_ok=True)

ZOOM = 3
for t in targets:
    q = next(x for x in qs if x["no"] == t)
    pi = q["page"]
    page = doc[pi]
    lines_on_page = by_page[pi]
    idx = lines_on_page.index(q)
    if idx + 1 < len(lines_on_page):
        y1 = lines_on_page[idx+1]["y0"] - 4
    else:
        y1 = find_footer_y(page) - 4
    y0 = q["y0"] - 6
    rect = page.rect
    clip = fitz.Rect(rect.x0 + 20, y0, rect.x1 - 20, y1)
    pix = page.get_pixmap(matrix=fitz.Matrix(ZOOM, ZOOM), clip=clip)
    out = f"assets/img/hygiene/b-03-{t:03d}.png"
    pix.save(out)
    print(out, clip)
