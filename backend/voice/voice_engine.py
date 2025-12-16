"""
Voice Engine - Handles speech recognition and text-to-speech using Coqui TTS
"""

import os
import logging
import speech_recognition as sr
import numpy as np
from pathlib import Path
from typing import Optional
import time
from faster_whisper import WhisperModel

try:
    from TTS.api import TTS
    HAS_COQUI_TTS = True
except ImportError:
    HAS_COQUI_TTS = False

import pyttsx3
import winsound
from .piper_engine import PiperEngine
from .kokoro_engine import KokoroEngine
from .edge_engine import EdgeEngine

# Sounddevice optional - only needed for Coqui TTS playback
HAS_SOUNDDEVICE = False

logger = logging.getLogger(__name__)


class VoiceEngine:
    """Manages voice input/output for JARVIS"""
    
    def __init__(self, voice_config: dict, speech_config: dict):
        """Initialize voice engine with configuration"""
        self.voice_config = voice_config
        self.speech_config = speech_config
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # State flags
        self.is_speaking = False
        
        # Configure recognizer (High Sensitivity for Distance)
        self.recognizer.energy_threshold = speech_config.get('energy_threshold', 200) # Ultra-sensitive
        self.recognizer.dynamic_energy_threshold = True # Enable auto-gain to catch faint voices
        self.recognizer.dynamic_energy_adjustment_damping = 0.15 # Less damping = faster adjustment
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = speech_config.get('pause_threshold', 0.8)
        
        # Initialize Faster-Whisper
        logger.info("Initializing Faster-Whisper...")
        try:
            # Force CPU to avoid CUDA dependency crashes (missing dlls)
            logger.info("Forcing CPU mode for stability (Base model with Beam=1)...")
            # Using base.en with beam_size=1 offers best balance of speed/accuracy on CPU
            self.whisper_model = WhisperModel("base.en", device="cpu", compute_type="int8")
            logger.info("Faster-Whisper initialized successfully (CPU Mode - Base)")
        except Exception as e:
            logger.error(f"Failed to load Faster-Whisper: {e}")
            # Fallback to CPU explicit if auto fails?
            self.whisper_model = WhisperModel("base.en", device="cpu", compute_type="int8")
        
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
            # Try Edge-TTS first (Microsoft Neural - Best Quality)
            try:
                self.edge = EdgeEngine(voice='en-US-AvaNeural')
                self.tts = self.edge
                self.tts_engine = 'edge'
                logger.info("Edge-TTS initialized successfully")
                return
            except Exception as e:
                logger.warning(f"Edge-TTS not available: {e}. Falling back...")

            # Try Kokoro first (Human-like, 82M params)
            try:
                self.kokoro = KokoroEngine(voice='af_heart') # Use warm female voice
                self.tts = self.kokoro
                self.tts_engine = 'kokoro'
                logger.info("Kokoro TTS initialized successfully")
                return
            except Exception as e:
                logger.warning(f"Kokoro TTS not available: {e}. Falling back...")
                
            # Try Piper next
            try:
                self.piper = PiperEngine()
                self.tts = self.piper # Assign to self.tts to satisfy availability check
                self.tts_engine = 'piper'
                logger.info("Piper TTS initialized successfully")
                return
            except Exception as e:
                logger.warning(f"Piper TTS not available: {e}. Falling back...")

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
            self.is_speaking = True
            
            if not self.tts:
                logger.warning("TTS not available, skipping speech")
                return
            
            logger.info(f"Speaking: {text}")
            
            if self.tts_engine == 'pyttsx3':
                # Use pyttsx3
                self.tts.say(text)
                self.tts.runAndWait()
                return
            
            if self.tts_engine == 'edge':
                output_path = save_path or "temp_speech.mp3"
                if self.edge.synthesize(text, output_path):
                    self._play_audio(output_path)
                    if not save_path and os.path.exists(output_path):
                         os.remove(output_path)
                return

            if self.tts_engine == 'kokoro':
                output_path = save_path or "temp_speech.wav"
                if self.kokoro.synthesize(text, output_path):
                    self._play_audio(output_path)
                    # Cleanup
                    if not save_path and os.path.exists(output_path):
                         os.remove(output_path)
                return

            if self.tts_engine == 'piper':
                output_path = save_path or "temp_speech.wav"
                if self.piper.synthesize(text, output_path):
                    self._play_audio(output_path)
                    # Cleanup
                    if not save_path and os.path.exists(output_path):
                        # Add small delay or wait for playback lock? winsound block waits
                         os.remove(output_path)
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
        finally:
            self.is_speaking = False
    
    def _play_audio(self, audio_path: str):
        """Play audio file"""
        try:
            if not os.path.exists(audio_path):
                logger.error(f"Audio file not found: {audio_path}")
                return
                
            file_size = os.path.getsize(audio_path)
            if file_size == 0:
                logger.error(f"Audio file is empty: {audio_path}")
                return
                
            logger.info(f"Playing audio: {audio_path} ({file_size} bytes)")

            if HAS_SOUNDDEVICE:
                logger.info("Using SoundDevice for playback")
                # These imports are only available if HAS_SOUNDDEVICE is True
                import sounddevice as sd
                import soundfile as sf
                
                data, samplerate = sf.read(audio_path)
                sd.play(data, samplerate)
                sd.wait()
                
                # Cooldown after SoundDevice
                import time
                time.sleep(0.1)
                
            else:
                logger.info("Using Pygame for playback")
                import pygame
                import time
                
                # Initialize mixer if not already done
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                
                # Load and play
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()
                
                # Wait for playback to finish (Blocking)
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                # Unload to release file lock (important for deletion)
                pygame.mixer.music.unload()
                
                # Minimal buffer for responsiveness
                time.sleep(0.1)
                logger.info("Playback complete. Listening immediately.")
                
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
            
            # Synchronization: Wait if currently speaking
            while self.is_speaking:
                time.sleep(0.1)
                
            with self.microphone as source:
                logger.info("Listening...")
                # Capture audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            # Check overlap again - if speech started during listening, discard
            if self.is_speaking:
                logger.info("Speech overlapped with listening - discarding input")
                return None
            
            logger.info("Processing speech with Faster-Whisper...")
            
            # Save to temporary WAV file for Whisper
            temp_wav = "temp_input.wav"
            with open(temp_wav, "wb") as f:
                f.write(audio.get_wav_data())
                
            try:
                # Transcribe with base.en (better accuracy) but beam_size=1 (speed)
                try:
                    segments, info = self.whisper_model.transcribe(temp_wav, beam_size=1)
                except Exception as e:
                    logger.warning(f"Whisper inference failed: {e}")
                    # Retry once
                    segments, info = self.whisper_model.transcribe(temp_wav, beam_size=1)
                    
                text = " ".join([segment.text for segment in segments]).strip()
                
                # Filter hallucinations (common in Whisper with noise/silence)
                if not text or len(text) < 2 or text.replace('.', '').replace(' ', '') == '':
                    return None
                    
                # Blacklist common Whisper hallucinations & Self-Hearing phrases
                hallucinations = [
                    "thank you", "thanks for watching", "subtitles by", "amara.org",
                    "copyright", "all rights reserved", "you", "start conversation",
                    "uncontrollable laughter", "silence", "bye",
                    # Self-Hearing Phrases (Response overlaps)
                    "anny is ready", "i'm sorry", "please provide", "eli online",
                    "how can i assist", "i understand", "is there anything else"
                ]
                
                text_lower = text.lower().strip()
                
                # Check for hallucinations
                if any(h in text_lower for h in hallucinations):
                    # Only filter if it's the ENTIRE phrase or very short
                    if len(text_lower) < 20 or any(text_lower == h for h in hallucinations):
                        logger.info(f"Filtered hallucination: {text}")
                        return None

                # Filter repetitive punctuation specifically
                if " . ." in text or ". . ." in text:
                    return None
                
            finally:
                # Cleanup
                if os.path.exists(temp_wav):
                    os.remove(temp_wav)
            
            logger.info(f"Recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            logger.warning("Listening timeout - no speech detected")
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
