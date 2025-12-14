"""
Voice Engine - Handles speech recognition and text-to-speech using Coqui TTS
"""

import os
import logging
import speech_recognition as sr
import numpy as np
from pathlib import Path
from typing import Optional

try:
    from TTS.api import TTS
    HAS_COQUI_TTS = True
except ImportError:
    HAS_COQUI_TTS = False

import pyttsx3

# Sounddevice optional - only needed for Coqui TTS playback
HAS_SOUNDDEVICE = False
# try:
#     import sounddevice as sd
#     import soundfile as sf
#     HAS_SOUNDDEVICE = True
# except (ImportError, OSError, AttributeError):
#     HAS_SOUNDDEVICE = False

logger = logging.getLogger(__name__)


class VoiceEngine:
    """Manages voice input/output for JARVIS"""
    
    def __init__(self, voice_config: dict, speech_config: dict):
        """Initialize voice engine with configuration"""
        self.voice_config = voice_config
        self.speech_config = speech_config
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Configure recognizer
        self.recognizer.energy_threshold = speech_config.get('energy_threshold', 4000)
        self.recognizer.pause_threshold = speech_config.get('pause_threshold', 0.8)
        
        # Initialize Coqui TTS
        logger.info("Initializing Coqui TTS...")
        self.tts = None
        self.custom_voice_loaded = False
        self._initialize_tts()
        
        # Adjust for ambient noise
        logger.info("Calibrating microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        logger.info("Voice engine initialized")
    
    def _initialize_tts(self):
        """Initialize TTS engine"""
        try:
            if HAS_COQUI_TTS:
                # Use Coqui TTS if available
                self.tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False)
                self.tts_engine = 'coqui'
                logger.info("Coqui TTS initialized successfully")
                
                # Check for custom voice model
                voice_model_path = self.voice_config.get('voice_model_path')
                if voice_model_path and os.path.exists(voice_model_path):
                    logger.info(f"Loading custom voice model from {voice_model_path}")
                    self.custom_voice_loaded = True
                else:
                    logger.info("Using default voice model")
            else:
                # Fallback to pyttsx3
                self.tts = pyttsx3.init()
                self.tts_engine = 'pyttsx3'
                # Set properties
                self.tts.setProperty('rate', 150)
                self.tts.setProperty('volume', 0.9)
                logger.info("Using pyttsx3 TTS (fallback)")
                
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            # Last resort fallback
            try:
                self.tts = pyttsx3.init()
                self.tts_engine = 'pyttsx3'
                logger.warning("TTS fallback to pyttsx3")
            except:
                logger.warning("TTS will not be available")
                self.tts = None
                self.tts_engine = None
    
    def clone_voice(self, voice_sample_path: str, output_model_path: str = None):
        """
        Clone voice from a sample audio file
        
        Args:
            voice_sample_path: Path to the voice sample WAV file
            output_model_path: Where to save the cloned voice model
        """
        try:
            logger.info(f"Cloning voice from {voice_sample_path}...")
            
            if not os.path.exists(voice_sample_path):
                raise FileNotFoundError(f"Voice sample not found: {voice_sample_path}")
            
            # Use YourTTS for voice cloning
            self.tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False)
            
            # Store the speaker reference
            self.speaker_wav = voice_sample_path
            self.custom_voice_loaded = True
            
            logger.info("Voice cloning successful!")
            return True
            
        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            return False
    
    def speak(self, text: str, save_path: Optional[str] = None):
        """
        Convert text to speech and play it
        
        Args:
            text: Text to speak
            save_path: Optional path to save the audio file
        """
        try:
            if not self.tts:
                logger.warning("TTS not available, skipping speech")
                return
            
            logger.info(f"Speaking: {text}")
            
            if self.tts_engine == 'pyttsx3':
                # Use pyttsx3
                self.tts.say(text)
                self.tts.runAndWait()
                return
            
            # Use Coqui TTS
            if self.custom_voice_loaded and hasattr(self, 'speaker_wav'):
                # Use cloned voice
                output_path = save_path or "temp_speech.wav"
                self.tts.tts_to_file(
                    text=text,
                    speaker_wav=self.speaker_wav,
                    language="en",
                    file_path=output_path
                )
            else:
                # Use default voice
                output_path = save_path or "temp_speech.wav"
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path
                )
            
            # Play the audio
            if HAS_SOUNDDEVICE:
                self._play_audio(output_path)
            
            # Clean up temp file
            if not save_path and os.path.exists(output_path):
                os.remove(output_path)
                
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
    
    def _play_audio(self, audio_path: str):
        """Play audio file"""
        if not HAS_SOUNDDEVICE:
            logger.warning("Sounddevice not available, skipping audio playback")
            return
            
        try:
            # These imports are only available if HAS_SOUNDDEVICE is True
            import sounddevice as sd
            import soundfile as sf
            
            data, samplerate = sf.read(audio_path)
            sd.play(data, samplerate)
            sd.wait()
        except Exception as e:
            logger.error(f"Audio playback failed: {e}")
    
    def listen(self, timeout: Optional[int] = None) -> Optional[str]:
        """
        Listen for voice input and convert to text
        
        Args:
            timeout: Maximum time to wait for speech (seconds)
            
        Returns:
            Recognized text or None if recognition failed
        """
        try:
            timeout = timeout or self.speech_config.get('timeout', 5)
            
            with self.microphone as source:
                logger.info("Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            logger.info("Processing speech...")
            
            # Use Google Speech Recognition (free)
            engine = self.speech_config.get('engine', 'google')
            language = self.speech_config.get('language', 'en-US')
            
            if engine == 'google':
                text = self.recognizer.recognize_google(audio, language=language)
            elif engine == 'sphinx':
                text = self.recognizer.recognize_sphinx(audio)
            else:
                text = self.recognizer.recognize_google(audio, language=language)
            
            logger.info(f"Recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            logger.warning("Listening timeout - no speech detected")
            return None
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error during speech recognition: {e}")
            return None
    
    def detect_wake_word(self) -> bool:
        """
        Listen for wake word (e.g., "Hey JARVIS")
        
        Returns:
            True if wake word detected, False otherwise
        """
        try:
            with self.microphone as source:
                # Short timeout for wake word detection
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
            
            text = self.recognizer.recognize_google(audio, language='en-US')
            text_lower = text.lower()
            
            # Check for wake word variations
            wake_words = [
                "hey eli",
                "eli",
                "ok eli",
                "hello eli"
            ]
            
            for wake_word in wake_words:
                if wake_word in text_lower:
                    logger.info(f"Wake word detected: {text}")
                    return True
            
            return False
            
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return False
        except Exception as e:
            logger.error(f"Wake word detection error: {e}")
            return False
    
    def stop(self):
        """Stop voice engine and cleanup"""
        logger.info("Stopping voice engine...")
        # Cleanup if needed
        if HAS_SOUNDDEVICE:
            try:
                import sounddevice as sd
                sd.stop()
            except:
                pass


if __name__ == "__main__":
    # Test voice engine
    logging.basicConfig(level=logging.INFO)
    
    voice_config = {
        "engine": "coqui",
        "sample_rate": 22050,
        "language": "en"
    }
    
    speech_config = {
        "engine": "google",
        "language": "en-US",
        "energy_threshold": 4000
    }
    
    engine = VoiceEngine(voice_config, speech_config)
    
    # Test TTS
    engine.speak("ELI voice engine test. All systems operational.")
    
    # Test listening
    print("Say something...")
    text = engine.listen()
    if text:
        print(f"You said: {text}")
        engine.speak(f"You said: {text}")
