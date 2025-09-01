"""
TTS module using Melo TTS

To run the demo:
python demo/inference_from_file.py   --model_path /home/josh/py_projs/notebooklm/VibeVoice-1.5B   --txt_path /home/josh/py_projs/notebooklm/sample.txt --output_dir /home/josh/py_projs/notebooklm/out --speaker_names Bowen Xinran
""" 

from __future__ import annotations
import os
import sys
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Iterable, Optional

def synthesize_with_vibevoice(
    script_text: str,
    *,
    model_path: str,
    vibe_repo_dir: str,
    speakers: Iterable[str] = ("Bowen", "Xinran"),
    output_dir: str = "./out",
    python_bin: str = sys.executable,
    extra_args: Optional[list[str]] = None,
) -> Path:
    """
    以官方 demo 腳本做推理，回傳生成的音檔路徑（通常是 .wav）。

    參數：
      - script_text : 逐字稿文字（會以暫存 txt 餵給 demo）
      - model_path  : 已下載的 VibeVoice-1.5B 權重路徑（例：/home/josh/.../VibeVoice-1.5B）
      - vibe_repo_dir : GitHub 專案根目錄（例：/home/josh/.../VibeVoice）
      - speakers    : 說話者名稱序列，會對應你文字中的「Speaker 1:」「Speaker 2:」等
      - output_dir  : 輸出資料夾（demo 使用 --output_dir）
      - python_bin  : 執行 demo 的 Python 直譯器
      - extra_args  : 額外 CLI 參數清單（例如 ["--device", "cuda:0"]）
    """
    vibe_repo = Path(vibe_repo_dir).resolve()
    model_path = str(Path(model_path).resolve())
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    demo_script = vibe_repo / "demo" / "inference_from_file.py"
    if not demo_script.exists():
        raise FileNotFoundError(f"找不到 demo 腳本：{demo_script}")

    # 將逐字稿寫入暫存 .txt
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        txt_path = Path(f.name)
        f.write(script_text.strip() + "\n")

    # 組裝命令列
    cmd = [
        python_bin, str(demo_script),
        "--model_path", model_path,
        "--txt_path", str(txt_path),
        "--output_dir", str(out_dir),
        "--speaker_names", *list(speakers),
    ]
    if extra_args:
        cmd.extend(extra_args)

    # 以 repo 根目錄為工作目錄（某些相對路徑/資源載入會依賴）
    cwd = str(vibe_repo)

    # 執行並擷取錯誤輸出
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                "VibeVoice 推理失敗：\n"
                f"CMD: {' '.join(cmd)}\n"
                f"STDOUT:\n{proc.stdout}\n"
                f"STDERR:\n{proc.stderr}"
            )
    finally:
        # 清理暫存 txt
        try:
            txt_path.unlink(missing_ok=True)
        except Exception:
            pass

    # 取輸出資料夾中最新的音檔
    candidates = sorted(
        [p for p in out_dir.iterdir() if p.suffix.lower() in {".wav", ".mp3", ".flac"}],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise RuntimeError(f"推理完成但在 {out_dir} 找不到輸出音檔。請檢查 demo 腳本行為/參數。")

    return candidates[0]


# --- 範例：直接執行本檔案做 smoke test ---
if __name__ == "__main__":
    # 請依你的實際路徑調整
    MODEL_PATH = "/home/josh/py_projs/notebooklm/VibeVoice-1.5B"
    REPO_DIR   = "/home/josh/py_projs/notebooklm/VibeVoice"
    OUT_DIR    = "/home/josh/py_projs/notebooklm/out"

    sample_script = """
Speaker 1: 我們測試一下 VibeVoice 的本地 TTS，看看能不能順利產生多人的對話。
Speaker 2: 好的，我現在開始回應，這個模型應該會自動幫我們切換不同的聲音。
Speaker 1: 之後我會把一整篇論文的逐字稿丟進來，請你幫我變成 podcast。
Speaker 2: 沒問題，等你把稿子準備好，我們就可以開始長篇合成了。
"""

    out_path = synthesize_with_vibevoice(
        script_text=sample_script,
        model_path=MODEL_PATH,
        vibe_repo_dir=REPO_DIR,
        speakers=("Bowen", "Xinran"),  # 你要的預設
        output_dir=OUT_DIR,
        # extra_args=["--device", "cuda:0"]  # 視 demo 是否支援
    )
    print(f"生成音檔：{out_path}")
