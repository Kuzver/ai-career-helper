from io import BytesIO
from html.parser import HTMLParser
from loguru import logger


def export_markdown(text: str) -> bytes:
    return text.encode("utf-8")


def export_html(text: str) -> bytes:
    import markdown
    html_body = markdown.markdown(text, extensions=["tables", "fenced_code"])

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ответ ИИ-помощника</title>
<style>
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; line-height: 1.6; }}
  h1, h2, h3 {{ color: #3649F9; }}
  code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }}
  pre {{ background: #1e1e2e; color: #cdd6f4; padding: 16px; border-radius: 8px; overflow-x: auto; }}
  pre code {{ background: none; color: inherit; padding: 0; }}
  ul, ol {{ padding-left: 24px; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
  th {{ background: #f8f9fa; }}
  .header {{ text-align: center; color: #6D7C90; font-size: 0.85em; margin-bottom: 32px; }}
</style>
</head>
<body>
<div class="header">Сгенерировано ИИ-помощником по карьере</div>
{html_body}
</body>
</html>"""
    return html.encode("utf-8")


class _DocxBuilder(HTMLParser):
    def __init__(self, doc):
        super().__init__()
        self.doc = doc
        self._tag_stack: list[str] = []
        self._current_paragraph = None
        self._in_pre = False
        self._in_strong = False
        self._in_em = False
        self._in_blockquote = False
        self._list_stack: list[str] = []
        self._table_rows: list[list[str]] = []
        self._current_row: list[str] | None = None
        self._cell_text = ""
        self._in_table = False
        self._in_th = False
        self._code_text = ""

    def handle_starttag(self, tag: str, attrs):
        self._tag_stack.append(tag)

        if tag in ("h1", "h2", "h3", "h4"):
            level = int(tag[1])
            self._current_paragraph = self.doc.add_heading("", level=level)

        elif tag == "p":
            if self._in_blockquote:
                self._current_paragraph = self.doc.add_paragraph(style="Intense Quote")
            else:
                self._current_paragraph = self.doc.add_paragraph()

        elif tag == "ul":
            self._list_stack.append("ul")
        elif tag == "ol":
            self._list_stack.append("ol")

        elif tag == "li":
            if self._list_stack and self._list_stack[-1] == "ol":
                self._current_paragraph = self.doc.add_paragraph(style="List Number")
            else:
                self._current_paragraph = self.doc.add_paragraph(style="List Bullet")

        elif tag == "pre":
            self._in_pre = True
            self._code_text = ""

        elif tag == "code":
            if not self._in_pre:
                self._in_strong = False
                self._in_em = False

        elif tag == "strong" or tag == "b":
            self._in_strong = True
        elif tag == "em" or tag == "i":
            self._in_em = True

        elif tag == "blockquote":
            self._in_blockquote = True

        elif tag == "table":
            self._in_table = True
            self._table_rows = []

        elif tag == "tr":
            self._current_row = []

        elif tag in ("td", "th"):
            self._in_th = tag == "th"
            self._cell_text = ""

    def handle_endtag(self, tag: str):
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

        if tag in ("h1", "h2", "h3", "h4", "p", "li"):
            self._current_paragraph = None

        elif tag in ("ul", "ol"):
            if self._list_stack:
                self._list_stack.pop()

        elif tag == "pre":
            self._in_pre = False
            p = self.doc.add_paragraph()
            from docx.shared import Pt, RGBColor
            run = p.add_run(self._code_text.rstrip("\n"))
            run.font.name = "Consolas"
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(0x1E, 0x1E, 0x2E)
            self._code_text = ""

        elif tag == "code":
            pass

        elif tag == "strong" or tag == "b":
            self._in_strong = False
        elif tag == "em" or tag == "i":
            self._in_em = False

        elif tag == "blockquote":
            self._in_blockquote = False

        elif tag in ("td", "th"):
            if self._current_row is not None:
                self._current_row.append(self._cell_text)
            self._cell_text = ""

        elif tag == "tr":
            if self._current_row is not None:
                self._table_rows.append(self._current_row)
            self._current_row = None

        elif tag == "table":
            self._flush_table()
            self._in_table = False

    def handle_data(self, data: str):
        if self._in_pre:
            self._code_text += data
            return

        if self._in_table and (self._current_row is not None):
            self._cell_text += data
            return

        if self._current_paragraph is not None:
            from docx.shared import Pt
            tag_in_code = "code" in self._tag_stack
            run = self._current_paragraph.add_run(data)
            if tag_in_code:
                run.font.name = "Consolas"
                run.font.size = Pt(9)
            if self._in_strong:
                run.bold = True
            if self._in_em:
                run.italic = True

    def _flush_table(self):
        if not self._table_rows:
            return
        cols = max(len(r) for r in self._table_rows)
        rows_count = len(self._table_rows)
        table = self.doc.add_table(rows=rows_count, cols=cols)
        table.style = "Table Grid"
        from docx.shared import Pt
        for i, row_data in enumerate(self._table_rows):
            row = table.rows[i]
            for j, cell_text in enumerate(row_data):
                if j < cols:
                    cell = row.cells[j]
                    cell.text = cell_text.strip()
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.font.size = Pt(10)
                    if i == 0:
                        for paragraph in cell.paragraphs:
                            for run in paragraph.runs:
                                run.bold = True
        self._table_rows = []


def md_to_docx(text: str, title: str = "") -> bytes:
    import markdown
    from docx import Document
    from docx.shared import Pt

    doc = Document()
    style = doc.styles["Normal"]
    style.font.size = Pt(11)
    style.font.name = "Calibri"

    if title:
        doc.add_heading(title, level=0)

    html_body = markdown.markdown(text, extensions=["tables", "fenced_code"])
    builder = _DocxBuilder(doc)
    builder.feed(html_body)

    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()


def export_docx(text: str) -> bytes:
    try:
        return md_to_docx(text)
    except Exception as e:
        logger.error(f"DOCX export error: {e}")
        return export_markdown(text)
