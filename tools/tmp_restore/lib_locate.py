import fitz, re, json

QLINE_RE = re.compile(r'^(\d+)\.\(([\d]+)\)$')

def norm(s):
    return re.sub(r'\s+', '', s)

def get_lines(page):
    d = page.get_text("dict")
    out = []
    for b in d["blocks"]:
        for l in b.get("lines", []):
            text = "".join(s["text"] for s in l["spans"])
            out.append({"bbox": l["bbox"], "text": text})
    return out

def find_qstarts(doc, page_start=0, page_end=None, x0_max=120):
    if page_end is None:
        page_end = len(doc)
    results = []
    for pi in range(page_start, page_end):
        page = doc[pi]
        for line in get_lines(page):
            x0, y0, x1, y1 = line["bbox"]
            t = norm(line["text"])
            m = QLINE_RE.match(t)
            if m and x0 < x0_max:
                results.append({"page": pi, "no": int(m.group(1)), "ans": m.group(2), "y0": y0, "y1": y1, "x0": x0})
    return results

def find_footer_y(page):
    for line in get_lines(page):
        if re.match(r'^Page\d+of\d+$', norm(line["text"])):
            return line["bbox"][1]
    return page.rect.y1

if __name__ == "__main__":
    import sys
    path = sys.argv[1]
    page_start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    doc = fitz.open(path)
    qs = find_qstarts(doc, page_start)
    with open("tools/tmp_restore/_qstarts.json", "w", encoding="utf-8") as f:
        json.dump(qs, f, ensure_ascii=False, indent=1)
    print(len(qs), "found")
