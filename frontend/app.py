import gradio as gr
from backend.pdf import extract_text
from backend.split import chunk_by_chars, labeled_chunks
from backend.generate import generate_script_from_chunks, title_generation
from backend.tts import synthesize_with_vibevoice

def pipeline(pdf_file, mins, style, domain):
    if pdf_file is None:
        return None, "請先上傳 PDF"
    
    print("Starting cutting the PDF into chunks...")
    name = pdf_file.name.split("/")[-1]
    text = extract_text(pdf_file.name)
    chunks = chunk_by_chars(text, max_chars=2000, overlap=200)
    labeled = labeled_chunks(chunks, name, mode="c")

    print("Start generating the script...")
    # 生成逐字稿
    script = generate_script_from_chunks(labeled, mins=mins, target_words=3300, style="口語化、自然，像是兩人討論技術，但保留專有名詞", domain="Computer Science")
    title = title_generation(script)
    print(f"Generated script title: {title}")
    print("Start synthesizing the audio...")
    # 語音合成 (這裡用 vibevoice, 假設 backend/tts.py 有 synthesize_with_vibevoice)
    out_audio = synthesize_with_vibevoice(
        script,
        model_path="/home/josh/py_projs/notebooklm/VibeVoice-1.5B",
        vibe_repo_dir="/home/josh/py_projs/notebooklm/VibeVoice",
        speakers=["Xinran", "Bowen"],
        output_dir="./out",
    )
    print("Done.")
    return str(out_audio), script


with gr.Blocks(title="Podcastifier") as demo:
    gr.Markdown("# 📄 → 🎙️ 論文 Podcast 生成器")

    with gr.Row():
        with gr.Column(scale=1):
            pdf = gr.File(label="上傳 PDF", file_types=[".pdf"])
            mins = gr.Slider(5, 30, value=15, step=1, label="Podcast 時長（分鐘）")
            style = gr.Textbox(value="口語化、自然，像是兩人討論技術，但保留專有名詞。", label="風格")
            domain = gr.Dropdown(
                ["Computer Science", "Medicine", "Physics", "Biology", "Mathematics"],
                value="Computer Science",
                label="論文領域"
            )
            btn = gr.Button("生成 Podcast", variant="primary")
        with gr.Column(scale=1):
            audio = gr.Audio(label="輸出 Podcast", type="filepath", interactive=False)
            script_box = gr.Textbox(label="逐字稿", lines=20)

    btn.click(pipeline, inputs=[pdf, mins, style, domain], outputs=[audio, script_box])


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
