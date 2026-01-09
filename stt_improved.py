"""
Improved Speech-to-Text Module
Features: Noise reduction, better accuracy, VAD (Voice Activity Detection)
"""

import whisper
import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
import noisereduce as nr

class ImprovedSpeechToText:
    def __init__(self, model_name="base"):
        """
        Initialize improved Whisper with noise reduction
        
        Args:
            model_name: Model size (tiny, base, small, medium, large)
        """
        print(f"📥 Loading Whisper model: {model_name}...")
        self.model = whisper.load_model(model_name)
        self.sample_rate = 16000
        print("✅ Improved STT ready with noise reduction!")
    
    def record_audio(self, duration=5):
        """
        Record audio with automatic gain control
        """
        print(f"🎙️  Recording for {duration} seconds... SPEAK CLEARLY!")
        
        try:
            # Record with higher quality settings
            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32,  # Higher quality
                blocking=True
            )
            
            # Normalize audio levels
            audio = audio / np.max(np.abs(audio))
            
            print("✅ Recording complete!")
            return audio
            
        except Exception as e:
            print(f"❌ Recording error: {e}")
            raise
    
    def reduce_noise(self, audio):
        """
        Apply noise reduction to improve quality
        """
        try:
            # Apply noise reduction
            reduced_noise = nr.reduce_noise(
                y=audio.flatten(),
                sr=self.sample_rate,
                stationary=True,
                prop_decrease=0.8
            )
            return reduced_noise
        except Exception as e:
            print(f"⚠️  Noise reduction failed: {e}, using original")
            return audio.flatten()
    
    def save_audio(self, audio, filename="temp_audio.wav"):
        """Save audio to WAV file"""
        # Ensure audio is in correct format
        if audio.dtype != np.int16:
            audio = (audio * 32767).astype(np.int16)
        
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio.tobytes())
        return filename
    
    def transcribe(self, audio_file):
        """
        Transcribe audio file with better accuracy settings
        """
        print("🔄 Transcribing with improved accuracy...")
        
        try:
            result = self.model.transcribe(
                audio_file,
                language="en",
                task="transcribe",
                temperature=0.0,  # More deterministic
                compression_ratio_threshold=2.4,
                logprob_threshold=-1.0,
                no_speech_threshold=0.6,
                condition_on_previous_text=True,
                initial_prompt="This is a conversation about soccer and football rules."
            )
            
            text = result["text"].strip()
            
            # Additional validation
            if len(text) < 2:
                return "[No clear speech detected]"
            
            return text
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return "[Transcription failed]"
    
    def listen_and_transcribe(self, duration=5):
        """
        Complete improved STT pipeline
        """
        try:
            # Record audio
            audio = self.record_audio(duration)
            
            # Apply noise reduction
            print("🔄 Reducing background noise...")
            audio_clean = self.reduce_noise(audio)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                audio_file = self.save_audio(audio_clean, tmp.name)
            
            # Transcribe
            text = self.transcribe(audio_file)
            
            # Cleanup
            try:
                os.remove(audio_file)
            except:
                pass
            
            return text
            
        except Exception as e:
            print(f"❌ STT Error: {e}")
            return "[Error in speech recognition]"


if __name__ == "__main__":
    # Test improved STT
    print("Testing Improved Speech-to-Text...")
    stt = ImprovedSpeechToText(model_name="base")
    
    text = stt.listen_and_transcribe(duration=5)
    print(f"\n📝 Transcribed: {text}")