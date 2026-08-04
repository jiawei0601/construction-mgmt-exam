import fitz, sys
pdf_path = sys.argv[1]
needle = sys.argv[2]
doc = fitz.open(pdf_path)
for i, page in enumerate(doc):
    rects = page.search_for(needle)
    if rects:
        print("page", i, "rects", rects)
