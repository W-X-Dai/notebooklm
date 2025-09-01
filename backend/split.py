from typing import List, Tuple

def chunk_by_chars(text: str, max_chars=2000, overlap=200) -> List[str]:
    """
    按字數切分文本，帶重疊。
    max_chars: 單塊最大字數
    overlap: 相鄰塊重疊字數，避免斷句過硬
    """
    chunks = []
    i, n = 0, len(text)
    while i < n:
        j = min(i + max_chars, n)
        chunks.append(text[i:j])
        if j == n:
            break
        i = max(0, j - overlap)
    return chunks

def chunk_by_paragraphs(text: str, max_chars=2000) -> List[str]:
    """
    先依段落切分，再合併段落直到接近 max_chars。
    """
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    chunks, buf = [], []
    cur_len = 0
    for p in paras:
        if cur_len + len(p) > max_chars and buf:
            chunks.append("\n".join(buf))
            buf, cur_len = [], 0
        buf.append(p)
        cur_len += len(p)
    if buf:
        chunks.append("\n".join(buf))
    return chunks

def labeled_chunks(chunks: List[str], source: str, mode="c") -> List[Tuple[str, str]]:
    """
    加上標籤方便 trace，例如 (filename#c1, text)
    mode = 'c' 表示 chunk，'p' 表示 page
    """
    return [(f"{source}#{mode}{i+1}", c) for i, c in enumerate(chunks)]
