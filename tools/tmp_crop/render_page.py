import fitz, sys
pdf_path = sys.argv[1]
page_no = int(sys.argv[2])  # 0-indexed
out = sys.argv[3] if len(sys.argv) > 3 else "tools/tmp_crop/preview.png"
zoom = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0
doc = fitz.open(pdf_path)
page = doc[page_no]
pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
pix.save(out)
print(out, page.rect, "npages=", len(doc))
