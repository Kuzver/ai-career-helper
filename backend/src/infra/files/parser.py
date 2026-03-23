import pdfplumber
from io import BytesIO
from loguru import logger

MAX_CHARS = 5000
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".md"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def validate_file(filename: str, size: int) -> str | None:
    ext = _get_extension(filename)
    if ext not in ALLOWED_EXTENSIONS:
        return f"Формат {ext} не поддерживается. Допустимые: PDF, DOCX, MD"
    if size > MAX_FILE_SIZE:
        return f"Файл слишком большой ({size // 1024 // 1024} МБ). Максимум 10 МБ"
    return None


def extract_text(filename: str, content: bytes) -> str:
    ext = _get_extension(filename)
    if ext == ".pdf":
        return _extract_pdf(content)
    if ext == ".docx":
        return _extract_docx(content)
    if ext == ".md":
        return _extract_md(content)
    return "Неподдерживаемый формат файла"


def _get_extension(filename: str) -> str:
    return ("." + filename.rsplit(".", 1)[-1]).lower() if "." in filename else ""


def _extract_pdf(content: bytes) -> str:
    try:
        text = ""
        with pdfplumber.open(BytesIO(content)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text[:MAX_CHARS] if text else "Не удалось извлечь текст из PDF"
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return f"Ошибка при чтении PDF: {e}"


def _extract_docx(content: bytes) -> str:
    try:
        from docx import Document
        doc = Document(BytesIO(content))
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return text[:MAX_CHARS] if text else "Не удалось извлечь текст из DOCX"
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        return f"Ошибка при чтении DOCX: {e}"


def _extract_md(content: bytes) -> str:
    try:
        text = content.decode("utf-8", errors="replace")
        return text[:MAX_CHARS] if text else "Пустой файл"
    except Exception as e:
        logger.error(f"MD extraction error: {e}")
        return f"Ошибка при чтении MD: {e}"
