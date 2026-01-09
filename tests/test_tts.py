"""Test Text-to-Speech module"""
import os
import sys
sys.path.append('..')

# ------------------------------------------------------------------
# PATH FIX: Allow importing from the main folder
# ------------------------------------------------------------------
# 1. Get the path to the current folder (C:\voice assistant NLP\tests)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Go up one level to the main project folder (C:\voice assistant NLP)
parent_dir = os.path.dirname(current_dir)

# 3. Add the main folder to Python's visible paths
sys.path.append(parent_dir)
# ------------------------------------------------------------------

from tts import TextToSpeech

print("="*60)
print("TESTING TEXT-TO-SPEECH MODULE")
print("="*60)

tts = TextToSpeech(method="pyttsx3")

test_messages = [
    "Hello! Testing voice output.",
    "The library is open from 8 AM to 10 PM.",
    "This is a test of the text to speech system."
]

for i, msg in enumerate(test_messages, 1):
    print(f"\nTest {i}/{len(test_messages)}")
    print(f"Speaking: {msg}")
    tts.speak(msg)
    print("✅ Done")

print("\n" + "="*60)
print("All TTS tests complete!")
print("="*60)