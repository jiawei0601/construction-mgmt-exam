import fitz, sys, os
sys.path.insert(0, "tools/tmp_restore")
from lib_locate import find_qstarts, find_footer_y

def crop_subject(pdf_path, targets, out_prefix, out_dir="assets/img/hygiene", zoom=3):
    doc = fitz.open(pdf_path)
    qs = find_qstarts(doc, 0)
    qs.sort(key=lambda q: (q["page"], q["y0"]))
    by_page = {}
    for q in qs:
        by_page.setdefault(q["page"], []).append(q)
    for p in by_page:
        by_page[p].sort(key=lambda q: q["y0"])
    os.makedirs(out_dir, exist_ok=True)
    results = {}
    for t in targets:
        matches = [x for x in qs if x["no"] == t]
        if not matches:
            print("MISSING", t)
            continue
        q = matches[0]
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
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip)
        out = f"{out_dir}/{out_prefix}-{t:03d}.png"
        pix.save(out)
        results[t] = out
        print(out, "page", pi, "ans", q["ans"], clip)
    return results

if __name__ == "__main__":
    import json
    pdf_path = sys.argv[1]
    out_prefix = sys.argv[2]
    targets = [int(x) for x in sys.argv[3:]]
    crop_subject(pdf_path, targets, out_prefix)
