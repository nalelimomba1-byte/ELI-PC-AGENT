"""
Kokoro TTS Engine - High-quality, local, human-like text-to-speech.
"""
import os
import logging
import soundfile as sf
# Kokoro imports - wrapped in try/except to handle import errors gracefully
try:
    from kokoro import KPipeline
    HAS_KOKORO = True
except ImportError:
    HAS_KOKORO = False

logger = logging.getLogger(__name__)

class KokoroEngine:
    """
    Wrapper for Kokoro-82M TTS
    """
    def __init__(self, lang_code='a', voice='af_heart'):
        """
        Initialize Kokoro Pipeline
        lang_code: 'a' for American English, 'b' for British English
        voice: 'af_heart' (default), 'af_sky', etc.
        """
        if not HAS_KOKORO:
            logger.error("Kokoro library not installed. Run 'pip install kokoro soundfile'")
            return

        logger.info(f"Initializing Kokoro TTS (Lang: {lang_code}, Voice: {voice})...")
        try:
            # Initialize pipeline (downloads model if needed)
            self.pipeline = KPipeline(lang_code=lang_code)
            self.default_voice = voice
            logger.info("Kokoro Pipeline loaded successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kokoro Pipeline: {e}")
            raise

    def synthesize(self, text: str, output_path: str):
        """
        Synthesize text to audio file
        """
        try:
            if not HAS_KOKORO:
                return False

            logger.info(f"Synthesizing with Kokoro: {text[:30]}...")
            
            # Generate audio
            # pipeline returns a generator of (graphemes, phonemes, audio)
            # We concatenate if multiple segments, but usually for short responses one is enough
            
            generator = self.pipeline(
                text, 
                voice=self.default_voice, 
                speed=1, 
                split_pattern=r'\n+'
            )
            
            all_audio = []
            
            for i, (gs, ps, audio) in enumerate(generator):
                all_audio.append(audio)
                
            if not all_audio:
                logger.warning("Kokoro generated no audio")
                return False
                
            import numpy as np
            # Concatenate all audio segments
            if len(all_audio) > 1:
                final_audio = np.concatenate(all_audio)
            else:
                final_audio = all_audio[0]

            # Save to file (Kokoro usually outputs 24khz)
            sf.write(output_path, final_audio, 24000)
            
            return True
            
        except Exception as e:
            logger.error(f"Kokoro synthesis failed: {e}")
            return False
