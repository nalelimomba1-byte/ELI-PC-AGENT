"""
Edge TTS Engine - Microsoft Azure Neural Voices (Free)
"""
import os
import logging
import asyncio
import edge_tts

logger = logging.getLogger(__name__)

class EdgeEngine:
    """
    Wrapper for Edge TTS (Microsoft Neural Voices)
    """
    def __init__(self, voice='en-US-AvaNeural'):
        """
        Initialize Edge TTS
        Voices: 'en-US-AvaNeural', 'en-US-AndrewNeural', 'en-US-AriaNeural', etc.
        """
        self.voice = voice
        logger.info(f"Initializing Edge-TTS (Voice: {self.voice})")

    async def _generate_audio(self, text, output_path):
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)

    def synthesize(self, text: str, output_path: str):
        """
        Synthesize text to audio file
        """
        try:
            logger.info(f"Synthesizing with Edge-TTS: {text[:30]}...")
            
            # Run async function in sync wrapper
            asyncio.run(self._generate_audio(text, output_path))
            
            return True
            
        except Exception as e:
            logger.error(f"Edge-TTS synthesis failed: {e}")
            return False
