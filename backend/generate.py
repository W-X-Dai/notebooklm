"""
using Ollama to generate the podcast script
"""

# backend/generate.py
from __future__ import annotations
import os
import json
import requests
from typing import List, Tuple

# ---- 基本設定 ----
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:latest")

# ---- 低階：呼叫 Ollama API ----
def ollama_generation(
    prompt: str,
    model: str = DEFAULT_MODEL,
    *,
    num_predict: int = 3000,
    temperature: float = 0.7,
    top_p: float = 0.9,
    stream: bool = False,
    timeout: int = 600,
) -> str:
    """
    使用 Ollama /api/generate 產生文字。
    - num_predict: 等同 OpenAI 的 max_tokens；Ollama 參數名是 num_predict
    - 其他採用 options 傳入，兼容常見設定
    """
    url = f"{OLLAMA_API_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream,
        "keep_alive": "1s", 
        "options": {
            "num_predict": num_predict,
            "temperature": temperature,
            "top_p": top_p,
        },
    }
    headers = {"Content-Type": "application/json"}

    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=timeout)
    resp.raise_for_status()

    # 非串流時，Ollama 會直接回一個 JSON：{"response": "...", ...}
    data = resp.json()
    return data.get("response", "")

# ---- 中階：組 Podcast Prompt ----
def build_podcast_prompt(
    chunks: List[str],
    *,
    mins: int = 15,
    target_words: int = 4000,
    domain: str = "Computer Science",
    style: str = "口語化、自然，像是兩人討論技術，但保留專有名詞。",
    speaker1: str = "Speaker 1",
    speaker2: str = "Speaker 2",
    max_context_chars: int = 20000,
) -> str:
    """
    把切好的文本片段組裝成 Podcast 專用 Prompt。
    - 會做最簡單的長度控管：把 chunks 連起來後，超過 max_context_chars 會截斷
    - 要求輸出逐行以「Speaker 1: / Speaker 2:」開頭，方便丟給 VibeVoice
    """
    target_words = mins * 600  # 220 words per minute
    header = (
        f"你是一名 Podcast 編輯，請將下列{domain}的內容轉寫為大約{mins}分鐘（{target_words}字）的雙人對話逐字稿。\n\n"
        "要求：\n"
        f"- 角色：{speaker1}（提問、澄清），{speaker2}（解釋、補充）。\n"
        "- 聽眾：基本高中學歷，沒有讀過該論文。\n"
        "- 語言：中文\n"
        f"- 風格：{style}\n"
        "- 結構：\n"
        f"    1. 開場（{speaker1}: 引入主題，{speaker2}: 簡述論文題目與背景）\n"
        "    2. 問題與動機（這篇 paper 解決什麼問題？為什麼重要？）\n"
        "    3. 方法（用比喻和簡單範例解釋，但保留核心術語）\n"
        "    4. 實驗與結果（討論作者驗證方法、數據、與 baseline 比較）\n"
        f"    5. 局限與未來方向（{speaker1}: 提出質疑，{speaker2}: 回答）\n"
        f"    6. 結尾（{speaker1}: 總結）\n"
        "- 請不要把方程式的詳細內容寫出來。\n"
        f"- 逐字稿格式：每行以「{speaker1}:」「{speaker2}:」開頭。沒有切換講者時，不要換行。\n"
        "- 嚴格僅根據下方提供的內容寫作；若未提供，不要編造。\n"
        "- 不要出現任何「非文字」，一切方程式、圖表、程式碼都請用文字描述。（例如：「tokens/s」 請說成「每秒處理的 token 數」）"
        "- 不要輸出任何額外解釋文字。\n\n"
        "以下是論文內容（已切分）：\n"
    )

    # 用明確邊界包住每個片段，降低幻覺風險
    blocks = []
    total = 0
    for i, txt in enumerate(chunks, 1):
        block = f"<<CHUNK c{i}>>\n{txt}\n<<END c{i}>>\n\n"
        blocks.append(block)
        total += len(block)

    context = "".join(blocks)
    if len(context) > max_context_chars:
        context = context[:max_context_chars] + "\n<<TRUNCATED: 其餘片段略>>\n"

    return header + context

# ---- 高階：端到端（吃 labeled_chunks）----
def generate_script_from_chunks(
    labeled_chunks: List[Tuple[str, str]],
    *,
    mins: int = 15,
    target_words: int = 4000,
    model: str = DEFAULT_MODEL,
    max_context_chars: int = 20000,
    num_predict: int = 3000,
    style: str = "口語化、自然，像是兩人討論技術，但保留專有名詞。",
    domain: str = "Computer Science",
) -> str:
    """
    labeled_chunks: [(tag, text)]，例如 [("paper.pdf#p1", "..."), ...]
    回傳：Podcast 逐字稿（每行以 Speaker 1/2 開頭）
    """
    # 只取文本部分，保持原有切分順序
    texts = [t for (_, t) in labeled_chunks if t and t.strip()]
    prompt = build_podcast_prompt(
        texts,
        mins=mins,
        target_words=target_words,
        max_context_chars=max_context_chars,
        domain=domain,
        style=style,
        speaker1="Speaker 1",
        speaker2="Speaker 2",
    )
    return ollama_generation(
        prompt,
        model=model,
        num_predict=num_predict,  # 需要足夠大，否則輸出會被截斷
    )

def title_generation(prompt: str) -> str:
    """
    使用 Ollama 產生標題
    """
    title_prompt = f"請為以下內容生成一個簡短且吸引人的標題：\n\n{prompt}\n\n標題："
    title = ollama_generation(
        title_prompt,
        model=DEFAULT_MODEL,
        num_predict=50,
        temperature=0.7,
        top_p=0.9,
    )
    return title.strip().strip('"').strip("'")

""" prompt for generating podcast script 
你是一名 Podcast 編輯，請將下列電腦科學論文的內容轉寫為大約15分鐘（3300字）的雙人對話逐字稿。

要求：
- 角色：Speaker 1（提問、澄清），Speaker 2（解釋、補充）。
- 聽眾：有基本 CS 背景，但不一定讀過該論文。
- 語言：中文
- 風格：口語化、自然，像是兩人討論技術，但保留專有名詞。
- 結構：
  1. 開場（Speaker 1引入主題，Speaker 2簡述論文題目與背景）
  2. 問題與動機（這篇 paper 解決什麼問題？為什麼重要？）
  3. 方法（用比喻和簡單範例解釋，但保留核心術語）
  4. 實驗與結果（討論作者驗證方法、數據、與 baseline 比較）
  5. 局限與未來方向（Speaker 1提出質疑，Speaker 2回答）
  6. 結尾（Speaker 1總結）
- 逐字稿格式：每行以「Speaker 1:」「Speaker 2:」開頭。沒有切換講者時，不要換行。
- 不要出現任何「非文字」，一切方程式、圖表、程式碼都請用文字描述。（例如：「tokens/s」 請說成「每秒處理的 token 數」）
- 不要額外輸出解釋文字。

以下是論文內容：
"""