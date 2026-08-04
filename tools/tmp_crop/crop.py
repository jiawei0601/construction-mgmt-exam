import fitz, sys
pdf_path = sys.argv[1]
page_no = int(sys.argv[2])  # 0-indexed
x0, y0, x1, y1 = map(float, sys.argv[3:7])
out = sys.argv[7]
zoom = float(sys.argv[8]) if len(sys.argv) > 8 else 3.0
doc = fitz.open(pdf_path)
page = doc[page_no]
clip = fitz.Rect(x0, y0, x1, y1)
pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip)
pix.save(out)
print(out, clip)
