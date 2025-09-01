import gradio as gr
import fitz  # PyMuPDF
from backend import db
from backend.api import ollama_embedding
from backend.rag import rag_pipeline

"""
Gradio frontend
"""

def extract_text_from_pdf(pdf_file):
    """讀取 PDF 並回傳純文字"""
    text = ""
    with fitz.open(pdf_file.name) as doc:
        for page in doc:
            text += page.get_text() # type: ignore
    return text


def upload_pdf(pdf_file):
    """處理 PDF 上傳，抽取文字並存入 DB"""
    if pdf_file is None:
        return "請先選擇 PDF"

    text = extract_text_from_pdf(pdf_file)

    # 產生 embedding
    emb = ollama_embedding(text, model="nomic-embed-text:v1.5")

    # 存到 DB（id 用檔名）
    db.add_document(pdf_file.name, text, emb)

    return f"已成功加入資料庫: {pdf_file.name}"


def chat(query, history):
    """RAG 問答"""
    answer = rag_pipeline(query, top_k=3)
    history.append((query, answer))
    return history, ""


with gr.Blocks() as demo:
    gr.Markdown("# 📚 NotebookLM MVP\nRAG + gpt-oss + PDF 上傳")

    with gr.Tab("💬 Chat"):
        chatbot = gr.Chatbot(label="對話")
        msg = gr.Textbox(label="輸入你的問題")

        msg.submit(chat, [msg, chatbot], [chatbot, msg])

    with gr.Tab("📂 上傳 PDF"):
        pdf_file = gr.File(label="上傳 PDF", file_types=[".pdf"])
        upload_btn = gr.Button("處理並存入資料庫")
        output = gr.Textbox(label="結果")

        upload_btn.click(upload_pdf, inputs=pdf_file, outputs=output)

demo.launch(server_name="0.0.0.0", server_port=7860)
