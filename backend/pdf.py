import fitz  # PyMuPDF

def extract_text(pdf_path: str) -> str:
    """讀取整份 PDF，回傳合併後的純文字"""
    text = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            t = page.get_text() # type: ignore
            if t.strip():
                text.append(t)
    return "\n".join(text)

def extract_pages(pdf_path: str) -> list[str]:
    """逐頁讀取 PDF，回傳 list[每頁文字]"""
    pages = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            t = page.get_text() # type: ignore
            pages.append(t.strip())
    return pages
