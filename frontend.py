from backend.pdf import extract_text, extract_pages
from backend.split import chunk_by_chars, labeled_chunks

def pipeline(pdf_file, mins, style):
    name = pdf_file.name.split("/")[-1]
    
    # 1. 讀取全文
    text = extract_text(pdf_file.name)
    
    # 2. 切分 (這裡示範按字數)
    chunks = chunk_by_chars(text, max_chars=2000, overlap=200)
    
    # 3. 加標籤
    labeled = labeled_chunks(chunks, name, mode="c")
    
    # 4. 丟給 LLM 生成 Podcast 腳本
    script = generate_script_from_chunks(labeled, mins=mins, target_words=3300)
    
    # 5. 丟給 VibeVoice TTS
    synthesize_with_vibevoice(script, "podcast.mp3", speaker_ids={})
    
    return "podcast.mp3", script
