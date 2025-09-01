# Podcastifier：論文 Podcast 生成器

## 摘要
使用 gpt-oss:20B 與 VibeVoice 結合，將 PDF 轉換成雙人對話式 Podcast。

## 動機
買了 5070Ti 就要好好的玩他！剛好 openai 釋出 gpt-oss 這麼強大的模型，微軟也釋出了 VibeVoice 這麼棒的 TTS 工具，天時地利人和，剛好突破 Notebooklm 每天 3 篇的限制，於是就有了這個專案。

## 功能
目前功能很簡單：上傳 PDF，選擇想要的 Podcast 長度、風格、領域，然後就會生成雙人對話式的逐字稿，並且合成語音。

## 本地安裝
0. 前置作業

本專案系使用 ollama 來執行 gpt-oss:20B，請先安裝好 [ollama](https://ollama.com/download) 來安裝 ollama 並下載 gpt-oss:20B 模型。

此外，也請配置好 VibeVoice 以及相應的權重 VibeVoice-1.5B，並且將這兩個資料夾模組化

1. Clone 這個 repo
   ```bash
   git clone https://github.com/W-X-Dai/notebooklm.git
   cd notebooklm
   ```
2. 建立並啟動虛擬環境
   ```bash
   conda create -n notebooklm python=3.10 -y
   conda activate notebooklm
   ```
3. 安裝依賴
    ```bash
    pip install -r requirements.txt
    ```

## 銘謝

特別感謝 ChatGPT 協助我完成了這個專案，這是我第一次開發這麼大的專案，從一開始的架構設計、程式碼撰寫、錯誤排除、文件撰寫，ChatGPT 都給了我很大的幫助，讓我能夠順利完成這個專案。

如果有任何需求都可以提出 issue 或 PR，或是寄[email](mailto:joshdai930908@gmail.com)給我，我會盡力協助。