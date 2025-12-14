"""
Voice Cloner - Utility for training custom voice from user samples
"""

import os
import logging
from pathlib import Path

try:
    from TTS.api import TTS
    HAS_TTS = True
except ImportError:
    HAS_TTS = False

logger = logging.getLogger(__name__)


class VoiceCloner:
    """Handles voice cloning from user samples"""
    
    def __init__(self):
        """Initialize voice cloner"""
        self.tts = None
        logger.info("Voice cloner initialized")
    
    def prepare_voice_sample(self, input_path: str, output_path: str = None) -> str:
        """
        Prepare voice sample for cloning (normalize, trim silence, etc.)
        
        Args:
            input_path: Path to input audio file
            output_path: Path to save processed audio
            
        Returns:
            Path to processed audio file
        """
        try:
            from pydub import AudioSegment
            from pydub.silence import detect_leading_silence
            
            logger.info(f"Processing voice sample: {input_path}")
            
            # Load audio
            audio = AudioSegment.from_file(input_path)
            
            # Convert to mono if stereo
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Normalize audio
            audio = audio.normalize()
            
            # Trim silence from start and end
            trim_ms = detect_leading_silence(audio)
            audio = audio[trim_ms:]
            
            trim_ms = detect_leading_silence(audio.reverse())
            audio = audio.reverse()[trim_ms:]
            
            # Ensure minimum length (10 seconds recommended)
            if len(audio) < 10000:  # 10 seconds in ms
                logger.warning("Voice sample is shorter than 10 seconds. Quality may be reduced.")
            
            # Save processed audio
            if not output_path:
                output_path = str(Path(input_path).with_suffix('.processed.wav'))
            
            audio.export(output_path, format='wav')
            logger.info(f"Processed voice sample saved to: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to process voice sample: {e}")
            raise
    
    def clone_voice(self, voice_sample_path: str, model_output_dir: str = "models/voice"):
        """
        Clone voice from sample using Coqui TTS
        
        Args:
            voice_sample_path: Path to voice sample WAV file
            model_output_dir: Directory to save voice model
        """
        try:
            logger.info("Starting voice cloning process...")
            
            # Create output directory
            os.makedirs(model_output_dir, exist_ok=True)
            
            # Process the voice sample
            processed_sample = self.prepare_voice_sample(voice_sample_path)
            
            # Initialize YourTTS for voice cloning
            logger.info("Loading YourTTS model for voice cloning...")
            self.tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts")
            
            # Save reference to the speaker wav
            speaker_wav_path = os.path.join(model_output_dir, "speaker_reference.wav")
            
            # Copy processed sample to model directory
            import shutil
            shutil.copy(processed_sample, speaker_wav_path)
            
            logger.info(f"Voice cloning complete! Speaker reference saved to: {speaker_wav_path}")
            logger.info("You can now use this voice for speech synthesis")
            
            # Test the cloned voice
            test_text = "Hello, this is a test of the custom voice cloning system."
            test_output = os.path.join(model_output_dir, "test_output.wav")
            
            self.tts.tts_to_file(
                text=test_text,
                speaker_wav=speaker_wav_path,
                language="en",
                file_path=test_output
            )
            
            logger.info(f"Test audio generated: {test_output}")
            return speaker_wav_path
            
        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            raise
    
    def test_voice(self, speaker_wav_path: str, test_text: str = None):
        """
        Test the cloned voice with sample text
        
        Args:
            speaker_wav_path: Path to speaker reference WAV
            test_text: Text to synthesize (optional)
        """
        try:
            if not self.tts:
                self.tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts")
            
            test_text = test_text or "ELI online. All systems operational. How may I assist you?"
            output_path = "voice_test.wav"
            
            logger.info(f"Generating test audio: {test_text}")
            
            self.tts.tts_to_file(
                text=test_text,
                speaker_wav=speaker_wav_path,
                language="en",
                file_path=output_path
            )
            
            logger.info(f"Test audio saved to: {output_path}")
            
            # Play the audio (optional)
            try:
                import sounddevice as sd
                import soundfile as sf
                
                data, samplerate = sf.read(output_path)
                sd.play(data, samplerate)
                sd.wait()
            except (ImportError, OSError, AttributeError):
                logger.warning("Sounddevice not available, skipping audio playback")
            
        except Exception as e:
            logger.error(f"Voice test failed: {e}")


def main():
    """Main function for voice cloning utility"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ELI Voice Cloning Utility")
    parser.add_argument("--sample", required=True, help="Path to voice sample file")
    parser.add_argument("--output", default="models/voice", help="Output directory for voice model")
    parser.add_argument("--test", action="store_true", help="Test the cloned voice")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    cloner = VoiceCloner()
    
    # Clone voice
    speaker_wav = cloner.clone_voice(args.sample, args.output)
    
    # Test if requested
    if args.test:
        cloner.test_voice(speaker_wav)


if __name__ == "__main__":
    main()
