import os
import requests
import zipfile
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PiperSetup")

PIPER_URL = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"
VOICE_URL_ONNX = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx"
VOICE_URL_JSON = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json"

DEST_DIR = Path("backend/voice/piper_bin")
VOICE_DIR = DEST_DIR / "voices"

def download_file(url, dest_path):
    logger.info(f"Downloading {url} to {dest_path}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    logger.info("Download complete.")

def setup_piper():
    if not DEST_DIR.exists():
        DEST_DIR.mkdir(parents=True)
    
    # 1. Download Piper Binary
    zip_path = DEST_DIR / "piper.zip"
    if not (DEST_DIR / "piper.exe").exists():
        download_file(PIPER_URL, zip_path)
        
        logger.info("Extracting Piper...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(DEST_DIR)
        
        # Move files from subfolder if needed (usually extracts to piper/)
        extracted_folder = DEST_DIR / "piper"
        if extracted_folder.exists():
            for item in extracted_folder.iterdir():
                shutil.move(str(item), str(DEST_DIR))
            extracted_folder.rmdir()
        
        os.remove(zip_path)
        logger.info("Piper binary installed.")
    else:
        logger.info("Piper binary already exists.")

    # 2. Download Voice Model
    if not VOICE_DIR.exists():
        VOICE_DIR.mkdir()
        
    voice_onnx = VOICE_DIR / "en_US-amy-medium.onnx"
    voice_json = VOICE_DIR / "en_US-amy-medium.onnx.json"
    
    if not voice_onnx.exists():
        download_file(VOICE_URL_ONNX, voice_onnx)
    if not voice_json.exists():
        download_file(VOICE_URL_JSON, voice_json)
        
    logger.info(f"Voice model installed at {voice_onnx}")

if __name__ == "__main__":
    setup_piper()
