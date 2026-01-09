"""
Text-to-Speech Module
Converts text responses to voice output
"""

import pyttsx3
from gtts import gTTS
import os
import platform

class TextToSpeech:
    def __init__(self, method="pyttsx3", rate=150, volume=0.9):
        """
        Initialize TTS engine
        
        Args:
            method: 'pyttsx3' (offline) or 'gtts' (online)
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
        """
        self.method = method
        
        if method == "pyttsx3":
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            print("✅ TTS initialized (pyttsx3 - offline)")
        else:
            print("✅ TTS initialized (gTTS - online)")
    
    def speak_pyttsx3(self, text):
        """
        Speak using pyttsx3 (offline)
        
        Args:
            text: Text to speak
        """
        self.engine.say(text)
        self.engine.runAndWait()
    
    def speak_gtts(self, text, filename="response.mp3"):
        """
        Speak using Google TTS (requires internet)
        
        Args:
            text: Text to speak
            filename: Temporary audio file name
        """
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filename)
        
        # Play audio based on operating system
        system = platform.system()
        if system == "Windows":
            os.system(f"start {filename}")
        elif system == "Darwin":  # macOS
            os.system(f"afplay {filename}")
        else:  # Linux
            os.system(f"mpg123 {filename}")
    
    def speak(self, text):
        """
        Main method to convert text to speech
        
        Args:
            text: Text to speak
        """
        print(f"🤖 Assistant: {text}")
        
        try:
            if self.method == "pyttsx3":
                self.speak_pyttsx3(text)
            else:
                self.speak_gtts(text)
        except Exception as e:
            print(f"❌ TTS Error: {e}")


if __name__ == "__main__":
    # Test TTS module
    print("Testing Text-to-Speech module...")
    
    tts = TextToSpeech(method="pyttsx3")
    
    test_messages = [
        "Hello! I am your IIUM voice assistant.",
        "The library is open from 8 AM to 10 PM on weekdays.",
        "How can I help you today?"
    ]
    
    for msg in test_messages:
        print(f"\nSpeaking: {msg}")
        tts.speak(msg)