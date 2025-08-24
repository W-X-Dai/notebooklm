from TTS.api import TTS

# 選一個支援中文的模型（示範用 coqui-ai 的多語言模型）
model_name = "tts_models/multilingual/multi-dataset/your_tts"

# 載入模型
tts = TTS(model_name)

# 輸出成 wav 檔
tts.tts_to_file(text="人工智慧正在改變世界", file_path="output.wav")

print("語音已產生 -> output.wav")
