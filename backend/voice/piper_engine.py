import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PiperEngine:
    def __init__(self, piper_path="backend/voice/piper_bin/piper.exe", model_path="backend/voice/piper_bin/voices/en_US-amy-medium.onnx"):
        self.piper_path = Path(piper_path).absolute()
        self.model_path = Path(model_path).absolute()
        
        if not self.piper_path.exists():
            logger.error(f"Piper binary not found at {self.piper_path}")
            raise FileNotFoundError("Piper binary missing")
            
        if not self.model_path.exists():
            logger.error(f"Piper model not found at {self.model_path}")
            raise FileNotFoundError("Piper model missing")
            
    def synthesize(self, text, output_file="output.wav"):
        """Synthesize text to audio file"""
        try:
            # Command: echo text | piper ...
            cmd = [
                str(self.piper_path),
                "--model", str(self.model_path),
                "--output_file", str(output_file)
            ]
            
            # Windows: subprocess might need shell=True for piping echo? 
            # Better: pass text via stdin
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = process.communicate(input=text.encode('utf-8'))
            
            if process.returncode != 0:
                logger.error(f"Piper failed: {stderr.decode()}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Piper synthesis error: {e}")
            return False
