**PyPDF2 (now `pypdf`) is not layout-aware.** It reads the content stream order, so multi-column pages, sidebars, figures, and maths often come out jumbled. No OCR, no table detection, no diagram/figure semantics, no equation parsing. Use it for merges/splits/metadata; avoid it for serious text extraction.

## What to use instead (by need)

- **General, layout-aware text**: `pdfplumber` or `pdfminer.six` (word/char boxes you can sort into columns). `PyMuPDF` (`fitz`) is fast and gives blocks/spans with coordinates.
- **Tables**: `camelot` (lattice/stream) or `tabula` (Java). `pdfplumber` can also work with table heuristics.
- **Figures/diagrams**: `PyMuPDF` for extracting embedded images reliably; vector diagrams can be tricky (often paths, not images).
- **Math formulae**:

  - If selectable text exists → you’ll get literal Unicode (sometimes TeX-like), but spacing can be off.
  - If rendered as images → you need OCR specialised for maths (e.g. **Mathpix** API). General OCR (Tesseract) won’t reliably reconstruct LaTeX.

## A robust extraction plan

1. **Parse the page with coordinates**
   Prefer `pdfplumber` or `PyMuPDF`. Keep word/line boxes (`x0,x1,y0,y1`) and any images.

2. **Detect columns (2–3 column papers, reports)**

   - Build a histogram of word midpoints on the X axis and find column bands.
   - Group words by column band; within each column sort by `(y desc, x asc)`.
   - Reflow lines; join columns in logical order (left→right).

3. **Handle tables & figures specially**

   - Run a table detector first (Camelot/Tabula). Remove those boxes from “body text”.
   - Extract images (figures) and capture nearby captions (regex for “Figure|Fig.” within N pixels).

4. **Maths**

   - If text layer contains glyphs, keep as text but **do not normalise away spaces too aggressively** (kills alignment).
   - If no text layer (scanned) → OCR that region. For high quality LaTeX, use Mathpix; otherwise store as image + caption.

5. **Output structured chunks**

   - Keep: `section_path`, `page_no`, `bbox`, `chunk_type` (text/table/figure/formula), and `text`.
   - Chunk prose to \~300–500 tokens with 10–20% overlap; keep tables/figures **atomic** and reference them from nearby paragraphs.

6. **Indexing hints for RAG**

   - Embed prose chunks normally.
   - For tables, embed **normalised CSV text** (headers + a few key rows) and keep the full table as an attachment.
   - For figures, embed the **caption + surrounding paragraph**; keep the image for rendering in answers.

## Minimal working examples

### A) Two-column extraction with `pdfplumber`

```python
import pdfplumber
from statistics import median

def extract_two_columns(pdf_path, page_no=0, gap_min=18):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_no]
        words = page.extract_words(
            keep_blank_chars=False, use_text_flow=True, extra_attrs=["size"]
        )
        # Estimate column split via x-midpoint clustering
        mids = [ (w["x0"]+w["x1"])/2 for w in words ]
        x_sorted = sorted(mids)
        # crude valley split around median gap
        gaps = [(x_sorted[i+1]-x_sorted[i], i) for i in range(len(x_sorted)-1)]
        gap, idx = max(gaps) if gaps else (0, 0)
        split_x = (x_sorted[idx] + x_sorted[idx+1]) / 2 if gaps else median(mids)

        left, right = [], []
        for w in words:
            mid = (w["x0"]+w["x1"])/2
            (left if mid < split_x else right).append(w)

        def to_text(ws):
            # sort by y descending (page origin at bottom), then x
            ws = sorted(ws, key=lambda w: (-w["top"], w["x0"]))
            lines, cur_y, buf = [], None, []
            for w in ws:
                if cur_y is None or abs(w["top"]-cur_y) < gap_min:
                    buf.append(w["text"])
                    cur_y = w["top"] if cur_y is None else cur_y
                else:
                    lines.append(" ".join(buf)); buf=[w["text"]]; cur_y=w["top"]
            if buf: lines.append(" ".join(buf))
            return "\n".join(lines)

        left_text  = to_text(left)
        right_text = to_text(right)
        return left_text + "\n\n" + right_text
```

### B) Get blocks, images, and captions with `PyMuPDF`

```python
import fitz  # PyMuPDF
import re

def page_blocks_images(pdf_path, page_no=0):
    doc = fitz.open(pdf_path)
    page = doc[page_no]

    # Text blocks with coordinates
    blocks = page.get_text("blocks")  # (x0,y0,x1,y1, text, block_no, block_type, ...)
    blocks = sorted(blocks, key=lambda b: (b[1], b[0]))  # y, then x

    # Images
    imgs = []
    for xref, *_ in page.get_images(full=True):
        pix = fitz.Pixmap(doc, xref)
        out = f"/tmp/img_{page_no}_{xref}.png"
        pix.save(out); pix = None
        rect = page.get_image_bbox(xref)  # image bbox if available
        imgs.append({"path": out, "bbox": rect})

    # Naive figure caption detection
    captions = []
    for b in blocks:
        text = (b[4] or "").strip()
        if re.match(r"^(Figure|Fig\.?)\s*\d+", text, re.I):
            captions.append({"text": text, "bbox": fitz.Rect(b[:4])})

    return blocks, imgs, captions
```

### C) Tables with Camelot (lattice first, then stream)

```python
import camelot

def extract_tables(pdf_path, pages="1"):
    tables = []
    try:
        tables = camelot.read_pdf(pdf_path, pages=pages, flavor="lattice")
        if not tables or tables.n == 0:
            tables = camelot.read_pdf(pdf_path, pages=pages, flavor="stream")
    except Exception:
        pass
    return [t.df for t in tables]
```

### D) Fallback OCR for scanned pages (Tesseract)

```python
import fitz, pytesseract
from PIL import Image

def ocr_page(pdf_path, page_no=0, dpi=300):
    doc = fitz.open(pdf_path)
    page = doc[page_no]
    pix = page.get_pixmap(dpi=dpi)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return pytesseract.image_to_pdf_or_hocr(img, extension="hocr")
```

## Practical gotchas

- **Reading order** is not guaranteed in PDFs. Always rely on **coordinates**, not stream order.
- **Ligatures** (“ﬁ”, “ﬂ”) and hidden characters can pollute text. Normalise carefully.
- **Vector diagrams** aren’t images. You often can’t “extract” them; capture captions and surrounding text.
- **Math fonts** may map to private glyphs; you’ll see gibberish unless the text layer is well-encoded.
- **Scanned PDFs** need OCR; consider page-level quality checks and only OCR when no text layer is present.

## “From X → Y” upgrades

- From **PyPDF2 text extraction → pdfplumber/PyMuPDF blocks**: jumbled → column-aware, reproducible order.
- From **generic OCR → math-aware OCR**: plaintext approximations → recover LaTeX/MathML (with a paid API).
- From **monolithic chunking → structure-aware chunks**: fewer hallucinations, better citations in RAG.
