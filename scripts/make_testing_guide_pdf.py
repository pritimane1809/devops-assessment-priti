from pathlib import Path
import re
import textwrap


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "testing-guide.md"
OUTPUT = ROOT / "docs" / "CloudMaven-Testing-Guide.pdf"

PAGE_WIDTH = 595
PAGE_HEIGHT = 842
MARGIN = 46
LINE_HEIGHT = 13
CODE_LINE_HEIGHT = 11
MAX_TEXT_WIDTH = 86
MAX_CODE_WIDTH = 78


def escape_pdf(text):
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def parse_markdown(markdown):
    blocks = []
    in_code = False
    code_lines = []
    paragraph = []

    def flush_paragraph():
        if paragraph:
            blocks.append(("paragraph", " ".join(paragraph).strip()))
            paragraph.clear()

    for raw in markdown.splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            if in_code:
                blocks.append(("code", code_lines[:]))
                code_lines.clear()
                in_code = False
            else:
                flush_paragraph()
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not line.strip():
            flush_paragraph()
            continue

        if line.startswith("# "):
            flush_paragraph()
            blocks.append(("title", line[2:].strip()))
        elif line.startswith("## "):
            flush_paragraph()
            blocks.append(("heading", line[3:].strip()))
        elif line.startswith("- "):
            flush_paragraph()
            blocks.append(("bullet", line[2:].strip()))
        else:
            paragraph.append(line.strip())

    flush_paragraph()
    return blocks


def wrap_text(text, width):
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False) or [""]


class Pdf:
    def __init__(self):
        self.pages = []
        self.current = []
        self.y = PAGE_HEIGHT - MARGIN
        self.page_number = 0
        self.new_page()

    def new_page(self):
        if self.current:
            self.pages.append(self.current)
        self.page_number += 1
        self.current = []
        self.y = PAGE_HEIGHT - MARGIN
        self.text("CloudMaven Testing Guide", 9, MARGIN, PAGE_HEIGHT - 26, "F2", (90, 90, 90))
        self.text(f"Page {self.page_number}", 9, PAGE_WIDTH - 82, 24, "F2", (90, 90, 90))
        self.line(MARGIN, PAGE_HEIGHT - 34, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 34, (210, 210, 210))

    def ensure(self, height):
        if self.y - height < MARGIN:
            self.new_page()

    def text(self, text, size, x, y, font="F1", color=(20, 28, 36)):
        r, g, b = [value / 255 for value in color]
        self.current.append(f"{r:.3f} {g:.3f} {b:.3f} rg BT /{font} {size} Tf {x} {y} Td ({escape_pdf(text)}) Tj ET")

    def line(self, x1, y1, x2, y2, color=(0, 0, 0)):
        r, g, b = [value / 255 for value in color]
        self.current.append(f"{r:.3f} {g:.3f} {b:.3f} RG {x1} {y1} m {x2} {y2} l S")

    def add_title(self, text):
        self.ensure(52)
        for line in wrap_text(text, 42):
            self.text(line, 21, MARGIN, self.y, "F1", (15, 51, 91))
            self.y -= 25
        self.y -= 6

    def add_heading(self, text):
        self.ensure(36)
        self.y -= 10
        self.text(text, 14, MARGIN, self.y, "F1", (18, 84, 132))
        self.y -= 20

    def add_paragraph(self, text):
        lines = wrap_text(text, MAX_TEXT_WIDTH)
        self.ensure(len(lines) * LINE_HEIGHT + 8)
        for line in lines:
            self.text(line, 10, MARGIN, self.y, "F2")
            self.y -= LINE_HEIGHT
        self.y -= 5

    def add_bullet(self, text):
        lines = wrap_text(text, MAX_TEXT_WIDTH - 4)
        self.ensure(len(lines) * LINE_HEIGHT + 8)
        self.text("-", 10, MARGIN, self.y, "F2")
        for index, line in enumerate(lines):
            self.text(line, 10, MARGIN + 14, self.y, "F2")
            self.y -= LINE_HEIGHT
        self.y -= 4

    def add_code(self, lines):
        wrapped = []
        for line in lines:
            parts = wrap_text(line, MAX_CODE_WIDTH)
            wrapped.extend(parts)
        height = len(wrapped) * CODE_LINE_HEIGHT + 14
        self.ensure(height)
        self.current.append(f"0.965 0.973 0.984 rg {MARGIN - 6} {self.y - height + 6} {PAGE_WIDTH - (2 * MARGIN) + 12} {height} re f")
        cursor = self.y - 9
        for line in wrapped:
            self.text(line, 8.5, MARGIN, cursor, "F3", (28, 43, 54))
            cursor -= CODE_LINE_HEIGHT
        self.y -= height + 8

    def finish(self):
        if self.current:
            self.pages.append(self.current)


def build_pdf(pdf):
    objects = []

    def add_object(content):
        objects.append(content)
        return len(objects)

    pages_id_placeholder = 0
    font_helvetica_bold = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    font_helvetica = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    font_courier = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")

    page_ids = []
    content_ids = []
    for page in pdf.pages:
        stream = "\n".join(page).encode("latin-1", "replace")
        content_ids.append(add_object(f"<< /Length {len(stream)} >>\nstream\n{stream.decode('latin-1')}\nendstream"))
        page_ids.append(None)

    pages_id = len(objects) + len(pdf.pages) + 1
    for index, content_id in enumerate(content_ids):
        page_ids[index] = add_object(
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Resources << /Font << /F1 {font_helvetica_bold} 0 R /F2 {font_helvetica} 0 R /F3 {font_courier} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        )

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    actual_pages_id = add_object(f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>")
    catalog_id = add_object(f"<< /Type /Catalog /Pages {actual_pages_id} 0 R >>")

    output = ["%PDF-1.4\n%\xE2\xE3\xCF\xD3\n"]
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(sum(len(part.encode("latin-1", "replace")) for part in output))
        output.append(f"{number} 0 obj\n{obj}\nendobj\n")

    xref_offset = sum(len(part.encode("latin-1", "replace")) for part in output)
    output.append(f"xref\n0 {len(objects) + 1}\n")
    output.append("0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.append(f"{offset:010d} 00000 n \n")
    output.append(
        f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n"
    )
    return "".join(output).encode("latin-1", "replace")


def main():
    markdown = SOURCE.read_text(encoding="utf-8")
    markdown = re.sub(r"`([^`]+)`", r"\1", markdown)
    blocks = parse_markdown(markdown)

    pdf = Pdf()
    for kind, value in blocks:
        if kind == "title":
            pdf.add_title(value)
        elif kind == "heading":
            pdf.add_heading(value)
        elif kind == "paragraph":
            pdf.add_paragraph(value)
        elif kind == "bullet":
            pdf.add_bullet(value)
        elif kind == "code":
            pdf.add_code(value)
    pdf.finish()

    OUTPUT.write_bytes(build_pdf(pdf))
    print(OUTPUT)


if __name__ == "__main__":
    main()

