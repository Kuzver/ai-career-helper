from io import BytesIO
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


def export_docx(text: str) -> bytes:
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor

        doc = Document()
        style = doc.styles["Normal"]
        style.font.size = Pt(11)
        style.font.name = "Calibri"

        for line in text.split("\n"):
            stripped = line.strip()
            if not stripped:
                doc.add_paragraph("")
                continue

            if stripped.startswith("### "):
                p = doc.add_heading(stripped[4:], level=3)
            elif stripped.startswith("## "):
                p = doc.add_heading(stripped[3:], level=2)
            elif stripped.startswith("# "):
                p = doc.add_heading(stripped[2:], level=1)
            elif stripped.startswith("- ") or stripped.startswith("* "):
                doc.add_paragraph(stripped[2:], style="List Bullet")
            elif stripped[0].isdigit() and ". " in stripped[:4]:
                doc.add_paragraph(stripped.split(". ", 1)[1], style="List Number")
            else:
                doc.add_paragraph(stripped)

        buf = BytesIO()
        doc.save(buf)
        return buf.getvalue()
    except Exception as e:
        logger.error(f"DOCX export error: {e}")
        return export_markdown(text)
